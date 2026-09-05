"""The read-only invariant, written down as something that can fail.

"Read-only by design" is a claim. This module is the executable version of it,
in four parts:

1. **A navigation allowlist.** :func:`assert_read_url` is the only door to
   ``page.goto``. Every url this server may open is enumerated below as a
   pattern. A keyword the operator types cannot become a navigation to an
   action url, because the built url has to match one of these first.

   **THIS ALLOWLIST IS NAVIGATION-ONLY, AND THAT IS A SCOPE RATHER THAN AN
   OVERSIGHT.** Stated here explicitly on 2026-08-24 because the sentence
   above is exact and reads as broader than it is: "the only door to
   ``page.goto``" is a claim about NAVIGATIONS, and a request issued with
   ``page.request.get`` is not one. It never reaches this function.

   There is exactly one such request in the package -- ``auth.py`` asks
   ``config.ME_API`` whether the session is live, because a page load cannot
   answer that honestly -- and **it would be REFUSED by this allowlist if this
   allowlist were consulted**: ``is_read_url(ME_API)`` is ``False``. Nothing is
   wrong with the request. It is one hardcoded module constant, GET only, with
   no url a caller can influence. What was wrong until this paragraph existed
   is that a reader of this module had no way to know the path was there.

   It is covered instead by an ENUMERATION rather than by a pattern:
   ``tests/test_api_call_sites.py`` walks the package's syntax tree, pins the
   set of direct HTTP call sites to that one entry -- with its first argument
   pinned AS SOURCE TEXT -- and fails if a second appears or this one moves.
   ``linkedin_server_info`` reports it as ``direct_api_reads``.

   **Why the path was not simply added to the patterns below.** Doing that
   would move a frozen boundary structure and fire the AST invariant in
   ``tests/test_readonly_boundary_invariant.py``, in order to authorise a
   constant nobody can redirect -- buying a widened allowlist to solve a
   problem that is really a documentation gap. A boundary that states its own
   edge is worth more than one that implies a coverage it does not have.

2. **A source scanner.** :func:`scan_source_for_mutations` greps this package
   for the Playwright calls that could change something -- clicking, typing,
   submitting, non-GET requests. ``tests/test_readonly.py`` runs it over every
   module in the package AND over a deliberately bad sample, so the check is
   shown catching something rather than merely passing.

   Since 2026-08-23 the package contains exactly ONE mutating call, and the
   scanner still reports it. What changed is not the SCANNER but the POLICY
   applied to what it finds: :data:`SANCTIONED_MUTATIONS` enumerates, by
   ``(path, function, kind)``, the calls that are permitted, and
   :func:`partition_mutation_hits` splits a scan into the sanctioned and the
   rest. The measurement was deliberately left exact -- a scanner taught to
   stop seeing ``page.click`` is worth nothing, and the whole value of this
   one is that its finding is unconditional and its ALLOWLIST is the thing a
   reviewer reads.

3. **A verb list.** :data:`WRITE_VERBS` is what the tool-surface test uses to
   assert that no tool name or docstring implies a mutation.

4. **A launch boundary.** :func:`assert_launch_flags_permitted` and
   :func:`scan_source_for_evasion` hold the line on HOW the browser is
   started: two sanctioned Chromium flags, and no anti-detection library
   pulled in through the back door. ``browser.py`` runs the first of those
   before every launch, so it binds at runtime and not only in the tests.

WHAT THIS MODULE GUARANTEED UNTIL 2026-08-23, AND WHAT IT GUARANTEES NOW.
The old sentence was: *this server has no code path that clicks, types,
submits a form, or issues a non-GET request.* It was true, it was proven here
rather than asserted, and IT IS NO LONGER TRUE. Leaving it in place would have
made this module the first thing a reader trusts and the first thing that
lies to them.

What is true now, and is what the four parts above enforce:

* This server can open a fixed set of LinkedIn's own read pages in the
  operator's browser and read what rendered.
* It contains **exactly two** calls that can change anything on LinkedIn,
  both inside ``writes.perform`` and both named in
  :data:`SANCTIONED_MUTATIONS`: a ``click``, and -- from 2026-09-01 -- a
  ``fill``. Neither runs unless a per-process flag is set, a human has read a
  confirm gate built from a live read, and a single-use grant is redeemed
  against it. See ``writes.py``.
* **IT TYPES, AND THIS SENTENCE SAID IT DID NOT UNTIL 2026-09-01.** The old
  text read *"It still types nothing, submits no form, issues no non-GET
  request"*, and the first clause is now false. It is corrected rather than
  quietly dropped, because a reader who remembers the old guarantee needs to
  meet the change here rather than infer it from a list that grew.

  WHAT THE TYPING IS, exactly: ONE ``page.fill``, draining a queue at a single
  call site, whose text is a slice of the GRANT's canonical target -- the
  string the preview printed and the token was minted against. This server
  does not COMPOSE text; it types back what a caller supplied and a human
  approved verbatim. And a fill is not a send: the act that reaches LinkedIn
  is the click after it, gated on a measured transition.
* It still submits no form, issues no non-GET request, and reaches LinkedIn as
  the ordinary Chrome it is. Read that list as what it says: "no non-GET
  request" is not "no request outside the allowlist". One GET goes to
  ``ME_API`` without passing :func:`assert_read_url` -- see part 1 -- and
  enumerating what this server does not do, without naming the things it
  does, is how a true list misleads.

The list in :data:`SANCTIONED_MUTATIONS` is the whole of the difference, which
is why it is short and why widening it is a test failure rather than a
judgement call.
"""

from __future__ import annotations

import ast
import re
from typing import Iterable, Optional

from linkedin_server.errors import WriteAttemptError

# ---------------------------------------------------------------------------
# 1. Navigation allowlist
# ---------------------------------------------------------------------------

#: Every url this server is permitted to open, as an anchored pattern.
#: Query strings are allowed only where a read surface genuinely needs them
#: (job search filters, the saved/applied card type).
_ALLOWED_URL_PATTERNS: tuple[re.Pattern[str], ...] = (
    # HIS OWN MESSAGE SURFACE, added 2026-08-26 on the operator's ruling.
    #
    # Both forms are here deliberately. Asking for the first lands on the
    # second: LinkedIn redirects /messaging/ into one specific conversation
    # thread of its own choosing, measured twice. Listing only the first would
    # have meant the server routinely sitting on a url its own allowlist does
    # not cover -- true today because the landed url is not re-checked, and a
    # trap the moment anybody adds that check.
    #
    # SENDING IS STILL IMPOSSIBLE: /messaging/compose remains on the forbidden
    # substring list, which is checked BEFORE this one.
    # TIGHTENED 2026-09-03, ON THE WAVE LEAD'S RULING, AND MEASURED FIRST.
    #
    # THE DEFECT. `"/messaging/compose"` is on the forbidden tuple precisely so
    # that a composer cannot be addressed with a recipient, and
    # `/messaging/compose/?recipient=` duly refuses. THREE SIBLING SPELLINGS
    # REACHED THE SAME PLACE AND DID NOT:
    #
    #     /messaging/thread/new/?recipient=<id>
    #     /messaging/?composeTo=<id>
    #     /messaging/?recipient=<id>
    #
    # **A ruling that one spelling cannot express is not a ruling, it is a
    # spelling filter.** Neither mechanism was argued; both were inherited. The
    # root pattern admitted ANY query, which is over-broad whatever the query
    # says, and the thread-id class matched the literal `new` -- a keyword it
    # was never written for.
    #
    # THE ROOT TAKES NO QUERY. Measured from the code rather than from memory:
    # `config.MESSAGING_URL` is the only construction of this address and it is
    # navigated ONCE, at `server.py`'s messaging reader, with nothing appended.
    # The query group protected a landed-url re-check that does not exist -- and
    # the landed url, which LinkedIn redirects into a conversation, is covered
    # by the thread pattern below, which keeps its query.
    #
    # A THREAD ID STARTS WITH A DIGIT. That is a SHAPE, deliberately, rather
    # than a blocklist naming `new` -- a filter on one spelling is what got us
    # here. Every thread id recorded anywhere in this repository starts with a
    # digit: `2-abc`, `2-abcdef123456`, `2-NjY1ZDkwYWEt==`,
    # `2-QUJDREVGSElKS0xNTk9Q==`, `4600000042`. `new` is a word.
    #
    # MEASURED BEFORE APPLIED, WITH ZERO CASUALTIES, and that is a fact worth
    # stating rather than assuming: every shipped construction and every url
    # `tests/test_readonly.py` pins as ALLOWED still matches, and all three gap
    # spellings now refuse.
    re.compile(r"^https://www\.linkedin\.com/messaging/?$"),
    re.compile(
        r"^https://www\.linkedin\.com/messaging/thread/"
        r"[0-9][A-Za-z0-9%\-_=]*/?(\?[^#]*)?$"
    ),
    # Own profile views (Premium analytics view, and the classic one).
    re.compile(r"^https://www\.linkedin\.com/analytics/profile-views/?(\?[^#]*)?$"),
    re.compile(r"^https://www\.linkedin\.com/me/profile-views/?(\?[^#]*)?$"),
    # HIS OWN SEARCH APPEARANCES. Added 2026-09-05. The sibling of the two
    # lines above: same analytics tree, same account scope, and the same
    # class of instrument -- it reads the RECEIVING end of a signal other
    # people emit at him, which is what makes it his to read.
    #
    # IT CANNOT ADDRESS ANYBODY ELSE, AND THAT IS STRUCTURAL RATHER THAN
    # PROMISED. This address carries NO member segment of any kind. There is
    # no slug, no id, no ``/in/`` -- the account is chosen by the session
    # cookie and by nothing in the string. So the constraint the intro-editor
    # entry below has to buy with the ``/in/me/`` spelling is free here: the
    # generalisation that entry forbids -- a pattern that can name a member --
    # is not expressible at this address. The reason it forbids it holds all
    # the same and is why this is anchored at all: ``linkedin_who_viewed_me``
    # has MEASURED that loading a third party's page leaves them a durable
    # record, so no pattern on this list may be able to reach one.
    #
    # ANCHORED WITH NO QUERY GROUP, unlike the two profile-views lines above.
    # Those predate the discipline; this entry is written under it. ``dom``
    # builds this url from one module constant with nothing appended, so
    # there is no query to preserve, and a pattern that accepts one is a
    # pattern that accepts whatever a caller appends. The landed url is never
    # re-checked (see the messaging note above), so a redirect that adds
    # LinkedIn's own tracking parameters is not refused by this.
    #
    # WHAT IS DELIBERATELY NOT HERE, because the obvious later "fix" is to
    # reach for one of them:
    #
    # * ``/me/search-appearances/``. The profile-views pair lists both
    #   spellings, so the symmetric thing would be to list both here. NO
    #   MEASUREMENT SAYS LINKEDIN SERVES IT. The profile-views pair earned
    #   its second line by being opened; this would be a guess wearing a
    #   precedent's clothes, and an allowlist should permit what is opened
    #   rather than what is plausible. If the live read finds the analytics
    #   address does not serve, that is a second deliberate edit here.
    # * ``/analytics/`` and every other page under it. The tree root and
    #   ``/analytics/creator/`` were both measured REFUSED before this line
    #   was written and are both still refused after it. One named page at a
    #   time, never the family, never a wildcard -- the settings ruling's
    #   words, applied to the tree next door.
    #
    # AND IT IS NOT THE OTHER SEARCH SURFACE. ``/search/results/people/`` is
    # the act this reading exists to inform, it is NOT admitted by this line
    # (measured: still REFUSED-NO-PATTERN after the edit), and the gate in
    # ``_audit/2026-08-30-linkedin-nine.md`` forbids using one load of that
    # page as the evidence that authorises it. This entry buys the reciprocal
    # reading and nothing next to it.
    re.compile(r"^https://www\.linkedin\.com/analytics/search-appearances/?$"),
    # The job tracker, which is where /my-items/saved-jobs/ now redirects (the
    # cardType query is dropped on the way, and that older address is no longer
    # on this list because nothing builds it any more). ``?stage=`` selects
    # which of his own lists renders. It is a read: measured 2026-08-22 by
    # opening three stages in turn and re-reading the default view afterwards,
    # where every tab count was unchanged. The tab strip itself is a set of
    # client-side radios with no url of their own, so ``?stage=`` is the ONLY
    # way to reach the applied list without clicking -- which is exactly why
    # this pattern exists rather than a click.
    #
    # The stages are ENUMERATED rather than left as ``?[^#]*``. LinkedIn's own
    # payload also names interview, archived and clicked_apply, and a wildcard
    # would have admitted all of them plus ``?stage=withdraw`` and ``?apply=1``
    # -- unreachable today, since the stage is a literal in server.py and never
    # a tool argument, but an allowlist should permit what is opened rather
    # than what happens to be harmless. A third stage needs a deliberate edit
    # here, which is the point, and on 2026-08-26 ``draft`` was given one. Its
    # token was READ off LinkedIn's own anchors rather than guessed from the
    # tab: tests/fixtures/jobs_tracker_row.html -- tracked, so the evidence
    # survives a clone -- carries href=".../jobs-tracker/?stage=draft". The
    # two disagree, and that is the trap: the tab is LABELLED "In Progress"
    # and ADDRESSED as ``?stage=draft``, so the word on the tab is the one
    # guess that does not work. interview, archived and clicked_apply remain
    # deliberately absent -- nothing builds them.
    re.compile(
        r"^https://www\.linkedin\.com/jobs-tracker/\?stage=(saved|applied|draft)$"
    ),
    # Job search results.
    re.compile(r"^https://www\.linkedin\.com/jobs/search/?(\?[^#]*)?$"),
    # ONE job posting, addressed by its numeric id and nothing else.
    #
    # No query string is permitted here, unlike every other pattern on this
    # list. LinkedIn hangs tracking parameters off its own job links
    # (``?refId=``, ``?trackingId=``, ``?eBP=``) and a real posting url in the
    # wild carries them, so admitting ``\?[^#]*`` would look like the
    # neighbourly thing to do. It is not: this server BUILDS the url from an
    # integer, so it never has a query to preserve, and a pattern that accepts
    # one is a pattern that accepts whatever a caller appends.
    #
    # The slug form LinkedIn also serves --
    # ``/jobs/view/senior-node-engineer-at-acme-4600000042`` -- is refused for
    # the same reason. A slug is a job TITLE, which is a string, and a string
    # in a url is the thing an allowlist exists to prevent. The numeric id is
    # the whole of what identifies a posting, and ``dom.JOB_HREF`` already
    # captures exactly that group out of either form.
    re.compile(r"^https://www\.linkedin\.com/jobs/view/\d{6,}/?$"),
    # Own profile. /in/me/ redirects to whoever is signed in.
    re.compile(r"^https://www\.linkedin\.com/in/me/?$"),
    # THE THIRD-PARTY PROFILE PATTERN WAS REMOVED 2026-09-04, ON THE OPERATOR'S
    # RULING. It read `^.../in/[A-Za-z0-9\-_%]+/?$` and admitted ANY member's
    # profile page. It carried NO COMMENT OF ITS OWN -- the "Own profile" line
    # above belongs to the `/in/me/` entry -- and nothing anywhere recorded a
    # decision to admit it.
    #
    # WHAT DECIDED IT: THE ALLOWLIST ADMITTED WHAT THIS SERVER'S OWN
    # DOCUMENTATION SAYS IT NEVER DOES. `known_side_effects` states plainly
    # that no tool here loads a third party's profile, and gives the MEASURED
    # reason -- `linkedin_who_viewed_me` reads the RECEIVING END of exactly
    # that signal, so a third-party profile load leaves a durable record in
    # that person's own viewer list. `PERMANENTLY_FORBIDDEN` names the act.
    # Removing this line makes the boundary say what the server already claims.
    #
    # NOT "NOTHING USES IT, SO CLOSE IT" -- that is the weaker argument and it
    # was rejected. The measurement is the second reason, not the first.
    #
    # AND THE MEASUREMENT ASKED THE RIGHT QUESTION, WHICH IS NOT THE OBVIOUS
    # ONE. A literal census answers what BUILDS a url; the boundary's question
    # is what OPENS one. Both were taken. Of 34 url-shaped `/in/` strings
    # across 6457 literals in 19 package files: 20 literal-me, 5 compiled
    # patterns, and 9 interpolated -- FIVE distinct sites, every one traced by
    # hand, and NOT ONE a navigation. `auth.py` and two `shape.py` card
    # parsers build a `profile` field for OUTPUT; `server.py` builds
    # `details_urls` for output; one more is a `startswith("/in/")` CHECK and
    # not a url at all. Every `goto` carrying `/in/` is `/in/me/`.
    #
    # `/in/me/` STILL WORKS, and that was checked rather than assumed:
    # `browser.goto` asserts the REQUESTED url before navigating and does not
    # re-check where it landed, so the redirect from `/in/me/` to his vanity
    # slug never meets this list. `writes._load` asserts the requested url too,
    # and its `PROFILE_URL` is the `/in/me/` form.
    #
    # THE OUTPUT FIELDS ARE A DIFFERENT OBJECT AND ARE NOT BROKEN BY THIS.
    # A url in tool OUTPUT is for a human to open in a browser; a url on this
    # list is for this server to navigate. Coupling them is the confusion, not
    # the consequence. `parse_person_card` and `parse_connection_card` emit
    # OTHER members' profile links and always will -- that is what those
    # fields are for -- and each now says so at its own site.
    # THE `/in/me/` FORM ONLY, NARROWED 2026-09-04 ON THE OPERATOR'S RULING.
    #
    # THIS ENTRY USED TO TAKE `[A-Za-z0-9\-_%]+` FOR THE MEMBER SEGMENT, so it
    # admitted ANY member's detail pages -- their experience, their education,
    # their skills. That was never ruled. It contradicted two things this same
    # file says about itself: `known_side_effects` states that no tool here
    # loads a third party's profile, and the intro editor below is confined to
    # `/in/me/` on the MEASURED ground that loading a third party's profile
    # leaves them a durable record in their own viewer list.
    #
    # IT WAS NEARLY INHERITED. The Interests page was first admitted by adding
    # a fourth word to this alternation, which for one commit ALLOWED
    # `/in/<a-third-party>/details/interests/` -- a stranger's follow graph,
    # read while announcing to that stranger that he had looked. Caught in
    # review. The RED is recorded here rather than fixed quietly, because a
    # boundary defect nobody can see afterwards teaches nobody.
    #
    # NARROWED ONLY AFTER MEASURING WHAT IT WOULD COST, never on the argument
    # alone -- changing a shipped read on a guess is how a working capability
    # breaks quietly, which is the lesson the navigation site below already
    # carries. `scripts/_probe_details_url_breadth.py` PARSED every module
    # (grep is defeated by this very entry: it is a two-line implicit
    # concatenation, and a partial read of it misled a reviewer the same day):
    #
    #     55 files, 10854 string literals, 122 mentioning `/in/`, 42
    #     mentioning `/details/`, 12 f-strings, 0 `.format()` calls
    #     -> 21 literal-me, 10 f-string literal-me, 4 compiled patterns,
    #        8 with no member segment, and TWO interpolated sites
    #
    # BOTH interpolated sites were traced by hand and NEITHER is a third
    # party: `server.py` builds `details_urls` from
    # `shape.profile_slug_from(final_url)` -- HIS OWN slug, off the landing of
    # `/in/me/` -- and `scripts/_probe_interests.py` interpolates the constant
    # `ME = "me"`. So the breadth was reach NOBODY USED.
    #
    # AND THE NAVIGATION SITE WAS CHECKED SEPARATELY, because a literal census
    # answers what BUILDS a url and not what OPENS one. `linkedin_my_profile`
    # picks its second load from `PROFILE_DETAIL_URLS`, a table of `/in/me/`
    # literals; the slug-built form was removed from that path earlier by
    # `tests/test_navigation_is_never_derived.py`. Zero callers break.
    #
    # ONE CONSEQUENCE, RECORDED SO IT IS NOT DISCOVERED LATER: the
    # `details_urls` field `linkedin_my_profile` returns is built in the SLUG
    # form, so this server now advertises three addresses its own read door
    # will refuse. Nothing consumes that field -- it has exactly one write site
    # and no readers -- so nothing breaks today. It is an inconsistency in an
    # OUTPUT, and it is the owner of that emission's to resolve, not this
    # entry's.
    re.compile(
        r"^https://www\.linkedin\.com/in/me/details/"
        r"(skills|experience|education)/?(\?[^#]*)?$"
    ),
    # THE INTERESTS PAGE, AND THE ``/in/me/`` FORM ONLY. Added 2026-09-04.
    #
    # IT IS A SEPARATE PATTERN RATHER THAN A FOURTH WORD IN THE ALTERNATION
    # ABOVE, AND THAT IS THE WHOLE OF THE PERMISSION. The pattern above takes
    # ``[A-Za-z0-9\-_%]+`` for the member segment, so it admits ANY member's
    # details pages. Adding a word to it would have admitted
    # ``/in/<a-third-party>/details/interests/`` -- and that is the worst
    # surface in the package on which to make that mistake, because this tab
    # enumerates the PEOPLE somebody follows. It would have read a third
    # party's follow graph WHILE ANNOUNCING TO THAT THIRD PARTY THAT HE
    # LOOKED: ``linkedin_who_viewed_me`` establishes that loading a member's
    # profile leaves them a durable record in their own viewer list.
    #
    # It was written the wrong way first and caught in review before it could
    # be used. The RED is recorded because a boundary defect that was fixed
    # quietly teaches nobody: at the intermediate commit,
    # ``/in/<other>/details/interests/`` measured ALLOWED.
    #
    # THIS FORM MATCHES THE INTRO EDITOR BELOW, WHICH RULED THE SAME QUESTION
    # SIXTEEN LINES AWAY: "a pattern that can address anybody but him is
    # refused on that ground alone, whatever the page underneath is for."
    # Two rulings three lines apart disagreed about the member segment; this
    # entry follows the narrow one.
    #
    # AND IT COSTS NOTHING: every census row this surface was admitted for is
    # about HIS OWN account, so the ``me`` form reaches all of them.
    #
    # THE SHAPE LAYER WAS ESTABLISHED FIRST, NOT ASSUMED. This tab enumerates
    # FIVE kinds of entity. People are covered by every guard in ``shape.py``
    # -- MEASURED, not argued: a person behind ``/in/`` redacts at both
    # counts, and that row is the CONTROL in
    # ``scripts/_probe_interests_entity_shaping.py``. Companies are settled by
    # precedent, since ``linkedin_followed_companies`` already publishes them.
    # Groups, Newsletters and Schools had never been asked about, and that
    # probe MEASURED all three shipping a name verbatim past both census
    # guards -- a newsletter also shipping its slug, routinely its author's
    # name, on every record. Fixed in ``shape.py`` BEFORE this line existed,
    # because a read that is safe only until he follows a person is not safe.
    #
    # WHAT IT WAS EXPECTED TO BUY, AND WHAT IT ACTUALLY BOUGHT. The claim was
    # that this surface answers whether he belongs to any group or attends any
    # event without opening ``/groups/`` or ``/events/`` -- the precondition
    # for ``GROUPS-SURFACE`` (32 census rows), ``EVENTS-SURFACE`` (18) and
    # ``NEWSLETTER-SURFACE`` (12).
    #
    # THE MEASUREMENT SAYS OTHERWISE: ``/in/me/details/interests/`` REDIRECTS
    # to the profile. Requested at path depth 4, landed at depth 2, returning
    # 236 controls and 8733 characters of main text -- identical on both
    # counts to a direct read of ``/in/me/`` taken the same hour. **The
    # address is admitted and LinkedIn does not serve it.**
    #
    # THE CONTROL, because a lone redirect is uninterpretable: both siblings
    # on the alternation above were loaded in the same run. ``skills`` landed
    # at depth 4 (84 controls, 2359 chars) and ``education`` did not redirect
    # at all (56 controls, 1231 chars). So the redirect is a fact about THIS
    # address, not about ``/details/`` pages and not about the session.
    #
    # TWO READINGS SURVIVE and this comment does not pick between them:
    # LinkedIn may not serve the page at all, or may serve it only when the
    # section is non-empty. Either way THE PRECONDITION QUESTION IS STILL
    # OPEN, and whoever picks it up should not re-derive this route as the
    # cheap answer -- it was tried and it does not serve.
    #
    # THE LINE STAYS. It admits a self-owned address that redirects to another
    # self-owned address already on this list, so it widens nothing, and it
    # costs nothing if LinkedIn starts serving it. The newsletter addresses
    # stay closed.
    #
    # ``/groups/`` AND ``/events/`` NO LONGER STAY CLOSED, and this sentence
    # used to say they did. The two entries below opened exactly their roots on
    # 2026-09-05, and the reasoning is there rather than repeated here. The
    # line is CORRECTED rather than deleted because a comment is a STANDING
    # INSTRUCTION -- whoever opens this file next reads it as current truth --
    # and this one would otherwise assert a closed door two entries above the
    # open one.
    re.compile(
        r"^https://www\.linkedin\.com/in/me/details/interests/?(\?[^#]*)?$"
    ),
    # HIS OWN GROUPS, AND THE ROOT ONLY. Added 2026-09-05 on the team lead's
    # split: which groups he belongs to is HIS OWN DATA, the same class as his
    # own profile; a group's MEMBER DIRECTORY is other people and is not
    # admitted here or anywhere.
    #
    # WHAT THIS SERVES: census rows ``N 173`` ("access the list of groups you
    # belong to"), ``N 174`` ("view the groups you have requested to join")
    # and ``C 60`` ("access your LinkedIn Groups", the same capability counted
    # in a second slice).
    #
    # AND IT IS THE PRECONDITION FOR TWENTY-NINE MORE. If he belongs to zero
    # groups then 29 of ``GROUPS-SURFACE``'s 32 rows are unreachable in
    # principle for this account and the largest blocker in the census is a
    # three-row one. Nobody has established which world we are in.
    #
    # THE CHEAP ROUTES WERE TRIED FIRST AND ALL THREE ARE DEAD. This entry
    # exists because the alternatives are exhausted, and exhausted is a
    # measurement here rather than a mood:
    #
    #   1. THE ALLOWLIST was the visible gate and the least interesting one.
    #      ``scripts/_probe_unmeasured_surface_addresses.py``, re-run at HEAD
    #      2026-09-05: 15 Groups/Events addresses, ALLOWED 0, all 7 controls
    #      passing.
    #   2. THE RENDER is the gate nobody had stated, and it kills every
    #      profile-side route. The profile's Interests region draws five tabs
    #      as ``div role="radio"`` with no href, no id and no data attribute,
    #      and A CATEGORY'S ROWS ARE NOT IN THE DOCUMENT UNTIL ITS TAB IS
    #      PRESSED. Proven by a control rather than argued: the Companies
    #      category holds at least 20 rows -- 20 and 40 distinct company
    #      anchors in ``tests/fixtures/manage_pages_following.html`` and its
    #      hydrated sibling -- and renders ZERO of them on the Interests
    #      capture and ZERO again on a LIVE 396909-character profile read.
    #      A page where a known-non-empty category reads zero cannot answer
    #      the membership question FOR ANY ANSWER.
    #   3. THE ADDRESS: ``/in/me/details/interests/`` is admitted two entries
    #      above and REDIRECTS, with two same-run siblings as the control.
    #
    # AND THERE IS NO OFFLINE ROUTE, measured with both controls behaving.
    # ``scripts/_probe_membership_signal_in_corpus.py`` sweeps every HTML
    # document this project holds -- 30 documents, 2522736 characters -- for
    # six group and event route needles: ALL ZERO, while the must-fire control
    # ``/company/`` found 90 and the must-stay-silent control found 0. Nothing
    # this project has ever captured carries a group or event signal.
    #
    # THE ROOT ONLY, AND THE ANCHORING IS THE WHOLE OF THE PERMISSION. No
    # query string and no sub-path, for the same reason as ``dark-mode`` and
    # ``my-premium``: nothing builds one, so nothing needs preserving, and an
    # anchor is what keeps one page from becoming a family. What that
    # deliberately does NOT admit, each named because a widening is only
    # narrow if its refusals are stated:
    #
    #     /groups/<id>/            a group feed -- other members' posts in full
    #     /groups/<id>/members/    THE MEMBER ROSTER. Census row N 165, and
    #                              the row the team lead put out of scope by
    #                              name. It is a list of people who did not
    #                              choose to be enumerated by him, and which
    #                              url serves it changes nothing about that.
    #     /groups/<id>/requests/   a pending-member queue, same objection
    #     /groups/discover/        recommendations
    #     /search/results/groups/  belongs to SEARCH-RESULTS-SURFACE, which is
    #                              queued DECIDE and is not this entry's to
    #                              inherit
    #
    # ``/groups/<id>/invite/`` IS REFUSED TWICE AND THAT IS WORTH KNOWING
    # RATHER THAN DISCOVERING. It contains ``/invite``, which is on
    # :data:`_FORBIDDEN_URL_SUBSTRINGS` and checked BEFORE this list, AND it
    # fails this anchored pattern. Census rows ``N 166`` and ``C 69`` need TWO
    # boundary changes, not one, and neither is proposed here.
    #
    # THE PAGE MAY RENDER OTHER PEOPLE AND THAT IS NOT THIS LIST'S QUESTION.
    # Six of the addresses already on this list draw pages substantially made
    # of other people -- the feed, notifications, both messaging forms, the
    # connections list, the profile-views analytics and an item permalink with
    # its comments. ``linkedin_who_viewed_me`` states the resolution in its
    # own docstring, on the hardest case this package has: "that page is made
    # of other people and its control labels carry them; the reader takes
    # numbers, filter labels, the chart's own sentence and COUNTS of page
    # regions, and nothing else." **This list decides what may be OPENED. The
    # shaper decides what may be SAID.**
    #
    # NO WRITE IS BOUGHT BY THIS. Joining, leaving, posting and inviting all
    # need their own url, their own sanction and their own ruling; posting in
    # a group is a second broadcast route with a different audience and is
    # ``publish_post``'s equal in risk rather than a lesser case.
    re.compile(r"^https://www\.linkedin\.com/groups/?$"),
    # HIS OWN EVENTS, AND THE ROOT ONLY. Added 2026-09-05, same ruling, same
    # anchoring, same refusals -- and BOUGHT ON A THINNER ROW BASIS THAN
    # ``/groups/`` ABOVE, which is recorded here rather than glossed.
    #
    # THE CENSUS HAS NO ROW FOR "the events you are registered for". The
    # Events family's nearest neighbours are ``N 185`` "attend an event you
    # accepted" (a WRITE) and ``N 183`` "receive event invitations only from
    # your 1st-degree connections" (a SETTING, which lives under preferences
    # and not here). The censused content of this root is ``N 180``: "events
    # recommended from your interests, Pages you follow, AND WHAT YOUR NETWORK
    # IS ATTENDING".
    #
    # So this admission buys a recommendation surface whose stated content
    # includes other people's attendance, and buys the self-scoped read it was
    # written for only if LinkedIn draws a "your events" region that no census
    # row names. That is a fact about the census rather than a reason to
    # refuse -- the row set was walked from LinkedIn's help tree, and a help
    # tree documents what a member can DO rather than what a page DRAWS.
    #
    # IT IS ADMITTED ANYWAY, FOR ONE STATED REASON: it is the only route left
    # to the precondition above, the precondition governs 50 census rows
    # across both blockers, and one load settles it. Whoever reads the result
    # should weigh the events half more carefully than the groups half.
    #
    # WHAT IT DOES NOT ADMIT:
    #
    #     /events/<id>/            an event page -- organizer and content.
    #                              Census row N 184, and it is the row that
    #                              proves the ledger's "allowlist +1" for this
    #                              blocker was short.
    #     /events/<id>/comments/   census row C 92, third-party comments
    #     /events/<id>/about/      same page, same objection
    #     THE ATTENDEE LIST        census rows N 188 and N 189. A second
    #                              member roster, and out of scope by the same
    #                              ruling that put N 165 out of scope.
    #     /search/results/events/  SEARCH-RESULTS-SURFACE again
    re.compile(r"^https://www\.linkedin\.com/events/?$"),
    # THE INTRO EDITOR ON HIS OWN PROFILE. Added 2026-08-31 on the operator's
    # ruling: the profile editors are his own profile, no third party, and
    # therefore his to open.
    #
    # THE ``/in/me/`` FORM ONLY, AND THAT IS THE WHOLE OF THE PERMISSION.
    # The obvious generalisation -- ``/in/[A-Za-z0-9-]+/edit/intro/`` -- is
    # the one shape that must never be written here, and the reason is
    # MEASURED rather than cautious: ``linkedin_who_viewed_me`` establishes
    # that loading a third party's profile leaves them a durable record in
    # their own "who viewed your profile" list. So a pattern that can address
    # anybody but him is refused on that ground alone, whatever the page
    # underneath is for. ``/in/me/`` redirects to whoever is signed in and can
    # therefore only ever reach his own profile.
    #
    # No query string, for the same reason as the job posting above: nothing
    # builds one, so nothing needs to be preserved.
    #
    # IT IS ADMITTED HERE AND STILL REFUSED ONE GATE EARLIER, unless it is
    # named. ``/edit/`` is on :data:`_FORBIDDEN_URL_SUBSTRINGS`, which is
    # checked BEFORE this list, and that entry is deliberately untouched: it
    # must keep refusing the whole rest of the family. What lets this ONE url
    # through is :data:`_FORBIDDEN_SUBSTRING_EXEMPTIONS`, an EXACT-url table,
    # below.
    #
    # ONE RESIDUE, recorded rather than left to be tripped over. The pattern
    # ends ``intro/?$``, so the slashless spelling matches it; the exemption
    # is keyed on the exact url ``server.py`` builds, which carries the
    # trailing slash. ``/in/me/edit/intro`` is therefore still refused by the
    # forbidden gate. The exemption being NARROWER than the pattern is the
    # conservative direction, and it is the direction chosen.
    re.compile(r"^https://www\.linkedin\.com/in/me/edit/intro/?$"),
    # The company Pages he follows -- LinkedIn calls the surface "Manage
    # Pages". Added 2026-08-23. A pure read, and the ONLY one LinkedIn offers
    # for this list: the profile's Interests section renders a Companies tab,
    # but that tab is a client-side radio with no url of its own and no href
    # anywhere in the DOM -- the same shape as the jobs-tracker tab strip,
    # except that this one has no ``?stage=``-style escape hatch. Measured by
    # loading the Interests page and finding zero candidate hrefs on it.
    #
    # No query string, for the same reason as the job posting below: nothing
    # builds one, so nothing needs to be preserved.
    #
    # RECORD THE SIBLING THAT IS NOT HERE, because the obvious later "fix" is
    # to reach for it. The PEOPLE he follows live at
    # ``/mynetwork/network-manager/people-follow/following/``, which contains
    # the substring ``/follow`` and is therefore refused by
    # :data:`_FORBIDDEN_URL_SUBSTRINGS` below before this list is even
    # consulted. The company url happens not to contain it. That is luck, not
    # design -- and the right response to the luck running out is to leave the
    # people list unread, never to shorten the forbidden list.
    re.compile(
        r"^https://www\.linkedin\.com/mynetwork/network-manager/company/?$"
    ),
    # THE NEWSLETTERS HE SUBSCRIBES TO, AND THE ROOT ONLY. Added 2026-09-05,
    # as the third sibling in the Manage-my-network family: the connections
    # list above, the Pages list directly above this, and now this one.
    #
    # THE ADDRESS WAS NOT GUESSED AND IT IS NOT THIS ENTRY'S FIND. It is a
    # constant this repository MEASURED on 2026-09-04 while hunting something
    # else entirely. ``dom.py``'s invitation-badge aim records the two
    # ``/mynetwork`` controls a live feed actually draws::
    #
    #     a  aria-label with a count   href="https://www.linkedin.com/mynetwork"
    #     a  no aria-label at all      href=".../mynetwork/network-manager/newsletters/"
    #
    # The badge hunt found this link and REJECTED it for carrying no label,
    # and the address then sat unused in a docstring and a test for a day.
    # It is also in a TRACKED FIXTURE -- one anchor in
    # ``tests/fixtures/connections_list.html`` -- so the spelling this pattern
    # admits is asserted against a captured document rather than against a
    # commit message. ``tests/test_newsletter_route.py`` is that assertion,
    # and it is the control that fires if LinkedIn moves the address.
    #
    # WHY THE CENSUS FILED THIS SURFACE SOMEWHERE ELSE, which is the whole
    # point of the entry. ``NEWSLETTER-SURFACE``'s reader-side rows -- ``N 57``
    # "view the newsletters you subscribe to" and its four neighbours -- are
    # filed against the surface where LinkedIn DRAWS the control, which is the
    # profile's Interests tab. That surface is dead twice over and both
    # deaths are measured, not argued:
    #
    #   * THE RENDER GATE. The Interests region draws five categories as
    #     ``div role="radio"`` with no href, and a category's rows are not in
    #     the document until its tab is pressed. Newsletters is one of the
    #     five. Proven by a control: the Companies category holds at least 20
    #     rows in the tracked fixtures and renders ZERO on the Interests
    #     capture and ZERO on a live 396909-character profile read.
    #   * THE ADDRESS. ``/in/me/details/interests/`` is admitted six entries
    #     above and LinkedIn REDIRECTS it to the profile, with two same-run
    #     siblings that did not redirect as its control.
    #
    # So a row filed against the surface where the control is drawn is not
    # necessarily blocked by that surface --
    # ``_audit/2026-09-05-routes-already-admitted.md``, which moved fourteen
    # rows on that hypothesis. This is the fifteenth.
    #
    # WHAT IT BUYS, STATED AS A PRECONDITION RATHER THAN AS A CAPABILITY,
    # because that is the honest size of it. Whether he subscribes to any
    # newsletter at all is unestablished, and if the answer is zero then five
    # of this blocker's reader-side rows (``N 55``, ``N 56``, ``N 57``,
    # ``N 58``, ``M C80``) are unreachable in principle for this account. One
    # load settles it. That is the same argument the groups and events roots
    # were paid for on, and it is deliberately not a larger one.
    #
    # AND IT DOES NOT BUY THE AUTHOR-SIDE PRECONDITION, which is the half a
    # careless reader will assume it covers. ``M C50``, ``M C51``, ``M C81``,
    # ``M C84`` and ``P L3`` are about newsletters he WRITES, and no
    # measurement here says this page lists those. Whether it does is a
    # question for the first live read, not an assumption for this entry.
    #
    # NO QUERY STRING AND NO SUB-PATH, and the anchoring is the whole of the
    # permission -- the same shape as the two roots opened on 2026-09-05.
    # What that deliberately does NOT admit, each named because a widening is
    # only narrow if its refusals are stated:
    #
    #     /newsletters/<slug>/       ONE newsletter's own page. Its slug is
    #                                ROUTINELY ITS AUTHOR'S NAME -- measured,
    #                                ``scripts/_probe_interests_entity_shaping.py``
    #                                -- so the address itself carries a person
    #                                and admitting it would put one in every
    #                                log line that records a page load.
    #     /newsletters/              the product root, which is a family
    #     /newsletters/<slug>/analytics/   census ``M C83``, ``P L4``
    #     .../newsletters/?<anything>      a query is where a filter naming a
    #                                person would arrive
    #
    # ONE REFUSAL WORTH KNOWING RATHER THAN DISCOVERING: creating a newsletter
    # is refused TWICE. ``/newsletters/create/`` contains ``/create``, which
    # is on :data:`_FORBIDDEN_URL_SUBSTRINGS` and checked BEFORE this list,
    # AND no pattern admits it. Census rows ``M C81`` and ``M C50`` need two
    # boundary changes and a WriteSpec, and none of the three is proposed
    # here. Measured at HEAD by ``scripts/_probe_newsletter_routes.py``.
    #
    # THE BADGE QUESTION IS OPEN AND IS NOT SETTLED BY THIS ENTRY. ``/mynetwork/``
    # itself is refused because opening it is BELIEVED to consume the pending
    # invitation badge; the connections sub-page was admitted on the argument
    # that a sub-page does not, and ``linkedin_connections`` does not rely on
    # the argument -- it reads the badge before and after and refuses when it
    # cannot. Any reader built on THIS address inherits that obligation, and
    # the instrument already exists: ``dom.read_invitation_badge``. This entry
    # opens the door; it does not certify that walking through it is free.
    #
    # THE PAGE IS MADE OF OTHER PEOPLE'S PUBLICATIONS AND THAT IS NOT THIS
    # LIST'S QUESTION. **This list decides what may be OPENED. The shaper
    # decides what may be SAID.** What may be said here is narrower than for
    # any sibling in this family: :func:`shape.subscription_row` publishes a
    # constant href shape and NEVER a newsletter's title, because no
    # instrument in this package can decide whether a title carries a
    # person's name -- MEASURED, and the measurement is in that function's
    # docstring rather than asserted here.
    re.compile(
        r"^https://www\.linkedin\.com/mynetwork/network-manager/newsletters/?$"
    ),
    # THE SETTINGS INDEX, AND ONLY THE INDEX. Added 2026-08-30 so that
    # linkedin_surface_census can measure it; nothing else in this package
    # builds this url.
    #
    # NO QUERY STRING AND NO SUB-PATH, and the anchoring is the whole of the
    # permission. ``/mypreferences/d/`` renders a LIST OF SECTIONS. The
    # toggles live one level down, on ``/mypreferences/d/categories/<name>``,
    # and those are refused twice over: they fail this anchored pattern, and
    # they now also contain a FORBIDDEN SUBSTRING (below). A census wants the
    # index -- which sections exist, and whether a section is url-addressed or
    # a modal -- and the index is exactly what this admits.
    #
    # THE SIDE-EFFECT RULING THAT PRECEDED THIS ENTRY, since a read surface is
    # admitted here only after one. Loading the index consumes no unread
    # counter (this surface carries no badge -- unlike notifications and
    # messaging, whose badges are MEASURED to reset on load, which is why
    # neither is a census key), emits nothing another person can observe, and
    # changes no value the account holds. Where LinkedIn interposes a re-auth
    # challenge instead of serving the page, the landing url carries
    # ``/checkpoint/`` and ``config.AUTHWALL_MARKERS`` already turns that into
    # a reported failure rather than a silent half-read. Recorded in full in
    # ``_audit/2026-08-30-linkedin-nine.md``.
    #
    # WHY NOT ``/psettings/``: it is the legacy address for the same surface
    # and nothing builds it, so it is on the forbidden list instead of here.
    re.compile(r"^https://www\.linkedin\.com/mypreferences/d/?$"),
    # ONE NAMED SETTINGS PAGE BELOW THE INDEX. Added 2026-08-31 on the
    # operator's ruling, and the ruling's own words are the constraint: ONE
    # NAMED PAGE AT A TIME, NEVER THE FAMILY, NEVER A WILDCARD. So this is an
    # anchored pattern naming one page, not ``/mypreferences/d/[a-z-]+``, and
    # a second page needs a second deliberate edit here.
    #
    # WHY ``dark-mode`` AND NOT ONE OF THE OTHERS, because three were on the
    # table and two were refused:
    #
    # * It is a pure PER-ACCOUNT DISPLAY PREFERENCE. It has no audience, it
    #   names no third party, and rendering it emits nothing another member
    #   can observe. The page RENDERS the value the account already holds; it
    #   changes none of them.
    # * And the part that actually decided it: IT REQUIRES NO NARROWING OF ANY
    #   FORBIDDEN SUBSTRING. ``/mypreferences/d/dark-mode`` contains none of
    #   them, so the second gate is untouched and stays fully intact for the
    #   ``categories/`` family. ``/mypreferences/d/settings/language`` and
    #   ``/mypreferences/d/settings/autoplay-videos`` would each have required
    #   ``"/settings/"`` to be narrowed to buy one page, which is trading a
    #   standing refusal for a single read. They are deliberately NOT
    #   admitted, and neither is any ``categories/`` page.
    #
    # No query string and no sub-path: nothing builds either, and the
    # anchoring is what keeps this one page from becoming the family.
    re.compile(r"^https://www\.linkedin\.com/mypreferences/d/dark-mode/?$"),
    # ONE ITEM PERMALINK. Added 2026-08-31 on the operator's ruling: ONE NAMED
    # ITEM PERMALINK PER CALL. It is the write surface ``react_to_item`` acts
    # on and the read surface ``linkedin_surface_census("feed_item")``
    # measures, so it is admitted with two consumers rather than none.
    #
    # THE SHAPE IS NOT INVENTED HERE. ``urn:li:[A-Za-z]+:[0-9]+`` is the
    # anchored shape ``dom.ACTIVITY_ITEMS_JS`` already requires before it will
    # emit an item key at all, so the only urns this server can build a url
    # from are the only urns this pattern admits, and the two cannot drift:
    # ``tests/test_readonly.py`` pins them equal. A percent-encoded spelling
    # matches NEITHER -- it has never been observed in this position, and a
    # shape nobody has seen is not a shape to admit.
    #
    # NO QUERY STRING, so LinkedIn's tracking parameters do not come with it
    # and neither does anything a caller appends.
    #
    # AND THE SECOND GATE THIS COST, STATED RATHER THAN GLOSSED.
    # ``"/feed/update"`` WAS on :data:`_FORBIDDEN_URL_SUBSTRINGS` and has been
    # REMOVED, because that list is substring-based and cannot express "this
    # permalink but nothing else under it" -- and the exemption table cannot
    # hold it either, since that table is keyed on an EXACT url and the urn
    # varies per call. So this family now stands on the anchored pattern
    # alone.
    #
    # WHAT THAT DOES AND DOES NOT GIVE UP, measured against the list rather
    # than argued: the destructive members of this family are ``/edit/``,
    # ``/delete``, ``/withdraw`` and ``action=``, and ALL FOUR are still on
    # the forbidden list and still checked first. So the second gate is intact
    # for everything under ``/feed/update/`` that could change anything; what
    # was given up is a blanket refusal of a surface that RENDERS one of his
    # own items. That is the trade the ruling made, and it is written here so
    # the next reader sees a decision rather than an omission.
    re.compile(
        r"^https://www\.linkedin\.com/feed/update/"
        r"urn:li:[A-Za-z]+:[0-9]+/?$"
    ),
    # THE TWO PUBLISHING COMPOSERS, admitted 2026-08-31 on the operator's
    # ruling, BY NAME AND ONE AT A TIME.
    #
    # Both were MEASURED as real anchors before being written here, which is
    # the whole of why they are addresses rather than guesses: ``Create a
    # post`` is an ``<a>`` whose href shapes to ``/preload/sharebox/`` (count
    # 1 on his profile, three readings across two days) and ``Write article``
    # is an ``<a>`` to ``/article/new/`` (count 1 on the feed, same). The
    # third composer route -- ``Start a post`` -- is a ``div[role=button]``
    # with NO href and is deliberately NOT here: reaching it needs a click on
    # a read path, which is a mutation this package does not sanction.
    #
    # THE COST THE OPERATOR CLEARED KNOWINGLY. A composer may AUTOSAVE, and
    # this server has no reachable surface on which a resulting draft could be
    # seen -- 17 candidate draft addresses were run against this very module
    # on 2026-08-31 and all 17 were refused. So opening one may leave an
    # artefact only he can find. He cleared that; the capture reports what it
    # can see and does not claim what it cannot.
    #
    # NEITHER ADMITS THIS SERVER TO PUBLISHING. Publishing needs text entry,
    # and ``fill``, ``type``, ``press`` and ``keyboard`` are on
    # :data:`_MUTATION_CALL_PATTERNS` and on no entry of
    # :data:`SANCTIONED_MUTATIONS`. An address is not a capability.
    re.compile(r"^https://www\.linkedin\.com/preload/sharebox/?$"),
    re.compile(r"^https://www\.linkedin\.com/article/new/?$"),
    # THE MESSAGE COMPOSER. Admitted 2026-08-31 on the operator's ruling, and
    # it is the narrowest admission on this list because it is the only one
    # that had to be bought past the forbidden gate.
    #
    # IT IS NOT REACHED BY SHORTENING THE FORBIDDEN LIST.
    # ``"/messaging/compose"`` STAYS on :data:`_FORBIDDEN_URL_SUBSTRINGS`
    # exactly as it was -- it is the entry that survived when the blanket
    # ``"/messaging"`` ban was narrowed on 2026-08-26 -- and this one url is
    # let past it by :data:`_FORBIDDEN_SUBSTRING_EXEMPTIONS`, an EXACT-url
    # table. So every other address in that family is refused by the same gate
    # it always was, and a second one needs a second deliberate entry.
    #
    # THE PRECONDITION THAT WAS CHECKED BEFORE THIS WAS WRITTEN. Loading
    # messaging can open a conversation LinkedIn chooses and mark a real
    # person's InMail read -- a cost paid by somebody who is not him. The
    # operator's ruling was conditioned on the messaging badge reading ZERO
    # first, and it was read first: ``Messaging, 0 new notifications``, count
    # 1, on ``/feed/`` and on his profile, 2026-08-31. With no unread message
    # there is no stranger's InMail to spend.
    re.compile(r"^https://www\.linkedin\.com/messaging/compose/?$"),
    # THE SAME COMPOSER, ADDRESSED TO ONE MEMBER BY IDENTIFIER. Added
    # 2026-09-03. The forbidden substring it carries is exempted by the
    # ANCHORED pattern in _FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS, and this
    # entry is the second, independent gate -- the exemption says which
    # substring the url may carry, this says the url is a permitted read.
    #
    # IT REPLACES A MEASURED DEAD END RATHER THAN ADDING A CAPABILITY.
    # Addressing a recipient by NAME is finished: three stable live census
    # runs, and an offset instrument that found the needle at ELEVEN distinct
    # positions across ten rows with accessible names 49 to 178 characters
    # long. No anchored or positional matcher can work there. This is how one
    # person gets named deterministically instead.
    re.compile(
        r"^https://www\.linkedin\.com/messaging/compose/"
        r"\?profileUrn=urn%3Ali%3Afsd_profile%3A[A-Za-z0-9_-]{1,64}"
        r"&recipient=[A-Za-z0-9_-]{1,64}$"
    ),
    # HIS OWN SUBSCRIPTION PAGE. Admitted 2026-09-01 on the operator's
    # ruling, as ONE named address, and it exists to answer ONE question:
    # whether an InMail balance is a countable thing this server can read.
    #
    # WHY IT IS NEEDED AT ALL. ``send_message`` may spend a finite credit
    # whose size this server does not know, and a gate that cannot tell him
    # what an action COSTS is not fully a gate -- every other write here names
    # its cost. The composer itself was captured on 2026-08-31 and DOES NOT
    # carry a balance: the control there named ``InMail`` is a
    # conversation-list FILTER PILL with aria-checked=false, sitting beside
    # Focused, Unread, Starred and Connections. So the balance is either here
    # or nowhere.
    #
    # IT NAMES NO THIRD PARTY. This is his own subscription state -- what he
    # pays for and what it includes -- and it appeared as an ordinary href on
    # his own feed and profile ("<redacted> features"), which is how it was
    # found rather than guessed.
    #
    # No query string and no sub-path: nothing builds either, and the
    # anchoring is what keeps this one page from becoming the family. In
    # particular ``/premium/`` has purchase and upgrade flows under it and
    # NONE of them is admitted here.
    re.compile(r"^https://www\.linkedin\.com/premium/my-premium/?$"),
    # HIS OWN CONNECTIONS LIST. Admitted 2026-09-03; the full argument is on
    # the paired entry in _FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS, which is
    # where the interesting half lives. This is the SECOND, INDEPENDENT gate:
    # the exemption says which forbidden substrings this url may carry, and
    # this says the url is a permitted read. Neither alone admits it.
    #
    # THE PEOPLE-SEARCH SIBLING IS DELIBERATELY NOT HERE.
    # ``/search/results/people/`` is the GENERAL case where this is the
    # specific one, it has no pattern and no written reason, and the lead
    # ruled it a separate decision rather than part of this one. Recording
    # that here because the obvious later "fix" is to reach for it, exactly as
    # the people-follow list is recorded on the Manage-Pages entry above.
    #
    # NO QUERY STRING. Nothing builds one, and a query is where a filter
    # naming a person would arrive.
    re.compile(
        r"^https://www\.linkedin\.com/mynetwork/invite-connect/connections/?$"
    ),
    # Notifications list.
    re.compile(r"^https://www\.linkedin\.com/notifications/?(\?[^#]*)?$"),
    # Feed, used only as a corroborating auth measurement.
    re.compile(r"^https://www\.linkedin\.com/feed/?$"),
    # The login page, opened for the operator to sign in himself.
    re.compile(r"^https://www\.linkedin\.com/login/?(\?[^#]*)?$"),
)

#: Substrings that must never appear in a navigation target, checked before
#: the allowlist as a second, independent gate. Belt and braces: a future
#: pattern edited too loosely still cannot reach these.
_FORBIDDEN_URL_SUBSTRINGS: tuple[str, ...] = (
    "/jobs/application",
    "easyapply",
    "easy-apply",
    # NARROWED 2026-08-26 from the blanket "/messaging", on the operator's
    # ruling that reading his own inbox is his to do. SENDING stays forbidden
    # and this is the entry that keeps it so: /messaging/compose is the
    # pre-filled composer LinkedIn opens from a job page, and nothing here may
    # reach it.
    #
    # WHY THE BLANKET ENTRY COULD NOT SIMPLY BE DROPPED, and why this is not
    # the smaller change it looks like: /messaging/ DOES NOT STAY ON A LIST.
    # Measured twice -- LinkedIn redirects it into one specific conversation
    # thread that LinkedIn, not the caller, chooses. And assert_read_url gates
    # the REQUESTED url only; the landed url is never re-checked. So leaving
    # "/messaging/thread" forbidden while permitting "/messaging/" would have
    # produced a guard that forbids a destination it knowingly delivers you
    # to -- a fiction, and a worse one than an honest permission, because the
    # next reader would trust it.
    #
    # So the thread surface is ALLOWED and the cost is stated where a caller
    # meets it, in linkedin_open_messaging's own name and docstring, rather
    # than being denied by a list that cannot enforce it.
    "/messaging/compose",
    "/invite",
    "invitation",
    "/connect",
    "/follow",
    "/unfollow",
    "/endorse",
    "/post/",
    # ``"/feed/update"`` WAS HERE AND WAS REMOVED 2026-08-31, on the
    # operator's ruling admitting ONE NAMED ITEM PERMALINK PER CALL. It is
    # recorded rather than deleted because a substring that quietly leaves
    # this tuple is indistinguishable from one that was never in it.
    #
    # WHY IT COULD NOT STAY. This gate is substring-based, so it cannot say
    # "the permalink but nothing under it", and the exemption table below is
    # keyed on an EXACT url while the urn varies per call. Neither mechanism
    # can express the ruling, so the ruling costs this entry.
    #
    # WHAT STILL REFUSES THE DANGEROUS HALF OF THAT FAMILY: ``/edit/``,
    # ``/delete``, ``/withdraw`` and ``action=`` are all still below and all
    # still checked before the allowlist. The permalink itself is admitted by
    # ONE anchored pattern requiring the literal ``urn:li:<type>:<digits>``
    # shape and no query string.
    "sharing/share",
    "/settings/",
    "opentowork",
    "open-to-work",
    # THE TWO SETTINGS ENTRIES BELOW WERE ADDED 2026-08-30, and they were
    # added because ``"/settings/"`` above was MEASURED NOT TO COVER THE
    # SURFACE IT IS NAMED FOR.
    #
    # The measurement, run against this very function rather than reasoned
    # about: ``is_read_url("https://www.linkedin.com/mypreferences/d/")`` and
    # ``is_read_url("https://www.linkedin.com/psettings/")`` were both False
    # -- but both were refused BY THE ALLOWLIST, not here. ``"/settings/"``
    # matched neither. LinkedIn moved its settings to ``/mypreferences/d/``,
    # and the legacy address is ``/psettings/``, which does not contain
    # ``"/settings/"`` because the character before ``settings/`` is a ``p``.
    # The only address the old entry ever caught is a ``/settings/`` LinkedIn
    # no longer serves.
    #
    # WHY THAT MATTERED ENOUGH TO FIX. The net refusal held, so nothing was
    # ever reachable that should not have been. What did not hold is this
    # list's stated job: it is documented above as a "second, independent
    # gate" and as "belt and braces: a future pattern edited too loosely still
    # cannot reach these". For the settings family there was no second gate at
    # all, and the allowlist has now been deliberately loosened -- the index is
    # admitted, one line up -- which is exactly the situation the backstop
    # exists for. The category pages carry the toggles; they are the part that
    # must stay unreachable however the allowlist is edited later.
    #
    # ``"/settings/"`` IS KEPT rather than replaced. It costs nothing, and an
    # address LinkedIn stopped serving is one it can start serving again.
    "/mypreferences/d/categories/",
    "/psettings/",
    # THE TWO ENTRIES BELOW WERE ADDED 2026-08-31, and they correct a claim
    # this module made about itself rather than adding a new caution.
    #
    # The settings audit assumed "Close and delete account" and "Hibernate
    # account" -- the two most destructive addresses on the account, and the
    # only two on it that are not undoable by re-running the opposite tool --
    # were covered by the ``/mypreferences/d/categories/`` entry three lines
    # up. THEY ARE NOT. Measured off a live census 2026-08-31, their real
    # addresses are ``/mypreferences/d/close-accounts`` and
    # ``/mypreferences/d/hibernate-account``, and NEITHER CONTAINS
    # ``categories/``. The only thing that had ever refused them was the
    # anchored allowlist.
    #
    # WHY THAT MATTERED ENOUGH TO FIX, in the same terms as the 2026-08-30
    # entry above it: the net refusal held, so neither was ever reachable.
    # What did not hold is this list's stated job. It is documented at the top
    # of this tuple as a "second, independent gate" and as "belt and braces: a
    # future pattern edited too loosely still cannot reach these" -- and for
    # the two worst addresses on the account there was no second gate at all.
    # The allowlist has now been deliberately widened twice in two days, which
    # is exactly the situation a backstop exists for. Now there is one.
    "/close-accounts",
    "/hibernate-account",
    # ------------------------------------------------------------------
    # ADDED 2026-09-03, AND THIS TIME THE THING BEING FIXED IS THE SHAPE OF
    # THE PREVIOUS TWO FIXES.
    #
    # The 2026-08-30 and 2026-08-31 entries above were each written after a
    # surface was found with no second gate, and each closed THAT SURFACE.
    # On 2026-09-03 the question was asked mechanically instead of
    # incidentally -- which addresses does the anchored allowlist refuse ALONE?
    # -- and ten came back. Reading them together names what the two
    # per-address fixes had both walked past:
    #
    #     THIS LIST WAS ANCHORED TO PATH SPELLINGS ON THE DESKTOP TREE.
    #
    # Three ways past it, all ten members accounted for by one of them:
    #
    # * A SECOND SPELLING. ``/public-profile/settings`` has no trailing
    #   slash, so ``"/settings/"`` -- slashes on both sides, present since
    #   the beginning -- does not match it. The SAME url with a trailing
    #   slash was already refused. A gate that turns on a trailing slash is
    #   a spelling filter, not a ruling.
    # * A LEGACY NAMESPACE. ``/uas/`` is LinkedIn's old auth tree and the
    #   exact sibling of the ``/psettings/`` three lines up, which is on this
    #   list for precisely the stated reason that a legacy address is one
    #   LinkedIn can start serving again.
    # * A PARALLEL TREE. ``/mwlite/`` is a whole mobile-web mirror of the
    #   site -- every settings page, every editor, at paths no desktop
    #   pattern anticipated. It is the sharpest instance and the cheapest
    #   entry here: one line, an unbounded number of members.
    #
    # NOTHING WAS EVER REACHABLE, and that matters more than the fix. All ten
    # are refused today and were refused before this block existed; the
    # anchored allowlist held every one. This is a defence-in-depth asymmetry
    # -- one layer where the paragraph at the top of this tuple promises two
    # -- and it is not an open door.
    #
    # EVERY ENTRY BELOW WAS MEASURED FOR CASUALTIES BEFORE IT WAS WRITTEN,
    # against every census surface, every readable setting and every write
    # target rebuilt from its own spec. Zero. The check ships as
    # ``test_the_second_gate_covers_the_class.py``, which also puts an address
    # through the real guard FOR EVERY ENTRY HERE that is not one of the ten
    # -- an entry that closed only its own member is a literal wearing a
    # class's clothes, and that test is what tells them apart.
    #
    # THE THREE THAT CLOSE A TREE OR A SPELLING.
    #
    # ``"settings"`` bare, and ``"/settings/"`` above is KEPT rather than
    # replaced: the bare word is a strict superset, so replacing costs nothing
    # behaviourally while being a DELETION from a list that has only ever
    # grown -- a boundary change needing its own review, bought for no gain.
    # A redundant refusal is free.
    "settings",
    "/uas/",
    "/mwlite/",
    # THE SIX WORD-SHAPED ENTRIES, and the reason they are words rather than
    # the one path prefix that would replace them.
    #
    # Six of the ten live under ``/mypreferences/d/``. That prefix is the
    # natural close and IT CANNOT BE TAKEN. Two reasons, the second measured:
    #
    # 1. The six share with the two ADMITTED urls under that prefix -- the
    #    settings index and ``/mypreferences/d/dark-mode``, both on the
    #    allowlist above -- only the prefix itself. No substring separates
    #    them. Same mechanical fact as ``/feed/update``, recorded above.
    # 2. :data:`_FORBIDDEN_SUBSTRING_EXEMPTIONS` could hold those two urls for
    #    the READ door. ``writes.assert_write_url`` DOES NOT CONSULT IT. It
    #    iterates this tuple directly and honours only
    #    ``spec.exempt_substring``, which is ``None`` on the settings write.
    #    So adding the prefix closes six read addresses and breaks the only
    #    settings write this server ships. Demonstrated, not supposed, in
    #    ``test_the_subtree_prefix_is_absent_and_the_blocker_is_shown``.
    #
    # The repair is one line -- ``exempt_substring="/mypreferences/d/"`` on
    # the ``update_setting`` spec -- and it is in ``writes.py``, which the
    # agent who wrote this block did not own. The prefix entry is therefore a
    # decision left to somebody who does, rather than a gap to be rediscovered
    # mechanically a third time.
    #
    # AND THE WORDS ARE NOT MERELY THE FALLBACK. ``password`` refuses the
    # password page at EVERY address -- desktop tree, mobile tree, legacy
    # namespace, and whatever LinkedIn ships next. The prefix would refuse it
    # at one. On this axis the second-best close is the broader one.
    #
    # ONE RESIDUE, RECORDED RATHER THAN LEFT TO BE TRIPPED OVER, in the same
    # spirit as the note on the intro-editor exemption above. A word entry is
    # matched against the WHOLE url, and ``/in/<vanity>/`` is on the allowlist
    # -- so a member whose vanity slug happens to contain one of these words
    # is now refused. ``cookies`` and ``visibility`` are the two that could
    # plausibly appear in a real person's handle; the rest could not.
    #
    # MEASURED BEFORE ACCEPTED, not waved past: every ``linkedin.com/in/<slug>``
    # in this repository was extracted and checked -- 16 distinct slugs, ZERO
    # of which any entry here refuses. And the failure mode is the safe one:
    # a loud WriteAttemptError naming the substring, never a silent wrong
    # read. A false refusal on one third-party profile is the price of a
    # second gate on the account's own cookie and visibility settings, and it
    # is a price this list is in the business of paying.
    "password",
    "two-factor",
    "verification",
    "cookies",
    "job-application",
    "visibility",
    # ------------------------------------------------------------------
    "/edit/",
    "action=",
    "/delete",
    "/withdraw",
    # THE VERB THAT WAS NEVER ON THIS LIST. The four entries above are the
    # destructive verbs and they have been here from the start; the verb that
    # MAKES something has not. ``/badges/profile/create`` is the member that
    # exposed it, and the class is every creation surface on the account.
    # Added 2026-09-03 with the block above.
    "/create",
)

#: The ONE url permitted to carry a forbidden substring, and WHICH substring.
#:
#: Added 2026-08-31, with the intro editor on the allowlist above.
#: ``/in/me/edit/intro/`` contains ``/edit/``, which is on the tuple above and
#: is checked BEFORE the allowlist, so admitting the page needed either this
#: table or a narrowed ``/edit/`` entry. Narrowing was refused: ``/edit/`` must
#: keep refusing the whole rest of that family, on his own profile and on
#: everybody else's, and buying one page by weakening a standing refusal is
#: the trade this module exists to make somebody argue for.
#:
#: THE SEMANTICS, and each of the three is load-bearing:
#:
#: * THE KEY IS AN EXACT, COMPLETE URL, compared with ``==`` against the whole
#:   lowercased url -- never a prefix, never a pattern, never ``startswith``.
#:   The dict lookup below IS that equality. This mirrors
#:   ``writes.WriteSpec.exempt_substring``, whose docstring states the
#:   discipline for the write door one level down: "Compared with ``==``
#:   against the entry in the forbidden list -- never as a shape, because a
#:   loose exemption is how a real write hides." A url that merely BEGINS with
#:   the key -- ``.../in/me/edit/intro/../../evil`` -- finds nothing here and
#:   is refused by ``/edit/`` like the rest of the family.
#: * THE EXEMPTION IS PER-SUBSTRING, which is why the value is a substring and
#:   not a ``True``. A url exempted for ``/edit/`` that also contained
#:   ``/delete`` is still refused, by ``/delete``. The check runs INSIDE the
#:   forbidden loop for exactly that reason.
#: * IT BUYS PAST ONE GATE, NEVER BOTH. The url still has to match an anchored
#:   pattern in :data:`_ALLOWED_URL_PATTERNS` afterwards. An entry here is
#:   permission to carry a forbidden substring, not permission to be opened.
#:
#: One entry, and a second is a boundary change rather than a maintenance
#: edit. ``tests/test_readonly.py`` pins the contents.
_FORBIDDEN_SUBSTRING_EXEMPTIONS: dict[str, str] = {
    "https://www.linkedin.com/in/me/edit/intro/": "/edit/",
    # THE MESSAGE COMPOSER, added 2026-08-31 on the operator's ruling. The
    # second entry, and it uses this table for exactly what the table is for:
    # the url is a CONSTANT with no variable part, so an equality key can hold
    # it and ``"/messaging/compose"`` stays on the forbidden tuple, refusing
    # every other spelling in that family as it always did.
    #
    # This is the contrast with ``/feed/update/<urn>/`` one gate up, and the
    # contrast is the reason each was handled the way it was: a url with a
    # variable segment cannot be an equality key, so admitting THAT one cost
    # its forbidden entry, while admitting this one costs nothing.
    "https://www.linkedin.com/messaging/compose/": "/messaging/compose",
}

#: THE SAME EXEMPTION, FOR A URL THAT CANNOT BE AN EQUALITY KEY.
#:
#: WHY THIS TABLE HAD TO EXIST AT ALL. The dict above is an equality test and
#: that is the whole of its discipline. The compose-with-recipient url carries
#: two MEMBER IDS, so there is no constant to key on -- and the alternative
#: precedent is worse: ``/feed/update/<urn>/`` was admitted by REMOVING its
#: substring from the forbidden tuple, which drops the guard for a whole
#: family to admit one member of it. This buys one anchored shape and leaves
#: ``"/messaging/compose"`` on the forbidden tuple, still refusing every other
#: spelling exactly as it did an hour ago.
#:
#: EACH ENTRY IS (PATTERN, THE ONE SUBSTRING IT EXEMPTS), so the per-substring
#: rule survives: a pattern admitted for ``/messaging/compose`` does not also
#: excuse a ``/delete`` that turns up in the same url. And it is ANCHORED at
#: both ends, so it cannot be reached by prefixing or suffixing.
#:
#: ADMITTING ONE IS A BOUNDARY CHANGE. The allowlist below must ALSO match --
#: this table only says which forbidden substring a url may carry, never that
#: the url is permitted.
_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS: tuple[
    tuple[re.Pattern[str], frozenset[str]], ...
] = (
    # THE COMPOSE-WITH-RECIPIENT ADDRESS, admitted 2026-09-03 on the operator's
    # ruling, relayed by the wave lead, and scoped to this one shape.
    #
    # WHAT IT PERMITS: opening a NEW message composer already addressed to one
    # member named by identifier. Nothing else.
    #
    # WHAT IT DOES NOT PERMIT, and each of these is a separate gate that still
    # stands between this url and a message leaving:
    #   * it is a NAVIGATION, which is a read. It types nothing and presses
    #     nothing;
    #   * ``assert_write_url`` is a different, narrower door and is untouched;
    #   * ``writes.PERFORMABLE``, the grant, the confirm token and
    #     ``_recipient_gate`` are all unchanged and all still run.
    #
    # WHY IT IS SAFER THAN THE GAP IT REPLACES. Three sibling spellings were
    # admitted by accident until this morning, and two of them reached
    # ``/messaging/`` -- which LinkedIn redirects into an EXISTING conversation
    # of its own choosing, spending a read receipt on a real person. A NEW
    # compose opens no thread and costs nobody anything.
    #
    # WHY THE SHAPE IS THIS EXACT. It is LinkedIn's own, read off a committed
    # sanitised fixture rather than guessed: the Message button on
    # Who's-Viewed-Me is an anchor carrying ``profileUrn`` and ``recipient``.
    # This admits those TWO parameters, in that order, and nothing else --
    # narrower than the url LinkedIn itself draws, which also carries
    # ``screenContext`` and ``interop``. If those turn out to be load-bearing,
    # that is a measurement and then a second deliberate entry, not a widening
    # of this one.
    (
        re.compile(
            r"^https://www\.linkedin\.com/messaging/compose/"
            r"\?profileUrn=urn%3Ali%3Afsd_profile%3A[A-Za-z0-9_-]{1,64}"
            r"&recipient=[A-Za-z0-9_-]{1,64}$"
        ),
        frozenset({"/messaging/compose"}),
    ),
    # HIS OWN CONNECTIONS LIST, admitted 2026-09-03 on the operator's question
    # -- "why must I supply a profile url; why can this server not find a
    # person in my own network?" -- ruled by the wave lead.
    #
    # A WRITE GUARD WAS MATCHING A READ ADDRESS, which is the whole of the
    # defect. ``/invite`` and ``/connect`` are on the forbidden list to stop
    # this server SENDING invitations. They also catch
    # ``/mynetwork/invite-connect/connections/``, which sends nothing and
    # invites nobody: it is the page listing people he is ALREADY connected
    # to. The substring was doing its job and hitting the wrong url.
    #
    # THIS IS THE FIRST ENTRY THAT NEEDS TWO SUBSTRINGS, and it is why the
    # value became a SET. The address trips ``/invite`` AND ``/connect`` --
    # measured, not assumed -- and a mechanism returning one substring per
    # pattern could only ever excuse half of it. The set is still a CLOSED,
    # WRITTEN ENUMERATION per pattern: no wildcard, and an entry that wanted a
    # third substring would have to say so.
    #
    # WHAT IT UNLOCKS, which is the reason it was asked for. The identifier
    # route needs a surface that draws Message buttons, because that is where
    # ``recipient_id`` comes from. Who's-Viewed-Me was the only such surface
    # this server could read, and it is the wrong one: it lists whoever
    # happened to look, so an authorised target who has not viewed his profile
    # is unreachable and one who has may still carry ``recipient_id: null``
    # when LinkedIn drew no button on that row.
    #
    # WHAT IT DOES NOT ADMIT, and each was measured refusing before and after:
    #   * ``/mynetwork/`` itself, which was put through a written side-effect
    #     ruling on 2026-08-30 and REFUSED because it consumes the pending
    #     invitation badge. Untouched, and this pattern cannot reach it;
    #   * ``/mynetwork/invite-connect/`` and ``.../invitations/`` -- the
    #     invitation surfaces the forbidden substrings exist for;
    #   * any query string. The pattern ends at the optional slash, so
    #     ``?foo=1`` refuses. Nothing builds one, so nothing needs it, and a
    #     query is where a filter that names a person would arrive;
    #   * ``/mynetwork/network-manager/people-follow/following/``, which
    #     carries ``/follow`` and is not excused here.
    #
    # ITS SIDE-EFFECT COST IS NOT YET MEASURED, and that is stated rather than
    # assumed. The argument for admitting it is that a list of EXISTING
    # connections consumes no badge -- but ``/mynetwork/`` was refused on
    # exactly that question, and reasoning is what this wave has been punished
    # for all day. The measurement that would settle it is the one
    # ``CENSUS_SURFACE_COST`` already prescribes for messaging: read the
    # invitation badge through the feed census before and after. Any TOOL
    # built on this url should carry that precondition; the boundary admitting
    # the address does not itself load anything.
    (
        re.compile(
            r"^https://www\.linkedin\.com/mynetwork/invite-connect/"
            r"connections/?$"
        ),
        frozenset({"/invite", "/connect"}),
    ),
)


def _pattern_exempted_substrings(url: str) -> frozenset[str]:
    """The forbidden substrings an anchored pattern lets this url carry.

    SEPARATE FROM THE DICT LOOKUP AND DELIBERATELY SO. The dict is an equality
    test and stays one; this is the narrow extension for urls with a variable
    segment, and keeping them apart means the cheap discipline still covers
    every url that can have it.

    RETURNS A SET, since 2026-09-03, and the singular version was not merely
    inconvenient -- it was WRONG for the first url that needed two. The
    connections list trips ``/invite`` and ``/connect`` together, so a
    mechanism returning one substring per pattern would excuse half of it and
    the url would still refuse, for a reason nothing in the table could state.
    Each entry still ENUMERATES what it excuses; the set adds no wildcard.
    """
    for pattern, substrings in _FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS:
        if pattern.match(url):
            return substrings
    return frozenset()


def assert_read_url(url: str) -> str:
    """Return ``url`` if it is a permitted read surface, else raise.

    Raises:
        WriteAttemptError: the url is not on the allowlist, or contains a
            forbidden substring. Callers must not catch this and continue --
            it means a navigation was attempted that this server has no
            business making.
    """
    if not isinstance(url, str) or not url:
        raise WriteAttemptError("empty navigation target")

    # Whitespace is refused up front, before any pattern sees the string.
    # Python's ``$`` matches before a trailing newline and ``[^#]*`` happily
    # eats a CRLF, so every anchored pattern below would otherwise accept
    # "https://www.linkedin.com/feed/\n" and a query carrying "\r\nHost: ...".
    # No caller can build such a string today; this closes the shape rather
    # than the instance.
    if any(character.isspace() for character in url):
        raise WriteAttemptError(
            f"navigation blocked: {url!r} contains whitespace. A url this "
            "server builds never does, and a newline inside one is how an "
            "anchored pattern is talked past."
        )

    lowered = url.lower()
    # The ONE substring this exact url may carry, or None. A dict lookup is an
    # equality test, which is the whole of the discipline: a url that merely
    # begins with an exempted one matches nothing here. See
    # :data:`_FORBIDDEN_SUBSTRING_EXEMPTIONS`.
    exact = _FORBIDDEN_SUBSTRING_EXEMPTIONS.get(lowered)
    exempted: frozenset[str] = frozenset({exact}) if exact is not None else frozenset()
    if not exempted:
        # THE PATTERN TABLE IS CHECKED SECOND AND AGAINST THE ORIGINAL URL,
        # not the lowered one: the member ids in a compose address are
        # case-sensitive, and lowering them would admit a url this server
        # could never build. The dict keeps its lowered equality test, which
        # is right for a constant.
        exempted = _pattern_exempted_substrings(url)
    for bad in _FORBIDDEN_URL_SUBSTRINGS:
        if bad in lowered:
            # PER-SUBSTRING, so an exemption for /edit/ does not survive a
            # /delete appearing in the same url. The loop continues rather
            # than returning: the remaining substrings still get their say,
            # and the allowlist below still has to admit the url.
            #
            # A SET SINCE 2026-09-03, because the connections list is the
            # first url to trip TWO forbidden substrings at once. Membership
            # replaces equality; what an entry excuses is still enumerated in
            # the table, one substring at a time, and nothing here excuses a
            # substring its pattern did not name.
            if bad in exempted:
                continue
            # WHETHER THE OTHER GATE WOULD HAVE REFUSED IT TOO, and this
            # clause exists because its absence MISLED THREE READERS.
            #
            # This loop runs FIRST, so a refusal from here names the substring
            # and stops -- and a reader takes the substring for the wall. It
            # is usually not the wall. Every address measured on 2026-09-04
            # that tripped a forbidden substring ALSO had no pattern admitting
            # it, so narrowing the substring would have freed nothing.
            #
            # THE THREE READERS, because a defect that misled one reader is an
            # anecdote and three is a property of the message: the blockers
            # ledger's section 2 filed `/invite` and `/follow` as the blocker
            # for rows they do not gate; a measurement wave reported the same
            # two as "the defect" the next morning; and the team lead relayed
            # that upward as an instruction to narrow the guards. All three
            # were reading a refusal that told them half of what it knew.
            #
            # IT ADDS INFORMATION AND REMOVES NO REFUSAL. The raise is
            # unconditional either way; only the sentence differs.
            #
            # THE WORDING IS CONSTRAINED, and deliberately so. Two tests tell
            # the two gates apart BY THE MESSAGE --
            # `test_readonly.py` asserts "not a read surface" is present here
            # and that the allowlist's own sentence is ABSENT. So this clause
            # must not borrow that sentence's words, and it does not.
            admitted = any(
                pattern.match(url) for pattern in _ALLOWED_URL_PATTERNS
            )
            second_gate = (
                "A READ PATTERN DOES ADMIT THIS ADDRESS, so this substring is "
                "the ONLY thing refusing it -- the refusal is a decision "
                "about the substring rather than about the address."
                if admitted
                else "AND NO READ PATTERN ADMITS THIS ADDRESS EITHER, so "
                "removing this substring would not make it readable. Both "
                "gates refuse it, and the substring is merely the first."
            )
            raise WriteAttemptError(
                f"navigation blocked: {url!r} contains {bad!r}, which is not a "
                "read surface. This is the READ door and it refuses; a write "
                "goes through assert_write_url, which is narrower still. If "
                f"you reached this, a url was built wrong. {second_gate}"
            )

    for pattern in _ALLOWED_URL_PATTERNS:
        if pattern.match(url):
            return url

    raise WriteAttemptError(
        f"navigation blocked: {url!r} is not on the read-only allowlist. "
        "Add a pattern to readonly._ALLOWED_URL_PATTERNS only if the target "
        "is genuinely a page that displays the operator's own data."
    )


def is_read_url(url: str) -> bool:
    """Non-raising form of :func:`assert_read_url`."""
    try:
        assert_read_url(url)
    except WriteAttemptError:
        return False
    return True


# ---------------------------------------------------------------------------
# 2. Source scanner
# ---------------------------------------------------------------------------

#: Playwright (and requests) calls that can change state. Matched against the
#: package source. ``page.goto``, ``page.content``, ``inner_text``, ``locator``
#: and ``request.get`` are all absent from this list on purpose: they read.
_MUTATION_CALL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("click", re.compile(r"\.click\s*\(")),
    ("dblclick", re.compile(r"\.dblclick\s*\(")),
    ("fill", re.compile(r"\.fill\s*\(")),
    ("type_text", re.compile(r"\.type\s*\(")),
    ("press", re.compile(r"\.press\s*\(")),
    ("check", re.compile(r"\.(check|uncheck)\s*\(")),
    ("select_option", re.compile(r"\.select_option\s*\(")),
    ("set_input_files", re.compile(r"\.set_input_files\s*\(")),
    ("drag", re.compile(r"\.drag_to\s*\(")),
    ("tap", re.compile(r"\.tap\s*\(")),
    ("dispatch_event", re.compile(r"\.dispatch_event\s*\(")),
    ("form_submit", re.compile(r"\.(submit|form_submit)\s*\(")),
    ("http_post", re.compile(r"\.(post|put|patch|delete|fetch)\s*\(")),
    ("keyboard", re.compile(r"\.keyboard\b")),
    ("mouse", re.compile(r"\.mouse\b")),
    # evaluate() runs code inside the page and COULD mutate. The handful of
    # read-only harvesters in dom.py waive it with a trailing
    # ``# readonly-ok``, which means any NEW evaluate call fails this check
    # until somebody deliberately waives it in a reviewable diff.
    ("evaluate", re.compile(r"\.evaluate\w*\s*\(")),
    ("add_init_script", re.compile(r"\.add_init_script\s*\(")),
    ("route", re.compile(r"\.route\s*\(")),
)


#: A line consisting only of a quoted string, optionally with a trailing
#: comma: a token-table entry, never a call.
_BARE_STRING_LINE = re.compile(r"""(['"])(?:(?!\1).)*\1,?""")


def scan_source_for_mutations(source: str) -> list[tuple[int, str, str]]:
    """Return ``(line_number, kind, line)`` for every mutating call found.

    Four kinds of line are skipped, and the first three exist because this
    module's own tables are made of the very strings being hunted, so the
    scanner would otherwise always find itself:

    * comments;
    * ``re.compile(...)`` lines;
    * lines that are nothing but a quoted string (a token-table entry) -- a
      bare literal is data, and data cannot call anything;
    * any line ending in ``# readonly-ok``, so a genuine false positive is
      waived visibly in the diff rather than by quietly weakening a pattern.
    """
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "re.compile(" in stripped:
            continue
        if _BARE_STRING_LINE.fullmatch(stripped):
            continue
        if stripped.endswith("# readonly-ok"):
            continue
        for kind, pattern in _MUTATION_CALL_PATTERNS:
            if pattern.search(line):
                hits.append((lineno, kind, stripped))
                break
    return hits


# ---------------------------------------------------------------------------
# 2a. The one sanctioned mutation, named
# ---------------------------------------------------------------------------

#: THE COMPLETE LIST of mutating calls this package is permitted to contain,
#: as ``(path, function, kind)``. Anything the scanner finds that is not on
#: this list is a defect, and anything on this list that the scanner does NOT
#: find is a stale entry -- ``tests/test_readonly.py`` asserts both directions,
#: so the list cannot rot in either.
#:
#: WHY A LIST AND NOT A RELAXED RULE. The scanner's value is that it is
#: unconditional: it reports every mutating call in the package, INCLUDING the
#: sanctioned one, and it would report a second. Teaching it to ignore clicks
#: in ``writes.py``, or to ignore a line wearing some new waiver comment, would
#: convert a measurement into an opinion -- and the very next click would
#: arrive wearing the same clothes as this one. So the SCAN is untouched and
#: the POLICY is this tuple, which a reviewer reads in full in one breath.
#:
#: THE TRIPLE IS THE POINT, and each of its three parts refuses something real:
#:
#: * the PATH, so a click cannot appear in ``dom.py`` or ``browser.py`` under
#:   this exemption;
#: * the FUNCTION, so a click cannot appear in a helper elsewhere in
#:   ``writes.py`` -- ``perform`` is the only function that redeems a grant --
#:   and attribution is to the INNERMOST enclosing function, so burying one in
#:   a closure inside ``perform`` does not inherit the exemption either;
#: * the KIND, so this entry buys a ``click`` and nothing else. A ``fill`` or
#:   an ``http_post`` inside ``perform`` is refused by the very list that
#:   permits the click.
SANCTIONED_MUTATIONS: tuple[tuple[str, str, str], ...] = (
    ("linkedin_server/writes.py", "perform", "click"),
    # THE SECOND ENTRY, added 2026-08-26, and it is on a READ path -- which is
    # why it is here rather than being waved through. The list is what a
    # reviewer reads, so a click that is not on it does not exist, and one
    # that is on it has to argue for itself in this comment.
    #
    # WHAT IT DOES: activates one of seven named filter pills on the messaging
    # surface. dom.MESSAGING_FILTERS is a CLOSED SET matched before any
    # selector is built, so an arbitrary string can never become a click
    # target. The permission is not "may click on that page", it is "may
    # activate one of these seven pills".
    #
    # WHY A READ PATH MAY CLICK AT ALL. Measured: all six pills are <button>
    # with no href, so the filter surface is not reachable by navigation --
    # established by READING their destinations rather than guessing a
    # ?filter= parameter. A pill SENDS NOTHING and CHANGES NOTHING on
    # LinkedIn's servers; it alters which rows are displayed. Counted by
    # EFFECT rather than by verb, which is how this family classifies
    # everything, a view filter is a read.
    #
    # And the argument that settles it: linkedin_open_messaging ALREADY opens
    # somebody's conversation and may fire a read receipt, and ships with that
    # stated as an accepted cost. Refusing the lesser act while performing the
    # greater one is backwards.
    ("linkedin_server/dom.py", "activate_messaging_filter", "click"),
    # THE THIRD ENTRY, added 2026-09-01, and the FIRST that is not a click.
    # This package typed nothing at all until this line, and that fact was
    # printed in the module docstring above, in server_info, and in four
    # refusal texts. Adding it changes what this server IS, so it argues for
    # itself here at length rather than being waved through.
    #
    # WHAT IT PERMITS: one page.fill, inside writes.perform, draining a queue
    # exactly as the click does. ONE DRAIN POINT IS THE WHOLE DESIGN -- the
    # scanner counts CALL SITES, so a queue keeps the guarantee this list
    # exists to give (there is one place in this package that types, and a
    # reviewer reads it) where a second literal page.fill would create a
    # second place to audit.
    #
    # THE TEXT IS NEVER COMPOSED BY THIS SERVER. It is a slice of the GRANT's
    # canonical target -- the same string the preview printed and the token
    # was minted against -- extracted by writes._text_component_of, which
    # refuses rather than guessing when it cannot split the target. consume()
    # has already refused any token whose target did not match, so the bytes
    # typed are provably the bytes he read. tests/test_typed_bytes.py asserts
    # that identity rather than trusting it.
    #
    # WHAT IT DOES NOT PERMIT, by the triple's own construction: a fill in
    # dom.py or browser.py (the PATH refuses it), a fill in any other function
    # in writes.py including a closure inside perform (the FUNCTION refuses
    # it, since attribution is to the innermost enclosing function), and a
    # type, press, keyboard or http_post anywhere at all (the KIND refuses
    # them -- this entry buys "fill" and nothing else).
    #
    # AND A FILL IS NOT A PUBLISH. Typing into a composer sends nothing; the
    # act that reaches LinkedIn is the click that follows, which is gated
    # separately by writes._publish_submit_gate on a measured transition -- the
    # publish control is drawn DISABLED on an empty composer, so a fill that
    # worked is observable and one that did not is refused.
    ("linkedin_server/writes.py", "perform", "fill"),
    # THE FOURTH ENTRY, added 2026-09-02, and it is the NARROWEST of the four
    # rather than the widest -- which is the argument for it.
    #
    # WHAT IT DOES: chooses one option on one <select> inside the profile
    # editor, matched BY THE OPTION'S OWN RENDERED LABEL.
    #
    # WHY IT IS STRICTLY NARROWER THAN THE FILL ALREADY SANCTIONED. A fill puts
    # an ARBITRARY STRING into a box -- the third entry above spends most of
    # its argument on exactly that, and on the drain point and AST assertion
    # built to bound it. A select_option cannot introduce a string at all. It
    # can only choose something THE PAGE ITSELF ALREADY DEFINED, so the set of
    # reachable outcomes is enumerated by LinkedIn and not by this server or by
    # a caller. A typo in a fill becomes his headline; a typo in a select is a
    # refusal, because no option carries that label.
    #
    # BY LABEL, NEVER BY VALUE AND NEVER BY INDEX -- and this is the half that
    # is a PROPERTY rather than a reassurance.
    #
    # `dom.read_self_owned_editor_values` returns, for a <select>, the OPTION'S
    # RENDERED TEXT. That is the string the preview prints for him, and it is
    # the string `select_option(label=...)` matches. Same string, from the same
    # reader, in BOTH HALVES OF THE TRANSACTION: what he agrees to and what is
    # chosen are not merely intended to correspond, they are the same value
    # read once.
    #
    # `value=` would break that. It is a submission token LinkedIn chose, it
    # never appears in anything he read, and no comparison could tie it back to
    # his consent. An index is worse still -- position-aiming, which is the
    # defect the container measurement was taken to end.
    #
    # AND THE CONTROL IS NOT CHOSEN BY THIS SERVER EITHER. `_live_control`
    # reads the editor live, requires EXACTLY ONE control named as asked, and
    # refuses otherwise -- naming what it saw, shaped, because that reader
    # returns accessible names ungated and one control in that editor is named
    # by its own content.
    ("linkedin_server/writes.py", "perform", "select_option"),
    # THE FIFTH ENTRY, added 2026-09-04, AND IT IS THE FIRST THAT REACHES THE
    # OTHER WAY. The four above all act on something ALREADY ON THE PAGE: a
    # control the reader found, a string the operator approved, an option
    # LinkedIn itself drew. This one takes a FILE FROM THIS MACHINE and hands
    # its bytes to a remote party. Nothing in the read-only boundary is about
    # that direction, because until this line nothing went that way -- so this
    # entry argues at more length than the other four, and it should.
    #
    # IT EXISTS BECAUSE THE OPERATOR WAS ASKED AND ANSWERED. The absence of
    # `set_input_files` from this list was not an oversight: it was an OPEN
    # QUESTION, written down as one, carried in
    # `tests/test_readonly.py::test_nothing_in_this_package_can_reach_a_file_
    # input` in the form "the operator has never been asked about it", and
    # counted in `_audit/2026-09-03-linkedin-gap-blockers.md` as the single
    # highest-value blocker in the census -- 16 capability rows, one ruling.
    # He was asked on 2026-09-04 and opened it FULLY: profile photo, post
    # media and message attachments. That test now asserts the opposite of
    # what it used to, by name, which is the correct way for a written
    # question to end.
    #
    # WHAT IT PERMITS: one `page.set_input_files`, inside `writes.perform`,
    # draining a queue exactly as the click, the fill and the select do. ONE
    # DRAIN POINT IS THE WHOLE DESIGN -- the scanner counts CALL SITES, so a
    # queue keeps the guarantee this list exists to give (there is one place
    # in this package that hands a file to a browser, and a reviewer reads it)
    # where a second literal call would create a second place to audit.
    #
    # AND THE SANCTION IS THE EASY HALF. THE PATH STRING IS THE NEW SURFACE.
    # A fill is bounded by the string being a slice of a target the operator
    # read; a PATH is a name for something this server has not seen and he has
    # not read. `linkedin_server/uploads.py` is what bounds it, and no part of
    # it is optional:
    #
    #   A DECLARED ROOT -- `config.UPLOAD_ROOT`, and nothing outside it. An
    #   unbounded path names a private key as readily as a photograph and a
    #   string comparison cannot tell them apart. Putting a file in that
    #   directory is an act the operator performs with his own hands, and it
    #   is the one part of this mechanism a caller cannot fake.
    #
    #   NO SYMLINK ANYWHERE ON THE CHAIN -- a symlink is a path that names one
    #   file and reads another, which defeats every other check by
    #   construction: the name is inside the root, the bytes are not. Checked
    #   per component AND by comparing the real path against the real root,
    #   because a Windows directory junction is not reported as a link.
    #
    #   A REGULAR FILE THAT EXISTS AND CAN BE READ, with a size, refused by
    #   name for each of those rather than as one flat "cannot use that file".
    #
    #   AND THE PATH IS NEVER COMPOSED BY THIS SERVER. It is a component of
    #   the GRANT -- the canonical target the preview printed and the token
    #   was minted against -- taken by `writes._file_component_of`, the third
    #   member of the family `_text_component_of` started. `consume` has
    #   already refused any token whose target did not match.
    #
    # A PATH IS NOT A FILE, WHICH THE GRANT ALONE CANNOT FIX. The token binds
    # the path; whatever sits under that path can change while a grant is
    # live. So the preview reads a sha256 prefix, prints it, and `perform`
    # re-reads it immediately before handing anything over -- a mismatch is a
    # refusal. That is what makes "the bytes uploaded are the bytes he saw" a
    # property rather than a hope.
    #
    # WHAT IT DOES NOT PERMIT, by the triple's own construction: a
    # set_input_files in `dom.py` or `browser.py` (the PATH refuses it), one
    # in any other function in `writes.py` including a closure inside
    # `perform` (the FUNCTION refuses it, since attribution is to the
    # innermost enclosing function), and a click, fill, select, type, press or
    # http_post bought by this line (the KIND refuses them -- this entry buys
    # "set_input_files" and nothing else).
    #
    # AND ATTACHING IS NOT SENDING. Putting a file in a composer dispatches
    # nothing; the act that reaches LinkedIn is the submit that follows, gated
    # separately and after this. The block the operator reads says so in those
    # words, and says the other half too -- that once that submit happens an
    # upload CANNOT BE UN-SENT, because the bytes have left this machine and
    # nothing here can withdraw them.
    #
    # NO ACTION USES IT YET, AND THAT IS DELIBERATE. `writes.UPLOAD_ACTIONS`
    # ships EMPTY: the ruling landed, the mechanism landed, and each of the
    # three composers still needs its own file input measured before it can
    # join. This entry therefore describes a capability that is OPEN and a
    # surface that is not yet wired, which is exactly the state it should
    # describe -- and it means wiring the first one is a one-line diff beside
    # a paragraph explaining what it costs.
    ("linkedin_server/writes.py", "perform", "set_input_files"),
)


def enclosing_function(source: str, lineno: int) -> Optional[str]:
    """Name the INNERMOST function containing ``lineno``, or ``None``.

    Innermost rather than outermost, deliberately: a nested helper is reported
    as ITSELF, so a mutating call hidden one scope down inside a sanctioned
    function does not inherit that function's exemption. Module-level code has
    no enclosing function and comes back ``None``, which no entry in
    :data:`SANCTIONED_MUTATIONS` can match.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    best: Optional[tuple[int, str]] = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = getattr(node, "end_lineno", None)
        if end is None or not node.lineno <= lineno <= end:
            continue
        # Innermost == the enclosing candidate that starts latest.
        if best is None or node.lineno > best[0]:
            best = (node.lineno, node.name)
    return None if best is None else best[1]


def partition_mutation_hits(
    module_path: str, source: str
) -> tuple[list[tuple[int, str, str]], list[tuple[int, str, str]]]:
    """Split one module's scan into ``(sanctioned, unsanctioned)``.

    ``module_path`` is the module's path RELATIVE TO THE REPO ROOT in posix
    spelling -- ``linkedin_server/writes.py``. Relative and normalised because
    an absolute path differs between this machine and each of the three CI
    cells, and an allowlist keyed on something that varies per checkout is an
    allowlist that silently stops matching.

    THE CONSERVATION PROPERTY, which is what makes this safe to introduce at
    all: ``sanctioned + unsanctioned`` is exactly what
    :func:`scan_source_for_mutations` returned, partitioned -- nothing is
    dropped and nothing is invented, so a caller can check the union. A filter
    that quietly consumed a hit would be the same defect as a scanner that
    stopped seeing one.
    """
    sanctioned: list[tuple[int, str, str]] = []
    unsanctioned: list[tuple[int, str, str]] = []
    normalised = str(module_path).replace("\\", "/").lstrip("./")
    for hit in scan_source_for_mutations(source):
        lineno, kind, _line = hit
        function = enclosing_function(source, lineno)
        if (normalised, function, kind) in SANCTIONED_MUTATIONS:
            sanctioned.append(hit)
        else:
            unsanctioned.append(hit)
    return sanctioned, unsanctioned


# ---------------------------------------------------------------------------
# 2b. The injected JavaScript
# ---------------------------------------------------------------------------

#: This server injects a small amount of JavaScript to read the rendered DOM
#: (``dom.py``). Injected code is the one place where "we only call read
#: methods in Python" stops being a sufficient argument, so the JS gets its
#: own scan: any token that could change the page, submit something, or issue
#: a request fails the check.
JS_MUTATION_TOKENS: tuple[str, ...] = (
    ".click(",
    ".submit(",
    ".focus(",
    ".blur(",
    "dispatchEvent",
    "setAttribute",
    "removeAttribute",
    "innerHTML =",
    "outerHTML =",
    ".value =",
    ".remove(",
    "appendChild",
    "insertBefore",
    "replaceChild",
    "fetch(",
    "XMLHttpRequest",
    "navigator.sendBeacon",
    "localStorage.setItem",
    "sessionStorage.setItem",
    "document.cookie =",
    "window.location =",
    "location.href =",
    "history.pushState",
    "eval(",
)


def scan_js_for_mutations(js: str) -> list[str]:
    """Return every mutating token found in an injected script."""
    return [token for token in JS_MUTATION_TOKENS if token in js]


# ---------------------------------------------------------------------------
# 3. Verb list for the tool-surface check
# ---------------------------------------------------------------------------

#: Verbs whose presence in a tool NAME would advertise a mutation.
WRITE_VERBS: tuple[str, ...] = (
    "apply",
    "save",
    "post",
    "send",
    "message",
    "invite",
    "connect",
    "endorse",
    "follow",
    "like",
    "comment",
    "share",
    "delete",
    "remove",
    "update",
    "edit",
    "set",
    "toggle",
    "mark",
    "withdraw",
    "submit",
    "upload",
    "create",
    "add",
    "dismiss",
    "archive",
    "accept",
    "decline",
    # Added 2026-08-23 with the negation prefixes below: without the base verb
    # on this list, "unsubscribe" cannot be reached by stripping "un".
    "subscribe",
    # ADDED 2026-08-30, and it was SHOWN MISSING before it was added: on the
    # day linkedin_react_to_item was registered as a sanctioned write,
    # name_implies_write("linkedin_react_to_item") returned False. A write
    # tool whose name the write-verb guard does not recognise is the exact
    # hole this list exists to close, and it was invisible until a tool wore
    # the verb.
    #
    # MEASURED BEFORE ADDING, because this list feeds the DOCSTRING check too
    # and a verb that is also ordinary prose turns a guard into noise: across
    # every registered tool description, "react" appears as a whole word in
    # exactly ONE -- the tool named for it. Zero false positives.
    "react",
)

#: A THIRD RESIDUE, measured the same day, and the record of what was done
#: INSTEAD of widening this list -- because the first instinct was to widen it
#: and that instinct was wrong.
#:
#: ``linkedin_change_setting`` was registered on 2026-08-30 as a sanctioned
#: write, and ``name_implies_write`` returned False for it: "change" is on no
#: list. The obvious fix was to add "change" here. MEASURED FIRST: across every
#: registered tool description, "change" appears as a whole word in SIX, and
#: three of those are READS using it to describe the boundary ("has no way to
#: change anything about the posting"). Adding it would have fired the
#: DOCSTRING check -- which shares this list -- on three tools behaving
#: correctly, and a guard that cries wolf is a guard somebody switches off.
#:
#: SO THE TOOL WAS RENAMED INSTEAD, to ``linkedin_update_setting``. "update" is
#: already here, it is on the frozen conservation baseline in test_writes.py,
#: and the new name announces the write that the old one concealed. That is
#: the OPPOSITE of the rename loophole
#: ``test_a_sanctioned_write_cannot_evade_the_law_by_being_renamed`` exists to
#: close: that one is renaming so a write passes as a read, this is renaming so
#: a write stops passing as one. The guard found an under-declaring name and
#: the name was corrected, which is the guard working.
#:
#: The residue that remains is the general one, unchanged: a verb that is also
#: ordinary English cannot join this list while the name check and the
#: docstring check share it. Revisit with a segmenter that tells a verb in a
#: tool NAME from a verb in prose.

#: Prefixes that NEGATE a verb without stopping it being a write.
#:
#: MEASURED 2026-08-23. ``name_implies_write`` split a tool name into segments
#: and looked each up in :data:`WRITE_VERBS`, which holds ``save`` and
#: ``follow`` but held no negated form at all. So every one of these read as
#: NOT-A-WRITE:
#:
#:     linkedin_unsave_job   linkedin_unfollow   linkedin_unlike
#:     linkedin_unsubscribe  linkedin_disconnect
#:
#: **Undoing a write is still a write.** They were caught only because somebody
#: had hand-listed two of them in the tool-surface test's ``FORBIDDEN_TOOLS``,
#: which is the failure this module exists to avoid: a literal list sees the
#: instances someone remembered, and the generalising check cannot see the
#: CLASS.
#:
#: Verified against every live tool when this landed: all five are now caught
#: and NONE of the thirteen read tools became a false positive.
NEGATION_PREFIXES: tuple[str, ...] = ("un", "dis", "de")

#: THE RESIDUE, stated rather than left for someone to rediscover.
#:
#: 1. ``re`` is NOT in the set above, and that is a judgement rather than an
#:    oversight. It would correctly catch ``reset``, ``resend``, ``reapply``,
#:    ``repost`` and ``reconnect`` -- all genuine writes -- but it also turns
#:    ``remark`` into ``re`` + ``mark``, and a guard that cries wolf on an
#:    ordinary English word is a guard somebody switches off. Revisit only with
#:    a real ``re``-prefixed tool to justify it.
#: 2. This rule generalises over NEGATIONS OF KNOWN VERBS, not over unknown
#:    verbs. ``linkedin_boost_profile`` or ``linkedin_publish`` would still
#:    pass, because ``boost`` and ``publish`` are on no list. :data:`WRITE_VERBS`
#:    remains a hand-kept list at its root and the only honest fix for that is
#:    to keep adding to it.


def _segments_that_are_write_verbs(text: str) -> set[str]:
    """Every segment of ``text`` that is a write verb, negated or plain.

    One implementation shared by the name check and the docstring check, so the
    two can never drift into disagreeing about what a write verb is.
    """
    found: set[str] = set()
    for segment in re.split(r"[^a-z]+", text.lower()):
        if not segment:
            continue
        if segment in WRITE_VERBS:
            found.add(segment)
            continue
        for prefix in NEGATION_PREFIXES:
            if segment.startswith(prefix) and segment[len(prefix) :] in WRITE_VERBS:
                found.add(segment)
                break
    return found


def name_implies_write(name: str) -> bool:
    """True if a tool name contains a write verb as a whole word segment.

    A NEGATED write verb counts: ``linkedin_unsave_job`` advertises a mutation
    exactly as loudly as ``linkedin_save_job`` does.
    """
    return bool(_segments_that_are_write_verbs(name))


def iter_write_verbs_in(text: str) -> Iterable[str]:
    """Yield write verbs appearing as whole words in ``text``, negations too."""
    yield from sorted(_segments_that_are_write_verbs(text))


#: Words that turn a write verb into a boundary statement rather than a claim.
#: "has no way to add or remove" is exactly the sentence a read-only tool
#: SHOULD contain, so a docstring check that banned the verbs outright would
#: forbid the clearest possible documentation of the boundary.
_NEGATORS = (
    "no ",
    "not ",
    "never",
    "cannot",
    "can't",
    "without",
    "out of scope",
    "deliberately",
    "nothing",
    "none",
    "does not",
    "do not",
    "did not",
    "rather than",
    "instead of",
    "is not",
    "there is no",
)

#: How far back to look for a negator, in characters.
_NEGATION_WINDOW = 80

#: Every spelling a docstring could make a write claim in: the plain verbs and
#: their negated forms. ``\bsubscribe\b`` does not match inside
#: ``unsubscribe`` -- there is no word boundary between the two halves -- so
#: without this the docstring check carried the same blind spot the NAME check
#: did, and "this tool will unfollow the company" read as a claim about
#: nothing. Sorted longest-first so a negated form is reported as itself rather
#: than as the bare verb hiding inside it.
_CLAIMABLE_VERBS: tuple[str, ...] = tuple(
    sorted(
        set(WRITE_VERBS)
        | {
            prefix + verb
            for verb in WRITE_VERBS
            for prefix in NEGATION_PREFIXES
        },
        key=lambda word: (-len(word), word),
    )
)


def docstring_write_claims(text: str) -> list[tuple[str, str]]:
    """Return ``(verb, context)`` for write verbs used as an AFFIRMATIVE claim.

    A tool docstring may say what the tool cannot do; it may not say it does
    something that changes LinkedIn. Every occurrence of a write verb is
    checked for a negator in the preceding
    :data:`_NEGATION_WINDOW` characters, and only the unnegated ones come
    back.
    """
    lowered = (text or "").lower()
    claims: list[tuple[str, str]] = []
    for verb in _CLAIMABLE_VERBS:
        for match in re.finditer(rf"\b{re.escape(verb)}\b", lowered):
            window_start = max(0, match.start() - _NEGATION_WINDOW)
            window = lowered[window_start : match.start()]
            if any(negator in window for negator in _NEGATORS):
                continue
            context = lowered[window_start : match.end() + 30].strip()
            claims.append((verb, context))
    return claims


# ---------------------------------------------------------------------------
# 4. The launch boundary
# ---------------------------------------------------------------------------

#: The flag NAMES this server may hand Chromium, with their values stripped
#: off. The complete list it actually passes is ``config.LAUNCH_ARGS``; this
#: is the gate that list has to get through, and
#: ``tests/test_launch_boundary.py`` puts it through it.
#:
#: Two flags, and the reason the line is drawn immediately after them:
#:
#: * ``--disable-blink-features=AutomationControlled`` switches off the one
#:   Blink feature that sets ``navigator.webdriver = true``. Without it the
#:   browser announces on every page load that it is automated, and LinkedIn
#:   will not complete a sign-in. It flips one boolean. The browser still
#:   reports the user agent, platform, canvas, font list and timezone of the
#:   Chrome it actually is.
#: * ``--remote-debugging-port`` opens the DevTools port on 127.0.0.1 that
#:   the recovery path attaches to (``cdp_bridge.py``).
#:
#: Anything past those two is a different activity rather than a bigger
#: version of the same one: a stealth plugin, a spoofed user agent or
#: platform, a patched canvas/WebGL/font/audio fingerprint, a proxy,
#: randomised "human-like" delays, a captcha solver. This server does none of
#: them. The check exists because whoever reaches for one will be fixing a
#: real failure at the time, and this boundary should be something they have
#: to raise with the operator rather than something a reviewer has to happen
#: to notice in a diff.
PERMITTED_LAUNCH_FLAGS: tuple[str, ...] = (
    "--disable-blink-features",
    "--remote-debugging-port",
)

#: The only Blink feature that may be switched off. The flag takes a
#: comma-separated LIST and can disable arbitrary web-platform behaviour, so
#: permitting the flag NAME is not enough: this one value is sanctioned, and
#: every other value -- including this one with anything appended to it -- is
#: not.
_PERMITTED_BLINK_FEATURE = "AutomationControlled"


def assert_launch_flags_permitted(args: Iterable[str]) -> None:
    """Return quietly if every launch flag is permitted, else raise.

    Args:
        args: the arguments as handed to Chromium -- ``config.LAUNCH_ARGS``
            in practice. Each entry is ``--name`` or ``--name=value``.

    Raises:
        WriteAttemptError: an argument's name is not in
            :data:`PERMITTED_LAUNCH_FLAGS`, or ``--disable-blink-features``
            carries a value other than ``AutomationControlled``. It is the
            same error the navigation allowlist raises, for the same reason:
            this server was asked to do something it has no business doing,
            and the only correct outcome is a loud stop.
    """
    for arg in args:
        name, _, value = str(arg).partition("=")
        if name not in PERMITTED_LAUNCH_FLAGS:
            raise WriteAttemptError(
                f"launch flag {name!r} is not permitted. This server passes "
                f"exactly {len(PERMITTED_LAUNCH_FLAGS)} Chromium flags -- "
                f"{', '.join(PERMITTED_LAUNCH_FLAGS)} -- and nothing else: "
                "no stealth plugin, no user-agent or platform spoofing, no "
                "fingerprint patching, no proxy, no captcha solver. That is "
                "a deliberate boundary, so widening it is the operator's "
                "call to make and not a code review's."
            )
        if name == "--disable-blink-features" and value != _PERMITTED_BLINK_FEATURE:
            raise WriteAttemptError(
                f"launch flag {name!r} may switch off "
                f"{_PERMITTED_BLINK_FEATURE!r} and nothing else, not "
                f"{value!r}. That one feature is what sets "
                "navigator.webdriver, and turning it off is the difference "
                "between a sign-in completing and being refused; the same "
                "flag can disable arbitrary Blink behaviour, which is a "
                "different thing and needs the operator's say-so, not a "
                "code review's."
            )


def _import_pattern(*packages: str) -> re.Pattern[str]:
    """Compile a pattern matching an import statement for any of ``packages``.

    Anchored to the start of a line under ``re.MULTILINE``, so it fires on
    ``import x`` and on ``from x import y`` and on nothing else. A package
    named in a sentence, a docstring or a comment is prose, and prose is not
    a dependency.
    """
    names = "|".join(re.escape(package) for package in packages)
    return re.compile(rf"^\s*(?:import|from)\s+(?:{names})\b", re.MULTILINE)


#: Anti-detection libraries, matched on the IMPORT LINE ONLY. Pulling one of
#: these in would cross the boundary above in a second way -- not through a
#: flag but through a dependency -- so it gets its own scan, run over every
#: module of this package by ``tests/test_launch_boundary.py``.
#:
#: Anchoring on ``import``/``from`` rather than on a bare substring is
#: load-bearing, not tidiness: this package says out loud, in this very
#: module, that it does not use a stealth plugin and does not spoof a user
#: agent. A substring check would make documenting the boundary impossible,
#: which is a worse outcome than not checking at all.
EVASION_IMPORT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "stealth",
        _import_pattern(
            "playwright_stealth", "selenium_stealth", "puppeteer_stealth"
        ),
    ),
    ("undetected", _import_pattern("undetected_chromedriver")),
    (
        "captcha",
        _import_pattern("twocaptcha", "2captcha", "anticaptcha", "capsolver"),
    ),
    ("useragent_spoofing", _import_pattern("fake_useragent", "user_agents")),
    ("tls_spoofing", _import_pattern("curl_cffi", "tls_client")),
    ("fingerprint", _import_pattern("browserforge", "fingerprint_suite")),
)


def scan_source_for_evasion(source: str) -> list[tuple[int, str, str]]:
    """Return ``(line_number, label, line)`` for every evasion import found.

    Three kinds of line are skipped -- the same three
    :func:`scan_source_for_mutations` skips, and for the same reason, since
    the table above is built out of the very package names being hunted:

    * comments;
    * ``re.compile(...)`` lines;
    * any line ending in ``# readonly-ok``, so a genuine false positive is
      waived visibly in the diff rather than by quietly loosening a pattern.

    The fourth skip in :func:`scan_source_for_mutations` -- a line that is
    nothing but a quoted string -- is not repeated here because it cannot
    matter: these patterns match an import STATEMENT, and a bare literal is
    never one.
    """
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "re.compile(" in stripped:
            continue
        if stripped.endswith("# readonly-ok"):
            continue
        for label, pattern in EVASION_IMPORT_PATTERNS:
            if pattern.search(line):
                hits.append((lineno, label, stripped))
                break
    return hits
