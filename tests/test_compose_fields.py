"""The composer's labels, and the two guards that stop them being published.

WHY THIS READER EXISTS, and it is not the message body's name. The composer
draws TWO SEND-MODE RADIOS, one checked, and the census reduces both --
``<redacted>`` and ``<redacted> to <redacted>``. **He is on Premium Career,
and one of those modes may be an InMail**: a metered allowance, not a free
action. So the unreadable choice is potentially the difference between sending
a message and SPENDING ONE OF HIS CREDITS, and a gate that cannot tell him
whether an action costs him something is not a gate, it is a formality.

WHAT THIS FILE ASSERTS is the two refusals, because they are the whole of the
permission:

1. **No recipient may be selected.** The self-ownership argument here is
   stronger than the profile editor's -- a composer with nobody in it contains
   no third party AT ALL. That is asserted rather than assumed, because once a
   recipient is chosen the labels start describing a conversation with a
   person in it and the argument evaporates.

2. **Nothing name-shaped is published.** Any label carrying a run of
   capitalised words -- INCLUDING ONE AT POSITION 0 -- stops the reader, using
   ``shape.looks_name_shaped``. Until 2026-09-02 this paragraph said that was
   deliberately the SAME rule the redactor applies. It is not, any more, and
   the reason is measured rather than argued: the composer's checked default
   radio is labelled ``<him> will send message``, a name at position 0, and
   the redactor's rule scores it zero runs. The shared predicate failed OPEN
   on the one label most likely to be his name and nothing else. The two
   predicates are now split, and the guard's is strictly the stricter -- see
   ``test_the_two_predicates_are_split_and_the_guard_is_stricter``.

AND NO NEW SCRIPT WAS ADDED. ``EDITOR_FIELDS_JS`` was already parameterised on
anchor, container and control selector, so this surface reuses it and costs no
``# readonly-ok`` waiver and no budget bump. That was checked before a second
script was written -- the question looked like it needed one and it needed a
keyword argument.
"""

from linkedin_server import dom, shape


class _Page:
    """A page with a recipient count and a canned editor-fields reading."""

    def __init__(self, recipients=0, fields=None, anchors=1, raises=None):
        self.recipients = recipients
        self.fields = fields
        # THE SCRIPT REPORTS COUNTS; the wrapper DERIVES the refusals from
        # them. A double that returned a ready-made "refused" would be
        # simulating a contract the script does not have.
        self.anchors = anchors
        self.raises = raises
        self.evaluated = False

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
        # THE RAW SCRIPT'S SHAPE, not the wrapper's. read_self_owned_editor_
        # fields post-processes this into `fields`, so a double that returned
        # the finished shape would be testing a contract that does not exist.
        return {
            "anchor_controls": self.anchors,
            "container_kind": "form",
            "controls_inside": len(self.fields or []),
            "controls": [
                {"name": n, "name_source": "aria-label", "tag": "button"}
                for n in self.fields or []
            ],
        }


async def test_a_selected_recipient_refuses_and_reads_nothing():
    """THE GUARD THAT CARRIES THE SELF-OWNERSHIP ARGUMENT.

    A composer with somebody in it is not a container this server may publish
    the labels of, and the refusal must happen BEFORE anything is read -- so
    the assertion is that the script never ran, not merely that the fields
    were dropped afterwards.
    """
    page = _Page(recipients=1)
    out = await dom.read_compose_fields(page)
    assert out["refused"] == "recipient_already_selected"
    assert "fields" not in out
    assert page.evaluated is False, "it read the container before refusing"


async def test_a_name_shaped_label_refuses_without_reporting_the_label():
    """THE SECOND GUARD, and the refusal must not itself be the disclosure.

    Reporting WHICH labels were name-shaped would publish exactly what the
    guard exists to withhold, so the refusal carries a COUNT and no strings.
    """
    page = _Page(fields=["Send", "Ada Lovelace will send message"])
    out = await dom.read_compose_fields(page)
    assert out["refused"] == "name_shaped_label_present"
    assert "fields" not in out
    assert "Ada" not in str(out), out
    assert "Lovelace" not in str(out), out
    # TWO, NOT ONE, AND THE CHANGE IS THE POINT. ``Send`` is name-shaped to the
    # guard's predicate since the 2026-09-02 split -- a capitalised word at
    # position 0 is exactly what the guard was widened to catch, and it cannot
    # tell a one-word verb from a one-word surname. The count is derived from
    # the labels rather than pinned to a literal, so a future widening moves
    # this number instead of silently agreeing with it.
    offending = [
        n for n in ["Send", "Ada Lovelace will send message"]
        if shape.looks_name_shaped(n)
    ]
    assert len(offending) == 2, offending
    assert "%d control label" % len(offending) in out["why"]


async def test_the_success_path_survives_though_no_measured_label_reaches_it():
    """THE PASSING CASE, now reachable only by a corpus that does not occur.

    THIS TEST CHANGED MEANING ON 2026-09-02 AND SAYS SO RATHER THAN QUIETLY
    MOVING ITS VALUES. It used to pass ``["Send", "Open send options", "Enter
    message recipients"]`` -- three real composer labels -- through the guard
    and out the success path. After the predicate split every one of those is
    name-shaped, because each opens with a capitalised word, so that corpus
    REFUSES and no substitution of values restores the old assertion.

    WHY THE CONTROL IS KEPT ANYWAY. Its job was to stop a reader that refuses
    unconditionally from looking identical to a working one, and that job did
    not go away: a mutation replacing the guard with ``return True`` must still
    be caught, and this is the only test that catches it.

    AND THE HONEST HALF, ASSERTED RATHER THAN LEFT IN PROSE: the corpus below
    is synthetic. Sentence case is how accessible names are written, so the
    second half pins that every label MEASURED on the live composer trips the
    guard -- recorded from the census in
    ``_audit/2026-08-31-linkedin-perform.md`` section 83. If a future predicate
    lets one of them through, this fails, and the passing corpus stops being a
    fiction nobody re-examined.
    """
    page = _Page(fields=["send", "open send options"])
    out = await dom.read_compose_fields(page)
    # THE SUCCESS PATH CARRIES NO "refused" KEY AT ALL, which is the profile
    # editor's own convention: a refusal cannot be misread as an empty result
    # because the two shapes have different keys.
    assert "refused" not in out or out["refused"] is None
    assert out["recipients_selected"] == 0
    fields = out.get("fields")
    assert fields is not None, out
    assert [f["name"] for f in fields] == ["send", "open send options"]

    # THE MEASURED COMPOSER. ``form#0`` holds ``Send``, ``Open send options``,
    # the recipient input, and two buttons whose names that census redacted.
    # NOT ONE of them reaches the branch above.
    for measured in ("Send", "Open send options", "Enter message recipients"):
        assert shape.looks_name_shaped(measured), measured


async def test_it_anchors_on_send_inside_the_form():
    """The parameters are the whole of what makes this a different surface."""
    page = _Page(fields=["Send"])
    await dom.read_compose_fields(page)
    assert page.cfg["anchorName"] == dom.MESSAGE_SEND_NAME == "Send"
    assert page.cfg["containerSelector"] == dom.MESSAGE_CONTAINER_SELECTOR == "form"


async def test_an_upstream_refusal_reaches_the_caller_with_its_reason_intact():
    """``ambiguous_anchor`` and friends must not be flattened into success.

    The editor reader's refusals are about the CONTAINER -- two Send controls,
    or none, or one with no form around it -- and each is a real answer this
    wrapper has no business improving on.

    THIS TEST WAS WEAKER THAN IT LOOKED AND A MUTATION PROVED IT. It used to
    pair with an explicit passthrough branch in the wrapper, and deleting that
    branch left the test GREEN -- because the fall-through handles a refusal
    identically: no ``fields`` key means nothing to name-check, so the reading
    is returned as it arrived. The branch was redundant, the test could not
    fail, and the two facts were the same fact.

    The branch is gone and this now asserts the property the REMAINING code
    provides: the reason survives, unimproved, and no ``fields`` key is
    invented for a container that was never read.
    """
    page = _Page(anchors=2, fields=["Send"])
    out = await dom.read_compose_fields(page)
    assert out["refused"] == "ambiguous_anchor"
    assert "fields" not in out
    # The reason text is the upstream reader's, not a summary of it.
    assert "Send" in str(out.get("reason", "")), out


async def test_an_unreadable_recipient_count_refuses_rather_than_assuming_zero():
    """Zero recipients and an unreadable count are different answers.

    Treating a failed read as "nobody is selected" would run the whole reader
    on a composer that might hold a person, which is the one thing the first
    guard exists to prevent.
    """
    page = _Page(raises=RuntimeError("detached"))
    out = await dom.read_compose_fields(page)
    assert out["refused"] == "recipient_count_unreadable"
    assert page.evaluated is False


def test_the_two_predicates_are_split_and_the_guard_is_stricter():
    """The guard STOPPED using the redactor's rule, and this asserts why.

    THIS TEST REPLACED ITS OWN OPPOSITE. Until 2026-09-02 it was
    ``test_the_guard_uses_the_redactors_own_rule`` and asserted that one rule
    served both callers, on the reasoning that two name detectors disagreeing
    is worse than one being imperfect. That reasoning was right about DRIFT and
    wrong about WHICH RULE TO SHARE, and the measurement that settled it is the
    first case below: the redactor scores ``<name> will send message`` at zero
    runs, so the guard it fed failed OPEN on the composer's checked default --
    the label most likely to be his name and nothing else.

    THE TWO QUESTIONS ARE NOT THE SAME QUESTION, which is the whole ruling:

    * ``census_redact_rare`` substitutes across a document-wide census.
      Teaching it about position 0 would blank ``Save``, ``Dismiss``, ``Jobs``,
      ``About`` -- every one-word control name seen once. A census that redacts
      its own vocabulary reports nothing.
    * ``looks_name_shaped`` decides whether a label may be PUBLISHED.
      Over-refusing costs a refusal; under-refusing costs a disclosure. The
      costs are not symmetric, so the guard does not inherit a predicate tuned
      for a counting instrument.

    DRIFT IS STILL THE HAZARD, so it is bounded rather than denied: the two are
    allowed to disagree in ONE DIRECTION ONLY, asserted below as containment.
    """
    # 1. THE MEASUREMENT THAT FORCED THE SPLIT. Both are name-shaped now; the
    #    first was False before, with a "name-free tail" of the whole string.
    checked_default = "Ada Lovelace will send message"
    other_mode = "Ada Lovelace to Grace Hopper will send message"
    assert shape.looks_name_shaped(checked_default) is True
    assert shape.describe_name_shaped(checked_default) == {
        "runs": 1,
        "joined_by_to": False,
        "tail": "will send message",
    }
    assert shape.describe_name_shaped(other_mode) == {
        "runs": 2,
        "joined_by_to": True,
        "tail": "will send message",
    }

    # 2. THE CENSUS KEEPS ITS OWN RULE, and this is the half that breaks loudly
    #    if somebody "simplifies" the split away by widening the shared pattern
    #    instead. These strings are the census's own vocabulary.
    for furniture in ("Save", "Dismiss", "Jobs", "About", "Send", "InMail"):
        assert shape.census_redact_rare(furniture, 1) == furniture, furniture

    # 3. THE PREDICATES DISAGREE, and a test that could not observe the
    #    disagreement would pass just as well against no split at all.
    disagreements = [
        text
        for text in ("Send", "InMail", "Enter message recipients", checked_default)
        if shape.looks_name_shaped(text) != (shape.census_redact_rare(text, 1) != text)
    ]
    assert disagreements, "the split is not observable, so it is not a split"

    # 4. CONTAINMENT -- THE ONE DIRECTION THE DRIFT MAY GO. The guard must match
    #    EVERYTHING the redactor blanks, and may match more. A guard that passed
    #    something the redactor would have blanked is precisely the failure the
    #    old shared-rule reasoning existed to prevent; it is now prevented by
    #    assertion rather than by sharing.
    for text in (
        checked_default,
        other_mode,
        "Ada Lovelace",
        "Connect with Prince",
        "Click to stop following Acme",
        "Send",
        "InMail",
        "Enter message recipients",
        "Open send options",
        "",
        "send",
    ):
        if shape.census_redact_rare(text, 1) != text:
            assert shape.looks_name_shaped(text), ("redactor blanked, guard passed", text)

    # 5. A BARE NAME, CARRYING NONE OF THE SURROUNDING PHRASE. Kept from the
    #    test this replaced: it was ADDED AFTER A MUTATION GOT THROUGH --
    #    replacing the rule with `" will send " in text` passed every case then,
    #    because every name-shaped example happened to contain that phrase.
    assert shape.looks_name_shaped("Ada Lovelace") is True

    # 6. STRUCTURAL, because 1-5 are behavioural and would all survive somebody
    #    deleting `_NAME_SHAPE_RUN` and re-widening `_CENSUS_CAPS_RUN` in place
    #    -- which is the one edit that reintroduces the census defect this split
    #    was made to avoid. The redactor must still name the census pattern; the
    #    guard and the descriptor must name the other one and NOT the census's.
    import ast
    import inspect
    import textwrap

    def _code_of(fn):
        """The function's CODE, with docstring and comments gone.

        Not a string replace of ``fn.__doc__``: Python 3.13 dedents docstrings
        at compile time, so ``__doc__`` no longer occurs verbatim in the source
        and the replace silently removes nothing -- which would leave this
        assertion satisfiable by PROSE, the exact failure mode it exists to
        catch. Unparsing the body drops the docstring node and every comment.
        """
        top = ast.parse(textwrap.dedent(inspect.getsource(fn))).body[0]
        # NARROWED RATHER THAN ASSUMED. `Module.body[0]` is typed `ast.stmt`,
        # which has no `.body` -- only some subclasses do. At runtime the source
        # of a function always parses to one FunctionDef (a decorator hangs off
        # the node rather than adding a statement), so the attribute is always
        # there; this states that instead of relying on it, and fails by name if
        # it ever stops being true.
        assert isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef)), top
        body = top.body
        first = body[0] if body else None
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            body = body[1:]
        return "\n".join(ast.unparse(node) for node in body)

    redactor = _code_of(shape.census_redact_rare)
    assert "_CENSUS_CAPS_RUN" in redactor, redactor
    assert "_NAME_SHAPE_RUN" not in redactor, redactor
    for fn in (shape.looks_name_shaped, shape.describe_name_shaped):
        code = _code_of(fn)
        assert "_NAME_SHAPE_RUN" in code, fn.__name__
        assert "_CENSUS_CAPS_RUN" not in code, fn.__name__


def test_no_second_injected_script_was_added_for_this_surface():
    """The reuse, asserted, because the alternative was a waiver.

    ``EDITOR_FIELDS_JS`` is parameterised on all three of anchor, container
    and control selector. A future edit that adds a composer-specific script
    would need a new ``# readonly-ok`` waiver and a budget bump, and it should
    have to justify that against this test rather than drift into it.
    """
    import inspect

    source = inspect.getsource(dom.read_compose_fields)
    assert "page.evaluate" not in source, source
    assert "read_self_owned_editor_fields" in source


# ---------------------------------------------------------------------------
# The discriminator: the guard refuses, and the reader still answers
# ---------------------------------------------------------------------------


async def test_a_refusal_still_reports_which_send_mode_is_checked():
    """THE POINT OF THE DISCRIMINATOR. Refusing must not mean answering nothing.

    The composer's two send modes differ STRUCTURALLY and the difference
    carries no name: one capitalised run without ``to``, against two runs
    joined by it, both before the same name-free tail. That is enough to say
    which mode is checked -- which is the question -- and it is storable where
    the label is not.
    """
    page = _Page(
        fields=[
            "Send",
            "Ada Lovelace will send message",
            "Ada Lovelace to Grace Hopper will send message",
        ]
    )
    out = await dom.read_compose_fields(page)
    assert out["refused"] == "name_shaped_label_present"

    # THREE, NOT TWO, SINCE THE 2026-09-02 SPLIT: ``Send`` is name-shaped to the
    # guard now, so this container's furniture is described alongside the two
    # radios. That is the over-refusal the split was known to buy, and it is why
    # the modes are selected BY TAIL rather than by position -- an index into
    # this list was only ever right while the container happened to hold nothing
    # else, and the reader is still aimed at ``form#0``, which holds several
    # things else.
    shapes = out["label_shapes"]
    assert len(shapes) == 3, shapes
    modes = [s for s in shapes if s["tail"] == "will send message"]
    assert len(modes) == 2, shapes
    assert modes[0]["runs"] == 1 and modes[0]["joined_by_to"] is False
    assert modes[1]["runs"] == 2 and modes[1]["joined_by_to"] is True
    # THE TAIL IS THE SAME ON BOTH and is what may be committed as a constant.
    assert modes[0]["tail"] == modes[1]["tail"] == "will send message"
    # AND THE FURNITURE IS STILL SEPARABLE FROM A MODE, which is what keeps the
    # answer readable while the container is too wide: ``Send`` COLLIDES with
    # the checked default on (runs, joined_by_to) and is separated only by the
    # tail. The discriminator is doing less work than its name suggests until
    # the reader is re-anchored on the radios.
    furniture = [s for s in shapes if s["tail"] != "will send message"]
    assert len(furniture) == 1 and furniture[0]["tail"] == "", shapes
    assert (furniture[0]["runs"], furniture[0]["joined_by_to"]) == (
        modes[0]["runs"],
        modes[0]["joined_by_to"],
    ), "the collision this comment describes stopped happening; re-read it"


async def test_no_part_of_a_name_survives_into_the_answer():
    """THE WHOLE PERMISSION, asserted on the returned object as a string.

    A shape that leaked one token of a name would be worse than a plain
    refusal, because it would arrive wearing the authority of a redacted
    thing. So the ENTIRE reply is searched, not just the fields meant to
    carry names.
    """
    page = _Page(fields=["Ada Lovelace to Grace Hopper will send message"])
    out = await dom.read_compose_fields(page)
    blob = str(out)
    for token in ("Ada", "Lovelace", "Grace", "Hopper"):
        assert token not in blob, (token, blob)


def test_every_tail_the_descriptor_returns_is_itself_name_free():
    """The descriptor's own invariant, checked rather than asserted in prose.

    ``tail`` is what survives the LAST capitalised run, so it cannot contain
    one -- but that is a claim about the regex, and a claim about a regex is
    the kind this package has been wrong about twice this week.
    """
    for text in (
        "Ada Lovelace will send message",
        "Ada Lovelace to Grace Hopper will send message",
        "Grace Hopper",
        "Send",
        "",
    ):
        tail = shape.describe_name_shaped(text)["tail"]
        assert not shape.looks_name_shaped(tail), (text, tail)


def test_the_two_modes_are_distinguishable_by_shape_alone():
    """If the shapes collide, the discriminator answers nothing.

    This is the property the whole design rests on: two DIFFERENT modes must
    produce two DIFFERENT descriptors, with no name involved. A descriptor
    that could not tell them apart would leave the credit question exactly
    where it was while looking like progress.
    """
    a = shape.describe_name_shaped("Ada Lovelace will send message")
    b = shape.describe_name_shaped("Ada Lovelace to Grace Hopper will send message")
    assert a != b
    assert (a["runs"], a["joined_by_to"]) != (b["runs"], b["joined_by_to"])
