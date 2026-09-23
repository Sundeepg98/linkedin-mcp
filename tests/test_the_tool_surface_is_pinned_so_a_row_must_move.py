"""The tool surface is PINNED, so shipping a capability forces a census decision.

THE THIRD GUARD IN A FAMILY OF THREE, and the one the other two say is missing.

    test_a_retired_row_rests_on_a_live_assertion.py   EXCLUDED-RULED row -> its rule
    test_a_covered_row_names_the_artifact_that_covers_it.py   COVERED row -> its code
    THIS FILE                                          shipped capability -> a decision

That second file states the gap in its own words: banking the unbanked rows
*"fixes the count once. It does not stop the reverse defect."* This is the
other direction -- a row left at GAP while the code that serves it ships.

## THE DEFECT, MEASURED ELEVEN TIMES

A row leaves GAP only when somebody EDITS THE CENSUS. Shipping a tool does not
move it. So the census over-reports GAP and a wave gets briefed to BUILD
something that shipped a fortnight ago:

    J 9, J 11, J 12, J 13, J 14   shipped 2026-09-04, filed GAP until 09-19
    M C60, N 173                  tool shipped and fired live, filed GAP
    N 165                         ruled out by name in readonly.py, filed GAP
    J 10, K10                     found independently by a sibling wave
    J 127                         GAP on a claim its own package refutes

**FIVE OF THOSE ELEVEN WERE PARAMETERS ON AN EXISTING TOOL**, not new tools --
`easy_apply`, `job_type`, `under_ten_applicants`, `in_your_network`,
`fair_chance_employer`, all added to `linkedin_search_jobs`. The tool COUNT
never moved. `test_every_tool_is_on_the_surface.py` pins which functions are
tools and would not have fired; nothing in this suite pinned the PARAMETER
surface at all. **That is the hole this file closes.**

=============================================================================
WHAT THIS GUARD DOES NOT DO, STATED FIRST BECAUSE IT IS THE HONEST PART
=============================================================================

**IT CANNOT CHECK THAT THE ROW WHICH MOVED IS THE ROW FOR THE CAPABILITY THAT
SHIPPED.** That correspondence is SEMANTIC, and this repository has the proof:
four separate designs tried to detect it and all four failed
(`scripts/unbanked_row_sweep.py`, committed as a failed instrument that
refuses to run). The closest design read 7 of 7 known answers and was still
wrong -- three of five matched a MESSAGING tool because the capability text
and the parameter shared the word "filter".

    A POSITIVE CONTROL THAT COUNTS HITS AND NOT THEIR CONTENT CAN BE
    SATISFIED ENTIRELY BY COINCIDENCE.

So a guard that fired green because *some* row moved would be exactly that
mistake wearing a guard's costume. **This file therefore makes no claim about
correspondence. It is a FORCING FUNCTION, not a detector**: it stops the tree
at the moment the surface changes and makes a human say what happened.

## WHY THERE IS NO BASELINE, AND WHY THAT IS NOT AN OVERSIGHT

The shipped ratchets baseline their known instances -- the tab-leak guard
carries 39. **A baseline would be wrong here, because this guard fires on a
CHANGE and not on a STATE.** The eleven instances above are already-shipped
code; they produce no future surface change, so they cannot trip it. Pinning
today's surface is the whole baseline, and it costs nothing to carry.

## HOW TO CLEAR IT WHEN IT FIRES

1. Update `PINNED_TOOL_SURFACE` below to the new surface, and
2. **In the SAME commit, either bank the census row the capability serves, or
   say in the commit message why no row moved.**

Step 2 is unverifiable by this file and is the point: the guard buys the
MOMENT, a human supplies the judgement. Reasons that have been correct before:
the parameter is plumbing with no capability behind it; the row is in another
slice and was reported rather than banked; the capability was already covered
by a row that moved earlier.
"""
from __future__ import annotations

import asyncio

import pytest

from linkedin_server import server as server_module

#: Tool -> its parameter names, from ``mcp.list_tools()`` on this tree.
#: NOT regexed out of the source: a decorator moving between two adjacent
#: defs changes WHICH function is a tool without changing anything a substring
#: search can see, which is the defect
#: ``test_every_tool_is_on_the_surface.py`` exists for. This reads the same
#: registry a client does.
PINNED_TOOL_SURFACE: dict[str, tuple[str, ...]] = {
    "linkedin_apply_job": ("confirm_token", "job_id"),
    "linkedin_auth_status": (),
    "linkedin_cdp_status": (),
    "linkedin_comment_on_item": ("confirm_token", "item", "text"),
    "linkedin_company_page_counts": ("organisation_id",),
    "linkedin_compose_fields": (),
    "linkedin_connections": ("limit",),
    "linkedin_creator_analytics": (),
    "linkedin_draft_applications": ("limit",),
    "linkedin_events_home": (),
    "linkedin_follow_company": ("confirm_token", "job_id"),
    "linkedin_follow_company_page": ("confirm_token", "organisation_id"),
    "linkedin_followed_companies": ("company", "limit"),
    "linkedin_group_memberships": (),
    "linkedin_group_page": ("group_id",),
    "linkedin_job_collections": (),
    "linkedin_job_detail": ("job_id",),
    "linkedin_login": ("wait_seconds",),
    "linkedin_login_browser": ("wait_seconds",),
    "linkedin_logout": ("confirm",),
    "linkedin_my_activity_items": (),
    "linkedin_my_applications": ("limit",),
    "linkedin_my_profile": ("details", "include_skills"),
    "linkedin_new_messages": (),
    "linkedin_newsletter_subscriptions": (),
    "linkedin_notifications": ("limit",),
    "linkedin_notify_cost_precondition": (),
    "linkedin_open_messaging": ("include_names", "message_filter"),
    "linkedin_page_plugin_snippet": ("page_id",),
    "linkedin_people_search_shape": (
        "connections_of", "current_company_ids", "keywords", "location_ids",
        "past_company_ids",
    ),
    "linkedin_premium_job_collection": ("collection",),
    "linkedin_premium_status": (),
    "linkedin_profile_editor_fields": (),
    "linkedin_profile_editor_values": (),
    "linkedin_publish_post": ("confirm_token", "text"),
    "linkedin_react_to_item": ("confirm_token", "item"),
    "linkedin_recent_job_searches": (),
    "linkedin_save_job": ("confirm_token", "job_id"),
    "linkedin_saved_jobs": ("limit",),
    "linkedin_search_appearances": (),
    "linkedin_search_jobs": (
        "company_id", "date_posted", "easy_apply", "experience_level",
        "fair_chance_employer", "in_your_network", "job_type", "keywords",
        "limit", "location", "locations", "remote", "sort_by", "start",
        "under_ten_applicants",
    ),
    "linkedin_send_invitation": ("confirm_token", "member"),
    "linkedin_send_message": ("confirm_token", "member", "text"),
    "linkedin_server_info": ("verbose",),
    "linkedin_session_info": ("verify_live",),
    "linkedin_surface_census": ("surface",),
    "linkedin_unfollow_company": ("company_id", "confirm_token"),
    "linkedin_unsave_job": ("confirm_token", "job_id"),
    "linkedin_update_profile_field": ("confirm_token", "field", "value"),
    "linkedin_update_setting": ("confirm_token", "setting", "value"),
    "linkedin_who_viewed_me": ("limit", "open_filter_menus"),
}

#: 44 tools and 61 parameters at the pin. Asserted rather than assumed, so a
#: pin edited to an empty dict cannot quietly disable the guard.
#:
#: **RE-PINNED 2026-09-19 at 43.** `linkedin_job_collections` shipped in
#: `b64580a`, and **the guard's substantive demand was already met in that
#: commit**: it moved `J 42` from GAP to COVERED-PROVEN in the same change,
#: verified here rather than taken on the commit subject's word. What was
#: missing was only this pin, which is the bookkeeping half.
#:
#: **THAT DISTINCTION IS WHY THE RE-PIN IS NOT A WAIVER.** The guard fires on
#: an unpinned surface whether or not a row moved, because it cannot check
#: WHICH row -- that correspondence is semantic and four designs failed to
#: detect it. So greening it always requires somebody to go and look. Here the
#: looking found a real, banked row. **A red guard left standing becomes
#: noise, and a guard everybody has learned to ignore is worse than none** --
#: which is the only reason this wave re-pinned a tool it did not ship.
#:
#: **RE-PINNED AGAIN AT 44 IN THE SAME SESSION**, this time for a tool
#: this wave DID ship: `linkedin_creator_analytics`, banking `M C40` in
#: the same commit -- which is the sequence this guard exists to force,
#: demonstrated by its author rather than only demanded of others.
#:
#: **RE-PINNED 2026-09-20 AT 44 TOOLS AND 62 PARAMETERS**, and this one is the
#: case the file's own header calls the hole it was dug for: a PARAMETER on an
#: existing tool, with the tool count not moving at all. `locations` shipped on
#: `linkedin_search_jobs` and banks census row `J 151` -- filter a job search by
#: MULTIPLE simultaneous locations -- in the same commit. The row is banked as
#: COVERED-UNFIRED rather than COVERED-PROVEN, because the fan-out is tested
#: offline and has not been run against live LinkedIn; that is a statement about
#: the evidence class, not a hedge about whether the capability exists.
#:
#: **RE-PINNED 2026-09-20 AT 45 TOOLS AND 63 PARAMETERS.**
#: `linkedin_page_plugin_snippet` ships and banks census row `N A6` --
#: build a Page follow widget for your own website -- in the same commit,
#: as COVERED-UNFIRED. The evidence class is the point: the generator is
#: complete and tested offline against the contract LinkedIn documents,
#: and it has produced no real snippet because the operator administers
#: no Page, so no Company ID exists to build one from. That is a
#: statement about what has been fired, not a hedge about whether the
#: capability exists.
#:
#: **AND IT IS THE ONLY ROW OF THAT BLOCKER'S FIFTEEN THIS COMMIT MOVES.**
#: The other fourteen need an address the navigation boundary refuses, a
#: write grant, or a second consenting human -- measured against the
#: shipped predicate rather than assumed; see
#: `_audit/2026-09-20-admin-rights-ready.md`.
#:
#: **RE-PINNED 2026-09-20 AT 47 TOOLS AND 64 PARAMETERS (UNCHANGED).**
#: `linkedin_people_search_shape` ships, takes NO parameters -- confirmed
#: against the live registry rather than assumed, which is why the
#: parameter count does not move even though the tool count does. It is
#: the S1 admission's other half: `readonly._ALLOWED_URL_PATTERNS` gained
#: `/search/results/people/?` in the same commit, and the ruling in
#: `_audit/2026-09-19-two-census-conventions-ruled.md` section 6 says
#: admitting the address without this shaper does not partially satisfy
#: that ruling, it violates it -- so the two pins move together.
#: **RE-PINNED 2026-09-21 AT 49 TOOLS AND 66 PARAMETERS**, and this is the
#: case the guard's own docstring asks for: the surface moved and census rows
#: move with it, in this commit. `linkedin_group_page("group_id")` and
#: `linkedin_company_page_counts("organisation_id")` each open an address that
#: has been on the read allowlist since 2026-09-19 and 2026-09-20 and that NO
#: tool in this package could navigate to, because every tool on those two
#: surfaces took no parameter at all -- which both allowlist entries state
#: about themselves.
#:
#: THE PARAMETER COUNT MOVES BY TWO AND BOTH ARE NUMERIC IDENTIFIERS. Neither
#: is a name, a url or a needle: each is refused unless it is a bounded run of
#: the ten ASCII digits, because a slug is a name. That is the same deliberate
#: exception `linkedin_job_detail("job_id")` and
#: `linkedin_page_plugin_snippet("page_id")` already carry -- a BUILDER has to
#: be handed the thing it builds from.
#:
#: THE ROWS: `N 175` for the group reader, `N 33` and `N 54` for the
#: organisation Page reader. All three move GAP -> COVERED-UNFIRED and NOT to
#: COVERED-PROVEN, because the wave that built them was forbidden the browser
#: and nothing has seen either tool return a payload live. See
#: `_audit/2026-09-21-the-three-readers.md`.
#:
#: **RE-PINNED 2026-09-23 AT 49 TOOLS AND 67 PARAMETERS.**
#: `linkedin_who_viewed_me("open_filter_menus")` -- the first package caller
#: of `press.disclose`: it opens each filter pill on his profile-views
#: analytics through the gate and reads what each disclosed, in the gate's
#: closed reading. **NO ROW MOVES IN THIS COMMIT, AND THAT IS STATED RATHER
#: THAN LEFT FOR THE GUARD TO INFER:** the rows it serves, `P O3` and `N 134`,
#: are decided by ONE live fire of this parameter, and they move -- or keep
#: their state with a named reason -- in the commit that records that fire.
#: See `_audit/2026-09-23-readers-four-rows.md`.
#: **RE-PINNED 2026-09-23 AT 50 TOOLS AND 67 PARAMETERS (lane L3), merged over the
#: readers wave's 49 and 67 just above: one tool added, no parameter, and the
#: surface change moves a census row in the same commit.**
#: `linkedin_recent_job_searches()` reads the jobs home and banks `J 18`.
#: **A SECOND TOOL WAS PINNED HERE AND WITHDRAWN BEFORE MERGE:**
#: `linkedin_tracked_job_proximity(stage, limit)` joined the tracker to the
#: posting's proximity read by navigating to job ids READ OFF THE TRACKER
#: PAGE -- a derived navigation `tests/test_navigation_is_never_derived.py`
#: forbids, and one its taint engine (a `goto` return and `.url` only) could
#: not see. `J 57` stays GAP.
#: **AND ONE MOVE THIS PIN CANNOT SEE, SAID HERE BECAUSE IT IS THE HOLE THIS
#: FILE WAS DUG FOR ONE LEVEL DOWN:** `linkedin_premium_job_collection` gained
#: a new VALUE, index 2 (`recommended`), on a parameter it already had, and it
#: banks `J 39`. No name and no parameter moved, so this guard is silent about
#: it by construction. Both rows move GAP -> COVERED-UNFIRED, not PROVEN: the
#: lane that built them was offline. See `_audit/2026-09-23-lane-l3-jobs.md`.
#: **RE-PINNED 2026-09-23 AT 51 TOOLS AND 69 PARAMETERS (lane L4), merged over
#: master's 50 and 67 just above: one tool added, two parameters, and the
#: census row moves in the same merge.** The lane's branch had pinned 50 and 68
#: over the base's 49 and 66.
#: `linkedin_follow_company_page("organisation_id", "confirm_token")` banks
#: `N 47` -- follow an organization's Page from the Page itself -- GAP ->
#: COVERED-UNFIRED. Not PROVEN: it is a WRITE, built to ready-to-fire behind
#: the flag and the single-use grant, and no grant was issued for it. Its two
#: parameters are the two every gated write takes -- a numeric identifier,
#: refused unless it is 4 to 20 ASCII digits, and the token. See
#: `_audit/2026-09-23-lane-l4-writes.md`.
#: **RE-PINNED 2026-09-24 AT 51 TOOLS AND 74 PARAMETERS (lane S, at its
#: merge with master d65759f): no tool added, five parameters on one, and the
#: census rows move in the same merge.** `linkedin_people_search_shape` --
#: which took NO parameters by design until D1-SEARCH-AS-READS and
#: OTHER-MEMBER-IDS-AS-READS decided a keyword and LinkedIn's own facets may
#: be passed from a tool's arguments -- gains `keywords`,
#: `current_company_ids`, `past_company_ids`, `location_ids` and
#: `connections_of`, all optional, composed by `people_search.compose` and
#: never echoed. FOUR ROWS MOVE GAP -> COVERED-UNFIRED, the filters: `N 84`,
#: `N 85`, `N 87`, `N 94`. THREE ROWS THE SAME PARAMETERS SERVE DO NOT MOVE,
#: and that is stated rather than left for this guard to infer: `N 79`,
#: `N 172` and `N 194` ask for WHO, and under the WHO rule (the orchestrator's
#: census call, 2026-09-24) a count-only reader does not deliver them; they
#: stay GAP on the name-free shaper doctrine, pending the operator. Not
#: PROVEN: the lane was offline. See `_audit/2026-09-24-lane-s-people-search.md`.
PINNED_TOOL_COUNT = 51
PINNED_PARAMETER_COUNT = 74


def live_surface() -> dict[str, tuple[str, ...]]:
    tools = asyncio.run(server_module.mcp.list_tools())
    return {
        tool.name: tuple(sorted((tool.parameters or {}).get("properties") or {}))
        for tool in tools
    }


def test_the_pin_itself_is_not_empty():
    """A guard whose pin can be emptied is a guard that can be switched off."""
    assert len(PINNED_TOOL_SURFACE) == PINNED_TOOL_COUNT
    assert sum(len(v) for v in PINNED_TOOL_SURFACE.values()) == (
        PINNED_PARAMETER_COUNT
    )


def test_no_tool_appeared_or_vanished_without_a_census_decision():
    live = live_surface()
    added = sorted(set(live) - set(PINNED_TOOL_SURFACE))
    gone = sorted(set(PINNED_TOOL_SURFACE) - set(live))
    assert not (added or gone), (
        f"THE TOOL SURFACE MOVED. added={added} removed={gone}. "
        "A capability shipped or left. Update PINNED_TOOL_SURFACE and, IN THE "
        "SAME COMMIT, bank the census row it serves or say why none moved. "
        "This guard cannot check WHICH row -- that correspondence is semantic "
        "and four designs failed to detect it. It buys the moment; you supply "
        "the judgement."
    )


@pytest.mark.parametrize("tool", sorted(PINNED_TOOL_SURFACE))
def test_no_tool_gained_or_lost_a_parameter_without_a_census_decision(tool):
    """FIVE OF THE ELEVEN KNOWN INSTANCES WERE THIS CASE, not a new tool."""
    live = live_surface()
    if tool not in live:
        pytest.skip("covered by the tool-set test")
    want = tuple(PINNED_TOOL_SURFACE[tool])
    got = live[tool]
    added = sorted(set(got) - set(want))
    gone = sorted(set(want) - set(got))
    assert got == want, (
        f"{tool} CHANGED ITS PARAMETERS. added={added} removed={gone}. "
        "The tool COUNT does not move for this, which is why the five filter "
        "parameters on linkedin_search_jobs sat unbanked for a fortnight. "
        "Update PINNED_TOOL_SURFACE and, IN THE SAME COMMIT, bank the census "
        "row this serves or say why none moved."
    )
