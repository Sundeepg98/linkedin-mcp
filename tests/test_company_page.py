"""The organisation-Page shaper, and the slug it must never let out.

``linkedin_server/company_page.py`` is the name-free shaper the ``/company/``
admission shipped WITH, in one commit, on the condition ``search_results.py``
states about itself. This file is what makes that condition checkable.

WHAT IT ASSERTS, in the order the module's own claims are made:

1. **THE ALPHABET IS A CONTRACT.** A reading is a POSITION in ``TAB_KINDS``,
   so reordering that tuple silently renames every reading ever taken.
2. **THE CLASSIFIER REFUSES WHAT IT CANNOT JUDGE.** A traversal is counted and
   dropped, never normalised; a member marker wins over a company marker; the
   comparison is case sensitive and the miss lands on the safe side.
3. **NOTHING A DOCUMENT HOLDS IS A RETURN VALUE.** Driven with adversarial
   inputs -- a slug that is a person's name, a slug carrying a forbidden
   substring, a hundred-character slug -- and the outputs are walked for any
   surviving substring of the input.
4. **THE REFUSALS REPORT A SHAPE.** ``company_identifier`` is handed the single
   most probable wrong value (a slug) and its refusal must not contain it.
5. **THE BUILDER IS NUMERIC-ONLY**, which is the asymmetry the admission is
   argued on: the boundary admits what LinkedIn serves, the package assembles
   only what names nobody.
6. **THE SHAPER AND THE BOUNDARY AGREE**, address for address, so the entry
   cannot open something the shaper would refuse or the reverse. That is the
   divergence the groups coupling test caught on its first run.

Everything here is pure. No browser, no page, no fixture, no network.
"""
from __future__ import annotations

import inspect

import pytest

from linkedin_server import company_page, readonly

BASE = "https://www.linkedin.com"

#: A slug that IS a person's name. **THIS IS THE WHOLE POINT OF THE MODULE**
#: and it is not invented for the test: ``hollingsworth-global`` is a real
#: segment in this repository's committed corpus, found by
#: ``scripts/_probe_company_path_segments.py``, and the spelling below is the
#: same shape with a token the identity guard already sanctions.
EPONYMOUS_SLUG = "a-company-and-partners"

#: A numeric id, in the spelling ``tests/fixtures/notifications.html`` carries.
IDENTIFIER = "5417062"


# ---------------------------------------------------------------------------
# 1. The alphabet is a contract
# ---------------------------------------------------------------------------


def test_the_alphabet_is_pinned_in_order():
    """Reordering renames every reading ever taken, so the order is pinned."""
    assert company_page.TAB_KINDS == (
        "people_tab",
        "home_tab",
        "about_tab",
        "posts_tab",
        "jobs_tab",
        "life_tab",
        "products_tab",
        "services_tab",
        "insights_tab",
        "events_tab",
        "videos_tab",
        "admin_surface",
        "page_creation",
        "traversal_refused",
        "unclassified",
        "off_company",
        "no_href",
    )


def test_the_hazard_class_is_first():
    """``people_tab`` is a MEMBER ROSTER and is first for the reason
    ``person_result`` is first in ``search_results.RESULT_KINDS``: it is the
    class anything misclassified into or out of is the defect."""
    assert company_page.TAB_KINDS[0] == "people_tab"


def test_every_table_token_is_in_the_alphabet():
    """A table row naming a token the alphabet does not hold would raise a
    KeyError inside ``tally`` on the first page that drew it."""
    for token, _segment in company_page.TAB_TABLE:
        assert token in company_page.TAB_KINDS


def test_term_for_refuses_out_of_range_rather_than_clamping():
    """A clamp silently renames one class to another."""
    assert company_page.term_for(0) == "people_tab"
    with pytest.raises(IndexError):
        company_page.term_for(len(company_page.TAB_KINDS))
    with pytest.raises(IndexError):
        company_page.term_for(-1)
    with pytest.raises(TypeError):
        company_page.term_for(True)


# ---------------------------------------------------------------------------
# 2. The classifier refuses what it cannot judge
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "href,expected",
    [
        (f"{BASE}/company/{EPONYMOUS_SLUG}/", "home_tab"),
        (f"{BASE}/company/{IDENTIFIER}/", "home_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}", "home_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/about/", "about_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/people/", "people_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/jobs/", "jobs_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/life/", "life_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/posts/", "posts_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/products/", "products_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/services/", "services_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/insights/", "insights_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/events/", "events_tab"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/videos/", "videos_tab"),
        # The write half of the root, which is not a tab.
        (f"{BASE}/company/{EPONYMOUS_SLUG}/admin/", "admin_surface"),
        (f"{BASE}/company/{EPONYMOUS_SLUG}/admin/dashboard/", "admin_surface"),
        (f"{BASE}/company/setup/new/", "page_creation"),
        # The product root, which is not a Page.
        (f"{BASE}/company/", "unclassified"),
        # Somewhere else entirely.
        (f"{BASE}/school/example-university/", "off_company"),
        (f"{BASE}/in/someone-else/", "off_company"),
        (None, "no_href"),
        ("", "no_href"),
        ("   ", "no_href"),
    ],
)
def test_the_classifier_puts_each_route_in_its_class(href, expected):
    assert company_page.classify_route(href) == expected


@pytest.mark.parametrize(
    "href",
    [
        f"{BASE}/company/{EPONYMOUS_SLUG}/../../mypreferences/d/close-account",
        f"{BASE}/company/{EPONYMOUS_SLUG}/../../in/someone-else/",
        f"{BASE}/company/../mypreferences/d/",
        f"{BASE}/company/{EPONYMOUS_SLUG}/..",
        f"{BASE}/company/./",
        "/company/./people/",
    ],
)
def test_a_traversal_is_refused_and_never_resolved(href):
    """**SHOWN FAILING WOULD BE THE DEFECT, SO THIS IS SHOWN REFUSING.**

    The first address's leading three segments are an organisation page and
    its browser-normalised form ENDS THE ACCOUNT; the second normalises onto a
    member profile. No forbidden substring names either. A classifier that
    read only the leading segments would report both as an organisation.

    The refusal is a COUNT, not a resolution: normalising here would mean this
    module deciding what a traversal means, which is the browser's job.
    """
    assert company_page.classify_route(href) == company_page.TRAVERSAL_REFUSED
    assert company_page.identifier_kind(href) == "none"
    assert company_page.slug_is_addressable(href) is False


def test_a_member_marker_wins_over_a_company_marker():
    """An address carrying BOTH is refused as foreign rather than counted as
    an organisation. The conservative direction is the one where a route
    pointing at a person cannot be counted."""
    both = f"{BASE}/company/{EPONYMOUS_SLUG}/in/someone-else/"
    assert company_page.classify_route(both) == "off_company"


def test_matching_is_case_sensitive_and_the_miss_is_safe():
    """``/COMPANY/<x>/`` is not recognised as an organisation at all, rather
    than admitted as one. A case-insensitive comparison is the dangerous
    repair: it widens what matches a table whose job is to be narrow."""
    assert company_page.classify_route(f"{BASE}/COMPANY/{IDENTIFIER}/") == (
        "off_company"
    )


def test_the_query_is_dropped_before_any_segment_is_read():
    """A query on this root is where a filter naming a person arrives, so the
    rule ``groups.py`` states governs: a part never read cannot carry
    anything. The route still classifies; the query is counted separately."""
    with_query = f"{BASE}/company/{EPONYMOUS_SLUG}/?keywords=somebody"
    assert company_page.classify_route(with_query) == "home_tab"
    assert company_page.tally([with_query])["queries"] == 1
    assert company_page.tally([f"{BASE}/company/{IDENTIFIER}/"])["queries"] == 0


# ---------------------------------------------------------------------------
# 3. Nothing a document holds is a return value
# ---------------------------------------------------------------------------


def _leaves(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _leaves(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            yield from _leaves(item)
    else:
        yield value


ADVERSARIAL = [
    f"{BASE}/company/{EPONYMOUS_SLUG}/",
    f"{BASE}/company/{EPONYMOUS_SLUG}/people/",
    f"{BASE}/company/{EPONYMOUS_SLUG}/?keywords={EPONYMOUS_SLUG}",
    f"{BASE}/company/{EPONYMOUS_SLUG}/../../in/someone-else/",
    f"{BASE}/company/{'a' * 100}/",
    f"{BASE}/company/{'a' * 101}/",
    f"{BASE}/company/connect-solutions/",
    f"{BASE}/company/{IDENTIFIER}/",
    f"{BASE}/company/setup/new/",
    None,
    "",
]


def test_no_segment_of_any_input_survives_into_the_tally():
    """THE PROPERTY THE WHOLE MODULE EXISTS FOR, driven over adversarial
    inputs rather than clean ones -- a shaper shown only the names it already
    handles certifies nothing."""
    out = company_page.tally(ADVERSARIAL)
    published = [str(leaf) for leaf in _leaves(out)]
    for needle in (EPONYMOUS_SLUG, "connect-solutions", IDENTIFIER,
                   "someone-else", "a" * 100, "linkedin.com", "/company/"):
        assert not any(needle in text for text in published), (
            f"{needle!r} survived into the tally"
        )


def test_the_tally_is_integers_and_a_count_list():
    out = company_page.tally(ADVERSARIAL)
    assert set(out) == {
        "hrefs", "counts", "distinct", "numeric", "slug", "page_roots",
        "queries",
    }
    assert out["hrefs"] == len(ADVERSARIAL)
    assert len(out["counts"]) == len(company_page.TAB_KINDS)
    assert all(isinstance(value, int) for value in out["counts"])
    for key in ("distinct", "numeric", "slug", "page_roots", "queries"):
        assert isinstance(out[key], int)


@pytest.mark.parametrize(
    "href",
    [
        "https://[",
        "http://[::1",
        "//[bad",
        "https://[/company/1234/",
    ],
)
def test_a_malformed_href_is_counted_rather_than_raised(href):
    """SHOWN FAILING AT HEAD, before ``_parts`` existed.

    ``urlsplit("https://[")`` raises ``ValueError`` -- Invalid IPv6 URL -- and
    MEASURED: ``tally`` propagated it straight out of ``linkedin_job_detail``.
    **One malformed href anywhere on a posting would have failed a read that
    had already succeeded**, turning a route this module cannot classify into
    a tool that returns nothing.

    A route that cannot be parsed cannot be judged, so it is COUNTED as
    unjudgeable -- a visible integer -- rather than guessed at or thrown.
    """
    assert company_page.classify_route(href) == company_page.UNCLASSIFIED
    assert company_page.identifier_kind(href) == "none"
    assert company_page.slug_is_addressable(href) is False
    out = company_page.tally([href, f"{BASE}/company/{IDENTIFIER}/"])
    assert out["hrefs"] == 2
    # The good row still lands, so this is not "everything became unjudgeable".
    assert out["counts"][company_page.TAB_KINDS.index("home_tab")] == 1
    assert out["page_roots"] == 1


@pytest.mark.parametrize(
    "href",
    [
        "https://evil.example/company/1234/",
        "https://linkedin.com.evil.example/company/1234/",
        "https://www.linkedin.com.evil.example/company/1234/",
        "http://www.linkedin.com:8080/company/1234/",
    ],
)
def test_a_foreign_host_is_not_an_organisation_route(href):
    """SHOWN FAILING AT HEAD. ``_HOST`` was defined and never read, so
    ``https://evil.example/company/1234/`` classified as ``home_tab`` and was
    COUNTED as a LinkedIn organisation.

    A count is a claim about what a page links to, and one that cannot tell
    LinkedIn's own routes from a foreign host's is making a different claim
    than its name makes. The port form is here because a netloc comparison
    that ignored it would be a different bug with the same shape.
    """
    assert company_page.classify_route(href) == company_page.UNCLASSIFIED
    assert company_page.slug_is_addressable(href) is False
    # And the shipped door agrees, which is the point of comparing at all.
    assert readonly.is_read_url(href) is False


def test_a_relative_href_still_classifies():
    """THE CONTROL for the host check, and it is not hypothetical: LinkedIn
    writes ``/company/<id>`` bare in the notification rail, measured in
    ``tests/fixtures/notifications.html``. A host check that refused an empty
    netloc would stop counting the one spelling this corpus actually holds."""
    assert company_page.classify_route(f"/company/{IDENTIFIER}") == "home_tab"
    assert company_page.classify_route("/company/x/people/") == "people_tab"
    assert company_page.identifier_kind(f"/company/{IDENTIFIER}") == "numeric"
    assert company_page.slug_is_addressable(f"/company/{IDENTIFIER}/") is True


def test_the_page_creation_flow_is_not_counted_as_an_organisation():
    """``/company/setup/new/`` puts the literal ``setup`` in segment 1, which a
    naive count would read as a slug and file as an organisation. It names
    none -- it is the flow that CREATES one -- so it is counted in its own
    class and excluded from `distinct`, `slug` and `page_roots`.

    The control beside it is a real Page in the same tally: without one, an
    implementation that excluded EVERYTHING would pass this.
    """
    out = company_page.tally([
        f"{BASE}/company/setup/new/",
        f"{BASE}/company/{IDENTIFIER}/",
    ])
    creation = out["counts"][company_page.TAB_KINDS.index("page_creation")]
    assert creation == 1
    assert out["distinct"] == 1
    assert out["slug"] == 0
    assert out["numeric"] == 1
    assert out["page_roots"] == 1


def test_distinct_counts_organisations_without_naming_one():
    """The set is built inside the function and its LENGTH is what leaves."""
    out = company_page.tally([
        f"{BASE}/company/{EPONYMOUS_SLUG}/",
        f"{BASE}/company/{EPONYMOUS_SLUG}/people/",
        f"{BASE}/company/{IDENTIFIER}/",
    ])
    assert out["distinct"] == 2
    assert out["slug"] == 2
    assert out["numeric"] == 1


def test_tally_takes_no_name_and_no_verdict_function_takes_a_page():
    """THE SIGNATURE IS HALF THE SAFETY PROPERTY, asserted the way
    ``groups.py`` and ``search_results.py`` assert it: the counting function
    is never handed a name, and nothing here touches a page at all."""
    assert list(
        inspect.signature(company_page.tally).parameters
    ) == ["hrefs"]
    for name, function in vars(company_page).items():
        if not inspect.isfunction(function):
            continue
        assert not inspect.iscoroutinefunction(function), (
            f"{name} is async, so it can touch a page. This module opens "
            "nothing and has no page function -- that is a claim in its "
            "docstring and this is where it is checked."
        )


def test_the_module_fires_nothing():
    """``J 86`` and ``N 47`` are the two writes on this root and neither is
    touched. No function here takes a confirm token, and a shaper that could
    fire would have imported their ruling by accident."""
    for name, function in vars(company_page).items():
        if not inspect.isfunction(function):
            continue
        parameters = set(inspect.signature(function).parameters)
        assert not (parameters & {"confirm_token", "token", "grant"}), name


# ---------------------------------------------------------------------------
# 4. The refusals report a shape
# ---------------------------------------------------------------------------


def test_a_slug_is_refused_as_an_identifier_and_never_echoed():
    """THE SINGLE MOST PROBABLE WRONG VALUE IS A SLUG, because that is what a
    posting hands you -- so the rule-following refusal publishes a third
    party's name on the commonest mistake. ``jobfilter.py`` ruled this and the
    ruling is imported with its function."""
    out = company_page.company_identifier(EPONYMOUS_SLUG)
    assert out["identified"] is False
    assert out["refused"] == "identifier_is_not_numeric"
    assert EPONYMOUS_SLUG not in repr(out)
    # A refusal that names only the absence is half a measurement.
    assert "characters" in out["saw"]
    assert "letters" in out["saw"]


def test_the_ten_ascii_digits_and_not_str_isdigit():
    """``str.isdigit()`` is True of several other scripts' digits. The module
    names the ten explicitly, and this is the control that shows the
    difference is real rather than theoretical."""
    arabic_indic = "".join(chr(0x0661 + n) for n in range(4))
    assert arabic_indic.isdigit() is True
    out = company_page.company_identifier(arabic_indic)
    assert out["identified"] is False
    assert out["refused"] == "identifier_is_not_numeric"


def test_an_identifier_is_bounded_and_the_bound_is_groups_number():
    assert company_page.MAX_IDENTIFIER_DIGITS == 20
    assert company_page.company_identifier("1" * 20)["identified"] is True
    too_long = company_page.company_identifier("1" * 21)
    assert too_long["identified"] is False
    assert too_long["refused"] == "identifier_too_long"


def test_an_empty_identifier_refuses_rather_than_building_a_bare_root():
    for value in (None, "", "   "):
        out = company_page.company_identifier(value)
        assert out["identified"] is False
        assert out["refused"] == "no_identifier"


def test_the_published_href_is_a_literal_and_not_a_shape_of_the_input():
    out = company_page.company_identifier(IDENTIFIER)
    assert out["href_shape"] == company_page.PUBLISHED_HREF
    assert out["href_shape"] == "/company/<company>/"


# ---------------------------------------------------------------------------
# 5. The builder is numeric-only
# ---------------------------------------------------------------------------


def test_the_builder_assembles_the_numeric_form_only():
    """THE ASYMMETRY THE ADMISSION IS ARGUED ON. The boundary admits the slug
    spelling because LinkedIn emits it and a landing page the boundary refuses
    puts a third party's slug in a traceback. It does not follow that this
    package should ASSEMBLE one."""
    built = company_page.company_page_url(IDENTIFIER)
    assert built["built"] is True
    assert built["url"] == f"{BASE}/company/{IDENTIFIER}/"

    refused = company_page.company_page_url(EPONYMOUS_SLUG)
    assert refused["built"] is False
    assert "url" not in refused
    assert EPONYMOUS_SLUG not in repr(refused)


def test_what_the_builder_builds_is_admitted_by_the_shipped_door():
    """The builder does not consult the allowlist -- two copies of one
    decision drift -- so this is where the two are compared."""
    built = company_page.company_page_url(IDENTIFIER)
    assert readonly.is_read_url(built["url"]) is True


# ---------------------------------------------------------------------------
# 6. The shaper and the boundary agree
# ---------------------------------------------------------------------------


AGREEMENT_CORPUS = [
    f"{BASE}/company/{EPONYMOUS_SLUG}/",
    f"{BASE}/company/{EPONYMOUS_SLUG}",
    f"{BASE}/company/{IDENTIFIER}/",
    f"{BASE}/company/{'a' * 100}/",
    f"{BASE}/company/{'a' * 101}/",
    f"{BASE}/company/{EPONYMOUS_SLUG}/people/",
    f"{BASE}/company/{EPONYMOUS_SLUG}/about/",
    f"{BASE}/company/{EPONYMOUS_SLUG}/admin/",
    f"{BASE}/company/setup/new/",
    f"{BASE}/company/{EPONYMOUS_SLUG}/?foo=1",
    f"{BASE}/company/a.company/",
    f"{BASE}/company/a..company/",
    f"{BASE}/company/",
    f"{BASE}/company/{EPONYMOUS_SLUG}/../../in/someone-else/",
]


@pytest.mark.parametrize("url", AGREEMENT_CORPUS)
def test_the_shaper_and_the_boundary_agree_address_for_address(url):
    """**THE COUPLING CHECK, AND IT IS NOT DECORATION.** The groups wave's
    equivalent caught a real divergence on its first run: an allowlist
    unbounded where its shaper capped at twenty, so the boundary opened an
    address the shaper then refused.

    ONE DOCUMENTED ASYMMETRY, and it is in the safe direction: an address
    carrying a FORBIDDEN SUBSTRING is refused by gate one, before the
    allowlist is consulted, while ``slug_is_addressable`` only knows about the
    character class. So the boundary can be STRICTER than the shaper and never
    looser. That case is asserted separately below rather than smuggled in
    here, because a parametrised test that quietly tolerates a mismatch is how
    a coupling check stops coupling anything.
    """
    assert company_page.slug_is_addressable(url) == readonly.is_read_url(url)


def test_the_boundary_is_stricter_than_the_shaper_on_a_forbidden_substring():
    """The documented asymmetry, in the safe direction, shown rather than
    promised: a slug containing ``connect`` refuses at gate one."""
    url = f"{BASE}/company/connect-solutions/"
    assert company_page.slug_is_addressable(url) is True
    assert readonly.is_read_url(url) is False


def test_the_shaper_caps_a_slug_where_the_pattern_does():
    assert company_page.MAX_SLUG_CHARS == 100
    assert company_page.slug_is_addressable(f"{BASE}/company/{'a' * 100}/")
    assert not company_page.slug_is_addressable(f"{BASE}/company/{'a' * 101}/")
