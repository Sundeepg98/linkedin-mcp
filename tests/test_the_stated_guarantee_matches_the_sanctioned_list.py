"""THE PROSE AND THE LIST MUST AGREE, AND UNTIL NOW NOTHING CHECKED.

``readonly.SANCTIONED_MUTATIONS`` cannot rot. ``test_every_sanctioned_entry_is_actually_present``
asserts, in both directions, that the list equals what the scanner finds -- so
an entry cannot go stale and a call cannot appear unlisted.

**The sentence a reader actually reads had no such guard, and it drifted.**
Measured 2026-09-19, ``readonly.py``'s module docstring stated its own
guarantee twice and both were wrong:

    line 44   "the package contains exactly ONE mutating call"
    line 74   "exactly two ... BOTH INSIDE writes.perform"
    MEASURED   FIVE entries, TWO functions, TWO files

Wrong in the count and wrong in the location. ``select_option`` and
``set_input_files`` -- a dropdown choice and a FILE UPLOAD -- were permitted
while the sentence named neither, and ``dom.activate_messaging_filter``'s
read-path click sat outside the ``writes.perform`` the sentence claimed held
both.

**THIS IS THE STANDING-INSTRUCTION CLASS.** A dated audit note rots harmlessly;
a module docstring is read as current truth by whoever opens the file next, and
this one is the first thing a reviewer reads about what the package is allowed
to do. The module warns about precisely this failure in its own words --
*"enumerating what this server does not do, without naming the things it does,
is how a true list misleads"* -- and then committed it.

**THE FIX WAS NOT A BETTER NUMBER.** A number in prose beside a list it cannot
read goes stale in silence, and re-baselining it by hand is the same edit
whether the list grew or shrank. The count was REMOVED from the prose, and this
file fails if one reappears without matching the list.
"""
from __future__ import annotations

import pathlib
import re

from linkedin_server import readonly

#: Number words this file understands, so a claim spelled out in English is
#: caught as well as one written in digits. Both spellings appeared in the two
#: stale sentences -- "exactly ONE" and "exactly two" -- which is why both
#: forms are read rather than just the digits.
_NUMBER_WORDS: dict[str, int] = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

#: A claim about how many mutating calls the package contains. The subject
#: words are what make this a claim about THIS list rather than about any
#: number that happens to sit near the word "exactly".
_COUNT_CLAIM = re.compile(
    r"(?:exactly\s+)?(?:\*\*)?([A-Za-z]+|\d+)(?:\*\*)?\s+"
    r"(?:such\s+)?(?:mutating\s+calls?|sanctioned\s+(?:entries|mutations)"
    r"|calls?\s+that\s+can\s+change)",
    re.IGNORECASE,
)

#: A BOLDED NUMBER, ANYWHERE IN THESE DOCSTRINGS.
#:
#: **THE HARDEST REAL CASE HAD NO SUBJECT AT ALL.** The stale sentence read
#: *"the scanner still reports every one of them -- **FIVE as of
#: 2026-09-19**"*, where the thing being counted is in the PREVIOUS clause. No
#: subject-anchored pattern can see that, and the count was wrong within hours.
#:
#: So this catches the FORMATTING instead: in these two docstrings a bolded
#: numeral has only ever been a count claim. **That is a convention, not a
#: meaning**, and it is the weaker kind of rule -- stated plainly because the
#: next person to bold a number for some other reason will meet it.
#:
#: Measured before adopting rather than assumed safe: **zero hits across both
#: current docstrings**, and a hit on the real stale string. If it ever fires
#: on a legitimate bolded number, do not widen it -- unbold the number or quote
#: it, because a bolded count in these files is the thing that keeps rotting.
_BOLD_NUMBER = re.compile(
    r"\*\*(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
    re.IGNORECASE,
)

#: THE MODULES THAT STATE THIS GUARANTEE IN PROSE. Both, because both did.
#:
#: **``writes.py`` WAS THE SECOND HOME AND WAS MISSED**, which is how a count
#: survived being fixed in ``readonly.py``: its docstring opened "FIVE mutating
#: calls exist in this package" and nothing compared that to anything either.
_GUARANTEE_MODULES = ("readonly", "writes")


#: A double-quoted span. See :func:`_assertions`.
_QUOTED = re.compile(r'"[^"]*"')


def _docstring() -> str:
    """Every prose home of the guarantee, concatenated.

    **WIDENED 2026-09-19 AFTER THIS GUARD MISSED TWO REAL STALE COUNTS**, both
    written by the wave that had just fixed the first one. It read only
    ``readonly.__doc__``; ``writes.__doc__`` stated the same guarantee and
    drifted independently.
    """
    from linkedin_server import writes as _writes
    parts = [readonly.__doc__ or ""]
    parts.append(_writes.__doc__ or "")
    return "\n".join(parts)


def _assertions() -> str:
    """The docstring with QUOTED SPANS REMOVED. A quotation is not a claim.

    **THIS RULE WAS FORCED BY THE GUARD FIRING ON ITS OWN CORRECTION**, and the
    alternative was worse. When the stale sentence was fixed, the fix RECORDED
    what the sentence used to say -- because a correction that erases the thing
    it corrects buys the reader's trust and tells them nothing. That record
    quotes the defective phrase verbatim, and the first version of this guard
    could not tell the quotation from a fresh claim.

    The tempting fix was to reword the correction until the test went green.
    That is the tail wagging the dog: this file's own false-positive control
    warns that every spurious hit is pressure to re-word the docstring around
    the test, and taking that route would have made the record less exact in
    order to satisfy a regex.

    So the guard learned the distinction instead. **A DOCUMENT REPORTING WHAT
    IT USED TO SAY IS NOT ASSERTING IT.** Quoting is how this repository
    records a corrected claim -- the module does it three times for earlier
    drifts -- so a guard over prose in this codebase has to read quotation
    marks or it will fight the correction convention every time it fires.

    Note the limit, because it is real: a claim that HAPPENS to be inside
    quotes is invisible here. That trade is deliberate. The failure mode it
    accepts (a quoted live claim) requires somebody to write a guarantee as a
    quotation, which nothing in this module does; the failure mode it avoids
    (every correction tripping the guard) is certain and recurring.
    """
    return _QUOTED.sub(" ", _docstring())


def _claimed_counts() -> list[int]:
    out: list[int] = []
    for raw in _COUNT_CLAIM.findall(_assertions()):
        token = raw.strip().lower()
        if token.isdigit():
            out.append(int(token))
        elif token in _NUMBER_WORDS:
            out.append(_NUMBER_WORDS[token])
    return out


def test_no_stale_count_claim_survives_in_the_docstring():
    """THE GUARD. A number in the prose must equal the list, or not be there.

    Both outcomes are acceptable and the second is preferred: the count was
    removed rather than corrected, because a number that has to be re-typed
    every time the list moves is a number somebody eventually re-types wrong.
    """
    claimed = _claimed_counts()
    actual = len(readonly.SANCTIONED_MUTATIONS)
    wrong = [n for n in claimed if n != actual]
    assert not wrong, (
        f"readonly.py's docstring claims the package contains exactly "
        f"{wrong} mutating call(s); SANCTIONED_MUTATIONS holds {actual}.\n\n"
        "This sentence is the first thing a reviewer reads about what the "
        "package may do, and it drifted through three widenings because "
        "nothing compared it to the list. Prefer deleting the number and "
        "pointing at SANCTIONED_MUTATIONS: a count in prose beside a list it "
        "cannot read goes stale in silence."
    )


def test_the_docstring_does_not_claim_a_single_home_for_the_sanctions():
    """The OTHER half of the drift, and it was the less visible one.

    The stale sentence said the permitted calls were "both inside
    writes.perform". That was false from 2026-08-26, when a READ-path click in
    ``dom.activate_messaging_filter`` was admitted -- a widening in a second
    FILE, which a count alone would never have surfaced even if the count had
    been right.
    """
    functions = {function for _path, function, _kind in readonly.SANCTIONED_MUTATIONS}
    files = {path for path, _function, _kind in readonly.SANCTIONED_MUTATIONS}
    text = _assertions().lower()
    if len(functions) > 1 or len(files) > 1:
        assert "both inside" not in text, (
            f"the docstring says the sanctioned calls are 'both inside' one "
            f"place, but they span {sorted(files)} / {sorted(functions)}. A "
            "claim about WHERE is as load-bearing as one about HOW MANY, and "
            "it is the one a count cannot catch."
        )


def test_the_claim_detector_actually_fires():
    """SHOWN FAILING, on the two real sentences this file was written for.

    A prose guard that matches nothing passes forever, and this one is a regex
    over English -- the class most likely to be silently inert. So it is run
    against the exact strings that were in the file, from the file's own
    history, rather than against something convenient.
    """
    historical = (
        "Since 2026-08-23 the package contains exactly ONE mutating call, and",
        "It contains **exactly two** calls that can change anything on LinkedIn,",
    )
    for sentence in historical:
        found = _COUNT_CLAIM.findall(sentence)
        assert found, (
            f"the detector did not fire on a sentence that really shipped: "
            f"{sentence!r}. A prose guard that cannot match the prose it was "
            "written for certifies nothing."
        )
    # And the numbers come back as NUMBERS, not as the words they were spelled
    # in -- the half that would silently pass if only the regex were checked.
    assert _NUMBER_WORDS["one"] == 1
    assert _NUMBER_WORDS["two"] == 2


def test_the_detector_catches_the_phrasings_that_got_past_it():
    """THE REGRESSION, AND ALL THREE STRINGS REALLY SHIPPED.

    **This guard was written on 2026-09-19 and two stale counts got past it the
    same day** -- both written by the wave that had just fixed the first one,
    which is the sharper half. It required the word ``exactly`` and a following
    ``mutating call``, so it saw neither of the forms that actually appeared:

        readonly.py   "FIVE as of 2026-09-19"     -- no "exactly", no subject
        writes.py     "FIVE mutating calls exist" -- no "exactly"

    A prose guard is the class most likely to be silently inert, and this one
    was: it matched the two historical sentences it had been written against
    and nothing else. **A detector built from the examples you already know is
    a detector that finds the examples you already know.**
    """
    shipped = (
        "FIVE mutating calls exist in this package.",
        "The package still contains exactly five mutating calls",
        "It contains **exactly two** calls that can change anything on LinkedIn,",
    )
    for sentence in shipped:
        assert _COUNT_CLAIM.findall(sentence), (
            f"the widened detector STILL does not see a real stale count: "
            f"{sentence!r}"
        )

    # THE SUBJECTLESS ONE, caught by FORMATTING rather than by meaning. Its
    # subject is in the previous clause, so no anchored pattern can reach it.
    subjectless = "still reports every one of them -- **FIVE as of 2026-09-19**"
    assert not _COUNT_CLAIM.findall(subjectless), (
        "if the anchored pattern has started matching this, the bold rule is "
        "no longer the thing catching it and this test is testing nothing."
    )
    assert _BOLD_NUMBER.findall(subjectless), (
        "the subjectless stale count is invisible to BOTH rules, which is the "
        "state that shipped it in the first place."
    )


def test_a_bolded_number_in_these_docstrings_is_a_count_claim():
    """THE CONVENTION RULE, and its false-positive control.

    Adopted only after measuring: zero hits across both current docstrings,
    and a hit on the real stale string. It catches FORMATTING rather than
    MEANING, which is the weaker kind of rule and is why the measurement came
    before the adoption rather than after.
    """
    assert not _BOLD_NUMBER.findall(_assertions()), (
        f"a bolded number is live in a guarantee docstring: "
        f"{_BOLD_NUMBER.findall(_assertions())}. In these two files that has "
        "only ever been a count claim, and every one of them has gone stale. "
        "Unbold it or quote it -- do not relax this rule."
    )


def test_the_second_prose_home_is_scanned():
    """``writes.py`` STATED THE SAME GUARANTEE AND WAS NEVER CHECKED.

    That is how a count survived being fixed in ``readonly.py``: the guard
    read one module's docstring and the drift was in another's. The scope is
    now both, and this asserts the second one is really being read rather than
    added to a tuple nobody consults.
    """
    from linkedin_server import writes as _writes

    assert "writes" in _GUARANTEE_MODULES
    text = _docstring()
    assert (_writes.__doc__ or "")[:60] in text, (
        "writes.__doc__ is not reaching the scanned text"
    )
    assert (readonly.__doc__ or "")[:60] in text


def test_the_scope_limit_is_recorded_rather_than_implied():
    """COMMENTS ARE NOT SCANNED, AND THAT IS A KNOWN HOLE.

    A third stale count shipped in a ``readonly.py`` COMMENT -- an entry
    labelled by ordinal inside ``SANCTIONED_MUTATIONS`` -- and this guard reads
    docstrings only, so it would not have caught that one either. It was fixed
    by hand.

    **Scanning every comment for numerals would be unusable**: the module's
    comments legitimately count entity kinds, tabs, categories, alert rows and
    call sites, and a guard that fired on those would be widened into
    uselessness within a day. So the limit is DECLARED here rather than left
    for somebody to discover by shipping past it.
    """
    source = pathlib.Path(readonly.__file__).read_text(encoding="utf-8")
    comment_lines = [
        line for line in source.splitlines()
        if line.strip().startswith("#") and "mutating call" in line.lower()
    ]
    # Not an assertion about the count -- an assertion that the SCANNED text
    # and the FULL SOURCE are different things, which is the limit itself.
    assert len(source) > len(_docstring()), (
        "the guard appears to be reading the whole source; if that became "
        "true, this test should be replaced by a real comment-scanning check."
    )
    assert isinstance(comment_lines, list)


def test_the_detector_does_not_fire_on_ordinary_prose():
    """THE FALSE-POSITIVE CONTROL.

    ``exactly`` is a common word in this module and most of its uses say
    nothing about the sanctioned list. A guard that flagged them would be
    re-worded into uselessness within a week.
    """
    innocuous = (
        "captures exactly that group out of either form.",
        "which is exactly why this refuses",
        "it contains exactly the patterns a reviewer reads",
        "exactly one place in this package can reach a file input",
    )
    for sentence in innocuous:
        assert not _COUNT_CLAIM.findall(sentence), (
            f"the detector fired on ordinary prose: {sentence!r}. Every false "
            "positive here is pressure to re-word the docstring around the "
            "test, which is the tail wagging the dog."
        )


def test_a_quoted_historical_claim_does_not_fire_and_a_live_one_does():
    """THE QUOTATION RULE, pinned in BOTH directions.

    This is the rule that lets a correction record what it corrected without
    tripping the guard, and a rule that only ever passes is not a rule -- so
    the live form must still fire.
    """
    live = 'It contains exactly two calls that can change anything.'
    quoted = 'The old text read "It contains exactly two calls" and is wrong.'

    assert _COUNT_CLAIM.findall(_QUOTED.sub(" ", live)), (
        "an UNQUOTED claim stopped firing, which would make the guard inert."
    )
    assert not _COUNT_CLAIM.findall(_QUOTED.sub(" ", quoted)), (
        "a QUOTED historical claim still fires, so every correction that "
        "records what it corrected will trip this guard -- and the only way "
        "out would be to make the correction less exact."
    )


def test_the_docstring_still_points_at_the_list():
    """Removing the number is only safe if the pointer survives.

    A docstring that dropped the count AND the reference would leave a reader
    with no way to find out, which is worse than a stale number: a wrong number
    at least tells you what question to ask.
    """
    text = _docstring()
    assert "SANCTIONED_MUTATIONS" in text, (
        "the docstring no longer names SANCTIONED_MUTATIONS. The count was "
        "removed from the prose on the understanding that the list is where a "
        "reader goes instead -- without the pointer, that trade is a loss."
    )


def test_the_sanctioned_list_is_not_empty():
    """A guard comparing prose against an empty list would pass on silence."""
    assert readonly.SANCTIONED_MUTATIONS, "the sanctioned list is empty"
    for entry in readonly.SANCTIONED_MUTATIONS:
        assert len(entry) == 3, f"malformed sanction entry: {entry!r}"
