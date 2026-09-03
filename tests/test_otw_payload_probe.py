"""The Open To Work payload probe, held to the register's second law.

IT IS AN INSTRUMENT NOW. It has run against his live profile, it produced a
result, and it will be reached for again -- which is the moment this repo's
standing rule applies: **an instrument enters the register only if it has been
SHOWN FAILING**, and shown failing on the DISTINCT SHAPES of the defect it
claims to cover rather than on one of them. One demonstration proves a check
can fire and says nothing about what it is silent on.

## What the probe is for, stated as narrowly as it deserves

``_audit/_slice-otw-census.md`` established that the open-to-work editor is not
addressed by a url AT ALL -- it is fetched by an SDUI RPC from a button with no
href -- and that finding is the whole basis for ``set_open_to_work``'s
``url_template=None``. The analysis was taken by SAVING HIS PROFILE TO DISK:
1,177,077 characters, 92.7% of it flight payload. Those files were his name,
his employer, his connections and a third party's photo id, so they could not
be committed and were destroyed. **The measurement therefore had no instrument
behind it** -- a number in a document, ageing against a page LinkedIn keeps
changing.

The probe is that instrument, built so it can answer WITHOUT KEEPING ANYTHING:
counts of a closed vocabulary, no capture group anywhere, no output path.

## The three shapes it claims to catch, and each is mutated below

    a VANISHED RPC          saveAndFetchNextStepRequest gone from the payload
    a SERVERREQUEST APPEARS where the census counted zero for a control
    a TOKEN STOPS MATCHING  a screen id or control id renamed

Plus the defect the FIRST LIVE RUN exposed in the probe itself, which is the
fourth thing pinned here and the one worth reading:

    a SUBSTRING IS NOT A TOKEN

``str.count("edit")`` matched inside ``isEditFlow``, ``edited``, ``editor``,
``credit`` and ``editorial``, and reported 117 for a token that identifies
nothing. **Measured: a string containing ONE standalone ``edit`` counts SIX.**
It is the THIRD instance of that shape in a single day -- the receipt work hit
it as ``"saved"`` versus ``"saved list"``, where ``apply_job``'s own text
contains ``the SAVED tab`` so the short token fires on a CORRECT row.

**The fix is the MECHANISM, not the token.** Dropping ``edit`` would have
repaired one instance and left the next author to rediscover the class, so
every token is matched with identifier boundaries and the probe reports which
tokens the two methods disagree about. The general form, worth carrying: **a
discriminator must be a string that cannot appear inside another string you did
not mean, and nothing in the act of writing one tells you which you have.**

## What is NOT tested here, said plainly

Nothing in this file runs a browser or reaches LinkedIn. Every payload below is
invented markup-free text carrying the shapes under test. **So this proves the
probe's LOGIC and proves nothing about what LinkedIn's page currently
contains** -- that is what running it does, and the run reports its own limits.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

_PROBE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "_probe_open_to_work_payload.py"
)

#: THE PROBE, IMPORTED BY PATH rather than by package. ``scripts/`` is not a
#: package and the file is underscore-prefixed on purpose; importing it here is
#: safe for the reason its own guard exists -- module scope does nothing, and
#: ``tests/test_scripts_are_import_safe.py`` asserts that for every script.
_spec = importlib.util.spec_from_file_location("_otw_probe", _PROBE_PATH)
probe = importlib.util.module_from_spec(_spec)
sys.modules["_otw_probe"] = probe
_spec.loader.exec_module(probe)


# ---------------------------------------------------------------------------
# A substring is not a token
# ---------------------------------------------------------------------------


def test_a_short_token_counts_only_where_it_stands_alone():
    """THE DEFECT THE FIRST LIVE RUN EXPOSED, pinned at the mechanism.

    The naive count and the boundary count are asserted to DISAGREE on this
    corpus, which is what makes the assertion meaningful: if they agreed, the
    test would pass against the broken implementation too.
    """
    corpus = "isEditFlow edited editor credit editorial creditCard edit"
    assert corpus.count("edit") == 6, corpus.count("edit")
    assert probe._occurrences(corpus, "edit") == 1


def test_a_camelcase_token_was_never_affected():
    """THE CONTROL, so the fix is not credited with more than it did.

    ``clickThrough`` and its siblings were always unambiguous -- their counts
    on the live run were real. A fix that changed every number would be a
    different change from the one described.
    """
    corpus = "clickThrough clickThroughRate preClickThrough dismissMenu"
    for token, expected in (("clickThrough", 1), ("dismissMenu", 1)):
        assert probe._occurrences(corpus, token) == expected, token


def test_the_probe_reports_which_of_its_own_tokens_are_undiscriminating():
    """The vocabulary's can-it-discriminate check, which the first run lacked.

    It REPORTS rather than refuses, and that is deliberate: a token the two
    methods disagree about is not useless -- the boundary count is still
    correct -- but the naive reading of it was noise, and whoever reads the run
    should be told which numbers those were.

    IT IS A MEASUREMENT OF THE PAGE, not of the token in the abstract:
    ``edit`` is undiscriminating on a page full of ``editor`` and harmless on
    one without.
    """
    noisy = probe._undiscriminating_tokens("editor edited edit ServerRequest")
    assert "edit" in noisy, noisy
    naive, bounded = noisy["edit"]
    assert naive > bounded, (naive, bounded)
    assert "ServerRequest" not in noisy, noisy

    # AND IT IS SILENT ON A PAGE WHERE NOTHING IS AMBIGUOUS, so the check is
    # not simply always reporting something.
    assert probe._undiscriminating_tokens("ServerRequest SetState") == {}


# ---------------------------------------------------------------------------
# The three regression shapes, each mutated independently
# ---------------------------------------------------------------------------


def _payload(**overrides: str) -> str:
    """A payload carrying every vocabulary token once, unless overridden.

    BUILT FROM THE PROBE'S OWN VOCABULARY rather than typed out, so a token
    renamed in the probe cannot leave this corpus quietly describing the old
    one -- the same rule the selector fixtures follow.
    """
    parts = []
    for tokens in probe._VOCABULARY.values():
        for token in tokens:
            parts.append(overrides.get(token, token))
    parts.append("psettings psettings")
    return " ".join(parts)


def test_the_baseline_corpus_finds_every_token():
    """The corpus is not allowed to be quietly incomplete.

    Every mutation below is "one token removed from this". If the baseline
    were already missing tokens, a mutation could pass by removing something
    that was not there.
    """
    counts = probe._count_vocabulary(_payload())
    missing = [
        token
        for group in counts.values()
        for token, count in group.items()
        if count == 0
    ]
    assert not missing, missing


def test_a_vanished_editor_rpc_is_visible():
    """SHAPE ONE, and the most consequential single token on the page.

    ``saveAndFetchNextStepRequest`` is what the census identified as the thing
    the editor is fetched BY, and therefore the reason it has no url. If it
    disappears, the August analysis is describing a page that no longer exists
    and a human has to re-take it.
    """
    # BOTH SPELLINGS MUST GO, and the first draft of this test overrode only
    # the bare one and FAILED -- correctly. The vocabulary carries the fully
    # qualified `com.linkedin.sdui.requests...saveAndFetchNextStepRequest` as
    # well, and a dotted qualified name still boundary-matches the bare token,
    # because `.` is not an identifier character. That is the probe behaving
    # RIGHT: on the live page the bare token's count came entirely from the
    # dotted form. The corpus was wrong, not the counter.
    without = _payload(
        saveAndFetchNextStepRequest="somethingElseEntirely",
        **{
            "com.linkedin.sdui.requests.preferenceCollection"
            ".saveAndFetchNextStepRequest": "com.linkedin.sdui.gone"
        },
    )
    counts = probe._count_vocabulary(without)
    assert counts["the editor RPC"]["saveAndFetchNextStepRequest"] == 0
    # ... and the baseline finds it, so the assertion is not vacuous. TWO,
    # not one: the corpus carries both spellings and the bare token correctly
    # matches inside the dotted one, since `.` is not an identifier character.
    # Asserted as "more than none" rather than as an exact number, because the
    # claim here is that the mutation REMOVED something the baseline had.
    assert (
        probe._count_vocabulary(_payload())["the editor RPC"][
            "saveAndFetchNextStepRequest"
        ]
        > 0
    )


def test_a_serverrequest_appearing_is_visible():
    """SHAPE TWO. The census counted ZERO ServerRequest for `Show details`.

    A count is not an attribution -- that is what the structural reader below
    is for -- but a ServerRequest appearing inside that control's own region
    is exactly the change that would make the click dangerous, and it must not
    be silent.
    """
    region = '{"componentKey":"x","label":"Show details","actions":["Navigate"]}'
    before = probe._actions_for(region, "Show details")
    assert before["kinds"]["ServerRequest"] == 0, before
    assert before["kinds"]["Navigate"] == 1, before

    mutated = region.replace('["Navigate"]', '["Navigate","ServerRequest"]')
    after = probe._actions_for(mutated, "Show details")
    assert after["kinds"]["ServerRequest"] == 1, after


def test_a_renamed_screen_id_is_visible():
    """SHAPE THREE. A token that simply stops matching.

    The screen ids and the three ``opento_button_*`` control ids are how the
    census identified what the card draws. A rename is the quietest possible
    change to this page and the one a tally is best at catching.
    """
    # BOTH SPELLINGS AGAIN, for the reason recorded on the RPC test above.
    renamed = _payload(
        PrefCollectionDetailView="PrefCollectionOverview",
        **{
            "com.linkedin.sdui.flagshipnav.jobs.PrefCollectionDetailView":
                "com.linkedin.sdui.flagshipnav.jobs.PrefCollectionOverview"
        },
    )
    counts = probe._count_vocabulary(renamed)
    assert counts["screen ids"]["PrefCollectionDetailView"] == 0
    # More than none for the reason recorded on the RPC test: the bare token
    # matches inside the dotted spelling too, so the baseline is 2.
    assert probe._count_vocabulary(_payload())["screen ids"][
        "PrefCollectionDetailView"
    ] > 0


# ---------------------------------------------------------------------------
# The structural reader: what it attributes, and what it refuses to
# ---------------------------------------------------------------------------


def test_it_reads_the_actions_of_the_object_that_encloses_the_label():
    """ATTRIBUTION BY BALANCED BRACES, not by a byte window.

    A fixed window either clips a control's own actions or swallows its
    neighbour's, and NEITHER FAILURE IS VISIBLE IN THE OUTPUT -- it would
    report a number that looks exactly like a measurement. Walking out to a
    balanced pair follows the payload's own nesting.

    THE NEIGHBOUR IN THIS CORPUS IS THE POINT: a second control sits directly
    beside the first carrying a ServerRequest, and the reader must not
    attribute it.
    """
    payload = (
        '{"label":"Edit","actions":["SetState","SetState",'
        '"ServerRequest","saveAndFetchNextStepRequest"]}'
        ',{"label":"Show details","actions":["Navigate"]}'
    )
    edit = probe._actions_for(payload, "Edit")
    assert edit["refused"] is None, edit
    assert edit["kinds"]["SetState"] == 2, edit
    assert edit["kinds"]["ServerRequest"] == 1, edit
    assert edit["kinds"]["saveAndFetchNextStepRequest"] == 1, edit

    show = probe._actions_for(payload, "Show details")
    assert show["refused"] is None, show
    assert show["kinds"]["Navigate"] == 1, show
    # THE NEIGHBOUR'S ServerRequest IS NOT ATTRIBUTED HERE. This is the whole
    # claim of the structural reader over a windowed one.
    assert show["kinds"]["ServerRequest"] == 0, show


def test_it_refuses_a_label_that_appears_twice():
    """Two controls, one label -- refuse rather than take the first.

    Picking the first would be attribution by document order, which is the
    thing this package refuses everywhere else: in _comment_submit_gate when
    two controls share the name ``Comment``, in aim_invitation when a needle
    matches twice, in _live_control whenever a count is not one.
    """
    payload = '{"label":"Edit","actions":["SetState"]}{"label":"Edit","x":1}'
    found = probe._actions_for(payload, "Edit")
    assert found["occurrences"] == 2, found
    assert found["kinds"] is None
    assert "document order" in found["refused"], found


def test_it_refuses_a_label_that_is_absent_and_calls_that_a_finding():
    """Zero is not an error, it is the measurement.

    A label that has left the page is exactly the drift this probe exists to
    detect, so the refusal says so rather than reading as a malfunction.
    """
    found = probe._actions_for('{"label":"Something else"}', "Edit")
    assert found["occurrences"] == 0
    assert found["kinds"] is None
    assert "the finding" in found["refused"], found


def test_it_refuses_when_the_braces_do_not_balance():
    """The walk fails CLOSED, which is the direction to be wrong in.

    A brace inside a quoted string, or a payload chunked mid-object, makes the
    region unfindable or absurdly large. Both refuse. The alternative -- fall
    back to a fixed window -- would report a number indistinguishable from a
    real attribution.
    """
    found = probe._actions_for('no braces at all "Edit" here', "Edit")
    assert found["kinds"] is None
    assert "balanced" in found["refused"], found


def test_the_region_cap_refuses_rather_than_swallowing_the_page():
    """A region larger than one control's object is not one control's object.

    Asserted by construction rather than by belief: the label is buried inside
    an object far larger than the cap, and the reader declines it.
    """
    filler = "a" * (probe._REGION_CAP + 100)
    payload = '{"' + filler + '","label":"Edit","actions":["SetState"]}'
    found = probe._actions_for(payload, "Edit")
    assert found["kinds"] is None, found
    assert found["refused"], found


# ---------------------------------------------------------------------------
# The probe's own declared bounds, pinned so they cannot soften
# ---------------------------------------------------------------------------


def test_the_probe_intercepts_nothing_and_writes_nowhere():
    """THE TWO BOUNDS THAT ARE STRUCTURAL RATHER THAN POLICED.

    ``page.route`` is the mutation-capable call and ``.route`` is on
    ``readonly._MUTATION_CALL_PATTERNS``; ``page.on`` is passive and has no
    channel through which it could modify a request or a response. The bound
    is met by NOT TAKING the capability rather than by guarding it -- every
    guard written this week is one edit from being an absent guard, and a
    mechanism that does not exist cannot be edited into one.

    And the probe holds no output path at all, following
    ``scripts/_probe_messaging.py``, whose docstring records why: the version
    that had one used it, and the captures had to be destroyed by hand.
    """
    source = _PROBE_PATH.read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    assert ".route(" not in code, "the probe has acquired an interception path"
    assert "page.on(" in code, "the passive listener has gone"
    for writer in ("open(", ".write_text(", ".write_bytes(", ".mkdir("):
        assert writer not in code, writer


def test_no_extractor_in_the_probe_returns_a_capture_group():
    """NOTHING IS READ OUT OF THE PAYLOAD -- it is asked how many times it
    contains each fixed string.

    That is the property which makes the whole design safe rather than
    carefully guarded, and it is checked structurally: the two counting
    helpers return integers, and the unknown-kind reader returns a COUNT of
    distinct names rather than the names.
    """
    assert isinstance(probe._occurrences("abc", "b"), int)
    assert isinstance(probe._unknown_action_kinds("proto.sdui.actions.core.X"), int)
    counts = probe._count_vocabulary(_payload())
    for group in counts.values():
        for value in group.values():
            assert isinstance(value, bool) is False and isinstance(value, int)


@pytest.mark.parametrize("label", sorted(probe._CONTROL_LABELS))
def test_the_located_labels_are_ui_furniture_and_not_identifiers(label):
    """WHY LOCATING BY THESE TWO STRINGS IS DIFFERENT IN KIND.

    ``Show details`` and ``Edit`` are LinkedIn's own words on his own profile.
    Neither can be a person, a company or an id, which is what makes them
    admissible as locators where a componentkey or a urn would not be. Pinned
    as a set so a third locator has to be argued for rather than added.
    """
    assert label in ("Show details", "Edit"), label
    assert probe._CONTROL_LABELS == ("Show details", "Edit")


# ---------------------------------------------------------------------------
# The reference-following reader
#
# THE THIRD INSTRUMENT AIMED AT ONE QUESTION, and the register's second law
# applies to it exactly as it did to the two above: it enters only if it has
# been SHOWN FAILING, on the DISTINCT shapes of the defect it claims to cover.
#
# ITS CLAIM IS NARROW AND IT IS NEW. The tally cannot attribute an action to a
# control because it has no control; the enclosure reader cannot because on
# this page a label's own object holds no actions. This one follows the
# reference SDUI actually uses -- and the FIRST test below is the one that
# matters, because it proves the difference rather than asserting it: on the
# same corpus, the enclosure reader returns zeroes and this returns the
# Navigate.
#
# WHAT IS NOT PROVED HERE, said as plainly as the file above says it: every
# payload below is invented. These prove the reader's LOGIC against the shape
# the census described. They prove NOTHING about what LinkedIn's page
# currently contains, and if the real payload attaches actions by some other
# relation, the reader will REFUSE rather than answer -- which is the whole
# reason the refusals are tested one by one.
# ---------------------------------------------------------------------------

#: Keys shaped like the four the census actually measured. Invented values, as
#: every literal in this repo's tests must be -- but the SHAPES are real: an
#: ``auto-component-<uuid>`` container key, an opaque uuid on the Edit button,
#: and the one that matters for the safety argument, a key carrying a profile
#: slug.
_CK_CARD = "auto-component-9b53a9f4-1111-2222-3333-444455556666"
_CK_EDIT = "4623f77c-1a18-4c85-9f42-d4115640cc74"
_CK_VANITY = "jordan-blake-7f31_openToButton"


def _component(key: str, label: str, *, escaped: bool = False) -> str:
    """A component chunk: a key, and a label nested inside it. NO ACTIONS.

    THE ABSENCE OF ACTIONS HERE IS THE CORPUS'S WHOLE POINT. It is what the
    live payload looked like -- a balanced 297-character object around
    ``Show details`` holding zero action kinds -- and any corpus that put the
    actions beside the label would be testing the enclosure reader again
    under a new name.
    """
    quote = '\\"' if escaped else '"'

    def field(name: str, value: str) -> str:
        return quote + name + quote + ":" + quote + value + quote

    return (
        "{"
        + field("componentkey", key)
        + ",{q}component{q}:{{{q}children{q}:[{{{t}}}]}}".format(
            q=quote, t=field("text", label)
        )
        + "}"
    )


def _action_chunk(
    key: str,
    kinds: tuple[str, ...],
    *,
    escaped: bool = False,
    request_id: str = "",
) -> str:
    """An action chunk: the SAME key, and the action types it fires, in order.

    Written the way the payload writes them -- fully qualified
    ``proto.sdui.actions.core.<Kind>`` -- because the probe's counter matches
    a bare token inside a dotted name and a corpus using bare kinds would be
    testing an easier string than the live one.
    """
    quote = '\\"' if escaped else '"'
    actions = ",".join(
        "{" + quote + "$type" + quote + ":" + quote
        + "proto.sdui.actions.core." + kind + quote
        + (
            "," + quote + "requestId" + quote + ":" + quote + request_id + quote
            if request_id and kind == "ServerRequest"
            else ""
        )
        + "}"
        for kind in kinds
    )
    return (
        "{" + quote + "componentkey" + quote + ":" + quote + key + quote
        + "," + quote + "onTap" + quote + ":[" + actions + "]}"
    )


def _sdui(*chunks: str) -> str:
    """A payload: chunks side by side, the way flight rows sit side by side."""
    return ",".join(chunks)


def test_it_attributes_an_action_the_enclosure_reader_structurally_cannot():
    """THE CLAIM OF THIS INSTRUMENT, PROVED BY DIFFERENCE ON ONE CORPUS.

    This is the test the whole file turns on. Two readers, the same bytes:

        enclosure   the label's own object -- ZERO kinds, exactly as the live
                    run reported for ``Show details`` at 297 characters
        reference   follows the key to the action chunk -- the Navigate

    If the enclosure reader could answer this, the new one would be a second
    way of doing something already done. It cannot, and the assertion that it
    cannot is written FIRST so the difference is the subject rather than a
    footnote.
    """
    payload = _sdui(
        _component(_CK_CARD, "Show details"),
        _action_chunk(_CK_CARD, ("Navigate", "NavigateToScreen")),
    )

    enclosure = probe._actions_for(payload, "Show details")
    assert enclosure["refused"] is None, enclosure
    assert not any(enclosure["kinds"].values()), enclosure

    reference = probe._actions_by_reference(payload, "Show details")
    assert reference["refused"] is None, reference
    assert reference["kinds"]["Navigate"] == 1, reference
    assert reference["kinds"]["ServerRequest"] == 0, reference


def test_it_reads_the_order_and_not_only_the_set():
    """August recorded ``SetState x2, THEN ServerRequest``. Order is half of it.

    A reader that reported an unordered set would drop the half of the census
    finding that says the button writes two optimistic state values BEFORE
    the save request leaves -- which is the reason the census called that
    click the dangerous step rather than a save with some state attached.
    """
    payload = _sdui(
        _component(_CK_EDIT, "Edit"),
        _action_chunk(
            _CK_EDIT,
            ("SetState", "SetState", "ServerRequest"),
            request_id="saveAndFetchNextStepRequest",
        ),
    )
    found = probe._actions_by_reference(payload, "Edit")
    assert found["refused"] is None, found
    assert found["kinds"]["SetState"] == 2, found
    assert found["kinds"]["ServerRequest"] == 1, found
    assert found["kinds"]["saveAndFetchNextStepRequest"] == 1, found
    assert found["sequence"][0] == "SetState", found
    assert found["sequence"].index("SetState") < found["sequence"].index(
        "ServerRequest"
    ), found


def test_a_serverrequest_arriving_on_show_details_is_visible():
    """THE REGRESSION THAT WOULD SETTLE THE CLICK, MUTATED.

    August counted ZERO ``ServerRequest`` for ``Show details``. If LinkedIn
    has since attached one, the click stays refused permanently -- so the
    reader must be shown reporting that transition rather than trusted to.
    """
    before = _sdui(
        _component(_CK_CARD, "Show details"),
        _action_chunk(_CK_CARD, ("Navigate",)),
    )
    assert probe._actions_by_reference(before, "Show details")["kinds"][
        "ServerRequest"
    ] == 0

    after = _sdui(
        _component(_CK_CARD, "Show details"),
        _action_chunk(_CK_CARD, ("Navigate", "ServerRequest")),
    )
    found = probe._actions_by_reference(after, "Show details")
    assert found["refused"] is None, found
    assert found["kinds"]["ServerRequest"] == 1, found


def test_it_does_not_attribute_a_neighbours_action_chunk():
    """THE NEGATIVE CONTROL, and it is the one a windowed reader fails.

    ``Edit``'s action chunk sits directly beside ``Show details``' own -- that
    is the real adjacency on the card, an edit button that is an immediate
    sibling of the detail link. A reader scoped by distance attributes the
    ServerRequest to both. This one follows a key, so it attributes it to
    exactly one.
    """
    payload = _sdui(
        _component(_CK_CARD, "Show details"),
        _component(_CK_EDIT, "Edit"),
        _action_chunk(_CK_CARD, ("Navigate",)),
        _action_chunk(_CK_EDIT, ("SetState", "SetState", "ServerRequest")),
    )
    show = probe._actions_by_reference(payload, "Show details")
    assert show["refused"] is None, show
    assert show["kinds"]["Navigate"] == 1, show
    assert show["kinds"]["ServerRequest"] == 0, show
    assert show["kinds"]["SetState"] == 0, show

    edit = probe._actions_by_reference(payload, "Edit")
    assert edit["refused"] is None, edit
    assert edit["kinds"]["ServerRequest"] == 1, edit
    assert edit["kinds"]["Navigate"] == 0, edit


def test_a_duplicated_action_definition_is_not_double_counted():
    """MAX ACROSS SITES, NOT SUM, and the census is why -- the RIGHT half of it.

    THE TEMPTING CITATION IS THE WRONG ONE, and it was in this file's first
    draft: the census's "responsive duplicate pair, identical componentkey"
    was measured on ``button[aria-label="Open to"]``, a control neither reader
    here reads. ``Edit`` is DOM count 1 and unique. Citing it would have been
    a measurement of a NEIGHBOURING control standing in for this one, which is
    this wave's own section-91 defect committed in a justification.

    The on-point measurement is in the payload, where this reader looks:
    ``Edit``'s click action was resolved at TWO offsets, and the Open-to menu
    items appear 3x each, once per rendering variant. Summing would report
    ``SetState 4`` against an August baseline of ``SetState x2`` and
    MANUFACTURE a disagreement out of an aggregation choice -- an instrument
    inventing the finding it was built to look for.
    """
    duplicated = _sdui(
        _component(_CK_EDIT, "Edit"),
        _action_chunk(_CK_EDIT, ("SetState", "SetState", "ServerRequest")),
        _action_chunk(_CK_EDIT, ("SetState", "SetState", "ServerRequest")),
    )
    found = probe._actions_by_reference(duplicated, "Edit")
    assert found["refused"] is None, found
    assert found["reference_sites"] == 2, found
    assert found["kinds"]["SetState"] == 2, found
    assert found["kinds"]["ServerRequest"] == 1, found


def test_an_ancestor_object_is_not_an_action_chunk():
    """A key that also appears on the CONTAINER must not attribute the container.

    An object enclosing the component encloses its NEIGHBOURS too, so its
    kinds are the carousel's. Attributing them would be the fixed-window
    failure arrived at by walking instead of by a constant -- the same wrong
    answer, harder to see.
    """
    inner = _sdui(
        _component(_CK_CARD, "Show details"),
        _action_chunk(_CK_EDIT, ("ServerRequest",)),
    )
    payload = (
        '{"componentkey":"' + _CK_CARD + '","carousel":[' + inner + "],"
        '"trailing":"' + _CK_CARD + '"}'
        + "," + _action_chunk(_CK_CARD, ("Navigate",))
    )
    found = probe._actions_by_reference(payload, "Show details")
    assert found["refused"] is None, found
    assert found["ancestor_sites"] >= 1, found
    # The neighbour's ServerRequest lives inside the ancestor and is NOT
    # attributed, which is the whole assertion.
    assert found["kinds"]["ServerRequest"] == 0, found
    assert found["kinds"]["Navigate"] == 1, found


# ---------------------------------------------------------------------------
# Every refusal, one at a time. A refusal that has never been produced is a
# branch nobody has read.
# ---------------------------------------------------------------------------


def test_it_refuses_when_every_reference_site_is_empty():
    """THE FLOOR, AND IT IS THE MOST CONSEQUENTIAL BRANCH IN THE READER.

    **Zero of everything is the exact shape of permission.** The operator
    ruled that a click measured to issue no ``ServerRequest`` is by effect a
    READ, so an all-zero reading from this instrument is what would authorise
    pressing a button on his live profile -- and all-zero has two causes that
    look identical: the control has no actions, or THE READER FOUND THE KEY
    IN OBJECTS THAT DO NOT CARRY ACTIONS.

    The second is not hypothetical: a payload writing the key BESIDE its
    actions rather than around them produces exactly this, and it is what the
    corpus below is. So the reader refuses, and that refusal is what makes
    every non-zero reading trustworthy -- a run that reports kinds has shown,
    on that same payload, that it can see kinds through a reference.
    """
    beside = _sdui(
        _component(_CK_CARD, "Show details"),
        '{"componentkey":"' + _CK_CARD + '"}',
        '{"onTap":[{"$type":"proto.sdui.actions.core.Navigate"}]}',
    )
    found = probe._actions_by_reference(beside, "Show details")
    assert found["reference_sites"] >= 1, found
    assert found["kinds"] is None, found
    assert "not a measurement" in found["refused"], found

    # AND IT IS NOT SIMPLY ALWAYS REFUSING: the same shape with the actions
    # INSIDE the referenced object is answered.
    inside = _sdui(
        _component(_CK_CARD, "Show details"),
        _action_chunk(_CK_CARD, ("Navigate",)),
    )
    assert probe._actions_by_reference(inside, "Show details")["refused"] is None


def test_it_refuses_when_no_key_encloses_the_label():
    """A label carried outside any keyed component cannot be followed.

    THE REFUSAL SAYS WHICH FACT IT IS. "No key within four levels" is a fact
    about the PAGE's shape -- learned, note, without a byte of the page
    crossing out of the process, which is the only way this instrument is
    allowed to teach anybody anything.
    """
    found = probe._actions_by_reference('{"text":"Show details"}', "Show details")
    assert found["key_found"] is False, found
    assert found["kinds"] is None, found
    assert "no component key" in found["refused"], found


def test_it_refuses_two_distinct_keys_at_the_same_level():
    """Two keys in one object, and no way to say which owns the label.

    Choosing would be attribution by document order -- refused here for the
    same reason the locator refuses a doubled label, and the reason ``Edit``
    itself refused as ambiguous on the last live run.
    """
    payload = (
        '{"componentkey":"' + _CK_CARD + '","sibling":'
        '{"componentkey":"' + _CK_EDIT + '"},"text":"Show details"}'
    )
    found = probe._actions_by_reference(payload, "Show details")
    assert found["kinds"] is None, found
    assert "DISTINCT component keys" in found["refused"], found


def test_it_refuses_a_key_too_short_to_follow():
    """A short key is the substring defect wearing a reference's clothes.

    Following ``ab`` through a megabyte matches prose. The floor refuses
    rather than reporting the whole page's kinds as one control's.
    """
    payload = '{"componentkey":"ab","text":"Show details"},{"componentkey":"ab"}'
    found = probe._actions_by_reference(payload, "Show details")
    assert found["kinds"] is None, found
    assert "character floor" in found["refused"], found


def test_it_refuses_a_key_that_is_never_referenced():
    """DEFINED AND UNREFERENCED IS A FACT ABOUT THE MECHANISM, not the control.

    If nothing else in the payload names this key, this page does not attach
    THIS control's actions by componentkey -- and a third instrument has now
    failed to attribute it. The refusal says exactly that, so nobody reads it
    as "the control has no actions" and treats it as permission.
    """
    found = probe._actions_by_reference(
        _component(_CK_CARD, "Show details"), "Show details"
    )
    assert found["key_found"] is True, found
    assert found["reference_sites"] == 0, found
    assert found["kinds"] is None, found
    assert "never referenced" in found["refused"], found


def test_it_refuses_a_key_that_occurs_too_often_without_walking_anything():
    """THE COST CEILING, and it is checked BEFORE the expensive pass starts.

    Every occurrence costs a region walk of up to ``_REGION_CAP`` in each
    direction. A key matching thousands of times would drag this reader
    through hundreds of millions of characters of his profile to produce a
    number it would refuse anyway on the site cap -- so the refusal comes
    first, and the assertion that NOTHING WAS WALKED is the point: an
    unwalked payload is the cheap answer and the honest one at once.
    """
    key = "aaaaaaaaaaaa-repeated-key"
    payload = (
        '{"componentkey":"' + key + '","text":"Show details"}'
        + ("," + '{"componentkey":"' + key + '"}') * (probe._MAX_KEY_OCCURRENCES + 5)
    )
    found = probe._actions_by_reference(payload, "Show details")
    assert found["key_occurrences"] > probe._MAX_KEY_OCCURRENCES, found
    assert found["sites"] == [], "a region was walked before the ceiling refused"
    assert found["kinds"] is None, found
    assert "occurrence ceiling" in found["refused"], found


def test_it_refuses_when_a_reference_site_cannot_be_walked():
    """A PARTIAL READING IS REFUSED, because the missing site is the dangerous one.

    The site this reader could not walk is exactly where the ``ServerRequest``
    that would REFUSE a click might be, and a reading that comes back missing
    a kind is indistinguishable from a control that does not have it. Those
    two errors are not symmetric, so this leans at the safe end -- the same
    argument ``dom.SDUI_WINDOW_CHARS`` makes about its window.
    """
    # THE UNWALKABLE SITE IS MADE BY CONSTRUCTION, not by hoping a brace walk
    # fails: one occurrence of the key is buried past the region cap, which is
    # the same technique the enclosure reader's own cap test uses. A test that
    # relied on an accidental imbalance would be testing the corpus.
    buried = '{"' + "a" * (probe._REGION_CAP + 100) + '","componentkey":"' + _CK_CARD + '"}'
    payload = _sdui(
        _component(_CK_CARD, "Show details"),
        _action_chunk(_CK_CARD, ("Navigate",)),
        buried,
    )
    found = probe._actions_by_reference(payload, "Show details")
    assert found["unresolved_sites"] >= 1, found
    assert found["kinds"] is None, found
    assert "refused rather than reported" in found["refused"], found


def test_it_inherits_the_locators_refusals():
    """The two readers share one locator, so they cannot answer about
    different bytes.

    A doubled label refused the enclosure reader on the last live run --
    ``Edit``'s escaped form occurred TWICE. The reference reader must refuse
    the same reading rather than quietly following the first one's key.
    """
    doubled = _sdui(
        _component(_CK_CARD, "Edit"),
        _component(_CK_EDIT, "Edit"),
        _action_chunk(_CK_EDIT, ("ServerRequest",)),
    )
    found = probe._actions_by_reference(doubled, "Edit")
    assert found["occurrences"] == 2, found
    assert found["kinds"] is None, found
    assert "document order" in found["refused"], found

    absent = probe._actions_by_reference('{"text":"nothing here"}', "Edit")
    assert absent["kinds"] is None, absent
    assert "the finding" in absent["refused"], absent


# ---------------------------------------------------------------------------
# The spellings, and the bound that lets this read a string at all
# ---------------------------------------------------------------------------


def test_the_key_field_is_read_in_the_escaped_flight_spelling():
    """FOUR SPELLINGS, AND THE ESCAPED ONE IS THE LIVE ONE.

    The label was found on the live page in its ESCAPED form -- a flight
    payload carries JSON inside JS string literals -- so a key reader that
    knew only ``"componentkey":"..."`` would report "no key" on the exact
    payload it was built for, and "no key" and "a key I cannot see" are the
    two answers this file exists to keep apart.

    The mutation is the assertion: the same corpus in the escaped spelling
    must answer, and the run must say WHICH spelling matched.
    """
    escaped = _sdui(
        _component(_CK_CARD, "Show details", escaped=True),
        _action_chunk(_CK_CARD, ("Navigate",), escaped=True),
    )
    found = probe._actions_by_reference(escaped, "Show details")
    assert found["located_by"] == "escaped", found
    assert found["refused"] is None, found
    assert found["key_spelling"] == "componentkey escaped", found
    assert found["kinds"]["Navigate"] == 1, found


def test_the_camelcase_key_field_is_read_too():
    """``componentkey`` is the DOM attribute's spelling. JSON may camel it.

    Counted separately for the same reason the label's three spellings are:
    a reader silent on one spelling reports a confident zero.
    """
    camel = (
        '{"componentKey":"' + _CK_CARD + '","text":"Show details"}'
        + "," + '{"componentKey":"' + _CK_CARD + '","onTap":'
        '[{"$type":"proto.sdui.actions.core.Navigate"}]}'
    )
    found = probe._actions_by_reference(camel, "Show details")
    assert found["refused"] is None, found
    assert found["key_spelling"] == "componentKey quoted", found
    assert found["kinds"]["Navigate"] == 1, found


def test_the_locator_aims_at_the_payload_and_not_at_the_dom():
    """RULING 1, AND THE CORPUS IS THE LIVE SHAPE RATHER THAN A CONVENIENT ONE.

    The document this probe reads is not a payload. It is an HTML page WITH a
    payload inside it, and the two spell a label differently::

        "Edit"        an HTML attribute, aria-label="Edit"   -> the DOM
        \\"Edit\\"     JSON inside a JS string literal        -> the payload

    So on a document carrying both, THE QUOTED FORM IS THE DOM -- and the
    reader preferred quoted until the live run of 2026-09-03, which aimed it
    at the HTML attribute where no JSON object exists. Both readers refused,
    neither refusal was about the page, and **a reader aimed at the wrong half
    of a document reports a fact about itself in the grammar of a fact about
    its subject.**

    THE CORPUS BELOW REPRODUCES THE MEASURED COUNTS EXACTLY: quoted 1,
    escaped 2 -- the census's unique ``button[aria-label="Edit"]`` and its two
    payload offsets. A quoted-first reader picks the attribute and refuses for
    the wrong reason; an escaped-first reader picks the payload and refuses as
    AMBIGUOUS, which is the right reason.
    """
    dom = '<button aria-label="Edit" class="x"></button>'
    # TWO escaped components, because the payload carries one action list ONCE
    # PER RENDERING VARIANT -- that is where the measured escaped 2 comes
    # from, and a corpus with one would be testing an easier document than the
    # live one.
    payload = _sdui(
        _component(_CK_EDIT, "Edit", escaped=True),
        _action_chunk(_CK_EDIT, ("SetState", "ServerRequest"), escaped=True),
        _component(_CK_EDIT, "Edit", escaped=True),
        _action_chunk(_CK_EDIT, ("SetState", "ServerRequest"), escaped=True),
    )
    document = dom + "<script>" + payload + "</script>"

    found = probe._actions_by_reference(document, "Edit")
    assert found["spellings"]["quoted"] == 1, found["spellings"]
    assert found["spellings"]["escaped"] == 2, found["spellings"]

    # THE AIM: the payload, not the attribute.
    assert found["located_by"] == "escaped", found

    # AND THE HONEST REFUSAL THAT BUYS. Two payload occurrences, so the reader
    # cannot say which is the control. This is the CORRECT outcome and not a
    # regression -- fixing the aim was never going to produce an answer here.
    assert found["kinds"] is None, found
    assert "document order" in found["refused"], found

    # THE DISCRIMINATING HALF: aimed at the DOM attribute instead, the refusal
    # is a different one entirely and says nothing true about the page.
    at_the_attribute = probe._actions_for(dom, "Edit")
    assert at_the_attribute["located_by"] == "quoted", at_the_attribute
    assert "balanced" in at_the_attribute["refused"], at_the_attribute


def test_the_quoted_fallback_survives_for_an_unescaped_payload():
    """The fallback is not decoration: a plain-JSON page has no escaped form.

    Preferring escaped WITH a quoted fallback is correct on both documents.
    Preferring quoted is correct only on the second, which is what made it
    wrong live.
    """
    plain = _sdui(
        _component(_CK_CARD, "Show details"),
        _action_chunk(_CK_CARD, ("Navigate",)),
    )
    found = probe._actions_by_reference(plain, "Show details")
    assert found["spellings"]["escaped"] == 0, found["spellings"]
    assert found["located_by"] == "quoted", found
    assert found["refused"] is None, found
    assert found["kinds"]["Navigate"] == 1, found


def test_the_component_key_never_reaches_a_printed_line():
    """THE ONE STRING THIS FILE READS OUT, AND IT MUST NOT BE PRINTED.

    Following a reference means holding the thing referred to, so the bound
    moved from "no capture group exists" to "one exists and its value is
    never emitted". THAT IS ASSERTED OVER THE RENDERED LINES, not over the
    dict: the dict is an intermediate, the lines are what reaches a
    transcript, and a transcript is a publication channel -- this repo's own
    finding about failure messages, applied to a printout.

    AND THE KEY IS NOT ASSUMED HARMLESS. The census measured one componentkey
    on this page as ``<vanity>_openToButton``. A key on this page can BE an
    identifier, which is why this is a leak test and not a tidiness test.
    """
    payload = _sdui(
        _component(_CK_VANITY, "Show details"),
        _action_chunk(_CK_VANITY, ("Navigate",)),
    )
    found = probe._actions_by_reference(payload, "Show details")
    assert found["refused"] is None, found
    assert found["kinds"]["Navigate"] == 1, found

    rendered = "\n".join(probe._render_reference(found))
    assert _CK_VANITY not in rendered, "the componentkey reached a printed line"
    assert "jordan-blake" not in rendered, "the slug reached a printed line"
    # ...and the render is not empty, so the assertion is not vacuous.
    assert "Navigate" in rendered, rendered

    # THE DICT IS ALLOWED TO BE AN INTERMEDIATE, but nothing in it that a
    # caller would loop over may carry the key either.
    assert _CK_VANITY not in repr(found["sites"]), found["sites"]
    assert _CK_VANITY not in repr(found["kinds"]), found["kinds"]


def test_a_refusal_never_quotes_the_key_either():
    """FAILURE MESSAGES RENDER REDACTED. A refusal is a publication too.

    The identity guard in this repo states it as a rule and earned it: a
    guard that prints the identifier it found has republished it somewhere
    new. Every refusal below is produced against a vanity-shaped key and none
    of them may contain it.
    """
    unreferenced = _component(_CK_VANITY, "Show details")
    empty = _sdui(
        _component(_CK_VANITY, "Show details"),
        '{"componentkey":"' + _CK_VANITY + '"}',
    )
    for payload in (unreferenced, empty):
        found = probe._actions_by_reference(payload, "Show details")
        assert found["refused"], payload[:40]
        assert _CK_VANITY not in "\n".join(probe._render_reference(found))


def test_the_probe_still_intercepts_nothing_and_writes_nowhere():
    """THE BOUNDS PINNED AS COUNTS, because the reader grew and they did not.

    The previous run measured ``.route`` 0 and ``page.on`` 2. Following a
    reference needed no new browser capability at all -- it reads bytes this
    process already held -- so those two numbers must be IDENTICAL after the
    change, and asserting the counts rather than mere absence is what makes
    that a measurement.
    """
    source = _PROBE_PATH.read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    assert code.count(".route(") == 0, "the probe has acquired an interception path"
    assert source.count("page.on(") == 2, source.count("page.on(")
    for writer in ("open(", ".write_text(", ".write_bytes(", ".mkdir("):
        assert writer not in code, writer
