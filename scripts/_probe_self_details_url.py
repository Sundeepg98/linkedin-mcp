"""Does LinkedIn SERVE the skills document at `/in/me/details/skills/`?

ONE QUESTION, AND IT IS THE MEASUREMENT A RULING IS WAITING ON.

`tests/test_navigation_is_never_derived.py` found a third site of the
derived-navigation class, and unlike the two probes it is not in a probe --
it is shipped:

    slug = shape.profile_slug_from(final_url)          # server.py:1695
    skills_url = f"{BASE_URL}/in/{slug}/details/skills/"
    skills_final = await BROWSER.goto(page, skills_url)

`linkedin_my_profile(include_skills=True)` aims a navigation at a url built
from a slug parsed OUT OF A LANDED URL. It is SAFE TODAY -- the allowlist
admits `/in/<member>/details/skills/`, so the navigation succeeds and no
refusal fires -- and it is the same class: the aim comes from the page rather
than from this repository.

**THE LIKELY FIX IS `/in/me/details/skills/` AND IT IS A GUESS UNTIL MEASURED.**
`me` matches the same allowlist pattern
(`/in/[A-Za-z0-9\\-_%]+/details/(skills|experience|education)/?`), and the
argument that carried the payload probes carries here too: `/in/me` is
LinkedIn's own self-reference, so it names the signed-in member and nobody
else, where a vanity path names merely SOME member. But **whether LinkedIn
serves the skills document at that address is a fact about LinkedIn**, and
changing a shipped read tool on an unverified guess is how a working
capability breaks quietly.

So this takes the measurement. Either outcome is an answer:

    IT SERVES         the fix is viable and `server.py:1695` can stop deriving
    IT DOES NOT       the derivation is load-bearing, the declaration in
                      KNOWN_DERIVED_NAVIGATIONS becomes permanent rather than
                      pending, and it gets that reason written beside it

## Bounds

**IT NAVIGATES A MODULE-LEVEL CONSTANT AND NOTHING ELSE**, which is the rule
this probe exists in service of -- a probe that measured the derived-navigation
fix by deriving a navigation would be the joke version of itself.
`tests/test_navigation_is_never_derived.py` scans this file like any other.

**IT COUNTS AND DOES NOT PRINT CONTENT.** His skills are his, not a third
party's, so the disclosure argument here is weaker than the payload probes' --
and the discipline is kept anyway, because a probe that prints his profile
content into a transcript is a habit worth not having. Counts, and the RELATION
between the address asked for and the one that came back. No url, no member
path, no skill name -- see `_shape_of`, which exists because the first run of
this probe printed his slug.

**NO OUTPUT PATH.** None, and no constant to become one.

**IT IS A READ.** Two allowlisted GETs of his own profile, nothing pressed,
nothing typed. `linkedin_who_viewed_me` establishes that the durable-record
cost belongs to loading OTHER people's profiles.

Run:  python scripts/_probe_self_details_url.py
Writes NOTHING.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

#: THE TWO ADDRESSES, BOTH MODULE-LEVEL CONSTANTS. Neither is built from
#: anything the page said.
SELF_PROFILE_URL = f"{BASE_URL}/in/me/"
SELF_SKILLS_URL = f"{BASE_URL}/in/me/details/skills/"


def _path_of(url: str) -> str:
    """The path of a url and nothing else -- no host, no query."""
    return urlsplit(str(url or "")).path.rstrip("/")


def _shape_of(url: str, requested: str) -> str:
    """WHAT HAPPENED TO AN ADDRESS, never the address it became.

    **THIS EXISTS BECAUSE THE FIRST RUN OF THIS PROBE PRINTED HIS SLUG.** The
    docstring above promised "a path, a status and counts -- never a url", and
    a member path IS an identity. `/in/me/details/skills/` REDIRECTS to
    `/in/<vanity>/details/skills`, so printing the landed path published the
    thing the whole day has been spent not publishing.

    The reasoning that let it through is worth naming, because it was borrowed
    and did not transfer: the resolver's tally emits paths and argues that
    costs no disclosure. True THERE -- every path it sees is a resource path
    and the profile document is served at `/in/me`. False HERE, where the
    landed path is a member path by construction.

    **A DISCLOSURE ARGUMENT IS ABOUT A PARTICULAR SET OF STRINGS, NOT ABOUT A
    KIND OF FIELD.** "Paths are safe" was never the rule; "these paths are
    safe" was, and carrying the short form one file over published a slug.

    So this returns the RELATION between what was asked for and what came
    back -- served, redirected within the member space, or redirected away --
    and the relation is what the question actually needs.
    """
    landed = _path_of(url)
    asked = _path_of(requested)
    if landed == asked:
        return "SERVED AT THE REQUESTED ADDRESS (no redirect)"
    if landed.startswith("/in/") and landed.endswith(asked.split("/in/me", 1)[-1]):
        return (
            "REDIRECTED to the same resource under a member path "
            "(slug withheld -- it is an identity)"
        )
    return "REDIRECTED ELSEWHERE (%d path segments)" % len(
        [part for part in landed.split("/") if part]
    )


async def main() -> None:
    print("=== DOES /in/me/details/skills/ SERVE THE SKILLS DOCUMENT?")
    print("    one question, two allowlisted reads, nothing pressed")
    print("    prints a path, a status and counts -- never a url or a skill\n")

    await BROWSER.start()
    async with BROWSER.session() as page:
        # THE AUTH WALL FIRST, off the profile itself, because a skills page
        # read while signed out is a measurement of the login screen.
        landed = await BROWSER.goto(page, SELF_PROFILE_URL)
        if "/login" in landed or "/checkpoint" in landed:
            print("    AUTH WALL. Not signed in, so nothing was measured.")
            await BROWSER.stop()
            return
        print("    signed in. profile: %s"
              % _shape_of(landed, SELF_PROFILE_URL))

        # THE MEASUREMENT. A CONSTANT, not a url derived from the line above.
        skills_landed = await BROWSER.goto(page, SELF_SKILLS_URL)
        print("    /in/me/details/skills/: %s"
              % _shape_of(skills_landed, SELF_SKILLS_URL))
        if "/login" in skills_landed or "/checkpoint" in skills_landed:
            print("    AUTH WALL on the skills address. Nothing measured.")
            await BROWSER.stop()
            return

        records = await dom.harvest_linked_cards(
            page,
            href_pattern=dom.SKILL_HREF,
            max_items=200,
            max_chars=300,
        )
        with_text = sum(1 for record in records if (record.get("text") or "").strip())
        print(f"\n    skill cards harvested: {len(records)}")
        print(f"    of those carrying text: {with_text}")
        print("    (the same harvest server.py runs, with the same arguments,")
        print("     off the /in/me spelling instead of the derived one)")

        print("\n=== READING")
        if records:
            print("    IT SERVES. The skills document is at /in/me/details/skills/")
            print("    and the shipped harvest finds cards there. The derivation")
            print("    at server.py:1695 is REPLACEABLE by this constant.")
            print("    NOT A LICENCE TO EDIT ON THIS ALONE -- a card count is not")
            print("    proof the two documents agree. What it settles is that the")
            print("    address is served, which is the half that was unknown.")
        else:
            print("    ZERO CARDS. That is NOT yet 'LinkedIn does not serve it':")
            print("    the page may render skills only after a scroll, and this")
            print("    probe does not scroll. Read the RELATION above -- redirected")
            print("    elsewhere means the address is not served; served or")
            print("    redirected within the member space means it is, and the")
            print("    harvest is what came back empty. Different findings.")

    await BROWSER.stop()


# GUARDED: importing a script must not DO anything.
# ``tests/test_scripts_are_import_safe.py`` asserts that for every script here.
if __name__ == "__main__":
    asyncio.run(main())
