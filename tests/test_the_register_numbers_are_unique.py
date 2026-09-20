"""Two waves cannot both be section 24 of the instrument register.

WHY THIS EXISTS. On 2026-09-20 five waves ran in parallel worktrees and FIVE of
them appended a section to `_audit/INSTRUMENTS.md` numbered 24. Each was correct
alone: every worktree saw 23 as the highest and picked the next integer. The
collision exists only in the merge, so no wave's own green run could see it, and
nothing checked the merged result -- the register just silently grew duplicate
numbers until someone read it.

THAT IS THE WHOLE SHAPE OF THE BUG, and it is not really about numbering. A
register whose next key is DERIVED FROM THE CURRENT MAXIMUM cannot be appended
to concurrently, because every writer computes the same next key from the same
stale maximum. The register's own second law says an instrument enters only if
it has been shown failing; this is the register failing to hold its own entries
apart.

WHAT THIS DOES NOT DO. It does not renumber anything and it does not enforce
contiguity -- the file already has a real gap at 22 and closing it would rewrite
published section numbers that other documents cite. Uniqueness is the property
that matters to a reader following a citation; density is not.
"""
import collections
import pathlib
import re

REGISTER = pathlib.Path(__file__).resolve().parents[1] / "_audit" / "INSTRUMENTS.md"

#: Headings are written both `## 24.` and `## 24 ·` in the committed file, by
#: different waves. Both spellings are real and neither is being normalised here.
HEADING = re.compile(r"^##\s+(\d+)\s*[.·]", re.M)


def _numbers(text: str) -> list[str]:
    return HEADING.findall(text)


def test_no_two_register_sections_share_a_number():
    """A citation to section N must reach exactly one section."""
    counts = collections.Counter(_numbers(REGISTER.read_text(encoding="utf-8")))
    dupes = {n: c for n, c in counts.items() if c > 1}
    assert not dupes, (
        "instrument register sections sharing a number: %s. Five waves picked 24 "
        "on 2026-09-20 because each computed 'the next integer' from the same "
        "stale maximum in its own worktree. Renumber the incoming section rather "
        "than the one already published, so existing citations keep resolving."
        % sorted(dupes.items())
    )


def test_the_register_actually_has_sections_to_check():
    """A zero here would make the test above vacuous, which is the failure this
    repo keeps finding: an assertion satisfied by an empty result cannot fail."""
    found = _numbers(REGISTER.read_text(encoding="utf-8"))
    assert len(found) >= 20, (
        "parsed only %d numbered sections from the register; the heading pattern "
        "has probably drifted, and a uniqueness check over nothing is not a check"
        % len(found)
    )


def test_control_the_guard_convicts_a_planted_duplicate():
    """SHOWN FAILING. The register's own law: an instrument enters only if it has
    been demonstrated capable of firing."""
    real = REGISTER.read_text(encoding="utf-8")
    planted = real + "\n## 23. A PLANTED DUPLICATE OF AN EXISTING SECTION\n"
    counts = collections.Counter(_numbers(planted))
    assert [n for n, c in counts.items() if c > 1] == ["23"], (
        "the duplicate detector did not convict a planted duplicate of section 23"
    )
    assert not [n for n, c in collections.Counter(_numbers(real)).items() if c > 1]
