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
   capitalised words stops the reader, using ``shape.looks_name_shaped`` --
   the SAME rule the redactor applies, deliberately not a cleverer one. Two
   name detectors disagreeing is worse than one being imperfect.

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
    assert "1 control label" in out["why"]


async def test_ordinary_composer_labels_pass():
    """THE PASSING CASE, without which the two refusals prove nothing.

    A reader that refused everything would satisfy both tests above while
    making the capability permanently dead -- and a reader that never answers
    looks exactly like a surface that has nothing to say.
    """
    page = _Page(fields=["Send", "Open send options", "Enter message recipients"])
    out = await dom.read_compose_fields(page)
    # THE SUCCESS PATH CARRIES NO "refused" KEY AT ALL, which is the profile
    # editor's own convention: a refusal cannot be misread as an empty result
    # because the two shapes have different keys.
    assert "refused" not in out or out["refused"] is None
    assert out["recipients_selected"] == 0
    fields = out.get("fields")
    assert fields is not None, out
    assert [f["name"] for f in fields] == [
        "Send",
        "Open send options",
        "Enter message recipients",
    ]


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


def test_the_guard_uses_the_redactors_own_rule():
    """One rule, asked two ways -- not two rules that can drift apart.

    A second, cleverer name detector would disagree with the redactor
    somewhere, and the direction that matters is the one where the guard
    PASSES something the redactor would have blanked.
    """
    assert shape.looks_name_shaped("Ada Lovelace will send message") is True
    assert shape.looks_name_shaped("Send") is False
    assert shape.looks_name_shaped("Enter message recipients") is False
    assert shape.looks_name_shaped("Open send options") is False
    assert shape.looks_name_shaped("InMail") is False

    # A BARE NAME, CARRYING NONE OF THE SURROUNDING PHRASE. This case was
    # ADDED AFTER A MUTATION GOT THROUGH: replacing the redactor's rule with
    # `" will send " in text` passed every assertion above, because every
    # name-shaped example happened to contain that phrase. The cases agreed
    # with the right answer without DISCRIMINATING between the two rules,
    # which is the same defect as a corpus that cannot fail.
    assert shape.looks_name_shaped("Ada Lovelace") is True

    # And the predicate agrees with the redactor it was derived from, across
    # cases that pull in both directions.
    for text in (
        "Ada Lovelace will send message",
        "Ada Lovelace",
        "Send",
        "InMail",
        "Enter message recipients",
    ):
        blanked = shape.census_redact_rare(text, 1) != text
        assert blanked == shape.looks_name_shaped(text), text


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
