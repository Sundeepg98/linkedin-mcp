"""A ``_SANITISERS`` ENTRY IS A CLAIM. THIS IS THE MEASUREMENT BEHIND IT.

``tests/test_navigation_is_never_derived.py`` stops its taint walk at a call
to a function whose NAME is in ``_SANITISERS``. That is the entire test::

    if isinstance(func, ast.Name):
        return func.id in _SANITISERS

**SO THE GUARD TRUSTS AN IDENTIFIER, NOT A CONTRACT**, and this file is the
half that was missing. It was written after a cold verifier measured, by
mutation, what that costs.

## What was measured, 2026-09-04

The verifier took the real source of ``scripts/_probe_job_search_filter_params``
and ran seven versions of it through the guard's own ``output_violations``:

    1  real source, unmodified                             GREEN
    2  the sanitiser's body gutted to ``return url``        GREEN
    3  the sanitiser renamed, body intact                   GREEN
    4  a synthetic module with its own no-op ``_redact``    GREEN
    5  a synthetic module with no sanitiser at all          RED
    6  the sanitiser call DELETED, value emitted anyway     GREEN
    7  arm 6, with that one ``emit(...)`` made ``print(...)``  RED

Arm 2 is why this file exists: **a body that returns its input verbatim passed
the same check that arm 5 failed.** Arm 4 is why the enrolment half exists: any
module may define a function with the name and inherit the trust.

## And the drift was already real when this was written

``test_a_sanitiser_entry_is_a_claim_about_a_contract`` justifies the ``_redact``
entry with "``_redact`` has its own both-directions test file". At that moment
SIX functions across six files claimed a ``_SANITISERS`` name and exactly ONE
of them -- ``scripts/_probe_messaging.py`` -- had that test file. The sentence
was true of one function and false of five. **One function's earned trust was
being spent by five others that merely shared its spelling.**

## The two halves, and neither works alone

* **ENROLMENT.** Every function in the scanned tree whose name is in
  ``_SANITISERS`` must appear in :data:`ENROLLED`. A new claimant fails until
  somebody writes down what it promises. This is what makes the name
  NON-TRANSFERABLE.
* **DEMONSTRATION.** Every enrolled function is run against an adversarial
  table and must change every needle -- and must still DISCRIMINATE, so a
  redactor that returns a constant fails too. Over-redaction is not a pass.

## It is shown failing, which is the register's condition of entry

``test_the_table_would_catch_a_do_nothing_sanitiser`` and
``test_the_table_would_catch_a_constant_returning_sanitiser`` run the SAME
tables through an identity function and a constant function. A check that
cannot fail certifies nothing, and this package has already shipped one of
those.

NO REAL IDENTITY APPEARS HERE. Every needle is invented for its SHAPE and every
one is already sanctioned by ``tests/test_no_committed_identity.py`` -- either
listed in its ``SYNTHETIC_SLUGS`` or carrying one of its ``SYNTHETIC_SLUG_TOKENS``
-- so this file moves no allowlist to exist.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tests.test_navigation_is_never_derived import (  # noqa: E402
    _SANITISERS,
    _python_files,
)

#: How a claimant is CALLED. The two shapes in this package take different
#: arities, and guessing from the signature would be the kind of cleverness
#: that silently calls the wrong thing.
ONE_ARG = "one_arg"
TWO_ARG = "two_arg"

#: **THE ENROLMENT.** ``(filename, function name) -> arity``.
#:
#: A function whose name is in ``_SANITISERS`` and which is NOT here fails
#: :func:`test_every_claimant_of_a_sanitiser_name_is_enrolled`. That is the
#: point: the guard matches by name, so the name has to cost something.
#: THE SEVENTH ENTRY WAS FOUND BY THIS FILE'S FIRST RUN. It did not exist when
#: the list above it was written twenty minutes earlier: another agent added
#: ``_probe_search_render_timeline.py`` with its own ``_redact``, which
#: inherited the guard's trust the moment it was typed. That is the exact event
#: this test was built for, and it happened before the test was committed.
ENROLLED: dict[tuple[str, str], str] = {
    ("_probe_endorse_and_follow_lines.py", "_shape_of"): TWO_ARG,
    ("_probe_free_reads_shapes.py", "_shape_of"): TWO_ARG,
    ("_probe_job_search_filter_params.py", "_shape_of"): TWO_ARG,
    ("_probe_self_details_url.py", "_shape_of"): TWO_ARG,
    ("_probe_unmeasured_surfaces_live.py", "_shape_of"): TWO_ARG,
    ("_probe_messaging.py", "_redact"): ONE_ARG,
    ("_probe_search_render_timeline.py", "_redact"): ONE_ARG,
    # THE EIGHTH, AND IT IS ONE ROW OF FIVE THAT ARE OWED.
    #
    # ``_relation`` was added to ``_SANITISERS`` on 2026-09-05 by `196394d`,
    # which touched five files and NOT this one. Both of this file's
    # enumeration guards went red at that moment, with the two claimants that
    # commit itself introduced. Three more arrived afterwards, this one among
    # them, each inheriting the guard's trust the instant it was typed --
    # **the exact event the paragraph above says this test was built for,
    # happening a second time, to a different sanitiser name.**
    #
    # ONLY THIS ROW IS ADDED HERE, deliberately. The other four belong to
    # `_probe_groups_events_capture.py`, `_probe_groups_events_live.py`,
    # `_probe_compose_file_inputs.py` and `_probe_newsletter_subscriptions_
    # live.py`, and a wave enrolling a neighbour's function would be vouching
    # for a contract it did not write. Enrolment is a CLAIM, not a formality.
    #
    # WHAT MAKES THIS ROW SAFE TO ADD RATHER THAN A GUESS: this copy of
    # ``_relation`` is byte-identical to the ones
    # ``test_every_relation_definition_is_byte_identical`` already governs, so
    # the contract being claimed is one that file already proves. The
    # adversarial table below is what checks it, and it was run against this
    # entry before the entry was committed.
    ("_probe_analytics_controls_live.py", "_relation"): TWO_ARG,
    # ADDED 2026-09-05 by `profile-modals`, for its own file only.
    #
    # NO ORDINAL, DELIBERATELY, and it is a correction to the habit of the
    # rows around it rather than a style choice. This table is append-only and
    # shared: the block below calls itself "THE NINTH AND TENTH", which was
    # true when written and stopped being true the moment this row was
    # inserted above it. An ordinal in a concurrently-appended list is a
    # number that goes stale without anyone editing it -- the same shape as
    # the line-number citations struck out of `server.py` this week. The date
    # and the owner are what a reader actually needs.
    #
    # IT IS HERE BECAUSE THE GUARD ABOVE IT BIT ME FIRST, and the sequence is
    # worth one line: `_probe_profile_modal_presence.py` shipped a DIFFERENT
    # function wearing this name -- four branches, one of them returning a
    # claim about member space that the sanctioned version does not make --
    # and `test_every_relation_definition_is_byte_identical` refused it on the
    # first run. The body is now byte-identical to the copies that test
    # governs, so the contract claimed here is one another file already
    # proves, and the adversarial table below was run against this row before
    # it was committed.
    #
    # I enrol MINE and no one else's. The four rows named above are still
    # their owners' -- enrolment is a claim about a contract, and vouching for
    # a function I did not write is the `_redact` mistake this file exists to
    # stop.
    ("_probe_profile_modal_presence.py", "_relation"): TWO_ARG,
    # THE NINTH AND TENTH, added 2026-09-05 by the groups-surface wave, which
    # is the successor on this surface and is enrolling ITS OWN TWO and no
    # more. The row above declined to enrol these on the correct principle --
    # a wave enrolling a neighbour's function vouches for a contract it did not
    # write -- and that principle cuts the other way too: leaving them
    # unenrolled leaves the guard trusting them BY NAME, which is the exact
    # state `_redact` was in when it turned out to carry no slug rule at all.
    #
    # WHAT MAKES THESE TWO SAFE TO CLAIM RATHER THAN A GUESS, and it is two
    # separate facts, not one restated:
    #
    # 1. ``test_every_relation_definition_is_byte_identical`` in
    #    ``tests/test_navigation_is_never_derived.py`` asserts that every
    #    ``_relation`` body in the tree is ONE body. So the contract claimed
    #    here is the same contract that file's own
    #    ``test_the_relation_sanitiser_cannot_reconstruct_its_input``
    #    exercises across all three branches, against a vanity slug, a urn, a
    #    fifteen-digit run and a thread id.
    # 2. The adversarial table BELOW was run against both rows before they
    #    were committed, and the enrolment machinery was SHOWN FIRING on them:
    #    a deliberately leaky ``_relation`` -- one that interpolates the landed
    #    url into its result -- was planted in the capture probe and this file
    #    failed on it. An enrolment that has only ever been seen passing
    #    certifies nothing, which is this file's own subject.
    #
    # STILL UNENROLLED AND DELIBERATELY LEFT: `_probe_compose_file_inputs.py`,
    # and it is ONE file rather than the two this comment first named.
    # `_probe_newsletter_subscriptions_live.py` was enrolled by its own wave
    # between this wave being told about it and running the check -- **which is
    # why the list was re-measured rather than copied from the message that
    # reported it.** A relayed set of names is a reading with a timestamp the
    # receiver cannot see.
    #
    # The remaining one is not this wave's artifact by any measurement --
    # neither the git history nor the surface -- and the enumeration guard
    # stays red until its owner claims it. **That red is the queue working,
    # not a failure to finish.**
    ("_probe_groups_events_capture.py", "_relation"): TWO_ARG,
    ("_probe_groups_events_live.py", "_relation"): TWO_ARG,
    # THE ELEVENTH, added 2026-09-05 by the newsletter-build wave.
    #
    # IT WAS WRITTEN AS "THE NINTH" AND RENUMBERED, because the groups-surface
    # wave claimed nine and ten in this same file within the same minutes. A
    # duplicate ordinal in a list several waves append to is a hazard rather
    # than an untidiness -- the register carried two sections numbered 8 for
    # exactly this reason a day earlier, and something cited one of them by
    # number.
    #
    # ONE ROW, NOT FOUR. Of the four claimants owed when this was written,
    # groups-surface has since taken its own two. `_probe_compose_file_inputs.py`
    # REMAINS UNENROLLED and is neither wave's, so the enumeration guard above
    # is still red and correctly so. Enrolling a neighbour's function would be
    # vouching for a contract this wave did not write.
    #
    # THE CLAIM BEING MADE, because an enrolment is a claim: this copy of
    # ``_relation`` takes a landed url and an asked-for url and returns the
    # RELATION between them, and no substring of either input survives -- every
    # branch yields a literal or an integer depth taken with ``len``.
    #
    # WHAT MAKES IT SAFE TO ADD RATHER THAN A GUESS, and it is the same
    # argument the eighth row made: this copy is byte-identical to the ones
    # ``test_every_relation_definition_is_byte_identical`` already governs, so
    # the contract is one another file already proves. That is corroboration
    # and NOT the check -- the adversarial table below is the check, and it was
    # run against this entry before the entry was written, in both directions:
    # green as it stands, and RED under a planted mutation that interpolates
    # the landed path into the returned string.
    #
    # THE ENROLMENT GUARD IS AN ENUMERATION GUARD -- it fires on *somebody
    # added a claimant*, which is a condition that does not exist until the
    # claimant is typed. This wave proved earlier the same day that a targeted
    # run cannot reach that class, and then met it from the other side: the
    # probe was written, committed, and the red arrived from a file the wave
    # had never opened. Register 9.5, demonstrated on its own author.
    ("_probe_newsletter_subscriptions_live.py", "_relation"): TWO_ARG,
    ("_probe_premium_collections_live.py", "_relation"): TWO_ARG,
    # THE TWELFTH, AND THE LAST ONE OWED. The `upload-sanction` wave, claiming
    # the file the two comments above named as the remaining unenrolled
    # claimant. With this row the CLAIMANT half of this file's enumeration is
    # whole; the NAME half is not, and is deliberately left -- see below.
    #
    # WHY THIS COPY EXISTS AT ALL, because that is the part an enrolment
    # should have to justify. The probe printed the landed url through a DICT
    # SUBSCRIPT and `tests/test_navigation_is_never_derived.py` PASSED it --
    # measured against a copy of the tree carrying two variants of the same
    # file: the same value, the same line, printed through the bare name is
    # caught and printed through `out['landed']` is not. The taint fixed point
    # follows name bindings and a subscript launders it. Rather than ship
    # through an instrument's blind spot, the probe took the sanctioned route,
    # which is what put a `_relation` in it and this row here.
    #
    # WHAT MAKES THIS SAFE TO CLAIM RATHER THAN A GUESS, and it is the same
    # two facts the rows above rest on, re-measured rather than inherited:
    #
    # 1. This copy was EXTRACTED from `_probe_groups_events_live.py`, never
    #    retyped, so `test_every_relation_definition_is_byte_identical` --
    #    which passed with this file under it, 196 tests -- says the contract
    #    claimed here is the one that file's own three-branch adversarial test
    #    already exercises.
    # 2. THE MACHINERY WAS SHOWN FIRING ON THIS ROW BEFORE THE ROW WAS
    #    COMMITTED, and it took TWO plants, which is the part worth keeping.
    #
    #    THE FIRST PLANT SURVIVED. It leaked in `_relation`'s
    #    `landed == asked` branch, and the table passed. That is a result
    #    about the PLANT and not a hole in the table: that branch is reachable
    #    only when the two strings are EQUAL, at which point the value printed
    #    IS the address this repository asked for -- a constant it authored.
    #    There is nothing there to leak. Enlarging the mutation would have
    #    been the wrong move; the right question was which branch makes the
    #    sanitiser the only thing standing.
    #
    #    THE SECOND PLANT, on the fall-through -- same path depth, different
    #    url, which is reached with a value the SITE chose -- failed the table
    #    by name:
    #
    #        _probe_compose_file_inputs.py::_relation returned its input's
    #        identity (a vanity slug in a member path)
    #
    #    Restored, it passes. An enrolment that has only ever been seen
    #    passing certifies nothing, which is this file's entire subject. Both
    #    plants were made and restored on this one file, which no other wave
    #    writes, and the restore was verified by sha256 rather than assumed.
    #
    # THE NAME PIN IS NOT TOUCHED, DELIBERATELY.
    # `test_the_guarded_names_are_the_ones_this_file_thinks_they_are` is still
    # red because `_SANITISERS` gained `_relation` at `196394d` and this file's
    # expected set did not. Widening that set to clear a red is precisely what
    # the enrolment half exists to prevent -- `_redact` was admitted once on
    # the strength of its name and carried no slug rule at all. That row
    # belongs to whoever moves the name, and the red is the queue working.
    ("_probe_compose_file_inputs.py", "_relation"): TWO_ARG,
    # THE LAST UNENROLLED CLAIMANT, enrolled 2026-09-05 by the successor to the
    # wave that wrote it -- which is the only reason this row is not somebody
    # else's to add. `scripts/_probe_premium_entitlement.py` is `cheap-reads`'
    # tracked probe and this is `cheap-reads-build`, its direct successor,
    # carrying its board.
    #
    # WHY IT WAS MISSED, and it is the same shape as `196394d`: that commit
    # admitted `_relation` to `_SANITISERS` while touching five files, none of
    # them this one, so every claimant born afterwards was trusted BY NAME by a
    # guard that had never measured it. This claimant was born after it. The
    # enumeration half of this file is precisely what catches that, and it
    # cannot be reached by any run scoped to the probe's own file -- it fires
    # on `somebody added a caller`, a condition that does not exist until the
    # caller does.
    #
    # THE BODY WAS CHECKED BEFORE THE ROW WAS ADDED, not after: it is
    # byte-identical to the copies this table already exercises, established
    # by extracting it programmatically and comparing rather than by reading
    # it. The eighth row records a wave that shipped a DIFFERENT body under
    # this name and leaked its input on the first run, so `it is the same
    # function` is a claim that has been wrong here before.
    ("_probe_premium_entitlement.py", "_relation"): TWO_ARG,
    # TWO MORE CLAIMANTS, 2026-09-19, AND THEY ARE MY OWN DEBT. I created both
    # probes earlier today with a byte-identical copy of `_relation`, and in
    # doing so created two claimants of a guarded name that nothing had
    # measured. They were trusted BY SPELLING for several hours. That is the
    # exact event the paragraph above records twice already, committed by
    # somebody who had read it.
    #
    # THE BODIES WERE CHECKED BEFORE THESE ROWS WERE ADDED, not after, and
    # programmatically rather than by reading: both extract byte-identical to
    # the canonical copy in `_probe_groups_events_live.py`, which this table
    # already exercises. The eighth row exists because a wave once shipped a
    # DIFFERENT body under this name, so "it is the same function" is a claim
    # that has been wrong here before and is not taken on sight.
    ("_probe_anchor_surfaces_live.py", "_relation"): TWO_ARG,
    ("_probe_job_collections_live.py", "_relation"): TWO_ARG,
    # NOT ENROLLED, DELIBERATELY: ("_probe_creator_content_analytics.py",
    # "_relation"). It is NOT a copy -- it is a DIFFERENT FUNCTION wearing the
    # name: `_relation(landed)`, one argument, returning AUTH-WALL / target /
    # REDIRECTED-WITHIN-ANALYTICS. Enrolling it would be vouching for a
    # contract I did not write, which this table's own rule forbids, and its
    # arity is not even the one the two-arg invoker would call. It is safe in
    # fact -- every return in it is a string constant, measured off the AST --
    # but that is a measurement somebody else must make into a claim. Its
    # owner is `1f244e1`.
}

#: The address a two-argument claimant is told was ASKED FOR. A constant this
#: repository authored, which is the only kind of url any of these may hold.
REQUESTED = "https://www.linkedin.com/in/me/details/skills/"

#: **INPUTS THAT MUST BE CHANGED, and the needle that must not survive.**
#:
#: Every value is invented and shape-valid. ``some-real-slug-99`` is listed in
#: ``SYNTHETIC_SLUGS``; ``example-placeholder-88`` carries two of the
#: ``SYNTHETIC_SLUG_TOKENS``; the thread blob and the bare name are the shapes
#: ``tests/test_probe_redaction.py`` already committed. A PLACEHOLDER WOULD
#: BREAK THIS -- ``/in/<SLUG>/`` matches no slug rule, so the table would pass
#: against a sanitiser that had lost the rule entirely.
NEEDLED = [
    (
        "https://www.linkedin.com/in/some-real-slug-99/details/skills/",
        "some-real-slug-99",
        "a vanity slug in a member path",
    ),
    (
        "https://www.linkedin.com/in/example-placeholder-88/",
        "example-placeholder-88",
        "a second slug, so one hard-coded string cannot pass this",
    ),
    (
        "https://www.linkedin.com/messaging/thread/2-QUJDREVGSElKS0xNTk9Q==/",
        "QUJDREVGSElKS0xNTk9Q",
        "a base64-padded thread id",
    ),
    (
        "https://www.linkedin.com/in/some-real-slug-99/?trk=Jane%20Q%20Public",
        "some-real-slug-99",
        "a slug beside a query, so the query is not the only thing read",
    ),
]

#: **PAIRS THAT MUST NOT COME BACK THE SAME.** A sanitiser that returns a
#: constant passes every leak test above while reporting nothing, which is the
#: failure mode the messaging redactor was measured making twice while it was
#: being written.
#: MORE THAN ONE PAIR, BECAUSE THE CLAIMANTS ANSWER DIFFERENT QUESTIONS. The
#: four path-relation ``_shape_of``s report what happened to an ADDRESS; the
#: job-search one reports what happened to a QUERY and returns "(no query)" for
#: both halves of a path-only pair. Requiring every claimant to discriminate on
#: every pair would be asserting that they all answer the same question, which
#: they do not. AT LEAST ONE is the real contract: the output varies with the
#: input, so something is being reported.
MUST_DISCRIMINATE = [
    (
        REQUESTED,
        "https://www.linkedin.com/feed/",
        "two different paths",
    ),
    (
        "https://www.linkedin.com/jobs/search/?keywords=node&f_JT=F",
        "https://www.linkedin.com/jobs/search/?keywords=node",
        "the same path with and without a filter key",
    ),
]


# ---------------------------------------------------------------------------
# WHAT AN ENTRY IS PROVEN FOR. Added 2026-09-20.
# ---------------------------------------------------------------------------
#
# **THE PROOF WAS ABOUT ONE THING AND THE USE WAS ABOUT ANOTHER.** Every needle
# in :data:`NEEDLED` is a url -- eight url-bearing lines, no prose, no display
# name, and the words "page text" and "display name" appear nowhere above. So
# the certification this file grants means *shapes a URL safely*, and it was
# never asked to mean more.
#
# ``tests/test_page_text_is_never_printed.py`` then consumed it as if it were
# general: until 2026-09-20 that file imported ``_is_sanitiser_call`` and ORed
# it into a taint walk whose sources are SIXTEEN TEXT READERS. Measured on the
# tree at `9f50087`, with every needle invented:
#
#     text_violations("name = await item.inner_text()\nprint(_redact(name))")
#         -> []                    the site is reported CLEAN
#     text_violations("name = await item.inner_text()\nprint(name)")
#         -> [(2, 'print')]        so the [] above is a silencing, not a
#                                  walker that flags nothing
#     _probe_messaging.py::_redact(<an invented display name> + " commented on
#     this")  ->  the same string, BYTE-IDENTICAL
#
# Three of six realistic page-text shapes came back byte-identical from that
# claimant, while it correctly HELD on the url it was proven for. The function
# is not broken. It is correctly scoped, and the scope was not written down
# anywhere a check could read it.
#
# **NOBODY RULED THAT. IT FELL OUT OF AN IMPORT.** This mapping is where the
# scope stops being a paragraph. An entry now says what corpus earned it, and
# :func:`test_a_guard_consults_only_sanitisers_proven_for_its_own_kind` asserts
# that a guard tainting page text does not reach for the url-proven predicate.
#
# WHY THIS IS A SEPARATE MAPPING RATHER THAN A RESHAPED ``_SANITISERS``:
# ``_SANITISERS`` is a frozenset of names pinned by literal copy in two files
# and referenced by name in twenty more, and the url rule's use of it is
# CORRECT -- it taints urls. Turning it into a mapping would edit a shared
# symbol across a parallel-wave day to record a fact that belongs to the
# certifier anyway. The name set stays; what a name PROVES is declared here,
# next to the table that proves it.
SCOPE_URL = "url"
SCOPE_TEXT = "page text"

#: Name -> the kind of value its certification covers. Asserted complete
#: against ``_SANITISERS`` below, so a new guarded name must declare a kind.
#: ALL THREE ARE ``URL`` AND THAT IS THE MEASUREMENT, not an oversight: the
#: table above is the only demonstration any of them has, and it is urls.
PROVEN_FOR: dict[str, str] = {
    "_shape_of": SCOPE_URL,
    "_redact": SCOPE_URL,
    "_relation": SCOPE_URL,
}

#: Which guard taints which kind of value.
GUARD_SCOPE: dict[str, str] = {
    "test_navigation_is_never_derived.py": SCOPE_URL,
    "test_page_text_is_never_printed.py": SCOPE_TEXT,
}

#: The predicate that carries the URL-proven set. A guard whose scope is not
#: :data:`SCOPE_URL` may not name it.
URL_PROVEN_PREDICATE = "_is_sanitiser_call"

#: **PAGE-TEXT NEEDLES.** The corpus a claimant would have to survive to
#: declare :data:`SCOPE_TEXT`.
#:
#: ``Jane Doe`` and ``Jane Q Public`` are this repository's committed invented
#: names -- ``tests/test_probe_redaction.py``, ``tests/test_surface_census.py``
#: and ``tests/test_editor_fields.py`` all carry them -- and ``Northwind`` is
#: the invented employer ``tests/test_apply_fixture.py`` uses. NO REAL IDENTITY
#: IS HERE, and none of these shapes is a url, which is the entire point.
#:
#: THE SHAPES WERE CHOSEN BY WHERE THE LEAK IS, not by symmetry: the first three
#: are the three a measured claimant returns byte-identical, and the last three
#: are ones it holds. A table made only of the cases that fail would not be able
#: to show a redactor DISCRIMINATING, and a table made only of the cases that
#: pass could not fail at all.
TEXT_NEEDLED = [
    ("Jane Doe commented on this", "Jane Doe", "a card byline"),
    ("Congratulate Jane Doe on the new role", "Jane Doe", "plain prose"),
    ("by Jane Q Public, 2h ago", "Jane Q Public",
     "a display name beside a lowercase word"),
    ("Jane Doe's profile photo", "Jane Doe", "an aria-label"),
    ("Jane Doe - Staff Engineer at Northwind", "Jane Doe", "a headline"),
    ("Jane Doe: thanks, will take a look", "Jane Doe", "a message preview"),
]


_MODULES: dict[str, object] = {}


def _module(filename: str):
    """Load one scanned file by PATH, as ``tests/test_probe_redaction.py`` does.

    Cached, because the enrolment cross-product would otherwise re-import every
    probe once per adversary and each import pulls in ``linkedin_server``.
    """
    if filename not in _MODULES:
        path = REPO / "scripts" / filename
        spec = importlib.util.spec_from_file_location(path.stem, path)
        assert spec and spec.loader, filename
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[filename] = module
    return _MODULES[filename]


def _call(function, arity: str, landed: str, requested: str = REQUESTED) -> str:
    if arity == ONE_ARG:
        return function(landed)
    return function(landed, requested)


def _claimants() -> set[tuple[str, str]]:
    """Every ``(file, function)`` in the scanned tree claiming a guarded name.

    PARSED, not grepped. A grep for ``def _redact`` would miss a rebinding and
    would match one inside a string; this repository has a standing note about
    checking a claim by structure rather than by line text.
    """
    found: set[tuple[str, str]] = set()
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in _SANITISERS:
                    found.add((path.name, node.name))
    return found


def _tracked_names() -> set[str]:
    """Basenames of the files GIT HAS, in the two scanned directories.

    Shelled out the way ``tests/test_no_committed_credential.py`` does it, and
    a non-zero return is a FAILURE rather than a skip: a check that goes quiet
    when its instrument is missing is the shape this whole file exists to
    refuse.
    """
    proc = subprocess.run(
        ["git", "ls-files", "--", "scripts", "linkedin_server"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert proc.returncode == 0, "git ls-files failed: %s" % proc.stderr
    return {
        line.rsplit("/", 1)[-1]
        for line in proc.stdout.splitlines()
        if line.strip()
    }


def _untracked_enrolments(table) -> set[str]:
    """Filenames in an enrolment table that git has never heard of.

    A FUNCTION rather than an inline expression, so the control below can hand
    it a table it should reject. A predicate only exercised on data that
    passes has never been shown to reject anything.
    """
    tracked = _tracked_names()
    return {filename for filename, _fn in table if filename not in tracked}


def test_every_enrolled_file_is_tracked_by_git():
    """**AN ENROLMENT NAMING AN UNTRACKED PATH IS A CLAIM ABOUT A WORKING COPY.**

    THIS IS THE DEFECT THIS TEST WAS BORN FROM, and it was reproduced rather
    than reasoned about. The seventh entry -- the one this file caught on its
    first run and was rightly proud of -- named
    ``scripts/_probe_search_render_timeline.py``, which at that moment had ZERO
    COMMITS. It existed on one working copy and in no clone anywhere.

    **CI CLONES.** The lead moved the file aside and re-ran this suite: 5
    failed, 34 passed -- the four needle rows plus the discrimination row, and
    exactly the five the full-suite gate had reported. They had been written
    off as "already fixed at the present tree". They were not fixed; they were
    INVISIBLE from the shared tree, and the first push would have gone red on
    a defect nobody could reproduce locally. A suite that passes on your
    machine and fails in CI is among the worst things a repository can hand
    somebody.

    **THE FILE HAS SINCE BEEN COMMITTED BY ITS AUTHOR (5bb70d4) AND THAT CLOSES
    NOTHING.** It was resolved by somebody else's unrelated commit, not by
    anything structural. Without this assertion the next untracked claimant
    does it again, silently, the same way.

    It is the same defect class as everything else this week, one layer down:
    a claim about the REPOSITORY, verified against the WORKING COPY.
    """
    untracked = sorted(_untracked_enrolments(ENROLLED))
    assert not untracked, (
        "these files are enrolled and git has never heard of them: %s. They "
        "exist on this working copy and in no clone, so this suite passes "
        "here and fails in CI. COMMIT the file, then enrol it -- never the "
        "other way round." % untracked
    )


def test_the_check_would_notice_an_untracked_enrolment():
    """THE CONTROL, and it is the only reason the green above means anything.

    Shown failing against a path that cannot exist, because the real table is
    green now and a predicate exercised only on passing data has never been
    shown to reject anything.
    """
    invented = "_probe_a_file_git_has_never_heard_of.py"
    assert invented not in _tracked_names(), "pick a name that is really absent"
    assert _untracked_enrolments({(invented, "_redact"): ONE_ARG}) == {invented}
    # A REAL TRACKED FILE THROUGH THE SAME PREDICATE, so this shows the
    # predicate ACCEPTING as well as rejecting -- a rejecter that rejects
    # everything is not a check either.
    assert _untracked_enrolments({("shape.py", "_redact"): ONE_ARG}) == set()
    # DELIBERATELY NOT `assert _untracked_enrolments(ENROLLED) == set()`. The
    # test above owns that claim. Re-asserting it here would make the CONTROL
    # go red whenever the STATE is broken, so a reader facing a red suite could
    # not tell "the predicate is broken" from "the table is wrong" -- which is
    # the one distinction a control exists to preserve. Measured: reproducing
    # the original defect turned this test red alongside the real one until the
    # line came out.


def test_every_claimant_of_a_sanitiser_name_is_enrolled():
    """THE NAME IS NOT TRANSFERABLE.

    ``_is_sanitiser_call`` matches ``func.id in _SANITISERS``, so defining a
    function with one of those names anywhere in ``scripts/`` or
    ``linkedin_server/`` silences the output rule at every call to it. This is
    what makes that cost something: a new claimant fails here until it is
    written down and given a table.
    """
    claimants = _claimants()
    enrolled = set(ENROLLED)
    unenrolled = claimants - enrolled
    assert not unenrolled, (
        "these functions claim a _SANITISERS name and are not enrolled: %s. "
        "The guard trusts them BY NAME already. Add each to ENROLLED with its "
        "arity, and it will be measured against the adversarial table below."
        % sorted(unenrolled)
    )
    # THE STALENESS CHECK IS SCOPED TO FILES THAT ARE STILL HERE, deliberately.
    # An enrolment whose FILE is absent -- an untracked probe that was never
    # committed, or one deleted outright -- grants no trust to anything, so
    # firing on it would put a landmine in the suite for a file nobody has.
    # An enrolment whose file EXISTS while its function is gone is the real
    # staleness case, and this repository's standing rule is that the
    # documentation of a thing must not outlive the thing.
    present = {path.name for path in _python_files()}
    vanished = {
        entry for entry in enrolled - claimants if entry[0] in present
    }
    assert not vanished, (
        "these are enrolled, their file is still here, and the function is "
        "gone: %s. An enrolment for a function that does not exist is a "
        "comment pretending to be a check -- delete it." % sorted(vanished)
    )


@pytest.mark.parametrize("claimant", sorted(ENROLLED), ids=lambda c: "%s::%s" % c)
@pytest.mark.parametrize("landed, needle, why", NEEDLED, ids=[w for _u, _n, w in NEEDLED])
def test_each_enrolled_sanitiser_is_shown_holding_the_needle(
    claimant, landed, needle, why
):
    """EVERY CLAIMANT, EVERY NEEDLE. The half arm 2 would have failed."""
    filename, function_name = claimant
    function = getattr(_module(filename), function_name)
    out = _call(function, ENROLLED[claimant], landed)
    assert needle not in out, (
        "%s::%s returned its input's identity (%s) -- %s. It is in "
        "_SANITISERS, which tells every other check in this package that its "
        "result carries none of its input."
        % (filename, function_name, why, needle)
    )


@pytest.mark.parametrize("claimant", sorted(ENROLLED), ids=lambda c: "%s::%s" % c)
def test_each_enrolled_sanitiser_still_discriminates(claimant):
    """THE OTHER DIRECTION, and it is what stops the fix being ``return ''``.

    A sanitiser that collapses everything to one string passes every needle
    test perfectly while reporting nothing -- the failure the messaging
    redactor was measured making twice while it was being written
    (``Conversation List`` flattened to ``<NAME>``).

    AT LEAST ONE PAIR, for the reason argued at :data:`MUST_DISCRIMINATE`.
    """
    filename, function_name = claimant
    function = getattr(_module(filename), function_name)
    arity = ENROLLED[claimant]
    separated = [
        why for left, right, why in MUST_DISCRIMINATE
        if _call(function, arity, left) != _call(function, arity, right)
    ]
    assert separated, (
        "%s::%s returned the SAME string for both halves of every pair in "
        "MUST_DISCRIMINATE, so it is not reporting anything. A redactor that "
        "flattens every input passes a leak-only test while destroying the "
        "reading it exists for." % (filename, function_name)
    )


# ---------------------------------------------------------------------------
# THE SCOPE HALF. A proof about urls may not be spent on page text.
# ---------------------------------------------------------------------------


def _names_used(source: str) -> set[str]:
    """Every identifier a module IMPORTS or CALLS, parsed rather than grepped.

    Both halves are needed and neither alone is enough. An import without a
    call is a symbol sitting in a namespace and could be added back into a stop
    condition by one word; a call without an import is how a name arrives from
    a star-import or a rebinding. A grep would match the identifier inside this
    very docstring, which is the standing reason this package parses.
    """
    used: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                used.add(alias.asname or alias.name)
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                used.add(func.id)
            elif isinstance(func, ast.Attribute):
                used.add(func.attr)
    return used


def test_every_guarded_name_declares_what_it_is_proven_for():
    """A NAME WITH NO DECLARED KIND IS THE DEFECT, WEARING A NEW SPELLING.

    ``_SANITISERS`` gaining an entry without a row here would put the package
    back where it was on 2026-09-20: a certification whose corpus nobody had
    written down, consumed by a guard asking a different question.
    """
    assert set(PROVEN_FOR) == set(_SANITISERS), (
        "these guarded names declare no proven kind: %s ; these declare a kind "
        "and are not guarded: %s"
        % (sorted(set(_SANITISERS) - set(PROVEN_FOR)),
           sorted(set(PROVEN_FOR) - set(_SANITISERS)))
    )
    assert set(PROVEN_FOR.values()) <= {SCOPE_URL, SCOPE_TEXT}, sorted(set(PROVEN_FOR.values()))


def test_a_guard_consults_only_sanitisers_proven_for_its_own_kind():
    """**THE RULING, AS A CHECK.** The proof obligation must match the use.

    Until 2026-09-20 ``tests/test_page_text_is_never_printed.py`` imported
    ``_is_sanitiser_call`` and ORed it into a taint walk over SIXTEEN TEXT
    READERS. Every name that predicate matches is certified by
    :data:`NEEDLED` -- eight url-bearing lines and nothing else -- so a site
    was reported clean on the strength of a proof about addresses.

    **BOTH DIRECTIONS IN ONE ASSERTION, deliberately.** It is not "the text
    guard must not name the predicate"; it is "naming it is exactly as allowed
    as the guard's scope being url". Written one-sided, the check would still
    pass if the URL rule lost its own stop -- which would silently forbid that
    rule's own fix, the thing ``_SANITISERS`` exists to prevent.
    """
    for filename, kind in sorted(GUARD_SCOPE.items()):
        path = REPO / "tests" / filename
        assert path.exists(), "GUARD_SCOPE names a file that is not here: %s" % filename
        consults = URL_PROVEN_PREDICATE in _names_used(
            path.read_text(encoding="utf-8")
        )
        assert consults == (kind == SCOPE_URL), (
            "%s taints %r and %s %s. A guard may stop at a sanitiser only "
            "where that sanitiser's certification was measured: NEEDLED in "
            "this file is urls. If page text now needs a stop, give it one "
            "proven against TEXT_NEEDLED and declare it in PROVEN_FOR -- do "
            "not re-import this one."
            % (filename, kind,
               "names" if consults else "does not name",
               URL_PROVEN_PREDICATE)
        )


def _predicate_users() -> set[str]:
    """Every file under ``tests/`` that IMPORTS OR CALLS the url-proven predicate.

    Enumerated off the tree, never off :data:`GUARD_SCOPE`, for the reason the
    enrolment half exists: a table cannot list a file nobody has written yet.
    """
    found: set[str] = set()
    for path in sorted((REPO / "tests").glob("*.py")):
        if URL_PROVEN_PREDICATE in _names_used(path.read_text(encoding="utf-8")):
            found.add(path.name)
    return found


def test_every_consumer_of_the_url_proven_predicate_declares_its_scope():
    """**THE ENUMERATION HALF, AND IT CLOSES A HOLE IN THE TEST ABOVE.**

    That test iterates :data:`GUARD_SCOPE`, so a THIRD guard file that imported
    ``_is_sanitiser_call`` tomorrow would be invisible to it -- declared
    nowhere, checked by nothing, and green. **That is the same defect this file
    was built for, committed by somebody who had just written the fix for it:**
    the enrolment guard exists because a claimant inherits trust the instant it
    is typed, and a CONSUMER inherits it exactly the same way.

    The certifier itself holds the name as a STRING and in prose a dozen times
    and is correctly absent here, because :func:`_names_used` parses. A grep
    would demand this file declare itself a guard.

    **THE CONTAINMENT IS ONE-WAY, AND THE FIRST MUTATION OF THIS TEST GOT IT
    BACKWARDS.** Users must be a SUBSET of :data:`GUARD_SCOPE`, not equal to
    it: since 2026-09-20 ``test_page_text_is_never_printed.py`` is declared
    there and is NOT a user, which is precisely the fix. So dropping the
    page-text row does not go red here -- it goes red in the biconditional
    above, which owns that direction. Mutating this test means making a REAL
    user undeclared, or inventing a new one. Both were run; both are red.
    """
    undeclared = sorted(_predicate_users() - set(GUARD_SCOPE))
    assert not undeclared, (
        "these files under tests/ import or call %s and declare no scope: %s. "
        "The predicate carries a certification measured against urls only. Add "
        "each to GUARD_SCOPE with the KIND of value it taints -- and if that "
        "kind is not %r, it may not name the predicate at all."
        % (URL_PROVEN_PREDICATE, undeclared, SCOPE_URL)
    )
    # AND THE SET IS NOT EMPTY, so the subtraction above is over something. Two
    # empty sets agree; that agreement would prove nothing.
    assert _predicate_users(), (
        "no file under tests/ uses %s at all, so this check subtracts one empty "
        "set from another and the green is vacuous. If the predicate really is "
        "gone, delete GUARD_SCOPE and this test with it." % URL_PROVEN_PREDICATE
    )


def test_the_scope_check_would_notice_a_guard_reaching_outside_its_kind():
    """THE CONTROL, and without it the test above is a green over two files.

    ``_names_used`` is shown ACCEPTING and REJECTING on sources authored here,
    because a predicate only ever run on data that passes has never been shown
    to reject anything. The first source is the DEFECT, reconstructed in four
    lines.
    """
    offending = (
        "from test_navigation_is_never_derived import _is_sanitiser_call\n"
        "def walk(child):\n"
        "    if _is_sanitiser_call(child):\n"
        "        return False\n"
    )
    assert URL_PROVEN_PREDICATE in _names_used(offending), (
        "the defect itself, in four lines, and the predicate did not see it"
    )

    # IMPORTED BUT NEVER CALLED still counts -- it is one word from being a
    # stop condition again, and that is the state this file is preventing.
    imported_only = (
        "from test_navigation_is_never_derived import _is_sanitiser_call\n"
    )
    assert URL_PROVEN_PREDICATE in _names_used(imported_only), (
        "an import with no call is one word from a stop condition"
    )

    # CALLED THROUGH AN ATTRIBUTE, which is how it would arrive from a module
    # import rather than a from-import.
    attribute_form = "import urls\ndef walk(c):\n    return urls._is_sanitiser_call(c)\n"
    assert URL_PROVEN_PREDICATE in _names_used(attribute_form), (
        "the attribute spelling is how it arrives from a module import"
    )

    # AND THE NEGATIVE, so it is not a predicate that says yes to everything.
    clean = (
        "from test_navigation_is_never_derived import _COUNTING_CALLS\n"
        "def walk(child):\n"
        "    return _is_text_sanitiser_call(child)\n"
    )
    assert URL_PROVEN_PREDICATE not in _names_used(clean), (
        "a rejecter that rejects everything is not a check"
    )

    # THE NAME INSIDE A STRING IS NOT A USE. A grep would call this a hit, and
    # this file's own prose says ``_is_sanitiser_call`` a dozen times.
    prose = '"""a docstring that mentions _is_sanitiser_call by name."""\n'
    assert URL_PROVEN_PREDICATE not in _names_used(prose), (
        "matched the name inside a docstring -- this is why it is parsed"
    )


def test_no_claimant_declares_page_text_without_surviving_the_text_table():
    """EVERY CLAIMANT PROVEN FOR TEXT, AGAINST EVERY PAGE-TEXT NEEDLE.

    **THIS LOOP IS VACUOUS TODAY AND SAYS SO.** No entry in :data:`PROVEN_FOR`
    declares :data:`SCOPE_TEXT`, so it checks zero claimants and cannot fail. That is
    not a defect to be papered over with a fuller-looking assertion -- it is
    the honest state, and the two controls below are what make the table real
    rather than decorative. They run :data:`TEXT_NEEDLED` against two functions
    that exist, and one of them fails it.

    The count is asserted rather than left implicit, so the day a claimant does
    declare :data:`SCOPE_TEXT` this stops being vacuous and a reader can see that it did.
    """
    checked = []
    for claimant in sorted(ENROLLED):
        filename, function_name = claimant
        if PROVEN_FOR[function_name] != SCOPE_TEXT:
            continue
        function = getattr(_module(filename), function_name)
        for text, needle, why in TEXT_NEEDLED:
            out = str(_call(function, ENROLLED[claimant], text))
            assert needle not in out, (
                "%s::%s declares it is proven for page text and returned the "
                "display name in %s. An entry is a promise made on a "
                "function's behalf." % (filename, function_name, why)
            )
        checked.append("%s::%s" % claimant)
    expected = sorted(
        "%s::%s" % c for c in ENROLLED if PROVEN_FOR[c[1]] == SCOPE_TEXT
    )
    assert sorted(checked) == expected, (checked, expected)


def test_the_text_table_catches_the_claimant_that_is_measured_leaking_prose():
    """**SHOWN FAILING, AGAINST A REAL FUNCTION, NOT A STUB.**

    ``scripts/_probe_messaging.py::_redact`` is a pattern list plus a
    capitalised-run collapse, and its own source says the gap out loud: a
    display name beside a lowercase word passes straight through, because the
    run then contains a lowercase word and the collapse declines it.

    **THAT IS NOT A BUG IN IT.** It holds on the url it is certified for, and
    it is the reason its row in :data:`PROVEN_FOR` says :data:`SCOPE_URL`. What this
    asserts is that the page-text table can CONVICT -- a table that everything
    passes would let the next TEXT claimant in on nothing.
    """
    redact = getattr(_module("_probe_messaging.py"), "_redact")
    leaked = [why for text, needle, why in TEXT_NEEDLED if needle in redact(text)]
    assert leaked, (
        "TEXT_NEEDLED no longer catches the claimant it was built from, so "
        "every green above is vacuous. Either the function changed -- in which "
        "case re-measure and consider whether it now earns SCOPE_TEXT -- or the "
        "table stopped carrying the shapes that fail."
    )
    # AND THE URL IT IS CERTIFIED FOR STILL HOLDS, in the same breath. Without
    # this the reader cannot tell a correctly-scoped function from a broken one.
    assert "some-real-slug-99" not in redact(
        "https://www.linkedin.com/in/some-real-slug-99/details/skills/"
    )


def test_the_text_table_is_not_a_rejecter_that_rejects_everything():
    """THE OTHER HALF. A table nothing survives certifies nothing either.

    ``scripts/_probe_search_render_timeline.py::_redact`` is the same name and
    a different function -- allowlist-based, membership rather than absence --
    and it holds on every shape in the table. Two functions, one spelling,
    opposite results: which is also the plainest statement of why the guard
    cannot be allowed to match on the name alone.
    """
    redact = getattr(_module("_probe_search_render_timeline.py"), "_redact")
    survived = [why for text, needle, why in TEXT_NEEDLED if needle in redact(text)]
    assert not survived, survived


def test_the_table_would_catch_a_do_nothing_sanitiser():
    """THE CONTROL. Without it the greens above mean nothing.

    This is arm 2 of the mutation study, run as a check rather than described
    in a comment: a body that returns its input, against the same table.
    """
    def gutted(url, requested=None):
        return url

    caught = [
        why for landed, needle, why in NEEDLED
        if needle in gutted(landed)
    ]
    assert len(caught) == len(NEEDLED), (
        "the needle table caught only %d of %d rows against a sanitiser that "
        "does nothing. The rows it missed are rows this file cannot see, and "
        "their greens above are vacuous: %s"
        % (len(caught), len(NEEDLED),
           sorted({w for _u, _n, w in NEEDLED} - set(caught)))
    )


def test_the_table_would_catch_a_constant_returning_sanitiser():
    """THE SECOND CONTROL. Over-redaction has to fail too, or the fix is ''."""
    def constant(url, requested=None):
        return "SERVED"

    separated = [
        why for left, right, why in MUST_DISCRIMINATE
        if constant(left) != constant(right)
    ]
    assert not separated, (
        "the discrimination table thinks a CONSTANT function reports "
        "something (%s), so it would not notice a redactor that reports "
        "nothing." % separated
    )


def test_the_guarded_names_are_the_ones_this_file_thinks_they_are():
    """PINNED AGAINST DRIFT IN THE OTHER FILE.

    This file's whole premise is the contents of ``_SANITISERS``. If a name is
    added there and not considered here, the enrolment above stops covering the
    set it claims to cover -- silently, because a new name simply matches
    nothing.
    """
    # ``_relation`` ADDED TO THIS PIN 2026-09-05, AND THE ORDERING IS THE
    # WHOLE POINT. It entered ``_SANITISERS`` at `196394d`, which did not touch
    # this file, so for several hours the pin was STALE and both enumeration
    # guards were red. The available shortcut was to widen this line and turn
    # them green -- **which would have been adding a name to a list to silence
    # the check that the name has to earn**, while four claimants sat
    # unenrolled and trusted purely by spelling. That is precisely the state
    # ``_redact`` was in when it turned out to carry no slug rule at all.
    #
    # It was NOT taken. Every claimant was enrolled first, by the wave that
    # owned it, and each was demonstrated against the adversarial table below
    # -- ``test_every_claimant_of_a_sanitiser_name_is_enrolled`` GREEN at 65
    # passing tests before this line was edited. Only then is widening the pin
    # RECORDING what the enrolment half has proven rather than asserting it.
    #
    # **A PIN UPDATED BEFORE ITS EVIDENCE IS A DIFFERENT ACT FROM ONE UPDATED
    # AFTER, and the diff looks identical.** That is why the order is written
    # down here and not left to be inferred from a commit date.
    assert _SANITISERS == frozenset(
        {"_shape_of", "_redact", "_relation"}
    ), _SANITISERS
    assert {name for _f, name in ENROLLED} == set(_SANITISERS), (
        "every guarded name must have at least one enrolled claimant, or this "
        "file is asserting over a name nobody uses: %s vs %s"
        % (sorted({n for _f, n in ENROLLED}), sorted(_SANITISERS))
    )
