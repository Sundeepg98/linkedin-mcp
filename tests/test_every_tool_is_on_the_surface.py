"""Every ``@mcp.tool()`` decorates the function it was written for.

THE DEFECT THIS FILE EXISTS FOR, measured 2026-09-03 on uncommitted work and
fixed the same hour. A helper was inserted BETWEEN an existing ``@mcp.tool()``
and the ``async def`` it decorated::

    @mcp.tool()
    async def _attach_recipient_ids(page, rows):   <- the new helper
        ...
    async def linkedin_who_viewed_me(limit=25):    <- the tool, now bare

``mcp.list_tools()`` then reported::

    linkedin_who_viewed_me registered: False
    _attach_recipient_ids  registered: True

A shipped READ tool -- the one the capability census calls the highest-signal
tool in the package -- stopped being callable, and a private helper whose
first parameter is a live Playwright page took its place on the tool surface.

## Why nothing already here saw it

**The file's SHAPE did not change.** The tool count stayed at 35. The
function is still defined, still has its docstring, still appears in every
grep. `tests/test_server_surface.py` is 107 KB of assertions about this
module and none of them failed, because a decorator moving between two
adjacent defs changes WHICH function is a tool without changing anything a
counter or a substring search can see.

So the check has to ask the registry for a NAME. That is the whole of this
file, and it is deliberately small: three questions that a large surface test
cannot ask by accident.

## Shown failing, and this says exactly how rather than more than it can

**THE DEFECTIVE REGISTRY WAS MEASURED, NOT IMAGINED.** The three lines quoted
above came off ``mcp.list_tools()`` on the real tree while the defect was
live, at commit ``c23a288`` -- the tool count 35, ``linkedin_who_viewed_me``
absent, ``_attach_recipient_ids`` present. That reading is recorded in
:data:`REGISTRY_WHILE_BROKEN` and
``test_both_rules_reject_the_registry_that_was_actually_measured`` runs both
rules over it, so each is shown REJECTING a real defect rather than only ever
being seen passing.

What is deliberately NOT claimed: these two test functions were written after
the fix and were never themselves red against the live module. Re-introducing
the defect to watch them go red would mean leaving a shipped tool
deregistered on a tree three other agents are running their own suites
against, and that is a worse trade than replaying the measurement. The rules
below and the rules in that control are the same two predicates, applied to
the same two names.
"""

from __future__ import annotations

import asyncio

import pytest

from linkedin_server import server as server_module


#: Tools this package ships that a caller reaches by NAME. Deliberately a
#: hand-written list rather than one derived from the module, because a
#: derived list would be computed the same way the bug was: from what the
#: decorator happened to land on. The point of naming them is that a name
#: cannot silently move.
#:
#: NOT EXHAUSTIVE, AND THAT IS STATED SO NOBODY TREATS IT AS A REGISTRY. It
#: is the read surface plus the two tools whose absence would be hardest to
#: notice. A tool missing from here is not asserted; a tool named here and
#: missing from the registry fails.
EXPECTED_TOOLS = (
    "linkedin_who_viewed_me",
    "linkedin_my_profile",
    "linkedin_job_detail",
    "linkedin_search_jobs",
    "linkedin_saved_jobs",
    "linkedin_my_applications",
    "linkedin_draft_applications",
    "linkedin_notifications",
    "linkedin_followed_companies",
    "linkedin_surface_census",
    "linkedin_server_info",
    "linkedin_session_info",
    "linkedin_group_page",
    # 2026-10-10, lane B5: a READ, one page of a group's member list as people
    # records, banking census rows N 165 and N 177 in the same commit.
    "linkedin_group_members",
    "linkedin_company_page_counts",
    # 2026-09-23, lane L3: a READ on the jobs surface, banking census row
    # J 18 (recent searches, off the jobs home) in the same commit.
    "linkedin_recent_job_searches",
    # 2026-09-23, the live lane: a READ that presses, the share link of one of
    # his own posts; census M C72, proven live on his own post.
    "linkedin_own_item_link",
    # 2026-10-10, lane B4: a READ of an organisation People tab's insight
    # cards (census J 108), the first tool to open a roster address.
    "linkedin_company_people_insights",
    # 2026-11-26, lane readers-jobs26: a READ of one tab of a Page -- About,
    # Events or Insights (census J 106, J 113, J 165).
    "linkedin_company_page_tab",
    # 2026-11-26, lane readers-jobs26: a READ of his resumes and application
    # data page (census P M2).
    "linkedin_application_settings",
    # 2026-10-10, lane B1 (lb1-audience): a READ, his follower count and
    # demographics off one admitted page; census P L1, banked at merge.
    "linkedin_audience_analytics",
    # 2026-10-10, lane B1 (child lb1-followers), merged by lane build-p26 on
    # 2026-11-25: a READ of his own follower list, each follower a people
    # record beside its relation; census P L2b.
    "linkedin_my_followers_list",
    # 2026-11-26, lane readers-net26, each a READ of one admitted page built
    # on live session 11's capture of it: his invitation manager's two tabs
    # (census N 13, N 9), the people he follows (N 38), the members he
    # unfollowed (N 39) and his Advertising data page (P P15).
    "linkedin_received_invitations",
    "linkedin_sent_invitations",
    "linkedin_my_following_list",
    "linkedin_my_unfollowed_list",
    "linkedin_my_advertising_data",
)


def _tool_names() -> list[str]:
    return sorted(tool.name for tool in asyncio.run(server_module.mcp.list_tools()))


def test_there_are_tools_to_check():
    """A sweep over an empty registry passes forever.

    Named for this file's own subject: a check that cannot fail looks exactly
    like coverage.
    """
    names = _tool_names()
    assert len(names) > 25, names


@pytest.mark.parametrize("name", EXPECTED_TOOLS)
def test_every_read_tool_this_package_ships_is_registered(name):
    """A tool that is defined but not decorated is not a tool.

    It keeps its docstring, keeps its name, keeps every test written about
    the function -- and no caller can invoke it.
    """
    names = _tool_names()
    assert name in names, (
        "%s is not on the tool surface. It is almost certainly still DEFINED "
        "in server.py -- check whether its @mcp.tool() now sits above a "
        "different def, which is how this failed before. Registered: %r"
        % (name, names)
    )


def test_no_private_helper_is_a_tool():
    """A leading underscore says "not part of the surface". Believe it.

    This is the other half of the same defect and it is the more dangerous
    half: the helper that got the decorator takes a live Playwright ``page``
    as its first parameter, so the schema published to callers asked for one.
    """
    private = [name for name in _tool_names() if name.startswith("_")]
    assert private == [], (
        "these private helpers are published as tools: %r. A name beginning "
        "with an underscore is not part of the tool surface, and one that "
        "takes a page or a rows list cannot be called meaningfully by "
        "anybody." % private
    )


#: THE REGISTRY AS IT ACTUALLY STOOD WHILE THE DEFECT WAS LIVE, read off
#: ``mcp.list_tools()`` at commit ``c23a288``. Two entries differ from the
#: repaired surface and they are the whole of the defect: the tool is gone and
#: the helper is there. Kept as data so both rules can be shown rejecting a
#: real reading rather than an invented one.
REGISTRY_WHILE_BROKEN = ("_attach_recipient_ids", "linkedin_my_profile")


def test_both_rules_reject_the_registry_that_was_actually_measured():
    """THE CONTROL. Both rules, run over the measured defective registry.

    Without this the two tests above are assertions that have only ever been
    seen passing, which is the state this repository treats as uncertified.
    """
    broken = list(REGISTRY_WHILE_BROKEN)

    # RULE 1 -- the missing tool. This is the assertion
    # test_every_read_tool_this_package_ships_is_registered makes, and it
    # fails on this reading.
    assert "linkedin_who_viewed_me" not in broken
    assert "linkedin_who_viewed_me" in _tool_names()

    # RULE 2 -- the private helper on the surface. This is the assertion
    # test_no_private_helper_is_a_tool makes, and it fails on this reading.
    assert [name for name in broken if name.startswith("_")] == [
        "_attach_recipient_ids"
    ]
    assert [name for name in _tool_names() if name.startswith("_")] == []

    # AND THE COUNT DID NOT MOVE, which is the reason neither rule could be
    # replaced by a cheaper one. 35 tools before, 35 after.
    #
    # 36 FROM 2026-09-03: ``linkedin_connections``, a READ that ships
    # refusing because its side-effect cost is unmeasured. The count is
    # updated in the commit that adds the tool, which is the review moment
    # this assertion exists to create.
    #
    # 37 FROM 2026-09-05: ``linkedin_search_appearances``, a READ, and the
    # review moment this assertion creates was USED rather than waved
    # through. It was going to ship as an unwired reader with no tool at all,
    # on the argument that a docstring should not describe a page its author
    # has not opened. ``test_reader_reachability`` refused that, and it was
    # right: its allowlist is EMPTY, no reader in this package has ever been
    # exempted, and "not wired yet" would have been filed as "by design".
    # The honest fix was to register the tool and put the ignorance in the
    # docstring, where a caller reads it.
    # 38 FROM 2026-09-05: ``linkedin_events_home``, a READ. **THE PIN MOVED
    # BECAUSE THE SURFACE MOVED, AND HERE IS THE TOOL THAT MOVED IT** -- that
    # ordering is the whole difference between recording a fact and faking
    # one, and a count pin is the class this repository is most careful about
    # precisely because bumping a number is the cheapest way to clear a test.
    #
    # IT DOES NOT WEAKEN THE CONTROL ABOVE. Both rules are run over
    # REGISTRY_WHILE_BROKEN, a two-entry reading compared BY CONTENT, so
    # nothing in the demonstration reads this number. What the number is for
    # is the sentence above it -- the defect did not move the count, which is
    # why neither rule could be replaced by a cheaper one -- and the review
    # moment that a bump forces on whoever adds a tool.
    #
    # THE REVIEW MOMENT WAS USED. The reader behind this tool answers ZERO,
    # and zero is the one number a read can get wrong in a way that looks like
    # success, so it is returned as an integer only when four independent
    # facts hold: the section present, no rows, a body holding neither text
    # nor elements, and a non-empty sibling. See ``linkedin_server/events.py``.
    #
    # 41 FROM 2026-09-05 EVENING: THREE AT ONCE, AND ALL THREE ARE READS.
    # **THE PIN MOVED BECAUSE THE SURFACE MOVED, AND HERE ARE THE TOOLS THAT
    # MOVED IT:**
    #
    #     linkedin_premium_status             premium.read_premium_surface
    #     linkedin_newsletter_subscriptions   newsletters.read_newsletter_subscriptions
    #     linkedin_notify_cost_precondition   notify_cost.read_notifications_badge
    #
    # MEASURED, NOT COUNTED BY HAND: 38 before the edit and 41 after, both off
    # ``mcp.list_tools()`` on this tree, and each new name present in the
    # sorted registry. The three readers were BUILT EARLIER THE SAME DAY and
    # NONE could be called -- they sat in
    # ``tests/test_readers_outside_dom_are_a_pinned_inventory.py`` as a pinned
    # inventory of exactly that state, and their three lines are deleted in
    # the same commit as this bump. That file's list is now EMPTY, which is
    # the end state its own docstring said could not be committed that day.
    #
    # THE REVIEW MOMENT THIS ASSERTION EXISTS TO CREATE WAS USED, per tool,
    # and the answers differ:
    #
    #   * premium publishes NO boolean and NO single number, because three
    #     states were named about Premium and one load of /premium/my-premium/
    #     refutes at most one of them. Every branch carries ``settles`` and
    #     ``leaves_open`` so a caller cannot read "entitled" and quietly
    #     assume a job-posting panel renders;
    #   * newsletters REFUSES rather than answering when the pending-invitation
    #     badge cannot be read either side of the load, or when it moved --
    #     the obligation that address inherits from /mynetwork/, discharged in
    #     the tool because the reader states it and does not do it;
    #   * notify_cost ships a PRECONDITION and spends nothing. It loads the
    #     feed and reads a nav badge; it never opens /notifications/, and
    #     ``notify_cost.cost_delta`` is deliberately left with no caller,
    #     because wiring the AFTER half is what would consume the operator's
    #     unread state.
    #
    # IT STILL DOES NOT WEAKEN THE CONTROL ABOVE, for the reason already
    # written: both rules run over REGISTRY_WHILE_BROKEN, a two-entry reading
    # compared BY CONTENT, and nothing in that demonstration reads this
    # number. That was re-checked after this bump rather than assumed --
    # ``test_both_rules_reject_the_registry_that_was_actually_measured`` was
    # run against a deliberately wrong pin and against the real one, and it
    # is the count assertion alone that moves.
    #
    # 42 FROM 2026-09-05, ~22:15 BY THE BOX: linkedin_group_memberships,
    # a READ, wiring linkedin_server/groups_page.read_group_memberships.
    # MEASURED off ``mcp.list_tools()``: 41 before the edit and 42 after.
    #
    # THE REVIEW MOMENT, USED. A predecessor wave DECLINED to wire
    # ``groups.py`` on the reasoning that *a groups tool cannot certify
    # its own cost from the page it loads* -- which is true and one step
    # short. ``linkedin_notify_cost_precondition``, wired in the bump
    # above, reads a badge on /feed/ to say something about
    # /notifications/: bracketing a load with a reading taken ELSEWHERE
    # is this package's pattern, not a workaround. So this tool loads the
    # feed, the groups page, and the feed again, and reports the cost as
    # DEGENERATE -- an honest 'I cannot measure this' rather than a zero.
    #
    # AND IT ADDS NOTHING TO ``dom.py``. Not one line. The walk this
    # reader needed was written as a ``page.evaluate`` in a probe, which
    # would have forced it into the one module ``_composer_audience_is_
    # readable`` feature-detects on; it was re-expressed with locators
    # instead and reproduced the validated split on its first live run.
    #
    # 44 FROM 2026-09-19: TWO AT ONCE, BOTH READS, AND THIS PIN WAS NOT THE
    # LAST SITE TO MOVE -- IT IS THE ONE THAT GOT MISSED.
    #
    #     linkedin_job_collections     b64580a, 11:13
    #     linkedin_creator_analytics   a8a7556, 12:42
    #
    # MEASURED OFF THE REGISTRY, NOT THE SOURCE, and not relayed from the
    # commit that moved the other sites: ``len(_tool_names())`` reads 44 on
    # this tree and both names are in it. An AST count of the ``@mcp.tool()``
    # decorator returned 46 on this same tree the same afternoon and was wrong,
    # which is why the registry is the instrument and the decorator is not.
    #
    # ``a4565cb`` moved four sites -- ``EXPECTED_TOOLS``, the count assertion
    # in ``test_server_surface.py``, the read split, and that test's own name
    # -- under a message reading "the pin was the LAST site to move". It was
    # not. This fifth site sat at forty-two, and the file left stale was the
    # one whose own comments say a bump is the cheapest way to clear a test.
    # **A COUNT PINNED IN TWO FILES IS TWO PINS**, and a rename sweep that
    # greps for the number it is moving finds the sites spelled in digits and
    # misses none; a sweep that greps for the test NAME finds only its own
    # file. The second is what happened.
    #
    # IT STILL DOES NOT WEAKEN THE CONTROL ABOVE, and that was re-measured
    # rather than assumed: with the pin standing at 42 against a real 44, this
    # test failed HERE and nowhere else -- both rule assertions ran green over
    # ``REGISTRY_WHILE_BROKEN`` first. The demonstration compares a two-entry
    # reading BY CONTENT and reads no count, so the number moving cannot reach
    # it.
    #
    # 45 FROM 2026-09-20: linkedin_page_plugin_snippet, a READ that opens
    # no page at all. This pin and the three sites in
    # test_server_surface.py -- EXPECTED_TOOLS, the count, the read split
    # -- plus that test's own name and the forcing-function pin were all
    # moved in the SAME edit as the tool, which is what the paragraph
    # above asks for and what a4565cb did not do. FIVE sites, measured
    # off the registry rather than relayed from a commit message.
    # FORTY-SEVEN FROM 2026-09-20: linkedin_people_search_shape, a READ on the
    # people-search surface, admitted together with its shaper.
    # FORTY-EIGHT AND FORTY-NINE FROM 2026-09-21: linkedin_group_page and
    # linkedin_company_page_counts, both READS, each opening an admitted
    # address that no registered tool could navigate to.
    # FIFTY FROM 2026-09-23 (lane L3): linkedin_recent_job_searches, a READ,
    # banking census row J 18 as COVERED-UNFIRED in the same commit. It opens
    # an address the boundary already admitted. (A fifty-first,
    # linkedin_tracked_job_proximity, was built the same day and WITHDRAWN
    # before merge: its join navigated to ids read off the tracker page.)
    # FIFTY-ONE FROM THE SAME DAY, at the merge of lane L4:
    # linkedin_follow_company_page, a WRITE (census row N 47), built on the
    # lane branch as its own fiftieth and moved with every other count site
    # in the merge commit.
    # FIFTY-TWO AT THE LIVE LANE'S MERGE, 2026-09-24: linkedin_own_item_link --
    # the share link of one of his own posts through the post's own "Copy link
    # to post", on the orchestrator-delegated call recorded in its docstring. A
    # READ by effect that PRESSES two controls; built on the lane branch as its
    # own fiftieth and moved with every other site in the merge commit.
    # FIFTY-THREE AT LANE L7'S MERGE, the same day:
    # linkedin_mark_company_interest, a WRITE (census row P I14), built on that
    # lane's branch as its own fifty-second, measured off the merged registry
    # and moved with every other count site.
    # FIFTY-SIX AT LANE L5'S MERGE OF MASTER 66aaa95, the same day: two
    # READS (linkedin_list_conversations, linkedin_open_thread) and a WRITE
    # (linkedin_send_reply) on top of lane L7's fifty-three -- fifty-five on
    # the lane's branch, which had counted from the live lane's fifty-two --
    # measured off the merged registry and moved with every other count site.
    # FIFTY-SEVEN AT LANE L8'S MERGE OF MASTER 2eb90ad, 2026-09-27: one WRITE,
    # linkedin_withdraw_from_group (census rows M C63 / N 64), on top of
    # master's fifty-six, measured off the merged registry and moved with
    # every other count site in the merge commit.
    # FIFTY-NINE AT LANE L5'S MERGE OF MASTER 52b55b6, the same day: two
    # WRITES from its follow-up branch, linkedin_connect_from_profile and
    # linkedin_message_from_profile (census N 4 by D6, N 2, and M M1; fifty-
    # eight on that branch), on top of master's fifty-seven -- measured off the
    # merged registry, not summed, and moved with every other count site in
    # the merge commit.
    # FIFTY-EIGHT ON LANE L5'S ORDER OF 2026-09-27 23:36: linkedin_send_message
    # RETIRED -- aimed by a name -- measured off the registry and moved with
    # every other count site in the same commit.
    # SIXTY AT LANE S'S MERGE OF MASTER 0867bda, 2026-09-28: two READS from its
    # branch (sixty-one there), linkedin_recruiter_insights (census N 195) and
    # linkedin_messaging_presence (census M M53), on top of master's
    # fifty-eight -- measured off the merged registry, not summed.
    # SIXTY-ONE ON LANE L5'S ORDER OF 2026-09-28 08:06: one READ,
    # linkedin_read_named_profile (ruling NAMED-PROFILE-READ-BEHIND-A-GRANT;
    # census N 178 stays GAP on its capture), measured off the registry and
    # moved with every other count site in the same commit.
    # SIXTY-FOUR AT LANE B2'S MERGE OF ITS SEARCH VERTICALS, 2026-10-10: two
    # READS, linkedin_search_groups (census N 161) and linkedin_search_events
    # (census N 179), beside lane U's one write below; measured off the
    # merged registry, never summed.
    # SIXTY-TWO ON LANE A, 2026-10-10: one READ, linkedin_tracker_stage (the
    # tracker's interview, archived and clicked_apply stages; census J 50,
    # J 51, J 52), measured off the registry and moved with every other count
    # site in the same commit.
    # SIXTY-TWO ON LANE U'S BRANCH, 2026-10-10: one WRITE,
    # linkedin_send_attachment (ruling FILE-UPLOAD-OPENED; census M M14, M15,
    # M18 stayed GAP on two captures, then moved to COVERED-UNFIRED the same
    # day on the session-8 capture), measured off the branch's registry and
    # moved with every other count site in the same commit.
    # SIXTY-THREE ON 2026-10-10 (lane S, settings, merged after lane U's): one WRITE,
    # linkedin_set_admitted_setting (HIS-OWN-SETTINGS-NOT-OUTWARD; census
    # P O17, split from P O6-O20, GAP -> COVERED-UNFIRED), measured off the
    # registry and moved with every other count site in the same commit.
    # SIXTY-THREE AT LANE B5'S MERGE OF MASTER 0103810, 2026-10-10: one READ,
    # linkedin_group_members -- one page of a group's member list as people
    # records (census N 165 and N 177, GAP -> COVERED-UNFIRED on the lane's
    # branch, where it was the sixty-second) -- on top of master's sixty-two,
    # measured off the merged registry, not summed.
    # SIXTY-FOUR AT THE INTEGRATION MERGE OF LANE B5 ONTO MASTER a457819,
    # 2026-10-10: lane S's write and lane B5's read, both counted from
    # sixty-two, are two tools -- measured off the merged registry, not summed.
    # SIXTY-THREE AT LANE NP'S MERGE OF MASTER 0103810, 2026-10-10: one WRITE,
    # linkedin_withdraw_reaction (the orchestrator's ruling of 14:14), counted
    # the sixty-second on lane NP's branch before lane U's tool arrived beside
    # it; measured off the merged registry.
    # SIXTY-FIVE AT THE INTEGRATION MERGE OF LANE NP ONTO LANES S AND B5 (2026-10-10): lane NP's write
    # beside lanes S's and B5's, measured off the merged registry, not summed.
    # SIXTY-SEVEN AT THE INTEGRATION MERGE OF LANE B2 ONTO LANE NP (2026-10-10): lane B2's two
    # reads beside the sixty-five, measured off the merged registry, not summed.
    # SIXTY-THREE AT LANE B3'S MERGE OF MASTER 0103810, 2026-10-10: one READ,
    # linkedin_read_item_text (ruling THIRD-PARTY-TEXT-AT-RUNTIME; census M C43
    # COVERED-UNFIRED), on top of master's sixty-two -- measured off the merged
    # registry, not summed, and moved with every other count site.
    # SIXTY-THREE ON LANE B3'S CHILD BRANCH, 2026-10-10: two READS,
    # linkedin_my_articles (census M C48) and linkedin_item_viewer_demographics
    # (census M C38), measured off the registry and moved with every other
    # count site in the same commit. The rows are banked by the lane's lead.
    # SIXTY-FIVE AT LANE B3'S MERGE OF ITS CHILD, 2026-10-10: the child's two
    # READS on top of the lead's sixty-three -- measured off the merged
    # registry, not summed, and moved with every other count site.
    # SEVENTY AT THE INTEGRATION MERGE OF LANE B3 ONTO LANE B2 (2026-10-10): lane B3's three
    # reads beside the sixty-seven, measured off the merged registry, not summed.
    # SIXTY-FIVE AT LANE B4'S MERGE OF MASTER a457819, 2026-10-10: lane S's
    # one write and lane B4's two on master's sixty-two -- measured off the
    # merged registry, not summed, and moved with every other count site.
    # SEVENTY-TWO AT THE INTEGRATION MERGE OF LANE B4 ONTO LANE B3 (2026-10-10): lane B4's two
    # writes beside the seventy, measured off the merged registry, not summed.
    # SIXTY-TWO ON LANE B4'S BRANCH, 2026-10-10 (child b4-j110): one READ,
    # linkedin_company_page_home (census J 110, ruling
    # THIRD-PARTY-TEXT-AT-RUNTIME), measured off the registry and moved with
    # every other count site in the same commit. That lane's branch held the
    # tool as its own sixty-second; it merged here as the seventy-third.
    # SEVENTY-THREE AT THIS INTEGRATION MERGE, 2026-10-26: lane B4's
    # linkedin_company_page_home (census J 110) beside the seventy-two,
    # measured off the merged registry, not summed.
    # SIXTY-TWO ON LANE B4'S BRANCH, 2026-10-10 (J 108): one READ,
    # linkedin_company_people_insights (census J 108), measured off the
    # registry and moved with every other count site in the same commit.
    # SEVENTY-FOUR AT THE J 108 MERGE, 2026-10-26: lane B4's
    # linkedin_company_people_insights (census J 108) beside the seventy-three,
    # measured off the merged registry, not summed.
    # SIXTY-THREE AT LANE A'S MERGE OF MASTER 6c65815, 2026-10-10: the two
    # sixty-seconds above, measured off the merged registry.
    # SEVENTY-FIVE AT INTEGRATION 2'S MERGE OF LANE A, 2026-11-24: lane A's
    # linkedin_tracker_stage beside the seventy-four, measured off the merged
    # registry, not summed.
    # SIXTY-THREE AT LANE B1'S MERGE OF ITS CHILD lb1-dashboard, 2026-10-10:
    # one READ, linkedin_analytics_hub (census P L8), measured off the merged
    # registry and moved with every other count site in the same commit.
    # SIXTY-FOUR AT LANE B1'S MERGE OF ITS CHILD lb1-audience, 2026-10-10: one
    # READ, linkedin_audience_analytics (census P L1), measured off the merged
    # registry and moved with every other count site in the same commit.
    # SEVENTY-SEVEN AT INTEGRATION 2'S MERGE OF LANE B1, 2026-11-24: lane B1's
    # linkedin_analytics_hub and linkedin_audience_analytics, two READS, beside
    # the seventy-five, measured off the merged registry, not summed.
    # SEVENTY-THREE AT LANE BUILDS-26 (2026-11-24): linkedin_set_tracker_stage,
    # a write-shaped tool that refuses -- measured off the registry.
    # SEVENTY-FIVE at its second commit: the endorsement pair, refusing.
    # EIGHTY AT INTEGRATION 2'S MERGE OF LANE BUILDS-26, 2026-11-25: its three
    # write-shaped tools beside the seventy-seven, measured off the merged
    # registry, not summed.
    # SIXTY-TWO ON LANE B1'S CHILD BRANCH lb1-followers, 2026-10-10: one READ,
    # linkedin_my_followers_list (census P L2b), measured off that branch's
    # registry.
    # EIGHTY-ONE AT LANE BUILD-P26'S MERGE OF THAT BRANCH, 2026-11-25: the
    # follower list beside the eighty, measured off the merged registry, not
    # summed.
    # EIGHTY-TWO AT LANE BUILD-JMN26 (2026-11-25): the search-alert pair, two
    # writes, measured off this branch's registry.
    # EIGHTY-THREE AT INTEGRATION 3'S MERGE OF LANE BUILD-JMN26, 2026-11-26: the
    # search-alert pair beside the eighty-one, measured off the merged registry,
    # not summed.
    # EIGHTY-FOUR ON LANE READERS-JOBS26 (2026-11-26): one tab of a Page, a
    # read, measured off this branch's registry.
    # EIGHTY-FIVE ON THE SAME LANE: his application settings page, a read.
    # NINETY AT INTEGRATION 4'S MERGE OF LANE READERS-NET26 (2026-11-26): its
    # five READS beside the eighty-five (its branch read eighty-eight), measured
    # off the merged registry, not summed.
    # NINETY-ONE AT INTEGRATION 4'S MERGE OF LANE READERS-MSG26 (2026-11-26):
    # linkedin_search_content, one read, beside the ninety (its branch read
    # eighty-four), measured off the merged registry, not summed.
    # NINETY-TWO ON LANE BUILD-JOBS2 (2026-11-26): linkedin_set_recent_job_searches_cleared,
    # a write-shaped tool that refuses (census J 19), measured off the registry.
    # NINETY-THREE ON THE SAME LANE: linkedin_send_recommendations_feedback, a
    # receipt-only write (census J 163), measured off the registry.
    # NINETY-FOUR ON THE SAME LANE: linkedin_job_alerts, a read (census J 37).
    assert len(_tool_names()) == 94
