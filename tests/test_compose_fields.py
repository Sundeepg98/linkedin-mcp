"""The composer's dispatch modes, and why no label reaches this process.

WHY THIS READER EXISTS, and it is not the message body's name. The composer
draws TWO SEND-MODE RADIOS, one checked, and the census reduces both --
``<redacted>`` and ``<redacted> to <redacted>``. **He is on Premium Career,
and one of those modes may be an InMail**: a metered allowance, not a free
action. So the unreadable choice is potentially the difference between sending
a message and SPENDING ONE OF HIS CREDITS, and a gate that cannot tell him
whether an action costs him something is not a gate, it is a formality.

WHAT CHANGED ON 2026-09-02, because this file used to assert the opposite of
half of what it now asserts.

**It was aimed at the wrong container.** The reader anchored on ``Send`` and
scoped to that control's nearest ``form``. The dispatch radios are in NO form
at all -- ``containers {"none": 1}``, measured 2026-08-31 and again 2026-09-02
-- so it had never read them. The two shapes it did return described two
unrelated buttons that happen to sit inside ``form#0``.

**And it published raw labels into Python and guarded them there.** That made
``shape.looks_name_shaped`` the only thing between his name and the output, on
the one surface whose labels ARE his name. That predicate FAILED OPEN on the
checked default for a day and a half, because the run rule it inherited from
the census declines to match a capitalised word at position 0.

So the shaping moved INTO THE PAGE. ``dom.COMPOSE_MODES_JS`` resolves each
radio's accessible name, reduces it to counts and a name-free tail, and returns
that. **The raw label never enters this process, on any path, refusals
included** -- which is what the tests below are mostly about. The guard is now
a second line rather than the only one, and a second line is worth having
precisely because the first one was wrong once.

THE STRUCTURAL CLAIM, and it is asserted rather than assumed: on this surface
``input[type=radio]`` is EXACTLY TWO across 77 controls, with exactly one
checked, and ``div[role=textbox]`` is exactly one. Anything else means the page
is not the page this was built against, and the reader refuses rather than
guessing which control is a send mode.
"""

import importlib.util
import inspect
import json
import os
import shutil
import subprocess
import tempfile
import textwrap

import pytest

from linkedin_server import dom, shape


class _Page:
    """A page with a recipient count and a canned COMPOSE_MODES_JS reading.

    THE DOUBLE RETURNS THE SCRIPT'S SHAPE, not the wrapper's answer. A double
    that returned a ready-made ``refused`` would be simulating a contract the
    script does not have -- and a double that disagreed with the real script
    would be worse than no double, which this file learned the hard way: the
    previous one returned ``container_kind: "form"`` for a reading the real
    script could only ever have labelled ``role=dialog``.
    """

    def __init__(self, recipients=0, reading=None, raises=None):
        self.recipients = recipients
        self.reading = reading
        self.raises = raises
        self.evaluated = False
        self.cfg = None

    def locator(self, _selector):
        page = self

        class _Loc:
            async def count(self):
                if page.raises is not None:
                    raise page.raises
                return page.recipients

        return _Loc()

    async def evaluate(self, _script, cfg=None):
        self.evaluated = True
        self.cfg = cfg
        return self.reading


def _reading(modes=None, radios=2, checked=1, boxes=1, refused=None, body=True):
    """The script's return shape, with the measured surface as the default."""
    return {
        "radio_count": radios,
        "checked_count": checked,
        "textbox_count": boxes,
        "body_present": body,
        "body_is_editable": body,
        "body_name_source": "aria-label" if body else None,
        "modes": modes if modes is not None else [],
        "refused": refused,
    }


#: The two modes as the live surface draws them, shaped. Committing THIS is
#: safe where committing the labels is not, which is the whole design.
MEASURED_MODES = [
    {"runs": 1, "joined_by_to": False, "tail": "will send message",
     "checked": True, "disabled": False},
    {"runs": 2, "joined_by_to": True, "tail": "will send message",
     "checked": False, "disabled": False},
]


# ---------------------------------------------------------------------------
# 1. The recipient guard, which runs before anything is read
# ---------------------------------------------------------------------------


async def test_a_selected_recipient_refuses_and_reads_nothing():
    """THE GUARD THAT CARRIES THE SELF-OWNERSHIP ARGUMENT.

    A composer with somebody in it is not a container this server may publish
    the labels of, and the refusal must happen BEFORE anything is read -- so
    the assertion is that the script never ran, not merely that the reading
    was dropped afterwards.
    """
    page = _Page(recipients=1, reading=_reading(MEASURED_MODES))
    out = await dom.read_compose_fields(page)
    assert out["refused"] == "recipient_already_selected"
    assert "modes" not in out
    assert page.evaluated is False, "it read the composer before refusing"


async def test_an_unreadable_recipient_count_refuses_rather_than_assuming_zero():
    """Zero recipients is a MEASUREMENT, and an exception is not that."""
    page = _Page(raises=RuntimeError("detached"), reading=_reading(MEASURED_MODES))
    out = await dom.read_compose_fields(page)
    assert out["refused"] == "recipient_count_unreadable"
    assert page.evaluated is False


# ---------------------------------------------------------------------------
# 2. The answer
# ---------------------------------------------------------------------------


async def test_the_two_modes_come_back_distinguishable_and_nameless():
    """THE CAPABILITY, and every field in it is safe to commit.

    One capitalised run without ``to``, against two joined by it, both before
    the same name-free tail. That is enough to say WHICH MODE IS CHECKED --
    which is the question -- and it is storable where the label is not.
    """
    page = _Page(reading=_reading(MEASURED_MODES))
    out = await dom.read_compose_fields(page)
    assert "refused" not in out
    assert out["recipients_selected"] == 0

    modes = out["modes"]
    assert len(modes) == 2
    assert (modes[0]["runs"], modes[0]["joined_by_to"]) == (1, False)
    assert (modes[1]["runs"], modes[1]["joined_by_to"]) == (2, True)
    assert modes[0]["tail"] == modes[1]["tail"] == "will send message"
    # WHICH ONE IS DEFAULT, which is the whole point of reading this surface.
    assert [m["checked"] for m in modes] == [True, False]


async def test_the_two_modes_are_distinguishable_by_shape_alone():
    """If the shapes collide, the discriminator answers nothing.

    Two DIFFERENT modes must produce two DIFFERENT descriptors with no name
    involved. A descriptor that could not tell them apart would leave the
    credit question exactly where it was while looking like progress.
    """
    page = _Page(reading=_reading(MEASURED_MODES))
    out = await dom.read_compose_fields(page)
    a, b = out["modes"]
    assert (a["runs"], a["joined_by_to"]) != (b["runs"], b["joined_by_to"])


async def test_the_body_is_reported_as_presence_and_kind_and_never_as_a_label():
    """THE BODY'S LABEL IS NEVER PUBLISHED, THEREFORE NEVER GUARDED.

    This is a decision, not an omission, and it has two halves.

    THE GUARD GATES PUBLICATION. A label that is never returned has nothing to
    gate, so running ``looks_name_shaped`` over it would buy nothing.

    AND IT WOULD COST SOMETHING REAL. The split predicate matches a capitalised
    word at position 0, which means ordinary furniture trips it -- the body's
    own accessible name is something like ``Write a message``. Feeding that to
    the guard would make this reader refuse forever on its own placeholder.
    That is correct behaviour for a publication gate and the wrong question to
    ask of it; the note on :data:`shape._NAME_SHAPE_RUN` says so where the next
    caller will find it.
    """
    page = _Page(reading=_reading(MEASURED_MODES))
    out = await dom.read_compose_fields(page)
    body = out["body"]
    assert body == {
        "present": True,
        "is_editable": True,
        # A KIND, never the name.
        "name_source": "aria-label",
    }
    assert "name" not in body and "label" not in body


# ---------------------------------------------------------------------------
# 3. The whole permission: no raw label, on any path
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "reading",
    [
        _reading(MEASURED_MODES),
        _reading(radios=3, refused="radio_count_not_two"),
        _reading(checked=0, refused="checked_count_not_one"),
        _reading(checked=2, refused="checked_count_not_one"),
        _reading(boxes=0, refused="textbox_count_not_one"),
        _reading(refused="label_carried_no_run"),
        _reading(refused="shaping_unavailable"),
    ],
    ids=["success", "three_radios", "none_checked", "two_checked",
         "no_textbox", "no_run", "no_shaping"],
)
async def test_no_label_text_survives_into_any_answer(reading):
    """THE WHOLE PERMISSION, asserted on every return path this reader has.

    A refusal that quotes what it refused is the leak wearing an apology, so
    the refusals are searched as hard as the success. The ENTIRE reply is
    stringified rather than only the fields meant to carry text, because a leak
    that arrived through an unexpected key would still be a leak.
    """
    page = _Page(reading=reading)
    out = await dom.read_compose_fields(page)
    blob = str(out)
    for token in ("Ada", "Lovelace", "Grace", "Hopper", "will send message"):
        if token == "will send message" and "modes" in out:
            # The name-free TAIL is deliberately returned; it is what survives
            # the last capitalised run and is the storable half of the answer.
            continue
        assert token not in blob, (token, blob)


async def test_a_refusal_carries_the_counts_and_no_modes():
    """A refusal must not hand back a partial reading.

    Returning the modes it managed to shape before refusing would make the
    refusal advisory, and a caller that reads past a refusal is a caller acting
    on data the reader declined to stand behind.
    """
    page = _Page(reading=_reading([MEASURED_MODES[0]], radios=3,
                                  refused="radio_count_not_two"))
    out = await dom.read_compose_fields(page)
    assert out["refused"] == "radio_count_not_two"
    assert "modes" not in out
    assert out["radio_count"] == 3
    assert "3 radio(s)" in out["why"]


async def test_a_tail_that_still_carries_a_name_is_refused_at_the_boundary():
    """THE SECOND LINE, SHOWN FIRING. Until this existed it was a claim.

    ``tail`` arrives from the page asserted name-free -- it is what SURVIVES
    the last capitalised run, so by construction it cannot contain one. This
    drives a reading where that construction has broken, which is exactly the
    regression the in-page design cannot self-report: if the page's shaping
    were wrong, the page would still say it was right.

    So the boundary re-asks the question with an independent implementation of
    the same rule, and refuses. **The tails are not returned**, because a tail
    that failed this check is the single string on this path most likely to be
    a name.

    It has never fired in production. That is the expected state for a boundary
    check and not a reason to delete it -- the reason to keep it is that the
    page cannot be trusted to detect its own regression, and the reason to test
    it is that a check nobody has seen fail certifies nothing.
    """
    page = _Page(reading=_reading([
        {"runs": 1, "joined_by_to": False, "tail": "Ada Lovelace",
         "checked": True, "disabled": False},
        {"runs": 2, "joined_by_to": True, "tail": "will send message",
         "checked": False, "disabled": False},
    ]))
    out = await dom.read_compose_fields(page)
    assert out["refused"] == "page_shaping_returned_a_name"
    assert "modes" not in out
    assert "1 of 2 tails" in out["why"]
    for token in ("Ada", "Lovelace"):
        assert token not in str(out), (token, out)


def test_the_guard_has_a_production_caller():
    """An uncalled guard is a comment, and this file said otherwise for a while.

    THE RE-ANCHORING LEFT ``shape.looks_name_shaped`` WITH NO CALLER while
    three docstrings and a commit message called it defence in depth. The claim
    was false for exactly as long as nobody checked, which is the shape of
    ``read_settings_surface`` -- dead for ten days with its own comment noting
    it was uncalled.

    So the claim is now asserted rather than repeated. If a future edit removes
    the boundary check, this fails and whoever removed it has to either restore
    it or stop calling the predicate a second line.
    """
    import inspect

    source = inspect.getsource(dom.read_compose_fields)
    assert "shape.looks_name_shaped(" in source
    assert "page_shaping_returned_a_name" in source


def test_every_structural_refusal_has_a_reason_written_for_it():
    """A refusal code with no sentence behind it is a code nobody can act on.

    The reader looks its reason up by key, so a code the script can emit and
    the table does not carry would raise ``KeyError`` in front of the operator
    instead of explaining itself.
    """
    emitted = {
        "radio_count_not_two",
        "checked_count_not_one",
        "textbox_count_not_one",
        "label_carried_no_run",
        "shaping_unavailable",
    }
    assert set(dom._COMPOSE_REFUSALS) == emitted
    for code in emitted:
        assert code in dom.COMPOSE_MODES_JS, f"{code} is never emitted"
        assert len(dom._COMPOSE_REFUSALS[code]) > 80, code


# ---------------------------------------------------------------------------
# 4. The script itself, structurally
# ---------------------------------------------------------------------------


def test_the_compose_script_returns_no_unshaped_label():
    """THE ASSERTION THE WHOLE DESIGN RESTS ON, checked on the source.

    Every behavioural test above drives a DOUBLE, so none of them can see what
    the real script would return -- which is exactly how the old
    ``container_kind`` defect survived. This one reads the shipped source.

    The rule: the only thing a resolved name may flow into is ``shapeOf``. If
    a future edit pushes ``raw`` onto ``out``, or returns it from the script,
    this fails.
    """
    js = dom.COMPOSE_MODES_JS
    # The name is resolved into a local and consumed by the shaper. Any OTHER
    # use of `.raw` is a path this test exists to refuse.
    raw_uses = [line.strip() for line in js.splitlines() if ".raw" in line]
    assert raw_uses == ["const shaped = shapeOf(nameOf(el).raw);"], raw_uses

    # Nothing named like a label may be assigned onto the returned object.
    for banned in ("out.label", "out.name", "out.raw", "label:", "name:"):
        assert banned not in js, banned

    # The keys the script may put on a mode are enumerated, so a new one has to
    # be added here deliberately rather than ride in.
    body = js[js.index("out.modes.push("):]
    pushed = body[: body.index("});")]
    assert sorted(
        line.split(":")[0].strip()
        for line in pushed.splitlines()
        if ":" in line and not line.strip().startswith("//")
    ) == ["checked", "disabled", "joined_by_to", "runs", "tail"]


def test_the_run_rule_is_handed_in_rather_than_rewritten_in_javascript():
    """ONE PREDICATE, TWO ENGINES -- the drift this package already paid for.

    A hand-written copy of the run rule in JavaScript would agree with the
    Python one until somebody edited one of them, which is precisely the defect
    ``_NAME_SHAPE_RUN`` was split out to end. So the pattern is passed through
    ``cfg`` and compiled in the page, and this asserts there is no second copy.
    """
    js = dom.COMPOSE_MODES_JS
    assert "cfg.nameShapeRun" in js
    assert "new RegExp(cfg.nameShapeRun" in js
    # No regex LITERAL carrying a capital-letter class -- that would be a
    # second predicate. (The one literal present splits on whitespace.)
    assert "[A-Z]" not in js, "the run rule has been copied into the script"

    source = inspect.getsource(dom.read_compose_modes)
    assert "shape.name_shape_run_pattern()" in source


def test_the_reader_injects_no_script_of_its_own():
    """The narrowness of the twelfth waiver, asserted where it is spent.

    THIS TEST REPLACED ITS OWN OPPOSITE. It was
    ``test_no_second_injected_script_was_added_for_this_surface`` and asserted
    that this surface added NO script -- written so that a second one would
    have to argue for itself rather than drift in. It did its job: the argument
    happened, it is recorded with the twelfth waiver in
    ``tests/test_readonly.py``, and the ruling was that reach could have been
    bought by widening ``EDITOR_FIELDS_JS`` but privacy could not.

    So the check becomes NARROWNESS rather than absence: exactly one new
    script, run from exactly one wrapper, and the reader itself still injects
    nothing.
    """
    reader = inspect.getsource(dom.read_compose_fields)
    assert "page.evaluate" not in reader, reader
    assert "read_compose_modes" in reader

    wrapper = inspect.getsource(dom.read_compose_modes)
    assert wrapper.count("page.evaluate") == 1
    assert "# readonly-ok" in wrapper
    assert "COMPOSE_MODES_JS" in wrapper


def test_the_container_kind_now_names_what_it_found():
    """The DOUBLE and the SCRIPT disagreed, and the double was the plausible one.

    ``EDITOR_FIELDS_JS`` computed ``tag === 'dialog' ? 'dialog' : 'role=dialog'``
    under a comment claiming its selector "admits exactly two things" -- true
    while the selector was the editor's, false from the moment it became an
    argument. ``read_compose_fields`` passed ``"form"``, so every form was
    labelled ``role=dialog``. Nothing branched on the value, so nothing failed;
    the old double in this file returned ``"form"``, a string the real script
    could not produce, and every test that read it was asserting against a
    fiction.

    Asserted on the shipped source of BOTH scripts, because the expression was
    duplicated and a fix to one would have left the other lying.

    AND IT IS ASSERTED ON CODE WITH THE COMMENTS STRIPPED, which this test
    learned by failing: the comment recording the fix QUOTES the old ternary to
    explain it, so a naive substring search over the whole source found the
    thing it was written to forbid, in the sentence forbidding it. That is the
    same shape as a comment quoting a forbidden pattern and a leak test naming
    its own subjects -- it keeps arriving in new costumes, and the answer is
    always to search what EXECUTES rather than what is written down.
    """
    for js in (dom.EDITOR_FIELDS_JS, dom.EDITOR_VALUES_JS):
        code = "\n".join(
            line for line in js.splitlines() if not line.strip().startswith("//")
        )
        assert "? 'dialog' : 'role=dialog'" not in code, "the old ternary is back"
        assert "containerTag === 'dialog' || containerTag === 'form'" in code
        assert "'role=' + containerRole" in code


# ---------------------------------------------------------------------------
# 5. The page and Python must shape identically
# ---------------------------------------------------------------------------


def _node() -> str | None:
    return shutil.which("node")


def _run_shape_of_in_node(cases):
    """Run the SHIPPED ``shapeOf`` under V8 and return its answers."""
    src = dom.COMPOSE_MODES_JS
    start = src.index("const shapeOf =")
    brace = src.index("{", start)
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                fn = src[start:i + 1]
                break
    else:  # pragma: no cover - unbalanced source would fail earlier
        raise AssertionError("could not extract shapeOf")

    driver = textwrap.dedent(
        """
        %s
        const cfg = { nameShapeRun: %s };
        console.log(JSON.stringify(%s.map((raw) => {
          const s = shapeOf(raw);
          return { raw, runs: s.runs, joined_by_to: s.joined_by_to, tail: s.tail };
        })));
        """
    ) % (fn, json.dumps(shape.name_shape_run_pattern()), json.dumps(cases))

    fd, path = tempfile.mkstemp(suffix=".mjs")
    os.close(fd)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(driver)
        proc = subprocess.run([_node(), path], capture_output=True, text=True)
    finally:
        os.remove(path)
    assert proc.returncode == 0, proc.stderr[:2000]
    return json.loads(proc.stdout)


SHAPING_CORPUS = [
    "Ada Lovelace will send message",
    "Ada Lovelace to Grace Hopper will send message",
    "Ada Lovelace",
    "Send",
    "InMail",
    "Enter message recipients",
    "Open send options",
    "Connect with Prince",
    "Click to stop following Acme",
    "will send message",
    "",
    "send",
    "A",
    "A B",
    "A to B",
    "O'Brien to Acme Corp will send message",
    "Jean-Luc Picard will send message",
    "Zoe  to  Acme will send message",
    "to Acme will send message",
    "Ada to Grace to Mary will send message",
    "Élodie will send message",
    "Ada Lovelace2 will send message",
    "X9 will send message",
]


def test_the_page_shaping_agrees_with_the_python_descriptor():
    """TWO ENGINES, ONE RULE -- and agreement measured rather than argued.

    The pattern has one definition, but the SHAPING LOGIC around it is written
    twice: once in :func:`shape.describe_name_shaped` and once in the script.
    Two implementations that agree today are two implementations that can
    disagree tomorrow, so this runs the SHIPPED ``shapeOf`` -- extracted from
    ``COMPOSE_MODES_JS`` by brace-matching, not transcribed -- under V8 and
    compares every case against Python.

    THERE IS NO DIVERGENCE ANY MORE, and how that happened is worth the
    sentence. This docstring used to record one as DELIBERATE: on zero runs
    the page returned ``null`` and Python returned the whole string,
    defended as safe because Python's caller already held it. The ASCII fix
    showed the defence was wrong -- a field documented "name-free by
    construction" carrying a name is a false statement whoever holds it --
    so Python returns ``None`` too.

    THE PAGE HAD THE RIGHT ANSWER FIRST, because there the wrong one would
    obviously have been the leak. Writing the rule where its consequence was
    visible produced the behaviour that turned out to be correct in both
    places -- which is an argument for shaping at the boundary, arriving
    from a third direction.
    """
    if _node() is None:
        pytest.skip(
            "THE CROSS-ENGINE SHAPING CHECK DID NOT RUN: node is not on PATH. "
            "The page-side shaping in COMPOSE_MODES_JS was NOT compared against "
            "shape.describe_name_shaped in this session, so a divergence "
            "between the two would not have been caught here. Every other test "
            "in this file drives a Python double and cannot see the script's "
            "real behaviour."
        )

    rows = _run_shape_of_in_node(SHAPING_CORPUS)
    assert len(rows) == len(SHAPING_CORPUS)

    divergences = []
    for row in rows:
        py = shape.describe_name_shaped(row["raw"])
        if (row["runs"], row["joined_by_to"], row["tail"]) != (
            py["runs"], py["joined_by_to"], py["tail"]
        ):
            divergences.append((row["raw"], row, py))
    assert not divergences, divergences

    # NOT VACUOUS: the zero-run branch is the one that used to differ, so the
    # corpus must actually reach it -- otherwise this would pass against two
    # implementations never compared where it mattered.
    zero_run = [r for r in rows if r["runs"] == 0]
    assert zero_run, "no zero-run case in the corpus"
    for row in zero_run:
        assert row["tail"] is None
        assert shape.describe_name_shaped(row["raw"])["tail"] is None


def test_the_shaping_check_is_loud_when_it_does_not_run():
    """Its skip is a sentence only because the config asks for reasons.

    ``pytest.skip`` prints a bare ``s`` unless the run requests skip reasons,
    so ``-ra`` in ``pytest.ini`` is what makes the check above announce that it
    did not run. Without it the skip is indistinguishable from a pass, which is
    the failure mode the sweep guard was rebuilt to avoid on 2026-09-02. The
    dependency lives in a different file from the design, so it is pinned.
    """
    import re as _re

    ini = (dom.Path(__file__).resolve().parent.parent / "pytest.ini"
           if hasattr(dom, "Path") else None)
    if ini is None:
        from pathlib import Path

        ini = Path(__file__).resolve().parent.parent / "pytest.ini"
    text = ini.read_text(encoding="utf-8")
    addopts = [ln for ln in text.splitlines() if ln.strip().startswith("addopts")]
    assert addopts, text
    assert _re.search(r"-ra\b", addopts[0]), addopts


def test_the_extractor_actually_found_the_shipped_function():
    """A harness that silently extracted nothing would pass every comparison.

    The control on the control: the slice must be the real ``shapeOf``, and it
    must carry the parts the comparison depends on.
    """
    if _node() is None:
        pytest.skip(
            "node is not on PATH, so the extractor was not exercised in this "
            "session -- see test_the_page_shaping_agrees_with_the_python_descriptor."
        )
    src = dom.COMPOSE_MODES_JS
    assert src.count("const shapeOf =") == 1
    rows = _run_shape_of_in_node(["Ada Lovelace to Grace Hopper will send message"])
    assert rows == [{
        "raw": "Ada Lovelace to Grace Hopper will send message",
        "runs": 2,
        "joined_by_to": True,
        "tail": "will send message",
    }]


def test_the_script_is_declared_where_scripts_are_reviewed():
    """An injected script nobody declared is one nobody reviewed.

    BOTH COMPOSER SCRIPTS ARE NAMED HERE FROM 2026-09-02, and the second one
    is why this test failed rather than quietly widening. ``dom.py`` gained
    ``SELECTED_RECIPIENT_JS`` when ``send_message`` shipped as the twelfth
    performable write, which took the count of executed scripts from 12 to 13.
    A count is the only thing that notices an ADDITION -- the membership line
    above it would have gone on passing with an undeclared thirteenth script
    in the tree -- so the count is what caught it.
    """
    spec = importlib.util.spec_from_file_location(
        "_readonly_check",
        os.path.join(os.path.dirname(__file__), "test_readonly.py"),
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert "COMPOSE_MODES_JS" in module.INJECTED_SCRIPTS
    # THE SECOND SCRIPT ON THE COMPOSER, and it is declared for the sharper
    # reason. COMPOSE_MODES_JS shapes a label already known to be HIS.
    # SELECTED_RECIPIENT_JS runs where a committed recipient is by definition
    # A THIRD PARTY, so every label it touches names somebody who is not him.
    #
    # WHAT IT DOES: it counts the committed recipients in the composer -- per
    # candidate selector, then de-duplicated -- and counts how many of them
    # carry the needle the caller handed in. WHY IT RETURNS INTEGERS ONLY:
    # the needle comparison is done INSIDE THE PAGE, for the reason
    # INVITE_NEEDLE_JS does the same, so no third party's name is ever pulled
    # into this process. There is deliberately no ``revealSingleMatch``
    # escape hatch either -- that flag exists so a PREVIEW can show him who he
    # would reach, and this script runs inside ``perform``, after he has
    # already confirmed, where there is nothing left to show and therefore no
    # reason for a name to exist here at all.
    assert "SELECTED_RECIPIENT_JS" in module.INJECTED_SCRIPTS
    # TWELVE UNTIL 2026-09-02, THIRTEEN SINCE. Not derived from
    # ``len(module.INJECTED_SCRIPTS)``, which happens to be 13 as well today:
    # EXECUTED_SCRIPTS is keyed by CALL SITE and INJECTED_SCRIPTS by NAME, so
    # one script executed from two places would make them differ, and a
    # derived assertion would silently accept exactly that.
    assert len(module.EXECUTED_SCRIPTS) == 13
