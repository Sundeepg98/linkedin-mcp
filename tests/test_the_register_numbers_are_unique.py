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
contiguity -- the file has real gaps (5 and 33 today) and closing them would
rewrite published section numbers that other documents cite. Uniqueness is the
property that matters to a reader following a citation; density is not.

THE GAP AT 22 WAS NEVER REAL, and this sentence used to say it was. Section 22
is at line 3736, spelled `## 22 THE IMPACT GATE...` with no separator after the
number -- which the heading pattern below could not match until 2026-09-20. The
guard could not see the section, so it reported a gap, and the gap was then
written down here as a fact about the register. **A measurement artifact became
documentation of the thing being measured**, and it survived every reading of
this file until a collision forced somebody to count headings by hand. See the
note on HEADING below for what it cost.
"""
import collections
import pathlib
import re

REGISTER = pathlib.Path(__file__).resolve().parents[1] / "_audit" / "INSTRUMENTS.md"

#: Headings are written `## 24.`, `## 24 ·` and `## 24 <title>` in the committed
#: file, by different waves. All three spellings are real and none is being
#: normalised here.
#:
#: WIDENED 2026-09-20, AND THE GUARD WAS BLIND UNTIL IT WAS. The pattern
#: required a `.` or `·` AFTER the digits, so anything else there made the
#: whole section invisible. TWO sections were, for two DIFFERENT reasons, and
#: the difference matters:
#:
#:     ## 22 THE IMPACT GATE, ...        an ordinary SPACE -- a real spelling
#:     ## 33<SOH> The sanitiser-scope    a literal 0x01 CONTROL BYTE
#:
#: The second was a defect, repaired at 771b323 and renumbered to 32: a
#: resolver built `f"## {hi+1}\1"` inside a shell heredoc, the heredoc passed
#: `\1` through, and Python read it as \x01 instead of a backreference. So the
#: widening below legitimises the FIRST spelling and must NOT be allowed to
#: paper over the second -- a control byte in a heading is corruption, not a
#: style. That is why the control asserts BOTH that section 22 is seen and that
#: no heading carries a control byte at all.
#:
#: **IT PASSED ON A REGISTER CARRYING TWO SECTION 33s.** The premium-four
#: integration renumbered its own section onto 33 believing 33 was free --
#: because this guard said the register was unique -- and found the collision by
#: reading the headings by hand. That is this file's own failure mode arriving
#: in this file: a check that reports what you wanted.
#:
#: AND THE DOCSTRING ABOVE USED TO ASSERT THE ARTIFACT AS A FACT. It said the
#: register "has a real gap at 22". There is no gap: section 22 is at line 3736
#: and always was. A number this guard could not see became, in its own prose, a
#: property of the thing it was measuring.
HEADING = re.compile(r"^##\s+(\d+)\b", re.M)


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


def test_control_the_guard_sees_a_heading_with_no_separator():
    """SHOWN FAILING on the exact spelling this guard was blind to until
    2026-09-20, and shown blind on the OLD pattern in the same breath.

    Without the second half this is just a green that could not fail: the point
    is not that the new pattern matches, it is that the old one did NOT, so the
    widening is doing work rather than decorating.
    """
    old_pattern = re.compile(r"^##\s+(\d+)\s*[.·]", re.M)

    specimen = (
        "## 33 The sanitiser-scope wave, 2026-09-20\n"
        "\n"
        "## 33. THE PREMIUM-FOUR WAVE\n"
    )
    assert _numbers(specimen) == ["33", "33"], _numbers(specimen)
    assert old_pattern.findall(specimen) == ["33"], (
        "the OLD pattern was supposed to see only one of these two headings; "
        "if it sees both, this control no longer demonstrates anything"
    )

    counts = collections.Counter(_numbers(specimen))
    assert [n for n, c in counts.items() if c > 1] == ["33"]
    assert not [n for n, c in collections.Counter(old_pattern.findall(specimen)).items()
                if c > 1], (
        "the old pattern must report this duplicated register as UNIQUE -- that "
        "is the defect being fixed, and it is the state master was in"
    )

    # And the heading in the committed file that the old pattern still cannot
    # see. There were TWO when this control was written; the sanitiser-scope
    # wave's `## 33<SOH>` was repaired at 771b323 and renumbered to 32, leaving
    # section 22 -- a plain `## 22 <title>`, separated by an ordinary space --
    # as the surviving specimen. If this list ever empties, the widening is no
    # longer load-bearing on the real file and this control says so.
    real = REGISTER.read_text(encoding="utf-8")
    invisible = sorted(set(_numbers(real)) - set(old_pattern.findall(real)), key=int)
    assert invisible == ["22"], invisible

    # No heading carries a control byte. 771b323 put a literal SOH where a
    # separator belonged, via `f"## {hi+1}\\1"` inside a shell heredoc -- the
    # heredoc passed `\\1` to Python, which read it as \\x01 rather than as a
    # regex backreference. That byte defeated the OLD pattern too, for a
    # different reason than section 22 does, and a widened regex would have
    # HIDDEN it rather than reporting it.
    for number, line in re.findall(r"(?m)^(##\s+\d+)(.*)$", real):
        assert not any(ord(c) < 32 and c != "\t" for c in number + line), (
            "a register heading carries a control byte: %r" % (number + line)[:60]
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


#: SUBSECTIONS -- added because the guard above FAILED TO CATCH A DEFECT I CAUSED.
#:
#: Renumbering a section heading during a merge leaves its `### N.x` children
#: pointing at the old parent. I did exactly that: moved a heading 33 -> 32 and
#: left five `### 33.x` beneath it, which then collided with a LATER wave's
#: genuine `### 33.x`. Every test above passed throughout, because they only read
#: `^## `. A guard that cannot see half the structure it is named for is the
#: shape this repo spent 2026-09-20 counting -- and this one was mine.
#:
#: A RATCHET, NOT A PIN, deliberately. The file already carries 22 subsections
#: whose number disagrees with their containing parent, from long before this
#: guard existed. Demanding zero would mean renumbering published sections that
#: other documents cite by number -- trading a cosmetic defect for dangling
#: citations, which is the worse one. The count may fall; it may not rise.
ORPHAN_SUBSECTION_CEILING = 22

SUBHEADING = re.compile(r"^###\s+(\d+)\.(\d+)", re.M)


def _orphans(text: str) -> list[str]:
    """`### N.x` whose N is not the `## N` section that contains it."""
    out: list[str] = []
    parent: str | None = None
    for line in text.splitlines():
        head = HEADING.match(line)
        if head:
            parent = head.group(1)
            continue
        sub = SUBHEADING.match(line)
        if sub and parent is not None and sub.group(1) != parent:
            out.append(f"{sub.group(1)}.{sub.group(2)} under {parent}")
    return out


def test_no_new_subsection_is_orphaned_from_its_parent():
    """A renumbered heading must take its children with it."""
    found = _orphans(REGISTER.read_text(encoding="utf-8"))
    assert len(found) <= ORPHAN_SUBSECTION_CEILING, (
        "%d orphaned subsections against a ceiling of %d. Renumbering a section "
        "leaves its `### N.x` children pointing at the old parent -- move them "
        "with it. Full list: %s"
        % (len(found), ORPHAN_SUBSECTION_CEILING, found)
    )


def test_control_the_orphan_check_convicts_a_planted_renumber():
    """SHOWN FAILING on the exact defect: a heading moved, its child left behind."""
    real = REGISTER.read_text(encoding="utf-8")
    planted = real + "\n## 99. A PLANTED SECTION\n\n### 98.1 ITS CHILD, LEFT BEHIND\n"
    assert "98.1 under 99" in _orphans(planted), (
        "the orphan detector did not convict a planted renumber"
    )
    assert len(_orphans(planted)) == len(_orphans(real)) + 1
