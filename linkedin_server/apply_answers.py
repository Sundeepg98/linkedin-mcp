"""The answer bank for applying: HIS confirmed answers, and nothing else.

PHASE A of lane apply-26 (2026-11-25), unwired; the record is
``_audit/2026-11-25-apply.md``. Its consumers are ``apply_walk`` (the
multi-step Easy Apply walker, itself unwired until a capture measures a
multi-step flow) and lane pipeline-26's job pipeline, which READS it through
:func:`lookup` (record section 4.1 answers that lane's six requirements).

WHAT IT IS. A LOCAL TSV under ``config.STATE_DIR`` -- ``_state/``, which
``.gitignore`` excludes whole (its line ``_state/``) -- one row per question
HE has answered. It holds his personal data (years of experience, notice
period, compensation, work authorisation), so it is never committed and never
copied into a record; the template that seeds it is written straight into
``_state/``.

THE ONE RULE. Each row carries TWO answer columns, ``DRAFT_UNCONFIRMED`` and
``CONFIRMED``. This module reads ONLY ``CONFIRMED``. A draft is a suggestion an
agent proposed -- from his resume, or imported from another server's cache --
for him to check; it is never parsed into an :class:`Answer`, so no code path
below can hand it to anybody. Every answer this module returns therefore has
one provenance, ``operator_confirmed``, and carries the date he confirmed it.

WHAT IT NEVER DOES, because each is how a wrong answer would reach an
application nobody can withdraw (LinkedIn Help a512388; Uplers and Naukri the
same):

* INFER. A question is answered only by a row whose ``question`` cell is the
  SAME TEXT as the question drawn, compared after :func:`normalise_question`
  (invisible characters out, whitespace collapsed, case folded) and nothing
  more; no keyword, prefix, class or containment match. A row that names its
  ``options`` answers only a question drawn with that same option set.
* CROSS KINDS OR PLATFORMS. A row answers only its own input kind, and only
  its own platform (``any`` answers every platform; a platform's own row is
  preferred over an ``any`` row for the same question).
* SERVE A STALE ANSWER. A row past its ``expires_at`` answers nothing; a row of
  a VOLATILE class (experience, availability, compensation, location) cannot
  be confirmed without an expiry.
* LET AN ATTESTATION FIRE UNSEEN. A row of a NEVER-AUTO class (work
  authorisation, self-identification, background checks, cover letters, free
  text about pay) is returned with ``auto: False``: a proposal for a preview
  he reads, never an answer for a submit he does not see, and the loader
  refuses ``auto=yes`` on one.
* REMEMBER. :func:`load_bank` reads the file on every call and keeps nothing
  at module level, so his edit is the bank the next read sees.
* ECHO A VALUE IN AN ERROR. A :class:`BankError` names the line, the row's
  ``id`` (his own label) and what is wrong, never a cell's value. Numbers and
  dates are checked with patterns, never with ``int()`` or ``date()`` on a
  raw value whose message would quote it.
"""

from __future__ import annotations

import datetime
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from . import config, people_data

#: The file, inside ``_state/``.
BANK_FILENAME = "apply-answer-bank.tsv"

#: The header, exactly. A file whose first non-comment line is not this is
#: refused whole rather than read by position: a column moved by one is how a
#: draft would be read as a confirmed answer.
COLUMNS: tuple[str, ...] = (
    "id",
    "class",
    "platform",
    "input_kind",
    "question",
    "options",
    "DRAFT_UNCONFIRMED",
    "CONFIRMED",
    "confirmed_at",
    "expires_at",
    "auto",
    "source",
    "notes",
)

#: The input kinds a row may answer. ``checkbox`` is ONE box (checked or
#: unchecked); ``multi_select`` is a group of boxes, answered by one or more of
#: its labels. A file input is none of them: which stored resume to send is a
#: radio answer, and uploading a new file is census row J 70.
INPUT_KINDS: tuple[str, ...] = (
    "text",
    "numeric",
    "select",
    "radio",
    "checkbox",
    "multi_select",
    "typeahead",
)
OPTION_KINDS = frozenset({"select", "radio", "multi_select"})

#: The platforms a row may answer for. ``any`` is the platform-neutral value.
PLATFORMS: tuple[str, ...] = ("any", "linkedin", "naukri", "uplers", "instahyre")

#: The classes, CLOSED, because a row's class decides whether it expires and
#: whether it may ever fire unseen.
CLASSES: tuple[str, ...] = (
    "contact",
    "links",
    "resume",
    "cover_letter",
    "experience",
    "availability",
    "compensation",
    "work_authorisation",
    "location",
    "education",
    "language",
    "checks",
    "review",
    "self_id",
    "other",
    "naukri_import",
)
#: Answers that go out of date: a confirmed row of these needs ``expires_at``.
VOLATILE_CLASSES = frozenset({"experience", "availability", "compensation", "location"})
#: Answers that are always put to him: legal and visa attestations, consents,
#: demographics, his own prose. ``auto=yes`` on one is refused.
NEVER_AUTO_CLASSES = frozenset({"work_authorisation", "self_id", "checks", "cover_letter"})
#: A row imported from another server's cache. It is classified BY HIM before
#: it is confirmed: the importer cannot say what a question is about without
#: inferring it.
IMPORTED_CLASS = "naukri_import"

#: How a cell lists several option labels (``options``, and a multi_select
#: answer). A label that itself contains it cannot be expressed, and an import
#: that meets one leaves the row's options empty and says so in its notes.
OPTION_SEPARATOR = " | "

CHECKBOX_VALUES: tuple[str, ...] = ("checked", "unchecked")
AUTO_VALUES: tuple[str, ...] = ("", "yes", "never")

_ID = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")
_NUMERIC = re.compile(r"^[0-9]{1,7}(?:\.[0-9]{1,2})?$")
_DATE = re.compile(r"^(20[0-9]{2})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")

MAX_ANSWER_CHARS = 1000
QUESTION_CAP = people_data.CAPS["text"]

PROVENANCE = "operator_confirmed"


class BankError(ValueError):
    """The bank file cannot be read as a bank. Its message carries NO value."""


@dataclass(frozen=True)
class Answer:
    """One CONFIRMED answer. There is no field for the draft, by construction."""

    entry_id: str
    cls: str
    platform: str
    question_key: str
    input_kind: str
    #: The option set the row was confirmed against, normalised; None = any.
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
    """What :func:`load_bank` read: the confirmed answers, and counts.

    ``path_found`` is False when there is no file at all, a state of its own:
    every question then goes to him, and the caller says why.
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
        """The confirmed answer to exactly this question, kind, option set and
        platform, unexpired -- or ``None``, the common and the safe answer.

        Two rows may fit one question: a platform's own row beats an ``any``
        row, and a row confirmed against this option set beats one confirmed
        against any. Rows equal on both are refused at load, so the choice is
        never a coin toss.
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
        return sum(1 for a in self.answers if a.expired(when))

    def status(self, today: Optional[datetime.date] = None) -> dict[str, Any]:
        """Counts only -- never a question and never a value."""
        return {
            "bank_file_found": self.path_found,
            "rows_read": self.rows_read,
            "rows_confirmed": self.rows_confirmed,
            "rows_confirmed_and_expired": self.expired_rows(today),
            "rows_awaiting_his_confirmation": self.rows_unconfirmed,
            "rows_without_a_question": self.rows_template,
        }


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
    return [part.strip() for part in cell.split(OPTION_SEPARATOR) if part.strip()]


def same_answer(input_kind: str, one: Any, other: Any) -> bool:
    """Are two answers the same answer? A group of boxes compares as a SET of
    labels; every other kind as one normalised string."""
    if input_kind == "multi_select":
        return options_key_of(split_options(str(one or ""))) == \
            options_key_of(split_options(str(other or "")))
    return normalise_answer(one) == normalise_answer(other)


def bank_path() -> Path:
    """Where the bank is read from: ``config.STATE_DIR`` / :data:`BANK_FILENAME`."""
    return Path(config.STATE_DIR) / BANK_FILENAME


def _date(cell: str) -> Optional[datetime.date]:
    """A YYYY-MM-DD cell as a date; None for a malformed one. Never raises."""
    match = _DATE.match(cell)
    if not match:
        return None
    year, month, day = (int(group) for group in match.groups())
    try:
        return datetime.date(year, month, day)
    except ValueError:
        return None


def value_problem(input_kind: str, value: str, options: Sequence[str] = ()) -> Optional[str]:
    """Why ``value`` cannot answer a row of ``input_kind``, or ``None``.

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
    # BEFORE the option check, and outside it, so that it guards the row that
    # names no options too: with options named, an answer naming two of them
    # is already no single option, and this check would never be the one to
    # refuse it (measured: its mutation survived when it sat inside).
    if input_kind in ("select", "radio") and len(split_options(value)) > 1:
        return f"a {input_kind} answer names more than one option"
    if input_kind in OPTION_KINDS and options:
        drawn = options_key_of(options)
        chosen = split_options(value) if input_kind == "multi_select" else [value]
        if not all(normalise_answer(c) in drawn for c in chosen):
            return "an answer that is not one of the row's options"
    return None


def auto_problem(cls: str, input_kind: str, auto: str) -> Optional[str]:
    if auto not in AUTO_VALUES:
        return "auto is not blank, yes or never"
    if auto == "yes" and never_auto(cls, input_kind):
        return f"class {cls} is never-auto: its answers are always put to him"
    return None


def never_auto(cls: str, input_kind: str) -> bool:
    """Is a row of this class and kind always put to him? Free text about pay
    is, because it is a negotiation; a pay NUMBER is volatile, not never-auto."""
    return cls in NEVER_AUTO_CLASSES or (cls == "compensation" and input_kind == "text")


def parse_bank(text: str, *, path_found: bool = True,
               today: Optional[datetime.date] = None) -> Bank:
    """Parse the TSV. Refuses the whole file on any malformed row.

    A partly-read bank is one whose missing rows nobody can see; worse, a
    shifted column would put a draft where a confirmed answer belongs. So one
    bad row refuses all of them, by line number.
    """
    when = today or datetime.date.today()
    numbered = [
        (number, line)
        for number, line in enumerate(text.splitlines(), start=1)
        if line.strip() and not line.startswith("#")
    ]
    if not numbered:
        raise BankError("the bank has no header line")
    header_line, header = numbered[0]
    if tuple(cell.strip() for cell in header.split("\t")) != COLUMNS:
        raise BankError(
            f"line {header_line}: the header is not exactly {'<TAB>'.join(COLUMNS)}"
        )

    answers: list[Answer] = []
    seen_ids: dict[str, int] = {}
    seen_slots: dict[tuple, int] = {}
    confirmed = unconfirmed = template = 0
    for number, line in numbered[1:]:
        cells = line.split("\t")
        if len(cells) != len(COLUMNS):
            raise BankError(f"line {number}: {len(cells)} cells, want {len(COLUMNS)}")
        row = dict(zip(COLUMNS, (cell.strip() for cell in cells)))
        entry_id = row["id"]
        if not _ID.match(entry_id):
            raise BankError(
                f"line {number}: the id is not 1-64 characters of a-z, 0-9, "
                "'_', '.', '-' starting with a letter or digit"
            )
        if entry_id in seen_ids:
            raise BankError(
                f"line {number}: id {entry_id!r} is already used on line {seen_ids[entry_id]}"
            )
        seen_ids[entry_id] = number
        where = f"line {number} ({entry_id})"
        kind, cls, platform = row["input_kind"], row["class"], row["platform"]
        if kind not in INPUT_KINDS:
            raise BankError(f"{where}: input_kind is not one of {', '.join(INPUT_KINDS)}")
        if cls not in CLASSES:
            raise BankError(f"{where}: class is not one of {', '.join(CLASSES)}")
        if platform not in PLATFORMS:
            raise BankError(f"{where}: platform is not one of {', '.join(PLATFORMS)}")
        question_key = normalise_question(row["question"])
        if not question_key:
            template += 1
            continue
        value = people_data.sanitise(row["CONFIRMED"], cap=MAX_ANSWER_CHARS + 1)
        if not value:
            unconfirmed += 1
            continue
        if cls == IMPORTED_CLASS:
            raise BankError(
                f"{where}: an imported row is confirmed only after you give it its "
                "class (its class decides whether it expires and whether it may fire unseen)"
            )
        options = split_options(row["options"])
        problem = (
            value_problem(kind, value, options)
            or auto_problem(cls, kind, row["auto"])
        )
        if problem:
            raise BankError(f"{where}: {problem}")
        confirmed_at = _date(row["confirmed_at"])
        if confirmed_at is None:
            raise BankError(f"{where}: a confirmed row needs confirmed_at as YYYY-MM-DD")
        if confirmed_at > when:
            raise BankError(f"{where}: confirmed_at is in the future")
        expires_at = _date(row["expires_at"]) if row["expires_at"] else None
        if row["expires_at"] and expires_at is None:
            raise BankError(f"{where}: expires_at is not YYYY-MM-DD")
        if cls in VOLATILE_CLASSES and expires_at is None:
            raise BankError(f"{where}: class {cls} goes out of date, so it needs expires_at")
        if expires_at is not None and expires_at <= confirmed_at:
            raise BankError(f"{where}: expires_at is not after confirmed_at")
        options_key = options_key_of(options) if options else None
        slot = (question_key, kind, platform, options_key)
        if slot in seen_slots:
            raise BankError(
                f"{where}: the same question, kind, platform and options are "
                f"confirmed on line {seen_slots[slot]} -- one question, one row"
            )
        seen_slots[slot] = number
        confirmed += 1
        answers.append(Answer(
            entry_id=entry_id,
            cls=cls,
            platform=platform,
            question_key=question_key,
            input_kind=kind,
            options_key=options_key,
            value=value,
            confirmed_at=confirmed_at,
            expires_at=expires_at,
            auto=not never_auto(cls, kind) and row["auto"] != "never",
            line=number,
        ))
    return Bank(
        answers=tuple(answers),
        path_found=path_found,
        rows_read=len(numbered) - 1,
        rows_confirmed=confirmed,
        rows_unconfirmed=unconfirmed,
        rows_template=template,
    )


def empty_bank() -> Bank:
    """The bank when there is no file: it answers nothing, and says so."""
    return Bank(answers=(), path_found=False, rows_read=0, rows_confirmed=0,
                rows_unconfirmed=0, rows_template=0)


def load_bank(path: Optional[Path] = None, *, today: Optional[datetime.date] = None) -> Bank:
    """Read the bank from ``path`` (default :func:`bank_path`), fresh every call.

    No file is :func:`empty_bank`, never an error. A file that is not UTF-8, or
    not a bank, raises :class:`BankError` with no value in it.
    """
    target = Path(path) if path is not None else bank_path()
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
    Without ``input_kind``, every kind is tried, and a question answered under
    two kinds is ``None`` too: which one the form wants is the caller's to say.
    ``auto: False`` means a proposal for a preview he reads, never an answer
    for a submit he does not see.
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
    so a bank row and a cache entry can be joined without guessing."""
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


def import_naukri_cache(cache: Mapping[str, Any]) -> list[dict[str, str]]:
    """Naukri's cached answers as bank rows: DRAFTS, never confirmed.

    Each row keeps the question verbatim and its option LABELS, carries the
    cached answer only in ``DRAFT_UNCONFIRMED``, and is of
    :data:`IMPORTED_CLASS`, which the loader refuses to confirm until he has
    given it a real class. A cached option answer that is not one of the
    drawn labels -- Naukri's formatter wraps an unmatched answer as-is -- is
    said so in the notes, because that is what its apply would send.
    """
    rows: list[dict[str, str]] = []
    for index, key in enumerate(sorted(cache), start=1):
        entry = cache[key]
        if not isinstance(entry, Mapping):
            continue
        name = str(entry.get("questionName") or "")
        kind = NAUKRI_KINDS.get(str(entry.get("questionType") or ""))
        options = _cache_options(key, name)
        labels = [str(v) for v in (options or {}).values()]
        notes: list[str] = []
        if kind is None:
            notes.append("question type not one the bank knows; kind left as text")
            kind = "text"
        if options is None:
            notes.append("options unreadable from the cache key")
        if any(OPTION_SEPARATOR in label for label in labels):
            notes.append("an option label contains the separator; options left empty")
            labels = []
        raw = entry.get("answer")
        parts = [str(x) for x in raw] if isinstance(raw, list) else [str(raw or "")]
        draft = OPTION_SEPARATOR.join(people_data.sanitise(p, cap=MAX_ANSWER_CHARS) for p in parts)
        if kind in OPTION_KINDS and labels:
            drawn = options_key_of(labels)
            if not all(normalise_answer(p) in drawn for p in parts):
                notes.append("the cached answer is NOT one of the options drawn")
        cached_at = entry.get("cached_at")
        when = ""
        if isinstance(cached_at, (int, float)):
            when = datetime.datetime.fromtimestamp(cached_at, tz=datetime.timezone.utc).date().isoformat()
        rows.append({
            "id": f"naukri.{index:03d}",
            "class": IMPORTED_CLASS,
            "platform": "naukri",
            "input_kind": kind,
            "question": people_data.sanitise(name, cap=QUESTION_CAP),
            "options": OPTION_SEPARATOR.join(people_data.sanitise(l, cap=MAX_ANSWER_CHARS) for l in labels),
            "DRAFT_UNCONFIRMED": draft,
            "CONFIRMED": "",
            "confirmed_at": "",
            "expires_at": "",
            "auto": "",
            "source": f"naukri questions.json, cached {when or 'on an unknown date'}",
            "notes": "; ".join(notes),
        })
    return rows


def naukri_cache_report(cache: Mapping[str, Any], bank: Bank, *,
                        today: Optional[datetime.date] = None) -> list[dict[str, Any]]:
    """What naukri_apply could submit unseen, entry by entry, against his bank.

    ``status`` per cached entry: ``confirmed_same`` (his confirmed, unexpired,
    auto-allowed answer equals the cached one), ``confirmed_differs``,
    ``never_auto`` (his row says it is always put to him), ``unconfirmed`` (no
    confirmed row). Only ``confirmed_same`` is an answer he has reviewed; the
    pipeline lists the rest before each Naukri yes. Pure, and local: the
    report carries his questions and answers back to his own machine's caller.
    """
    out: list[dict[str, Any]] = []
    for key in sorted(cache):
        entry = cache[key]
        if not isinstance(entry, Mapping):
            continue
        name = str(entry.get("questionName") or "")
        kind = NAUKRI_KINDS.get(str(entry.get("questionType") or ""), "text")
        labels = [str(v) for v in (_cache_options(key, name) or {}).values()]
        raw = entry.get("answer")
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
