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
    "linkedin_analytics_hub": (),
    "linkedin_apply_job": ("confirm_token", "job_id"),
    "linkedin_audience_analytics": (),
    "linkedin_auth_status": (),
    "linkedin_cdp_status": (),
    "linkedin_comment_on_item": ("confirm_token", "item", "text"),
    "linkedin_company_page_counts": ("organisation_id",),
    "linkedin_company_page_home": ("organisation_id",),
    # 2026-10-10 (lane B4, census J 108): the People tab's insight cards.
    "linkedin_company_people_insights": ("organisation_id",),
    "linkedin_compose_fields": (),
    "linkedin_connect_from_profile": ("confirm_token", "profile"),
    "linkedin_connections": ("limit",),
    "linkedin_creator_analytics": (),
    "linkedin_draft_applications": ("limit",),
    "linkedin_tracker_stage": ("limit", "stage"),
    "linkedin_events_home": (),
    "linkedin_follow_company": ("confirm_token", "job_id"),
    "linkedin_follow_company_page": ("confirm_token", "organisation_id"),
    "linkedin_followed_companies": ("company", "limit"),
    "linkedin_group_members": ("group_id",),
    "linkedin_group_memberships": (),
    "linkedin_group_page": ("group_id",),
    "linkedin_job_collections": (),
    "linkedin_job_detail": ("job_id",),
    "linkedin_list_conversations": ("include_names",),
    "linkedin_login": ("wait_seconds",),
    "linkedin_login_browser": ("wait_seconds",),
    "linkedin_logout": ("confirm",),
    "linkedin_mark_company_interest": ("confirm_token", "job_id"),
    # Lane B4, 2026-10-10 (census J 161): the similar-jobs alert pair.
    "linkedin_set_similar_jobs_alert": ("confirm_token", "job_id"),
    "linkedin_unset_similar_jobs_alert": ("confirm_token", "job_id"),
    # Lane build-jmn26, 2026-11-25 (census J 31): the search-alert pair.
    "linkedin_set_search_job_alert": ("confirm_token", "keywords", "location"),
    "linkedin_unset_search_job_alert": ("confirm_token", "keywords", "location"),
    "linkedin_message_from_profile": ("confirm_token", "profile", "text"),
    "linkedin_my_activity_items": (),
    "linkedin_my_applications": ("limit",),
    "linkedin_my_articles": (),
    # 2026-10-10, lane B1 (child lb1-followers), merged by lane build-p26 on
    # 2026-11-25: his own follower list, each follower a people record
    # beside its relation. Census P L2b.
    "linkedin_my_followers_list": (),
    "linkedin_my_profile": ("details", "include_skills"),
    "linkedin_new_messages": (),
    "linkedin_newsletter_subscriptions": (),
    "linkedin_notifications": ("limit",),
    "linkedin_notify_cost_precondition": (),
    "linkedin_open_messaging": ("allow_unread", "include_names", "message_filter"),
    "linkedin_open_thread": ("allow_unread", "thread_id"),
    "linkedin_page_plugin_snippet": ("page_id",),
    "linkedin_item_viewer_demographics": ("item",),
    "linkedin_people_search_shape": (
        "connections_of", "current_company_ids", "include_names", "keywords",
        "location_ids", "network", "past_company_ids",
    ),
    "linkedin_premium_job_collection": ("collection",),
    "linkedin_premium_status": (),
    "linkedin_messaging_presence": (),
    "linkedin_profile_editor_fields": (),
    "linkedin_profile_editor_values": (),
    "linkedin_publish_post": ("confirm_token", "text"),
    "linkedin_react_to_item": ("confirm_token", "item"),
    "linkedin_read_item_text": ("item",),
    "linkedin_read_named_profile": ("confirm_token", "profile", "section"),
    "linkedin_withdraw_reaction": ("confirm_token", "item"),
    "linkedin_recent_job_searches": (),
    "linkedin_recruiter_insights": (),
    "linkedin_save_job": ("confirm_token", "job_id"),
    "linkedin_saved_jobs": ("limit",),
    "linkedin_search_appearances": (),
    # 2026-10-10, lane B2: census N 161 and N 179, REPORTED to the lane's lead
    # rather than banked -- the census is the lead's to move at merge.
    "linkedin_search_events": ("keywords",),
    "linkedin_search_groups": ("keywords",),
    "linkedin_search_jobs": (
        "company_id", "date_posted", "easy_apply", "experience_level",
        "fair_chance_employer", "in_your_network", "job_type", "keywords",
        "limit", "location", "locations", "remote", "sort_by", "start",
        "under_ten_applicants",
    ),
    # 2026-10-10, lane U: one file into one conversation he names.
    "linkedin_send_attachment": ("confirm_token", "file", "thread_id"),
    # ``member`` -> ``profile`` on 2026-09-27 (lane L5, the orchestrator's
    # order of 23:36): aimed by the person's profile link, never a name.
    # Census N 1 keeps its state; its note records the new aim.
    "linkedin_send_invitation": ("confirm_token", "profile"),
    # (``linkedin_send_message`` -- confirm_token, member, text -- was
    # RETIRED on 2026-09-27, lane L5, the orchestrator's order of 23:36:
    # aimed by a name. Census M M1, N 155 and M M2 moved; see the record.)
    "linkedin_send_reply": ("confirm_token", "text", "thread_id"),
    "linkedin_server_info": ("verbose",),
    "linkedin_session_info": ("verify_live",),
    # 2026-10-10, lane S (settings): ONE control on ONE admitted settings
    # page, behind the single-use grant. Census P O17 moves; see the pin note.
    "linkedin_set_admitted_setting": ("confirm_token", "control", "settings_page", "value"),
    # 2026-11-24, lane builds-26: SANCTIONED AND REFUSING -- the stage move on
    # a saved job. Census J 54 does NOT move: its control has never been
    # captured; the cell names that capture as its held-by.
    "linkedin_set_tracker_stage": ("confirm_token", "job_id", "stage"),
    # 2026-11-24, lane builds-26: the endorsement pair, SANCTIONED AND
    # REFUSING. Census P E4 / N 111 and P E5 / N 113 do NOT move: the
    # per-skill control has never been captured.
    "linkedin_endorse_skill": ("confirm_token", "profile", "skill"),
    "linkedin_withdraw_endorsement": ("confirm_token", "profile", "skill"),
    "linkedin_surface_census": ("item", "surface"),
    "linkedin_unfollow_company": ("company_id", "confirm_token"),
    "linkedin_unsave_job": ("confirm_token", "job_id"),
    "linkedin_update_profile_field": ("confirm_token", "field", "value"),
    "linkedin_update_setting": ("confirm_token", "setting", "value"),
    "linkedin_who_viewed_me": ("limit", "open_filter_menus", "show_more_analytics", "view_switch"),
    "linkedin_own_item_link": ("activity_id", "include_link"),
    "linkedin_withdraw_from_group": ("confirm_token", "group_id"),
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
#:
#: **RE-PINNED 2026-09-23 AT 49 TOOLS AND 69 PARAMETERS, by the live lane.**
#: `linkedin_who_viewed_me("view_switch", "show_more_analytics")` -- the view
#: switch (one ruled filter applied, read, and proven restored, on
#: VIEW-SWITCH-PRESS-RESTORED) and the one decided reveal ("Show more
#: analytics", on its orchestrator-delegated call). **NO ROW MOVES IN THIS
#: COMMIT:** `N 134` and `P O3` are decided by ONE live fire of these two
#: parameters and move, or keep their state with a named reason, in the commit
#: that records it. See `_audit/2026-09-23-live-lane-session-1.md`.
#:
#: **RE-PINNED 2026-09-23 AT 50 TOOLS AND 71 PARAMETERS, by the live lane.**
#: `linkedin_own_item_link("activity_id", "include_link")` -- the share link
#: of one of HIS OWN posts through the post's own "Copy link to post", on the
#: orchestrator-delegated call that `M C72`'s copy-link is proven on his own
#: posts only. The id is a NUMERIC IDENTIFIER, refused unless it is 1-20
#: ASCII digits, the exception `linkedin_group_page("group_id")` already
#: carries: a builder has to be handed the thing it builds from.
#: **NO ROW MOVES IN THIS COMMIT:** `M C72` moves, or keeps its state with a
#: named reason, in the commit recording one live fire of this tool.
#: (Both live-lane pins above were taken on the lane's branch, over the base's
#: 49 and 67; the merge below reconciles them with master's two.)
#:
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
#:
#: **RE-PINNED 2026-09-24 AT 52 TOOLS AND 73 PARAMETERS, at the live lane's
#: merge of master.** The lane's branch stood at 50 and 71 over the base's 49
#: and 67 (four parameters: `view_switch`, `show_more_analytics`,
#: `activity_id`, `include_link`; one tool); master stood at 51 and 69 over
#: the same base (two tools, two parameters). 49 + 1 + 2 = 52 and
#: 67 + 4 + 2 = 73, and both are measured off the merged registry by the
#: tests below rather than trusted from this sum. No row moves in the merge:
#: every row the lane's surface serves moved in the lane commit that fired it
#: (`N 134`, `P O3`, `M C72`), and master's rows in master's.
#:
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
#:
#: **RE-PINNED 2026-09-24 AT 52 TOOLS AND 78 PARAMETERS, at the live lane's
#: merge of lane S's master.** The two pins above were each taken on its own
#: branch: the live lane's 52 and 73, lane S's 51 and 74, over master's 51 and
#: 69. The merge carries both -- the live lane's one tool and four parameters,
#: lane S's five parameters -- so 52 tools and 69 + 4 + 5 = 78 parameters,
#: measured off the merged registry below. No row moves in the merge.
#: **RE-PINNED 2026-09-24 AT 53 TOOLS AND 80 PARAMETERS (lane L7,
#: at its merge of master 9b9a4d0), MEASURED off the merged registry, not
#: summed.** The lane's branch had pinned 52 and 76 at its first merge (master
#: ff98a7f); master had since pinned 52 and 78. The lane adds one tool and two
#: parameters: `linkedin_mark_company_interest("job_id", "confirm_token")`,
#: which banks `P I14` -- signal interest in working for a company -- GAP ->
#: COVERED-UNFIRED. Not PROVEN: a WRITE built to ready-to-fire behind the flag
#: and the single-use grant, never granted. See
#: `_audit/2026-09-24-lane-l7-profile-writes.md`.
#:
#: **RE-PINNED 2026-09-24 AT 51 TOOLS AND 70 PARAMETERS (lane G follow-up), on
#: its own branch over the base's 51 and 69.** `linkedin_surface_census`
#: gained `item`, and NO CENSUS ROW MOVES, which is this guard's question
#: answered out loud: it is not a new capability but the same measurement
#: re-aimed. The census's `feed_item` surface used to open an item the PAGE
#: chose -- the first on his rail, or, under the retired `feed_item_commented`
#: key, the one with the most anchors -- and the ruling
#: PAGE-MAY-VETO-NEVER-SUPPLY forbids that. So the caller names the item and
#: his own rail may only refuse it. See `_audit/2026-09-24-lane-g-guards.md`,
#: Follow-up.
#: **RE-PINNED 2026-09-24 AT 53 TOOLS AND 81 PARAMETERS, at lane G's merge of
#: master 66aaa95, MEASURED off the merged registry, not summed.** Master's 53
#: and 80 carry every pin above; the branch adds one parameter (`item`) and no
#: tool. No row moves in the merge.
#: **RE-PINNED 2026-09-24 AT 54 TOOLS AND 81 PARAMETERS (lane L5, at its
#: merge with master ff98a7f): three tools added, seven parameters, and the
#: census rows move in the same merge.** `linkedin_send_reply("thread_id",
#: "text", "confirm_token")` -- a reply inside a conversation he names,
#: the fourteenth performable write -- banks `M M10` and, by
#: D6-CAPABILITY-OVER-AFFORDANCE, `M M17`, both GAP -> COVERED-UNFIRED.
#: `linkedin_open_thread("thread_id", "allow_unread")` and the new
#: `allow_unread` on `linkedin_open_messaging` bank `M M49` (the read
#: indicator on his own last message) GAP -> COVERED-UNFIRED, and put the
#: receipt guard in front of `M M33`. `linkedin_list_conversations
#: ("include_names")` is the receipt-free list that `M M43` rests on --
#: ALREADY COVERED-UNFIRED, so it moves no row, and that is said here rather
#: than left for this guard to infer. Every thread id is a caller's argument,
#: shape-checked, never read off a page. Not PROVEN: the lane was offline.
#: See `_audit/2026-09-24-lane-l5-messaging.md`.
#: **AND 55 TOOLS AND 85 PARAMETERS AT LANE L5'S SECOND MERGE, of master
#: 9b9a4d0 (the live lane's), 2026-09-24:** the live lane's 52 and 78 plus
#: this lane's three tools and seven parameters, measured off the merged
#: registry below. No row moves in the merge itself.
#: **AND 56 TOOLS AND 87 PARAMETERS AT LANE L5'S THIRD MERGE, of master
#: 66aaa95 (lane L7's, and its CI fix), 2026-09-24:** lane L7's 53 and 80
#: plus this lane's
#: three tools and seven parameters, measured off the merged registry
#: below. No row moves in the merge itself.
#: **RE-PINNED 2026-09-27 AT 56 TOOLS AND 88 PARAMETERS, at lane G's merge of
#: master 2eb90ad, MEASURED off the merged registry, not summed.** Master's 56
#: and 87 carry every pin above; the branch adds one parameter (`item`) and no
#: tool. No row moves in the merge.
#: **RE-PINNED 2026-09-27 AT 57 TOOLS AND 89 PARAMETERS (lane L8, at its
#: merge of master 2eb90ad), MEASURED off the merged registry: one tool, two
#: parameters.** `linkedin_withdraw_from_group("group_id", "confirm_token")`
#: -- leaving one group he names by numeric id -- banks `M C63` and `N 64`
#: (one capability counted twice), GAP -> COVERED-UNFIRED, moved in the
#: lane's census commit on its branch, which this merge carries. Not PROVEN:
#: a WRITE built to ready-to-fire behind the flag and the single-use grant,
#: never granted. The id is a NUMERIC IDENTIFIER, refused unless it is 1 to
#: 20 ASCII digits -- the rule `linkedin_group_page("group_id")` already
#: carries, reused rather than restated.
#: See `_audit/2026-09-24-lane-l8-outward-classes.md`.
#: **RE-PINNED 2026-09-27 AT 57 TOOLS AND 90 PARAMETERS, at lane G's merge of
#: master 7986ae3 (lane L8's), MEASURED off the merged registry, not
#: summed.** Master's 57 and 89 carry every pin above; the branch adds one
#: parameter (`item`) and no tool. No row moves in the merge.
#: **RE-PINNED 2026-09-27 AT 59 TOOLS AND 95 PARAMETERS, at lane L5's merge of
#: master 52b55b6, MEASURED off the merged registry, not summed: two tools and
#: five parameters from lane L5's follow-up branch (58 and 92 there, over
#: master 96c1165), on top of master's 57 and 90.** The census rows moved in
#: the lane's own commits on its branch, which this merge carries, and one
#: more moves in the merge itself.
#: `linkedin_connect_from_profile("profile", "confirm_token")` banks `N 4`, by
#: D6-CAPABILITY-OVER-AFFORDANCE, GAP -> COVERED-UNFIRED -- and `N 2`, whose
#: only ground (R4) the ruling dissolved, NOT-REV -> COVERED-UNFIRED at this
#: merge, on the orchestrator's application of the same ruling;
#: `linkedin_message_from_profile("profile", "text", "confirm_token")` banks
#: `M M1`, COVERED-CANNOT-DELIVER -> COVERED-UNFIRED. Ruling
#: THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET. `profile` is a profile LINK or a
#: member id, parsed by shape and refused when it could be a name. Not PROVEN:
#: two WRITES built to ready-to-fire behind the flag and the single-use grant,
#: never granted. See `_audit/2026-09-24-lane-l5-messaging.md`, "Follow-up:
#: the named-person route" and "Integration: lane L5's merge of master
#: 52b55b6".
#: **RE-PINNED 2026-09-27 AT 57 TOOLS AND 91 PARAMETERS (lane S, names at
#: runtime): no tool added, one parameter on one, and three census rows move
#: in the same commit.** `linkedin_people_search_shape` gains
#: `include_names`, off by default: with it, the people the results page draws
#: come back as people records (`people_results.read_result_people`, under
#: NAMES-AT-RUNTIME and the six PEOPLE-DATA-MITIGATIONS). THE THREE WHO ROWS
#: THE 2026-09-24 ENTRY ABOVE LEFT GAP MOVE GAP -> COVERED-UNFIRED: `N 79`,
#: `N 172` and `N 194`, which asked for WHO and waited on a reader that
#: returns names. Not PROVEN: the lane was offline, and the reader was built
#: over the one captured results page. See
#: `_audit/2026-09-24-lane-s-people-search.md`, "Names returned".
#: **RE-PINNED 2026-09-27 AT 59 TOOLS AND 96 PARAMETERS, at lane S's merge of
#: master 687b07c, MEASURED off the merged registry, not summed.** Master's
#: 59 and 95 carry lane L5's two tools and every pin above; this branch
#: adds one parameter (`include_names`) and no tool. The census rows moved
#: in each side's own commits; none moves in the merge itself.
#: **RE-PINNED 2026-09-27 AT 58 TOOLS AND 92 PARAMETERS, on lane L5's order of
#: 23:36 (PEOPLE-DATA-MITIGATIONS, mitigation 6): `linkedin_send_message`
#: RETIRED -- it was aimed by a name -- taking one tool and three parameters
#: (`member`, `text`, `confirm_token`); `linkedin_send_invitation`'s `member`
#: became `profile`, which moves no count.** Census `M M1` and `N 155` note the
#: retirement; `M M2` returns to GAP (its only tool was the retired one). See
#: `_audit/2026-09-24-lane-l5-messaging.md`, "The name-aimed debts".
#: **AND AT 58 TOOLS AND 93 PARAMETERS AT LANE L5'S MERGE OF MASTER
#: 64afa6c, MEASURED off the merged registry, not summed**: master's 59 and
#: 96 carry lane S's `include_names`; this branch takes one tool and three
#: parameters (`linkedin_send_message`). No census row moves in the merge.
#: **RE-PINNED 2026-09-28 AT 61 TOOLS AND 96 PARAMETERS on lane S's branch (the
#: offline frontier): two tools, no parameter, and four census rows move in the
#: same commit.** `linkedin_recruiter_insights()` banks `N 195` and
#: `linkedin_messaging_presence()` banks `M M53`, each GAP -> COVERED-UNFIRED
#: over a capture's skeleton (people as records, under NAMES-AT-RUNTIME and
#: the six PEOPLE-DATA-MITIGATIONS). `P S5` moves on
#: `linkedin_search_appearances`' new `engagement` field and `J 107` on
#: `linkedin_search_jobs` taking `company_id` without a keyword -- neither a
#: surface change. Not PROVEN: nothing was fired live. See
#: `_audit/2026-09-24-lane-s-people-search.md`, "The offline frontier".
#: **AND AT 60 TOOLS AND 93 PARAMETERS AT LANE S'S MERGE OF MASTER 0867bda,
#: MEASURED off the merged registry, not summed**: master's 58 and 93 carry
#: lane L5's retirement; this branch adds two tools and no parameter. No
#: census row moves in the merge.
#: **RE-PINNED 2026-09-28 AT 61 TOOLS AND 95 PARAMETERS on lane L5's order of
#: 08:06 (ruling NAMED-PROFILE-READ-BEHIND-A-GRANT): one READ,
#: `linkedin_read_named_profile(profile, confirm_token)` -- the profile of a
#: member he names, loaded once behind the single-use grant, its name and
#: headline returned as a people record.** THE CENSUS DECISION: `N 178` (which
#: groups a member belongs to) STAYS GAP -- no capture shows a member's groups
#: on their profile, so the read returns them ABSENT and the row waits on the
#: capture spec C-P7; no other row moves. See
#: `_audit/2026-09-24-lane-l5-messaging.md`, "The read he names".
#: **RE-PINNED 2026-09-28 AT 61 TOOLS AND 96 PARAMETERS on the orchestrator's
#: order of 15:10 (lane S): no tool, one parameter -- `network` on
#: `linkedin_people_search_shape`, LinkedIn's degree facet as its own
#: shared-connections link writes it, sent only beside `connections_of`.**
#: THE CENSUS DECISION, in the same commit: `N 31` (the connections he shares
#: with a member) GAP -> COVERED-UNFIRED on it, and `N 30` (a connection's own
#: connections) GAP -> COVERED-UNFIRED by D6 on the orchestrator's ruling, on
#: `connections_of`, which shipped earlier. Never fired. See
#: `_audit/2026-09-24-lane-s-people-search.md`, "Four people-search items".
#: **RE-PINNED 2026-10-10 AT 61 TOOLS AND 97 PARAMETERS on lane NP (ruling
#: NAMED-PROFILE-DETAIL-PAGES): no tool, one parameter -- `section` on
#: `linkedin_read_named_profile`, ONE detail page of the same profile he names,
#: behind the same grant and warning.** THE CENSUS DECISION, in the same commit:
#: NO ROW MOVES. `N 178` and `N 65` stay GAP -- no capture of the Interests
#: detail page exists, so the load returns counts and no entry; the capture spec
#: and the reader design are in `_audit/2026-10-10-lane-np-named-profile.md`.
#: The read's two new fields (`member_token`, `activity_items`) are not
#: parameters; `N 30`, `N 85`, `N 172`, `N 31` and `M C32` move only when proven
#: live.
#: **RE-PINNED 2026-10-10 AT 62 TOOLS AND 99 PARAMETERS on lane NP (the
#: orchestrator's ruling of 14:14): one tool, two parameters --
#: `linkedin_withdraw_reaction(item, confirm_token)`, the reaction's inverse.**
#: THE CENSUS DECISION, in the same commit: NO ROW MOVES. `M C32` waits on its
#: live proof (react, then withdraw, on a post of the member he named); `M C35`
#: ("Remove or change a reaction") is compound and keeps its cell. Never fired.
#: **A ROW MOVED THE SAME DAY, ON THE ORCHESTRATOR'S CALL OF 15:45:** `M C35`
#: was split under COMPOUND-ROW-SPLITS-ONLY-ON-STATE -- `M C35` ("Remove a
#: reaction") COVERED-UNFIRED on this tool, `M C35b` ("Change a reaction to
#: another kind") GAP. The counts above did not move with it.
#: **RE-PINNED 2026-10-10 AT 62 TOOLS AND 98 PARAMETERS (lane A): one tool,
#: `linkedin_tracker_stage(stage, limit)`, a READ of the tracker's interview,
#: archived and clicked_apply stages.** THE CENSUS DECISION, in the same
#: commit: `J 50` and `J 51` GAP -> COVERED-UNFIRED (the tracker's own reader,
#: aimed at the tracked live captures of that page, never fired); `J 52`
#: stays GAP -- no capture draws a clicked_apply tab, so whether the stage
#: renders a list is the capture's to learn. See
#: `_audit/2026-09-28-lane-a-admissions.md`, section 4.2.
#: **MERGED AT LANE A'S MERGE OF MASTER f8c7392 (2026-10-10), MEASURED off the
#: merged registry, not summed:** lane NP's `section` and lane A's tool.
#: **RE-PINNED 2026-10-10 AT 62 TOOLS AND 99 PARAMETERS on lane U's branch
#: (ruling FILE-UPLOAD-OPENED): one WRITE,
#: `linkedin_send_attachment(thread_id, file, confirm_token)` -- one file from
#: the declared upload root into one conversation he names, behind the
#: single-use grant.** THE CENSUS DECISION, in the same commit: `M M14`,
#: `M M15` and `M M18` STAY GAP -- the file input is aimed on a real capture,
#: but no capture shows a composer holding an attachment or a sent
#: attachment message, so the read-back and the verification are aimed at
#: the file's name rather than at markup; each row waits on its capture
#: (U-REPLY-ATTACHMENT-SENT and -PENDING). No other row moves. See
#: `_audit/2026-09-28-lane-u-uploads.md`, section 5.
#: THE THREE ROWS MOVED LATER THE SAME DAY, with no change to the surface:
#: GAP -> COVERED-UNFIRED on the live lane's session-8 capture of the
#: composer's footer, each row aimed at its own input there; the read-back
#: and the verification stay aimed at the file's name, and refuse otherwise.
#: **RE-PINNED AT THE MERGE OF MASTER f8c7392 INTO LANE U, 2026-10-10: 62
#: TOOLS AND 100 PARAMETERS.** The two re-pins above meet here: lane NP's one
#: parameter (96 -> 97, no tool) and lane U's one tool with its three
#: parameters (61 -> 62 tools, 96 -> 99). Neither moved the other's entry, so
#: the sum holds: 61 + 1 tools, 96 + 1 + 3 parameters.
#: **RE-PINNED 2026-10-10 AT 62 TOOLS AND 100 PARAMETERS (lane S, settings,
#: HIS-OWN-SETTINGS-NOT-OUTWARD): one WRITE,
#: `linkedin_set_admitted_setting(settings_page, control, value, confirm_token)` -- ONE
#: control on ONE admitted settings page, by its exact label.** THE CENSUS
#: DECISION, in the same commit: `P O17` ("share profile updates with your
#: network") is SPLIT from `P O6-O20` under COMPOUND-ROW-SPLITS-ONLY-ON-STATE
#: and goes GAP -> COVERED-UNFIRED, its switch built on the real capture of
#: its page; the other fourteen toggles stay GAP on their pages' captures.
#: Never fired. See `_audit/2026-09-28-lane-s-settings.md`.
#: **AT LANE S'S MERGE OF MASTER 1027bf8 (2026-10-10): 62 TOOLS AND 101
#: PARAMETERS** -- master's 61 and 97 (lane NP's `section`) with lane S's one
#: tool and its four parameters, counted on the merged tree.
#: **AT LANE S'S MERGE OF MASTER 0103810 (2026-10-10): 63 TOOLS AND 104
#: PARAMETERS** -- master's 62 and 100 (lane U's tool and its three
#: parameters, on lane NP's 97) with lane S's one tool and its four,
#: counted on the merged tree.
#: **RE-PINNED 2026-10-10 AT 63 TOOLS AND 101 PARAMETERS on lane B5 (the groups
#: slice), at its merge of master 0103810: one tool, one parameter --
#: `linkedin_group_members("group_id")`, ONE page of a group's member list as
#: people records, on MEMBER-ROSTERS-AS-BOUNDED-READS, NAMES-AT-RUNTIME and the
#: six PEOPLE-DATA-MITIGATIONS.** THE CENSUS DECISION, in the lane's commit:
#: `N 165` and `N 177` move GAP -> COVERED-UNFIRED, over the live lane's
#: tracked skeleton of one member list; not PROVEN, nothing was fired. The id
#: is a NUMERIC IDENTIFIER, refused unless it is 1 to 20 ASCII digits -- the
#: rule `linkedin_group_page("group_id")` already carries, reused through
#: `member_rosters.compose`. `linkedin_group_page` gains a FIELD, `group_link`,
#: and no parameter; `N 197` moves on it by CALLER-COMPOSITION-UNDER-D6. The
#: lane's branch pinned 62 and 98 over the base's 61 and 97; master stood at 62
#: and 100; 62 + 1 and 100 + 1, measured off the merged registry. See
#: `_audit/2026-10-10-lane-b5-groups-build.md`.
#: **AT THE INTEGRATION MERGE OF LANE B5 ONTO MASTER a457819 (2026-10-10):
#: 64 TOOLS AND 105 PARAMETERS** -- lane S's tool and four parameters
#: and lane B5's tool and one parameter, both over 62 and 100, counted on
#: the merged registry, never summed.
#: **RE-PINNED AT LANE NP'S MERGE OF MASTER 0103810, 2026-10-10: 63 TOOLS
#: AND 102 PARAMETERS.** Lane NP's tool with its two parameters
#: (`linkedin_withdraw_reaction(item, confirm_token)`) meets lane U's with its
#: three: 61 + 1 + 1 tools, 97 + 3 + 2 parameters. Neither moved the other's
#: entry, and the census moves are each lane's own (`M C35` and `M C35b`;
#: `M M14`, `M M15`, `M M18`).
#: **AT THE INTEGRATION MERGE OF LANE NP ONTO LANES S AND B5 (2026-10-10): 65 TOOLS AND
#: 107 PARAMETERS** -- lane NP's tool and two parameters beside lanes S's
#: and B5's, counted on the merged registry, never summed.
#: **RE-PINNED 2026-10-10 AT 63 TOOLS AND 99 PARAMETERS for lane B2's search
#: verticals: two READS, `linkedin_search_groups(keywords)` and
#: `linkedin_search_events(keywords)` -- one search results page each,
#: composed from the keyword alone, its results returned as group and event
#: records.** THE CENSUS DECISION, stated in the commit: NO ROW MOVES ON THE
#: CHILD BRANCH THAT BUILT THEM. `N 161` and `N 179` are REPORTED to lane B2's
#: lead, whose census slice it is, to move GAP -> COVERED-UNFIRED at the
#: lane's merge on the evidence of that commit.
#: **RE-PINNED AT LANE B2'S MERGE OF ITS SEARCH VERTICALS OVER MASTER, 2026-10-10:
#: THE UNION, MEASURED BY THIS FILE'S OWN TEST.** Master's 62 tools and 100
#: parameters (lane NP's one parameter, lane U's one tool and three) and lane
#: B2's two read tools with one parameter each: 62 + 2 tools, 100 + 2
#: parameters. Neither side moved the other's entries.
#: **AT THE INTEGRATION MERGE OF LANE B2 ONTO LANE NP (2026-10-10): 67 TOOLS AND
#: 109 PARAMETERS** -- lane B2's two tools and their one parameter each
#: beside the sixty-five, counted on the merged registry, never summed.
#: **RE-PINNED AT LANE B3'S MERGE OF MASTER 0103810, 2026-10-10: 63 TOOLS
#: AND 101 PARAMETERS (ruling THIRD-PARTY-TEXT-AT-RUNTIME).** Lane B3's
#: branch had re-pinned 62 and 98: one READ, `linkedin_read_item_text(item)`,
#: ONE item's own words off its permalink inside one people_data.Post record.
#: THE CENSUS DECISION, in the commit that built it: `M C43` GAP ->
#: COVERED-UNFIRED on it, never fired. Neither side moved the other's
#: entry, so the sum holds: 62 + 1 tools, 100 + 1 parameters. See
#: `_audit/2026-10-10-lane-b3-messaging-build.md`.
#: **RE-PINNED 2026-10-10 AT 63 TOOLS AND 98 PARAMETERS on lane B3's child
#: branch: two READS, one parameter -- `linkedin_my_articles()` (census `M C48`)
#: and `linkedin_item_viewer_demographics(item)` (census `M C38`, the viewer-
#: demographics half), each over an address the read allowlist already admits,
#: each built and tested over a tracked skeleton of the session-1 capture.**
#: THE CENSUS DECISION: NO ROW MOVES IN THIS COMMIT. The child does not edit
#: census files; lane B3's LEAD banks both rows against these tools. Measured
#: off mcp.list_tools(), not summed.
#: **RE-PINNED AT LANE B3'S MERGE OF ITS CHILD, 2026-10-10: 65 TOOLS AND
#: 102 PARAMETERS.** The lead's 63 and 101 meet the child's two reads and
#: one parameter: 63 + 2 tools, 101 + 1 parameters. THE CENSUS DECISION, in
#: the lead's census commit: `M C48` and `M C38` GAP -> COVERED-UNFIRED on
#: them, never fired. See `_audit/2026-10-10-lane-b3-messaging-build.md`.
#: **AT THE INTEGRATION MERGE OF LANE B3 ONTO LANE B2 (2026-10-10): 70 TOOLS AND
#: 111 PARAMETERS** -- lane B3's three tools beside the sixty-seven,
#: counted on the merged registry, never summed.
#: **AT LANE B4'S MERGE OF MASTER a457819 (2026-10-10): 65 TOOLS AND 108
#: PARAMETERS** -- master's 63 and 104 with lane B4's two writes,
#: `linkedin_set_similar_jobs_alert` and `linkedin_unset_similar_jobs_alert`
#: (`job_id`, `confirm_token` each; census `J 161` GAP -> COVERED-UNFIRED),
#: counted on the merged tree.
#: **AT THE INTEGRATION MERGE OF LANE B4 ONTO LANE B3 (2026-10-10): 72 TOOLS AND
#: 115 PARAMETERS** -- lane B4's two tools and their two parameters each
#: beside the seventy, counted on the merged registry, never summed.
#: **RE-PINNED 2026-10-10 AT 62 TOOLS AND 98 PARAMETERS on lane B4's branch
#: (child b4-j110, ruling THIRD-PARTY-TEXT-AT-RUNTIME): one READ,
#: `linkedin_company_page_home(organisation_id)` -- an organisation Page's own
#: description off its Page root, returned as an untrusted-text record, and the
#: feed items the root drew as counts.** THE CENSUS DECISION: NO ROW MOVES IN
#: THIS COMMIT, because a child of lane B4 does not edit the census; `J 110` is
#: the lane lead's to move from the child's report, by its own cell's bar (the
#: reader is aimed at a 2026-09-23 capture of the Home view, and the same root
#: drew the Posts view on 2026-10-10 -- both are fixtures, see
#: `tests/test_company_home.py`).
#: **AT THIS INTEGRATION MERGE, 2026-10-26: 73 TOOLS AND 116 PARAMETERS** --
#: lane B4's one tool and its one parameter beside the seventy-two and 115,
#: counted on the merged registry, never summed.
#: **RE-PINNED 2026-10-10 AT 62 TOOLS AND 98 PARAMETERS on lane B4's branch
#: (census J 108): one READ, `linkedin_company_people_insights(organisation_id)`
#: -- an organisation People tab's insight cards as categories and counts, the
#: first tool to open a roster address (MEMBER-ROSTERS-AS-BOUNDED-READS).**
#: THE CENSUS DECISION is the lane lead's, reported rather than banked: the
#: child's report proposes `J 108` GAP -> COVERED-UNFIRED on code aimed at the
#: session-2 capture of a People tab; no census file moves in this commit.
#: **AT THE J 108 MERGE, 2026-10-26: 74 TOOLS AND 117 PARAMETERS** -- lane
#: B4's one tool and its one parameter beside the seventy-three and 116,
#: counted on the merged registry, never summed.
#: **MERGED AT LANE A'S MERGE OF MASTER 6c65815 (2026-10-10), MEASURED off the
#: merged registry, not summed: 63 TOOLS AND 102 PARAMETERS** -- lane A's
#: tracker stage (two) and lane U's attachment (three) over the base with
#: lane NP's section.
#: **AT INTEGRATION 2'S MERGE OF LANE A, 2026-11-24: 75 TOOLS AND 119
#: PARAMETERS** -- lane A's one tool and its two parameters
#: (`linkedin_tracker_stage(stage, limit)`) beside the seventy-four and 117,
#: counted on the merged registry, never summed.
#: **RE-PINNED AT LANE B1'S MERGE OF ITS CHILD lb1-dashboard, 2026-10-10: 63
#: TOOLS AND 100 PARAMETERS.** One READ with no parameter,
#: `linkedin_analytics_hub()`, his analytics hub `/dashboard/` loaded once.
#: THE CENSUS DECISION: the census row `P L8` moves GAP -> COVERED-UNFIRED in
#: lane B1's census commit (`_audit/2026-10-10-lane-b1-profile-build.md`).
#: **RE-PINNED AT LANE B1'S MERGE OF ITS CHILD lb1-audience, 2026-10-10: 64
#: TOOLS AND 100 PARAMETERS.** One READ with no parameter,
#: `linkedin_audience_analytics()`, his follower count and follower
#: demographics off one admitted page. THE CENSUS DECISION: the census row
#: `P L1` moves GAP -> COVERED-UNFIRED in lane B1's census commit.
#: **AT INTEGRATION 2'S MERGE OF LANE B1, 2026-11-24: 77 TOOLS AND 119
#: PARAMETERS** -- lane B1's two tools, `linkedin_analytics_hub()` and
#: `linkedin_audience_analytics()`, take no parameter, beside the seventy-five
#: and 119, counted on the merged registry, never summed.
#: **AT LANE BUILDS-26 (2026-11-24): 73 TOOLS AND 118 PARAMETERS** --
#: `linkedin_set_tracker_stage` (`job_id`, `stage`, `confirm_token`), a
#: sanctioned write that refuses; census `J 54` keeps its state (no capture of
#: the control). Counted off the registry, never summed.
#: **AND 75 TOOLS AND 124 PARAMETERS** at the lane's second commit: the
#: endorsement pair (`profile`, `skill`, `confirm_token` each), refusing.
#: **AT INTEGRATION 2'S MERGE OF LANE BUILDS-26, 2026-11-25: 80 TOOLS AND 128
#: PARAMETERS** -- that lane's three refusing writes and their nine parameters
#: (three each) beside the seventy-seven and 119, counted on the merged
#: registry, never summed.
#: **RE-PINNED 2026-10-10 AT 62 TOOLS AND 97 PARAMETERS on lane B1's branch
#: (child lb1-followers): one READ and no parameter --
#: `linkedin_my_followers_list()`, his own follower list loaded once at the
#: address `readonly.py` admits for census `P L2b`, read as counts and
#: relations only (how many of the rows he follows back) over the live lane's
#: session-2 skeleton.** THE CENSUS DECISION is the lane lead's: the census
#: row `P L2b` is banked by the lane B1 lead at merge, not in this commit. Never
#: fired live.
#: **AT LANE BUILD-P26'S MERGE OF THAT BRANCH, 2026-11-25: 81 TOOLS AND 128
#: PARAMETERS** -- `linkedin_my_followers_list()`, one READ and no
#: parameter, beside the eighty and 128, counted on the merged registry,
#: never summed. THE CENSUS DECISION, in lane build-p26's census commit:
#: `P L2b` GAP -> COVERED-UNFIRED (`_audit/2026-11-25-build-p26.md`).
#: **AT LANE BUILD-JMN26 (2026-11-25): 82 TOOLS AND 134 PARAMETERS** --
#: `linkedin_set_search_job_alert` and `linkedin_unset_search_job_alert`
#: (`keywords`, `location`, `confirm_token` each) beside the eighty and 128,
#: counted off `mcp.list_tools()`, never summed. THE CENSUS DECISION, IN THE
#: SAME COMMIT: `J 31` GAP -> COVERED-UNFIRED on them, never fired. See
#: `_audit/2026-11-25-build-jmn26.md`.
#: **AT INTEGRATION 3'S MERGE OF LANE BUILD-JMN26, 2026-11-26: 83 TOOLS AND 134
#: PARAMETERS** -- the search-alert pair (three parameters each) beside
#: build-p26's eighty-one tools and 128 parameters (its follower list takes
#: none), counted on the merged registry, never summed.
PINNED_TOOL_COUNT = 83
PINNED_PARAMETER_COUNT = 134


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
