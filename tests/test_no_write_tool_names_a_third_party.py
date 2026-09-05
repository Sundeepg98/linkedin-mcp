"""No write tool may take a parameter whose value IS another member.

THE RULING THIS ASSERTS, and it was not invented for this file. The operator's
typing ruling carries three conditions, one of them structural: *text the
caller supplied rather than this server composing it*.
``tests/test_typed_bytes.py`` already enforces that for the ONE ``page.fill``
site, off the AST, so a future edit that "interpolates, truncates, strips or
decorates" his string fails there.

**A MENTION IS THAT EDIT WEARING A FEATURE'S NAME.** Typing the characters
``@Name`` into a LinkedIn composer produces no mention -- the platform requires
a typeahead commit -- so a mention is bytes the SERVER puts into his post at a
position the SERVER chooses. It cannot be built without loosening the guard
that exists because "the substring version passed a mutation that appended a
hashtag". The same holds for a tag and for a named collaborator.

WHY A PARAMETER NAME AND NOT A CALL SITE. ``test_typed_bytes`` guards the
mechanism that types. This guards the SURFACE: a parameter is the promise a
caller reads, and adding ``mentions=[...]`` to a signature is a ruling change
whoever makes it should have to argue for. The failure is meant to be the
argument's trigger, not its conclusion.

WHAT IS DELIBERATELY NOT FORBIDDEN, so this file is not read as wider than it
is: ``audience`` and ``visibility``. Amendment A9 of
``_audit/2026-09-03-linkedin-gap-blockers.md`` rules those admissible as a
CLOSED VOCABULARY -- LinkedIn's post-audience options are a closed set, matched
by name before any selector is built, so such a parameter "cannot pass an
arbitrary string, therefore cannot carry a member's name". They are exempted BY
NAME below rather than by silence, so a reader can see the ruling rather than
infer it from an absence.

AND WHAT THIS DOES NOT CLAIM. A needle is not forbidden and must not be:
``send_message`` and ``send_invitation`` take one, and this repository ruled on
2026-08-31 that a needle is HIS OWN WORD going INTO the page, with integers
coming back -- collection of nobody's identity. The distinction this file draws
is DESTINATION, not presence: a needle selects a control and is discarded; a
mention becomes part of an outward, permanent, third-party-visible artifact.

SHOWN FAILING before admission: adding ``mentions: list[str] = []`` to
``linkedin_publish_post``'s signature turns this red, naming the tool and the
parameter. Recorded in ``_audit/2026-09-05-article-publish.md``.
"""

import ast
import pathlib

import pytest

_SERVER = pathlib.Path(__file__).resolve().parent.parent / "linkedin_server" / "server.py"

#: Parameter names whose VALUE would be another member, carried into content
#: this server publishes. Adding one is a ruling change; see the module
#: docstring and census rows ``C10``, ``C28``, ``C9``, ``C54``, ``C55``.
FORBIDDEN_PARAMETER_NAMES = frozenset(
    {
        "mention",
        "mentions",
        "tag",
        "tags",
        "tagged",
        "tagged_person",
        "tagged_people",
        "collaborator",
        "collaborators",
        "invitee",
        "invitees",
        "celebrant",
        "honoree",
    }
)

#: Exempted BY NAME, under Amendment A9's closed-vocabulary ruling. These name
#: a value from a closed set LinkedIn defines, never a person.
RULED_ADMISSIBLE = frozenset({"audience", "visibility"})


def _tool_signatures() -> dict[str, tuple[str, ...]]:
    """Every ``linkedin_*`` tool function and its parameter names, off the AST.

    Read from source rather than by import: the assertion is about the SURFACE
    a caller reads, and an import would resolve decorators and defaults that
    are not part of that promise.
    """
    tree = ast.parse(_SERVER.read_text(encoding="utf-8"))
    out: dict[str, tuple[str, ...]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        if not node.name.startswith("linkedin_"):
            continue
        args = node.args
        names = [a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)]
        if args.vararg is not None:
            names.append(args.vararg.arg)
        if args.kwarg is not None:
            names.append(args.kwarg.arg)
        out[node.name] = tuple(names)
    return out


def test_the_tool_surface_is_readable_at_all() -> None:
    """The control. A guard that enumerates nothing refuses nothing.

    Without this, a rename of the ``linkedin_`` prefix would empty the corpus
    and every assertion below would pass by reading no tools at all.
    """
    sigs = _tool_signatures()
    assert len(sigs) >= 30, f"only {len(sigs)} linkedin_* tools parsed out of {_SERVER.name}"
    assert "linkedin_publish_post" in sigs
    assert sigs["linkedin_publish_post"][0] == "text"


@pytest.mark.parametrize("forbidden", sorted(FORBIDDEN_PARAMETER_NAMES))
def test_no_tool_takes_a_third_partys_identity_as_a_parameter(forbidden: str) -> None:
    """Fails naming the tool and the parameter, so the message is the address."""
    offenders = [
        f"{tool}({forbidden}=...)"
        for tool, params in sorted(_tool_signatures().items())
        if forbidden in params
    ]
    assert not offenders, (
        f"{offenders} takes a parameter whose value is another member, carried "
        "into content this server publishes. That is a RULING CHANGE, not a "
        "feature: the operator's typing ruling requires text the caller "
        "supplied rather than this server composing it, and a mention or tag "
        "is bytes this server inserts at a position it chooses. If the ruling "
        "has been revisited, amend _audit/2026-09-05-article-publish.md and "
        "remove the name from FORBIDDEN_PARAMETER_NAMES with the reason -- do "
        "not rename the parameter to get past this."
    )


def test_the_exemptions_are_stated_rather_than_silent() -> None:
    """``audience``/``visibility`` are admissible and must not drift into the
    forbidden set by a later editor who reads this file as "no new parameters".
    """
    assert not (RULED_ADMISSIBLE & FORBIDDEN_PARAMETER_NAMES), (
        "A9 rules the post-audience control admissible as a closed vocabulary. "
        "Forbidding it here would make this file contradict a written ruling."
    )
