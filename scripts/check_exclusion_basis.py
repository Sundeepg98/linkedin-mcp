"""Every row outside the census denominator: who ruled it out, and can you find the ruling?

THE QUESTION. ``scripts/census_completion.py`` removes two states from the
achievable surface -- EXCLUDED-RULED and MEASURED-ABSENT -- and plans on what is
left. So the "pending" figure is only as exact as those exclusions are real. Nobody
had checked who ruled each one. The census's own bar for EXCLUDED-RULED
(``EXCLUDED-RULED-ADMISSION`` in ``_audit/RULINGS.md``) names FOUR written grounds
and says nothing about WHO wrote them; the register records rulings without their
author; and a grep of the census found 345 lines for 308 rows.

``_audit/_census/exclusion-basis.tsv`` is the answer, one line per out-of-scope
row. This file keeps it TRUE, and exits 1 when:

  * an EXCLUDED-RULED row is class C -- NO TRACEABLE BASIS. This is the failure
    the file exists for. It is RED AT THE COMMIT THAT SHIPPED IT, deliberately:
    whether a C row returns to GAP is the operator's decision, and a check that
    went green by relabelling his open question would certify nothing;
  * an EXCLUDED-RULED row is class A-lifted or B-lifted -- its basis is
    traceable and its maker has WITHDRAWN it. The operator's ruling (b) of
    2026-09-23 lifted three bases (``LIFTED``); a row resting on one is pending
    work the census hides, reported under its own heading and never folded
    into the untraced count, because the two call for different acts;
  * the table does not cover the population EXACTLY -- a row that ENTERED an
    out-of-scope state carries no traced basis; a row that LEFT one leaves a
    basis pointing at nothing;
  * a B or A row names a family this file does not know, or claims an operator
    verdict (``op=``) different from the one the family records;
  * a B or A row's basis cannot be reached FROM THE ROW -- none of its family's
    citation tokens occurs in the row's resolved census text, and no roll-up
    passage names its id. A table that asserts a link the census does not carry
    is a second, unaudited census;
  * a cited source does not resolve: the file is missing, or its anchor text no
    longer occurs in it. Anchors are VERBATIM TEXT, never line numbers, because a
    line-number citation rots into a plausible wrong answer rather than a
    dangling one (``CANONICAL-RULING-ID``);
  * a family's own registered sources do not resolve.

THE CLASSES, stated so they can be argued with.

  A    The operator's own ruling reaches THIS ROW -- it names the capability or
       the exact act or address -- with no agent step between the ruling and the
       row. Quote him.
  B    An agent placed the row under a FAMILY or AREA ruling (an act-class, an
       address family, a code refusal, a retirement family). Two flags carry the
       judgement the operator needs:
         op=     YES       the operator's recorded words establish the family
                 NO        no operator words on record for this family
                 CONTRARY  an operator ruling or instruction on record, or the
                           document recording it, classes this capability or
                           family as something to BUILD or MEASURE
         scope=  YES       the family's own words plainly reach the row
                 EXTENDED  the row is inside only by an agent's widening
                 NO        the family's own words do not make it an exclusion
                           of this row (a refusal that is conditional on an
                           unmeasured state; a measurement of a narrower object)
  C    No traceable basis: nothing written is cited (NONE); only allowlist
       silence or an unmeasured state (SILENCE); the only ground is recorded
       false at HEAD (REFUTED); a registered ruling names the row, or its exact
       address class, and says it stays GAP (OVERRULED); or the citation does
       not resolve from a clone (DANGLING).
  A-lifted / B-lifted
       As A or B, and the basis is one the operator has since withdrawn.
       ``lifted=`` names which of ``LIFTED``; ``remaining=`` names a family that
       still holds the row, or ``-``. Every such row cites ``LIFT_SOURCE``.
  M+   MEASURED-ABSENT, the measurement recorded in a TRACKED document.
  M-   MEASURED-ABSENT, the measurement missing from the tracked corpus, or
       recorded there as not establishing absence.

IT IMPORTS THE SHIPPED PARSE AND ADDS NONE OF ITS OWN. The population is
``census_completion.walk()`` folded by its own ``FOLD`` and ``OUT_OF_SCOPE``; the
resolved text of each row -- own cell, positional backreference donor, network
R-code body, section heading -- is ``classify_writeoff_reasons.build()``. The two
shipped walks are cross-checked and any disagreement is a problem, because a
table checked against a walk that drifted is checked against nothing.

WHAT IT DOES NOT CHECK. The CLASS of a row is a judgement recorded in the table;
this file checks that the judgement cites something real and reachable, not that
it is the right judgement. ``op=`` is checked against this file's registry, and
the registry's operator attributions are only as good as the passages they quote
-- those passages are checked to EXIST, not to be true. A cold re-classification
of a random sample is the only check on the judgement itself; its agreement rate
is in ``_audit/2026-09-23-exclusion-audit.md``.

SHOWN FAILING: ``tests/test_exclusion_basis.py`` plants each failure above into
built fixtures and into a COPY of the real table, and asserts each is red and
names its row.

    python scripts/check_exclusion_basis.py
    python scripts/check_exclusion_basis.py --summary     # counts, then the verdict
    python scripts/check_exclusion_basis.py --table <a copy>
"""
from __future__ import annotations

import argparse
import collections
import dataclasses
import pathlib
import re
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

ROOT = _HERE.parent
TABLE = ROOT / "_audit" / "_census" / "exclusion-basis.tsv"

COLUMNS = ("slice", "row", "state", "class", "basis", "source")
ER, MA = "EXCLUDED-RULED", "MEASURED-ABSENT"
CLASSES = {ER: ("A", "B", "C", "A-lifted", "B-lifted"), MA: ("M+", "M-", "C")}
#: The three bases the operator's ruling (b) of 2026-09-23 withdrew. A row
#: resting on one is class A-lifted or B-lifted, and it FAILS the run under its
#: own heading: its basis is traceable and no longer stands, so it is pending
#: work the census hides. The ruling reached this repository as a relay, and
#: its only tracked record is LIFT_SOURCE, which every lifted row must cite.
LIFTED = ("READ-ONLY-NO-WRITES", "APPLY-CONNECT-INMAIL-CUT", "DO-NOT-OPEN-MESSAGING")
LIFT_SOURCE = ("_audit/2026-09-23-exclusion-audit.md",
               "At 18:15 the OPERATOR ruled \"(b)\": the linkedin MCP may connect, message,")
OPS = ("YES", "NO", "CONTRARY")
SCOPES = ("YES", "EXTENDED", "NO")
WHYS = ("NONE", "SILENCE", "REFUTED", "OVERRULED", "DANGLING")
EVIDENCE = ("RECORDED", "DISPUTED", "UNRECORDED")
#: A source outside this repository. It is REPORTED as unverifiable from a clone
#: and never counted as the basis on its own: every A/B/M+ row needs one source
#: this repository can resolve.
EXT = "EXT:"


@dataclasses.dataclass(frozen=True)
class Family:
    """One ruling that exclusions are filed under, and how to find it.

    ``link`` are regexes, any of which occurring in a row's resolved census text
    connects the row to the family. ``rollup`` are passages that enumerate row ids
    by name -- the only honest link for a row whose own cell points somewhere else
    by position (``P G3`` reads ``same ruling`` and resolves to a COVERED row).
    """

    fid: str
    title: str
    made_by: str          # OPERATOR | LEAD | WAVE | CODE
    op: str               # YES | NO | CONTRARY
    sources: tuple[tuple[str, str], ...]
    link: tuple[str, ...]
    rollup: tuple[tuple[str, str], ...] = ()


def _f(fid, title, made_by, op, sources, link, rollup=()):
    return Family(fid, title, made_by, op, tuple(sources), tuple(link), tuple(rollup))


_DECIDE = "_audit/2026-09-05-decide-retire-rulings.md"
_QUEUE = ("_audit/2026-09-03-linkedin-gap-blockers.md",
          "Needs his answer, and the answer is almost certainly")
_NET = "_audit/_census/network.md"

#: The twelve blockers `_audit/2026-09-05-decide-retire-rulings.md` RETIRED, each
#: under its own section. The queue they came from was defined by
#: `_audit/2026-09-03-linkedin-gap-blockers.md` as needing HIS answer; the
#: answers were written by a wave. `MESSAGING-SETTINGS` (3.10) is not here: that
#: section re-filed rows under the operator's settings ruling, which is
#: `SETTINGS-BY-NAME` below.
_RETIRED = (
    ("AI-INTERVIEW-PRODUCT", "3.1"), ("CONTACT-IMPORT", "3.2"),
    ("HELP-CENTER-FORM", "3.3"), ("OFF-PLATFORM-WIDGET", "3.4"),
    ("LIVE-BROADCAST", "3.5"), ("AI-ASSIST-MESSAGING", "3.6"),
    ("DEVICE-GEOLOCATION", "3.7"), ("SIGNIN-INTERSTITIAL", "3.8"),
    ("MOBILE-APP-ONLY", "3.9"), ("VOICE-CAPTURE", "3.11"),
    ("PAID-BOOST", "3.12"), ("PANEL-NOT-OBSERVED", "3.13"),
)
_RETIREMENTS = [
    _f(f"RETIRE-{name}", f"retired 2026-09-05 under {name} (section {sec})",
       "WAVE", "NO", [(_DECIDE, f"### {sec} `{name}`"), _QUEUE], [re.escape(name)])
    for name, sec in _RETIRED
]

#: THE REGISTRY. Every family an out-of-scope row is filed under, with who made it
#: and the operator's recorded position. Each attribution is quoted in the audit
#: document; here each is anchored so that a ruling that stops resolving is loud.
FAMILIES: dict[str, Family] = {f.fid: f for f in (
    # ---- rulings the OPERATOR made, applied by an agent to a family ----------
    _f("SETTINGS-BY-NAME",
       "a settings page is admitted one at a time, BY NAME -- never the family",
       "OPERATOR", "YES",
       [("_audit/2026-08-31-linkedin-finish.md", "ONE NAMED settings page below"),
        ("linkedin_server/server.py", "BY NAME on the operator's ruling")],
       [r"\bR11\b", r"MESSAGING-SETTINGS", r"(?i)settings[- ]family",
        r"(?i)admitted by name or not at all", r"ONE SETTING IS WRITABLE",
        r"/mypreferences/d/", r"/psettings/", r"/close-accounts",
        r"/hibernate-account"]),
    _f("NO-THIRD-PARTY-PROFILE-LOAD",
       "no third party's profile is loaded -- boundary narrowed to /in/me/",
       "OPERATOR", "YES",
       [("linkedin_server/readonly.py",
         "THE THIRD-PARTY PROFILE PATTERN WAS REMOVED 2026-09-04, ON THE OPERATOR'S"),
        ("linkedin_server/writes.py",
         '"load_a_third_partys_profile_to_measure_a_control": (')],
       [r"\bR4\b", r"load_a_third_partys_profile", r"(?i)third party'?s profile"]),
    _f("TYPING-RULING-MENTIONS",
       "operator's typing ruling (caller-supplied text), read as forbidding mentions and tags",
       "OPERATOR", "YES",
       [("tests/test_typed_bytes.py", "THE OPERATOR'S TYPING RULING CARRIED THREE CONDITIONS"),
        ("_audit/2026-09-05-article-publish.md", "That ruling was already made, by the operator")],
       [r"MENTION-COMPOSITION", r"MENTION/TAG", r"(?i)typing ruling", r"test_typed_bytes"]),
    # ---- families the operator's recorded words point AGAINST ------------------
    _f("EDIT-FAMILY",
       "`/edit/` keeps refusing every profile editor but the intro editor",
       "CODE", "CONTRARY",
       [("linkedin_server/readonly.py", "Narrowing was refused"),
        ("_audit/2026-08-31-linkedin-finish.md", "and the profile editors are allowed")],
       [r"/edit/"]),
    _f("OTW-SPEC-NEVER-LOADED",
       "set_open_to_work refuses: the editor was never loaded",
       "CODE", "CONTRARY",
       # CONTRARY on HIS words, not only on a wave's: on 2026-08-23 he
       # "approved save/unsave, follow, Open To Work". No census cell cites
       # that passage, which is why the blind verifier classed this family
       # op=NO -- recorded in the audit's section 7.
       [("linkedin_server/writes.py", "NEVER LOADED"),
        ("_audit/2026-08-23-build-linkedin.md",
         "and approved **save/unsave, follow, Open To"),
        ("_audit/2026-08-25-cannot-vs-will-not.md",
         "Open To Work -- I am OVERTURNING the pre-classification")],
       [r"(?i)set_open_to_work", r"NEVER.LOADED", r"(?i)never loaded", r"(?i)open.to.work"]),
    _f("PF-ENDORSE-OR-RECOMMEND",
       "PERMANENTLY_FORBIDDEN endorse_or_recommend, surviving on a measurement of endorse controls",
       "CODE", "CONTRARY",
       [("linkedin_server/writes.py", '"endorse_or_recommend": ('),
        ("_audit/2026-08-25-cannot-vs-will-not.md",
         "the operator ruled on 2026-08-25 that it gets built")],
       [r"endorse_or_recommend", r"\bR3\b"]),
    # THE ROOT OF R9 IS THE OPERATOR'S OWN CUT, which is why op is YES: on
    # 2026-08-23 he "cut apply, connect and InMail". The census cites the cut
    # through the skill file and an agent research report; the tracked record
    # of the ruling itself is the build document. Withdrawn by his ruling (b)
    # of 2026-09-23, so every R9 row is B-lifted.
    _f("R9-OUTREACH-AUTOMATION",
       "network R9: InMail and outreach -- the operator's 2026-08-23 cut",
       "OPERATOR", "YES",
       [(_NET, "### R9 -- InMail and outreach automation."),
        ("_audit/2026-08-23-build-linkedin.md", "The operator **cut apply, connect and InMail**"),
        ("EXT:mcp-servers/_audit/2026-08-20-linkedin-parity.md",
         "NOT RECOMMENDED - outreach or invitation automation")],
       [r"\bR9\b"]),
    # ---- code refusals written by agents ----------------------------------------
    _f("PF-DELETE-OR-WITHDRAW",
       "PERMANENTLY_FORBIDDEN delete_or_withdraw_anything (network R5)",
       "CODE", "NO",
       [("linkedin_server/writes.py", '"delete_or_withdraw_anything": ('),
        (_NET, "### R5 -- `delete_or_withdraw_anything`.")],
       # "five specs" is the key's own content -- FIVE specs cite it in
       # reversible_by -- and occurs nowhere else in the census or the package.
       # It is the only link `M C31` has left: that row's locator is a LINE
       # RANGE, `writes.py:1801-1814`, which at HEAD lands inside send_message's
       # spec.
       [r"delete_or_withdraw_anything", r"\bR5\b", r"(?i)\bfive specs\b"]),
    _f("PF-DEANONYMISE-A-VIEWER",
       "PERMANENTLY_FORBIDDEN deanonymise_a_viewer (network R6)",
       "CODE", "NO",
       [("linkedin_server/writes.py", '"deanonymise_a_viewer": (')],
       [r"deanonymise_a_viewer", r"\bR6\b"]),
    _f("PF-AUTO-ACCEPT-OR-REPLY",
       "PERMANENTLY_FORBIDDEN auto_accept_or_auto_reply (network R8)",
       "CODE", "NO",
       [("linkedin_server/writes.py", '"auto_accept_or_auto_reply": (')],
       [r"auto_accept_or_auto_reply", r"\bR8\b"]),
    _f("PF-LOOP-SWEEP-SCHEDULED",
       "PERMANENTLY_FORBIDDEN any_loop_sweep_or_scheduled_write",
       "CODE", "NO",
       [("linkedin_server/writes.py", '"any_loop_sweep_or_scheduled_write": (')],
       [r"any_loop_sweep_or_scheduled_write"]),
    _f("PF-MARK-NOTIFICATIONS-READ",
       "PERMANENTLY_FORBIDDEN mark_notifications_read, measured impossible",
       "CODE", "NO",
       [("linkedin_server/writes.py", '"mark_notifications_read": (')],
       [r"mark_notifications_read"]),
    _f("PF-REPOST-OR-SHARE",
       "PERMANENTLY_FORBIDDEN repost_or_share",
       "CODE", "NO",
       [("linkedin_server/writes.py", '"repost_or_share": (')],
       [r"repost_or_share"]),
    _f("R2-INVITATION-SUBSTRINGS",
       "forbidden substrings invitation, /invite, /connect, /withdraw (network R2)",
       "CODE", "NO",
       [("linkedin_server/readonly.py", "A WRITE GUARD WAS MATCHING A READ ADDRESS"),
        (_NET, "### R2 -- `invitation`, `/invite`, `/connect`, `/withdraw` are forbidden substrings.")],
       [r"\bR2\b", r"(?i)\binvitation\b", r"/invite", r"/connect", r"/withdraw"]),
    _f("JOBS-APPLICATION-SUBSTRING",
       "forbidden substring /jobs/application",
       "CODE", "NO",
       [("linkedin_server/readonly.py", '"/jobs/application",')],
       [r"/jobs/application"]),
    _f("FOLLOW-SUBSTRING",
       "forbidden substring /follow, present since the server's first commit, no argument recorded",
       "CODE", "NO",
       [("linkedin_server/readonly.py", '"/follow",'),
        ("_audit/2026-09-19-two-census-conventions-ruled.md", "a filter that catches the ADDRESS")],
       [r"/follow\b"]),
    _f("FOLLOW-PEOPLE-LIST",
       "the people-follow list is left unread; /follow is not shortened",
       "CODE", "NO",
       [("linkedin_server/readonly.py", "people list unread, never to shorten the forbidden list")],
       [r"people-follow"]),
    _f("POST-EDIT-SUBSTRINGS",
       "forbidden substrings /post/ and /edit/ on a post-edit address",
       "CODE", "NO",
       [("linkedin_server/readonly.py", '"/post/",'),
        ("linkedin_server/readonly.py", '"/edit/",')],
       [r"/post/"]),
    _f("OFF-DOMAIN-FORM",
       "a form on somebody else's domain is reported, not driven",
       "CODE", "NO",
       [("linkedin_server/server.py", "OFF-SITE POSTINGS ARE REPORTED, NOT DRIVEN"),
        ("_audit/2026-08-25-cannot-vs-will-not.md",
         "Driving an off-site applicant-tracking system stays, and it was NOT part of")],
       [r"(?i)somebody else's domain", r"(?i)off-domain", r"(?i)off-site"]),
    _f("APPLY-NO-GUESSED-STEPS",
       "multi-step apply refused: unseen steps are the one guess not made",
       "CODE", "NO",
       [("linkedin_server/server.py", "one guess this server does not make"),
        ("_audit/2026-08-25-cannot-vs-will-not.md", "Anything whose request shape you would have to guess")],
       [r"(?i)zero advance controls", r"(?i)advance control", r"(?i)same gate"]),
    _f("DRAFT-DELETE-NOT-PRESSED",
       "the draft-application Delete control is never pressed",
       "CODE", "NO",
       [("linkedin_server/server.py", "never pressed from here")],
       [r"never pressed from here"]),
    _f("ARTICLE-ROUTE-NOT-USED",
       "publish_post does not use the article route (no measured anchor)",
       "CODE", "NO",
       [("linkedin_server/writes.py", "THE ARTICLE ROUTE IS DELIBERATELY NOT USED")],
       [r"ARTICLE ROUTE IS DELIBERATELY NOT USED"]),
    # ---- rulings made by a wave or a lead ------------------------------------
    _f("R1-MYNETWORK-BADGE",
       "/mynetwork/ refused as a census key on a derived badge cost (network R1)",
       "WAVE", "NO",
       [("_audit/2026-08-30-linkedin-nine.md", "connection invitations. **REFUSED.**"),
        (_NET, "### R1 -- `/mynetwork/` is refused, on a measured badge cost.")],
       [r"\bR1\b"]),
    _f("ROSTER-ENUMERATION",
       "member rosters (group members, event attendees) are not enumerated",
       "LEAD", "NO",
       [("linkedin_server/readonly.py", "THE MEMBER ROSTER. Census row N 165, and")],
       [r"(?i)ENUMERATING PEOPLE", r"(?i)roster"]),
    _f("NAV-FROM-PAGE-CONTENT",
       "a destination is never assembled from a name read off a page",
       "LEAD", "NO",
       [("_audit/_census/jobs.md", "The lead's ruling, given on this wave's report")],
       [r"(?i)navigation derived from page content"]),
    _f("FEED-CONTENT-READ",
       "feed content is read as counts and relations only",
       "LEAD", "NO",
       [("_audit/2026-09-05-lead-rulings-round-two.md",
         "`FEED-CONTENT-READ-RULING` -- COUNTS AND RELATIONS ONLY")],
       [r"FEED-CONTENT-READ"]),
    _f("MEASURED-NO-LINK",
       "a list measured unreachable by LINK from the composer (scheduled posts)",
       "WAVE", "NO",
       [("linkedin_server/writes.py", "THE SCHEDULED-POSTS SURFACE WOULD HAVE FIXED")],
       [r"(?i)scheduled-posts surface"]),
    _f("URL-UNREACHABLE-237",
       "career-interests page: zero of 237 urls reach one",
       "WAVE", "NO",
       [("_audit/_census/profile.md", "measured: zero of 237 urls reach one"),
        ("_audit/2026-08-25-cannot-vs-will-not.md", "Open To Work is not reachable BY NAVIGATION.")],
       [r"zero of 237 urls"]),
    _f("NO-ROUTE-MEASURED",
       "a control measured unidentifiable by every non-press route",
       "WAVE", "NO",
       [("_audit/_census/profile.md", "NO ROUTE REMAINS, which is why this is a refusal")],
       [r"NO ROUTE REMAINS"]),
    # ---- the 2026-09-05 retirement families (wave-ruled; the queue was his) ----
    *_RETIREMENTS,
)}


# ---------------------------------------------------------------------------
# The table
# ---------------------------------------------------------------------------

def load(path: pathlib.Path = TABLE) -> tuple[list[dict[str, str]], list[str]]:
    """(rows, problems). A missing or malformed table is a NAMED problem."""
    if not path.exists():
        return [], [f"the table {path.name} does not exist"]
    raw = path.read_bytes()
    problems: list[str] = []
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        return [], [f"the table is not ASCII (byte {exc.start})"]
    lines = text.splitlines()
    if not lines or tuple(lines[0].split("\t")) != COLUMNS:
        return [], [f"the header must be exactly {COLUMNS}"]
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != len(COLUMNS):
            problems.append(f"line {n}: {len(parts)} fields, want {len(COLUMNS)}")
            continue
        rows.append(dict(zip(COLUMNS, parts), _line=str(n)))
    return rows, problems


def key(row: dict[str, str]) -> tuple[str, str]:
    return row["slice"], row["row"]


def parse_basis(text: str) -> dict[str, str]:
    """``k=v; k=v; note=free text``. ``note`` is last and may hold anything."""
    out: dict[str, str] = {}
    head, sep, note = text.partition("note=")
    for part in head.split(";"):
        part = part.strip()
        if not part:
            continue
        k, eq, v = part.partition("=")
        if eq:
            out[k.strip()] = v.strip()
    if sep:
        out["note"] = note.strip()
    return out


def parse_sources(text: str) -> list[tuple[str, str]]:
    """``path#anchor ; path#anchor``. ``-`` means none."""
    out = []
    for item in text.split(" ; "):
        item = item.strip()
        if not item or item == "-":
            continue
        path, _hash, anchor = item.partition("#")
        out.append((path.strip(), anchor.strip()))
    return out


# ---------------------------------------------------------------------------
# The census, through the shipped parse only
# ---------------------------------------------------------------------------

def population() -> tuple[dict[tuple[str, str], str], dict[tuple[str, str], str], list[str]]:
    """(key -> folded state, key -> resolved census text, problems).

    TWO SHIPPED WALKS, CROSS-CHECKED. ``census_completion.walk`` is the one the
    completion figure divides by; ``classify_writeoff_reasons.build`` is the one
    that resolves pointers. A disagreement is reported, never averaged.
    """
    import census_completion as cc
    import classify_writeoff_reasons as cwr

    problems: list[str] = []
    pop = {(letter, rid): st for letter, rid, st, _d in cc.walk()
           if st in cc.OUT_OF_SCOPE}
    rows, _wo, dialects, _stated, _rulings, cwr_problems, _adj = cwr.build()
    problems += [f"classify_writeoff_reasons: {p}" for p in cwr_problems]
    problems += [f"state dialect: {d}" for d in dialects]
    hay: dict[tuple[str, str], str] = {}
    other: dict[tuple[str, str], str] = {}
    for r in rows:
        st = cc.FOLD.get(r.state, r.state)
        if st not in cc.OUT_OF_SCOPE:
            continue
        k = (r.letter, r.rid)
        other[k] = st
        hay[k] = "\n".join((r.resolved, r.section, r.resolution))
    if other != pop:
        a, b = set(pop) - set(other), set(other) - set(pop)
        problems.append(
            f"the two shipped walks disagree on the out-of-scope population: "
            f"{sorted(a)[:6]} only in census_completion, {sorted(b)[:6]} only "
            f"in classify_writeoff_reasons")
    return pop, hay, problems


# ---------------------------------------------------------------------------
# Checks -- each pure, each returning named problems
# ---------------------------------------------------------------------------

def coverage_problems(rows, pop) -> list[str]:
    problems = []
    seen = collections.Counter(key(r) for r in rows)
    for k, n in sorted(seen.items()):
        if n > 1:
            problems.append(f"{k[0]} {k[1]}: {n} lines for one row")
    for k in sorted(set(pop) - set(seen)):
        problems.append(
            f"{k[0]} {k[1]}: is {pop[k]} in the census and has NO LINE -- a row "
            f"entered an out-of-scope state with no traced basis")
    for k in sorted(set(seen) - set(pop)):
        problems.append(
            f"{k[0]} {k[1]}: has a line and is not out of scope in the census -- "
            f"a basis left pointing at a row that moved")
    for r in rows:
        k = key(r)
        if k in pop and r["state"] != pop[k]:
            problems.append(f"{k[0]} {k[1]}: table says {r['state']}, census says {pop[k]}")
    return problems


def _linked(fam: Family, rid: str, text: str, root: pathlib.Path) -> bool:
    if any(re.search(p, text) for p in fam.link):
        return True
    for path, anchor in fam.rollup:
        para = _paragraph(root, path, anchor)
        if para and re.search(rf"(?<![A-Za-z0-9-]){re.escape(rid)}(?![A-Za-z0-9-])", para):
            return True
    return False


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


_FILE_CACHE: dict[tuple[str, str], str | None] = {}


def _read(root: pathlib.Path, path: str) -> str | None:
    ck = (str(root), path)
    if ck not in _FILE_CACHE:
        p = root / path
        _FILE_CACHE[ck] = (_norm(p.read_text(encoding="utf-8", errors="replace"))
                           if p.is_file() else None)
    return _FILE_CACHE[ck]


def _paragraph(root: pathlib.Path, path: str, anchor: str) -> str:
    p = root / path
    if not p.is_file():
        return ""
    paras = re.split(r"\n\s*\n", p.read_text(encoding="utf-8", errors="replace"))
    for para in paras:
        if _norm(anchor) in _norm(para):
            return para
    return ""


def source_problem(root: pathlib.Path, path: str, anchor: str) -> str | None:
    """None if ``anchor`` occurs verbatim (whitespace-collapsed) in ``path``."""
    if path.startswith(EXT):
        return None
    if path.startswith("/") or re.match(r"^[A-Za-z]:", path) or ".." in path.split("/"):
        return f"source {path!r} is not a repo-relative path"
    text = _read(root, path)
    if text is None:
        return f"source {path!r} does not exist"
    if not anchor:
        return f"source {path!r} carries no anchor text"
    if _norm(anchor) not in text:
        return f"source {path!r} no longer contains {anchor[:70]!r}"
    return None


def family_problems(families: dict[str, Family], root: pathlib.Path) -> list[str]:
    problems = []
    for fam in families.values():
        if fam.op not in OPS:
            problems.append(f"family {fam.fid}: op {fam.op!r} not in {OPS}")
        for path, anchor in fam.sources + fam.rollup:
            p = source_problem(root, path, anchor)
            if p:
                problems.append(f"family {fam.fid}: {p}")
        if not any(not s.startswith(EXT) for s, _a in fam.sources):
            problems.append(f"family {fam.fid}: no source this repository can resolve")
    return problems


def row_problems(rows, hay, families: dict[str, Family],
                 root: pathlib.Path) -> tuple[list[str], list[str], list[str]]:
    """(structural problems, UNTRACED rows, LIFTED rows).

    The second and third lists are the VERDICT, and each fails the run under its
    own heading: an untraced row has no basis anyone can find, a lifted row has
    one that its maker has withdrawn. They are different facts and the operator
    acts on them differently, so they are never merged into one count.
    """
    problems: list[str] = []
    untraced: list[str] = []
    lifted: list[str] = []
    for r in rows:
        k = key(r)
        tag = f"{k[0]} {k[1]}"
        st, cls = r["state"], r["class"]
        if st not in CLASSES:
            problems.append(f"{tag}: state {st!r} is not out of scope")
            continue
        if cls not in CLASSES[st]:
            problems.append(f"{tag}: class {cls!r} is not allowed for {st} {CLASSES[st]}")
            continue
        b = parse_basis(r["basis"])
        srcs = parse_sources(r["source"])
        for path, anchor in srcs:
            p = source_problem(root, path, anchor)
            if p:
                problems.append(f"{tag}: {p}")
        local = [s for s in srcs if not s[0].startswith(EXT)]
        base = cls.replace("-lifted", "")
        if base in ("A", "B"):
            fids = [x for x in b.get("family" if base == "B" else "ruling", "").split("+") if x]
            if not fids:
                problems.append(f"{tag}: class {cls} names no family")
                continue
            unknown = [f for f in fids if f not in families]
            if unknown:
                problems.append(f"{tag}: unknown family {unknown}")
                continue
            primary = families[fids[0]]
            if b.get("op") != primary.op:
                problems.append(
                    f"{tag}: op={b.get('op')!r} but {primary.fid} records op={primary.op}")
            if base == "B" and b.get("scope") not in SCOPES:
                problems.append(f"{tag}: scope {b.get('scope')!r} not in {SCOPES}")
            if base == "A" and (primary.made_by != "OPERATOR" or primary.op != "YES"):
                problems.append(f"{tag}: class {cls} on {primary.fid}, which is not an operator ruling")
            # A NAMED POINTER, never a positional one. ``via=M12`` is accepted
            # only when this row's own text names that row, and then the family
            # must link to THAT row -- `M M26` reads "same entry as M12".
            text = hay.get(k, "")
            via = b.get("via", "")
            if via:
                if not re.search(rf"(?<![A-Za-z0-9-]){re.escape(via)}(?![A-Za-z0-9-])", text):
                    problems.append(f"{tag}: via={via} but the row's own text does not name {via}")
                text = hay.get((k[0], via), "")
            if not _linked(primary, k[1], text, root):
                problems.append(
                    f"{tag}: nothing in the row's resolved census text cites "
                    f"{primary.fid}, and no roll-up names it -- the table asserts a "
                    f"link the census does not carry")
            if not local:
                problems.append(f"{tag}: no source this repository can resolve")
            if cls.endswith("-lifted"):
                bases = [x for x in b.get("lifted", "").split("+") if x]
                bad = [x for x in bases if x not in LIFTED]
                if not bases or bad:
                    problems.append(f"{tag}: lifted={b.get('lifted')!r} -- each part must be one of {LIFTED}")
                if LIFT_SOURCE not in srcs:
                    problems.append(f"{tag}: a lifted row must cite the tracked record of the lift, "
                                    f"{LIFT_SOURCE[0]}")
                remaining = b.get("remaining", "")
                if remaining and remaining != "-" and remaining not in families:
                    problems.append(f"{tag}: remaining={remaining!r} is not a registered family")
                if st == ER:
                    held = ("" if remaining in ("", "-")
                            else f"; still held by {remaining}")
                    lifted.append(f"{tag}: EXCLUDED-RULED on a LIFTED ruling "
                                  f"({b.get('lifted')}){held}")
            elif b.get("lifted"):
                problems.append(f"{tag}: carries lifted= but its class is {cls}, not {base}-lifted")
        elif cls == "C":
            if b.get("why") not in WHYS:
                problems.append(f"{tag}: C row why={b.get('why')!r} not in {WHYS}")
            if st == ER:
                untraced.append(f"{tag}: EXCLUDED-RULED with NO TRACEABLE BASIS "
                                f"({b.get('why')}) -- {b.get('note', '')[:90]}")
        else:  # M+ / M-
            if b.get("evidence") not in EVIDENCE:
                problems.append(f"{tag}: evidence={b.get('evidence')!r} not in {EVIDENCE}")
            if not b.get("measurement"):
                problems.append(f"{tag}: names no measurement")
            if (cls == "M+") != (b.get("evidence") == "RECORDED"):
                problems.append(f"{tag}: class {cls} contradicts evidence={b.get('evidence')}")
            if cls == "M+" and not local:
                problems.append(f"{tag}: M+ with no source this repository can resolve")
    return problems, untraced, lifted


def summary(rows, families: dict[str, Family]) -> list[str]:
    out = []
    by_cls = collections.Counter((r["state"], r["class"]) for r in rows)
    out.append("rows by state and class:")
    for (st, cls), n in sorted(by_cls.items()):
        out.append(f"    {st:16s} {cls:9s} {n:4d}")
    fams: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        if r["class"].replace("-lifted", "") in ("A", "B"):
            b = parse_basis(r["basis"])
            fid = (b.get("family") or b.get("ruling") or "").split("+")[0]
            fams[fid][f"scope={b.get('scope', '-')}"] += 1
            if r["class"].endswith("-lifted"):
                fams[fid]["lifted"] += 1
    out.append("A/B rows, lifted included, by primary family (op as registered):")
    for fid in sorted(fams, key=lambda f: -sum(v for k2, v in fams[f].items() if k2 != "lifted")):
        op = families[fid].op if fid in families else "?"
        total = sum(v for k2, v in fams[fid].items() if k2 != "lifted")
        detail = " ".join(f"{k2}:{v}" for k2, v in sorted(fams[fid].items()))
        out.append(f"    {total:4d}  {fid:32s} op={op:9s} {detail}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Every out-of-scope row's traced basis.")
    ap.add_argument("--table", type=pathlib.Path, default=TABLE)
    ap.add_argument("--summary", action="store_true", help="print the counts first")
    args = ap.parse_args(argv)

    rows, problems = load(args.table)
    pop, hay, pop_problems = population()
    problems += pop_problems
    problems += family_problems(FAMILIES, ROOT)
    problems += coverage_problems(rows, pop)
    structural, untraced, lifted = row_problems(rows, hay, FAMILIES, ROOT)
    problems += structural

    if args.summary:
        print("\n".join(summary(rows, FAMILIES)))
        print()
    print(f"population {len(pop)}, table {len(rows)}, "
          f"structural problems {len(problems)}, untraced {len(untraced)}, "
          f"lifted {len(lifted)}")
    for p in problems:
        print(f"  PROBLEM  {p}")
    for u in untraced:
        print(f"  UNTRACED {u}")
    for li in lifted:
        print(f"  LIFTED   {li}")
    if untraced:
        print(f"\n{len(untraced)} EXCLUDED-RULED row(s) have no traceable basis. "
              f"Whether each returns to GAP is the operator's decision; this "
              f"check stays red until it is made.")
    if lifted:
        print(f"\n{len(lifted)} EXCLUDED-RULED row(s) rest on a ruling the operator "
              f"has withdrawn. They are pending work the census hides; moving "
              f"them is the orchestrator's, at merge.")
    return 1 if (problems or untraced or lifted) else 0


if __name__ == "__main__":
    sys.exit(main())
