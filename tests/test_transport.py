"""The HTTP transport, and the gate that makes a loopback port acceptable.

WHAT MOVING TO HTTP ACTUALLY CHANGES. Under stdio the MCP client owns this
process, so the only way to load changed code is the operator typing ``/mcp``.
Under HTTP the client holds a url and reconnects a dropped server by itself, so
the server can be restarted from a shell. That is the whole benefit, and it is
bought with two costs that stdio did not have:

* the server outlives any one session, so in the default LAUNCH mode it would
  hold the persistent Chrome profile lock permanently -- which is why HTTP is
  meant to be paired with ``LINKEDIN_CDP_ATTACH=1``;
* a loopback port is drivable by ANY process running as this user, where stdio
  could only ever be driven by the parent that spawned it.

The second is what ``bearer_gate`` answers, and most of this file is about it.
A gate is worth exactly what its refusals are worth, so every refusal it is
supposed to make has a test that FAILS if the gate stops making it -- including
the two that a plausible-looking wrong implementation would let through: a
token that is a prefix of the real one, and a token that merely starts with it.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import pathlib
import socket

import pytest

from linkedin_server import transport

_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"


def _load(path: pathlib.Path):
    """Import a scripts/ module by path. There is no scripts/__init__.py."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Where it binds, and where it will not
# ---------------------------------------------------------------------------


def test_the_host_is_loopback_and_nothing_reads_an_override():
    """A server driving his signed-in LinkedIn has no business on a LAN.

    The sibling Naukri server has an ``MCP_REMOTE`` escape hatch that binds
    0.0.0.0. There is deliberately no equivalent here, and this test is what
    makes that a decision rather than an omission: it fails the moment
    ``HTTP_HOST`` becomes anything other than the literal loopback address, so
    adding an override is something someone has to do on purpose and argue for
    in this file.
    """
    assert transport.HTTP_HOST == "127.0.0.1"


def test_the_default_port_is_free_of_the_known_occupants():
    """8322 was chosen against a measured list, not guessed.

    Enumerated on this machine on 2026-09-05: 3000, 4317, 4318, 5432, 8000,
    8096, 8321 (the Naukri MCP server), 8889, 9090, 13133. Picking a port that
    collides costs a confusing bind failure at the worst moment -- during a
    cutover -- so the number is pinned here.
    """
    assert transport.DEFAULT_HTTP_PORT == 8322
    assert transport.DEFAULT_HTTP_PORT not in {
        3000, 4317, 4318, 5432, 8000, 8096, 8321, 8889, 9090, 13133
    }


def test_the_url_is_the_one_shape_that_goes_in_mcp_json(monkeypatch):
    """One spelling of the url, so a config entry cannot drift from the server.

    It matches the Naukri entry's shape (``http://127.0.0.1:<port>/mcp``) on
    purpose: the two servers read as a pair in ``.mcp.json`` and a reader who
    knows one knows the other.
    """
    monkeypatch.delenv("LINKEDIN_HTTP_PORT", raising=False)
    assert transport.http_url() == "http://127.0.0.1:8322/mcp"
    assert transport.http_url(9999) == "http://127.0.0.1:9999/mcp"


def test_the_port_is_overridable_by_environment(monkeypatch):
    monkeypatch.setenv("LINKEDIN_HTTP_PORT", "8399")
    assert transport.http_port() == 8399
    assert transport.http_url() == "http://127.0.0.1:8399/mcp"


@pytest.mark.parametrize("bad", ["not-a-number", "0", "70000", "-1"])
def test_an_unusable_port_stops_the_process_rather_than_being_guessed(
    monkeypatch, bad
):
    """Refuse, do not fall back.

    Silently ignoring a bad ``LINKEDIN_HTTP_PORT`` and using the default is the
    failure that starts a server on a port nobody is pointing at, which then
    reads as "the server is down" for as long as it takes someone to check.
    """
    monkeypatch.setenv("LINKEDIN_HTTP_PORT", bad)
    with pytest.raises(SystemExit):
        transport.http_port()


def test_a_port_already_bound_is_refused_before_anything_starts(monkeypatch):
    """A bind failure inside uvicorn is a traceback; this is a sentence.

    The check is a real bind rather than a connect, because those answer
    different questions: connect asks whether something is SERVING, bind asks
    whether uvicorn will be able to take the port -- and a socket bound but not
    listening separates them.
    """
    held = socket.socket()
    held.bind((transport.HTTP_HOST, 0))
    port = held.getsockname()[1]
    try:
        assert transport._port_is_free(port) is False
        with pytest.raises(SystemExit) as raised:
            transport.serve_http(object(), port=port)
        assert str(port) in str(raised.value)
    finally:
        held.close()


def test_a_free_port_reads_as_free():
    """The control. Without it the check above passes on a function that
    always returns False, which would refuse every start."""
    probe = socket.socket()
    probe.bind((transport.HTTP_HOST, 0))
    port = probe.getsockname()[1]
    probe.close()
    assert transport._port_is_free(port) is True


# ---------------------------------------------------------------------------
# The bearer gate
# ---------------------------------------------------------------------------


class _Recorder:
    """A stand-in ASGI app that records whether it was reached at all."""

    def __init__(self) -> None:
        self.reached = 0
        self.scopes: list[dict] = []

    async def __call__(self, scope, receive, send) -> None:
        self.reached += 1
        self.scopes.append(scope)
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})


def _drive(app, headers: list[tuple[bytes, bytes]], scope_type: str = "http") -> dict:
    """Run one ASGI request through ``app`` and collect what it sent back."""
    sent: list[dict] = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {"type": scope_type, "headers": headers, "path": "/mcp", "method": "POST"}
    asyncio.get_event_loop_policy().new_event_loop().run_until_complete(
        app(scope, receive, send)
    )
    status = next((m["status"] for m in sent if m["type"] == "http.response.start"), None)
    body = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    return {"status": status, "body": body}


def test_the_right_token_reaches_the_app():
    """The control, and it goes first: without it every refusal below is
    satisfied by a gate that refuses everything, which is not a gate."""
    app = _Recorder()
    gated = transport.bearer_gate(app, "s3cret")
    answer = _drive(gated, [(b"authorization", b"Bearer s3cret")])
    assert answer["status"] == 200
    assert app.reached == 1


def test_a_request_with_no_authorization_header_is_refused():
    app = _Recorder()
    gated = transport.bearer_gate(app, "s3cret")
    answer = _drive(gated, [])
    assert answer["status"] == 401
    assert app.reached == 0, "the app was reached by an unauthenticated request"


def test_a_wrong_token_is_refused():
    app = _Recorder()
    gated = transport.bearer_gate(app, "s3cret")
    answer = _drive(gated, [(b"authorization", b"Bearer wrong")])
    assert answer["status"] == 401
    assert app.reached == 0


def test_a_token_that_is_a_prefix_of_the_real_one_is_refused():
    """The specific bug this guards: comparing with ``startswith``.

    A gate written that way accepts every prefix of the secret, which turns a
    32-character token into a one-character one for anyone willing to try 26
    of them. It passes all the tests above.
    """
    app = _Recorder()
    gated = transport.bearer_gate(app, "s3cret")
    assert _drive(gated, [(b"authorization", b"Bearer s3c")])["status"] == 401
    assert app.reached == 0


def test_a_token_the_real_one_is_a_prefix_of_is_refused():
    """The mirror bug: a gate that checks the presented value STARTS WITH the
    secret. Appending anything would then be accepted."""
    app = _Recorder()
    gated = transport.bearer_gate(app, "s3cret")
    assert _drive(gated, [(b"authorization", b"Bearer s3cret-and-more")])["status"] == 401
    assert app.reached == 0


def test_the_bearer_prefix_is_optional_but_the_token_is_not():
    """Accepting a bare token is a kindness to a caller that forgot the scheme;
    accepting the scheme with no token is not."""
    app = _Recorder()
    gated = transport.bearer_gate(app, "s3cret")
    assert _drive(gated, [(b"authorization", b"s3cret")])["status"] == 200
    assert _drive(gated, [(b"authorization", b"Bearer ")])["status"] == 401
    assert _drive(gated, [(b"authorization", b"Bearer")])["status"] == 401


def test_the_header_is_found_whatever_case_it_arrives_in():
    """ASGI lowercases header names, but nothing in the spec forbids a server
    from handing them over as sent. Matching case-sensitively would produce a
    gate that refuses valid requests from some servers and not others."""
    app = _Recorder()
    gated = transport.bearer_gate(app, "s3cret")
    assert _drive(gated, [(b"Authorization", b"Bearer s3cret")])["status"] == 200


def test_a_lifespan_message_passes_through_ungated():
    """A lifespan event is the server booting, not a caller knocking.

    Gating it would refuse the application's own startup and the server would
    never come up -- a failure that looks nothing like an auth problem and is
    therefore expensive to diagnose.
    """
    app = _Recorder()
    gated = transport.bearer_gate(app, "s3cret")
    _drive(gated, [], scope_type="lifespan")
    assert app.reached == 1


def test_the_refusal_names_the_variable_that_fixes_it():
    """A 401 with no explanation sends the reader to the wrong file."""
    gated = transport.bearer_gate(_Recorder(), "s3cret")
    body = _drive(gated, [])["body"].decode()
    assert "LINKEDIN_HTTP_TOKEN" in body


# ---------------------------------------------------------------------------
# mcp_probe: the claim a rename rests on, and the payload it must not print
# ---------------------------------------------------------------------------
#
# `test_navigation_is_never_derived` taints ANY `.url` attribute in this
# package, on the generalisation that a `.url` here was read off a page, a
# request or a response. That is true of `linkedin_server/` and it is right to
# be coarse -- enumerating the objects that may hold one would be a list to
# keep in step.
#
# `scripts/mcp_probe.py` is its first counterexample: an argparse Namespace
# holding an address the caller typed. The argument is now `dest="endpoint"`,
# which clears the guard -- and a rename that clears a guard is EXACTLY the
# move that hides a value from the check that was watching it. What separates
# the two is whether the claim behind the rename is itself checked. It is the
# first test below, and it is the reason the rename is allowed to stand.

_PROBE = _SCRIPTS / "mcp_probe.py"

#: Every module `mcp_probe.py` is permitted to import. Not "no playwright" --
#: an exact allowlist, because the interesting failure is a browser arriving
#: through something nobody thought to ban.
_PROBE_ALLOWED_IMPORTS = frozenset(
    {"__future__", "argparse", "json", "os", "sys", "time", "urllib"}
)


def test_mcp_probe_has_no_browser_surface():
    """THE CLAIM THE RENAME RESTS ON, made falsifiable.

    `options.url` became `options.endpoint` because nothing in that file can
    reach a browser, so the taint rule's premise does not hold there. If anyone
    ever teaches the probe to drive a page, that stops being true -- and
    without this test it would stop being true SILENTLY, because the guard that
    would have caught it is looking for an attribute the file no longer has.

    So this is the guard's replacement for that one file, and it is stricter:
    the guard tolerates a browser as long as nothing is printed, this tolerates
    no browser at all.
    """
    tree = ast.parse(_PROBE.read_text(encoding="utf-8"), filename=_PROBE.name)

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])

    assert imported <= _PROBE_ALLOWED_IMPORTS, (
        "mcp_probe.py imports %s, which is outside the stdlib set its "
        "`dest=\"endpoint\"` rename depends on. If it now reaches a browser, "
        "the navigation guard must see its urls again -- rename the argparse "
        "dest back to `url` rather than widening this list."
        % sorted(imported - _PROBE_ALLOWED_IMPORTS)
    )


def test_the_probe_still_takes_the_flag_its_callers_pass():
    """The rename moved the ATTRIBUTE, and must not have moved the FLAG.

    `start_server.ps1` and the cutover runbook both pass `--url`. A rename that
    silently changed the command line would have broken the restart command --
    which is the one thing this whole wave exists to deliver -- and it would
    have broken it in a script whose failure output nobody reads until a
    cutover.
    """
    source = _PROBE.read_text(encoding="utf-8")
    assert '"--url"' in source
    assert 'dest="endpoint"' in source


def test_a_tool_that_was_never_measured_has_its_payload_withheld():
    """The leak the navigation guard pointed at by accident.

    It flagged this file for `options.url`, which is caller-supplied and
    harmless. But the line it flagged also prints `call_result` -- the verbatim
    result of ANY tool `--call` names. `linkedin_my_profile` would put the
    operator's profile, vanity slug and all, into whatever transcript ran the
    probe. That is the channel all three slug leaks of 2026-09-03 used.
    """
    probe = _load(_PROBE)
    payload = {
        "structuredContent": {
            "public_identifier": "a-vanity-slug",
            "headline": "some headline",
            "connections": 500,
        }
    }
    rendered = probe._render_call_result("linkedin_my_profile", payload)

    assert "call_result" not in rendered
    flat = repr(rendered)
    assert "a-vanity-slug" not in flat
    assert "some headline" not in flat
    assert "500" not in flat, "a value survived into the shape"


def test_the_shape_reports_the_keys_and_the_types_and_nothing_else():
    """A shape must stay ANSWERABLE without being informative about content.

    Reporting nothing would make the probe useless for "did the call come back
    with what it should"; reporting a summary would be a second thing to trust.
    Keys plus type names is the line: it cannot reconstruct what it describes.
    """
    probe = _load(_PROBE)
    rendered = probe._render_call_result(
        "linkedin_my_profile", {"structuredContent": {"slug": "x", "count": 3}}
    )
    assert rendered["call_result_shape"] == {"count": "int", "slug": "str"}
    assert "withheld" in repr(rendered)


#: A SLUG-SHAPED LITERAL, and it has to be shape-valid to be the test.
#:
#: The block below proves that text content does not survive into a shape. A
#: bland string would prove that some string did not survive; only a string
#: wearing the shape of the thing that actually leaked proves the class. And
#: assembling it at runtime would hide it from `test_no_committed_identity`,
#: blinding that sweep to a real value pasted into this file later -- the exact
#: reasoning its own entries give.
#:
#: IT CARRIES A SANCTIONED TOKEN RATHER THAN A DECLARATION, and the difference
#: is not cosmetic. `a-real-person` is in that guard's `SYNTHETIC_SLUG_TOKENS`
#: -- its ruling that a slug containing it cannot be anyone's -- so this value
#: needs no entry in `DECLARED_PLANTS` at all.
#:
#: The declaration was written first and then withdrawn, because it is the
#: WORSE of the two. A `("tests/test_transport.py", "linkedin slug"): 1` entry
#: tolerates ONE slug in this file whatever it is, so a real one pasted in
#: later passes. The token exempts this VALUE and nothing else. Measured: with
#: the literal below the file reads clean, and the same file plus one
#: real-looking slug goes red.
A_SLUG_SHAPED_REFUSAL = "refused /in/synthetic-not-a-real-person/"


def test_a_text_block_result_is_counted_not_quoted():
    """The other payload shape. Text blocks are where a refusal's prose lands,
    and a refusal naming what it refused was leak number one."""
    probe = _load(_PROBE)
    rendered = probe._render_call_result(
        "linkedin_my_profile",
        {"content": [{"text": A_SLUG_SHAPED_REFUSAL}, {"text": "second"}]},
    )
    assert rendered["call_result_shape"] == {"content_blocks": 2}
    assert "synthetic-not-a-real-person" not in repr(rendered)


def test_the_measured_diagnostic_is_still_printed_in_full():
    """The control, and it decides whether the rule above is a rule or a wall.

    `linkedin_cdp_status` is what the cutover runbook calls and what proves
    attach mode is live. If withholding applied to it too, the probe would pass
    every test here while telling the operator nothing at the one moment he
    needs it.
    """
    probe = _load(_PROBE)
    body = {"reachable": True, "active_browser_mode": "attach"}
    rendered = probe._render_call_result(
        "linkedin_cdp_status", {"structuredContent": body}
    )
    assert rendered == {"call_result": body}


def test_the_printable_list_is_exactly_what_was_measured():
    """Adding a name here is a claim that a tool returns no identity.

    `_redact` was admitted to the navigation guard's sanitiser list on the
    strength of its NAME and turned out to carry no slug rule at all. This
    pins the list so that widening it is a deliberate edit with a test to
    change, not a quiet append.
    """
    probe = _load(_PROBE)
    assert probe._PRINTABLE_IN_FULL == frozenset({"linkedin_cdp_status"})
    assert "linkedin_my_profile" not in probe._PRINTABLE_IN_FULL
    assert "linkedin_connections" not in probe._PRINTABLE_IN_FULL

