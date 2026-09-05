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

import asyncio
import socket

import pytest

from linkedin_server import transport


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
