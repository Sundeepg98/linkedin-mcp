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
    r"exactly\s+(?:\*\*)?([A-Za-z]+|\d+)(?:\*\*)?\s+"
    r"(?:such\s+)?(?:mutating\s+call|call)",
    re.IGNORECASE,
)


#: A double-quoted span. See :func:`_assertions`.
_QUOTED = re.compile(r'"[^"]*"')


def _docstring() -> str:
    return readonly.__doc__ or ""


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
