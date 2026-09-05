"""The read-only boundary is frozen ON BEHAVIOUR, not on bytes.

WHAT THIS REPLACES. For most of this wave the rule was "``readonly.py``,
``test_readonly.py`` and ``test_launch_boundary.py`` stay ZERO-LINE DIFFS
against ``oldsha14``". That is a proxy, and on 2026-08-23 the proxy and the
thing it stood for came apart: a real job id and a real vanity slug were
sitting in a comment and in test url data inside those files, and removing them
was a privacy fix that a line count would have refused.

A line count cannot tell an identity swap from a widened allowlist. This can.
What the freeze was ever protecting is that **the navigation allowlist, the
forbidden-substring list, the mutation scanners and the functions around them
do not change** -- so those are what is pinned, by AST, with comments and
string literals in comments contributing nothing.

WHY HASHES AND NOT THE STRUCTURES THEMSELVES. Two reasons, and the second is
the one that bit.

1. The dumps are large and unreadable; a digest fails just as loudly.
2. **The evidence may not depend on git history being present.** An earlier
   guard in this repo proved a point about ``oldsha22`` by running
   ``git show`` -- correct here, where a full clone has the object, and red on
   all three CI cells, where ``actions/checkout`` is SHALLOW. A shallow clone
   is the normal case. So the baseline travels with the test.

RE-DERIVING THE BASELINE, in any full clone::

    git show 7eee070:linkedin_server/readonly.py

and re-run :func:`ast_digest` over it.

THAT COMMAND SAID ``5277dfc`` UNTIL 2026-09-03 AND HAD STOPPED WORKING. A
history rewrite scrubbed a name out of every blob and message, so every commit
kept its subject and author date and took a NEW hash; ``5277dfc`` resolves to
nothing, in this clone and in a fresh one. The instruction this file gives for
checking itself had gone false without anybody editing the line.

**THE REPLACEMENT IS VERIFIED, NOT LOOKED UP.** ``7eee070`` is the live
commit whose subject is "feat(writes): perform() for save_job, and unsave
built but refusing", and the proof that it is the right one is this file's own
instrument: running ``ast_digest`` over ``git show
7eee070:linkedin_server/readonly.py`` reproduces ALL FOUR documented constant
digests exactly -- ``ae3977e43da53d26``, ``0b857f0637cdaaad``,
``23aece1483afdee9``, ``d47e30b67c583c1b`` -- and yields
``<functions> = 9f0a86dafffc2299``, which is the value named four paragraphs
below as the pre-2026-08-24 ``<functions>``. Five independent 64-bit
agreements. A subject could be a coincidence; five digests are not.

AND THE LESSON GENERALISES BEYOND THIS LINE: **cite the SUBJECT first and the
hash second.** A subject survives a rewrite and a hash does not, so a
reference pinned to a hash goes false with nobody editing it. The two
2026-08-24 audit files carry the same correction and a full recovery table.

If a future change to the boundary is
DELIBERATE, update the digests in the same commit that changes the behaviour --
that is the review moment this file exists to create, and it should feel like
one.

IT HAS BEEN ONE FIVE TIMES, and this sentence said "ONCE" until 2026-08-31 --
count rot in the file whose whole job is to notice when something moved, which
is worth correcting here rather than anywhere else. The re-freezes are dated in
the comments on PINNED below; read those for what moved each time. The first is
described next because it is the one that established the format.

On 2026-08-23 the package acquired its first mutating
call and the baseline moved from ``oldsha14`` to "perform() for save_job,
and unsave built but refusing" (``7eee070``; written as ``5277dfc`` before
the rewrite). Two digests moved
and four did not, and the four are the ones that matter: the navigation
allowlist, the forbidden-substring list, the mutation scanner's patterns and
the JS token list are byte-identical across the change. That is asserted below
against the old values rather than left as a claim, because "the write widened
nothing" is exactly the sentence a reader most needs to be able to check.
"""

from __future__ import annotations

import ast
import hashlib
import io
import re
import tokenize
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
READONLY = REPO / "linkedin_server" / "readonly.py"

#: The structures whose meaning IS the read-only guarantee.
#:
#: ``SANCTIONED_MUTATIONS`` JOINED THIS LIST on 2026-08-23, with the write. It
#: is the newest of the five and the only one that GRANTS rather than refuses,
#: which is exactly why it belongs here: the other four are worth freezing
#: because widening them lets something through, and this one is worth freezing
#: because ADDING TO IT lets something through. A boundary made of four
#: denylists and one allowlist is only as frozen as its allowlist.
#:
#: ---------------------------------------------------------------------------
#: THE RE-FREEZE LEDGER FOR THE VALUES BELOW. Entries are dated; the newest is
#: first. Both digest dicts in this file carry the same values, so an entry
#: lives here once rather than being written twice and updated once.
#: ---------------------------------------------------------------------------
#:
#: RE-FROZEN 2026-09-03 A SECOND TIME, by a different wave, AND THIS IS THE
#: FIRST RE-FREEZE IN THIS FILE'S HISTORY WHERE THE MOVING DIGEST IS A DENYLIST
#: GROWING. Every previous one moved the allowlist. Recorded here rather than
#: beside the values because BOTH digest dicts carry it and a ledger entry
#: written twice is a ledger entry that will be updated once.
#:
#:     _FORBIDDEN_URL_SUBSTRINGS  afcb7f0d14c481a0 -> b0291a66ec9bd51e
#:
#:     _ALLOWED_URL_PATTERNS      7696e6f928aee6e2   UNCHANGED
#:     _MUTATION_CALL_PATTERNS    23aece1483afdee9   UNCHANGED
#:     JS_MUTATION_TOKENS         d47e30b67c583c1b   UNCHANGED
#:     SANCTIONED_MUTATIONS       bccb17cef4b986f2   UNCHANGED
#:     <functions>                df57656b3e6e8cf9   UNCHANGED
#:
#: THE DIRECTION: TEN SUBSTRINGS ADDED, NONE REMOVED, NOTHING ELSE MOVED AT
#: ALL. ``<functions>`` unchanged means ``assert_read_url`` is byte-identical
#: across a change that added ten refusals to it -- no gate was taught an
#: exception, no check reordered, no clause relaxed. The whole change is DATA,
#: which is the only shape of boundary change a reviewer can check by reading
#: a list.
#:
#: WHAT MOVED IT. ``_FORBIDDEN_URL_SUBSTRINGS`` documents itself as "a second,
#: independent gate ... belt and braces". Asked MECHANICALLY for the first
#: time -- which addresses does the anchored allowlist refuse ALONE? -- ten
#: came back, including the account's password page and its second
#: authentication factor. NONE WAS EVER REACHABLE. The allowlist held all ten
#: and holds them still; this is a defence-in-depth asymmetry, not an open
#: door, and it is worth saying in that order.
#:
#: AND WHY TEN ENTRIES IS NOT TEN LITERALS. The 2026-08-30 and 2026-08-31
#: entries each closed the surface that had just been found. These close the
#: reason those surfaces were findable: the list was anchored to path
#: spellings on the DESKTOP tree, so a second spelling
#: (``/public-profile/settings``, no trailing slash), a legacy namespace
#: (``/uas/``) or a parallel tree (``/mwlite/``, an entire mobile-web mirror)
#: walked past it. ``tests/test_the_second_gate_covers_the_class.py`` is where
#: that claim is CHECKED rather than made: it puts an address through the real
#: guard for every one of these ten that is not itself one of the ten found,
#: so an entry that closed only its own member goes red there.
#:
#: ZERO CASUALTIES, MEASURED BEFORE APPLIED, in the order the 2026-09-03
#: allowlist re-freeze required rather than trusted: every census surface,
#: every readable setting and every write target rebuilt from its own spec,
#: filtered to those the ANCHORED ALLOWLIST admits, all still open. That check
#: ships in the same file rather than being a sentence here.
#:
#: ONE PART OF THE CLASS IS DELIBERATELY NOT CLOSED and the boundary is honest
#: about it: six of the ten live under ``/mypreferences/d/``, that prefix is
#: the natural close, and it CANNOT be taken -- ``writes.assert_write_url``
#: reads this tuple directly and does not consult
#: ``_FORBIDDEN_SUBSTRING_EXEMPTIONS``, so the prefix would break the only
#: settings write this server ships. Shown, not argued, in
#: ``test_the_subtree_prefix_is_absent_and_the_blocker_is_shown``.
#:
#: VERIFIED UNDER 3.13.14 ONLY, and that is a real gap in this file's own
#: ritual, stated rather than papered over: the box carries one interpreter.
#: What limits the risk is not an argument but the shape of what moved -- a
#: tuple of plain string literals, the class this file's docstring records as
#: matching on EVERY Python through both interpreter splits that killed digest
#: v1 and v2 ("the four CONSTANT digests matching every time because a regex
#: is a string on every Python"). The f-string hazard lives in
#: ``<functions>``, which did not move. The 3.10 cell in CI is the actual
#: verification and it runs on push; if it reds on this digest, that sentence
#: was wrong and this is where to come back to.
#: THE TWO EXEMPTION TABLES WERE ADDED 2026-09-03, AND THE HOLE WAS PROVEN
#: RATHER THAN SUSPECTED.
#:
#: This freeze pinned the DENYLIST and not the door beside it. The two tables
#: that excuse a url FROM the denylist were unpinned, and neither is a
#: function, so a planted exemption moved NOTHING:
#:
#:     plant: one line added to _FORBIDDEN_SUBSTRING_EXEMPTIONS, excusing
#:            "/invite" for /mynetwork/invitation-manager/ -- an address
#:            nobody ruled on and one this file's own MUST_STAY_UNREADABLE
#:            table forbids
#:     result: 0 of 6 digests moved
#:
#: A permission could be granted with zero digest movement, past a guard whose
#: entire purpose is to make a boundary change visible. That is the same shape
#: this package spent 2026-09-03 finding elsewhere -- a check that fires and
#: does not cover what it appears to -- arriving in the instrument that exists
#: to catch exactly this.
#:
#: ADDING THEM IS PURELY ADDITIVE. It can only make the freeze notice more; no
#: existing digest changes meaning, and the four originals are byte-identical
#: across the addition.
PINNED = (
    "_ALLOWED_URL_PATTERNS",
    "_FORBIDDEN_URL_SUBSTRINGS",
    "_FORBIDDEN_SUBSTRING_EXEMPTIONS",
    "_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS",
    "_MUTATION_CALL_PATTERNS",
    "JS_MUTATION_TOKENS",
    "SANCTIONED_MUTATIONS",
)

#: Digests of ``linkedin_server/readonly.py`` at "perform() for save_job, and
#: unsave built but refusing" -- ``7eee070`` today, written as ``5277dfc``
#: before the history rewrite. Subject first, hash second.
#:
#: RE-FROZEN 2026-08-23, DELIBERATELY, and this is the review moment the file's
#: own docstring promised. The previous baseline was ``oldsha14``, the commit
#: the zero-line-diff freeze was declared against, and every digest below moved
#: except one. WHAT CHANGED AND WHY, so a reader does not have to diff two
#: commits to find out:
#:
#: * ``SANCTIONED_MUTATIONS`` is NEW. The package acquired its first mutating
#:   call -- one click, in ``writes.perform`` -- and this is the list that
#:   admits it. It is pinned from birth.
#: * ``<functions>`` MOVED, because ``readonly.py`` gained two:
#:   ``enclosing_function`` and ``partition_mutation_hits``. Neither weakens
#:   anything; the scan itself is byte-for-byte what it was.
#: * ``_ALLOWED_URL_PATTERNS``, ``_FORBIDDEN_URL_SUBSTRINGS``,
#:   ``_MUTATION_CALL_PATTERNS`` and ``JS_MUTATION_TOKENS`` are UNCHANGED, and
#:   that is the load-bearing half of this re-freeze. The write did not widen
#:   the navigation allowlist, did not shorten the forbidden list, did not
#:   remove a detector from the scanner and did not drop a JS token. Their
#:   digests are identical to the ``oldsha14`` values, which are kept below so
#:   the claim is checkable rather than asserted::
#:
#:       _ALLOWED_URL_PATTERNS      ae3977e43da53d26
#:       _FORBIDDEN_URL_SUBSTRINGS  0b857f0637cdaaad
#:       _MUTATION_CALL_PATTERNS    23aece1483afdee9
#:       JS_MUTATION_TOKENS         d47e30b67c583c1b
#:       <functions>                fd79a6a7c02c3e34   (moved)
#:
#: Frozen rather than fetched (CI checks out shallow), and computed from VALUES
#: rather than from ``ast.dump`` output.
#:
#: THREE ATTEMPTS, and the first two failed the same way. v1 hashed
#: ``ast.dump``; v2 hashed a TOKEN STREAM. Both are THE PARSER DESCRIBING
#: ITSELF, and both split along the interpreter matrix -- green on the two
#: 3.13 cells, red on 3.10, with the four CONSTANT digests matching every time
#: because a regex is a string on every Python. v2's failure named its own
#: cause precisely: four of eleven functions differed and every one contained
#: an f-string (PEP 701, 3.12).
#:
#: v3 asks the tokenizer only WHERE THE COMMENTS ARE -- a position question,
#: stable -- and hashes the remaining source text. VERIFIED rather than
#: argued: computed under 3.13.14 and 3.10.19 on the same file, all five
#: digests identical.
#: RE-FROZEN 2026-08-24, and the shape of the move is the argument. A false
#: sentence was removed from ``assert_read_url``'s error message -- it told a
#: live caller "This server has no write path" while three write tools ship.
#: ONLY ``<functions>`` moved (9f0a86dafffc2299 -> 199939f7998e8d48); all four
#: CONSTANT digests are byte-identical across the change, which is what proves
#: the correction touched prose and widened no boundary. Verified under 3.13.14
#: AND 3.10.19 -- a single-version run cannot verify a version-independent
#: claim, and this file has three red CI runs in its history saying so.
#:
#: RENAMED at the same time: the constant was called ...AT_5277DFC while
#: holding a value re-frozen twice since. A name that asserts a provenance it
#: no longer has is the same defect as a docstring that denies a capability
#: that ships, one layer down.
#: RE-FROZEN 2026-09-03, and this entry records a hole in the freeze ITSELF
#: alongside the boundary change that exposed it.
#:
#: WHAT MOVED ON THE BOUNDARY, and it is one address:
#:
#:     _ALLOWED_URL_PATTERNS   7696e6f928aee6e2 -> 97f175ae03ccc7d1
#:     <functions>             df57656b3e6e8cf9 -> 4a6eba4033964196
#:
#: HIS OWN CONNECTIONS LIST is now readable. ``/invite`` and ``/connect`` are
#: on the forbidden list to stop this server SENDING invitations, and they
#: were also catching ``/mynetwork/invite-connect/connections/`` -- a page
#: that sends nothing and invites nobody, listing people he is ALREADY
#: connected to. A write guard matching a read address. The operator asked why
#: this server cannot find a person in his own network; that was the reason.
#:
#: MEASURED BEFORE THE BOUNDARY MOVED, over every linkedin url literal in the
#: package and its tests plus the neighbourhood of the change: 204 addresses
#: compared against the previous implementation, TWO widened (the trailing-
#: slash and slashless spellings of that one page) and ZERO tightened.
#:
#: ``<functions>`` moved because ``_pattern_exempted_substring`` returns a SET
#: now and is renamed to match. That was not a preference: the connections
#: address is the first url to trip TWO forbidden substrings at once, so a
#: mechanism returning one substring per pattern could excuse only half of it.
#: Each entry still ENUMERATES what it excuses.
#:
#: THE FORBIDDEN ROSTER DID NOT MOVE -- b0291a66ec9bd51e before and after.
#: Nothing was shortened to admit this. That is the load-bearing half.
#:
#: AND TWO NAMES JOINED THE FREEZE, WHICH IS THE FINDING WORTH MORE THAN THE
#: FIX. This file pinned the DENYLIST and not the door beside it: the two
#: tables that excuse a url FROM the denylist were unpinned, and one of them
#: is a dict, which ``_literal`` did not handle and rendered as a CONSTANT
#: placeholder. Both were proven by planting an exemption for
#: ``/mynetwork/invitation-manager/`` -- an address MUST_STAY_UNREADABLE
#: forbids -- and watching 0 of 6 digests move, then 0 of 8 after pinning the
#: names, then 1 of 8 once ``_literal`` learned about dicts.
#:
#: **A permission could be granted with zero digest movement, past the guard
#: whose entire purpose is to make a boundary change visible.** Same shape as
#: everything else this package found on 2026-09-03 -- a check that fires and
#: does not cover what it appears to -- arriving in the instrument built to
#: catch exactly that.
#:
#: VERIFIED UNDER 3.13.14 ONLY; the 3.10 cell in CI is the real check. What
#: moved is a tuple of string literals and a dict of them, the class this
#: file records as matching on every Python.
#: RE-FROZEN 2026-09-04, AND EXACTLY ONE DIGEST MOVED:
#:
#:     SANCTIONED_MUTATIONS   bccb17cef4b986f2 -> ab8fdd31f93ef4fc
#:
#: **THE OPERATOR OPENED FILE UPLOAD.** ``set_input_files`` was on
#: ``_MUTATION_CALL_PATTERNS`` and in no sanction, which closed every photo,
#: video, document and attachment path this server could ever take -- 16
#: capability rows, the single highest rows-per-cost item in
#: ``_audit/2026-09-03-linkedin-gap-blockers.md``. That absence was never an
#: oversight: it was an OPEN QUESTION, written down as one in
#: ``tests/test_readonly.py`` in the words "the operator has never been asked
#: about it". He was asked on 2026-09-04 and opened it FULLY -- profile photo,
#: post media and message attachments. The fifth entry is that answer.
#:
#: THE OTHER SEVEN DIGESTS ARE BYTE-IDENTICAL, AND THAT IS THE LOAD-BEARING
#: HALF OF THIS RE-FREEZE. Widening a capability is exactly the moment a
#: boundary quietly loses something else, so what did NOT move is the claim
#: worth checking:
#:
#:     _ALLOWED_URL_PATTERNS                    97f175ae03ccc7d1  unchanged
#:     _FORBIDDEN_URL_SUBSTRINGS                b0291a66ec9bd51e  unchanged
#:     _FORBIDDEN_SUBSTRING_EXEMPTIONS          43e2bf7f3db0dbed  unchanged
#:     _FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS  419e64a3cd92ec7e  unchanged
#:     _MUTATION_CALL_PATTERNS                  23aece1483afdee9  unchanged
#:     JS_MUTATION_TOKENS                       d47e30b67c583c1b  unchanged
#:     <functions>                              4a6eba4033964196  unchanged
#:
#: No navigation address was added, no forbidden substring was dropped, no
#: exemption was widened, NO DETECTOR WAS REMOVED FROM THE SCANNER -- the
#: pattern that finds ``set_input_files`` is the same pattern it was, and it
#: still reports the new call site, which is why
#: ``test_exactly_one_place_in_this_package_can_reach_a_file_input`` can
#: assert there is exactly one. And ``<functions>`` did not move because
#: ``readonly.py`` gained no function and no function body changed: this is a
#: POLICY change of one tuple entry and nothing else in the module.
#:
#: WHERE THE ACTUAL RISK WENT, since it is not in this file. The sanction is
#: one line; the new surface is a PATH STRING, which is the first thing this
#: package has ever taken from a caller and handed to something outside it.
#: What bounds it is ``linkedin_server/uploads.py`` -- a declared root, a
#: refusal on any link along the chain, a regular-file check, and a digest
#: read at preview and re-read at the drain point -- and
#: ``tests/test_uploads.py``, where every one of those is shown firing with a
#: positive control beside it.
#:
#: VERIFIED UNDER 3.13.14 ONLY; the 3.10 cell in CI is the real check. What
#: moved is one entry in a tuple of string literals, the class this file
#: records as matching on every Python.
#: RE-FROZEN AGAIN 2026-09-04, NARROWING WHAT THE ENTRY BELOW ADMITTED:
#:
#:     _ALLOWED_URL_PATTERNS   a334f9fd2683831d -> 3791e30def5f29bc
#:
#: THE FIRST VERSION OF THE INTERESTS ADMISSION WAS TOO WIDE AND THIS RECORDS
#: IT RATHER THAN HIDING IT. `interests` was added as a fourth word to the
#: self-profile details alternation -- whose member segment is
#: `[A-Za-z0-9\-_%]+`, NOT `me`. So for one commit the boundary admitted
#: `/in/<a-third-party>/details/interests/`, MEASURED ALLOWED, on the worst
#: possible surface for that mistake: the Interests tab enumerates the PEOPLE
#: somebody follows, so it would have read a third party's follow graph while
#: announcing to that third party that he looked -- `linkedin_who_viewed_me`
#: establishes the durable viewer record.
#:
#: It is now its own anchored `/in/me/` pattern, NARROWER than its three
#: siblings and matching the intro editor's form, which had already ruled the
#: same question sixteen lines away. Twelve controls, zero mismatches: the
#: `me` form and its tab query admitted; both third-party spellings refused;
#: the three siblings unchanged; `interests/edit/`, `recommendations`,
#: `/groups/` and `/events/` all still refused.
#:
#: EVERY OTHER DIGEST IS AGAIN BYTE-IDENTICAL. A narrowing that touched a
#: denylist or an exemption would show here, and none did.
#:
#: A SEPARATE FINDING, MEASURED AND NOT ACTED ON: the three SIBLINGS are
#: still `[A-Za-z0-9\-_%]+`, so `/in/<a-third-party>/details/skills/` is
#: admitted and always has been. That breadth predates this wave and is
#: recorded in the blockers ledger with its measurement. It is the operator's
#: to rule on; nothing here changes it.
#:
#: RE-FROZEN 2026-09-04, and ONE digest moved:
#:
#:     _ALLOWED_URL_PATTERNS   97f175ae03ccc7d1 -> a334f9fd2683831d
#:
#: THE PROFILE INTERESTS PAGE is now readable. `/in/me/details/interests/`
#: joins the alternation that already held `skills`, `experience` and
#: `education` -- one word, the same page, the same owner, the same shape as
#: three siblings the operator has already argued. `/in/me/` resolves to
#: whoever is signed in, so no third party's page is admitted by this.
#:
#: EVERY OTHER DIGEST IS BYTE-IDENTICAL and that is the substance of the
#: claim, not a formality: `<functions>`, all three denylists, and BOTH
#: exemption tables are unmoved. A read admission that widened a denylist or
#: opened an exemption would show here, and none did.
#:
#: THE SHAPER LANDED FIRST, DELIBERATELY. The Interests tab enumerates FIVE
#: kinds of entity. People and Companies were covered -- the first by every
#: guard in `shape.py`, the second by precedent, since
#: `linkedin_followed_companies` already publishes company names. Groups,
#: Newsletters and Schools had never been asked about, and
#: `scripts/_probe_interests_entity_shaping.py` MEASURED all three shipping a
#: name verbatim past both census guards, with a newsletter also shipping its
#: slug -- routinely its author's name -- on every record. That was fixed in
#: `shape.py` BEFORE this line moved, because a read that is safe only until
#: he follows a person is not safe.
#:
#: VERIFIED UNDER 3.13.14 ONLY; the 3.10 cell in CI is the real check. What
#: moved is one entry in a tuple of string literals -- the class this file
#: records as matching on every Python -- which is the same class of move as
#: the 2026-09-03 connections admission below.
#: RE-FROZEN 2026-09-04 (third time today), AND ONLY `<functions>` MOVED:
#:
#:     <functions>   4a6eba4033964196 -> d7e1d0922e3af446
#:
#: EXACTLY THE SHAPE OF THE 2026-08-24 MOVE RECORDED BELOW, and for the same
#: kind of reason: a sentence in `assert_read_url`'s error message. All four
#: CONSTANT digests are byte-identical -- both denylists, both exemption
#: tables, the pattern list and the mutation tables -- which is what proves the
#: change touched the MESSAGE and widened no boundary.
#:
#: WHAT THE MESSAGE NOW SAYS. The forbidden loop runs FIRST and raised naming
#: only the substring, so a reader took the substring for the wall. It is
#: usually not the wall: the allowlist is closed by default, and every address
#: measured on 2026-09-04 that tripped a forbidden substring ALSO had no
#: pattern admitting it. The refusal now says which case it is.
#:
#: IT MISLED THREE READERS BEFORE IT WAS FIXED -- the blockers ledger's
#: section 2, a measurement wave the next morning, and the team lead relaying
#: that upward as an instruction to narrow the guards. That is why this is a
#: code change and not a note.
#:
#: NO REFUSAL WAS REMOVED. The raise is unconditional either way; only the
#: sentence differs. `tests/test_refusal_names_both_gates.py` proves BOTH
#: branches fire -- the second one by emptying the exemption tables, because
#: the shipped boundary deliberately contains no address that a pattern admits
#: and a substring still refuses.
#:
#: RE-FROZEN 2026-09-04 (fourth today), REDUCING REACH ON AN OPERATOR RULING:
#:
#:     _ALLOWED_URL_PATTERNS   3791e30def5f29bc -> a37487dee3bbcc5f
#:
#: THE SELF-PROFILE DETAIL PAGES ARE NOW `/in/me/` ONLY. That entry took
#: `[A-Za-z0-9\-_%]+` for its member segment, so it admitted ANY member's
#: experience, education and skills pages -- and nobody had ever ruled that.
#: It contradicted two things `readonly.py` says about itself:
#: `known_side_effects` states no tool here loads a third party's profile, and
#: the intro editor is confined to `/in/me/` on the MEASURED ground that
#: loading a third party's profile leaves them a durable record in their own
#: viewer list.
#:
#: RULED ONLY AFTER THE COST WAS MEASURED.
#: `scripts/_probe_details_url_breadth.py` PARSED 55 files and 10854 string
#: literals: 21 literal-me, 10 f-string literal-me, 4 compiled patterns, 8
#: with no member segment, and TWO interpolated sites -- both traced to HIS
#: OWN slug and to the constant `ME = "me"`. The navigation site was checked
#: separately, because a literal census answers what BUILDS a url and not what
#: OPENS one: `linkedin_my_profile` picks its second load from
#: `PROFILE_DETAIL_URLS`, a table of `/in/me/` literals. **Zero callers
#: break.**
#:
#: NOT A NEW RULE -- the code brought into line with a rule the file already
#: states about itself.
#:
#: STILL OPEN AND DELIBERATELY NOT TOUCHED HERE: the entry directly above,
#: `^.../in/[A-Za-z0-9\-_%]+/?$`, admits ANY member's profile page itself. It
#: carries no comment of its own, and the same measurement finds nothing
#: navigating it either. That is the same question one level up and a larger
#: reach than the one just closed; it is recorded rather than ruled.
#:
#: RE-FROZEN 2026-09-04 (fifth today), REDUCING REACH AGAIN AND FOR THE LAST
#: OF THE TWO THAT DISAGREED:
#:
#:     _ALLOWED_URL_PATTERNS   a37487dee3bbcc5f -> 9d21c894b13316f7
#:
#: THE THIRD-PARTY PROFILE PATTERN IS GONE. `^.../in/[A-Za-z0-9\-_%]+/?$`
#: admitted ANY member's profile page, carried no comment of its own, and
#: nothing anywhere recorded a decision to admit it.
#:
#: WHAT DECIDED IT: the allowlist admitted what this server's own
#: documentation says it never does. `known_side_effects` states no tool here
#: loads a third party's profile, and gives the MEASURED reason --
#: `linkedin_who_viewed_me` reads the RECEIVING END of that signal, so such a
#: load leaves a durable record in that person's own viewer list.
#: `PERMANENTLY_FORBIDDEN` names the act. Removing the line makes the boundary
#: say what the server already claims. **Not "nothing uses it, so close it"**
#: -- that argument was considered and rejected as the weaker one.
#:
#: `/in/me/` SURVIVES, CHECKED RATHER THAN ASSUMED: `browser.goto` asserts the
#: REQUESTED url before navigating and never re-checks where it landed, so the
#: redirect from `/in/me/` to his vanity slug does not meet this list.
#: `writes._load` asserts the requested url too, and its `PROFILE_URL` is the
#: `/in/me/` form. Seven controls, zero mismatches.
#:
#: AND IT SURFACED NO STALE FIXTURE -- 498 passed. That is itself the finding,
#: and it CONTRASTS with the sibling narrowing three entries below, which
#: surfaced two tests that had been wrong for a day. Nothing in this suite
#: ever asserted the third-party profile breadth, which is what you would
#: expect of reach nobody ruled and nobody used.
#:
#: RE-FROZEN 2026-09-05, GROWING BY TWO ANCHORED ROOTS:
#:
#:     _ALLOWED_URL_PATTERNS   9d21c894b13316f7 -> 6737b38115e05b1c
#:
#: (RESTORED to the value this entry was COMMITTED with, at 6b5dad5. The
#: working tree had it reading 6f82ef147356ce5d, which is the digest AFTER a
#: THIRD pattern this entry does not describe. See the amendment below: the
#: entry is correct as its author wrote it, and the number belongs to it.)
#:
#: HIS OWN GROUPS AND HIS OWN EVENTS, THE ROOTS ONLY. On the team lead's
#: split: which groups he belongs to is his own data, the same class as his
#: own profile; a group's MEMBER DIRECTORY and an event's ATTENDEE LIST are
#: other people and are admitted nowhere.
#:
#: WHY IT WAS PAID FOR AT ALL, because the previous two attempts at this
#: question were both cheaper and both wrong. ``GROUPS-SURFACE`` (32 census
#: rows) and ``EVENTS-SURFACE`` (18) rest on a precondition nobody had
#: established -- whether he belongs to anything at all -- and 29 of the 32
#: are unreachable in principle if the answer is zero. THREE ROUTES TO THAT
#: ANSWER WERE MEASURED AND ALL THREE ARE DEAD:
#:
#:   * THE ALLOWLIST, the visible gate: 15 Groups/Events addresses, ALLOWED 0,
#:     seven controls passing (``_probe_unmeasured_surface_addresses.py``,
#:     re-run at HEAD rather than relayed).
#:   * THE RENDER, the gate nobody had stated, and the one that kills every
#:     profile-side route: a category's rows are not in the document until its
#:     tab is pressed. PROVEN BY A CONTROL -- the Companies category holds at
#:     least 20 rows (20 and 40 distinct company anchors in the two tracked
#:     manage-Pages fixtures) and renders ZERO on the Interests capture and
#:     ZERO on a live 396909-character profile read.
#:   * THE ADDRESS: ``/in/me/details/interests/`` was admitted on 2026-09-04
#:     for exactly this purpose and REDIRECTS, with two same-run siblings as
#:     its control.
#:
#: AND NO OFFLINE ROUTE EXISTS: ``_probe_membership_signal_in_corpus.py``
#: swept 30 documents and 2522736 characters for six group/event route
#: needles and found ZERO, with a must-fire control at 90 and a
#: must-stay-silent control at 0. That instrument was shown failing four ways
#: before it was believed -- see ``_audit/_scratch/_redproof-corpus-sweep.txt``.
#:
#: EVERY OTHER DIGEST IS BYTE-IDENTICAL, and that is the load-bearing half.
#: ``<functions>`` did not move, so ``assert_read_url`` and every other gate
#: function is unchanged; no denylist shortened; neither exemption table was
#: touched. The change is two tuple entries and the comments around them.
#:
#: WHAT THE WIDENING DELIBERATELY DID NOT BUY, asserted in
#: ``tests/test_readonly.py`` rather than promised here: the group feed, the
#: member roster (census row N 165), the join-request queue, group discovery,
#: an event page (N 184), event comments (C 92), the attendee list (N 188,
#: N 189), and both search verticals. A query string on either root refuses
#: too.
#:
#: ONE DISCLOSURE THAT BELONGS WITH THIS ENTRY RATHER THAN BURIED IN A TEST.
#: ``/groups/<id>/invite/`` is refused TWICE -- ``/invite`` fires AND no
#: pattern matches. **The member roster is refused ONCE.** It carries no
#: forbidden substring at all, so the anchor on the entry above is the only
#: thing between this server and a list of people who did not choose to be
#: enumerated by him. ``test_the_member_roster_is_refused_by_ONE_gate_and_the
#: _count_is_the_point`` asserts the count, and a companion test plants the
#: wildcard a future reader is most likely to write and shows the roster
#: falling out of it.
#:
#: ------------------------------------------------------------------------
#: A THIRD ROOT, 2026-09-05, BY THE SEARCH-APPEARANCES WAVE. THE ENTRY ABOVE
#: IS CORRECT AS ITS AUTHOR WROTE IT AND IS NOT REWRITTEN.
#:
#:     _ALLOWED_URL_PATTERNS   6737b38115e05b1c -> 6f82ef147356ce5d
#:
#: ONE ANCHORED PATTERN:
#:
#:     ^https://www\.linkedin\.com/analytics/search-appearances/?$
#:
#: **AND THE INTERESTING PART IS HOW THIS ENTRY NEARLY DID NOT GET WRITTEN.**
#: At the moment this wave looked, the working tree carried the entry above
#: with its arrow ending at ``6f82ef147356ce5d`` -- the digest INCLUDING this
#: third pattern -- so the record read as though two roots had produced a move
#: that three had. The first diagnosis was that the groups/events wave had
#: frozen a stale reading. **THAT DIAGNOSIS WAS WRONG AND THE COMMIT SAYS SO:**
#: at ``6b5dad5`` the prose and both pinned values all read
#: ``6737b38115e05b1c``, entirely self-consistent, describing exactly the two
#: roots it claims. What had happened since was an UNCOMMITTED re-pin by a
#: third writer -- prose line and both values bumped to match whatever the
#: live tuple hashed to, which by then included this pattern.
#:
#: THE DIAGNOSTIC THAT SETTLED IT IS THE STANDING ONE: date both readings
#: before adjudicating either. ``git show <commit>:<file>`` is the reading
#: with a date on it; the working tree is a reading with none.
#:
#: THE LESSON IS ABOUT THE RE-PIN, NOT ABOUT EITHER WAVE. **Re-pinning a
#: frozen digest to whatever the tree currently hashes to is the one edit this
#: instrument cannot survive.** It turns a freeze into a mirror: the test goes
#: green, and the record of WHAT MOVED -- the only thing a reviewer can
#: actually check -- is silently overwritten with somebody else's change. The
#: entry above was restored to its committed number for that reason, and this
#: entry carries the second leg on its own line, so the two moves stay
#: separately readable and separately attributable.
#:
#: HIS OWN SEARCH-APPEARANCES PAGE. Same class as the two roots above and as
#: ``/analytics/profile-views/`` beside it: his own analytics, no member
#: segment anywhere in the address, so it cannot resolve to anybody but
#: whoever is signed in. It is the reciprocal instrument in the people-search
#: consent question -- ``_audit/2026-09-05-search-results-consent.md`` LOAD A.
#:
#: MEASURED, NOT INFERRED FROM THE TIMELINE, because "it must have been
#: included" is exactly the reasoning this freeze exists to replace. Each of
#: the three 2026-09-05 additions was removed from the SOURCE TEXT IN MEMORY
#: -- ``readonly.py`` was never written -- and the allowlist digest
#: recomputed. A digest that moves when a line is removed is a digest that
#: covers that line::
#:
#:     pinned, and live on disk                     6f82ef147356ce5d
#:     without /analytics/search-appearances/       6737b38115e05b1c   COVERED
#:     without the groups root                      cd3289ecf04a6d0e   COVERED
#:     without the events root                      3593b5d272af55fe   COVERED
#:     CONTROL: without a substring that is absent  6f82ef147356ce5d   0 lines
#:
#: THE CONTROL LINE IS WHY THE OTHER THREE MEAN ANYTHING: a removal that
#: drops no line moves no digest, so the three that DID move, moved because
#: of what was taken out. ``_audit/_scratch/_probe_which_refreeze_carries_my_line.py``
#: and ``_audit/_scratch/_refreeze-attribution.txt``.
#:
#: WHAT MOVED AND WHAT DID NOT. ``_ALLOWED_URL_PATTERNS`` moved, once, by one
#: tuple entry. **EVERY OTHER PINNED DIGEST IS BYTE-IDENTICAL** --
#: ``<functions>`` did not move, so ``assert_read_url`` and every other gate
#: function is unchanged; no denylist was shortened; neither exemption table
#: was touched. This wave added no forbidden substring and removed none: the
#: count was 33 before the edit and 33 after, and all ten candidate addresses
#: were measured REFUSED at HEAD carrying NO forbidden substring at all, so
#: the pattern is the only thing standing between this server and that
#: address.
#:
#: THE TWO PINNED VALUES WERE ALREADY AT ``6f82ef147356ce5d`` IN THE WORKING
#: TREE WHEN THIS WAVE ARRIVED, typed by the third writer described above.
#: They are ADOPTED here rather than retyped, because they are the correct
#: consequence of THIS wave's allowlist entry and this wave owns the change
#: that requires them -- committing the pattern without them would ship a
#: knowingly red boundary invariant, which is worse than adopting three lines.
#: **What is NOT adopted is the prose edit**, which has been put back to the
#: number its own entry was committed with.
#:
#: WHAT THE THIRD ENTRY DELIBERATELY DID NOT BUY, in the same form the entry
#: above uses and asserted in ``tests/test_search_appearances.py`` rather
#: than promised here: the analytics tree root, ``/analytics/creator/``, any
#: sub-path under the search-appearances address, a query string on it, the
#: ``/me/`` spelling (which no measurement says LinkedIn serves), a
#: member-addressed spelling, and -- the one that matters --
#: ``/search/results/people/``, the surface the reading exists to inform,
#: which is still refused.
#:
#: ------------------------------------------------------------------------
#: A FOURTH ROOT, 2026-09-05, BY THE NEWSLETTER-SURFACE WAVE. THE THREE
#: ENTRIES ABOVE ARE CORRECT AS THEIR AUTHORS WROTE THEM AND ARE NOT
#: REWRITTEN.
#:
#:     _ALLOWED_URL_PATTERNS   6f82ef147356ce5d -> a8ea5dcf4f8b3d52
#:
#: ONE ANCHORED PATTERN:
#:
#:     ^https://www\.linkedin\.com/mynetwork/network-manager/newsletters/?$
#:
#: THE NEWSLETTERS HE SUBSCRIBES TO -- the third sibling in the
#: Manage-my-network family, beside the connections list and the Pages list
#: this server has read since 2026-08-23. The full argument is on the entry
#: itself in ``readonly.py``; what belongs here is the attribution and what
#: did not move.
#:
#: THE ADDRESS IS A MEASURED CONSTANT, NOT A GUESS, and it is not this wave's
#: find. ``dom.py``'s invitation-badge aim records the two ``/mynetwork``
#: controls a live feed drew on 2026-09-04, one of which is this address; it
#: was found by an instrument hunting the badge, REJECTED for carrying no
#: label, and left sitting in a docstring and a test for a day. It is also one
#: anchor in the tracked fixture ``tests/fixtures/connections_list.html``, so
#: ``tests/test_newsletter_route.py`` asserts the pattern against a captured
#: document rather than against this paragraph.
#:
#: ATTRIBUTION MEASURED, AND THIS ONE ADMITS OF NO ARGUMENT. The removal
#: control was run in the form the search-appearances entry above established
#: -- drop the line from the SOURCE TEXT IN MEMORY, recompute -- with a
#: variant that handles the multi-line ``re.compile`` construct, since the
#: sibling probe's filter requires the call and the needle on one line::
#:
#:     pinned, and live on disk                     a8ea5dcf4f8b3d52
#:     without the newsletters root                 6f82ef147356ce5d   COVERED
#:     without the Pages sibling                    052961dfb7a8ed83   COVERED
#:     CONTROL: without a needle no line carries    a8ea5dcf4f8b3d52   0 lines
#:
#: **THE TREE MINUS THIS WAVE'S LINE HASHES TO EXACTLY THE PREVIOUSLY PINNED
#: VALUE.** That is stronger than "a digest that moves covers that line": it
#: says this line is the ONLY allowlist change in this tree, so no neighbour's
#: uncommitted work is riding inside this re-pin. The second row is the
#: control that the mechanism can move at all, and the third is the control
#: that a removal dropping no line moves nothing.
#: ``_audit/_scratch/_probe_newsletter_refreeze_attribution.py`` and
#: ``_audit/_scratch/_newsletter-refreeze-attribution.txt``.
#:
#: ONE INTERPRETER, NOT TWO, AND SAYING SO RATHER THAN CLAIMING BOTH. Earlier
#: entries in this file verify each digest under 3.13 AND 3.10 before writing
#: it down. **This box has no 3.10** -- measured: the four sibling venvs under
#: ``mcp-servers/`` are all 3.13.14 and there is no ``py`` launcher -- so the
#: value above is verified under Python 3.13.14 only. The 3.10 cell exists and
#: is CI's (``ubuntu-latest`` x 3.10 in the matrix), so the second reading is
#: available on push and is not available here. A claim of two interpreters
#: would have been the cheapest false sentence in this file.
#:
#: WHAT MOVED AND WHAT DID NOT. ``_ALLOWED_URL_PATTERNS`` moved, once, by one
#: tuple entry. **EVERY OTHER PINNED DIGEST IS BYTE-IDENTICAL** -- seven of
#: eight identical, reported by the failure itself before the re-pin.
#: ``<functions>`` did not move, so ``assert_read_url`` and every other gate
#: function is unchanged; no denylist was shortened; neither exemption table
#: was touched. This wave added no forbidden substring and removed none: 33
#: before and 33 after.
#:
#: AND THE PATTERN IS THE ONLY THING STANDING, which is the disclosure the
#: groups entry established as belonging with a widening rather than buried in
#: a test. ``/mynetwork/network-manager/newsletters/`` carries NO forbidden
#: substring at all -- measured at HEAD by
#: ``scripts/_probe_newsletter_routes.py``, whose control row shows the
#: neighbouring people-follow address refused by ``/follow`` and this one
#: refused by no substring before the pattern existed. So the anchor on this
#: entry is the whole of the narrowness.
#:
#: WHAT THE FOURTH ENTRY DELIBERATELY DID NOT BUY, asserted in
#: ``tests/test_newsletter_route.py`` rather than promised here: one
#: newsletter's own page in either slug form (its slug is ROUTINELY ITS
#: AUTHOR'S NAME), the ``/newsletters/`` product root, per-newsletter
#: analytics, the creator-hub analytics form, a query string on the admitted
#: root, any sub-path under it, and ``/newsletters/create/`` -- which is
#: refused TWICE, by the ``/create`` substring and by no pattern, and which
#: census rows ``M C50`` and ``M C81`` would need.
READONLY_AST_AT_LAST_REFREEZE = {
    "<functions>": "d7e1d0922e3af446",
    "JS_MUTATION_TOKENS": "d47e30b67c583c1b",
    "SANCTIONED_MUTATIONS": "ab8fdd31f93ef4fc",
    "_ALLOWED_URL_PATTERNS": "a8ea5dcf4f8b3d52",
    "_FORBIDDEN_SUBSTRING_EXEMPTIONS": "43e2bf7f3db0dbed",
    "_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS": "419e64a3cd92ec7e",
    "_FORBIDDEN_URL_SUBSTRINGS": "b0291a66ec9bd51e",
    "_MUTATION_CALL_PATTERNS": "23aece1483afdee9",
}

_SUPERSEDED_READONLY_AST_AT_LAST_REFREEZE = {
    # RE-FROZEN 2026-08-26, deliberately, in the commit that moved them.
    #
    # WHAT MOVED AND WHY. The operator ruled that reading his own inbox is his
    # to do, so the blanket "/messaging" denylist entry was NARROWED to
    # "/messaging/compose" -- sending stays impossible -- and the messaging
    # read surface was added to the allowlist. Two structures, two digests,
    # and the other four are byte-identical across the change, which is the
    # evidence that nothing else on the boundary was touched while these were.
    #
    # VERIFIED UNDER BOTH INTERPRETERS before being written down, because a
    # digest that differs by Python version would freeze nothing:
    #     Python 3.13.14  and  Python 3.10.19  ->  identical, all six.
    #
    # BOTH FORMS OF THE MESSAGING URL ARE ON THE ALLOWLIST, and that is not
    # belt-and-braces. Asking for /messaging/ LANDS on /messaging/thread/...:
    # LinkedIn redirects it into a conversation it chooses. Listing only the
    # first would leave the server sitting on a url its own allowlist does not
    # cover -- harmless today because assert_read_url gates the REQUESTED url
    # and never re-checks the landed one, and a trap the moment anyone adds
    # that check.
    #
    # RE-FROZEN AGAIN 2026-08-26, and this is the narrowest move this file has
    # recorded: ONE alternative added to ONE pattern. The jobs-tracker
    # allowlist admitted a THIRD stage, ``?stage=draft`` -- the tab LinkedIn
    # labels "In Progress" -- so that the one row in the operator's tracker
    # became readable at all. The token was READ off LinkedIn's own anchors
    # rather than guessed from the label, and the label and the token differ;
    # the argument in full is on the pattern itself in readonly.py.
    #
    # ONLY THIS DIGEST MOVED, 20224a18ccb46283 -> 6542383b4619c935. The other
    # five are byte-identical across the change, and that is the load-bearing
    # half: admitting a third READ surface did not shorten the forbidden list,
    # did not drop a detector from the scanner, did not lose a JS token and
    # did not sanction a mutation on the way past.
    #
    # VERIFIED UNDER BOTH INTERPRETERS, because a digest that differs by
    # Python version freezes nothing:
    #     Python 3.13.14  and  Python 3.10.19  ->  identical, all six.
    #
    # RE-FROZEN AGAIN 2026-08-30, and this is the first re-freeze where TWO
    # url structures moved at once. They moved in OPPOSITE DIRECTIONS, which
    # is the only reason the pair is one change rather than two:
    #
    #   _ALLOWED_URL_PATTERNS      6542383b4619c935 -> 0edd01ead91a89ea
    #   _FORBIDDEN_URL_SUBSTRINGS  92b02ca73055330f -> fcb931b0eaee5b84
    #
    # * THE ALLOWLIST WIDENED, by exactly one anchored pattern:
    #   ``^https://www\.linkedin\.com/mypreferences/d/?$`` -- the settings
    #   INDEX, no query, no sub-path -- so that
    #   ``linkedin_surface_census(surface="settings")`` can measure it. Every
    #   census surface before this one was already on the allowlist for
    #   another reason; this is the first that was not, and it was admitted
    #   only after a written side-effect ruling
    #   (``_audit/2026-08-30-linkedin-nine.md``): the settings index consumes
    #   no unread badge, emits nothing another person observes, and changes no
    #   value the account holds. /mynetwork/ and messaging were put through
    #   the SAME test on the same day and REFUSED; they are not here.
    # * THE FORBIDDEN LIST NARROWED, by two substrings --
    #   ``/mypreferences/d/categories/`` and ``/psettings/`` -- and it did so
    #   BECAUSE OF the widening. It is documented in readonly.py as a second,
    #   independent gate, and on 2026-08-30 it was measured NOT TO COVER THE
    #   SETTINGS FAMILY AT ALL: ``"/settings/"`` matches neither address
    #   LinkedIn serves. The category pages carry the toggles, and they are
    #   now refused twice rather than once.
    #
    # A DIGEST CANNOT TELL A LIST THAT GREW FROM ONE THAT SHRANK, which is the
    # whole hazard in re-baselining a denylist. So this re-freeze ships with
    # ``test_the_forbidden_list_has_only_ever_grown``, which pins the roster
    # itself and is not retired by the next re-baseline.
    #
    # VERIFIED UNDER 3.13.14. The two that moved are VALUE digests, which this
    # file's ``_literal`` docstring establishes as interpreter-independent (a
    # regex and a string literal are the same on every Python); ``<functions>``
    # -- the one digest that HAS split along the interpreter matrix -- did not
    # move at all here, so the 3.10 cell has nothing new to disagree about. CI
    # runs that cell and is the check.
    #
    # RE-FROZEN AGAIN 2026-08-31, on the operator's ruling that admitted TWO
    # NAMED URLS -- one out of each of two families that stay refused. THREE
    # digests moved and THREE did not:
    #
    #   _ALLOWED_URL_PATTERNS      0edd01ead91a89ea -> 72bc5d4a88b5325b
    #   _FORBIDDEN_URL_SUBSTRINGS  fcb931b0eaee5b84 -> 5e26ec3a8b29c38c
    #   <functions>                199939f7998e8d48 -> eb16cd07f5cf369d
    #
    #   _MUTATION_CALL_PATTERNS    23aece1483afdee9   UNCHANGED
    #   JS_MUTATION_TOKENS         d47e30b67c583c1b   UNCHANGED
    #   SANCTIONED_MUTATIONS       bccb17cef4b986f2   MOVED 2026-09-02 (select_option)
    #
    # A DIGEST CANNOT TELL A LIST THAT GREW FROM ONE THAT SHRANK. That is the
    # whole hazard in re-baselining, it is why the roster tests in
    # test_readonly.py exist, and it is why the direction of each move is
    # written out here rather than left to whoever diffs two commits:
    #
    # * THE ALLOWLIST GREW, by exactly two anchored patterns, and each admits
    #   ONE url rather than a family:
    #     ``^https://www\.linkedin\.com/in/me/edit/intro/?$``
    #     ``^https://www\.linkedin\.com/mypreferences/d/dark-mode/?$``
    #   No pattern was widened, relaxed or removed. The ``/in/me/`` spelling is
    #   the whole of the first permission: no member-slug form was written,
    #   because ``linkedin_who_viewed_me`` has MEASURED that loading a third
    #   party's profile leaves them a durable record.
    # * THE FORBIDDEN LIST ALSO GREW, by two substrings -- ``/close-accounts``
    #   and ``/hibernate-account``. Nothing left it. This is the rarer and more
    #   important half: the settings audit had assumed the two account-ending
    #   pages were covered by ``/mypreferences/d/categories/`` and a live
    #   census that day showed their real addresses contain no ``categories/``
    #   at all, so the only thing that had ever refused them was the anchored
    #   allowlist. So the same commit that widened the allowlist twice also
    #   gave the two most destructive addresses on the account their first
    #   second gate.
    # * ``<functions>`` MOVED because ``assert_read_url`` gained four lines:
    #   an equality lookup into a new EXACT-URL table,
    #   ``_FORBIDDEN_SUBSTRING_EXEMPTIONS``, consulted INSIDE the forbidden
    #   loop so that an exemption is per-substring and buys past one gate
    #   only. Nothing was deleted from that function and no refusal was
    #   loosened.
    #
    # ONE THING THIS RE-FREEZE DOES NOT PIN, stated because the next reader
    # will look for it: ``_FORBIDDEN_SUBSTRING_EXEMPTIONS`` is NOT in
    # ``PINNED``. It GRANTS rather than refuses, which is the property that
    # earned ``SANCTIONED_MUTATIONS`` its place here, so it belongs -- but
    # ``_literal`` above has no ``ast.Dict`` branch and would digest every
    # possible dict as ``['<unhandled>', 'Dict']``, i.e. a pin that cannot
    # fail. Adding it means teaching ``_literal`` to render a dict first. The
    # contents are pinned meanwhile by
    # ``test_the_exemption_table_is_exactly_one_url_for_exactly_one_substring``
    # in test_readonly.py, which asserts the key, the value, and that the
    # exempted substring is really on the forbidden list.
    #
    # VERIFIED UNDER 3.13.14 ONLY -- no 3.10 interpreter is installed on this
    # box, and the previous note's escape hatch does not apply here because
    # ``<functions>`` is exactly the digest that DID move this time. What
    # carries it is construction rather than a second run: ``_function_source``
    # asks the tokenizer only WHERE the comments are, which is a position
    # question and stable, and hashes the remaining source TEXT -- the v3 fix
    # that was measured identical under 3.13.14 and 3.10.19 when it landed.
    # The 3.10 CI cell is the check, and it is the right place for this claim
    # to be settled.
    #
    # RE-FROZEN AGAIN 2026-08-31 (SECOND TIME THAT DAY), on the operator's
    # rulings admitting FOUR MORE NAMED URLS. TWO digests moved and FOUR did
    # not:
    #
    #   _ALLOWED_URL_PATTERNS      72bc5d4a88b5325b -> ea0fe246a3818bb9
    #   _FORBIDDEN_URL_SUBSTRINGS  5e26ec3a8b29c38c -> afcb7f0d14c481a0
    #
    #   _MUTATION_CALL_PATTERNS    23aece1483afdee9   UNCHANGED
    #   JS_MUTATION_TOKENS         d47e30b67c583c1b   UNCHANGED
    #   SANCTIONED_MUTATIONS       bccb17cef4b986f2   MOVED 2026-09-02 (select_option)
    #   <functions>                eb16cd07f5cf369d   UNCHANGED
    #
    # ``<functions>`` NOT MOVING IS THE LOAD-BEARING LINE HERE. Four surfaces
    # were admitted and ``assert_read_url`` is byte-identical: no gate was
    # taught an exception, no check was reordered, no clause was relaxed. The
    # whole change is DATA -- two patterns added, one substring removed, one
    # exemption-table entry added -- which is the only shape of boundary
    # change a reviewer can check by reading a list.
    #
    # AND THE DIRECTION, which is the thing a digest cannot say. For the first
    # time in this file's history the two do not point the same way:
    #
    # * THE ALLOWLIST GREW, by exactly four anchored patterns, each admitting
    #   ONE url or one url shape and never a family:
    #     ``.../feed/update/urn:li:[A-Za-z]+:[0-9]+/?$``  (one item permalink;
    #        the urn shape is dom.ACTIVITY_ITEMS_JS's own, so the only urns
    #        this server can build are the only ones this admits)
    #     ``.../preload/sharebox/?$``                     (the post composer)
    #     ``.../article/new/?$``                          (the article
    #        composer -- both measured as real anchors, count 1 each, before
    #        either was written down)
    #     ``.../messaging/compose/?$``                    (the message
    #        composer)
    #   No existing pattern was widened, relaxed or removed.
    #
    # * THE FORBIDDEN LIST SHRANK, AND THAT HAS NEVER HAPPENED BEFORE. It has
    #   grown at every previous re-freeze and the roster test exists precisely
    #   because a digest cannot tell the two apart. ``"/feed/update"`` was
    #   REMOVED, on the ruling admitting one item permalink per call, and it
    #   could not be kept for a mechanical reason rather than a matter of
    #   appetite: this gate matches SUBSTRINGS and cannot say "the permalink
    #   but nothing beneath it", while the exemption table is keyed on an
    #   EXACT url and the urn varies per call. Neither mechanism can express
    #   the ruling.
    #
    #   WHAT DID NOT GO WITH IT is asserted rather than asserted-in-prose:
    #   ``test_the_removed_substring_did_not_take_the_family_with_it`` in
    #   test_readonly.py puts that family's destructive members through the
    #   real guard and reads back WHICH substring refused each --
    #   ``/edit/``, ``/delete`` and ``action=``, all still present. The
    #   removal is also recorded in
    #   ``FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED`` rather than by deleting
    #   the entry from the roster, because a substring quietly dropped from
    #   the roster is indistinguishable from one that was never on it.
    #
    # * ``/messaging/compose`` WAS NOT REMOVED, and the contrast with the line
    #   above is the reason each was handled the way it was. That composer's
    #   url is a CONSTANT, so an exact-url exemption can hold it and the
    #   substring stays, refusing every other spelling in that family exactly
    #   as before. A url with a variable segment has no such option.
    #
    # RE-FROZEN 2026-09-01, on the operator's ruling admitting ONE more named
    # url. ONE digest moved and FIVE did not:
    #
    #   _ALLOWED_URL_PATTERNS      ea0fe246a3818bb9 -> 6ae718fcbdbfc3ae
    #
    #   _FORBIDDEN_URL_SUBSTRINGS  afcb7f0d14c481a0   UNCHANGED
    #   _MUTATION_CALL_PATTERNS    23aece1483afdee9   UNCHANGED
    #   JS_MUTATION_TOKENS         d47e30b67c583c1b   UNCHANGED
    #   SANCTIONED_MUTATIONS       bccb17cef4b986f2   MOVED 2026-09-02 (select_option)
    #   <functions>                eb16cd07f5cf369d   UNCHANGED
    #
    # THE DIRECTION: THE ALLOWLIST GREW BY ONE ANCHORED PATTERN and nothing
    # else moved at all -- no substring left the forbidden list this time, no
    # gate was reordered, and ``assert_read_url`` is byte-identical again.
    #
    #     ``^https://www\.linkedin\.com/premium/my-premium/?$``
    #
    # WHAT IT BUYS, and it is one question rather than a capability:
    # ``send_message`` may spend a finite InMail credit whose size this server
    # does not know, and a gate that cannot say what an action COSTS is not
    # fully a gate. The composer was captured on 2026-08-31 and does NOT carry
    # a balance -- the control named ``InMail`` there is a conversation-list
    # FILTER PILL with aria-checked=false -- so the balance is either on this
    # page or nowhere, and that is worth knowing whether or not #9 ever ships.
    #
    # IT NAMES NO THIRD PARTY: his own subscription state, found as an
    # ordinary href on his own feed and profile rather than guessed. And
    # ``/premium/`` has purchase and upgrade flows under it, NONE of which is
    # admitted -- the anchoring is the whole of that, and
    # ``tests/test_readonly.py`` puts three of them through the real guard.
    #
    # RE-FROZEN 2026-09-03, AND THIS ONE MOVED IN THE DIRECTION THAT ALMOST
    # NEVER HAPPENS: THE ALLOWLIST GOT NARROWER. Two patterns tightened, none
    # added, nothing removed from any denylist.
    #
    #   _ALLOWED_URL_PATTERNS      6ae718fcbdbfc3ae -> b064768de4ee4036
    #
    # WHAT IT CLOSES. "/messaging/compose" is on the forbidden tuple precisely
    # so a composer cannot be addressed with a recipient, and
    # /messaging/compose/?recipient= duly refused. THREE SIBLING SPELLINGS
    # REACHED THE SAME PLACE AND DID NOT:
    #
    #     /messaging/thread/new/?recipient=<id>
    #     /messaging/?composeTo=<id>
    #     /messaging/?recipient=<id>
    #
    # Neither mechanism was argued; both were inherited. The root pattern took
    # ANY query, and the thread-id class matched the literal `new`, a keyword
    # it was never written for. A ruling that ONE SPELLING CANNOT EXPRESS is
    # not a ruling, it is a spelling filter.
    #
    # CLOSED BY SHAPE, NOT BY BLOCKLIST, deliberately -- naming `new` would be
    # another filter on another spelling. The root now takes no query, and a
    # thread id must START WITH A DIGIT, which every thread id recorded
    # anywhere in this repository does (2-abc, 2-abcdef123456,
    # 2-NjY1ZDkwYWEt==, 2-QUJDREVGSElKS0xNTk9Q==, 4600000042) and which `new`
    # does not.
    #
    # MEASURED BEFORE APPLIED, ZERO CASUALTIES, and the wave lead required
    # that order rather than trusting it: every shipped construction was
    # enumerated FROM THE CODE (config.MESSAGING_URL, navigated once with
    # nothing appended; the census and write templates, both exact) and run
    # through the tightened patterns offline alongside every url
    # tests/test_readonly.py pins as ALLOWED. All still match. A tightening
    # with no casualties is a fact worth stating rather than assuming.
    #
    # THE INVENTORY IS THE RECEIPT. tests/test_messaging_recipient_addressing.py
    # pinned the pre-ruling verdicts, so this change turned it red on exactly
    # the three lines that moved and on the test asserting the two families
    # DIFFERED. Both were updated in the same commit; that file now records one
    # argued admission and three closed accidents.
    "_ALLOWED_URL_PATTERNS": "7696e6f928aee6e2",
    # RE-BASELINED 2026-09-03 by the class close. afcb7f0d14c481a0 ->
    # b0291a66ec9bd51e, ten substrings added and none removed. The full
    # ledger entry is above ``PINNED``; both dicts carry the same value and
    # both moved for the same edit.
    "_FORBIDDEN_URL_SUBSTRINGS": "b0291a66ec9bd51e",
    "_MUTATION_CALL_PATTERNS": "23aece1483afdee9",
    "JS_MUTATION_TOKENS": "d47e30b67c583c1b",
    # RE-FROZEN AGAIN 2026-08-26, and this one moved for a different reason
    # from the pair above it. The allowlist gained its SECOND entry:
    # dom.activate_messaging_filter, a click on a READ path, permitted because
    # the messaging filter pills are buttons with no href (measured) and a
    # filter sends nothing and changes nothing on LinkedIn -- a read by
    # effect. The argument in full is on the entry itself in readonly.py.
    #
    # ONLY THIS DIGEST MOVED. The other five are byte-identical across the
    # change, which is the evidence that sanctioning a new click did not
    # quietly loosen a url list or a mutation pattern on the way past.
    # Verified under Python 3.13.14 and 3.10.19: identical, all six.
    #
    # RE-FROZEN A THIRD TIME, 2026-09-01, and this one is the largest change
    # the allowlist has ever taken: a THIRD entry, and the first that is not a
    # click. ``("linkedin_server/writes.py", "perform", "fill")`` -- one
    # page.fill, draining a queue at a single call site, for the first action
    # in this package that types. The argument in full is on the entry itself.
    #
    # AND ONLY THIS DIGEST MOVED AGAIN, which is the point of freezing them
    # separately and is worth reading carefully here. ``<functions>`` is
    # UNCHANGED at eb16cd07f5cf369d, so ``assert_read_url`` and every other
    # gate function in that module is BYTE-IDENTICAL across the change that
    # taught this package to type. The four denylists are unchanged too.
    #
    # That is the strongest available statement about this commit: permitting
    # a fill widened the ALLOWLIST DATA by one tuple and touched no gate, no
    # url pattern, and no mutation pattern. A change that had loosened any of
    # those on the way past would have moved a second digest, and none moved.
    "SANCTIONED_MUTATIONS": "bccb17cef4b986f2",
    #
    # AND ON 2026-09-03 <functions> MOVED FOR THE FIRST TIME SINCE, which is
    # the loudest thing this file can say and is why it is frozen separately:
    #
    #   <functions>                eb16cd07f5cf369d -> df57656b3e6e8cf9
    #   _ALLOWED_URL_PATTERNS      b064768de4ee4036 -> 7696e6f928aee6e2
    #
    # assert_read_url GAINED FOUR LINES. The exemption lookup was a dict
    # get() on the lowered url and stays one; when it returns None, an
    # ANCHORED PATTERN TABLE is consulted against the ORIGINAL url.
    #
    # WHY A SECOND MECHANISM WAS NEEDED. The compose-with-recipient address
    # carries two MEMBER IDS, so there is no constant to key on. The older
    # precedent for that problem was /feed/update/<urn>/, admitted by REMOVING
    # its substring from the forbidden tuple -- which drops the guard for a
    # whole family in order to admit one member of it. This buys one anchored
    # shape and leaves "/messaging/compose" on the forbidden tuple, refusing
    # every other spelling exactly as before.
    #
    # AGAINST THE ORIGINAL URL, NOT THE LOWERED ONE, and that asymmetry is
    # deliberate: member ids are case-sensitive, and matching a lowered url
    # would admit an address this server could never build.
    #
    # WHAT THE FORBIDDEN ROSTER DID: NOTHING. No substring left it. The
    # allowlist gained ONE anchored pattern, and the exemption table gained
    # ONE anchored entry paired with the single substring it excuses -- so the
    # per-substring rule survives and a /delete appearing in the same url
    # would still refuse.
    #
    # AND IT IS A READ. A navigation types nothing and presses nothing;
    # assert_write_url is a different and narrower door and is byte-identical.
    "<functions>": "df57656b3e6e8cf9",
}

#: The four denylist digests as they stood at ``oldsha14``, kept so that "the
#: write widened nothing" is CHECKABLE rather than a sentence in a comment.
#: ``test_the_write_did_not_touch_any_of_the_four_denylists`` compares them.
DENYLISTS_AT_A76FE32 = {
    # UPDATED 2026-09-03. _ALLOWED_URL_PATTERNS moved for a deliberate READ
    # admission -- his own connections list -- so its value here moves with
    # it, exactly as the 2026-08-26 note below describes for the same reason.
    # The other three are byte-identical and are the ones that would have to
    # move for anything to have been weakened.
    #
    # _FORBIDDEN_SUBSTRING_EXEMPTIONS JOINS THIS DICT, because it is now
    # frozen at all: it is the door beside the denylist, and it did NOT move
    # in this change. A widening that arrived through it would now show up
    # here rather than nowhere.
    # UPDATED AGAIN 2026-09-04, same reason and same shape as the 2026-09-03
    # entry above it: a deliberate READ admission moved this one value. The
    # profile Interests page joined the self-profile details alternation. The
    # other three denylists and the exemption table beside them are
    # byte-identical, which is the whole of what this dict is for.
    # NARROWED 2026-09-04, after the admission above went in too wide for one
    # commit. Same direction as every other move in this dict: a READ
    # admission, and this time a read admission being REDUCED. The three
    # denylists and the exemption table beside them are byte-identical.
    # NARROWED 2026-09-04 on an operator ruling: the self-profile detail
    # pages are `/in/me/` only. REDUCING reach, the first move in this dict's
    # history to go that direction on purpose. Denylists and exemptions
    # byte-identical, as ever.
    # NARROWED AGAIN 2026-09-04: the third-party profile pattern removed. The
    # second reducing move in this dict's history, both on the same day and
    # both on the same measured ground.
    # GREW 2026-09-05 by two anchored roots -- his own groups and his own
    # events, the roots ONLY. Same shape as every other move in this dict: a
    # deliberate READ admission, with the three denylists and the exemption
    # table beside them byte-identical. What is different about this one is
    # WHY it was paid for: three cheaper routes to the same question were
    # measured first and all three are dead, which is written out in full
    # above the dict this one shadows.
    #
    # THAT LINE IS ONE ROOT BEHIND ITS OWN VALUE AND IS LEFT AS ITS AUTHOR
    # WROTE IT. The search-appearances pattern landed the same day and the
    # value above absorbed it without this prose saying so -- which is the
    # narrative-by-deletion hazard the entry above the shadowed dict describes,
    # arriving here as a narrative-by-omission instead. Correcting somebody
    # else's line would be the same overwrite in the other direction, so it
    # stands and this paragraph names the gap.
    #
    # GREW AGAIN 2026-09-05 by ONE anchored root -- the newsletters he
    # subscribes to, the root ONLY. Same shape again: a deliberate READ
    # admission, three denylists and both exemption tables byte-identical,
    # `<functions>` unmoved. Its attribution is the strongest this dict has
    # carried, because the tree MINUS this line hashes to exactly the value
    # this line replaced -- so nothing else is riding inside the re-pin.
    "_ALLOWED_URL_PATTERNS": "a8ea5dcf4f8b3d52",
    "_FORBIDDEN_SUBSTRING_EXEMPTIONS": "43e2bf7f3db0dbed",
    # TWO OF THESE FOUR MOVED ON 2026-08-26 and the values are updated here.
    #
    # This dict answers "did the WRITE widen anything", and the answer is
    # still no -- the write did not touch these. What touched two of them was
    # a separate, later, deliberate boundary change: the operator's ruling on
    # inbox reading. Leaving the old values here would have made this test
    # fail for a change it was never written to police, and updating them
    # without saying so would have quietly retired the check.
    #
    # The name is kept even though the sha no longer describes the contents,
    # because renaming it would break the link to the write it was created
    # for. What it now means: the last values anyone deliberately froze.
    #
    # ONE OF THEM MOVED AGAIN ON 2026-08-26, for a third-stage READ on the
    # jobs tracker (``?stage=draft``). Same reasoning as the entry above it:
    # this dict answers "did the WRITE widen anything", the answer is still
    # no, and what moved the value was a later deliberate boundary change that
    # this check was never written to police. The other three are untouched,
    # which is the half of the sentence worth reading.
    #
    # TWO OF THEM MOVED ON 2026-08-30, for the settings-index census -- the
    # allowlist widened by one anchored pattern and the forbidden list gained
    # two substrings. The reasoning is on the dict above; what belongs HERE is
    # the honest note that this dict is now carrying its third re-baseline and
    # is answering a smaller question each time.
    #
    # THAT EROSION IS WHY THE ROSTER TEST BELOW EXISTS. A dict of digests that
    # gets rewritten whenever the boundary legitimately changes cannot, by
    # itself, distinguish a legitimate change from a weakening -- and the
    # weakening it most needs to catch is a DELETION from the forbidden list,
    # which looks exactly like an addition from here. So the two structures
    # whose direction matters are now ALSO pinned by their contents:
    # ``test_the_forbidden_list_has_only_ever_grown`` and
    # ``test_no_previously_forbidden_address_became_readable``. Those two do
    # not need re-baselining when the boundary grows, only when it shrinks,
    # and a re-baseline of THEM is a much louder edit to have to make.
    #
    # THE SAME TWO MOVED AGAIN ON 2026-08-31, for the two ruled urls. This is
    # the fourth re-baseline of this dict and the question it answers is
    # smaller again; what belongs here is the DIRECTION, which the roster
    # tests now police independently: BOTH LISTS GREW. The allowlist gained
    # two anchored patterns naming two urls, and the forbidden list gained
    # ``/close-accounts`` and ``/hibernate-account``. Nothing left either one.
    # The other two entries are untouched, which is the half of the sentence
    # worth reading.
    #
    # AND THE SAME TWO MOVED AGAIN LATER ON 2026-08-31, for four more ruled
    # urls. Fifth re-baseline, and THE FIRST WHERE THE TWO DIRECTIONS
    # DISAGREE: the allowlist grew by four anchored patterns and the forbidden
    # list SHRANK by one, ``"/feed/update"``. That is the exact move this
    # dict cannot see and the roster tests can, which is why they exist and
    # why the removal had to be written into
    # ``FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED`` -- an edit somebody
    # reviews -- rather than absorbed by re-baking a hash here. The other two
    # entries are untouched.
    #
    # AND THE ALLOWLIST ALONE MOVED AGAIN ON 2026-09-01, for one named
    # subscription page. Sixth re-baseline; the forbidden list did NOT move
    # this time, which is the direction that matters and the one the roster
    # tests police independently.
    #
    # RE-FROZEN 2026-09-03, AND THIS ONE MOVED IN THE DIRECTION THAT ALMOST
    # NEVER HAPPENS: THE ALLOWLIST GOT NARROWER. Two patterns tightened, none
    # added, nothing removed from any denylist.
    #
    #   _ALLOWED_URL_PATTERNS      6ae718fcbdbfc3ae -> b064768de4ee4036
    #
    # WHAT IT CLOSES. "/messaging/compose" is on the forbidden tuple precisely
    # so a composer cannot be addressed with a recipient, and
    # /messaging/compose/?recipient= duly refused. THREE SIBLING SPELLINGS
    # REACHED THE SAME PLACE AND DID NOT:
    #
    #     /messaging/thread/new/?recipient=<id>
    #     /messaging/?composeTo=<id>
    #     /messaging/?recipient=<id>
    #
    # Neither mechanism was argued; both were inherited. The root pattern took
    # ANY query, and the thread-id class matched the literal `new`, a keyword
    # it was never written for. A ruling that ONE SPELLING CANNOT EXPRESS is
    # not a ruling, it is a spelling filter.
    #
    # CLOSED BY SHAPE, NOT BY BLOCKLIST, deliberately -- naming `new` would be
    # another filter on another spelling. The root now takes no query, and a
    # thread id must START WITH A DIGIT, which every thread id recorded
    # anywhere in this repository does (2-abc, 2-abcdef123456,
    # 2-NjY1ZDkwYWEt==, 2-QUJDREVGSElKS0xNTk9Q==, 4600000042) and which `new`
    # does not.
    #
    # MEASURED BEFORE APPLIED, ZERO CASUALTIES, and the wave lead required
    # that order rather than trusting it: every shipped construction was
    # enumerated FROM THE CODE (config.MESSAGING_URL, navigated once with
    # nothing appended; the census and write templates, both exact) and run
    # through the tightened patterns offline alongside every url
    # tests/test_readonly.py pins as ALLOWED. All still match. A tightening
    # with no casualties is a fact worth stating rather than assuming.
    #
    # THE INVENTORY IS THE RECEIPT. tests/test_messaging_recipient_addressing.py
    # pinned the pre-ruling verdicts, so this change turned it red on exactly
    # the three lines that moved and on the test asserting the two families
    # DIFFERED. Both were updated in the same commit; that file now records one
    # argued admission and three closed accidents.
    # RE-BASELINED 2026-09-03 by the class close. afcb7f0d14c481a0 ->
    # b0291a66ec9bd51e, ten substrings added and none removed. The full
    # ledger entry is above ``PINNED``; both dicts carry the same value and
    # both moved for the same edit.
    "_FORBIDDEN_URL_SUBSTRINGS": "b0291a66ec9bd51e",
    "_MUTATION_CALL_PATTERNS": "23aece1483afdee9",
    "JS_MUTATION_TOKENS": "d47e30b67c583c1b",
}

def _literal(node: ast.AST):
    """The VALUE a boundary structure holds, as ordinary Python.

    NOT ``ast.dump``. The first version of this file hashed ``ast.dump``
    output, passed on Python 3.13 and failed on 3.10 -- the dump is a
    SERIALISATION OF THE PARSER'S OWN NODES and its fields move between
    interpreter versions, so it pins the interpreter as much as the code. What
    the freeze is about is the patterns themselves, and a regex is a string on
    every version of Python there has ever been.
    """
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return [_literal(item) for item in node.elts]
    # A DICT, ADDED 2026-09-03, AND ITS ABSENCE WAS NOT COSMETIC. Without this
    # branch a dict fell through to the ``<unhandled>`` placeholder at the
    # bottom, which is CONSTANT whatever the dict holds -- so
    # ``_FORBIDDEN_SUBSTRING_EXEMPTIONS``, the exact-url table that excuses a
    # url from the forbidden list, hashed identically no matter what was in
    # it. Adding the name to :data:`PINNED` bought nothing until this existed:
    # measured by planting an exemption for an address MUST_STAY_UNREADABLE
    # forbids and watching 0 of 8 digests move, twice -- once before the name
    # was pinned and once after.
    #
    # KEYS AND VALUES BOTH, IN SOURCE ORDER. Not sorted: a table whose entries
    # were REORDERED is a table somebody edited, and the freeze exists to make
    # somebody look.
    if isinstance(node, ast.Dict):
        return [
            [_literal(key) if key is not None else "**", _literal(value)]
            for key, value in zip(node.keys, node.values)
        ]
    if isinstance(node, ast.Call):
        func = node.func
        name = (
            f"{getattr(func.value, 'id', '?')}.{func.attr}"
            if isinstance(func, ast.Attribute)
            else getattr(func, "id", "?")
        )
        args = [_literal(a) for a in node.args]
        flags = [ast.unparse(k.value) for k in node.keywords]
        return [name, args, flags]
    if isinstance(node, ast.Attribute):
        return f"{getattr(node.value, 'id', '?')}.{node.attr}"
    if isinstance(node, ast.BinOp):
        return ["binop", _literal(node.left), _literal(node.right)]
    return ["<unhandled>", type(node).__name__]


def _function_source(source: str, node: ast.FunctionDef) -> str:
    """One function's code with comments removed.

    ``tokenize`` is used ONLY to LOCATE comments, never to render structure,
    and that distinction is the whole correction. A ``COMMENT`` is one token on
    every version of Python; how the tokenizer decomposes a STRING is not --
    **PEP 701 splits an f-string into FSTRING_START/MIDDLE/END on 3.12+** where
    3.10 emits a single ``STRING``. ``readonly.py``'s refusal messages are
    f-strings, so a digest built from the token STREAM split exactly along the
    interpreter matrix: four of eleven functions differed, and every one of the
    four contained an f-string.

    Asking the tokenizer WHERE a comment is, is a position question and stable.
    Asking it WHAT a string is made of is a structure question and moved. The
    first two attempts at this digest -- ``ast.dump`` and then the token stream
    -- were both the parser describing ITSELF, which is exactly what the
    ``_literal`` docstring above warns against. The four value digests were
    safe throughout precisely because a regex is a string on every Python.

    ONE DELIBERATE CONSEQUENCE: trailing whitespace is stripped and blank lines
    dropped, so REFORMATTING a function moves the digest where a token stream
    would have ignored it. That is the conservative direction for a boundary
    invariant -- it fires more readily, never less -- and it is chosen rather
    than inherited.
    """
    segment = "".join(
        source.splitlines(keepends=True)[node.lineno - 1 : node.end_lineno]
    )
    spans = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(segment).readline):
            if token.type == tokenize.COMMENT:
                spans.append((token.start, token.end))
    except (tokenize.TokenError, IndentationError):  # pragma: no cover
        pass
    lines = segment.splitlines()
    for (start_row, start_col), (end_row, end_col) in reversed(spans):
        if start_row == end_row and 1 <= start_row <= len(lines):
            lines[start_row - 1] = (
                lines[start_row - 1][:start_col] + lines[start_row - 1][end_col:]
            )
    return "\n".join(
        line for line in (raw.rstrip() for raw in lines) if line.strip()
    )


def ast_digest(source: str) -> dict[str, str]:
    """Name -> digest of its VALUE, plus one digest over every function body.

    Version-independent by construction: every input to a hash below is either
    a string literal out of the source or a token from it. Comments survive
    neither path, so a remark cannot move a digest; a changed regex, a new
    allowlist entry, a deleted forbidden substring or an edited function body
    all do.
    """
    tree = ast.parse(source)
    out: dict[str, str] = {}
    for node in tree.body:
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
        if target in PINNED and node.value is not None:
            rendered = repr(_literal(node.value))
            out[target] = hashlib.sha256(rendered.encode()).hexdigest()[:16]

    functions = {
        node.name: _function_source(source, node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    out["<functions>"] = hashlib.sha256(
        repr(sorted(functions.items())).encode()
    ).hexdigest()[:16]
    return out


def test_the_read_only_boundary_is_where_it_was_re_frozen():
    """THE FREEZE, as the invariant it was always standing in for."""
    live = ast_digest(READONLY.read_text(encoding="ascii"))
    assert live == READONLY_AST_AT_LAST_REFREEZE


def test_the_write_did_not_touch_any_of_the_four_denylists():
    """THE HALF OF THE RE-FREEZE THAT IS A CLAIM ABOUT THE WRITE.

    Re-freezing a boundary is only honest if somebody can see WHAT moved. Two
    digests moved -- a new allowlist, and two new functions. These four did
    not, and they are the four that would have to move for the write to have
    weakened anything: a widened navigation allowlist, a shortened forbidden
    list, a detector removed from the scanner, a JS token dropped.

    Compared against the values from ``oldsha14``, the baseline BEFORE the
    write, so this is a statement about the change and not a restatement of the
    new map.
    """
    live = ast_digest(READONLY.read_text(encoding="ascii"))
    for name, digest in DENYLISTS_AT_A76FE32.items():
        assert live[name] == digest, (
            f"{name} moved across the write. It is one of the four structures "
            "the write was not supposed to touch."
        )



def test_adding_a_second_sanctioned_mutation_moves_the_digest():
    """SHOWN FAILING on the edit this new pin exists to catch.

    The other three weakening cases below delete or widen a REFUSAL. This one
    is the opposite shape and is the reason SANCTIONED_MUTATIONS was pinned at
    all: it grows a PERMISSION. A second entry -- here, a click in dom.py --
    has to move the digest, or the allowlist is frozen in name only.
    """
    source = READONLY.read_text(encoding="ascii")
    widened = source.replace(
        '    ("linkedin_server/writes.py", "perform", "click"),\n',
        '    ("linkedin_server/writes.py", "perform", "click"),\n'
        '    ("linkedin_server/dom.py", "read_job", "click"),\n',
        1,
    )
    assert widened != source, "the edit did not apply"
    assert (
        ast_digest(widened)["SANCTIONED_MUTATIONS"]
        != READONLY_AST_AT_LAST_REFREEZE["SANCTIONED_MUTATIONS"]
    )


def test_every_pinned_structure_was_actually_found():
    """A digest map that silently lost an entry would pass the check above by
    comparing two equally-empty dictionaries."""
    live = ast_digest(READONLY.read_text(encoding="ascii"))
    assert set(live) == set(PINNED) | {"<functions>"}
    assert all(len(digest) == 16 for digest in live.values())


def test_a_comment_or_an_identity_swap_does_not_move_the_digest():
    """The whole reason this replaces a line count.

    Both edits below change the FILE and change nothing a caller can observe:
    a comment, and a job id inside a comment. A zero-line-diff rule refuses
    them; this does not, which is what let the privacy scrub proceed.
    """
    source = READONLY.read_text(encoding="ascii")
    baseline = ast_digest(source)

    commented = source.replace(
        "# ONE job posting, addressed by its numeric id and nothing else.",
        "# ONE job posting. (An added remark, which changes nothing.)",
        1,
    )
    assert commented != source
    assert ast_digest(commented) == baseline

    swapped = re.sub(r"acme-\d{6,}", "acme-4600000099", source, count=1)
    if swapped != source:
        assert ast_digest(swapped) == baseline


@pytest.mark.parametrize(
    "name, edit",
    [
        (
            "_FORBIDDEN_URL_SUBSTRINGS",
            # REPOINTED 2026-08-26. This removed '    "/messaging",' until the
            # blanket entry was narrowed to "/messaging/compose" -- so the edit
            # stopped applying, and the control CAUGHT ITSELF: its
            # `assert weakened != source` refused to run vacuously rather than
            # reporting a pass it had not earned. Exactly what a can-it-fail
            # control is for, and the second one on this repo to do it today.
            lambda s: s.replace('    "/messaging/compose",\n', "", 1),
        ),
        (
            "_ALLOWED_URL_PATTERNS",
            lambda s: s.replace(
                r're.compile(r"^https://www\.linkedin\.com/feed/?$"),',
                r're.compile(r"^https://www\.linkedin\.com/.*$"),',
                1,
            ),
        ),
        (
            "_MUTATION_CALL_PATTERNS",
            lambda s: s.replace('("click", re.compile(r"\\.click\\s*\\(")),', "", 1),
        ),
    ],
)
def test_a_real_weakening_does_move_the_digest(name, edit):
    """SHOWN FAILING, on the three edits that would actually matter: deleting
    a forbidden substring, widening the allowlist to everything on the domain,
    and removing the click detector from the scanner."""
    source = READONLY.read_text(encoding="ascii")
    weakened = edit(source)
    assert weakened != source, f"the edit for {name} did not apply"
    assert ast_digest(weakened)[name] != READONLY_AST_AT_LAST_REFREEZE[name]


def test_the_launch_boundary_is_still_a_zero_line_diff():
    """The one file where a byte-level freeze is still the right instrument.

    Nothing in it names a person, so no privacy fix can ever need to touch it,
    and its subject -- which Chromium flags this server launches -- is a thing
    a diff should be read line by line.
    """
    source = (REPO / "tests" / "test_launch_boundary.py").read_text(encoding="ascii")
    assert "--disable-blink-features=AutomationControlled" in source
    assert source.count("LAUNCH_ARGS") >= 1


def test_a_planted_exemption_moves_a_digest():
    """THE HOLE THIS FREEZE HAD, closed and shown closed.

    Until 2026-09-03 this file pinned the DENYLIST and not the door beside it.
    The two tables that excuse a url FROM the forbidden list were unpinned,
    and ``_FORBIDDEN_SUBSTRING_EXEMPTIONS`` is a dict, which ``_literal`` did
    not handle -- it fell through to the ``<unhandled>`` placeholder, constant
    whatever the dict held. So a permission could be granted with ZERO digest
    movement, past the guard whose entire purpose is to make a boundary change
    visible.

    The plant is not hypothetical: it excuses ``/invite`` for
    ``/mynetwork/invitation-manager/``, an address ``test_readonly``'s
    MUST_STAY_UNREADABLE table forbids by name.

    Measured three times while fixing it -- 0 of 6 digests moved before the
    names were pinned, 0 of 8 after pinning them, 1 of 8 once ``_literal``
    learned about dicts. The first two are why this is a test and not a
    comment.
    """
    source = READONLY.read_text(encoding="ascii")
    anchor = "_FORBIDDEN_SUBSTRING_EXEMPTIONS: dict[str, str] = {"
    assert anchor in source, (
        "the exemption table was renamed or re-typed; this control is aimed "
        "at a declaration that no longer exists and is certifying nothing"
    )
    # THE NEWLINE IS BUILT, NOT TYPED. A shell heredoc collapses a backslash
    # escape, and this repository lost six edits to that on 2026-09-03 alone;
    # chr(10) survives every quoting layer between an author and this file.
    entry = (
        chr(10)
        + '    "https://www.linkedin.com/mynetwork/invitation-manager/":'
        + ' "/invite",'
    )
    planted = source.replace(anchor, anchor + entry, 1)
    assert planted != source

    before = ast_digest(source)
    after = ast_digest(planted)
    moved = {name for name in before if before[name] != after.get(name)}
    assert moved == {"_FORBIDDEN_SUBSTRING_EXEMPTIONS"}, (
        "a planted exemption moved %s. It must move exactly the exemption "
        "table's digest: nothing means the freeze is blind to permissions "
        "again, and more means this plant is changing something else."
        % (sorted(moved) or "NOTHING")
    )


def test_every_pinned_structure_hashes_its_real_content():
    """A PINNED NAME IS NOT A FROZEN STRUCTURE, which is the trap above.

    ``_literal`` returns ``["<unhandled>", ...]`` for node types it does not
    know, and that value is CONSTANT -- so a structure of an unhandled type is
    listed in the freeze, digested, reported, and pinned to nothing at all.
    Adding a name to PINNED bought exactly this until dicts were handled.

    Asserted for every pinned name rather than for the one that was wrong,
    because the next unhandled type will arrive the same way.
    """
    tree = ast.parse(READONLY.read_text(encoding="ascii"))
    seen = set()
    for node in tree.body:
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
        if target in PINNED and node.value is not None:
            seen.add(target)
            rendered = _literal(node.value)
            assert not (
                isinstance(rendered, list)
                and rendered
                and rendered[0] == "<unhandled>"
            ), (
                f"{target} is pinned but _literal cannot render a "
                f"{type(node.value).__name__}, so its digest is a constant "
                "placeholder and freezes nothing"
            )
    assert seen == set(PINNED), sorted(set(PINNED) - seen)
