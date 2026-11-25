"""The answer bank for applying: HIS confirmed answers, shared by every job platform.

PHASE A of lane apply-26 (2026-11-25), unwired; the record is
``_audit/2026-11-25-apply.md`` (its section 2.3 is this file's specification,
written for lane pipeline-26, which READS the bank through :func:`lookup`).
Its consumers are ``apply_walk`` -- the multi-step Easy Apply walker, itself
unwired until a capture measures a multi-step flow -- and the job pipeline.

WHERE IT LIVES, as ruled by the orchestrator (2026-11-25): one JSON file,
``<jobhunt root>/mcp-servers/_audit/job-pipeline/answer-bank.json``, beside the
pipeline's tracker. ``mcp-servers/_audit`` is a NESTED git repository whose own
``.gitignore`` ignores ``*.json`` and ``*.jsonl``, so the file is ignored by the
repository that actually contains it. The path is RESOLVED AT RUNTIME
(:func:`locate_bank`), never written into code: the bank's own environment
variable, then ``JOBHUNT_HOME``, then a walk up to the ``.jobhunt-root`` marker.
It holds his personal data, so nothing here writes it; it is created only by a
writer that has first asked git whether the path is ignored.

THE SHAPE. One ENTRY per NORMALIZED QUESTION CLASS -- ``experience.years.nodejs``,
``availability.notice_period``, ``work_authorisation.india`` -- holding ONE
platform-neutral answer, and, per platform, the FIELD HINTS that say which of
that platform's questions ARE this class: their exact wordings, the option set
they are drawn with, the platform's own name for the field type. A
platform-formatted answer (Naukri's option label for a notice period LinkedIn
asks in days) is a per-platform override of the confirmed answer, confirmed
like it.

THE ONE RULE. Each entry carries ``draft`` and ``confirmed``. ONLY ``confirmed``
is read. A draft is a suggestion an agent proposed -- from his resume, or
imported from Naukri's cache -- for him to check; it is type-checked and never
parsed into an :class:`Answer`, so no code path below can hand it to anybody.
Every answer returned has one provenance, ``operator_confirmed``.

WHAT IT NEVER DOES, because each is how a wrong answer would reach an
application nobody can withdraw (LinkedIn Help a512388; Uplers and Naukri the
same):

* INFER. A question belongs to a class only if its exact wording is listed in
  that class's hints for that platform, compared after :func:`normalise_question`
  (invisible characters out, whitespace collapsed, case folded) and nothing
  more: no keyword, prefix or containment match, and no guessing a class from
  a question. A hint that names ``options`` matches only that option set.
* CROSS KINDS OR PLATFORMS. A class answers only its own input kind, and a
  hint only its own platform (``any`` hints every platform; a platform's own
  hint is preferred over an ``any`` one for the same wording).
* SERVE A STALE ANSWER. A confirmed answer past ``expires_at`` answers nothing;
  a VOLATILE family (experience, availability, compensation, location) cannot
  be confirmed without an expiry.
* LET AN ATTESTATION FIRE UNSEEN. A NEVER-AUTO family (work authorisation,
  self-identification, checks, cover letters, and free text about pay) is
  returned with ``auto`` off: a proposal for a preview he reads, never an
  answer for a submit he does not see; ``auto: "yes"`` on one refuses the file.
* REMEMBER. :func:`load_bank` reads the file on every call and keeps nothing at
  module level, so his edit is the bank the next read sees.
* ECHO A VALUE IN AN ERROR. A :class:`BankError` names the entry's position and
  id (his own label) and what is wrong, never a value. Numbers and dates are
  checked with patterns; a JSON error is reported by line and column only.
"""

from __future__ import annotations

import datetime
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from . import people_data

# ---------------------------------------------------------------------------
# Where it lives
# ---------------------------------------------------------------------------

SCHEMA_ID = "jobhunt-answer-bank/1"
BANK_FILENAME = "answer-bank.json"
#: The bank under the jobhunt root (the orchestrator's ruling, 2026-11-25).
BANK_PARTS: tuple[str, ...] = ("mcp-servers", "_audit", "job-pipeline", BANK_FILENAME)
#: The bank's own override: a file path, used as given.
ENV_BANK = "JOBHUNT_ANSWER_BANK"
#: The jobhunt ROOT, as lane pipeline-26 reads it (``jp.state_dir``). Note that
#: jobcore's ``config.locate`` reads the same variable as the directory that
#: holds ``jobhunt.json``; the two readers differ, and this bank sides with
#: the pipeline that shares it.
ENV_HOME = "JOBHUNT_HOME"
ROOT_MARKER = ".jobhunt-root"
#: How far up the walk goes -- lane pipeline-26's ``find_root`` bound, so the
#: two readers find the same root from the same places.
MAX_WALK_UP = 12


@dataclass(frozen=True)
class BankLocation:
    """Where the bank is, or why no place was found. ``how`` names the step."""

    path: Optional[Path]
    how: str


def locate_bank(start: Any = None, env: Optional[Mapping[str, str]] = None) -> BankLocation:
    """The bank's path by the order: ``JOBHUNT_ANSWER_BANK``, then
    ``JOBHUNT_HOME``, then a walk up from ``start`` (default: this module) to
    the ``.jobhunt-root`` marker. No path is ever written into code."""
    environ = os.environ if env is None else env
    explicit = str(environ.get(ENV_BANK) or "").strip()
    if explicit:
        return BankLocation(Path(explicit).expanduser(), ENV_BANK)
    home = str(environ.get(ENV_HOME) or "").strip()
    if home:
        return BankLocation(Path(home).expanduser().joinpath(*BANK_PARTS), ENV_HOME)
    base = Path(start if start is not None else __file__).resolve()
    if base.is_file():
        base = base.parent
    for parent in [base, *base.parents][: MAX_WALK_UP + 1]:
        if (parent / ROOT_MARKER).is_file():
            return BankLocation(parent.joinpath(*BANK_PARTS), f"walk-up to {ROOT_MARKER}")
    return BankLocation(
        None,
        f"no {ENV_BANK}, no {ENV_HOME}, and no {ROOT_MARKER} within {MAX_WALK_UP} parents",
    )


def bank_path() -> Optional[Path]:
    """The resolved bank path, or None where the order finds no root."""
    return locate_bank().path


# ---------------------------------------------------------------------------
# The vocabulary
# ---------------------------------------------------------------------------

#: The input kinds a class may be answered in. ``checkbox`` is ONE box (checked
#: or unchecked); ``multi_select`` is a group of boxes, answered by one or more
#: labels. A file input is none of them: which stored resume to send is a
#: radio answer, and uploading a new file is census row J 70.
INPUT_KINDS: tuple[str, ...] = (
    "text", "numeric", "select", "radio", "checkbox", "multi_select", "typeahead",
)
OPTION_KINDS = frozenset({"select", "radio", "multi_select"})

#: The platforms a hint may name. ``any`` is a wording every platform uses.
PLATFORMS: tuple[str, ...] = ("any", "linkedin", "naukri", "uplers", "instahyre")

#: The class FAMILIES, closed, because a family decides whether an answer
#: expires and whether it may ever fire unseen.
FAMILIES: tuple[str, ...] = (
    "contact", "links", "resume", "cover_letter", "experience", "availability",
    "compensation", "work_authorisation", "location", "education", "language",
    "checks", "review", "self_id", "other", "naukri_import",
)
VOLATILE_FAMILIES = frozenset({"experience", "availability", "compensation", "location"})
NEVER_AUTO_FAMILIES = frozenset({"work_authorisation", "self_id", "checks", "cover_letter"})
#: An entry imported from another server's cache: given a real family BY HIM
#: before it may be confirmed, because the importer cannot say what a question
#: is about without inferring it.
IMPORTED_FAMILY = "naukri_import"

#: How a cell lists several labels (a multi_select answer).
OPTION_SEPARATOR = " | "
CHECKBOX_VALUES: tuple[str, ...] = ("checked", "unchecked")
AUTO_VALUES: tuple[str, ...] = ("", "yes", "never")

ENTRY_KEYS = frozenset({"id", "family", "input_kind", "platforms", "draft", "confirmed", "notes"})
HINT_KEYS = frozenset({"questions", "options", "native_type"})
DRAFT_KEYS = frozenset({"value", "per_platform", "source"})
CONFIRMED_KEYS = frozenset({"value", "per_platform", "confirmed_at", "expires_at", "auto"})

_ID = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,95}$")
_NUMERIC = re.compile(r"^[0-9]{1,7}(?:\.[0-9]{1,2})?$")
_DATE = re.compile(r"^(20[0-9]{2})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")

MAX_ANSWER_CHARS = 1000
QUESTION_CAP = people_data.CAPS["text"]
PROVENANCE = "operator_confirmed"


class BankError(ValueError):
    """The bank cannot be read as a bank. Its message carries NO value."""


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------


def normalise_question(text: Any) -> str:
    """The comparison form of a question: sanitised, whitespace collapsed, case folded.

    NOTHING ELSE IS STRIPPED -- not a trailing asterisk, not "(required)" --
    because whether a form writes such marks into a label has never been
    measured, and stripping one that is part of the question would merge two.
    """
    return people_data.sanitise(text, cap=QUESTION_CAP).casefold()


def normalise_answer(text: Any) -> str:
    """The comparison form of an answer or an option label: the same rule."""
    return people_data.sanitise(text, cap=MAX_ANSWER_CHARS).casefold()


def options_key_of(options: Iterable[Any]) -> frozenset:
    """An option set's identity: its normalised labels, order ignored."""
    return frozenset(normalise_answer(o) for o in options if normalise_answer(o))


def split_options(cell: str) -> list[str]:
    return [part.strip() for part in str(cell).split(OPTION_SEPARATOR) if part.strip()]


def same_answer(input_kind: str, one: Any, other: Any) -> bool:
    """Are two answers the same answer? A group of boxes compares as a SET of
    labels; every other kind as one normalised string."""
    if input_kind == "multi_select":
        return options_key_of(split_options(str(one or ""))) == \
            options_key_of(split_options(str(other or "")))
    return normalise_answer(one) == normalise_answer(other)


def never_auto(family: str, input_kind: str) -> bool:
    """Is an answer of this family and kind always put to him? Free text about
    pay is -- it is a negotiation; a pay NUMBER is volatile, not never-auto."""
    return family in NEVER_AUTO_FAMILIES or (family == "compensation" and input_kind == "text")


def _date(cell: Any) -> Optional[datetime.date]:
    """A YYYY-MM-DD string as a date; None for anything else. Never raises."""
    match = _DATE.match(cell) if isinstance(cell, str) else None
    if not match:
        return None
    year, month, day = (int(group) for group in match.groups())
    try:
        return datetime.date(year, month, day)
    except ValueError:
        return None


def value_problem(input_kind: str, value: str, options: Sequence[str] = ()) -> Optional[str]:
    """Why ``value`` cannot answer a field of ``input_kind``, or ``None``.

    The reason never quotes the value.
    """
    if input_kind not in INPUT_KINDS:
        return f"input_kind is not one of {', '.join(INPUT_KINDS)}"
    if not value:
        return "the answer is empty"
    if len(value) > MAX_ANSWER_CHARS:
        return f"an answer longer than {MAX_ANSWER_CHARS} characters"
    if input_kind == "numeric" and not _NUMERIC.match(value):
        return "a numeric answer that is not a plain number (digits, at most two decimals)"
    if input_kind == "checkbox" and value not in CHECKBOX_VALUES:
        return f"a checkbox answer that is not one of {', '.join(CHECKBOX_VALUES)}"
    # BEFORE the option check, and outside it, so it guards a hint that names
    # no options too (measured: its mutation survived when it sat inside,
    # where the option check always refused first).
    if input_kind in ("select", "radio") and len(split_options(value)) > 1:
        return f"a {input_kind} answer names more than one option"
    if input_kind in OPTION_KINDS and options:
        drawn = options_key_of(options)
        chosen = split_options(value) if input_kind == "multi_select" else [value]
        if not all(normalise_answer(c) in drawn for c in chosen):
            return "an answer that is not one of the hint's options"
    return None


# ---------------------------------------------------------------------------
# The parsed bank
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Answer:
    """One CONFIRMED answer, resolved for one platform's hint. No draft field."""

    entry_id: str
    cls: str
    platform: str
    question_key: str
    input_kind: str
    #: The option set the hint names, normalised; None = any option set.
    options_key: Optional[frozenset]
    value: str
    confirmed_at: datetime.date
    expires_at: Optional[datetime.date]
    auto: bool
    line: int

    def expired(self, today: datetime.date) -> bool:
        return self.expires_at is not None and today > self.expires_at

    def as_lookup(self) -> dict[str, Any]:
        """The pipeline's read shape -- see :func:`lookup`."""
        return {
            "answer": self.value,
            "type": self.input_kind,
            "provenance": PROVENANCE,
            "confirmed_at": self.confirmed_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "auto": self.auto,
            "entry_id": self.entry_id,
            "platform": self.platform,
        }


@dataclass(frozen=True)
class Bank:
    """What :func:`load_bank` read: the confirmed answers, one per platform hint
    wording, and counts. ``line`` on an :class:`Answer` is the entry's position.
    """

    answers: tuple[Answer, ...]
    path_found: bool
    rows_read: int
    rows_confirmed: int
    rows_unconfirmed: int
    rows_template: int

    def answer_for(
        self,
        question: Any,
        input_kind: str,
        *,
        options: Sequence[Any] = (),
        platform: str = "any",
        today: Optional[datetime.date] = None,
    ) -> Optional[Answer]:
        """The confirmed answer to exactly this wording, kind, option set and
        platform, unexpired -- or ``None``, the common and the safe answer.

        A platform's own hint beats an ``any`` hint, and a hint naming this
        option set beats one naming none. Hints equal on both are refused at
        load, so the choice is never a coin toss.
        """
        key = normalise_question(question)
        if not key or input_kind not in INPUT_KINDS or platform not in PLATFORMS:
            return None
        drawn = options_key_of(options) if options else None
        when = today or datetime.date.today()
        fits = [
            a for a in self.answers
            if a.question_key == key
            and a.input_kind == input_kind
            and a.platform in (platform, "any")
            and (a.options_key is None or a.options_key == drawn)
            and not a.expired(when)
        ]
        if not fits:
            return None
        fits.sort(key=lambda a: (a.platform == "any", a.options_key is None))
        return fits[0]

    def expired_rows(self, today: Optional[datetime.date] = None) -> int:
        when = today or datetime.date.today()
        return len({a.entry_id for a in self.answers if a.expired(when)})

    def status(self, today: Optional[datetime.date] = None) -> dict[str, Any]:
        """Counts only -- never a question, a value or a path."""
        return {
            "bank_file_found": self.path_found,
            "entries_read": self.rows_read,
            "entries_confirmed": self.rows_confirmed,
            "entries_confirmed_and_expired": self.expired_rows(today),
            "entries_awaiting_his_confirmation": self.rows_unconfirmed,
            "entries_with_no_question_wording": self.rows_template,
        }


def _strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def _platform_strings(value: Any) -> bool:
    return isinstance(value, dict) and all(
        k in PLATFORMS and isinstance(v, str) for k, v in value.items())


def _check_shape(index: int, entry: Any) -> str:
    """Type-check one entry, strictly; returns its id. Unknown keys refuse:
    a misspelt ``confimed`` would otherwise be an answer silently ignored."""
    where = f"entry {index}"
    if not isinstance(entry, dict):
        raise BankError(f"{where}: an entry is not a JSON object")
    unknown = set(entry) - ENTRY_KEYS
    if unknown:
        raise BankError(f"{where}: unknown keys {sorted(unknown)}")
    entry_id = entry.get("id")
    if not isinstance(entry_id, str) or not _ID.match(entry_id):
        raise BankError(f"{where}: the id is not 1-96 characters of a-z, 0-9, '_', '.', '-'")
    where = f"entry {index} ({entry_id})"
    if entry.get("family") not in FAMILIES:
        raise BankError(f"{where}: family is not one of {', '.join(FAMILIES)}")
    if entry.get("input_kind") not in INPUT_KINDS:
        raise BankError(f"{where}: input_kind is not one of {', '.join(INPUT_KINDS)}")
    platforms = entry.get("platforms", {})
    if not isinstance(platforms, dict) or not all(p in PLATFORMS for p in platforms):
        raise BankError(f"{where}: platforms keys are not among {', '.join(PLATFORMS)}")
    for platform, hint in platforms.items():
        if not isinstance(hint, dict) or set(hint) - HINT_KEYS:
            raise BankError(f"{where}: the {platform} hint has keys outside {sorted(HINT_KEYS)}")
        if not _strings(hint.get("questions", [])) or not _strings(hint.get("options", [])):
            raise BankError(f"{where}: the {platform} hint's questions and options are lists of text")
        if not isinstance(hint.get("native_type", ""), str):
            raise BankError(f"{where}: the {platform} hint's native_type is not text")
    for block, keys in (("draft", DRAFT_KEYS), ("confirmed", CONFIRMED_KEYS)):
        part = entry.get(block, {})
        if not isinstance(part, dict) or set(part) - keys:
            raise BankError(f"{where}: {block} has keys outside {sorted(keys)}")
        for name in keys - {"per_platform"}:
            if not isinstance(part.get(name, ""), str):
                raise BankError(f"{where}: {block}.{name} is not text")
        if not _platform_strings(part.get("per_platform", {})):
            raise BankError(f"{where}: {block}.per_platform maps platforms to text")
    if not isinstance(entry.get("notes", ""), str):
        raise BankError(f"{where}: notes is not text")
    return entry_id


def parse_bank(text: str, *, path_found: bool = True,
               today: Optional[datetime.date] = None) -> Bank:
    """Parse the JSON bank. Refuses the whole file on any malformed entry.

    A partly-read bank is one whose missing answers nobody can see; worse, a
    misplaced key would put a draft where a confirmed answer belongs. So one
    bad entry refuses all of them, by position.
    """
    when = today or datetime.date.today()
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise BankError(f"the bank is not JSON (line {exc.lineno}, column {exc.colno})") from None
    if not isinstance(document, dict) or document.get("schema") != SCHEMA_ID:
        raise BankError(f"the bank is not a {SCHEMA_ID} document")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise BankError("the bank has no entries list")

    answers: list[Answer] = []
    seen_ids: dict[str, int] = {}
    seen_hints: dict[tuple, int] = {}
    confirmed = unconfirmed = template = 0
    for index, entry in enumerate(entries, start=1):
        entry_id = _check_shape(index, entry)
        if entry_id in seen_ids:
            raise BankError(f"entry {index}: id {entry_id!r} is already used by entry {seen_ids[entry_id]}")
        seen_ids[entry_id] = index
        where = f"entry {index} ({entry_id})"
        family, kind = entry["family"], entry["input_kind"]
        hints = [
            (platform, normalise_question(q), list(hint.get("options", [])))
            for platform, hint in entry.get("platforms", {}).items()
            for q in hint.get("questions", [])
            if normalise_question(q)
        ]
        part = entry.get("confirmed", {})
        neutral = people_data.sanitise(part.get("value", ""), cap=MAX_ANSWER_CHARS + 1)
        per_platform = {
            p: people_data.sanitise(v, cap=MAX_ANSWER_CHARS + 1)
            for p, v in part.get("per_platform", {}).items()
        }
        if not neutral and not any(per_platform.values()):
            if hints:
                unconfirmed += 1
            else:
                template += 1
            continue
        if family == IMPORTED_FAMILY:
            raise BankError(
                f"{where}: an imported entry is confirmed only after you give it its "
                "family (its family decides whether it expires and whether it may fire unseen)"
            )
        auto = part.get("auto", "")
        if auto not in AUTO_VALUES:
            raise BankError(f"{where}: auto is not blank, yes or never")
        if auto == "yes" and never_auto(family, kind):
            raise BankError(f"{where}: family {family} is never-auto: its answers are always put to him")
        confirmed_at = _date(part.get("confirmed_at", ""))
        if confirmed_at is None:
            raise BankError(f"{where}: a confirmed entry needs confirmed_at as YYYY-MM-DD")
        if confirmed_at > when:
            raise BankError(f"{where}: confirmed_at is in the future")
        raw_expiry = part.get("expires_at", "")
        expires_at = _date(raw_expiry) if raw_expiry else None
        if raw_expiry and expires_at is None:
            raise BankError(f"{where}: expires_at is not YYYY-MM-DD")
        if family in VOLATILE_FAMILIES and expires_at is None:
            raise BankError(f"{where}: family {family} goes out of date, so it needs expires_at")
        if expires_at is not None and expires_at <= confirmed_at:
            raise BankError(f"{where}: expires_at is not after confirmed_at")
        if not hints:
            raise BankError(
                f"{where}: a confirmed entry names no question wording on any platform, "
                "so it could answer nothing"
            )
        confirmed += 1
        for platform, question_key, options in hints:
            value = per_platform.get(platform) or neutral
            if not value:
                raise BankError(f"{where}: no confirmed answer for its {platform} hint")
            problem = value_problem(kind, value, options)
            if problem:
                raise BankError(f"{where}: {platform}: {problem}")
            options_key = options_key_of(options) if options else None
            slot = (platform, question_key, kind, options_key)
            if slot in seen_hints:
                raise BankError(
                    f"{where}: a {platform} wording is already answered by entry "
                    f"{seen_hints[slot]} -- one question, one class"
                )
            seen_hints[slot] = index
            answers.append(Answer(
                entry_id=entry_id, cls=family, platform=platform,
                question_key=question_key, input_kind=kind, options_key=options_key,
                value=value, confirmed_at=confirmed_at, expires_at=expires_at,
                auto=not never_auto(family, kind) and auto != "never", line=index,
            ))
    return Bank(
        answers=tuple(answers),
        path_found=path_found,
        rows_read=len(entries),
        rows_confirmed=confirmed,
        rows_unconfirmed=unconfirmed,
        rows_template=template,
    )


def empty_bank() -> Bank:
    """The bank when there is no file: it answers nothing, and says so."""
    return Bank(answers=(), path_found=False, rows_read=0, rows_confirmed=0,
                rows_unconfirmed=0, rows_template=0)


def load_bank(path: Optional[Path] = None, *, today: Optional[datetime.date] = None) -> Bank:
    """Read the bank from ``path`` (default: :func:`locate_bank`), fresh every call.

    No root and no file are both :func:`empty_bank`, never an error. A file
    that is not UTF-8, or not a bank, raises :class:`BankError` with no value.
    """
    target = Path(path) if path is not None else bank_path()
    if target is None:
        return empty_bank()
    try:
        raw = target.read_bytes()
    except FileNotFoundError:
        return empty_bank()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise BankError(f"the bank is not UTF-8 (byte {exc.start})") from None
    return parse_bank(text, path_found=True, today=today)


# ---------------------------------------------------------------------------
# The read API for other lanes
# ---------------------------------------------------------------------------


def lookup(
    question_text: Any,
    options: Sequence[Any] = (),
    platform: str = "any",
    *,
    input_kind: Optional[str] = None,
    bank: Optional[Bank] = None,
    today: Optional[datetime.date] = None,
) -> Optional[dict[str, Any]]:
    """``{answer, type, provenance, confirmed_at, expires_at, auto, entry_id,
    platform}`` or ``None``. Pure: no network and no write; the bank is read
    from disk unless one is handed in.

    ``None`` is a question for him -- there is no guessed default behind it.
    Without ``input_kind``, every kind is tried, and a wording answered under
    two kinds is ``None`` too: which one the form wants is the caller's to say.
    ``auto`` off means a proposal for a preview he reads, never an answer for
    a submit he does not see.
    """
    source = bank if bank is not None else load_bank(today=today)
    kinds = (input_kind,) if input_kind else INPUT_KINDS
    found = [
        answer for answer in (
            source.answer_for(question_text, kind, options=options,
                              platform=platform, today=today)
            for kind in kinds
        )
        if answer is not None
    ]
    if len(found) != 1:
        return None
    return found[0].as_lookup()


# ---------------------------------------------------------------------------
# Naukri's cache (questions.json), which naukri_apply submits WITHOUT showing
# ---------------------------------------------------------------------------

#: Naukri's question types, as its server writes them, and the bank's kinds.
NAUKRI_KINDS: dict[str, str] = {
    "Text Box": "text",
    "Radio Button": "radio",
    "List Menu": "select",
    "Check Box": "multi_select",
}


def naukri_cache_key(question_name: str, answer_option: Any) -> str:
    """The key ``naukri_server.cache._cache_key`` writes -- the question's name
    VERBATIM, an underscore, and its options dict as sorted JSON -- reproduced
    so an entry's Naukri hint and a cache entry join without guessing."""
    try:
        opts = json.dumps(answer_option, sort_keys=True)
    except (TypeError, ValueError):
        opts = str(sorted(answer_option.items()) if answer_option else "")
    return f"{question_name}_{opts}"


def _cache_options(key: str, name: str) -> Optional[dict]:
    """The options dict a cache key carries after the name, or None."""
    prefix = f"{name}_"
    if not key.startswith(prefix):
        return None
    try:
        parsed = json.loads(key[len(prefix):])
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def import_naukri_cache(cache: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Naukri's cached answers as bank entries: DRAFTS, never confirmed.

    One entry per cached question, of family :data:`IMPORTED_FAMILY` -- which
    the loader refuses to confirm until he has given it a real family -- with
    the question VERBATIM and its option labels as the entry's Naukri hint, and
    the cached answer only in ``draft``. A cached option answer that is none of
    the drawn labels (Naukri's formatter wraps an unmatched answer as-is) is
    said so in the notes, because that is what its apply would send.
    """
    entries: list[dict[str, Any]] = []
    for index, key in enumerate(sorted(cache), start=1):
        record = cache[key]
        if not isinstance(record, Mapping):
            continue
        name = str(record.get("questionName") or "")
        native = str(record.get("questionType") or "")
        kind = NAUKRI_KINDS.get(native)
        options = _cache_options(key, name)
        labels = [people_data.sanitise(v, cap=MAX_ANSWER_CHARS) for v in (options or {}).values()]
        notes: list[str] = []
        if kind is None:
            notes.append("question type not one the bank knows; kind left as text")
            kind = "text"
        if options is None:
            notes.append("options unreadable from the cache key")
        raw = record.get("answer")
        parts = [str(x) for x in raw] if isinstance(raw, list) else [str(raw or "")]
        if kind in OPTION_KINDS and labels:
            drawn = options_key_of(labels)
            if not all(normalise_answer(p) in drawn for p in parts):
                notes.append("the cached answer is NOT one of the options drawn")
        cached_at = record.get("cached_at")
        when = ""
        if isinstance(cached_at, (int, float)):
            when = datetime.datetime.fromtimestamp(
                cached_at, tz=datetime.timezone.utc).date().isoformat()
        entries.append({
            "id": f"naukri.import.{index:03d}",
            "family": IMPORTED_FAMILY,
            "input_kind": kind,
            "platforms": {"naukri": {
                "questions": [people_data.sanitise(name, cap=QUESTION_CAP)],
                "options": labels,
                "native_type": native,
            }},
            "draft": {
                "value": OPTION_SEPARATOR.join(
                    people_data.sanitise(p, cap=MAX_ANSWER_CHARS) for p in parts),
                "per_platform": {},
                "source": f"naukri questions.json, cached {when or 'on an unknown date'}",
            },
            "confirmed": {"value": "", "per_platform": {}, "confirmed_at": "",
                          "expires_at": "", "auto": ""},
            "notes": "; ".join(notes),
        })
    return entries


def naukri_cache_report(cache: Mapping[str, Any], bank: Bank, *,
                        today: Optional[datetime.date] = None) -> list[dict[str, Any]]:
    """What naukri_apply could submit unseen, entry by entry, against his bank.

    ``status`` per cached entry: ``confirmed_same`` (his confirmed, unexpired,
    auto-allowed answer equals the cached one), ``confirmed_differs``,
    ``never_auto`` (his family says it is always put to him), ``unconfirmed``
    (no confirmed class holds the wording). Only ``confirmed_same`` is an
    answer he has reviewed; the pipeline lists the rest before each Naukri yes.
    Pure and local: the report carries his questions back to his own caller.
    """
    out: list[dict[str, Any]] = []
    for key in sorted(cache):
        record = cache[key]
        if not isinstance(record, Mapping):
            continue
        name = str(record.get("questionName") or "")
        kind = NAUKRI_KINDS.get(str(record.get("questionType") or ""), "text")
        labels = [str(v) for v in (_cache_options(key, name) or {}).values()]
        raw = record.get("answer")
        cached = OPTION_SEPARATOR.join(str(x) for x in raw) if isinstance(raw, list) else str(raw or "")
        answer = bank.answer_for(name, kind, options=labels, platform="naukri", today=today)
        if answer is None:
            status = "unconfirmed"
        elif not answer.auto:
            status = "never_auto"
        elif same_answer(kind, answer.value, cached):
            status = "confirmed_same"
        else:
            status = "confirmed_differs"
        out.append({"question": name, "type": kind, "status": status,
                    "entry_id": answer.entry_id if answer else None})
    return out
