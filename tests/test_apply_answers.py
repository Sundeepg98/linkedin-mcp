"""The answer bank reads HIS confirmed answers and nothing else (lane apply-26).

Every bank below is SYNTHETIC: invented questions, invented answers, no real
person or employer. The real bank is a gitignored file under ``_state/`` and no
test reads it; the Naukri cache below is invented too, in the shape
``naukri_server.cache`` writes.

Each guard was shown failing before it was trusted -- the mutation and the
failure are in ``_audit/2026-11-25-apply.md`` section 2.6.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

from linkedin_server import apply_answers, config
from linkedin_server.apply_answers import BankError, load_bank, lookup, parse_bank

REPO = Path(__file__).resolve().parents[1]
HEADER = "\t".join(apply_answers.COLUMNS)
TODAY = datetime.date(2026, 11, 25)
CONFIRMED_ON = "2026-11-01"

#: A value no message may ever carry. It stands for his phone number, his pay.
PLANT = "PLANTED-VALUE-7731"


def row(entry_id, kind, question, draft="", confirmed="", *, cls="other", platform="any",
        options="", confirmed_at=None, expires_at="", auto="", source="synthetic", notes=""):
    if confirmed_at is None:
        confirmed_at = CONFIRMED_ON if confirmed else ""
    return "\t".join((entry_id, cls, platform, kind, question, options, draft, confirmed,
                      confirmed_at, expires_at, auto, source, notes))


def bank(*rows: str) -> str:
    return "\n".join((HEADER,) + rows) + "\n"


def parsed(*rows: str) -> apply_answers.Bank:
    return parse_bank(bank(*rows), today=TODAY)


# ---------------------------------------------------------------------------
# 1. The one rule: CONFIRMED only
# ---------------------------------------------------------------------------


def test_the_draft_column_is_never_read():
    """A full draft and an empty CONFIRMED answers nothing, by construction."""
    result = parsed(
        row("yoe-widgets", "numeric", "How many years of experience do you have with Widgets?",
            draft="4"),
        row("auth", "radio", "Are you legally authorized to work in Elsewhere?", draft="Yes"),
    )
    assert result.answers == ()
    assert result.rows_unconfirmed == 2
    assert result.answer_for(
        "How many years of experience do you have with Widgets?", "numeric") is None
    assert not any("draft" in name.lower() for name in apply_answers.Answer.__dataclass_fields__), (
        "an Answer grew a field for the draft; a reader could then hand it on"
    )


def test_a_confirmed_answer_is_read_and_its_draft_is_not():
    result = parsed(
        row("yoe-widgets", "numeric", "How many years of experience do you have with Widgets?",
            draft="4", confirmed="3"),
    )
    answer = result.answer_for("How many years of experience do you have with Widgets?", "numeric")
    assert answer is not None and answer.value == "3"
    assert answer.entry_id == "yoe-widgets"


def test_no_file_is_an_empty_bank_not_an_error(tmp_path):
    result = load_bank(tmp_path / "absent.tsv")
    assert result.path_found is False
    assert result.answers == ()
    assert result.status()["bank_file_found"] is False


# ---------------------------------------------------------------------------
# 2. No inference: the question's own words, the field's own kind
# ---------------------------------------------------------------------------

QUESTION = "How many years of experience do you have with Widgets?"


@pytest.mark.parametrize(
    "drawn",
    [
        QUESTION,
        "  how many years of EXPERIENCE do you have with widgets?  ",
        "How many years of\nexperience do you\thave with Widgets?",
        "How many​ years of experience do you have with Widgets?",
    ],
)
def test_whitespace_case_and_invisible_characters_do_not_make_a_new_question(drawn):
    result = parsed(row("w", "numeric", QUESTION, confirmed="3"))
    assert result.answer_for(drawn, "numeric") is not None


@pytest.mark.parametrize(
    "drawn",
    [
        "How many years of Widgets experience do you have?",
        "How many years of experience do you have with Widgets in a lead role?",
        "years of experience with Widgets",
        "How many years of experience do you have with Widgets",
        "How many years of experience do you have with Widgets? *",
    ],
)
def test_a_question_is_answered_only_by_its_own_words(drawn):
    """NO keyword match, no prefix match, no "close enough"."""
    result = parsed(row("w", "numeric", QUESTION, confirmed="3"))
    assert result.answer_for(drawn, "numeric") is None


def test_an_answer_answers_only_its_own_input_kind():
    result = parsed(row("w", "numeric", QUESTION, confirmed="3"))
    for other in ("text", "select", "radio", "checkbox", "multi_select", "typeahead", "file"):
        assert result.answer_for(QUESTION, other) is None, other


# ---------------------------------------------------------------------------
# 3. The file is refused whole, and no error carries a value
# ---------------------------------------------------------------------------

MALFORMED = {
    "cell_count": bank(row("a", "text", "Q one?", confirmed=PLANT) + "\textra"),
    "numeric": bank(row("a", "numeric", "Q one?", confirmed=PLANT)),
    "checkbox": bank(row("a", "checkbox", "Q one?", confirmed=PLANT)),
    "input_kind": bank(row("a", PLANT, "Q one?", confirmed="x")),
    "class": bank(row("a", "text", "Q one?", confirmed="x", cls=PLANT)),
    "platform": bank(row("a", "text", "Q one?", confirmed="x", platform=PLANT)),
    "id": bank(row(PLANT, "text", "Q one?", confirmed="x")),
    "duplicate_question": bank(
        row("a", "text", "Q one?", confirmed=PLANT),
        row("b", "text", "q ONE?", confirmed=PLANT + "-2"),
    ),
    "duplicate_id": bank(
        row("a", "text", "Q one?", confirmed=PLANT),
        row("a", "text", "Q two?", confirmed=PLANT),
    ),
    "too_long": bank(row("a", "text", "Q one?", confirmed=PLANT * 100)),
    "not_an_option": bank(row("a", "radio", "Q one?", confirmed=PLANT, options="Yes | No")),
    "confirmed_at": bank(row("a", "text", "Q one?", confirmed=PLANT, confirmed_at=PLANT)),
    "expires_at": bank(row("a", "text", "Q one?", confirmed=PLANT, expires_at=PLANT)),
    "auto": bank(row("a", "text", "Q one?", confirmed=PLANT, auto=PLANT)),
}


@pytest.mark.parametrize("case", sorted(MALFORMED))
def test_a_malformed_bank_is_refused_and_the_refusal_carries_no_value(case):
    with pytest.raises(BankError) as raised:
        parse_bank(MALFORMED[case], today=TODAY)
    message = str(raised.value)
    assert PLANT not in message, f"{case}: the refusal quoted a value: {message!r}"
    assert "line " in message, f"{case}: the refusal does not name the line: {message!r}"


def test_one_question_one_row():
    with pytest.raises(BankError) as raised:
        parse_bank(MALFORMED["duplicate_question"], today=TODAY)
    assert "line 2" in str(raised.value) and "line 3" in str(raised.value)


def test_a_header_out_of_order_refuses_the_whole_file():
    """A moved column is how a draft would be read as a confirmed answer."""
    swapped = list(apply_answers.COLUMNS)
    i, j = swapped.index("DRAFT_UNCONFIRMED"), swapped.index("CONFIRMED")
    swapped[i], swapped[j] = swapped[j], swapped[i]
    text = "\t".join(swapped) + "\n" + row("a", "numeric", QUESTION, draft="9") + "\n"
    with pytest.raises(BankError):
        parse_bank(text, today=TODAY)


def test_a_bank_that_is_not_utf8_is_refused_without_its_bytes(tmp_path):
    target = tmp_path / apply_answers.BANK_FILENAME
    target.write_bytes(HEADER.encode("ascii") + b"\n" + b"a\tother\tany\ttext\tQ?\t\t\t\xff\xfe\t\t\t\ts\t\n")
    with pytest.raises(BankError) as raised:
        load_bank(target)
    assert "UTF-8" in str(raised.value)


# ---------------------------------------------------------------------------
# 4. Provenance, dates and expiry
# ---------------------------------------------------------------------------


def test_a_confirmed_row_carries_the_date_he_confirmed_it():
    with pytest.raises(BankError) as raised:
        parsed(row("a", "text", "Q one?", confirmed="x", confirmed_at=""))
    assert "confirmed_at" in str(raised.value)
    with pytest.raises(BankError) as raised:
        parsed(row("a", "text", "Q one?", confirmed="x", confirmed_at="2026-12-31"))
    assert "future" in str(raised.value)


def test_an_expiry_must_follow_the_confirmation():
    with pytest.raises(BankError):
        parsed(row("a", "text", "Q one?", confirmed="x", expires_at="2026-10-01"))


@pytest.mark.parametrize("cls", sorted(apply_answers.VOLATILE_CLASSES))
def test_a_volatile_answer_cannot_be_confirmed_without_an_expiry(cls):
    with pytest.raises(BankError) as raised:
        parsed(row("a", "numeric", "Q one?", confirmed="5", cls=cls))
    assert "expires_at" in str(raised.value)
    assert parsed(row("a", "numeric", "Q one?", confirmed="5", cls=cls,
                      expires_at="2027-02-01")).rows_confirmed == 1


def test_an_expired_answer_answers_nothing():
    result = parsed(row("a", "numeric", QUESTION, confirmed="5", cls="experience",
                        expires_at="2026-12-01"))
    assert result.answer_for(QUESTION, "numeric", today=datetime.date(2026, 11, 30)) is not None
    assert result.answer_for(QUESTION, "numeric", today=datetime.date(2026, 12, 2)) is None
    assert result.status(datetime.date(2026, 12, 2))["rows_confirmed_and_expired"] == 1


# ---------------------------------------------------------------------------
# 5. Never-auto, platforms and option sets
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", sorted(apply_answers.NEVER_AUTO_CLASSES))
def test_a_never_auto_class_cannot_be_set_to_fire_unseen(cls):
    with pytest.raises(BankError) as raised:
        parsed(row("a", "radio", "Q one?", confirmed="Yes", cls=cls, auto="yes"))
    assert "never-auto" in str(raised.value)
    answer = parsed(row("a", "radio", "Q one?", confirmed="Yes", cls=cls)).answer_for("Q one?", "radio")
    assert answer is not None and answer.auto is False


def test_free_text_about_pay_is_never_auto_and_a_pay_number_is_not():
    text = parsed(row("a", "text", "Q one?", confirmed="x", cls="compensation",
                      expires_at="2027-01-01"))
    assert text.answer_for("Q one?", "text").auto is False
    number = parsed(row("a", "numeric", "Q one?", confirmed="10", cls="compensation",
                        expires_at="2027-01-01"))
    assert number.answer_for("Q one?", "numeric").auto is True


def test_a_row_answers_only_its_own_platform_and_prefers_its_own():
    result = parsed(
        row("n", "text", "Q one?", confirmed="from naukri", platform="naukri"),
        row("any", "text", "Q two?", confirmed="anywhere"),
        row("any2", "text", "Q three?", confirmed="neutral"),
        row("li", "text", "Q three?", confirmed="linkedin's own", platform="linkedin"),
    )
    assert result.answer_for("Q one?", "text", platform="linkedin") is None
    assert result.answer_for("Q one?", "text", platform="naukri").value == "from naukri"
    assert result.answer_for("Q two?", "text", platform="linkedin").value == "anywhere"
    assert result.answer_for("Q three?", "text", platform="linkedin").value == "linkedin's own"
    assert result.answer_for("Q three?", "text", platform="uplers").value == "neutral"


def test_a_row_confirmed_against_options_answers_only_that_option_set():
    result = parsed(row("a", "radio", "Q one?", confirmed="Yes", options="Yes | No"))
    assert result.answer_for("Q one?", "radio", options=("No", "Yes")) is not None
    assert result.answer_for("Q one?", "radio", options=("Yes", "No", "Prefer not to say")) is None
    assert result.answer_for("Q one?", "radio") is None


@pytest.mark.parametrize("kind,options,answer", [
    ("radio", "Yes | No", "Maybe"),
    ("select", "A | B", "A | B"),
    ("multi_select", "A | B", "A | C"),
])
def test_an_option_answer_must_be_one_of_its_options(kind, options, answer):
    with pytest.raises(BankError):
        parsed(row("a", kind, "Q one?", confirmed=answer, options=options))


@pytest.mark.parametrize("kind", ["select", "radio"])
def test_a_single_choice_answer_names_one_option_even_with_no_options_named(kind):
    with pytest.raises(BankError) as raised:
        parsed(row("a", kind, "Q one?", confirmed="A | B"))
    assert "more than one option" in str(raised.value)
    assert parsed(row("a", "multi_select", "Q one?", confirmed="A | B")).rows_confirmed == 1


def test_an_imported_row_is_confirmed_only_after_he_classifies_it():
    with pytest.raises(BankError) as raised:
        parsed(row("n", "text", "Q one?", confirmed="x", cls=apply_answers.IMPORTED_CLASS,
                   platform="naukri"))
    assert "class" in str(raised.value)


# ---------------------------------------------------------------------------
# 6. The read API other lanes use
# ---------------------------------------------------------------------------


def test_lookup_returns_the_read_shape_and_none_is_a_question():
    result = parsed(row("w", "numeric", QUESTION, confirmed="3"))
    found = lookup(QUESTION, platform="linkedin", bank=result, today=TODAY)
    assert found == {
        "answer": "3", "type": "numeric", "provenance": "operator_confirmed",
        "confirmed_at": CONFIRMED_ON, "expires_at": None, "auto": True,
        "entry_id": "w", "platform": "any",
    }
    assert lookup("A question nobody answered?", bank=result, today=TODAY) is None


def test_lookup_without_a_kind_refuses_a_question_answered_under_two():
    result = parsed(row("t", "text", "Q one?", confirmed="3"),
                    row("n", "numeric", "Q one?", confirmed="3"))
    assert lookup("Q one?", bank=result, today=TODAY) is None
    assert lookup("Q one?", input_kind="numeric", bank=result, today=TODAY)["entry_id"] == "n"


def test_lookup_reads_the_bank_from_disk_when_none_is_handed_in(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "STATE_DIR", tmp_path)
    (tmp_path / apply_answers.BANK_FILENAME).write_text(
        bank(row("w", "numeric", QUESTION, confirmed="3")), encoding="utf-8")
    assert lookup(QUESTION, today=TODAY)["answer"] == "3"


# ---------------------------------------------------------------------------
# 7. Naukri's cache, which its apply submits unseen
# ---------------------------------------------------------------------------

CACHE = {
    'Notice period in days?_{}': {
        "questionType": "Text Box", "questionName": "Notice period in days?",
        "answer": "30", "cached_at": 1773300000.0,
    },
    'Willing to relocate?_{"1": "Yes", "2": "No"}': {
        "questionType": "Radio Button", "questionName": "Willing to relocate?",
        "answer": ["Sometimes"], "cached_at": 1773300000.0,
    },
    'Tools used?_{"a": "Docker", "b": "Kafka", "c": "Redis"}': {
        "questionType": "Check Box", "questionName": "Tools used?",
        "answer": ["Docker", "Redis"], "cached_at": 1773300000.0,
    },
}


def test_the_naukri_key_is_naukris_own():
    """``naukri_server.cache._cache_key``: the name verbatim, '_', sorted JSON."""
    assert apply_answers.naukri_cache_key("Willing to relocate?", {"2": "No", "1": "Yes"}) == (
        'Willing to relocate?_{"1": "Yes", "2": "No"}'
    )
    assert apply_answers.naukri_cache_key(" Spaced  Name ", {}) == " Spaced  Name _{}"
    for key, entry in CACHE.items():
        options = apply_answers._cache_options(key, entry["questionName"])
        assert apply_answers.naukri_cache_key(entry["questionName"], options) == key


def test_a_naukri_import_is_drafts_only_and_names_an_answer_no_option_matches():
    rows = apply_answers.import_naukri_cache(CACHE)
    assert len(rows) == 3
    assert all(r["CONFIRMED"] == "" and r["class"] == apply_answers.IMPORTED_CLASS for r in rows)
    by_question = {r["question"]: r for r in rows}
    relocate = by_question["Willing to relocate?"]
    assert relocate["input_kind"] == "radio" and relocate["options"] == "Yes | No"
    assert relocate["DRAFT_UNCONFIRMED"] == "Sometimes"
    assert "NOT one of the options drawn" in relocate["notes"]
    tools = by_question["Tools used?"]
    assert tools["input_kind"] == "multi_select" and tools["DRAFT_UNCONFIRMED"] == "Docker | Redis"
    assert tools["notes"] == ""
    imported = parse_bank(bank(*("\t".join(r[c] for c in apply_answers.COLUMNS) for r in rows)),
                          today=TODAY)
    assert imported.answers == () and imported.rows_unconfirmed == 3


def test_the_cache_report_names_what_could_fire_unseen():
    result = parsed(
        row("notice", "text", "Notice period in days?", confirmed="45", cls="availability",
            platform="naukri", expires_at="2027-01-01"),
        row("tools", "multi_select", "Tools used?", confirmed="Docker | Redis",
            options="Docker | Kafka | Redis", platform="naukri"),
    )
    report = {r["question"]: r["status"]
              for r in apply_answers.naukri_cache_report(CACHE, result, today=TODAY)}
    assert report == {
        "Notice period in days?": "confirmed_differs",
        "Willing to relocate?": "unconfirmed",
        "Tools used?": "confirmed_same",
    }
    attested = parsed(row("r", "radio", "Willing to relocate?", confirmed="No",
                          cls="work_authorisation", options="Yes | No", platform="naukri"))
    statuses = {r["question"]: r["status"]
                for r in apply_answers.naukri_cache_report(CACHE, attested, today=TODAY)}
    assert statuses["Willing to relocate?"] == "never_auto"


# ---------------------------------------------------------------------------
# 8. Where it lives, and that it is read fresh
# ---------------------------------------------------------------------------


def test_the_bank_lives_under_the_gitignored_state_dir():
    assert apply_answers.bank_path().parent == Path(config.STATE_DIR)
    ignored = (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "_state/" in ignored, "the state directory is no longer ignored whole"


def test_the_bank_is_read_fresh_every_call(tmp_path):
    target = tmp_path / apply_answers.BANK_FILENAME
    target.write_text(bank(row("w", "numeric", QUESTION)), encoding="utf-8")
    assert load_bank(target).answer_for(QUESTION, "numeric") is None
    target.write_text(bank(row("w", "numeric", QUESTION, confirmed="3")), encoding="utf-8")
    answer = load_bank(target).answer_for(QUESTION, "numeric")
    assert answer is not None and answer.value == "3"


def test_comments_and_blank_lines_are_not_rows():
    text = "# a comment\n\n" + bank(row("w", "numeric", QUESTION, confirmed="3")) + "\n# trailing\n"
    result = parse_bank(text, today=TODAY)
    assert result.rows_read == 1 and result.rows_confirmed == 1


def test_a_row_with_no_question_is_guidance_and_answers_nothing():
    result = parsed(row("class-only", "numeric", "", draft="4", confirmed="4"))
    assert result.rows_template == 1 and result.answers == ()


def test_status_carries_counts_only():
    status = parsed(row("w", "numeric", QUESTION, confirmed="3")).status(TODAY)
    assert all(isinstance(value, (int, bool)) for value in status.values()), status
    assert "Widgets" not in repr(status)
