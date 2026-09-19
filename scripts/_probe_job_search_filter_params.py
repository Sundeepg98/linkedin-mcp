"""Does LinkedIn HONOUR the job-search url filter parameters that
``linkedin_search_jobs`` is about to gain, or does it DISCARD them in silence?

THEIR SPELLINGS ARE BELIEVED, NOT MEASURED, and this repository does not ship
believed values. Five parameters are about to be appended to
``https://www.linkedin.com/jobs/search/`` by a shipped read tool::

    f_AL=true      Easy Apply only
    f_JT=F         job type, F = full-time
    f_EA=true      under ten applicants
    f_JIYN=true    in your network
    f_FCE=true     fair chance employer

**A PARAMETER LINKEDIN DOES NOT KNOW IS NOT AN ERROR.** It is dropped without
a word: the page still renders, the pills still draw, the cards still come
back. So a tool that appends a misspelled one reports a filter the member
never got, and nothing anywhere says otherwise. The question here is therefore
not "does the address load" -- every address below is already allowed by
``readonly._ALLOWED_URL_PATTERNS``, and all thirteen were confirmed ALLOWED
against ``readonly.is_read_url`` before this file was written -- but "does the
page COME BACK DIFFERENT".

THIS FILE RUNS TWO SEPARATE PASSES, in one browser session, with
``asyncio.sleep`` between every pair of loads in both.

=============================================================================
PASS ONE -- the five candidates, seven loads
=============================================================================

    1    BASELINE            ?keywords=<K> and nothing else
    2    NEGATIVE CONTROL    ?keywords=<K>&f_ZZQQX=true
    3-7  the five candidates, one per load

**THE NEGATIVE CONTROL IS THE CALIBRATION, NOT DECORATION.** ``f_ZZQQX`` is a
parameter LinkedIn has never had, so whatever it does to the page is exactly
what BEING IGNORED looks like on this surface. If it comes back identical to
BASELINE, then "identical to BASELINE" is a reading that MEANS ignored, and a
candidate that also comes back identical is ignored too. If it comes back
DIFFERENT, the page varies between loads on its own -- LinkedIn re-ranks, the
rendered card set moves -- and pass one cannot discriminate anything.

**THAT IS A FINDING, NOT A FAILURE, AND PASS ONE STOPS THERE.** It does not go
on to take five more readings and present them as evidence; it reports WHICH
channel disagreed and by how much. PASS TWO STILL RUNS -- it is a separate
instrument with its own controls and does not inherit pass one's verdict.

=============================================================================
PASS TWO -- settling ``f_JT`` on its own, six loads
=============================================================================

WHY A SECOND PASS EXISTS. Pass one's first live run returned, for ``f_JT=F``,
a zero on both channels it consults (card delta 0, differing pills 0) while
two channels it does NOT consult said the page had changed: LinkedIn KEPT the
``f_JT`` key in the landed url where the negative control's key was STRIPPED,
and the page carried 76 buttons against 71 for both baseline and the negative
control. A verdict of IGNORED on a silent channel is not a measurement, it is
an instrument reporting its own blind spot.

THE HYPOTHESIS UNDER TEST, and it is here to be REFUTED rather than confirmed:
the four boolean filters each render their own named checkbox, which is why
the pill channel sees them; job type renders as a DROPDOWN whose control name
stays "Job type" whatever value is chosen, so the pill channel is
STRUCTURALLY BLIND to it rather than reporting a true negative.

    1  BASELINE            ?keywords=<K>
    2  NEGATIVE CONTROL    ?keywords=<K>&f_ZZQQX=true   RE-TAKEN, not reused
    3  f_JT=F              full-time
    4  f_JT=C              contract
    5  f_JT=F,C            two values comma-joined
    6  f_JT=ZZ             A VALUE-LEVEL NEGATIVE CONTROL

**LOAD 6 IS THE ONE THAT DECIDES.** The KEY KEPT channel that pass one turned
up is only worth promoting if it is measuring the PARAMETER. If ``f_JT=ZZ`` --
a value the job-type filter has never had -- is kept and looks identical to
``f_JT=F``, then LinkedIn keeps any ``f_``-prefixed pair whatever it says, the
channel is measuring the PREFIX, and it proves nothing about ``f_JT``. If
``f_JT=ZZ`` behaves differently from ``f_JT=F`` in some channel while the name
survives, ``f_JT`` is honoured. Anything else is CANNOT TELL, said plainly
rather than split down the middle.

ONE FIXED KEYWORD for all thirteen loads, never varied, because a changed
keyword changes the result set for reasons that have nothing to do with a
filter.

## What is measured, per load

* **CARD COUNT.** ``dom.harvest_linked_cards`` with ``dom.JOB_HREF``, the
  shipped harvest with the shipped pattern. THE COUNT ONLY.
* **PILL STATE -- THE ARIA CHANNEL.** Every ``<button>`` on the page, read
  through ``page.locator`` and ``get_attribute``, reported as an accessible
  name beside its ``aria-pressed`` / ``aria-checked`` / ``aria-expanded``.
  A control carrying none of the three CANNOT APPEAR ON THIS CHANNEL AT ALL,
  which is why the one below exists.
* **NAME PRESENCE -- A SECOND, SEPARATE CHANNEL.** The set of accessible NAMES
  of every named button, WHATEVER its aria state, under the same length gate
  and the same shaper. Reported as names that APPEARED or DISAPPEARED between
  a load and its baseline, printed apart from the aria channel and never
  merged into it. **THIS CHANNEL EXISTS BECAUSE A ZERO FROM A GATE THAT
  CANNOT SEE THE CONTROL IS NOT A NEGATIVE READING.** ``Reset selected Job
  type`` -- the single control that evidences ``f_JT`` having applied --
  carries ``pressed=- checked=- expanded=-``, so the aria gate excluded it
  structurally and pass one reported ``(none)`` differing for ``f_JT=F``.
* **KEY KEPT** -- whether the landed url still carries the key=value pair
  that was asked for, compared AFTER percent-encoding is normalised on both
  sides (see :func:`_key_kept`).

  **THE ENCODING IS REPORTED AS A RELATION, NOT BY ECHOING IT.** The reading
  says whether the landed value was BYTE-IDENTICAL to the literal this file
  asked for and how many characters each ran to; the landed value itself is
  never printed. An earlier draft of this probe printed the raw landed pair
  "so the encoding is visible rather than merely trusted", and that is
  precisely the design :func:`_shape_of` retired on a measurement: a cold
  verifier fed the old per-pair renderer thirty adversarial urls and it leaked
  eight, because **no property of a string separates a vanity slug from an
  enum** -- ``f_TPR=r86400``, ``origin=JOBS_HOME`` and a slug are one shape to
  any charset or length rule. A renderer cannot be made safe by inspecting the
  value, so this one reports the relation and the reader trusts an integer
  instead of a redactor.

  **THE KEY WAS KEPT; WHETHER THE VALUE WAS APPLIED IS A DIFFERENT QUESTION
  AND THIS CHANNEL CANNOT ANSWER IT.** ``f_JT=ZZ`` -- a job-type value the
  filter has never had -- was kept VERBATIM and was inert on every other
  channel: +0 buttons, identical to BASELINE and to the negative control. So
  this channel measures whether LinkedIn RECOGNISES THE KEY (``f_ZZQQX`` was
  stripped; ``f_JT`` was not) and says nothing whatever about the VALUE.
  **NOTHING MAY PRINT HONOURED ON THE STRENGTH OF THIS CHANNEL ALONE.**
* **THE LANDED QUERY, AS A RELATION** through :func:`_shape_of` -- which
  keys of ours it carried, how many it carried that are not ours, and which
  of ours it dropped. Counts and our own key names; never a value.
* **PASS TWO ALSO:** every control whose name contains "job type",
  "full-time", "contract" or "employment", case-insensitively, together with
  the inventory of names that were SEARCHED, so a zero says what it looked at.
* **PASS TWO BASELINE ALSO:** the ``dom.JOB_HREF`` diagnosis -- that pattern
  printed beside the count of anchors whose href contains ``/jobs/view/`` --
  because pass one's card channel returned exactly 7 on all seven loads
  including baseline, which is an inert channel and worth one line of
  diagnosis. Taken on a page that is being loaded anyway.

## Bounds

**EVERY ADDRESS IS A MODULE-LEVEL CONSTANT.** The thirteen urls are literals
in :data:`LOADS` and :data:`PASS2_LOADS`; nothing is built from a landed url
or from anything the page said. ``tests/test_navigation_is_never_derived.py``
scans this file like any other, and a probe that measured url parameters by
deriving a url from the page would be the joke version of itself.

**THE LANDED QUERY IS REPORTED AS A RELATION, AND THE NAME IS THE CONTRACT.**
That same test guards a second sink -- ``print`` -- because a landed url
reached a transcript three separate ways on 2026-09-03, and it stops
descending only at a call to a function named in its ``_SANITISERS`` set.
:func:`_shape_of` below carries that name deliberately.

What it emits: which members of :data:`QUERY_KEYS_PRINTABLE` the landed query
carried, how many pairs it carried that are NOT in that set, and which of ours
it dropped. Our own key names and integers. **No value is read at all, and a
key the page invented is COUNTED, never named.**

**WHAT THIS PARAGRAPH SAID UNTIL 2026-09-04, BECAUSE THE CORRECTION IS THE
POINT.** It described an allowlist called ``_redact`` which printed a pair's
value verbatim when its KEY was in :data:`QUERY_KEYS_PRINTABLE`, and it closed
with **"NOTHING OUTSIDE THIS FILE VERIFIES IT."**

That sentence was an honest disclosure when it was written and became a FALSE
one the hour it was fixed. ``tests/test_a_sanitiser_earns_its_entry.py`` now
enrols every function in the scanned tree claiming a ``_SANITISERS`` name and
runs each against an adversarial table, so this one IS verified from outside.
**Leaving the old line standing would have UNDERSTATED this file's safety and
pointed away from the instrument that fixed it** -- an auditor reading
top-down meets "nothing verifies this" and stops, which is the corrector and
the corrected drifting apart inside a single file.

**A REWRITE THAT REPLACES A FUNCTION LEAVES ITS PROSE BEHIND BY DEFAULT.**
That is the shape of the edit rather than carelessness, and it is why prose
gets a deliberate pass after one -- not a glance.

**IT IS THIRTEEN GETS AND NOTHING ELSE.** No click, no fill, no scroll, no
``set_input_files``, and ``asyncio.sleep`` between every pair of loads. One
``BROWSER.session()`` for all thirteen.

**NO NEW ``page.evaluate``.** The button walk is ``page.locator("button")``
plus ``get_attribute`` / ``inner_text``. ``dom.read_surface_census`` was read
first and REJECTED for this question on two measured grounds: it does not read
``aria-pressed`` at all (grep ``aria-pressed`` across ``linkedin_server/`` and
every hit is a comment -- no reader consults it), and it puts every accessible
name through ``shape.census_shape`` INSIDE itself, so a filter pill would come
back as a shape rather than as the LinkedIn furniture the answer needs to
name. No other reader in ``dom.py`` returns names beside aria state.

**REDACTION, AND IT IS NOT THE ONE THE QUESTION ASSUMED.** Job cards carry
EMPLOYER names and JOB TITLES -- third parties -- so no card text, no title,
no company and no job id is printed. Counts only. Filter pill names ARE
printed verbatim, because they are LinkedIn's own furniture. But **the two
sets share one enumeration**: a job card's own controls are ``<button>``
elements on the same page, and LinkedIn writes titles and employers into their
accessible names. Three gates separate them, in this order:

    1. ARIA-STATE GATE. A button enters the ARIA-STATE inventory only if it
       carries at least one of the three aria attributes. One that carries
       none is COUNTED and never named ON THAT CHANNEL.

       **IT WAS WRITTEN HERE THAT THIS COSTS THE QUESTION NOTHING. THAT WAS
       WRONG, AND IT COST THE QUESTION THE WHOLE f_JT READING.** ``Reset
       selected Job type`` carries ``pressed=- checked=- expanded=-``; it is
       the single control that evidences ``f_JT`` having applied, and gate 1
       excluded it structurally, so ``_differing_names`` reported ``(none)``
       and that zero was read as a negative. A zero from a gate that cannot
       see the thing is not a negative reading.

       THE GATE STAYS -- it is still the structural proxy for "this control
       is filter chrome", and dropping it would publish card text -- and the
       repair is a SECOND CHANNEL beside it rather than a wider gate: the
       NAME-PRESENCE channel carries every named button whatever its aria
       state, under gates 2 and 3 only. Every reading off the aria channel
       now prints its own denominator, so an absence there says how many
       controls it could not see.
    2. ``shape.census_shape``, so a urn, a member path, a company path, a
       possessive or a long digit run cannot survive inside a printed name.
    3. LENGTH. Names of 60 characters or more are dropped, which is also
       ``shape.CENSUS_NAME_LIMIT``.

**TWO READINGS LOOK OUTSIDE GATE 1: THE NAME-PRESENCE CHANNEL ABOVE, AND THE
NEEDLE SEARCH IN PASS TWO.** The needle search does so because a job-type
control that carries no aria state is precisely the thing the hypothesis
predicts, and a search that could not see it would confirm the hypothesis by
construction. It gets its own gate instead: a needle match
prints only if it CARRIES AN ARIA STATE or is under
:data:`NEEDLE_NAME_LIMIT` characters. "Job type", "Full-time" and "Contract"
are all short; "Save <a title> at <an employer>" is not, and is withheld with
a count. Gates 2 and 3 still apply on top.

**THE RESIDUAL, NAMED RATHER THAN IMPLIED:** a card control that carries an
aria state AND a job title in its accessible name would be printed. Gate 1 is
a proxy, not a proof. Every gate reports how many names it dropped, so the
size of what is not being shown is on the page rather than assumed.

Run:  venv/Scripts/python.exe scripts/_probe_job_search_filter_params.py
Writes: ``_audit/_scratch/_probe-jobsearch-params.txt`` (that directory is
unconditionally gitignored) and the same text to stdout.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import parse_qsl, unquote_plus, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: THE ONE KEYWORD, FIXED FOR ALL THIRTEEN LOADS. Printed in the report so the
#: reader can see it never varied; the urls below carry it percent-encoded.
KEYWORD_TEXT = "node.js developer"

#: **PASS ONE'S SEVEN ADDRESSES, AS MODULE-LEVEL LITERALS.** Written out in
#: full, one per row, rather than assembled -- there is nothing here for a
#: landed url to reach into, which is the property
#: ``tests/test_navigation_is_never_derived`` exists to enforce and the
#: property this probe's own subject matter makes most tempting to break.
#:
#: Each row is ``(label, parameter, url)``. The parameter is ALSO the needle
#: used to ask whether LinkedIn kept the pair in the address it finished on,
#: so it is a literal here and not a slice of anything.
LOADS: tuple[tuple[str, str, str], ...] = (
    (
        "BASELINE",
        "",
        "https://www.linkedin.com/jobs/search/?keywords=node.js%20developer",
    ),
    (
        "NEGATIVE CONTROL",
        "f_ZZQQX=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_ZZQQX=true",
    ),
    (
        "Easy Apply only",
        "f_AL=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_AL=true",
    ),
    (
        "job type full-time",
        "f_JT=F",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=F",
    ),
    (
        "under ten applicants",
        "f_EA=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_EA=true",
    ),
    (
        "in your network",
        "f_JIYN=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JIYN=true",
    ),
    (
        "fair chance employer",
        "f_FCE=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_FCE=true",
    ),
)

#: **PASS TWO'S SIX ADDRESSES.** Same rule, same literal form. Rows 1 and 2
#: are RE-TAKEN rather than carried over from pass one: a baseline measured
#: minutes and six loads earlier is a reading with a timestamp, and the whole
#: point of a control is that it was taken beside the thing it controls.
PASS2_LOADS: tuple[tuple[str, str, str], ...] = (
    (
        "BASELINE",
        "",
        "https://www.linkedin.com/jobs/search/?keywords=node.js%20developer",
    ),
    (
        "NEGATIVE CONTROL",
        "f_ZZQQX=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_ZZQQX=true",
    ),
    (
        "f_JT full-time",
        "f_JT=F",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=F",
    ),
    (
        "f_JT contract",
        "f_JT=C",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=C",
    ),
    (
        "f_JT two values",
        "f_JT=F,C",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=F,C",
    ),
    (
        "f_JT VALUE CONTROL",
        "f_JT=ZZ",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=ZZ",
    ),
)

#: Index of the two loads every pass rests on.
BASELINE_INDEX = 0
NEGATIVE_INDEX = 1

#: The three attributes a filter pill can carry its state in. A button wearing
#: none of them is counted and never named -- gate 1 in the docstring.
ARIA_STATE_ATTRS: tuple[str, ...] = ("aria-pressed", "aria-checked", "aria-expanded")

#: Ceiling on buttons walked per load, so a page that draws hundreds cannot
#: turn one read into thousands of round trips. Reported as truncated rather
#: than silently cut, the way ``dom.CENSUS_MAX_CONTROLS`` is.
MAX_BUTTONS = 400

#: Gate 3. Same number as ``shape.CENSUS_NAME_LIMIT``, and deliberately so.
NAME_LIMIT = 60

#: The needle gate for pass two's job-type search -- the one search that looks
#: outside the aria-state gate, and so the one that needs a length rule of its
#: own. A match longer than this prints only if it carries an aria state.
NEEDLE_NAME_LIMIT = 30

#: WHAT PASS TWO HUNTS FOR, lowercased and matched as substrings. "employment"
#: is here because LinkedIn labels this filter "Job type" on some surfaces and
#: "Employment type" on others, and a search that knew only one spelling would
#: report a confident zero.
JT_NEEDLES: tuple[str, ...] = ("job type", "full-time", "contract", "employment")

#: Between every pair of loads. Not a settle wait -- ``BROWSER.goto`` already
#: does that and enforces its own navigation interval on top.
SLEEP_BETWEEN_LOADS_S = 3

#: Substrings that mean the browser was bounced off the surface entirely.
WALL_MARKERS: tuple[str, ...] = ("/login", "/checkpoint", "/authwall", "/uas/login")

#: The path every one of the thirteen addresses asks for.
JOBS_SEARCH_PATH = "/jobs/search"

#: **THE KEYS :func:`_shape_of` WILL NAME IN A RELATION.** Membership here
#: decides whether a landed key is NAMED in the reading. It does not decide
#: what a VALUE may print, because since 2026-09-04 no value prints at all.
#:
#: THE DIRECTION MATTERS AND IS STILL THE ARGUMENT FOR THE SET. A blocklist of
#: known-bad keys fails OPEN on the identifier nobody thought of, and a
#: jobs-search url grows them without warning -- ``currentJobId`` is a job id,
#: ``geoId`` is a location id, and LinkedIn appends tracking pairs at will.
#:
#: **UNTIL 2026-09-04 THIS SET GATED VALUES, AND THAT WAS RIGHT AND
#: INSUFFICIENT.** Membership fails closed against an unforeseen KEY, and a
#: cold verifier then measured the two ways it fails open anyway: an
#: allowlisted key can carry a vanity slug as its VALUE, which no charset or
#: length rule separates from ``f_TPR=r86400``; and ``key, value = pair, ""``
#: for a pair with no ``=`` moved a value into the KEY position, walking round
#: the gate entirely. Eight of thirty adversarial urls leaked. The set stayed;
#: what it gates changed. See :func:`_shape_of`.
#:
#: Every key here is either one this repository put in the url itself or a
#: LinkedIn search-shape parameter that carries no identity. ``keywords`` is
#: here because it is the constant this probe supplies and holds nothing else.
QUERY_KEYS_PRINTABLE: frozenset[str] = frozenset(
    {
        "keywords",
        "f_AL",
        "f_JT",
        "f_EA",
        "f_JIYN",
        "f_FCE",
        "f_ZZQQX",
        "f_E",
        "f_TPR",
        "f_WT",
        "f_SB2",
        "sortBy",
        "origin",
        "refresh",
        "position",
        "pageNum",
        "start",
        "distance",
    }
)

#: The anchor shape the ``dom.JOB_HREF`` diagnosis counts.
JOB_VIEW_ANCHOR = 'a[href*="/jobs/view/"]'

#: Where the findings land. The directory is gitignored unconditionally
#: (``.gitignore``: ``_audit/_scratch/``), which is why a live reading may be
#: written there at all.
OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "_audit"
    / "_scratch"
    / "_probe-jobsearch-params.txt"
)

#: How many differing pill names one table cell will name before it stops.
MAX_NAMED_IN_CELL = 6


def _shape_of(landed_url: str, requested_url: str) -> str:
    """WHAT THE LANDED QUERY IS, never what it says. A RELATION.

    **THIS REPLACED AN ALLOWLIST CALLED ``_redact`` ON 2026-09-04, AND THE
    REASON IS A MEASUREMENT RATHER THAN A PREFERENCE.** That function rendered
    each pair, printing a value verbatim when its KEY was in
    :data:`QUERY_KEYS_PRINTABLE` and a name-plus-count otherwise. A cold
    verifier fed it thirty adversarial urls and it leaked EIGHT, in four
    classes that no repair to it could have closed:

    1. A BARE VANITY SLUG under an allowlisted key. ``shape.census_shape``
       substitutes ``/in/<slug>/``; strip the ``/in/`` prefix and a slug is
       ``[a-z0-9-]``, which is entirely inside ``shape._CENSUS_SAFE_CHARS``,
       carries no six-digit run, and passes both layers untouched.
    2. A DISPLAY NAME under an allowlisted key, for the reason ``shape.py``
       states about itself: ``census_shape`` is not a name oracle, and names
       are caught at the TALLY in ``census_redact_rare``, which needs a count
       this function never has.
    3. THE KEY CHANNEL, which was never an allowlist at all. The membership
       test gated VALUES; the KEY was printed through the shaper alone. And
       ``key, value = pair, ""`` for a pair with no ``=`` moves a VALUE INTO
       THE KEY POSITION, so a bare token walked straight around the gate.
    4. A REPEATED allowlisted key printed every occurrence.

    **THE COMMON CAUSE IS THAT NO PROPERTY OF A STRING SEPARATES A SLUG FROM
    AN ENUM.** ``f_TPR=r86400``, ``origin=JOBS_HOME`` and a vanity slug are
    the same shape to any charset or length rule -- which is precisely the
    fact ``shape.py`` records when it explains why ``census_redact_rare`` keys
    on a COUNT and not on the string. A sanitiser here cannot win, so this
    stops trying to render the query and reports the RELATION instead.

    WHAT IT RETURNS, and every part is either a string this file authored or
    an integer: which members of :data:`QUERY_KEYS_PRINTABLE` the landed query
    carried, how many pairs it carried that are NOT in that literal set, and
    whether it kept every key the requested address asked for. **No value is
    read. No key the page invented is named.** A key nobody anticipated cannot
    print anything but its existence.

    THE NAME IS THE CONTRACT AND IS NOW EARNED RATHER THAN ASSERTED.
    ``_shape_of`` is this package's established name for a relation-returner,
    it is in ``tests/test_navigation_is_never_derived.py::_SANITISERS``, and
    ``tests/test_a_sanitiser_earns_its_entry.py`` now runs this function --
    with every other function claiming a sanitiser name -- against an
    adversarial table and refuses to let an unenrolled claimant exist.

    NOTHING IS LOST THAT A VERDICT USED. The old rendering fed no verdict: it
    was assigned once and printed once. Whether LinkedIn KEPT THE KEY is
    answered by :func:`_key_kept`, against a module-level constant, computed
    four lines above the call site.

    **THAT FIELD WAS CALLED ``survived`` WHEN THIS DOCSTRING WAS WRITTEN AND
    THE RENAME IS NOT COSMETIC.** "Survived" was read as evidence the filter
    was HONOURED; it is not. ``f_JT=ZZ`` -- a job-type value the filter has
    never had -- survived VERBATIM and was inert on every other channel, while
    ``f_ZZQQX`` was STRIPPED. So the channel measures whether LinkedIn
    RECOGNISES THE KEY, and the name now says that and only that.
    """
    landed = urlsplit(str(landed_url or "")).query
    if not landed:
        return "(no query)"

    carried: set[str] = set()
    unrecognised = 0
    for pair in landed.split("&"):
        if not pair:
            continue
        # THE KEY IS TESTED FOR MEMBERSHIP AND OTHERWISE ONLY COUNTED. This is
        # the half the old function printed, and printing it is what let a
        # valueless pair smuggle a token through the key position.
        key = pair.partition("=")[0]
        if key in QUERY_KEYS_PRINTABLE:
            carried.add(key)
        else:
            unrecognised += 1

    asked = {
        pair.partition("=")[0]
        for pair in urlsplit(str(requested_url or "")).query.split("&")
        if pair
    }
    # A SET DIFFERENCE OVER KEYS THIS FILE PUT IN THE ADDRESS. `asked` comes
    # from a module-level literal in LOADS/PASS2_LOADS, never from the page,
    # so naming a dropped key names nothing the browser chose.
    dropped = sorted(asked - {p.partition("=")[0] for p in landed.split("&") if p})

    return (
        "printable keys carried: %s; %d further pair(s) withheld; "
        "asked-for keys dropped: %s"
        % (", ".join(sorted(carried)) or "none",
           unrecognised,
           ", ".join(dropped) or "none")
    )


def _state_text(values: list) -> str:
    """One button's aria state, as a fixed-width reading.

    ``-`` means the attribute is ABSENT, which is a different fact from an
    attribute present and reading ``false``. Collapsing them would delete the
    vocabulary this whole probe needs: a pill that GAINS ``aria-pressed`` when
    a parameter is honoured is exactly an absent-to-present transition.
    """
    parts = []
    for attribute, value in zip(ARIA_STATE_ATTRS, values):
        short = attribute.replace("aria-", "")
        parts.append("%s=%s" % (short, "-" if value is None else str(value)))
    return " ".join(parts)


def _button_reading(records) -> dict:
    """THE WHOLE BUTTON READING, from raw ``(name, aria-values)`` pairs. PURE.

    **THE JUDGEMENT IS SEPARATED FROM THE I/O SO IT CAN BE TESTED WITHOUT A
    BROWSER**, which is the only reason the gate ladder below is checkable at
    all. ``tests/test_probe_filter_channels.py`` feeds this function synthetic
    controls -- including the one shape that broke the probe -- and needs no
    live page to prove what the gates do.

    TWO CHANNELS COME OUT OF ONE WALK, and keeping them apart is the fix:

    * ``states`` -- THE ARIA CHANNEL. Name to aria state, for controls
      carrying at least one of the three aria attributes (gate 1).
    * ``names`` -- THE NAME-PRESENCE CHANNEL. Every named control that passed
      gates 2 and 3, WHATEVER its aria state. Gate 1 does not apply.

    **WHY THE SECOND EXISTS, MEASURED RATHER THAN IMAGINED.** ``Reset selected
    Job type`` -- the single control that evidences ``f_JT`` having applied --
    carries ``pressed=- checked=- expanded=-``. Gate 1 excluded it, so
    ``_differing_names`` returned ``(none)`` for ``f_JT=F`` and that zero was
    read as a negative. A zero from a gate that cannot see the control is not
    a negative reading.

    ``no_aria_state`` COUNTS EVERY WALKED CONTROL LACKING ARIA STATE, counted
    BEFORE the name gates rather than after. It used to be incremented in two
    of the three branches, so a control with a 60-character name and no aria
    state fell out of the denominator entirely -- an undercount in the one
    number whose whole job is to say how blind the aria channel was. The count
    therefore OVERLAPS ``nameless`` and ``too_long`` by construction, and the
    emitted line says so rather than leaving a reader to subtract.
    """
    result = {
        "total": 0,
        "walked": 0,
        "truncated": False,
        "no_aria_state": 0,
        "nameless": 0,
        "too_long": 0,
        "unread": 0,
        "named": 0,
        "states": {},
        "names": frozenset(),
        "needle_hits": [],
        "needle_withheld": 0,
        "failed": "",
    }
    states: dict[str, set] = {}
    hits: dict[str, set] = {}
    names: set[str] = set()

    for raw, values in records:
        result["walked"] += 1
        has_state = not all(one is None for one in values)
        if not has_state:
            # COUNTED HERE, BEFORE ANY NAME GATE CAN SWALLOW IT.
            result["no_aria_state"] += 1
        name = " ".join(str(raw or "").split())
        if not name:
            result["nameless"] += 1
            continue
        if len(name) >= NAME_LIMIT:
            result["too_long"] += 1
            continue
        # GATE 2. The repository owns this shaper, so a urn, a member path, a
        # company path or a long digit run cannot ride through inside a name
        # that passed the gates above.
        safe = shape.census_shape(name)
        if not safe:
            result["nameless"] += 1
            continue
        result["named"] += 1
        state = _state_text(values)

        # THE NAME-PRESENCE CHANNEL. No aria condition, deliberately: this is
        # the half gate 1 cannot have.
        names.add(safe)

        # THE NEEDLE SEARCH LOOKS OUTSIDE GATE 1 DELIBERATELY. A job-type
        # control carrying no aria state is exactly what the hypothesis
        # predicts, so a search confined to aria-carrying controls would
        # confirm that hypothesis by construction rather than test it.
        lowered = safe.lower()
        if any(needle in lowered for needle in JT_NEEDLES):
            if has_state or len(safe) < NEEDLE_NAME_LIMIT:
                hits.setdefault(safe, set()).add(state)
            else:
                result["needle_withheld"] += 1

        if not has_state:
            continue
        states.setdefault(safe, set()).add(state)

    result["states"] = {key: frozenset(value) for key, value in states.items()}
    result["names"] = frozenset(names)
    result["needle_hits"] = sorted(
        (key, sorted(value)) for key, value in hits.items()
    )
    return result


async def _read_buttons(page) -> dict:
    """Walk every ``<button>``, hand the raw pairs to :func:`_button_reading`.

    THIS FUNCTION DOES THE I/O AND NOTHING ELSE. Every gate, every count and
    both channels live in the pure function above, where a test can reach them
    without a browser and without a network.
    """
    buttons = page.locator("button")
    try:
        total = int(await buttons.count())
    except Exception as exc:
        empty = _button_reading([])
        empty["failed"] = type(exc).__name__
        return empty

    limit = min(total, MAX_BUTTONS)
    records: list[tuple[str, list]] = []
    unread = 0
    for index in range(limit):
        control = buttons.nth(index)
        try:
            values = []
            for attribute in ARIA_STATE_ATTRS:
                values.append(await control.get_attribute(attribute))
            raw = await control.get_attribute("aria-label")
            if not raw:
                raw = await control.inner_text()
        except Exception:
            unread += 1
            continue
        records.append((raw, values))

    result = _button_reading(records)
    result["total"] = total
    result["truncated"] = total > MAX_BUTTONS
    result["unread"] = unread
    return result


def _differing_names(baseline: dict, other: dict) -> list[str]:
    """Names whose ARIA STATE is not the same in the two loads.

    A name PRESENT in one and ABSENT in the other counts as differing, which
    is the case a set-of-pairs difference would report twice and a
    key-intersection would miss entirely: a pill that changes its accessible
    name when a filter applies leaves one key and arrives as another.

    **THIS IS THE ARIA CHANNEL AND IT IS STRUCTURALLY BLIND TO A CONTROL THAT
    CARRIES NO ARIA STATE.** It cannot be read alone: an empty result here
    means "nothing this channel can see changed", never "nothing changed".
    :func:`_name_presence_delta` is the other half, and :func:`_aria_absence`
    is why an absence here cannot be printed without its denominator.
    """
    left = baseline.get("states") or {}
    right = other.get("states") or {}
    names = set(left) | set(right)
    return sorted(name for name in names if left.get(name) != right.get(name))


def _name_presence_delta(baseline: dict, other: dict) -> dict:
    """Names that APPEARED or DISAPPEARED between two loads. ARIA IGNORED.

    **THE CHANNEL THE ARIA GATE CANNOT HAVE, and it exists because of a
    measured false negative rather than a worry.** On the live run ``f_JT=F``
    drew ``Reset selected Job type`` -- a control absent from baseline, and
    the only one on the page evidencing that the job-type filter applied. It
    carries ``pressed=- checked=- expanded=-``, so it could not enter
    ``states``, and the aria channel reported ``(none)``. On this channel it
    reads as APPEARED.

    Reported SEPARATELY from the aria channel and never merged into it. They
    answer different questions, and a reader who cannot tell which one spoke
    is back to a number with no denominator.
    """
    left = set(baseline.get("names") or ())
    right = set(other.get("names") or ())
    return {"appeared": sorted(right - left), "disappeared": sorted(left - right)}


def _aria_absence(buttons: dict) -> str:
    """WHAT AN EMPTY ARIA-CHANNEL READING IS ALLOWED TO SAY.

    **A BARE ``(none)`` IS NOT ON THE LIST, AND THAT IS THE WHOLE POINT.**
    Pass one printed ``(none)`` for ``f_JT=F`` while 51 controls on that page
    carried no aria state: the zero was a fact about the gate and it was read
    as a fact about the page. Every absence now carries the count of what the
    channel could not see -- a denominator, exactly like the endorsement
    reading elsewhere in this repository.

    FAILS CLOSED. Handed no reading at all it says so, rather than claiming
    the channel saw everything.
    """
    if not buttons:
        return ("(none on the aria channel; NO BUTTON READING WAS TAKEN, so "
                "this absence has no denominator at all)")
    blind = int(buttons.get("no_aria_state") or 0)
    if blind == 1:
        return ("(none on the aria channel; 1 control carries no aria state "
                "and is invisible to it)")
    if blind:
        return ("(none on the aria channel; %d controls carry no aria state "
                "and are invisible to it)" % blind)
    return ("(none on the aria channel; every control walked carried an aria "
            "state, so this absence has a full denominator)")


def _cell(names: list[str], buttons: dict) -> str:
    """The differing-pill column, bounded so one row cannot become a page.

    ``buttons`` IS REQUIRED AND CARRIES NO DEFAULT, deliberately. A default
    would let a caller print an absence with no denominator by forgetting an
    argument, which is exactly the failure this exists to make impossible.
    Omitting it is a TypeError, not a quieter table.
    """
    if not names:
        return _aria_absence(buttons)
    shown = names[:MAX_NAMED_IN_CELL]
    text = "; ".join(shown)
    if len(names) > len(shown):
        text += "; ... (%d more)" % (len(names) - len(shown))
    return text


def _key_kept(parameter: str, landed_url: str) -> dict:
    """Did the landed url still carry the pair this file asked for?

    **THIS MEASURES WHETHER LINKEDIN RECOGNISES THE KEY. IT DOES NOT MEASURE
    WHETHER THE VALUE WAS APPLIED, AND NOTHING MAY READ IT AS HONOURED.**
    ``f_JT=ZZ`` -- a job-type value the filter has never had -- was kept
    VERBATIM and was inert on every other channel (+0 buttons, identical to
    BASELINE and to the negative control), while ``f_ZZQQX`` was STRIPPED.
    Those two facts together are the entire content of this channel.

    **THE COMPARISON IS NORMALISED, AND THE RAW ONE PRODUCED A FALSE
    NEGATIVE.** This was ``parameter in landed_url``, a raw substring test,
    and it reported ``f_JT=F,C`` as NOT surviving for one reason only:
    LinkedIn percent-encoded the comma and returned ``f_JT=F%2CC``, which was
    accepted. Both sides are decoded before they are compared.

    NO LANDED VALUE IS RETURNED OR PRINTED -- only integers and strings this
    file authored. That is :func:`_shape_of`'s ruling and it binds here: a
    cold verifier measured that no charset or length rule separates a vanity
    slug from an enum, so the encoding is reported as a RELATION (byte
    identical or not, how many characters) rather than by echoing the text.
    """
    asked = parse_qsl(str(parameter or ""), keep_blank_values=True)
    if not asked:
        return {"kept": None, "key": "", "asked_value": "", "asked_chars": 0,
                "key_present": False, "occurrences": 0,
                "byte_identical": False, "landed_chars": 0}

    key, value = asked[0]
    landed_query = urlsplit(str(landed_url or "")).query
    # THE KEY MATCHED AGAINST IS OURS. It comes from parse_qsl over a
    # module-level literal in LOADS / PASS2_LOADS, never from the page, so
    # selecting pairs by it names nothing the browser chose.
    raw_values = [
        pair.partition("=")[2]
        for pair in landed_query.split("&")
        if pair and pair.partition("=")[0] == key
    ]
    decoded = [unquote_plus(one) for one in raw_values]
    return {
        "kept": value in decoded,
        "key": key,
        "asked_value": value,
        "asked_chars": len(value),
        "key_present": bool(raw_values),
        "occurrences": len(raw_values),
        "byte_identical": value in raw_values,
        "landed_chars": max((len(one) for one in raw_values), default=0),
    }


def _key_kept_lines(parameter: str, reading: dict) -> list[str]:
    """The KEY KEPT reading, as lines, printing no landed value.

    **THE WORD HONOURED DOES NOT APPEAR HERE AND MUST NOT.** This channel
    cannot support it; :func:`_key_kept` argues why.
    """
    if reading.get("kept") is None:
        return []
    kept = bool(reading["kept"])
    lines = ["%r KEY KEPT (compared after percent-decoding both sides): %s"
             % (parameter, "YES" if kept else "NO")]
    if not reading["key_present"]:
        lines.append(
            "    the key is ABSENT from the landed query entirely, which is "
            "what a key LinkedIn does not recognise looks like -- f_ZZQQX "
            "reads this way")
    else:
        lines.append(
            "    asked %r (%d chars, a literal in this file); the landed "
            "value %s byte-identical to it (%d chars) and %s identical "
            "after decoding"
            % (reading["asked_value"], reading["asked_chars"],
               "IS" if reading["byte_identical"] else "IS NOT",
               reading["landed_chars"],
               "IS" if kept else "IS NOT"))
    if reading["occurrences"] > 1:
        lines.append("    the key appears %d times in the landed query"
                     % reading["occurrences"])
    if kept:
        lines.append(
            "    THE KEY WAS KEPT; WHETHER THE VALUE WAS APPLIED IS A "
            "DIFFERENT QUESTION AND THIS CHANNEL CANNOT ANSWER IT. f_JT=ZZ "
            "-- a value the job-type filter has never had -- was kept "
            "verbatim and was inert on every other channel.")
    return lines


def _verdict(row: dict, negative_matches: bool) -> str:
    """The PASS ONE reading for one candidate.

    **THIS RULE CONSULTS TWO CHANNELS AND THE RUN PRODUCES FIVE.** It is left
    deliberately narrow rather than widened in place, because widening it on
    the strength of one surprising run is how an instrument gets tuned until
    it agrees with whoever is holding it. Pass two is the widening, done as a
    separate measurement with its own controls.

    **WHAT CHANGED IS THAT IT MAY NO LONGER RETURN A BARE NO-CHANGE.** The
    aria channel drops every control carrying no aria state, so a zero off it
    is a fact about the gate until the size of that drop is stated beside it.
    A no-change reading now carries the count, and a difference on the
    name-presence channel is reported as a CHANGE these two channels could
    not see rather than being folded into silence.
    """
    if not negative_matches:
        return "CANNOT TELL (negative control disagreed with baseline)"
    if row.get("failed"):
        return "CANNOT TELL (the load did not complete)"
    if row["cards_delta"] != 0 or row["differing"]:
        return "HONOURED (on the two channels this rule reads)"

    appeared = row.get("names_appeared") or []
    disappeared = row.get("names_disappeared") or []
    if appeared or disappeared:
        return ("CHANGED ON THE NAME-PRESENCE CHANNEL ONLY (%d name(s) "
                "appeared, %d disappeared) while the aria channel read zero "
                "-- a control carrying no aria state cannot appear on that "
                "channel at all" % (len(appeared), len(disappeared)))

    blind = int((row.get("buttons") or {}).get("no_aria_state") or 0)
    if blind:
        return ("NO CHANGE on the two channels this rule reads, BUT %d "
                "control(s) carry no aria state and are invisible to the "
                "pill channel -- see pass two" % blind)
    return "NO CHANGE on the two channels this rule reads -- see pass two"


async def _one_load(page, emit, label, parameter, url, index) -> dict:
    """Load one address and take every reading. Shared by both passes."""
    row = {
        "label": label,
        "parameter": parameter or "(none)",
        "cards": -1,
        "cards_delta": 0,
        "buttons_delta": 0,
        "differing": [],
        "names_appeared": [],
        "names_disappeared": [],
        "key_kept": None,
        "key_byte_identical": None,
        "failed": "",
        "buttons": None,
        "walled": False,
    }
    emit("--- LOAD %d  %s  [%s]" % (index + 1, label, row["parameter"]))
    try:
        landed_url = await BROWSER.goto(page, url)
    except Exception as exc:
        row["failed"] = type(exc).__name__
        emit("    NAVIGATION FAILED: %s" % type(exc).__name__)
        emit("    (the message is withheld -- BrowserUnavailableError")
        emit("     interpolates the url it could not reach)")
        return row

    # EVERY READING OFF THE LANDED ADDRESS IS EITHER A COMPARISON AGAINST A
    # CONSTANT THIS REPOSITORY AUTHORED, OR A CALL TO _shape_of. A boolean
    # about a url, or a relation over its query -- never the url.
    served_exactly = landed_url == url
    walled = any(marker in landed_url for marker in WALL_MARKERS)
    on_surface = JOBS_SEARCH_PATH in landed_url
    # KEY KEPT, COMPARED AFTER PERCENT-DECODING BOTH SIDES. This was
    # `parameter in landed_url` -- a raw substring test that read `f_JT=F,C`
    # as NOT surviving because LinkedIn returned the comma as `%2C`. The
    # reading carries no landed value, only integers and our own literals.
    kept_reading = _key_kept(parameter, landed_url)
    query_shape = _shape_of(landed_url, url)

    row["walled"] = walled
    if parameter:
        # BOOLEANS, WRITTEN AS COMPARISONS, AND THAT SHAPE IS LOAD-BEARING.
        # `tests/test_navigation_is_never_derived` collects taint per MODULE
        # by NAME rather than per scope, so binding the landed-derived
        # reading itself into `row[...]` taints the name `row` everywhere and
        # cascades to `print`. A comparison yields a boolean whatever it
        # compared, which that engine exempts by design -- and the row really
        # does hold two booleans. The full reading stays local, below.
        row["key_kept"] = kept_reading["kept"] is True
        row["key_byte_identical"] = kept_reading["byte_identical"] is True

    emit("    landed at the exact address asked for: %s"
         % ("YES" if served_exactly else "NO"))
    emit("    still on %s: %s" % (JOBS_SEARCH_PATH, "YES" if on_surface else "NO"))
    emit("    auth wall: %s" % ("YES" if walled else "no"))
    for text in _key_kept_lines(parameter, kept_reading):
        emit("    %s" % text)
    emit("    landed query: %s" % query_shape)

    if walled:
        row["failed"] = "auth wall"
        emit("    AUTH WALL. Not signed in, so nothing was measured here.")
        return row

    try:
        records = await dom.harvest_linked_cards(
            page,
            href_pattern=dom.JOB_HREF,
            max_items=100,
            max_chars=200,
        )
        row["cards"] = len(records)
    except Exception as exc:
        row["failed"] = type(exc).__name__
        emit("    HARVEST FAILED: %s (message withheld -- it can carry a url)"
             % type(exc).__name__)

    buttons = await _read_buttons(page)
    row["buttons"] = buttons

    emit("    job cards harvested: %s"
         % ("n/a" if row["cards"] < 0 else row["cards"]))
    emit("    buttons on the page: %d (walked %d%s)"
         % (buttons["total"], buttons["walked"],
            ", TRUNCATED" if buttons["truncated"] else ""))
    emit("    of those, carrying an aria state and named: %d"
         % len(buttons["states"]))
    emit("    invisible to the aria channel: %d carried no aria state "
         "(this count OVERLAPS the three that follow -- it is every walked "
         "control lacking aria state, whatever else dropped it)"
         % buttons["no_aria_state"])
    emit("    also dropped: %d nameless, %d name >= %d chars, %d unreadable"
         % (buttons["nameless"], buttons["too_long"], NAME_LIMIT,
            buttons["unread"]))
    emit("    NAME-PRESENCE CHANNEL carried: %d distinct named control(s), "
         "aria state ignored" % len(buttons["names"]))
    if buttons["failed"]:
        emit("    BUTTON WALK FAILED: %s" % buttons["failed"])
    return row


def _compare_to_baseline(rows: list[dict], row: dict, emit) -> None:
    """Fill in the deltas against this pass's own baseline, and print them."""
    base = rows[BASELINE_INDEX]
    if base["cards"] >= 0 and row["cards"] >= 0:
        row["cards_delta"] = row["cards"] - base["cards"]
    if base["buttons"] and row["buttons"]:
        row["buttons_delta"] = row["buttons"]["total"] - base["buttons"]["total"]
    row["differing"] = _differing_names(base["buttons"] or {}, row["buttons"] or {})
    presence = _name_presence_delta(base["buttons"] or {}, row["buttons"] or {})
    row["names_appeared"] = presence["appeared"]
    row["names_disappeared"] = presence["disappeared"]

    emit("    card delta vs BASELINE: %+d" % row["cards_delta"])
    emit("    button delta vs BASELINE: %+d" % row["buttons_delta"])

    emit("    ARIA CHANNEL -- pills whose aria state differs from BASELINE: %d"
         % len(row["differing"]))
    if not row["differing"]:
        emit("        %s" % _aria_absence(row["buttons"] or {}))
    for name in row["differing"][:MAX_NAMED_IN_CELL]:
        left = sorted((base["buttons"] or {}).get("states", {}).get(name, ()))
        right = sorted((row["buttons"] or {}).get("states", {}).get(name, ()))
        emit("        %-40s baseline=%s  here=%s"
             % (name, left or "ABSENT", right or "ABSENT"))

    # THE SECOND CHANNEL, REPORTED SEPARATELY AND NEVER MERGED INTO THE
    # FIRST. This is where a control carrying no aria state -- `Reset
    # selected Job type`, the one that evidences f_JT applying -- can appear
    # at all.
    emit("    NAME-PRESENCE CHANNEL -- names appeared: %d, disappeared: %d "
         "(aria state ignored; this channel sees every named control)"
         % (len(presence["appeared"]), len(presence["disappeared"])))
    for name in presence["appeared"][:MAX_NAMED_IN_CELL]:
        emit("        APPEARED     %s" % name)
    for name in presence["disappeared"][:MAX_NAMED_IN_CELL]:
        emit("        DISAPPEARED  %s" % name)


async def _pass_one(page, emit, first_overall) -> tuple:
    emit()
    emit("=============================================================")
    emit("=== PASS ONE -- THE FIVE CANDIDATES, SEVEN LOADS")
    emit("=============================================================")
    rows: list[dict] = []
    stopped = ""
    negative_matches = False

    for index, (label, parameter, url) in enumerate(LOADS):
        if index or not first_overall:
            await asyncio.sleep(SLEEP_BETWEEN_LOADS_S)
        row = await _one_load(page, emit, label, parameter, url, index)
        rows.append(row)

        if row["walled"]:
            stopped = "an auth wall interrupted pass one"
            break
        if row["failed"] and index == BASELINE_INDEX:
            stopped = "pass one's baseline load failed"
            break
        if index == BASELINE_INDEX:
            emit("    (this is the baseline every later load is read against)")
            continue

        _compare_to_baseline(rows, row, emit)

        if index == NEGATIVE_INDEX:
            same_cards = row["cards_delta"] == 0 and row["cards"] >= 0
            same_pills = not row["differing"]
            negative_matches = same_cards and same_pills
            emit()
            emit("=== PASS ONE NEGATIVE CONTROL'S VERDICT")
            emit("    card count identical to baseline: %s"
                 % ("YES" if same_cards else "NO"))
            emit("    pill states identical to baseline: %s"
                 % ("YES" if same_pills else "NO"))
            if negative_matches:
                emit("    THE INSTRUMENT DISCRIMINATES. A parameter LinkedIn")
                emit("    has never had changed nothing, so 'identical to")
                emit("    baseline' now MEANS ignored.")
            else:
                emit("    PASS ONE CANNOT DISCRIMINATE. A parameter LinkedIn")
                emit("    has never had came back DIFFERENT from baseline, so")
                emit("    the page varies between loads on its own. STOPPING")
                emit("    pass one rather than calling five more readings")
                emit("    evidence. PASS TWO STILL RUNS -- separate controls.")
                stopped = "pass one's negative control disagreed with baseline"
                break
            emit()

    return rows, negative_matches, stopped


async def _pass_two(page, emit) -> tuple:
    emit()
    emit("=============================================================")
    emit("=== PASS TWO -- SETTLING f_JT ON ITS OWN, SIX LOADS")
    emit("=============================================================")
    rows: list[dict] = []
    stopped = ""
    diagnosis: list[str] = []

    for index, (label, parameter, url) in enumerate(PASS2_LOADS):
        await asyncio.sleep(SLEEP_BETWEEN_LOADS_S)
        row = await _one_load(page, emit, label, parameter, url, index)
        rows.append(row)

        buttons = row["buttons"] or {}
        hits = buttons.get("needle_hits") or []
        emit("    controls whose name contains %s: %d"
             % (", ".join(repr(one) for one in JT_NEEDLES), len(hits)))
        for name, state_list in hits:
            emit("        MATCH  %-38s %s" % (name, state_list))
        if buttons.get("needle_withheld"):
            emit("        (%d further match(es) withheld: no aria state and a"
                 % buttons["needle_withheld"])
            emit("         name of %d+ chars, so possibly card text)"
                 % NEEDLE_NAME_LIMIT)
        emit("    THE SEARCHED INVENTORY (every aria-carrying named control):")
        inventory = sorted(buttons.get("states") or {})
        if inventory:
            for name in inventory:
                emit("        %-40s %s" % (name, sorted(buttons["states"][name])))
        else:
            emit("        (empty -- so a zero above says nothing was searched)")

        if row["walled"]:
            stopped = "an auth wall interrupted pass two"
            break

        if index == BASELINE_INDEX:
            # THE JOB_HREF DIAGNOSIS. One extra measurement on a page that is
            # being loaded anyway, because pass one's card channel returned 7
            # on every one of seven loads and an inert channel deserves a
            # cause rather than a shrug.
            emit()
            emit("=== dom.JOB_HREF DIAGNOSIS (pass two baseline page)")
            emit("    dom.JOB_HREF = %s" % dom.JOB_HREF)
            try:
                anchors = int(await page.locator(JOB_VIEW_ANCHOR).count())
            except Exception as exc:
                anchors = -1
                emit("    anchor count FAILED: %s" % type(exc).__name__)
            try:
                all_anchors = int(await page.locator("a[href]").count())
            except Exception:
                all_anchors = -1
            emit("    anchors matching %s: %d" % (JOB_VIEW_ANCHOR, anchors))
            emit("    anchors with any href on the page: %d" % all_anchors)
            emit("    harvest_linked_cards returned: %d" % row["cards"])
            if anchors >= 0 and row["cards"] >= 0:
                if anchors == row["cards"]:
                    diagnosis.append(
                        "THE PAGE DRAWS ONLY %d /jobs/view/ ANCHORS. The "
                        "harvest is not finding the wrong set -- it is finding "
                        "all there are, so the results list is not in the DOM "
                        "this read sees (virtualised, or behind a scroll this "
                        "probe does not perform)." % anchors)
                else:
                    diagnosis.append(
                        "THE HARVEST IS FINDING THE WRONG SET. %d anchors on "
                        "the page match /jobs/view/ but harvest_linked_cards "
                        "returned %d, so dom.JOB_HREF or the card walk is "
                        "dropping %d of them."
                        % (anchors, row["cards"], anchors - row["cards"]))
            emit("    %s" % (diagnosis[0] if diagnosis else "inconclusive"))
            emit()
            emit("    (this is pass two's own baseline, re-taken)")
            continue

        _compare_to_baseline(rows, row, emit)

    return rows, stopped, diagnosis


def _jt_reading(rows: list[dict]) -> list[str]:
    """THE f_JT VERDICT, in the vocabulary that was asked for and no other.

    The decision rests on ONE comparison, and it is not ``f_JT=F`` against
    baseline. It is ``f_JT=ZZ`` -- a value the filter has never had -- against
    ``f_JT=F``. KEY KEPT alone cannot separate "LinkedIn understood f_JT" from
    "LinkedIn keeps anything spelled f_something", and only a value-level
    control can. **THE ONE HONOURED THIS FILE STILL PRINTS IS PRINTED HERE,
    AND IT RESTS ON THAT CONTROL RATHER THAN ON KEY SURVIVAL** -- the key
    being kept is a precondition it states separately, never the evidence.

    ``f_JT=F,C`` IS REPORTED AS TWO QUESTIONS BECAUSE IT IS TWO. Whether the
    key was kept is now settled (it was; an earlier run said otherwise only
    because the comma came back percent-encoded). Whether BOTH values applied
    is NOT settled and is not settleable from these loads.
    """
    out: list[str] = []
    by_parameter = {row["parameter"]: row for row in rows}
    full = by_parameter.get("f_JT=F")
    control = by_parameter.get("f_JT=ZZ")
    if not full or not control:
        return ["CANNOT TELL -- f_JT=F and/or f_JT=ZZ were never loaded."]
    if full.get("failed") or control.get("failed"):
        return ["CANNOT TELL -- one of the two decisive loads did not complete."]

    kept_full = bool(full.get("key_kept"))
    kept_control = bool(control.get("key_kept"))
    same_cards = full["cards_delta"] == control["cards_delta"]
    same_buttons = full["buttons_delta"] == control["buttons_delta"]
    same_pills = sorted(full["differing"]) == sorted(control["differing"])
    identical = same_cards and same_buttons and same_pills

    out.append("f_JT=F  KEY KEPT (after decoding): %s"
               % ("YES" if kept_full else "NO"))
    out.append("f_JT=ZZ KEY KEPT (after decoding): %s"
               % ("YES" if kept_control else "NO"))
    out.append("    -- KEY KEPT means LinkedIn RECOGNISED THE KEY. It is not")
    out.append("       evidence the VALUE was applied, which is exactly why")
    out.append("       the f_JT=ZZ control below decides and this line does")
    out.append("       not.")
    out.append("f_JT=ZZ vs f_JT=F -- cards same: %s, buttons same: %s, "
               "pills same: %s" % (same_cards, same_buttons, same_pills))

    if kept_full and not identical:
        out.append("VERDICT: HONOURED -- AND NOT ON THE KEY-KEPT CHANNEL.")
        out.append("The key being kept is a precondition, stated above. THE")
        out.append("EVIDENCE IS THE VALUE-LEVEL CONTROL: f_JT=ZZ behaves")
        out.append("differently from a real value, so what separates them is")
        out.append("the VALUE and not the f_ prefix. Key survival alone would")
        out.append("not support this word and does not carry it.")
    elif kept_control and identical:
        out.append("VERDICT: DISBELIEVED. f_JT=ZZ is kept and looks identical")
        out.append("to f_JT=F, so LinkedIn keeps any f_-prefixed pair and the")
        out.append("key-kept channel is measuring the PREFIX. It proves")
        out.append("nothing about f_JT.")
    else:
        out.append("VERDICT: CANNOT TELL. Neither pattern was produced --")
        out.append("see the three readings above for which half is missing.")

    out.extend(_jt_multi_value_reading(by_parameter.get("f_JT=F,C"), full))
    return out


def _jt_multi_value_reading(multi: dict, full: dict) -> list[str]:
    """``f_JT=F,C`` -- TWO QUESTIONS, ANSWERED SEPARATELY AND BOTH SAID OUT.

    **FIXING THE KEY-KEPT COMPARISON SETTLED THE ENCODING AND NOTHING ELSE,
    AND THIS FUNCTION EXISTS SO THAT CANNOT BE MISREAD.** The old raw
    substring test reported ``f_JT=F,C`` as not surviving purely because
    LinkedIn returned ``f_JT=F%2CC``; normalising the comparison corrects a
    FALSE NEGATIVE about the key. It says nothing whatever about whether BOTH
    values were applied, and a reader who saw only a NO become a YES would
    reasonably assume it did.

    THE SECOND QUESTION STAYS CANNOT TELL. The button delta for two values was
    identical to single-value ``f_JT=F``, which does not separate "both
    applied" from "only the first applied" -- and no control in this pass can,
    because the reading that would is a per-value control taken on the same
    load, which this probe does not take.
    """
    if not multi or multi.get("failed"):
        return ["", "f_JT=F,C -- not loaded, or its load did not complete."]

    out = ["", "f_JT=F,C -- TWO QUESTIONS, ANSWERED SEPARATELY:"]
    out.append("  (1) KEY KEPT: %s. Compared after percent-decoding both"
               % ("YES" if multi.get("key_kept") else "NO"))
    out.append("      sides; the landed value %s byte-identical to the"
               % ("IS" if multi.get("key_byte_identical") else "IS NOT"))
    out.append("      literal this file asked for.")
    out.append("      AN EARLIER RUN READ THIS AS 'NO' PURELY BECAUSE THE")
    out.append("      COMMA CAME BACK PERCENT-ENCODED. That was a false")
    out.append("      negative from a raw substring test, and correcting it")
    out.append("      SETTLED THE ENCODING AND NOTHING ELSE.")
    out.append("  (2) DID BOTH VALUES APPLY: CANNOT TELL, and it stays")
    out.append("      CANNOT TELL. Its button delta (%+d) is %s single-value"
               % (multi.get("buttons_delta", 0),
                  "IDENTICAL TO"
                  if multi.get("buttons_delta") == full.get("buttons_delta")
                  else "DIFFERENT FROM"))
    out.append("      f_JT=F (%+d), which does not separate 'both applied'"
               % full.get("buttons_delta", 0))
    out.append("      from 'only the first applied'. NO CONTROL IN THIS PASS")
    out.append("      SEPARATES THEM: the reading that would is a per-value")
    out.append("      control on the same load, and this probe takes none.")
    return out


async def main() -> None:
    lines: list[str] = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit("=== DOES LINKEDIN HONOUR THE JOB-SEARCH FILTER PARAMETERS?")
    emit("    two passes, one session, one fixed keyword, nothing pressed")
    emit("    keyword (fixed for all thirteen loads): %r" % KEYWORD_TEXT)
    emit("    card COUNTS only -- no title, no employer, no job id is printed")
    emit("    the landed query is reported as a RELATION (_shape_of):")
    emit("    our key names and counts only -- no value is ever read")

    p1_rows: list[dict] = []
    p2_rows: list[dict] = []
    p1_negative = False
    p1_stopped = ""
    p2_stopped = ""
    diagnosis: list[str] = []

    try:
        await BROWSER.start()
    except Exception as exc:
        # The local profile lock and the launch failures both land here. The
        # message names a directory on this box, never a LinkedIn identity, so
        # it is printed -- a lock report that will not say what is locked is
        # the report nobody can act on.
        emit("    COULD NOT START THE BROWSER: %s: %s"
             % (type(exc).__name__, str(exc)[:300]))
        emit("    THAT IS THE RESULT. Nothing was measured. If this is the")
        emit("    cross-process profile lock, another process holds the")
        emit("    profile -- this probe does not retry and kills nothing.")
        _write(lines)
        return

    try:
        async with BROWSER.session() as page:
            p1_rows, p1_negative, p1_stopped = await _pass_one(page, emit, True)
            p2_rows, p2_stopped, diagnosis = await _pass_two(page, emit)
    except Exception as exc:
        emit("    THE RUN RAISED: %s (message withheld)" % type(exc).__name__)
        p2_stopped = p2_stopped or "the session raised %s" % type(exc).__name__
    finally:
        await BROWSER.stop()

    emit()
    emit("=== PASS ONE TABLE")
    emit("    %-22s %-14s %6s %7s  %s"
         % ("LOAD", "PARAMETER", "CARDS", "DELTA", "PILLS DIFFERING FROM BASELINE"))
    for index, row in enumerate(p1_rows):
        cards = (row["failed"] if (row["failed"] and row["cards"] < 0)
                 else str(row["cards"]))
        delta = "n/a" if index == BASELINE_INDEX else "%+d" % row["cards_delta"]
        emit("    %-22s %-14s %6s %7s  %s"
             % (row["label"][:22], row["parameter"][:14], cards, delta,
                "(baseline)" if index == BASELINE_INDEX
                else _cell(row["differing"], row["buttons"] or {})))
    if len(p1_rows) < len(LOADS):
        emit("    %d load(s) NOT TAKEN -- %s"
             % (len(LOADS) - len(p1_rows), p1_stopped or "stopped"))

    emit()
    emit("=== PASS ONE READING, ONE LINE PER CANDIDATE")
    for index, row in enumerate(p1_rows):
        if index in (BASELINE_INDEX, NEGATIVE_INDEX):
            continue
        emit("    %-22s %-14s %s"
             % (row["label"][:22], row["parameter"][:14],
                _verdict(row, p1_negative)))

    emit()
    emit("=== PASS TWO TABLE")
    emit("    %-22s %-12s %8s %8s %8s %6s  %s"
         % ("LOAD", "PARAMETER", "KEY KEPT", "BUTTONS", "B-DELTA", "CARDS",
            "JT-MATCHED CONTROLS"))
    for index, row in enumerate(p2_rows):
        buttons = row["buttons"] or {}
        kept = ("n/a" if row["key_kept"] is None
                else ("YES" if row["key_kept"] else "NO"))
        hits = buttons.get("needle_hits") or []
        emit("    %-22s %-12s %8s %8s %8s %6s  %s"
             % (row["label"][:22], row["parameter"][:12], kept,
                buttons.get("total", "n/a"),
                "n/a" if index == BASELINE_INDEX else "%+d" % row["buttons_delta"],
                row["cards"] if row["cards"] >= 0 else "n/a",
                "; ".join(name for name, _s in hits) or "(no needle match)"))
    if len(p2_rows) < len(PASS2_LOADS):
        emit("    %d load(s) NOT TAKEN -- %s"
             % (len(PASS2_LOADS) - len(p2_rows), p2_stopped or "stopped"))

    emit()
    emit("=== f_JT READING")
    for text in _jt_reading(p2_rows):
        emit("    %s" % text)

    emit()
    emit("=== dom.JOB_HREF DIAGNOSIS")
    emit("    %s" % (diagnosis[0] if diagnosis else "not taken"))

    _write(lines)


def _write(lines: list[str]) -> None:
    """Put the report on disk, in the one directory that is always ignored."""
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="ascii")
    print("\n    findings written to %s" % OUT_PATH)


# GUARDED: importing a script must not DO anything.
# tests/test_scripts_are_import_safe.py asserts this for every file in scripts/.
if __name__ == "__main__":
    asyncio.run(main())
