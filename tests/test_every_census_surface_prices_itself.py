"""A SURFACE THAT COSTS SOMETHING MUST SAY SO, AND ABSENCE IS A CLAIM.

``server.CENSUS_SURFACE_COST`` carries, per census key, what loading that page
spends. It is emitted ON THE ANSWER -- ``out["cost"]`` -- and not only in a
docstring, because *"a cost written where the caller does not look is a cost the
caller was not told about"*.

**THE TABLE HAS A RULE AND THE RULE IS LOAD-BEARING.** ``server.py`` states it
while explaining why one surface is absent:

    "It is absent from CENSUS_SURFACE_COST below, which by that table's own
    rule means 'believed to cost nothing' -- BELIEVED, NOT MEASURED."

So an absence is not a blank. It is an assertion that the page is free, made by
whoever added the key, in the only way the table can express it: by saying
nothing. **Nothing enforced that.** Measured 2026-09-19: 12 surfaces, 5 priced,
7 silent, and no test anywhere requires a new key to do either.

That matters because of what the priced entries actually say. Two of the five
are composers, and both carry this:

    "A COMPOSER MAY AUTOSAVE. This loads the post composer, types nothing and
    clicks nothing -- but if LinkedIn saves a draft on open, this server cannot
    see it: 17 candidate draft-listing addresses were run against the read
    boundary on 2026-08-31 and all 17 were refused ... The operator cleared
    this cost knowingly."

**So the autosave exposure is DISCLOSED AND RULED, not unsanctioned** -- a
distinction worth keeping, because it has been reported the other way. What is
unsanctioned is a FUTURE surface: add a third composer to ``CENSUS_SURFACES``
tomorrow, forget the cost line, and the emit path at ``server.py`` is
``if key in CENSUS_SURFACE_COST`` -- so the caller is told nothing at all, and
the table's own rule silently reclassifies the omission as "believed free".

This file makes that omission a test failure instead. It does not decide what
anything costs; it requires somebody to have decided.
"""
from __future__ import annotations

from linkedin_server import server

#: Surfaces asserted to cost NOTHING, each with the reason somebody is
#: standing behind. This is the explicit form of what the table previously
#: expressed by silence.
#:
#: **THESE ARE THE SEVEN THAT WERE ALREADY SILENT**, transcribed rather than
#: re-adjudicated: this file's job is to stop the NEXT silent one, not to
#: re-open seven rulings it did not make. Where the existing prose already
#: records a doubt, the doubt is carried across verbatim rather than smoothed.
BELIEVED_FREE: dict[str, str] = {
    "feed": (
        "The feed is this server's default read and has been loaded routinely "
        "since it shipped. It carries the nav badges rather than consuming "
        "them -- the messaging and invitation badges are READ off /feed/ "
        "precisely because loading it does not move them, which is the "
        "before/after discipline several probes depend on."
    ),
    "profile": (
        "His own profile. No third party on the page, and it is the other "
        "surface the nav badges are read from."
    ),
    "profile_edit_intro": (
        "The intro editor on HIS OWN profile. An editor rather than a "
        "composer: it opens populated with values that already exist and "
        "creates no new artefact, so there is no draft for LinkedIn to "
        "autosave."
    ),
    "settings": (
        "The settings INDEX. It renders links; the pages carrying actual "
        "toggles are refused by the read boundary."
    ),
    "settings_dark_mode": (
        "One named settings page below the index, admitted individually."
    ),
    "premium": (
        "His own subscription page. One question was asked of it -- whether "
        "an InMail balance is countable -- and it holds no third party."
    ),
    "search_appearances": (
        "BELIEVED FREE WITH A STATED DOUBT, carried across from the comment "
        "on the key itself rather than resolved here: the address carries no "
        "member segment so it can only resolve to whoever is signed in, and "
        "it changes no value the account holds -- but WHETHER THE SURFACE "
        "CARRIES A COUNTER OF ITS OWN IS UNMEASURED. Notifications and "
        "messaging are refused as census keys because their badges are "
        "measured to reset on load, and nobody has looked at this one. The "
        "first reading is what fills this in."
    ),
}


def test_every_census_surface_is_priced_or_declared_free():
    """THE GUARD. A new key must cost something or be argued free."""
    surfaces = set(server.CENSUS_SURFACES)
    priced = set(server.CENSUS_SURFACE_COST)
    declared_free = set(BELIEVED_FREE)
    unaccounted = sorted(surfaces - priced - declared_free)
    assert not unaccounted, (
        f"these census surfaces neither declare a cost nor argue they are "
        f"free: {unaccounted}.\n\n"
        "By CENSUS_SURFACE_COST's own rule an absence MEANS 'believed to cost "
        "nothing', so a missing entry is an assertion somebody made by "
        "omission. The emit path is `if key in CENSUS_SURFACE_COST`, which "
        "means a caller loading this surface is told nothing at all. Either "
        "add the cost, or add the key to BELIEVED_FREE with the reason you "
        "are standing behind. This test does not decide what it costs; it "
        "requires that somebody did."
    )


def test_no_surface_is_both_priced_and_declared_free():
    """A key in both tables is two answers to one question.

    The reader who finds the free declaration first would conclude the load is
    free while the answer emits a cost -- and this package's standing complaint
    about its own docstrings is exactly that shape.
    """
    both = sorted(set(server.CENSUS_SURFACE_COST) & set(BELIEVED_FREE))
    assert not both, (
        f"these surfaces are priced AND declared free: {both}. Remove one. "
        "The cost table wins on the answer, so a stale free-declaration is "
        "the one that misleads a reader."
    )


def test_neither_table_names_a_surface_that_does_not_exist():
    """A cost or a free-declaration for a removed key grants nothing and hides
    the next real omission behind a familiar name."""
    surfaces = set(server.CENSUS_SURFACES)
    stale_cost = sorted(set(server.CENSUS_SURFACE_COST) - surfaces)
    stale_free = sorted(set(BELIEVED_FREE) - surfaces)
    assert not stale_cost, f"cost entries for surfaces that do not exist: {stale_cost}"
    assert not stale_free, f"free declarations for surfaces that do not exist: {stale_free}"


def test_the_two_composers_still_disclose_the_autosave():
    """THE DISCLOSURE THAT IS ALREADY RIGHT, PINNED SO IT STAYS ATTACHED.

    Both composer surfaces carry a cost naming the autosave risk. That text is
    the ONLY thing standing between a caller and an undetectable draft, because
    every draft-listing address is refused by the read boundary -- so if the
    sentence is ever trimmed, nothing else reports the exposure.

    Pinned by SUBSTANCE rather than by exact text, so rewording is free and
    deletion is not.
    """
    for key in ("post_composer", "article_composer"):
        assert key in server.CENSUS_SURFACE_COST, (
            f"{key} lost its cost declaration. It is a COMPOSER: loading it "
            "may autosave a draft this server has no reachable surface to "
            "detect."
        )
        text = server.CENSUS_SURFACE_COST[key].lower()
        assert "autosave" in text, (
            f"{key}'s cost text no longer names the autosave. The operator "
            "cleared that cost knowingly and this sentence is the record of "
            "what was cleared."
        )


def test_a_new_surface_without_a_cost_is_caught():
    """SHOWN FAILING, against a simulated addition rather than a real edit.

    The simulation is the honest form here: the real failure mode is somebody
    adding a key to CENSUS_SURFACES, and reproducing that by mutating the
    module at import time would leave the process in a state later tests read.
    """
    surfaces = set(server.CENSUS_SURFACES) | {"newsletter_composer"}
    priced = set(server.CENSUS_SURFACE_COST)
    unaccounted = surfaces - priced - set(BELIEVED_FREE)
    assert unaccounted == {"newsletter_composer"}, (
        "a newly added surface with no cost and no free-declaration was not "
        "flagged, so this guard would not catch the case it exists for."
    )


def test_the_surface_count_is_not_silently_shrinking():
    """A guard over an empty table passes forever.

    Deliberately a floor and not a pin: waves add surfaces, and a number that
    has to be edited every time is a number people edit without reading.
    """
    assert len(server.CENSUS_SURFACES) >= 12, (
        f"only {len(server.CENSUS_SURFACES)} census surfaces found; this "
        "guard may be reading the wrong table."
    )
    assert server.CENSUS_SURFACE_COST, "the cost table is empty"
