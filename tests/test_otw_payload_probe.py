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
