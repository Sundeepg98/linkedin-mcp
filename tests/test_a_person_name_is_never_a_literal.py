"""A real person's name may not arrive as a test constant.

WHAT THIS COSTS BEFORE IT EXISTS. On 2026-09-03 a real third party's given
name -- the operator's brother, supplied by the wave lead as the needle for a
live typeahead measurement -- reached three tracked files and five commit
messages. It was caught before the push, and closing it cost a rewrite of every
unpushed commit. **The alternative was deleting and recreating the repository**,
which this project has already had to do once: a force-push makes history
unreachable, not unserved, and retained objects stay resolvable by SHA.

NEITHER EXISTING GUARD WAS AT FAULT AND NEITHER CLAIMED THIS.
``test_no_committed_identity`` says of itself that no check it holds detects a
personal name, because names have no shape. The exact-value sweep passed for a
different reason: its wordlist is the OPERATOR's identity, and this was
somebody else's. **Both instruments were correct about the questions they ask.**
Nobody was asking this one.

## The inversion that makes it checkable

A name cannot be recognised. **A CONSTANT THAT HOLDS ONE CAN BE.** This
repository already names them consistently -- ``NEEDLE``, ``MEMBER_NAME``,
``OTHER`` -- because a needle is what you hand a matcher when you are pretending
to be a person. So the rule runs the other way round from a detector:

    every module-level assignment to a PERSON-CARRYING constant, in tests/ or
    scripts/, must hold a value listed in INVENTED_NAMES.

Writing ``NEEDLE = "<a real person>"`` then fails until somebody adds that name
to a table called INVENTED_NAMES -- **which is the moment they notice it is
not invented.** The check is not cleverness about strings; it is a speed bump
placed exactly where the mistake happens, and the entry is a claim a human
makes rather than a pattern a machine matches.

Same shape as ``_SANITISERS`` in the taint rule and
``KNOWN_DERIVED_NAVIGATIONS`` beside it: the declaration IS the assertion, and
adding one costs a visible edit.

## The lesson that was already written down, one layer too shallow

``tests/test_typeahead_gate.py`` carried this sentence while carrying the real
name:

    a shape-valid literal is required when the SHAPE is what the code reads;
    when it is not, an unmistakable placeholder is strictly better

A typeahead matcher reads a name as an opaque string -- it never inspects its
shape -- so an invented name exercises the identical code path. **The governing
rule was in the same file as the violation.** That is why this is a test and
not a note: a rule that has to be remembered at the moment of writing is a rule
that will be forgotten at the moment of writing.

## WHAT THIS DOES NOT COVER, named rather than implied

* **Prose.** A name in a docstring, a comment or a commit message is out of
  reach of an AST rule, and four of the five commit messages in the incident
  were exactly that. This closes the constant, not the sentence.
* **Names not held by a declared constant shape** -- a literal passed straight
  into a call, or built by concatenation. The constant is where this repository
  actually puts them, which is why the rule is aimed there, but aiming is not
  coverage and saying so is the difference between a guard and a claim.
* **Whether a listed name is genuinely invented.** Nothing here can know. The
  table is a human's claim; its value is that making it is deliberate.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCANNED = ("tests", "scripts")

#: CONSTANT NAMES THAT HOLD A PERSON. An inventory, not a pattern -- ``OTHER``
#: holds a person here while ``OTHER_ITEM`` holds a urn and
#: ``OTHER_THIRD_PARTY`` holds a url, so a prefix match would drag in values
#: that are not names and teach the next author to ignore this file.
#:
#: A NEW SHAPE IS A DELIBERATE ADDITION. If a constant starts holding a person
#: under a name not listed here, this rule is silent about it -- which is the
#: gap named in the docstring rather than a claim of coverage.
PERSON_CONSTANTS = frozenset(
    {
        "NEEDLE",
        "OTHER",
        "MEMBER",
        "MEMBER_NAME",
        "MEMBER_SLUG",
        "OTHER_SLUG",
        "OTHER_AUTHOR",
        "DISPLAY_NAME",
        "FULL_NAME",
        "RECIPIENT",
        "RECIPIENT_NAME",
    }
)

#: EVERY INVENTED PERSON THIS REPOSITORY IS ALLOWED TO NAME.
#:
#: THE ENTRY IS THE CLAIM. Nothing here verifies that a listed value is really
#: invented -- nothing could. What it does is make naming a person a
#: DELIBERATE act with a diff attached, so the question "is this a real
#: person?" gets asked once, by a human, at the only moment it can be answered.
#:
#: The needle marker and the slugs are here because they occupy the same
#: constants and would otherwise force the shape list to grow special cases.
INVENTED_NAMES = frozenset(
    {
        # People, all invented, each already in use below.
        "Grace Hopper",
        "Savita Krishnan",
        "Priya Raghunathan",
        "Thornwick M",
        "Somebody",
        # Not people, but held by the same constants.
        "zzqneedlemarkerzz",
        "alex-r-12ab34",
        "priya-sharma-12ab34",
        "Always off",
    }
)


def _person_assignments() -> list[tuple[str, int, str, str]]:
    """Every module-level assignment of a literal to a person-carrying name.

    MODULE LEVEL ONLY, DELIBERATELY. A needle built inside a function from a
    parameter is not a literal anybody typed, and chasing those would flag the
    machinery that CONSUMES a needle rather than the place one is written down.
    The incident put a real name at module scope, which is where a fixture
    constant lives.
    """
    out: list[tuple[str, int, str, str]] = []
    for folder in SCANNED:
        for path in sorted((REPO / folder).glob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:  # pragma: no cover - a broken file fails elsewhere
                continue
            for node in tree.body:
                if not isinstance(node, ast.Assign):
                    continue
                if not (
                    isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                ):
                    continue
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id in PERSON_CONSTANTS
                    ):
                        out.append(
                            (path.name, node.lineno, target.id, node.value.value)
                        )
    return out


def undeclared(assignments, declared) -> list:
    """The assignments whose value is not on the declared table.

    A PURE FUNCTION, SEPARATE FROM THE SWEEP, so the rule can be shown failing
    without writing a real person's name into a real file to prove it catches
    real people's names. That is not a hypothetical objection: the only honest
    way to demonstrate a filesystem-reading version of this rule going red
    would be to commit the exact thing it exists to prevent.
    """
    return [entry for entry in assignments if entry[3] not in declared]


def test_every_person_constant_holds_a_declared_invented_name():
    """THE RULE. A name arrives by being declared, or it does not arrive.

    The failure names the file, the constant and what to do -- because the
    person hitting this is mid-measurement with a real name in their hand,
    which is exactly the moment the reasoning is hardest to reconstruct.
    """
    found = undeclared(_person_assignments(), INVENTED_NAMES)
    assert found == [], (
        "a person-carrying constant holds a value that is not on "
        "INVENTED_NAMES: %s. If it is invented, add it to the table -- that "
        "edit is the check. IF IT IS A REAL PERSON'S NAME, IT DOES NOT GO IN "
        "A TRACKED FILE AT ALL: a needle is read as an opaque string, so an "
        "invented name exercises the identical code path, and a real one cost "
        "this project a rewrite of every unpushed commit on 2026-09-03."
        % found
    )


# ---------------------------------------------------------------------------
# Shown failing, and shown NOT failing, on synthetic assignments
# ---------------------------------------------------------------------------

#: (file, line, constant, value) -- the shape _person_assignments returns.
_INVENTED = ("tests/test_x.py", 10, "NEEDLE", "Thornwick M")
_REAL = ("tests/test_x.py", 10, "NEEDLE", "A Real Person")


def test_it_goes_red_on_a_name_that_is_not_declared():
    """THE INCIDENT, REPRODUCED WITHOUT REPRODUCING THE LEAK.

    A person constant holding a value nobody put on the table is exactly what
    happened, and it fails here -- against an obviously-invented stand-in,
    because demonstrating this rule with a real name would be committing the
    thing it prevents in order to prove it prevents it.
    """
    assert undeclared([_REAL], INVENTED_NAMES) == [_REAL]


def test_it_stays_green_on_a_declared_name():
    """THE CONTROL. Without it a checker that flagged EVERYTHING would pass the
    red case above while making every fixture in the repository unwritable."""
    assert undeclared([_INVENTED], INVENTED_NAMES) == []


def test_the_table_is_not_a_prefix_or_a_substring_match():
    """A NEAR-MISS IS A MISS.

    "Thornwick" is not "Thornwick M", and a rule that accepted one for the
    other would accept a real first name whose surname happens to be on the
    table. Membership, not resemblance.
    """
    near = ("tests/test_x.py", 10, "NEEDLE", "Thornwick")
    longer = ("tests/test_x.py", 10, "NEEDLE", "Thornwick M Jr")
    assert undeclared([near], INVENTED_NAMES) == [near]
    assert undeclared([longer], INVENTED_NAMES) == [longer]


def test_an_empty_table_refuses_everything_rather_than_nothing():
    """THE FAIL-CLOSED DIRECTION, which is the one that matters if the table is
    ever emptied by a bad merge: no declarations means no names, not free
    rein."""
    assert undeclared([_INVENTED], frozenset()) == [_INVENTED]


def test_the_rule_has_something_to_check():
    """A SWEEP OVER AN EMPTY GLOB IS A GREEN TEST THAT CHECKS NOTHING.

    Both halves are pinned: constants are found, and more than one file has
    them -- so a refactor that moved every needle out of module scope would
    fail here rather than silently disarming the rule.
    """
    found = _person_assignments()
    assert len(found) >= 8, found
    assert len({name for name, _l, _c, _v in found}) >= 5, found


def test_every_declared_name_is_actually_used():
    """A TABLE THAT OUTLIVES ITS ENTRIES IS A LIST OF PERMISSIONS.

    An unused entry is a name this repository is allowed to write and does
    not -- which is how a table stops being an inventory and becomes a
    standing licence nobody reviews. Deleting the last use forces the deletion
    of the entry.
    """
    used = {value for _n, _l, _c, value in _person_assignments()}
    unused = sorted(INVENTED_NAMES - used)
    assert unused == [], (
        "declared and unused: %s. Delete the entry -- a name nobody writes is "
        "a permission nobody is reviewing." % unused
    )


@pytest.mark.parametrize("constant", sorted(PERSON_CONSTANTS))
def test_the_person_constant_list_is_an_inventory_not_a_prefix(constant):
    """WHY THIS IS A LIST AND NOT ``startswith("OTHER")``.

    ``OTHER`` holds a person; ``OTHER_ITEM`` holds a urn and
    ``OTHER_THIRD_PARTY`` holds a url. A prefix rule would flag values that are
    not names, and a guard that cries wolf is one somebody switches off. So the
    shapes are enumerated, and each is asserted to be a bare identifier rather
    than a pattern -- if this ever becomes a regex, that is a different
    instrument and needs its own argument.
    """
    assert constant.isupper()
    assert constant.replace("_", "").isalpha(), constant
    assert "*" not in constant and "." not in constant
