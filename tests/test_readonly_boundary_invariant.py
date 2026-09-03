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

    git show 5277dfc:linkedin_server/readonly.py

and re-run :func:`ast_digest` over it. If a future change to the boundary is
DELIBERATE, update the digests in the same commit that changes the behaviour --
that is the review moment this file exists to create, and it should feel like
one.

IT HAS BEEN ONE FIVE TIMES, and this sentence said "ONCE" until 2026-08-31 --
count rot in the file whose whole job is to notice when something moved, which
is worth correcting here rather than anywhere else. The re-freezes are dated in
the comments on PINNED below; read those for what moved each time. The first is
described next because it is the one that established the format.

On 2026-08-23 the package acquired its first mutating
call and the baseline moved from ``oldsha14`` to ``5277dfc``. Two digests moved
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
PINNED = (
    "_ALLOWED_URL_PATTERNS",
    "_FORBIDDEN_URL_SUBSTRINGS",
    "_MUTATION_CALL_PATTERNS",
    "JS_MUTATION_TOKENS",
    "SANCTIONED_MUTATIONS",
)

#: Digests of ``linkedin_server/readonly.py`` at ``5277dfc``.
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
READONLY_AST_AT_LAST_REFREEZE = {
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
    "_ALLOWED_URL_PATTERNS": "7696e6f928aee6e2",
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
