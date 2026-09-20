"""WHAT DOES THE /company/ ENTRY OPEN, AND WHAT WOULD FOUR WRONG SPELLINGS?

``scripts/blast_radius.py`` answers "what does this candidate newly admit"
for ANY pattern, over a corpus assembled from what this repository has already
argued about. Its corpus holds exactly ONE ``/company/`` address, so it cannot
see the family this entry had to refuse.

This script supplies the missing denominator -- forty-one company-family
spellings, every one a real neighbour of the admitted address rather than a
synthetic near-miss -- and runs the SHIPPED candidate beside FOUR CONTROLS, so
the entry's narrowness is an instrument reading rather than a claim:

    the shipped entry            the school character class, anchored
    numeric only                 the tempting narrower entry, for comparison
    the backslash-d spelling     any Unicode decimal digit
    the dot admitted             what a dotted slug costs
    the FAMILY pattern           the standing boundary trap on this root

**A GUARD THAT HAS ONLY EVER PASSED CERTIFIES NOTHING**, so three of the four
controls are expected to open MORE, and the report says by how much and which.

**AND IT MEASURES AGAINST THE ROSTER WITHOUT THE SHIPPED ENTRY.** That is not
a nicety: this probe's FIRST run was taken after the entry had landed and
reported NEWLY ADMITTED 0 for it -- true, and useless, because the question
the comment beside that entry answers is what it admitted.

Opens no browser. Navigates nothing. Reads no page. The roster is restored in
a ``finally`` here and again in ``blast_radius.newly_admitted``'s own.

Run:  ./venv/Scripts/python.exe scripts/_probe_company_family_blast.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402
from linkedin_server import readonly  # noqa: E402

BASE = "https://www.linkedin.com"

#: A slug and an id, both synthetic, both in the spellings this repository's
#: corpora already use. No third party is addressed by this file. The id is
#: the one ``tests/fixtures/notifications.html`` carries and is already on
#: ``tests/test_no_committed_identity.SYNTHETIC_IDS``: a value the identity
#: guard has already ruled on beats a freshly minted one, which would spend
#: that guard's precision on a string nothing needed.
SLUG = "a-company"
IDENTIFIER = "5417062"

#: THE FOUR OTHER SCRIPTS' DIGITS, AS CODE POINTS RATHER THAN CHARACTERS, so
#: THIS FILE STAYS PURE ASCII. ``str.isdigit()`` is True of every one of these
#: and the ``re`` escape for a digit matches every one of them, which is the
#: entire reason the shipped entry names the ten ASCII digits instead.
#:
#: A tracked source carrying the characters it is testing for cannot be read
#: by the ascii decoder ``tests/test_readonly_boundary_invariant.py`` uses,
#: and a probe that breaks the tree it is measuring has measured nothing.
NON_ASCII_DIGITS: dict[str, str] = {
    "arabic_indic": "".join(chr(0x0661 + n) for n in range(4)),
    "extended_arabic": "".join(chr(0x06F1 + n) for n in range(4)),
    "devanagari": "".join(chr(0x0967 + n) for n in range(4)),
    "fullwidth": "".join(chr(0xFF11 + n) for n in range(4)),
}


#: FORTY-ONE CONCRETE ADDRESSES. Every one is a real neighbour: the tabs are
#: drawn by the Page itself, the admin paths are the write half of the same
#: root, the traversals are the class ``search_results.py`` measured
#: normalising onto an account-ending address, and the four non-ASCII digit
#: runs are the spellings a bare digit escape admits and ``[0-9]`` does not.
def family() -> list[str]:
    return [
        # the spellings the entry is written for
        f"{BASE}/company/{SLUG}/",
        f"{BASE}/company/{SLUG}",
        f"{BASE}/company/{IDENTIFIER}/",
        f"{BASE}/company/{IDENTIFIER}",
        # every tab the Page draws
        f"{BASE}/company/{SLUG}/about/",
        f"{BASE}/company/{SLUG}/people/",
        f"{BASE}/company/{SLUG}/jobs/",
        f"{BASE}/company/{SLUG}/life/",
        f"{BASE}/company/{SLUG}/posts/",
        f"{BASE}/company/{SLUG}/products/",
        f"{BASE}/company/{SLUG}/services/",
        f"{BASE}/company/{SLUG}/videos/",
        f"{BASE}/company/{SLUG}/events/",
        f"{BASE}/company/{SLUG}/insights/",
        f"{BASE}/company/{SLUG}/insights/?insightType=HEADCOUNT",
        f"{BASE}/company/{IDENTIFIER}/people/",
        # the write half of the same root
        f"{BASE}/company/{SLUG}/admin/",
        f"{BASE}/company/{SLUG}/admin/dashboard/",
        f"{BASE}/company/{SLUG}/admin/settings/",
        f"{BASE}/company/setup/new/",
        # queries
        f"{BASE}/company/{SLUG}/?foo=1",
        f"{BASE}/company/{SLUG}/?trk=x",
        f"{BASE}/company/{SLUG}/people/?keywords=x",
        # parents and roots
        f"{BASE}/company/",
        f"{BASE}/company",
        # traversals
        f"{BASE}/company/{SLUG}/../../mypreferences/d/close-account",
        f"{BASE}/company/{SLUG}/../../psettings/member-data",
        f"{BASE}/company/{SLUG}/../../in/someone-else/",
        f"{BASE}/company/../mypreferences/d/",
        f"{BASE}/company/{SLUG}/..",
        # dotted segments
        f"{BASE}/company/a.company/",
        f"{BASE}/company/a..company/",
        f"{BASE}/company/./",
        # a urn spelling
        f"{BASE}/company/urn:li:organization:12345/",
        # the four non-ASCII digit spellings of one id
        f"{BASE}/company/" + NON_ASCII_DIGITS["arabic_indic"] + "/",
        f"{BASE}/company/" + NON_ASCII_DIGITS["extended_arabic"] + "/",
        f"{BASE}/company/" + NON_ASCII_DIGITS["devanagari"] + "/",
        f"{BASE}/company/" + NON_ASCII_DIGITS["fullwidth"] + "/",
        # slugs carrying a forbidden substring: refused one gate earlier
        f"{BASE}/company/connect-solutions/",
        f"{BASE}/company/invite-partners/",
        f"{BASE}/company/{SLUG}/follow/",
    ]


CANDIDATES: tuple[tuple[str, str], ...] = (
    (
        "THE SHIPPED ENTRY -- the school class, anchored",
        r"^https://www\.linkedin\.com/company/[A-Za-z0-9%\-_]{1,100}/?$",
    ),
    (
        "CONTROL: numeric only, the tempting narrower entry",
        r"^https://www\.linkedin\.com/company/[0-9]{1,20}/?$",
    ),
    (
        "CONTROL: the digit escape, the spelling the groups entry refused",
        r"^https://www\.linkedin\.com/company/\d+/?$",
    ),
    (
        "CONTROL: a dot inside the character class",
        r"^https://www\.linkedin\.com/company/[A-Za-z0-9%\-_.]{1,100}/?$",
    ),
    (
        "CONTROL: THE FAMILY PATTERN THIS ENTRY MUST NOT BE",
        r"^https://www\.linkedin\.com/company/.*$",
    ),
)

#: The prefix that identifies this wave's entry on the shipped roster.
#:
#: **THE NEEDLE IS THE WHOLE PREFIX, NOT THE SUBSTRING ``/company/``.** The
#: first spelling of this filter used the substring and removed TWO patterns:
#: this entry AND ``/mynetwork/network-manager/company/``, the Manage-Pages
#: list, which has nothing to do with this wave. It happened not to change a
#: single number, because that address is in no corpus here -- so the defect
#: would have survived the run that found it.
_ENTRY_PREFIX = "^https://www\\.linkedin\\.com/company/"


def without_the_company_entry() -> tuple:
    """The roster AS IT STOOD BEFORE this wave, so the reading reproduces.

    Removal is by PATTERN SOURCE rather than by index, so it survives the
    roster being reordered, and the count removed is printed -- a filter that
    silently removed nothing would make every candidate below look narrower
    than it is.
    """
    return tuple(
        pattern for pattern in readonly._ALLOWED_URL_PATTERNS
        if not pattern.pattern.startswith(_ENTRY_PREFIX)
    )


def _show(text: str) -> str:
    """ASCII-safe, because a cp1252 console cannot print a Devanagari digit
    and a probe that dies on its own output has measured nothing."""
    return text.encode("ascii", "backslashreplace").decode("ascii")


def _report(urls: list[str]) -> int:
    for label, candidate in CANDIDATES:
        result = blast_radius.newly_admitted(candidate, urls)
        undefended = set(result["newly_admitted_and_defended_by_nothing"])
        print("")
        print("=" * 72)
        print(label)
        print("  pattern %s" % candidate)
        print("  tested %d | already admitted %d | NEWLY ADMITTED %d"
              % (result["tested"], result["already_admitted"],
                 len(result["newly_admitted"])))
        for url in result["newly_admitted"]:
            flag = "!!! defended by nothing" if url in undefended else "  +"
            print("    %s %s" % (flag, _show(url)))
        if result["newly_refused"]:
            print("  NEWLY REFUSED -- an allowlist entry cannot refuse more,")
            print("  so a non-empty list means the candidate BROKE a pattern:")
            for url in result["newly_refused"]:
                print("    - %s" % _show(url))
    print("")
    print("THE DENOMINATOR IS THE POINT. A LOWER BOUND over these addresses.")
    return 0


def main() -> int:
    shipped = blast_radius.corpus()
    urls = sorted(set(shipped) | set(family()))
    print("corpus %d addresses = shipped %d + company family %d"
          % (len(urls), len(shipped), len(family())))

    original = readonly._ALLOWED_URL_PATTERNS
    stripped = without_the_company_entry()
    removed = len(original) - len(stripped)
    print("roster %d patterns; measuring against %d, with the %d /company/"
          % (len(original), len(stripped), removed))
    print("entr%s removed, so every number below is what it ADMITTED."
          % ("y" if removed == 1 else "ies"))
    if removed == 0:
        print("")
        print("NOTE: nothing was removed, so this run measures a tree with no")
        print("/company/ entry at all. The numbers are still the candidates'")
        print("own; they are simply not a delta over this wave.")

    try:
        readonly._ALLOWED_URL_PATTERNS = stripped
        return _report(urls)
    finally:
        readonly._ALLOWED_URL_PATTERNS = original


if __name__ == "__main__":
    raise SystemExit(main())
