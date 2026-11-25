"""The answer bank reads HIS confirmed answers and nothing else (lane apply-26).

Every bank below is SYNTHETIC: invented questions, invented answers, no real
person or employer. The real bank is a gitignored JSON file under the jobhunt
root and no test reads it; the Naukri cache below is invented too, in the shape
``naukri_server.cache`` writes.

Each guard was shown failing before it was trusted -- the mutation and the
failure are in ``_audit/2026-11-25-apply.md`` section 2.6.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

import pytest

from linkedin_server import apply_answers
from linkedin_server.apply_answers import BankError, load_bank, lookup, parse_bank

REPO = Path(__file__).resolve().parents[1]
TODAY = datetime.date(2026, 11, 25)
CONFIRMED_ON = "2026-11-01"

#: A value no message may ever carry. It stands for his phone number, his pay.
PLANT = "PLANTED-VALUE-7731"


def entry(entry_id, kind, question, draft="", confirmed="", *, cls="other", platform="any",
          options=(), confirmed_at=None, expires_at="", auto="", per_platform=None,
          extra_platforms=None, native_type=""):
    """One SYNTHETIC class entry with one wording on one platform."""
    if confirmed_at is None:
        confirmed_at = CONFIRMED_ON if (confirmed or per_platform) else ""
    platforms = {}
    if question is not None:
        platforms[platform] = {"questions": [question], "options": list(options),
                               "native_type": native_type}
    platforms.update(extra_platforms or {})
    return {
        "id": entry_id, "family": cls, "input_kind": kind, "platforms": platforms,
        "draft": {"value": draft, "per_platform": {}, "source": "synthetic"},
        "confirmed": {"value": confirmed, "per_platform": dict(per_platform or {}),
                      "confirmed_at": confirmed_at, "expires_at": expires_at, "auto": auto},
        "notes": "",
    }


def bank(*entries) -> str:
    return json.dumps({"schema": apply_answers.SCHEMA_ID, "entries": list(entries)})


def parsed(*entries) -> apply_answers.Bank:
    return parse_bank(bank(*entries), today=TODAY)


# ---------------------------------------------------------------------------
# 1. The one rule: CONFIRMED only
# ---------------------------------------------------------------------------

QUESTION = "How many years of experience do you have with Widgets?"


def test_the_draft_is_never_read():
    """A full draft and an empty confirmed block answers nothing, by construction."""
    result = parsed(
        entry("experience.years.widgets", "numeric", QUESTION, draft="4"),
        entry("work_authorisation.elsewhere", "radio",
              "Are you legally authorized to work in Elsewhere?", draft="Yes"),
    )
    assert result.answers == ()
    assert result.rows_unconfirmed == 2
    assert result.answer_for(QUESTION, "numeric") is None
    assert not any("draft" in name.lower() for name in apply_answers.Answer.__dataclass_fields__), (
        "an Answer grew a field for the draft; a reader could then hand it on"
    )


def test_a_confirmed_answer_is_read_and_its_draft_is_not():
    result = parsed(entry("experience.years.widgets", "numeric", QUESTION, draft="4", confirmed="3"))
    answer = result.answer_for(QUESTION, "numeric")
    assert answer is not None and answer.value == "3"
    assert answer.entry_id == "experience.years.widgets"


def test_no_file_is_an_empty_bank_not_an_error(tmp_path):
    result = load_bank(tmp_path / "absent.json")
    assert result.path_found is False and result.answers == ()
    assert result.status()["bank_file_found"] is False


# ---------------------------------------------------------------------------
# 2. No inference: the class's own wordings, the field's own kind
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("drawn", [
    QUESTION,
    "  how many years of EXPERIENCE do you have with widgets?  ",
    "How many years of\nexperience do you\thave with Widgets?",
    "How many\u200b years of experience do you have with Widgets?",
])
def test_whitespace_case_and_invisible_characters_do_not_make_a_new_question(drawn):
    result = parsed(entry("w", "numeric", QUESTION, confirmed="3"))
    assert result.answer_for(drawn, "numeric") is not None


@pytest.mark.parametrize("drawn", [
    "How many years of Widgets experience do you have?",
    "How many years of experience do you have with Widgets in a lead role?",
    "years of experience with Widgets",
    "How many years of experience do you have with Widgets",
    "How many years of experience do you have with Widgets? *",
])
def test_a_question_is_answered_only_by_a_wording_its_class_lists(drawn):
    """NO keyword match, no prefix match, no "close enough"."""
    result = parsed(entry("w", "numeric", QUESTION, confirmed="3"))
    assert result.answer_for(drawn, "numeric") is None


def test_one_class_answers_every_wording_it_lists_on_every_platform_it_names():
    """A normalized class with per-platform hints: one answer, many wordings."""
    result = parsed(entry(
        "experience.years.widgets", "numeric", QUESTION, confirmed="3", platform="linkedin",
        extra_platforms={"naukri": {"questions": ["Widgets experience (years)?"],
                                    "options": [], "native_type": "Text Box"}},
    ))
    assert result.answer_for(QUESTION, "numeric", platform="linkedin").value == "3"
    assert result.answer_for("Widgets experience (years)?", "numeric", platform="naukri").value == "3"
    assert result.answer_for(QUESTION, "numeric", platform="naukri") is None


def test_an_answer_answers_only_its_own_input_kind():
    result = parsed(entry("w", "numeric", QUESTION, confirmed="3"))
    for other in ("text", "select", "radio", "checkbox", "multi_select", "typeahead", "file"):
        assert result.answer_for(QUESTION, other) is None, other


# ---------------------------------------------------------------------------
# 3. The file is refused whole, and no error carries a value
# ---------------------------------------------------------------------------

MALFORMED = {
    "unknown_key": bank(dict(entry("a", "text", "Q one?", confirmed=PLANT), confimed={"value": PLANT})),
    "numeric": bank(entry("a", "numeric", "Q one?", confirmed=PLANT)),
    "checkbox": bank(entry("a", "checkbox", "Q one?", confirmed=PLANT)),
    "input_kind": bank(entry("a", PLANT, "Q one?", confirmed="x")),
    "family": bank(entry("a", "text", "Q one?", confirmed="x", cls=PLANT)),
    "platform": bank(entry("a", "text", "Q one?", confirmed="x", platform=PLANT)),
    "id": bank(entry(PLANT, "text", "Q one?", confirmed="x")),
    "duplicate_wording": bank(
        entry("a", "text", "Q one?", confirmed=PLANT),
        entry("b", "text", "q ONE?", confirmed=PLANT + "-2"),
    ),
    "duplicate_id": bank(
        entry("a", "text", "Q one?", confirmed=PLANT),
        entry("a", "text", "Q two?", confirmed=PLANT),
    ),
    "too_long": bank(entry("a", "text", "Q one?", confirmed=PLANT * 100)),
    "not_an_option": bank(entry("a", "radio", "Q one?", confirmed=PLANT, options=("Yes", "No"))),
    "confirmed_at": bank(entry("a", "text", "Q one?", confirmed=PLANT, confirmed_at=PLANT)),
    "expires_at": bank(entry("a", "text", "Q one?", confirmed=PLANT, expires_at=PLANT)),
    "auto": bank(entry("a", "text", "Q one?", confirmed=PLANT, auto=PLANT)),
    "per_platform": bank(entry("a", "text", "Q one?", per_platform={PLANT: PLANT})),
    "not_text": bank(dict(entry("a", "text", "Q one?", confirmed="x"), notes=[PLANT])),
}


@pytest.mark.parametrize("case", sorted(MALFORMED))
def test_a_malformed_bank_is_refused_and_the_refusal_carries_no_value(case):
    with pytest.raises(BankError) as raised:
        parse_bank(MALFORMED[case], today=TODAY)
    message = str(raised.value)
    assert PLANT not in message, f"{case}: the refusal quoted a value: {message!r}"
    assert "entry " in message, f"{case}: the refusal does not name the entry: {message!r}"


@pytest.mark.parametrize("text", [
    '{"schema": "' + PLANT,
    json.dumps({"schema": PLANT, "entries": []}),
    json.dumps({"schema": apply_answers.SCHEMA_ID, "entries": PLANT}),
    json.dumps([PLANT]),
])
def test_a_document_that_is_not_a_bank_is_refused_without_its_content(text):
    with pytest.raises(BankError) as raised:
        parse_bank(text, today=TODAY)
    assert PLANT not in str(raised.value), str(raised.value)


def test_one_wording_one_class():
    with pytest.raises(BankError) as raised:
        parse_bank(MALFORMED["duplicate_wording"], today=TODAY)
    assert "entry 2" in str(raised.value) and "entry 1" in str(raised.value)


def test_a_misspelt_block_is_refused_rather_than_ignored():
    """``confimed`` read as absent would be an answer he gave, silently dropped."""
    with pytest.raises(BankError) as raised:
        parse_bank(MALFORMED["unknown_key"], today=TODAY)
    assert "unknown keys" in str(raised.value)


def test_a_bank_that_is_not_utf8_is_refused_without_its_bytes(tmp_path):
    target = tmp_path / apply_answers.BANK_FILENAME
    target.write_bytes(b'{"schema": "\xff\xfe"}')
    with pytest.raises(BankError) as raised:
        load_bank(target)
    assert "UTF-8" in str(raised.value)


# ---------------------------------------------------------------------------
# 4. Provenance, dates and expiry
# ---------------------------------------------------------------------------


def test_a_confirmed_entry_carries_the_date_he_confirmed_it():
    with pytest.raises(BankError) as raised:
        parsed(entry("a", "text", "Q one?", confirmed="x", confirmed_at=""))
    assert "confirmed_at" in str(raised.value)
    with pytest.raises(BankError) as raised:
        parsed(entry("a", "text", "Q one?", confirmed="x", confirmed_at="2026-12-31"))
    assert "future" in str(raised.value)


def test_an_expiry_must_follow_the_confirmation():
    with pytest.raises(BankError):
        parsed(entry("a", "text", "Q one?", confirmed="x", expires_at="2026-10-01"))


@pytest.mark.parametrize("cls", sorted(apply_answers.VOLATILE_FAMILIES))
def test_a_volatile_answer_cannot_be_confirmed_without_an_expiry(cls):
    with pytest.raises(BankError) as raised:
        parsed(entry("a", "numeric", "Q one?", confirmed="5", cls=cls))
    assert "expires_at" in str(raised.value)
    assert parsed(entry("a", "numeric", "Q one?", confirmed="5", cls=cls,
                        expires_at="2027-02-01")).rows_confirmed == 1


def test_an_expired_answer_answers_nothing():
    result = parsed(entry("a", "numeric", QUESTION, confirmed="5", cls="experience",
                          expires_at="2026-12-01"))
    assert result.answer_for(QUESTION, "numeric", today=datetime.date(2026, 11, 30)) is not None
    assert result.answer_for(QUESTION, "numeric", today=datetime.date(2026, 12, 2)) is None
    assert result.status(datetime.date(2026, 12, 2))["entries_confirmed_and_expired"] == 1


def test_a_confirmed_entry_with_no_wording_is_refused_not_kept():
    """It could answer nothing; keeping it would look like coverage."""
    with pytest.raises(BankError) as raised:
        parsed(entry("a", "text", None, confirmed="x"))
    assert "no question wording" in str(raised.value)


# ---------------------------------------------------------------------------
# 5. Never-auto, platforms, option sets and per-platform formatting
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", sorted(apply_answers.NEVER_AUTO_FAMILIES))
def test_a_never_auto_family_cannot_be_set_to_fire_unseen(cls):
    with pytest.raises(BankError) as raised:
        parsed(entry("a", "radio", "Q one?", confirmed="Yes", cls=cls, auto="yes"))
    assert "never-auto" in str(raised.value)
    answer = parsed(entry("a", "radio", "Q one?", confirmed="Yes", cls=cls)).answer_for("Q one?", "radio")
    assert answer is not None and answer.auto is False


def test_free_text_about_pay_is_never_auto_and_a_pay_number_is_not():
    text = parsed(entry("a", "text", "Q one?", confirmed="x", cls="compensation",
                        expires_at="2027-01-01"))
    assert text.answer_for("Q one?", "text").auto is False
    number = parsed(entry("a", "numeric", "Q one?", confirmed="10", cls="compensation",
                          expires_at="2027-01-01"))
    assert number.answer_for("Q one?", "numeric").auto is True


def test_a_hint_answers_only_its_own_platform_and_prefers_its_own():
    result = parsed(
        entry("n", "text", "Q one?", confirmed="from naukri", platform="naukri"),
        entry("any", "text", "Q two?", confirmed="anywhere"),
        entry("any2", "text", "Q three?", confirmed="neutral"),
        entry("li", "text", "Q three?", confirmed="linkedin's own", platform="linkedin"),
    )
    assert result.answer_for("Q one?", "text", platform="linkedin") is None
    assert result.answer_for("Q one?", "text", platform="naukri").value == "from naukri"
    assert result.answer_for("Q two?", "text", platform="linkedin").value == "anywhere"
    assert result.answer_for("Q three?", "text", platform="linkedin").value == "linkedin's own"
    assert result.answer_for("Q three?", "text", platform="uplers").value == "neutral"


def test_a_per_platform_answer_formats_the_neutral_one_for_that_platform():
    """Naukri's option label for a notice period LinkedIn asks in days."""
    result = parsed(entry(
        "availability.notice_period", "text", "Notice period in days?", confirmed="30",
        cls="availability", expires_at="2027-01-01", platform="linkedin",
        per_platform={"naukri": "1 Month"},
        extra_platforms={"naukri": {"questions": ["Notice period?"],
                                    "options": ["15 Days or less", "1 Month", "2 Months"],
                                    "native_type": "Radio Button"}},
    ))
    assert result.answer_for("Notice period in days?", "text", platform="linkedin").value == "30"
    with pytest.raises(BankError):
        # a radio hint's answer must be one of its labels: the neutral "30"
        # is not, which is why Naukri's own label is a per-platform answer
        parsed(entry("x", "radio", "Notice period?", confirmed="30", platform="naukri",
                     options=("15 Days or less", "1 Month")))
    radio = parsed(entry("availability.notice_period", "radio", "Notice period?",
                         confirmed="30", per_platform={"naukri": "1 Month"},
                         cls="availability", expires_at="2027-01-01", platform="naukri",
                         options=("15 Days or less", "1 Month", "2 Months")))
    answer = radio.answer_for("Notice period?", "radio", platform="naukri",
                              options=("15 Days or less", "1 Month", "2 Months"))
    assert answer.value == "1 Month"


def test_a_hint_that_names_options_matches_only_that_option_set():
    result = parsed(entry("a", "radio", "Q one?", confirmed="Yes", options=("Yes", "No")))
    assert result.answer_for("Q one?", "radio", options=("No", "Yes")) is not None
    assert result.answer_for("Q one?", "radio", options=("Yes", "No", "Prefer not to say")) is None
    assert result.answer_for("Q one?", "radio") is None


@pytest.mark.parametrize("kind,options,answer", [
    ("radio", ("Yes", "No"), "Maybe"),
    ("select", ("A", "B"), "A | B"),
    ("multi_select", ("A", "B"), "A | C"),
])
def test_an_option_answer_must_be_one_of_its_options(kind, options, answer):
    with pytest.raises(BankError):
        parsed(entry("a", kind, "Q one?", confirmed=answer, options=options))


@pytest.mark.parametrize("kind", ["select", "radio"])
def test_a_single_choice_answer_names_one_option_even_with_no_options_named(kind):
    with pytest.raises(BankError) as raised:
        parsed(entry("a", kind, "Q one?", confirmed="A | B"))
    assert "more than one option" in str(raised.value)
    assert parsed(entry("a", "multi_select", "Q one?", confirmed="A | B")).rows_confirmed == 1


def test_an_imported_entry_is_confirmed_only_after_he_gives_it_a_family():
    with pytest.raises(BankError) as raised:
        parsed(entry("n", "text", "Q one?", confirmed="x", cls=apply_answers.IMPORTED_FAMILY,
                     platform="naukri"))
    assert "family" in str(raised.value)


# ---------------------------------------------------------------------------
# 6. The read API other lanes use, and where the bank is
# ---------------------------------------------------------------------------


def test_lookup_returns_the_read_shape_and_none_is_a_question():
    result = parsed(entry("w", "numeric", QUESTION, confirmed="3"))
    found = lookup(QUESTION, platform="linkedin", bank=result, today=TODAY)
    assert found == {
        "answer": "3", "type": "numeric", "provenance": "operator_confirmed",
        "confirmed_at": CONFIRMED_ON, "expires_at": None, "auto": True,
        "entry_id": "w", "platform": "any",
    }
    assert lookup("A question nobody answered?", bank=result, today=TODAY) is None


def test_lookup_without_a_kind_refuses_a_question_answered_under_two():
    result = parsed(entry("t", "text", "Q one?", confirmed="3"),
                    entry("n", "numeric", "Q one?", confirmed="3"))
    assert lookup("Q one?", bank=result, today=TODAY) is None
    assert lookup("Q one?", input_kind="numeric", bank=result, today=TODAY)["entry_id"] == "n"


def test_the_bank_is_found_by_its_own_variable_then_the_root_then_the_marker(tmp_path):
    root = tmp_path / "jobhunt"
    deep = root / "mcp-servers" / "linkedin" / "linkedin_server"
    deep.mkdir(parents=True)
    explicit = tmp_path / "elsewhere.json"
    found = apply_answers.locate_bank(deep, env={apply_answers.ENV_BANK: str(explicit),
                                                 apply_answers.ENV_ROOT: str(root)})
    assert found.path == explicit and found.how == apply_answers.ENV_BANK
    found = apply_answers.locate_bank(deep, env={apply_answers.ENV_ROOT: str(root)})
    assert found.path == root.joinpath(*apply_answers.BANK_PARTS)
    assert found.how == apply_answers.ENV_ROOT
    assert apply_answers.locate_bank(deep, env={}).path is None
    (root / apply_answers.ROOT_MARKER).write_text("", encoding="utf-8")
    found = apply_answers.locate_bank(deep, env={})
    assert found.path == root.joinpath(*apply_answers.BANK_PARTS)
    assert found.how.startswith("walk-up")
    assert apply_answers.BANK_PARTS == ("mcp-servers", "_audit", "job-pipeline", "answer-bank.json")


def test_the_walk_up_stops_at_its_bound(tmp_path):
    root = tmp_path / "jobhunt"
    deep = root.joinpath(*(f"d{i}" for i in range(apply_answers.MAX_WALK_UP + 1)))
    deep.mkdir(parents=True)
    (root / apply_answers.ROOT_MARKER).write_text("", encoding="utf-8")
    assert apply_answers.locate_bank(deep, env={}).path is None
    assert apply_answers.locate_bank(deep.parent, env={}).path is not None


# ---------------------------------------------------------------------------
# 6b. Parity with jobcore's config.locate: ONE root, and JOBHUNT_HOME is jobcore's
# ---------------------------------------------------------------------------
#
# THE SEMANTICS HELD HERE, from jobcore/src/jobcore/config.py (``locate``):
#   * JOBHUNT_HOME names the directory that HOLDS jobhunt.json -- it reads
#     ``Path(home) / CONFIG_FILENAME`` -- so it is never the root;
#   * a directory holding ``.jobhunt-root`` is the root, and its config is
#     ``<root>/config/jobhunt.json``;
#   * the walk looks at the start and at most MAX_WALK_UP (6) parents.
# The first tests hold the bank to those words with no jobcore import; the
# last runs jobcore's OWN locate, found the way the vendored-copy drift guard
# finds jobcore (a sibling ``jobcore/src/jobcore``, which CI clones for every
# shard), and it fails rather than skips where jobcore is missing.

JOBCORE_MARKER = ".jobhunt-root"
JOBCORE_MAX_WALK_UP = 6


def _jobcore_marker_walk(start: Path):
    """jobcore's marker branch, restated: the config it would find, or None."""
    for parent in [start, *start.parents][: JOBCORE_MAX_WALK_UP + 1]:
        if (parent / JOBCORE_MARKER).is_file():
            return parent / "config" / "jobhunt.json"
    return None


def _jobhunt_tree(tmp_path: Path, depth: int = 3) -> tuple[Path, Path]:
    root = tmp_path / "jobhunt"
    (root / "config").mkdir(parents=True)
    (root / "config" / "jobhunt.json").write_text("{}", encoding="utf-8")
    (root / JOBCORE_MARKER).write_text("", encoding="utf-8")
    deep = root.joinpath(*(f"d{i}" for i in range(depth)))
    deep.mkdir(parents=True, exist_ok=True)
    return root.resolve(), deep


def test_the_marker_and_the_bound_are_jobcores():
    assert apply_answers.ROOT_MARKER == JOBCORE_MARKER
    assert apply_answers.MAX_WALK_UP == JOBCORE_MAX_WALK_UP


@pytest.mark.parametrize("depth", [0, 3, JOBCORE_MAX_WALK_UP, JOBCORE_MAX_WALK_UP + 1])
def test_the_bank_and_jobcore_find_one_root_or_neither(tmp_path, depth):
    root, deep = _jobhunt_tree(tmp_path, depth)
    config = _jobcore_marker_walk(deep)
    bank = apply_answers.locate_bank(deep, env={}).path
    if config is None:
        assert bank is None, "the bank found a root jobcore's walk would not"
    else:
        assert bank is not None
        assert bank.resolve().parents[3] == config.resolve().parent.parent == root


def test_jobhunt_home_keeps_jobcores_meaning_and_never_moves_the_bank(tmp_path):
    """Set as jobcore means it -- the config's directory -- it changes nothing."""
    root, deep = _jobhunt_tree(tmp_path)
    for home in (root / "config", root, tmp_path / "anywhere"):
        found = apply_answers.locate_bank(deep, env={apply_answers.JOBCORE_ENV_HOME: str(home)})
        assert found.path.resolve() == root.joinpath(*apply_answers.BANK_PARTS), home
        assert found.how.startswith("walk-up"), found.how
    bare = tmp_path / "bare"
    bare.mkdir()
    lone = apply_answers.locate_bank(bare, env={apply_answers.JOBCORE_ENV_HOME: str(root)})
    assert lone.path is None, "JOBHUNT_HOME was read as the root"


def _jobcore_src():
    """jobcore's ``src`` directory, found EXACTLY as the vendored-copy drift
    guard finds it -- its own ``canonical_dir``, imported rather than
    rewritten: a walk up from the test file to a sibling
    ``jobcore/src/jobcore``. That is the layout this box carries and the one
    CI's workflow clones ("Check out jobcore as a sibling, so the drift guards
    run"). A first version walked to the ``.jobhunt-root`` marker instead,
    which CI does not have, and lane CI run 45662953454 counted the skip it
    made as one nobody had declared."""
    from tests.test_vendored_buildinfo import canonical_dir

    canonical = canonical_dir()
    return None if canonical is None else canonical.parent


def test_jobcores_own_locate_finds_the_bank_s_root(tmp_path, monkeypatch):
    src = _jobcore_src()
    assert src is not None and (src / "jobcore" / "config.py").is_file(), (
        "jobcore's source is not a sibling of this checkout (../jobcore/src/jobcore), "
        "the layout this box and CI's sibling clone both carry: the parity against "
        "jobcore's own locate cannot run, and it is not allowed to skip"
    )
    monkeypatch.syspath_prepend(str(src))
    import importlib
    config = importlib.import_module("jobcore.config")
    root, deep = _jobhunt_tree(tmp_path)
    found = config.locate(start=deep, env={})
    assert found.path is not None and found.path.parent.parent == root
    bank = apply_answers.locate_bank(deep, env={}).path
    assert bank.resolve().parents[3] == found.path.parent.parent
    as_home = config.locate(start=deep, env={config.ENV_HOME: str(root / "config")})
    assert as_home.reason == config.ENV_HOME, "jobcore no longer reads JOBHUNT_HOME as the config dir"
    same = apply_answers.locate_bank(deep, env={config.ENV_HOME: str(root / "config")})
    assert same.path == bank


def test_lookup_reads_the_bank_the_order_finds(tmp_path, monkeypatch):
    target = tmp_path / "bank.json"
    target.write_text(bank(entry("w", "numeric", QUESTION, confirmed="3")), encoding="utf-8")
    monkeypatch.setenv(apply_answers.ENV_BANK, str(target))
    assert lookup(QUESTION, today=TODAY)["answer"] == "3"
    monkeypatch.setenv(apply_answers.ENV_BANK, str(tmp_path / "missing.json"))
    assert lookup(QUESTION, today=TODAY) is None


def test_no_absolute_path_is_written_into_the_module():
    """The location is RESOLVED; a literal drive-rooted path is a leak and a lie."""
    source = (REPO / "linkedin_server" / "apply_answers.py").read_text(encoding="ascii")
    drive_rooted = __import__("re").compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/home/|/Users/")
    assert not drive_rooted.search(source), drive_rooted.search(source)
    assert drive_rooted.search("C:" + "\\" + "x") and not drive_rooted.search("https://x")


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
    for key, record in CACHE.items():
        options = apply_answers._cache_options(key, record["questionName"])
        assert apply_answers.naukri_cache_key(record["questionName"], options) == key


def test_a_naukri_import_is_drafts_only_and_names_an_answer_no_option_matches():
    entries = apply_answers.import_naukri_cache(CACHE)
    assert len(entries) == 3
    assert all(e["confirmed"]["value"] == "" and e["family"] == apply_answers.IMPORTED_FAMILY
               for e in entries)
    by_question = {e["platforms"]["naukri"]["questions"][0]: e for e in entries}
    relocate = by_question["Willing to relocate?"]
    assert relocate["input_kind"] == "radio"
    assert relocate["platforms"]["naukri"]["options"] == ["Yes", "No"]
    assert relocate["platforms"]["naukri"]["native_type"] == "Radio Button"
    assert relocate["draft"]["value"] == "Sometimes"
    assert "NOT one of the options drawn" in relocate["notes"]
    tools = by_question["Tools used?"]
    assert tools["input_kind"] == "multi_select" and tools["draft"]["value"] == "Docker | Redis"
    assert tools["notes"] == ""
    imported = parse_bank(bank(*entries), today=TODAY)
    assert imported.answers == () and imported.rows_unconfirmed == 3


def test_the_cache_report_names_what_could_fire_unseen():
    result = parsed(
        entry("notice", "text", "Notice period in days?", confirmed="45", cls="availability",
              platform="naukri", expires_at="2027-01-01"),
        entry("tools", "multi_select", "Tools used?", confirmed="Docker | Redis",
              options=("Docker", "Kafka", "Redis"), platform="naukri"),
    )
    report = {r["question"]: r["status"]
              for r in apply_answers.naukri_cache_report(CACHE, result, today=TODAY)}
    assert report == {
        "Notice period in days?": "confirmed_differs",
        "Willing to relocate?": "unconfirmed",
        "Tools used?": "confirmed_same",
    }
    attested = parsed(entry("r", "radio", "Willing to relocate?", confirmed="No",
                            cls="work_authorisation", options=("Yes", "No"), platform="naukri"))
    statuses = {r["question"]: r["status"]
                for r in apply_answers.naukri_cache_report(CACHE, attested, today=TODAY)}
    assert statuses["Willing to relocate?"] == "never_auto"


# ---------------------------------------------------------------------------
# 8. Read fresh, and counts only
# ---------------------------------------------------------------------------


def test_the_bank_is_read_fresh_every_call(tmp_path):
    target = tmp_path / apply_answers.BANK_FILENAME
    target.write_text(bank(entry("w", "numeric", QUESTION)), encoding="utf-8")
    assert load_bank(target).answer_for(QUESTION, "numeric") is None
    target.write_text(bank(entry("w", "numeric", QUESTION, confirmed="3")), encoding="utf-8")
    answer = load_bank(target).answer_for(QUESTION, "numeric")
    assert answer is not None and answer.value == "3"


def test_an_entry_with_no_wording_is_guidance_and_answers_nothing():
    result = parsed(entry("class-only", "numeric", None, draft="4"))
    assert result.rows_template == 1 and result.answers == ()


def test_status_carries_counts_only():
    status = parsed(entry("w", "numeric", QUESTION, confirmed="3")).status(TODAY)
    assert all(isinstance(value, (int, bool)) for value in status.values()), status
    assert "Widgets" not in repr(status)
