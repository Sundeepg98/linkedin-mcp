"""The urn substitution must remove the WHOLE urn, not the part it recognised.

THE HOLE, FOUND 2026-09-02 while designing a different fix. ``_CENSUS_URN`` was
``urn:li:[A-Za-z0-9_.:%@-]+`` and that character class excludes ``(``, so on a
COMPOSITE urn the pattern stopped at the first parenthesis and left the rest of
the token standing:

    urn:li:fsd_profileGeo:(<member token>,GEO)  ->  <urn>(<member token>,GEO)

**A MEMBER TOKEN SURVIVED A SUBSTITUTION WHOSE ENTIRE JOB IS REMOVING ONE.**
Nothing downstream caught it either: ``_CENSUS_LONG_DIGITS`` wants six
consecutive digits and a LinkedIn member token is alphanumeric, so it sailed
past every later rule. ``census_substitute``'s own docstring says "a urn, a
member path, a company path, a possessive and a long digit run identify
somebody whichever container they were read in" -- and for the composite form
that was simply not true.

WHY IT MATTERS MORE THAN ITS HIT COUNT. This predicate is the FIRST half of
``census_shape``, so it runs on everything the surface census publishes, and it
runs UNGATED in ``dom.read_self_owned_editor_fields`` -- the reader that
returns raw accessible names because its container is measured to be his own.
There the substitutions ARE the whole protection.

## What was measured before anything was changed

The instruction was to enumerate the class rather than patch the instance,
because a fix found from one instance rarely covers the class. Both halves were
run:

  THE REAL CORPUS -- the ten captured LinkedIn documents in ``_audit/``, about
  1.9 MB. SEVEN urn tokens, ONE escaping character (``(``), and all seven are
  ``urn:li:application:(web,flagship-web)``, which identifies nobody.

  CONSTRUCTED PROBES -- none of them his -- which found THREE escaping
  characters rather than one. That is the finding: the corpus showed one, and
  the corpus is not the class.

So the honest statement, and it is deliberately narrower than "there was a
leak": **a real hole, in a form that is present in the corpus, with no
identity-bearing instance observed through it.** Not a leak, and not nothing.

## What this file asserts

1. every escaping shape is now consumed WHOLE;
2. each of them is SHOWN FAILING against the old pattern INDEPENDENTLY -- one
   parametrised case per shape, so a fix that covered two of three could not
   pass by averaging;
3. the one shape deliberately NOT consumed says why;
4. the callers are enumerated, so a new consumer of this predicate has to be
   considered rather than inherited.

EVERY URN AND MEMBER TOKEN BELOW IS BUILT, NEVER WRITTEN OUT. That is not
decoration: ``test_no_committed_identity`` refuses a urn-shaped or
member-token-shaped literal in a tracked file, on the SHAPE, because a reviewer
reading a diff cannot tell an invented identifier from a real one. It refused
two of this session's files already -- a urn literal in one test table and two
slug-shaped example paths in a comment -- so the constructions here are the
rule being followed rather than a precaution.
"""

from __future__ import annotations

import re

import pytest

from linkedin_server import shape

#: THE OLD PATTERN, kept ONLY so each shape can be shown escaping it. This is
#: the exact string that shipped, and it is the thing under test in part 2.
NARROW = re.compile("urn" + ":li:" + r"[A-Za-z0-9_.:%@-]+")

#: A member-token-shaped string, BUILT. LinkedIn's are alphanumeric and start
#: with a fixed prefix; this carries the shape and belongs to nobody.
_TOKEN = "AC" + "oAAB" + "0" * 4 + "xyz"

#: A urn head, built for the same reason.
def _urn(namespace: str, tail: str) -> str:
    return "urn" + ":li:" + namespace + ":" + tail


#: THE ESCAPING SHAPES, each with the character that stopped the old pattern
#: and what it left behind. Enumerated from the probe run, not imagined.
#:
#: THE FIRST TWO ARE THE ONES THAT MATTER: they are the forms in which a MEMBER
#: TOKEN survives. The third leaks base64 padding, which identifies nobody --
#: it is here because it proves the defect is a CLASS rather than one
#: parenthesis, which is the whole reason the enumeration was demanded before
#: the fix.
ESCAPING: dict[str, str] = {
    "composite 2-tuple": _urn("fsd_profileGeo", "(" + _TOKEN + ",GEO)"),
    "composite nested": _urn(
        "fsd_profilePosition", "(" + _urn("fsd_profile", _TOKEN) + ",1234)"
    ),
    "base64 padding": _urn("fs_messagingThread", "2-ZGVmYXVsdA=="),
}

#: THE SHAPES THAT WERE ALWAYS CLEAN, asserted so a widening cannot quietly
#: break what already worked. A pattern that consumed MORE could start eating
#: the text around a urn, and that would be a different defect with the same
#: green suite.
ALREADY_CLEAN: dict[str, str] = {
    "plain activity": _urn("activity", "7" + "0" * 18),
    "member id": _urn("fsd_profile", _TOKEN),
    "url encoded": "urn" + ":li:" + "activity%3A" + "7" + "0" * 18,
    "the one in the corpus": _urn("application", "(web,flagship-web)"),
}


def _residue(text: str) -> str:
    """What survives the substitution, with the placeholder removed."""
    return shape.census_substitute(text).replace("<urn>", "").strip()


# ---------------------------------------------------------------------------
# 1. Every escaping shape is now consumed whole
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", sorted(ESCAPING))
def test_an_escaping_shape_is_now_consumed_whole(label):
    """Nothing of the urn may survive, whichever delimiter it carries."""
    residue = _residue(ESCAPING[label])
    assert residue == "", (
        "%s: %r survived the substitution. The point of this predicate is "
        "that a urn identifies somebody whichever container it was read in, "
        "so a partially-removed one is worse than an untouched one: it looks "
        "handled." % (label, residue)
    )


@pytest.mark.parametrize("label", sorted(ESCAPING))
def test_the_member_token_is_not_in_the_output(label):
    """THE PROPERTY, stated directly rather than inferred from the residue.

    Asserting an empty residue is the structural claim. This is the one that
    matters to him: the token is not in what gets published, whatever else the
    string does.
    """
    out = shape.census_substitute(ESCAPING[label])
    assert _TOKEN not in out, out


@pytest.mark.parametrize("label", sorted(ALREADY_CLEAN))
def test_a_shape_that_was_already_clean_stays_clean(label):
    """The widening must not start eating text that is not a urn.

    A pattern that consumes MORE can consume the wrong thing, and that failure
    would pass every test written about the leak.
    """
    assert _residue(ALREADY_CLEAN[label]) == "", ALREADY_CLEAN[label]


def test_a_urn_inside_a_sentence_takes_only_the_urn():
    """The neighbouring words are not part of the identifier.

    This is the control for the test above: if the composite tail were matched
    too greedily, a urn followed by ordinary prose would swallow the prose, and
    the census would report ``<urn>`` where a control had a readable name.
    """
    sentence = "View more options for " + ESCAPING["composite 2-tuple"] + " here"
    assert shape.census_substitute(sentence) == "View more options for <urn> here"


# ---------------------------------------------------------------------------
# 2. SHOWN FAILING -- each shape independently, against the pattern that shipped
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", sorted(ESCAPING))
def test_each_shape_escaped_the_old_pattern_independently(label, monkeypatch):
    """The instrument must fire on EACH shape, not on the set.

    A check that only catches the composite would pass while base64 padding
    still escaped, and a check that passed because ONE of three failed would be
    an average rather than a measurement. So the old pattern is restored and
    each shape asserted to escape it on its own case.

    THE OLD PATTERN IS THE ONE THAT SHIPPED, spelled out at the top of this
    file. Reconstructing it is what makes this a demonstration rather than a
    story about one.
    """
    monkeypatch.setattr(shape, "_CENSUS_URN", NARROW)
    residue = _residue(ESCAPING[label])
    assert residue, (
        "%s did NOT escape the old pattern, so this case demonstrates nothing "
        "and the shape does not belong in ESCAPING." % label
    )


def test_the_old_pattern_left_the_member_token_standing(monkeypatch):
    """THE HEADLINE, reproduced: the token survived on the composite form.

    Kept separate from the parametrised case above because the residue merely
    being non-empty is not the finding. The finding is WHAT was in it.
    """
    monkeypatch.setattr(shape, "_CENSUS_URN", NARROW)
    out = shape.census_substitute(ESCAPING["composite 2-tuple"])
    assert _TOKEN in out, out
    # ... and nothing downstream rescued it, which is why this mattered.
    assert shape._CENSUS_LONG_DIGITS.search(_TOKEN) is None, (
        "the member token now contains six consecutive digits, so the long-"
        "digit rule would have caught it and this reproduction is measuring "
        "the wrong thing."
    )


# ---------------------------------------------------------------------------
# 3. What is deliberately NOT consumed
# ---------------------------------------------------------------------------


def test_a_following_path_segment_is_left_alone_on_purpose():
    """A ``/`` after a urn is a PATH SEPARATOR, not urn content.

    It appeared in no urn in the captured corpus. A urn sitting inside a media
    url is followed by more path, and widening the pattern to swallow it would
    eat text that is not part of the identifier -- which is a different defect
    with the same green suite.

    ASSERTED RATHER THAN OMITTED, because "we thought about it and decided no"
    and "nobody considered it" look identical in a diff. If a real urn form
    with an internal slash is ever measured, this test is the thing that has to
    be argued with.
    """
    with_path = _urn("digitalmediaAsset", "D000") + "/xyz"
    assert shape.census_substitute(with_path) == "<urn>/xyz"


# ---------------------------------------------------------------------------
# 4. Who sees this predicate
# ---------------------------------------------------------------------------


def test_the_consumers_of_this_predicate_are_the_ones_that_were_considered():
    """A new caller must be considered rather than inherited.

    Changing this pattern changes what EVERY census publishes, so the callers
    were enumerated before it was touched. This pins that enumeration: a fifth
    consumer fails here and has to be looked at, the same way a twelfth
    performable action fails the reachability instrument.

    THE FIVE, and what each of them shows a caller:

      dom.read_self_owned_editor_fields   control NAMES, UNGATED -- the
                                          substitutions are the whole
                                          protection there
      dom.read_self_owned_editor_values   control NAMES, same rule
      server._path_without_member         a LANDED URL PATH, which can carry a
                                          composite urn in a segment or query
      shape.census_shape                  calls this as its first half, so the
                                          entire surface census is downstream
      writes._live_control                NOT a publisher -- a REFUSAL TEST

    THE FIFTH IS THE ONE WORTH READING TWICE, and this test caught it. The
    enumeration reported to the lead named FOUR, and it was correct when it was
    taken: ``writes._live_control`` gained ``census_substitute(dom_id) !=
    dom_id`` in ``ea5354d``, an hour later and by the same hand. **A caller was
    added to the predicate between measuring it and changing it**, which is the
    stale-measurement shape this wave has now found in four places, arriving at
    the person holding the instrument.

    ITS VERDICT DOES NOT MOVE, and that is derived rather than hoped. It asks
    whether the substitution CHANGES the id. Both patterns require ``urn:li:``
    to appear before anything matches, and the wide one matches a superset of
    what the narrow one does -- so any id the wide pattern alters, the narrow
    one already altered. The refusal fires on exactly the same set of ids. What
    the widening buys elsewhere it does not spend here.

    Read off the source rather than promised, and by AST so a mention in a
    docstring does not count as a call.
    """
    import ast
    import pathlib

    package = pathlib.Path(shape.__file__).parent
    callers: set[tuple[str, str]] = set()
    for path in sorted(package.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for inner in ast.walk(node):
                if not isinstance(inner, ast.Call):
                    continue
                func = inner.func
                name = (
                    func.attr
                    if isinstance(func, ast.Attribute)
                    else getattr(func, "id", "")
                )
                if name == "census_substitute":
                    callers.add((path.name, node.name))

    assert callers == {
        ("dom.py", "read_self_owned_editor_fields"),
        ("dom.py", "read_self_owned_editor_values"),
        ("server.py", "_path_without_member"),
        ("shape.py", "census_shape"),
        ("writes.py", "_live_control"),
        # SIXTH AND SEVENTH, added 2026-09-03, and this test caught them --
        # which is a third instance of the shape its own docstring describes:
        # a caller arriving between the enumeration and the reading of it.
        #
        # BOTH ARE THE SAME ONE-LINE FIX TO A `source_url` FIELD, and both are
        # PUBLISHERS rather than refusal tests, so they are the kind this
        # enumeration exists to make somebody look at.
        #
        #   linkedin_surface_census  a REAL LEAK, closed. Its source_url was
        #       the only unshaped url in a payload that substituted
        #       /in/<member>/ everywhere else, and the profile surface it names
        #       carries THIRD PARTIES.
        #
        #   linkedin_my_profile      NOT a leak, and the distinction matters
        #       more than the line. That tool publishes `name`,
        #       `public_identifier` and `profile_url` DELIBERATELY -- it is a
        #       window onto his own account and redacting them would empty it.
        #       source_url was a redundant copy of output published on purpose
        #       two fields up. Shaped for CONSISTENCY, never concealment: a
        #       shaped source_url sitting above a deliberate public_identifier
        #       is WORSE than an unshaped one if a reader takes it for a
        #       redaction, because it claims a property the payload does not
        #       have.
        ("server.py", "linkedin_surface_census"),
        ("server.py", "linkedin_my_profile"),
        # AN EIGHTH ARRIVED AND THEN LEFT AGAIN ON 2026-09-04, and the round
        # trip is worth more than either state.
        #
        # linkedin_connections became a consumer without anybody deciding it
        # should be one, and this test caught it -- the fourth instance of the
        # shape its own docstring describes. The consideration it forced is
        # below, and its conclusion was that THIS TOOL SHOULD NOT DEPEND ON
        # THIS PREDICATE AT ALL. So there is no eighth entry, and the absence
        # is the finding rather than an oversight.
        #
        # WHY. Its surface is the one page in this package made ENTIRELY of
        # third parties, so the question was never "is the predicate correct"
        # but "is it correct over rows that are all other people". Measured,
        # the answer was RIGHT BUT INSUFFICIENT:
        #
        #     /in/<slug>/                             -> /in/<member>/  CHANGED
        #     /x/urn:li:fsd_profileGeo:(<token>,GEO)/ -> /x/<urn>/      CHANGED
        #     /y/?q=urn:li:fsd_profile:<token>        -> /y/?q=<urn>    CHANGED
        #     /feed/update/<10 digits>/               -> <id>           CHANGED
        #     /...connections/?u=<member token>            UNCHANGED  <-- gap
        #
        # A BARE MEMBER TOKEN IN A QUERY SURVIVES THE SUBSTITUTION, and that
        # is the one identifier class this particular surface traffics in:
        # every Message control on the connections page carries
        # `?recipient=<token>`. A gap elsewhere is theoretical; here it is the
        # page's own vocabulary.
        #
        # WHAT WAS DONE ABOUT IT, and it is deliberately not a widening. The
        # predicate was NOT changed -- eight consumers publish through it and
        # only this one has evidence for the gap -- and no second redactor was
        # written, because a package with two privacy boundaries has two that
        # can disagree.
        #
        # TWO FIXES WERE TRIED BEFORE THE RIGHT ONE, and both failed the same
        # way -- a claim that outran its code:
        #
        #   1. shape the whole landed url. Correct on the matching branch and
        #      useless on the only branch where a token can appear.
        #   2. shape the landed PATH with the query dropped. Still leaves a
        #      token standing anywhere outside an `/in/` segment, because that
        #      is the only member shape this predicate knows:
        #          /messaging/thread/<token>/  -> unchanged
        #          /mynetwork/<token>/         -> unchanged
        #      The six landings (2) was measured against did not include one,
        #      because they were chosen to match what its author already
        #      believed. Found by reviewing the function as though somebody
        #      else had written it.
        #
        # WHAT SHIPPED IS A CLOSED VOCABULARY -- `_PUBLISHABLE_SEGMENTS` --
        # matched BY NAME before any url is emitted, exactly as
        # `dom.MESSAGING_FILTERS` is matched before any selector is built. An
        # arbitrary string can never be published, so it can never carry an
        # identifier. Structural, where every version above was a filter that
        # had to keep up with LinkedIn's shapes.
        #
        # So `census_substitute` is not called on that path at all, this set
        # does not name it, and `test_no_identifier_leaves_through_source_url`
        # holds it to ten landings including the two that leaked.
        #
        # AND THE `my_profile` LESSON APPLIES HERE HARDER THAN THERE. That
        # entry warns a shaped source_url above deliberately published
        # identifiers claims a property the payload lacks. This payload
        # publishes OTHER PEOPLE'S names, profile urls and member ids on
        # purpose, so the false claim would be worse -- hence
        # `rows_are_not_redacted` is returned beside it, saying in the payload
        # what the shaping does and does not mean.
    }, sorted(callers)


def test_the_refusal_caller_fires_on_the_same_ids_either_way():
    """THE FIFTH CALLER'S VERDICT, ASSERTED RATHER THAN ARGUED.

    ``writes._live_control`` refuses a DOM id when the substitution CHANGES it.
    The paragraph above derives that the widening cannot move that verdict --
    both patterns need ``urn:li:`` before they match anything, and the wide one
    matches a superset -- but a derivation about a privacy predicate is worth
    one measurement.

    Both patterns are run over every shape in this file. For each, the two must
    AGREE on whether the string was altered, because that boolean is the whole
    of what the refusal reads.
    """
    for label, probe in sorted({**ESCAPING, **ALREADY_CLEAN}.items()):
        wide_changed = shape.census_substitute(probe) != probe
        narrow_changed = NARROW.sub("<urn>", probe) != probe
        assert wide_changed == narrow_changed, (
            "%s: the widening moved the refusal verdict (wide=%s narrow=%s). "
            "That is a behaviour change in a caller this fix was not supposed "
            "to touch." % (label, wide_changed, narrow_changed)
        )
