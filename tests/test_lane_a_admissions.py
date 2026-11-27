"""Lane A admissions: read pages of his own account past a substring written to
stop an ACT, and pages refused by allowlist silence alone.

Ruling READ-PAST-AN-ACT-SUBSTRING (orchestrator, 2026-09-28), registered in
``_audit/2026-09-28-rulings-build-classes.md`` section 5. Record:
``_audit/2026-09-28-lane-a-admissions.md``.

THE RULING'S CONDITIONS, EACH A TEST BELOW, FOR EVERY ADMISSION IN ONE TABLE:

1. ONE exact, anchored pattern per address -- exactly one allowlist line
   matches the address, and it carries no wildcard.
2. A control is shown failing: the substring (or the allowlist) still refuses
   every other spelling and every sibling path. Each sibling names the gate
   that must refuse it, and the refusal's own sentence is checked.
3. Where a forbidden substring is crossed, the exemption excuses EXACTLY the
   substrings the address trips, for exactly that anchored address; the
   forbidden tuple is unchanged. EITHER GATE ALONE ADMITS NOTHING: drop the
   exemption and the substring refuses (saying a pattern would admit it); drop
   the line and the allowlist refuses.
4. The blast radius, measured the way ``scripts/blast_radius.py`` measures --
   ``is_read_url`` before and after on concrete urls, never a grep: each
   admission newly admits exactly its own spellings and refuses nothing new.

Nothing here opens a page. Every variable segment is a placeholder
(``placeholder-org``, ``someone-else``, invented digits).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple, Optional

import pytest

from linkedin_server import readonly
from linkedin_server.errors import WriteAttemptError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402

B = "https://www.linkedin.com"

#: The allowlist's own refusal sentence and the forbidden branch's, as the
#: shipped gate writes them (tests/test_refusal_names_both_gates.py pins both).
ALLOWLIST_SENTENCE = "not on the read-only allowlist"
PATTERN_WOULD_ADMIT = "A READ PATTERN DOES ADMIT THIS ADDRESS"

#: The forbidden tuple's size when lane A landed. An admission here never
#: shortens it; the floor in tests/test_readonly_boundary_invariant.py is the
#: standing guard, this is the lane's own statement.
FORBIDDEN_TUPLE_SIZE = 33


class Sibling(NamedTuple):
    url: str
    #: The forbidden substring that must refuse it, or None when the
    #: allowlist alone must refuse it.
    gate: Optional[str]
    why: str


class Admission(NamedTuple):
    key: str
    rows: tuple
    address: str
    #: The forbidden substrings the address trips and the exemption excuses;
    #: empty for an allowlist-silence admission.
    excused: frozenset
    siblings: tuple
    #: Spellings the pair must newly admit besides ``address`` and, when
    #: ``twin``, its other slash form.
    spellings: tuple = ()
    #: False for an address that ends in a query value: it has no slash twin.
    twin: bool = True
    #: True for the search-shaped lines that take a query, as the classic job
    #: search line does; the shape check then permits exactly that one group,
    #: ``(\?[^#]*)?``, and nothing else.
    query: bool = False


def _slash_twin(url: str) -> str:
    return url[:-1] if url.endswith("/") else url + "/"


def _own(adm) -> set:
    own = {adm.address, *adm.spellings}
    if adm.twin:
        own.add(_slash_twin(adm.address))
    return own


QUERY_GROUP = r"(\?[^#]*)?"


ADMISSIONS = (
    Admission(
        key="invitations-received",
        rows=("N 13", "N 14", "N 19"),
        address=f"{B}/mynetwork/invitation-manager/",
        excused=frozenset({"invitation"}),
        siblings=(
            Sibling(f"{B}/mynetwork/invitation-manager/?filterCriteria=x",
                    "invitation", "a QUERY -- the anchor is load-bearing"),
            Sibling(f"{B}/mynetwork/invitation-manager/received/",
                    "invitation", "an unrecorded leaf: its own line if served"),
            Sibling(f"{B}/mynetwork/invitation-manager/accept/",
                    "invitation", "a SUB-PATH naming an act"),
            Sibling(f"{B}/mynetwork/invitation-manager/../../in/someone-else/",
                    "invitation", "a TRAVERSAL onto a third party"),
            Sibling(f"{B}/mynetwork/invite-connect/invitations/",
                    "/invite", "the other invitation surface"),
            Sibling(f"{B}/groups/12345678/invite/", "/invite",
                    "inviting somebody to a group"),
            # The hub, /mynetwork/, stood here until 2026-11-25, "refused on
            # its badge cost (R1) and by nothing else"; lane admit26 admitted
            # it (tests/test_admit26_admissions.py). Its discovery lists did
            # not travel with it; they stood here until 2026-11-27, when lane
            # net7 admitted them by their own anchored line on
            # GROW-SUGGESTIONS-BY-ADMISSION-NOT-SCROLL
            # (tests/test_net7_admissions.py). A sub-path of them stands in.
            Sibling(f"{B}/mynetwork/discovery-see-all/people/", None,
                    "a sub-path of the hub's full suggestion lists"),
        ),
    ),
    Admission(
        key="invitations-sent",
        rows=("N 9", "N 11"),
        address=f"{B}/mynetwork/invitation-manager/sent/",
        excused=frozenset({"invitation"}),
        siblings=(
            Sibling(f"{B}/mynetwork/invitation-manager/sent/?invitationType=x",
                    "invitation", "a QUERY -- the Page tab's spelling is "
                    "unrecorded"),
            Sibling(f"{B}/mynetwork/invitation-manager/sent/withdraw/",
                    "invitation", "a SUB-PATH naming the write (N 10)"),
            Sibling(f"{B}/mynetwork/invitation-manager/sent/x/../../",
                    "invitation", "a TRAVERSAL"),
        ),
    ),
    Admission(
        key="people-followed",
        rows=("N 38",),
        address=f"{B}/mynetwork/network-manager/people-follow/following/",
        excused=frozenset({"/follow"}),
        siblings=(
            Sibling(f"{B}/mynetwork/network-manager/people-follow/following/?x=1",
                    "/follow", "a QUERY"),
            Sibling(f"{B}/mynetwork/network-manager/people-follow/following/"
                    "unfollow/", "/follow", "a SUB-PATH naming the write"),
            Sibling(f"{B}/in/me/follow/", "/follow", "following a member"),
            Sibling(f"{B}/company/placeholder-org/follow/", "/follow",
                    "following a Page"),
            Sibling(f"{B}/company/placeholder-org/unfollow/", "/unfollow",
                    "unfollowing a Page"),
            Sibling(f"{B}/feed/follows/", "/follow",
                    "a read the exemption does not reach"),
            Sibling(f"{B}/company/placeholder-org/admin/following/", "/follow",
                    "his Page's following list (N A3), not admitted here"),
            Sibling(f"{B}/mynetwork/network-manager/people-follow/", None,
                    "the family root, refused by the allowlist alone"),
        ),
    ),
    Admission(
        key="job-application-settings",
        rows=("P M2", "P M4", "P M5", "P M6", "P M12", "J 71", "J 72", "J 73"),
        address=f"{B}/jobs/application-settings/",
        excused=frozenset({"/jobs/application", "settings"}),
        siblings=(
            Sibling(f"{B}/jobs/application-settings/?resume=1",
                    "/jobs/application", "a QUERY"),
            Sibling(f"{B}/jobs/application-settings/resume/delete",
                    "/jobs/application", "a SUB-PATH naming a write"),
            Sibling(f"{B}/jobs/application/1234567890/", "/jobs/application",
                    "an application itself"),
            Sibling(f"{B}/jobs/applications/", "/jobs/application",
                    "a sibling the exemption does not reach"),
            Sibling(f"{B}/jobs/easy-apply/", "easy-apply", "applying"),
            Sibling(f"{B}/mypreferences/d/job-application-accounts",
                    "job-application", "the stored applicant accounts, NOT "
                    "admitted (a credential-adjacent surface; the record, 2.6)"),
            Sibling(f"{B}/mypreferences/d/settings/language", "/settings/",
                    "a settings page the dark-mode entry declined by name"),
            Sibling(f"{B}/public-profile/settings", "settings",
                    "the second spelling the 2026-09-03 block closed"),
        ),
    ),
    Admission(
        key="unfollowed",
        rows=("N 39",),
        address=f"{B}/mypreferences/d/unfollowed",
        excused=frozenset({"/unfollow"}),
        siblings=(
            Sibling(f"{B}/mypreferences/d/unfollowed?member=1", "/unfollow",
                    "a QUERY -- where a person would arrive"),
            Sibling(f"{B}/mypreferences/d/unfollowed/refollow", "/unfollow",
                    "a SUB-PATH naming the write"),
            Sibling(f"{B}/company/placeholder-org/unfollow/", "/unfollow",
                    "unfollowing a Page"),
            # categories/privacy stood here until 2026-11-25, when lane admit26
            # admitted it by name; another category page stands in.
            Sibling(f"{B}/mypreferences/d/categories/notifications",
                    "/mypreferences/d/categories/", "a category page"),
            Sibling(f"{B}/mypreferences/d/settings/show-profile-photos",
                    "/settings/", "a sibling settings page"),
            Sibling(f"{B}/mypreferences/d/demographic-info-copy", None,
                    "a settings page recording a sensitive attribute -- the "
                    "allowlist alone refuses it, and nothing here reaches it"),
        ),
    ),
    Admission(
        key="ads-settings",
        rows=("P P15",),
        address=f"{B}/mypreferences/d/categories/ads",
        excused=frozenset({"/mypreferences/d/categories/"}),
        siblings=(
            Sibling(f"{B}/mypreferences/d/categories/",
                    "/mypreferences/d/categories/", "the category root"),
            Sibling(f"{B}/mypreferences/d/categories/account",
                    "/mypreferences/d/categories/", "the account category"),
            Sibling(f"{B}/mypreferences/d/categories/sign-in-and-security",
                    "/mypreferences/d/categories/",
                    "the security category -- a surface the ruling excludes"),
            # The privacy category stood here until 2026-11-25, when lane
            # admit26 admitted it by name in its own commit.
            Sibling(f"{B}/mypreferences/d/categories/notifications",
                    "/mypreferences/d/categories/", "the notifications category"),
            Sibling(f"{B}/mypreferences/d/categories/ads?x=1",
                    "/mypreferences/d/categories/", "a QUERY"),
            Sibling(f"{B}/mypreferences/d/categories/ads/off",
                    "/mypreferences/d/categories/", "a SUB-PATH"),
            Sibling(f"{B}/mypreferences/d/categories/adsx",
                    "/mypreferences/d/categories/", "a longer leaf"),
        ),
    ),
    # ------------------------------------------------------------------
    # ALLOWLIST SILENCE (the ruling's second clause): no substring crossed,
    # so `excused` is empty and the exemption table must hold nothing for
    # any of these.
    Admission(
        key="featured",
        rows=("P S1",),
        address=f"{B}/in/me/details/featured/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/in/me/details/featured/edit/", "/edit/",
                    "the Featured editor, a write"),
            Sibling(f"{B}/in/me/details/featured/?x=1", None, "a QUERY"),
            Sibling(f"{B}/in/someone-else/details/featured/", None,
                    "another member's Featured page"),
            Sibling(f"{B}/in/me/details/", None, "the details root"),
        ),
    ),
    Admission(
        key="skill-insights",
        rows=("P S3",),
        address=f"{B}/in/me/skill-insights/2/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/in/me/skill-insights/", None, "no segment"),
            Sibling(f"{B}/in/me/skill-insights/12345/", None,
                    "five digits -- the class is closed at four"),
            Sibling(f"{B}/in/me/skill-insights/abc/", None, "a word segment"),
            Sibling(f"{B}/in/me/skill-insights/\u0662/", None,
                    "an Arabic-Indic digit, which a \\d class would admit"),
            Sibling(f"{B}/in/me/skill-insights/2/?x=1", None, "a QUERY"),
            Sibling(f"{B}/in/someone-else/skill-insights/2/", None,
                    "another member's skill page"),
        ),
        spellings=(f"{B}/in/me/skill-insights/9999/",),
    ),
    Admission(
        key="premium-matches",
        rows=("N 199",),
        address=f"{B}/premium/matches/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/premium/", None, "the purchase family root"),
            Sibling(f"{B}/premium/matches/?x=1", None, "a QUERY"),
            Sibling(f"{B}/premium/matches/connect/", "/connect",
                    "a SUB-PATH naming an act"),
            Sibling(f"{B}/premium/products/", None, "a purchase page"),
        ),
    ),
    Admission(
        key="tracker-interview",
        rows=("J 50",),
        address=f"{B}/jobs-tracker/?stage=interview",
        excused=frozenset(),
        twin=False,
        siblings=(
            Sibling(f"{B}/jobs-tracker/?stage=withdraw", None,
                    "a stage nothing names"),
            Sibling(f"{B}/jobs-tracker/?stage=interview&x=1", None,
                    "a second key"),
            Sibling(f"{B}/jobs-tracker/?stage=INTERVIEW", None,
                    "another case"),
            Sibling(f"{B}/jobs-tracker/?stage=in_progress", None,
                    "the tab's LABEL, which is not its address"),
            Sibling(f"{B}/jobs-tracker/?stage=interview/", None,
                    "a trailing slash after the token"),
        ),
    ),
    Admission(
        key="tracker-archived",
        rows=("J 51",),
        address=f"{B}/jobs-tracker/?stage=archived",
        excused=frozenset(),
        twin=False,
        siblings=(
            Sibling(f"{B}/jobs-tracker/?stage=archive", None,
                    "a near spelling"),
            Sibling(f"{B}/jobs-tracker/?stage=archived&x=1", None,
                    "a second key"),
        ),
    ),
    Admission(
        key="tracker-clicked-apply",
        rows=("J 52",),
        address=f"{B}/jobs-tracker/?stage=clicked_apply",
        excused=frozenset(),
        twin=False,
        siblings=(
            Sibling(f"{B}/jobs-tracker/?stage=clicked_apply&apply=1", None,
                    "a second key naming the act"),
            Sibling(f"{B}/jobs-tracker/?stage=clicked", None,
                    "a near spelling"),
        ),
    ),
    Admission(
        key="ai-job-search",
        rows=("J 16",),
        address=f"{B}/jobs/search-results/",
        excused=frozenset(),
        query=True,
        siblings=(
            Sibling(f"{B}/jobs/search-results/?keywords=a&alertAction=viewjobs",
                    "action=", "the alert links LinkedIn draws, which carry "
                    "alertAction= (J 38: its D6 route is elsewhere)"),
            Sibling(f"{B}/jobs/search-results/x/", None, "a SUB-PATH"),
            Sibling(f"{B}/jobs/search-resultsx/", None, "a longer word"),
            Sibling(f"{B}/jobs/search-results/?keywords=a#frag", None,
                    "a fragment"),
        ),
        spellings=(f"{B}/jobs/search-results/?keywords=placeholder",
                   f"{B}/jobs/search-results?keywords=placeholder"),
    ),
    Admission(
        key="career-insights",
        rows=("J 160",),
        address=f"{B}/explore-career-insights/",
        excused=frozenset(),
        query=True,
        siblings=(
            Sibling(f"{B}/explore-career-insights/x/", None, "a SUB-PATH"),
            Sibling(f"{B}/explore-career-insights/?action=x", "action=",
                    "a query naming an act"),
        ),
        spellings=(
            f"{B}/explore-career-insights/?job_title=placeholder&location=placeholder",
            f"{B}/explore-career-insights?job_title=placeholder",
        ),
    ),
    Admission(
        key="learning-home",
        rows=("J 152",),
        address=f"{B}/learning/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/learning/chatbot/", None,
                    "the AI coach (J 155), not admitted"),
            Sibling(f"{B}/learning/1234567890/1234567890/", None,
                    "a course video (J 153), not admitted"),
            Sibling(f"{B}/learning/role-play/scenarios/new/", None,
                    "starting a role-play session"),
            Sibling(f"{B}/learning/me/", None, "the library's parent"),
            Sibling(f"{B}/learning/?x=1", None, "a QUERY"),
        ),
    ),
    Admission(
        key="learning-browse",
        rows=("J 152",),
        address=f"{B}/learning/browse/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/learning/browse/x/", None, "a SUB-PATH"),
        ),
    ),
    Admission(
        key="learning-certifications",
        rows=("J 152",),
        address=f"{B}/learning/browse/certifications/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/learning/browse/certifications/x/", None,
                    "a SUB-PATH"),
        ),
    ),
    Admission(
        key="learning-library",
        rows=("J 154",),
        address=f"{B}/learning/me/my-library/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/learning/me/my-library/x/", None, "a SUB-PATH"),
        ),
    ),
    Admission(
        key="learning-in-progress",
        rows=("J 154",),
        address=f"{B}/learning/me/my-library/in-progress/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/learning/me/my-library/in-progress/?x=1", None,
                    "a QUERY"),
        ),
    ),
    Admission(
        key="learning-career-journey",
        rows=("J 156",),
        address=f"{B}/learning/career-journey/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/learning/career-journey/goals/", None,
                    "a SUB-PATH where a goal would be set"),
        ),
    ),
    Admission(
        key="company-about",
        rows=("J 106",),
        address=f"{B}/company/placeholder-org/about/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/company/placeholder-org/jobs/", None,
                    "the jobs tab (J 107 needs none)"),
            Sibling(f"{B}/company/placeholder-org/posts/", None,
                    "the posts tab (J 110, a RULING row)"),
            Sibling(f"{B}/company/placeholder-org/admin/", None,
                    "Page administration"),
            Sibling(f"{B}/company/%2e%2e/about/", None,
                    "an encoded dot segment: the class holds no percent"),
            Sibling(f"{B}/company/a.b/about/", None, "a dotted segment"),
            Sibling(f"{B}/company/placeholder-org/about/?x=1", None, "a QUERY"),
            Sibling(f"{B}/company/placeholder-org/about/../../in/someone-else/",
                    None, "a TRAVERSAL onto a member profile"),
        ),
        spellings=(f"{B}/company/5417062/about/",),
    ),
    Admission(
        key="company-life",
        rows=("J 109",),
        address=f"{B}/company/placeholder-org/life/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/company/placeholder-org/life/12345/", None,
                    "one Life video by id"),
        ),
        spellings=(f"{B}/company/5417062/life/",),
    ),
    Admission(
        key="company-products",
        rows=("J 111",),
        address=f"{B}/company/placeholder-org/products/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/company/placeholder-org/products/placeholder/", None,
                    "one product under the tab (J 166 reads it at /products/)"),
        ),
        spellings=(f"{B}/company/5417062/products/",),
    ),
    Admission(
        key="company-product",
        rows=("J 111",),
        address=f"{B}/company/placeholder-org/product/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/company/placeholder-org/product/x/", None,
                    "a SUB-PATH"),
        ),
        spellings=(f"{B}/company/5417062/product/",),
    ),
    Admission(
        key="company-services",
        rows=("J 111",),
        address=f"{B}/company/placeholder-org/services/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/company/placeholder-org/services/request/", None,
                    "a SUB-PATH where a request would be made"),
        ),
        spellings=(f"{B}/company/5417062/services/",),
    ),
    Admission(
        key="company-insights",
        rows=("J 113", "J 114"),
        address=f"{B}/company/placeholder-org/insights/?insightType=HEADCOUNT",
        excused=frozenset(),
        twin=False,
        siblings=(
            Sibling(f"{B}/company/placeholder-org/insights/", None,
                    "the tab without its drawn key"),
            Sibling(f"{B}/company/placeholder-org/insights/?insightType=ALUMNI",
                    None, "another value -- only the drawn one is admitted"),
            Sibling(f"{B}/company/placeholder-org/insights/?insightType=HEADCOUNT&x=1",
                    None, "a second key"),
        ),
        spellings=(f"{B}/company/5417062/insights/?insightType=HEADCOUNT",),
    ),
    Admission(
        key="company-events",
        rows=("J 165",),
        address=f"{B}/company/placeholder-org/events/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/company/placeholder-org/events/12345/", None,
                    "one event under the tab"),
        ),
        spellings=(f"{B}/company/5417062/events/",),
    ),
    Admission(
        key="showcase",
        rows=("J 167",),
        address=f"{B}/showcase/placeholder-page/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/showcase/", None, "the family root"),
            Sibling(f"{B}/showcase/a.b/", None, "a dotted segment"),
            Sibling(f"{B}/showcase/placeholder-page/admin/", None,
                    "Page administration"),
        ),
    ),
    Admission(
        key="product-page",
        rows=("J 166",),
        address=f"{B}/products/placeholder-product/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/products/", None, "the family root"),
            Sibling(f"{B}/products/placeholder-product/reviews/", None,
                    "a SUB-PATH"),
        ),
        spellings=(f"{B}/products/12345/",),
    ),
    Admission(
        key="resume-tailoring",
        rows=("J 147", "J 148", "J 149"),
        address=f"{B}/job-apply-resources/?jobPostingId=1234567890",
        excused=frozenset(),
        twin=False,
        siblings=(
            Sibling(f"{B}/job-apply-resources/", None, "no posting"),
            Sibling(f"{B}/job-apply-resources/?jobPostingId=abc", None,
                    "a non-numeric id"),
            Sibling(f"{B}/job-apply-resources/?jobPostingId=1&x=1", None,
                    "a second key"),
            Sibling(f"{B}/jobs/view/1234567890/apply/", None,
                    "the apply route (J 82), not admitted"),
        ),
    ),
    # THE CONTENT SEARCH VERTICAL, 2026-10-10, on CONTENT-VERTICAL-NOT-ALL-
    # RESULTS: its own exact line, D2's spelling (a closed segment, the query
    # as a shape), and the CONTROL the ruling asks for -- the mixed
    # all-results page, with and without a query, still refused.
    Admission(
        key="search-content",
        rows=("M C70", "M C93"),
        address=f"{B}/search/results/content/",
        excused=frozenset(),
        query=True,
        siblings=(
            Sibling(f"{B}/search/results/all/?keywords=x", None,
                    "the mixed all-results page the ruling keeps refused"),
            Sibling(f"{B}/search/results/all/", None,
                    "the all-results page with no query"),
            Sibling(f"{B}/search/results/content/x/", None, "a SUB-PATH"),
            Sibling(f"{B}/search/results/contents/", None, "a longer word"),
            Sibling(f"{B}/search/results/content/../../mypreferences/d/close-account",
                    None, "the account-ending traversal"),
            Sibling(f"{B}/search/results/schools/?keywords=x", None,
                    "a vertical no ruling reached"),
            Sibling(f"{B}/search/results/content/?keywords=a#frag", None,
                    "a fragment"),
        ),
        spellings=(
            f"{B}/search/results/content/?keywords=placeholder",
            f"{B}/search/results/content?keywords=placeholder",
            f"{B}/search/results/content/?keywords=%23placeholder&origin=HASHTAG_SEARCH",
        ),
    ),
)

KEYS = [a.key for a in ADMISSIONS]


def _refusal(url: str) -> str:
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    return str(caught.value)


def _lines_for(url: str):
    return [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]


def _exemptions_for(url: str):
    return [
        (p, s) for p, s in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
        if p.match(url)
    ]


def _trips(url: str) -> frozenset:
    lowered = url.lower()
    return frozenset(s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in lowered)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_the_address_is_admitted_through_the_shipped_gate(adm):
    for url in sorted(_own(adm)):
        assert readonly.is_read_url(url), (adm.key, url)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_exactly_one_anchored_line_carries_it_and_it_has_no_wildcard(adm):
    lines = _lines_for(adm.address)
    assert len(lines) == 1, (adm.key, [p.pattern for p in lines])
    source = lines[0].pattern
    assert source.startswith("^https://www\\.linkedin\\.com/"), source
    assert source.endswith("$"), source
    if adm.query:
        assert source.endswith("/?" + QUERY_GROUP + "$"), source
        source = source.replace(QUERY_GROUP, "")
    for token in (".*", ".+", r"\w", r"\S", r"\d", "[^"):
        assert token not in source, (adm.key, token, source)
    if "/in/" in source:
        assert "/in/me/" in source, (adm.key, source)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_the_exemption_excuses_exactly_what_the_address_trips(adm):
    # MEASURED against the shipped tuple, not copied from the table above:
    # the table's claim is checked against the gate's own substrings.
    assert _trips(adm.address) == adm.excused, (adm.key, _trips(adm.address))
    entries = _exemptions_for(adm.address)
    if not adm.excused:
        assert entries == [], (adm.key, entries)
        return
    assert len(entries) == 1, (adm.key, entries)
    assert entries[0][1] == adm.excused, (adm.key, entries[0][1])
    for bad in adm.excused:
        assert bad in readonly._FORBIDDEN_URL_SUBSTRINGS, bad


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_every_sibling_is_still_refused_on_the_gate_that_names_it(adm):
    for sib in adm.siblings:
        assert not readonly.is_read_url(sib.url), (adm.key, sib.why)
        message = _refusal(sib.url)
        if sib.gate is None:
            assert ALLOWLIST_SENTENCE in message, (adm.key, sib.why, message)
        else:
            assert "contains %r" % sib.gate in message, (adm.key, sib.why, message)
        # The exemption reaches no sibling.
        assert readonly._pattern_exempted_substrings(sib.url) == frozenset(), (
            adm.key, sib.why)


@pytest.mark.parametrize(
    "adm", [a for a in ADMISSIONS if a.excused], ids=[a.key for a in ADMISSIONS if a.excused]
)
def test_without_the_exemption_the_substring_refuses_and_says_a_pattern_would_admit(
    adm, monkeypatch
):
    """THE FIRST GATE ALONE: the allowlist line cannot admit it by itself."""
    kept = tuple(
        (p, s) for p, s in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
        if not p.match(adm.address)
    )
    assert len(kept) == len(readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS) - 1
    monkeypatch.setattr(readonly, "_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS", kept)
    assert not readonly.is_read_url(adm.address)
    message = _refusal(adm.address)
    assert PATTERN_WOULD_ADMIT in message, (adm.key, message)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_without_the_line_the_address_is_refused(adm, monkeypatch):
    """THE SECOND GATE ALONE, and the proven rollback of the allowlist half."""
    kept = tuple(
        p for p in readonly._ALLOWED_URL_PATTERNS if not p.match(adm.address)
    )
    assert len(kept) == len(readonly._ALLOWED_URL_PATTERNS) - 1
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", kept)
    assert not readonly.is_read_url(adm.address)
    assert ALLOWLIST_SENTENCE in _refusal(adm.address), adm.key


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_each_admission_newly_admits_exactly_its_own_spellings(adm):
    """THE BLAST RADIUS of each pair, over the shipped corpus plus every
    address in this file -- before and after, on concrete urls."""
    own = _own(adm)
    corpus = sorted(
        set(blast_radius.corpus())
        | own
        | {s.url for a in ADMISSIONS for s in a.siblings}
        | {a.address for a in ADMISSIONS}
    )
    allow = readonly._ALLOWED_URL_PATTERNS
    exempt = readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
    after = {url: readonly.is_read_url(url) for url in corpus}
    try:
        readonly._ALLOWED_URL_PATTERNS = tuple(
            p for p in allow if not p.match(adm.address)
        )
        readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS = tuple(
            (p, s) for p, s in exempt if not p.match(adm.address)
        )
        before = {url: readonly.is_read_url(url) for url in corpus}
    finally:
        readonly._ALLOWED_URL_PATTERNS = allow
        readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS = exempt
    gained = sorted(u for u in corpus if after[u] and not before[u])
    lost = sorted(u for u in corpus if before[u] and not after[u])
    assert gained == sorted(own), (adm.key, gained)
    assert lost == [], (adm.key, lost)


def test_the_forbidden_tuple_is_unchanged_and_every_crossed_substring_is_in_it():
    assert len(readonly._FORBIDDEN_URL_SUBSTRINGS) == FORBIDDEN_TUPLE_SIZE
    for adm in ADMISSIONS:
        for bad in adm.excused:
            assert bad in readonly._FORBIDDEN_URL_SUBSTRINGS, (adm.key, bad)


def test_the_table_holds_no_duplicate_address():
    addresses = [a.address for a in ADMISSIONS]
    assert len(addresses) == len(set(addresses)), addresses
