"""How a posting is applied to, and every way that question goes wrong.

WHY THIS READ IS HELD TO A HIGHER STANDARD THAN THE OTHERS. Follow and save
are toggles: read one backwards and the worst case is an offer to unfollow a
company he already left, which he can undo in one click. An apply cannot be
undone by anybody. So this reader is allowed to be wrong in exactly ONE way --
by declining to answer -- and every assertion below is arranged around that
asymmetry. ``linkedin_apply`` and ``offsite`` are POSITIVE identifications
requiring several independent fields to agree; everything else is
``shape.APPLY_UNKNOWN`` with a reason a person can act on.

TWO ROUTES, NOT TWO STATES, and this is the distinction the module is built
on. ``linkedin_apply`` keeps the application inside LinkedIn. ``offsite`` hands
the applicant to a third party on somebody else's domain. They are different
problems with different owners, and naming the wrong one is naming the wrong
recipient for an application.

WHY NO SINGLE FIELD IS TRUSTED, each point checked here rather than asserted
in a comment:

* THE ACCESSIBLE NAME IS THE STRONGEST FIELD AND STILL NOT ENOUGH. LinkedIn
  has already renamed this control once, and ``job_detail_hydrated.html``
  carries LinkedIn's own banner announcing it. The feature everybody calls
  "Easy Apply" is not called that in any accessible name on the page -- the
  phrase appears only in prose, twice, which is exactly what makes a substring
  search over the page look like it works.
* THE HREF IS NOT SPECIFIC TO APPLYING. ``/safety/go/`` is LinkedIn's generic
  outbound wrapper; ``job_detail_following_hydrated.html`` holds TWO of them
  and only one is the apply control. Href shape alone false-positives.
* THE HYDRATION ATTRIBUTE CARRIES NO INFORMATION. ``data-view-name`` is on the
  settled LinkedIn-route capture and absent from the settled off-site one, so
  its absence proves nothing. Both renders of each posting must classify
  identically, and that is asserted pairwise.

WHAT IS PINNED AND WHAT IS NOT. The job ids, the employer and the destination
subdomain in these fixtures are INVENTED, and the ones this module names are
already named by its siblings. The third-party host is never typed out: it is
read from the decode at runtime and checked for the properties that matter --
that it decoded, and that it is not LinkedIn. Every host written into this
file is under the reserved ``.test`` TLD and belongs to no one.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

FIXTURES = {
    # The LinkedIn-hosted route, before and after the page settles. The two
    # differ by the hydration attribute and by nothing that matters.
    "li_pre": FIXTURE_DIR / "job_detail.html",
    "li_hydrated": FIXTURE_DIR / "job_detail_hydrated.html",
    # The off-site route, same pair. This posting's apply control hands the
    # applicant to the employer's own system.
    "off_pre": FIXTURE_DIR / "job_detail_following.html",
    "off_hydrated": FIXTURE_DIR / "job_detail_following_hydrated.html",
    # The document before anything renders. No apply control of any kind.
    "shell": FIXTURE_DIR / "job_detail_shell.html",
}

LI_RENDERS = ["li_pre", "li_hydrated"]
OFF_RENDERS = ["off_pre", "off_hydrated"]

#: Invented job ids, the same ones ``test_job_detail_fixture.py`` and
#: ``test_follow_state_fixture.py`` already name.
LI_JOB_ID = "4600000042"
OFF_JOB_ID = "4600000117"

LI_LABEL = "LinkedIn Apply to this job"
OFF_LABEL = "Apply on company website"

#: The LinkedIn-hosted apply url for that posting, spelled out rather than
#: lifted from the fixture, so the fixture and this constant can be compared.
LI_APPLY_HREF = (
    f"https://www.linkedin.com/jobs/view/{LI_JOB_ID}/apply/?openSDUIApplyFlow=true&"
)

#: The invented employer's own subdomain in the off-site fixture. Only the
#: leading label is pinned: it is the invented half, and it is the half that
#: proves the percent-encoded destination actually decoded.
OFF_EMPLOYER_SLUG = "vantrex-systems"

#: Destinations invented FOR THIS MODULE under the reserved ``.test`` TLD, so
#: no assertion here names anybody's real applicant-tracking system.
THIRD_PARTY = "https://careers.hollowfield-example.test/openings/55"
THIRD_PARTY_HOST = "careers.hollowfield-example.test"
OTHER_THIRD_PARTY = "http://jobs.brackmoor-example.test/apply?req=7"
OTHER_THIRD_PARTY_HOST = "jobs.brackmoor-example.test"

#: The phrase LinkedIn no longer uses on this control, and the reason
#: ``shape.APPLY_LABELS`` must never grow a key containing it.
RENAMED_AWAY = "easy apply"


def outbound(destination: str) -> str:
    """Wrap ``destination`` the way LinkedIn's interstitial wraps one.

    The dots of the hostname are percent-encoded as ``%2E``, and the trailing
    ampersands are LinkedIn's, not a typo -- both are the real shape, copied
    from the committed capture. A helper that encoded the destination the
    "sensible" way would leave the dots alone and would then not exercise the
    decode this module exists to check.
    """
    encoded = quote(destination, safe="").replace(".", "%2E")
    return f"https://www.linkedin.com/safety/go/?url={encoded}&&&isSdui=true"


# ---------------------------------------------------------------------------
# The browser harness
# ---------------------------------------------------------------------------


async def _with_html(html: str, work):
    """Run ``work(page)`` over frozen markup in a LOCAL headless Chromium.

    Same harness as ``test_follow_state_fixture.py``: nothing here reaches the
    network or an account. The apply control is an anchor and its destination
    is an attribute, so a fake page could not answer -- the attribute has to be
    read off a real parsed DOM.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await browser.close()


def markup(which: str) -> str:
    return FIXTURES[which].read_text(encoding="ascii")


async def _apply_control(which: str) -> dict:
    async def work(page):
        return await dom.read_apply_control(page)

    return await _with_html(markup(which), work)


def _route_of(control: dict, job_id: str) -> dict:
    """The verdict the tool builds, assembled exactly as the tool assembles it."""
    return shape.apply_route(
        control.get("label"),
        control.get("href"),
        count=int(control.get("count") or 0),
        job_id=job_id,
        link_target=control.get("link_target"),
    )


async def _apply_verdict(which: str, job_id: str) -> tuple[dict, dict]:
    control = await _apply_control(which)
    return control, _route_of(control, job_id)


async def _accessible_names(which: str) -> list:
    """Every ``aria-label`` on the page, in document order."""

    async def work(page):
        return await page.eval_on_selector_all(
            "[aria-label]", "els => els.map(el => el.getAttribute('aria-label'))"
        )

    return await _with_html(markup(which), work)


async def _visible_text(which: str) -> str:
    async def work(page):
        return await page.inner_text("body")

    return await _with_html(markup(which), work)


# ---------------------------------------------------------------------------
# 0. What the fixtures actually contain
# ---------------------------------------------------------------------------

#: How many apply anchors of each route each capture draws. These counts ARE
#: the premise of every browser test below, so they are checked rather than
#: assumed: a fixture re-captured with a second apply control would otherwise
#: turn several tests below into assertions about a page nobody looked at.
APPLY_CONTROL_CENSUS = {
    "li_pre": {LI_LABEL: 1, OFF_LABEL: 0},
    "li_hydrated": {LI_LABEL: 1, OFF_LABEL: 0},
    "off_pre": {LI_LABEL: 0, OFF_LABEL: 1},
    "off_hydrated": {LI_LABEL: 0, OFF_LABEL: 1},
    "shell": {LI_LABEL: 0, OFF_LABEL: 0},
}

#: ``/safety/go/`` urls per capture. TWO in the settled off-site render, and
#: that second one is the whole argument against classifying on the href.
OUTBOUND_WRAPPERS = {"off_pre": 1, "off_hydrated": 2}


@pytest.mark.parametrize("which", list(FIXTURES))
def test_the_fixture_exists_and_draws_the_apply_controls_this_module_expects(which):
    """The premise of every browser test in this file, stated as a check.

    Deleting this leaves the browser tests below asserting routes about a page
    whose apply controls nobody counted -- and a re-capture that picked up a
    second control would show up as a confusing "unknown" three tests away
    instead of here. The ASCII decode is checked in the same place because the
    harness reads these with ``encoding="ascii"``, and a fixture that acquired
    a curly quote otherwise fails as a UnicodeDecodeError inside Chromium,
    naming neither the file nor the reason.
    """
    path = FIXTURES[which]
    assert path.exists(), f"missing fixture: {path}"
    raw = path.read_bytes()
    assert raw != b"", f"empty fixture: {path}"
    text = raw.decode("ascii")

    for label, expected in APPLY_CONTROL_CENSUS[which].items():
        assert text.count(f'aria-label="{label}"') == expected, (which, label)


@pytest.mark.parametrize("which, expected", sorted(OUTBOUND_WRAPPERS.items()))
@pytest.mark.asyncio
async def test_the_outbound_wrapper_is_not_specific_to_applying(which, expected):
    """THE CASE AGAINST CLASSIFYING ON THE HREF, made from this repo's own capture.

    The settled off-site posting carries TWO ``/safety/go/`` urls and only one
    of them is the apply control; the other is an unrelated external link on
    the same page. A reader that took "has an outbound wrapper" as evidence of
    the off-site route would therefore have two candidates and no way to
    choose. The label is what narrows it to one, which is why the read still
    reports count 1 here.

    Delete this and the conjunction in ``apply_route`` looks like caution
    rather than a response to something measured.
    """
    assert markup(which).count("/safety/go/") == expected

    control = await _apply_control(which)
    assert control["count"] == 1
    assert control["label"] == OFF_LABEL


def test_the_two_renders_of_the_linkedin_posting_really_do_differ():
    """The control for the pairwise-agreement test, and it is not optional.

    "Both renders agree" is trivially true of two identical files. The pair
    differs by exactly the hydration attribute -- present on the settled
    render, absent from the other -- which is the attribute a reader would be
    tempted to anchor on. Asserting the asymmetry here is what gives the
    agreement test something to prove.
    """
    hydration_marker = 'data-view-name="job-apply-button"'
    assert hydration_marker in markup("li_hydrated")
    assert hydration_marker not in markup("li_pre")


# ---------------------------------------------------------------------------
# 1. The classifier, exhaustively, with no browser involved
# ---------------------------------------------------------------------------


def test_no_apply_control_is_not_evidence_the_job_cannot_be_applied_to():
    """THE LOAD-BEARING REFUSAL.

    A posting that has not hydrated and a posting drawing a route nobody has
    catalogued look identical from here. Reporting either as "this job has no
    apply route" would tell him a live posting is closed, so the reason has to
    say out loud that absence is not evidence -- a caller cannot tell a real
    negative from a failed read unless the answer says which it is.
    """
    verdict = shape.apply_route(LI_LABEL, LI_APPLY_HREF, count=0, job_id=LI_JOB_ID)
    assert verdict["route"] == shape.APPLY_UNKNOWN
    assert verdict["destination"] is None
    assert verdict["destination_host"] is None

    why = verdict["why"].casefold()
    assert "not evidence" in why, verdict["why"]
    assert "hydrated" in why, verdict["why"]
    assert "applied to" in why, verdict["why"]


@pytest.mark.parametrize("count", [2, 3, 7])
def test_more_than_one_control_is_ambiguous_and_names_the_count(count):
    """Several apply controls means at least one belongs to something else.

    Taking the first would be taking it by position on the one action that
    cannot be undone. The count goes into the reason because "nothing
    rendered" and "there were three of them" want opposite responses from
    whoever reads it, and both arrive spelled ``unknown``.
    """
    verdict = shape.apply_route(LI_LABEL, LI_APPLY_HREF, count=count, job_id=LI_JOB_ID)
    assert verdict["route"] == shape.APPLY_UNKNOWN
    assert str(count) in verdict["why"], verdict["why"]
    assert verdict["destination"] is None
    assert verdict["destination_host"] is None


@pytest.mark.parametrize("label", ["Postuler", "Apply now", "", "  ", None])
def test_an_unrecognised_label_is_refused_and_the_label_is_quoted(label):
    """LinkedIn in French, LinkedIn having renamed the control again, or a
    control that rendered without a name at all.

    None of those is a route, and picking one would be a coin toss reported as
    a reading. The label is quoted into the reason because the response
    differs: a French label is a locale problem, a new English label is drift
    in LinkedIn's own vocabulary and means this reader's table needs a row.
    """
    verdict = shape.apply_route(label, LI_APPLY_HREF, count=1, job_id=LI_JOB_ID)
    assert verdict["route"] == shape.APPLY_UNKNOWN
    assert repr(str(label or "").strip()) in verdict["why"], verdict["why"]
    assert verdict["destination"] is None


def test_the_settled_label_carrying_title_and_employer_is_still_the_linkedin_route():
    """THE SPELLING THAT SHIPPED BROKEN, and the coverage gap that hid it.

    LinkedIn serves this control under TWO names during a single page load:
    ``LinkedIn Apply to this job`` while it is still hydrating, and
    ``LinkedIn Apply to <TITLE> at <COMPANY>`` once it settles. Measured
    2026-08-24 on a live posting.

    ``APPLY_LABELS`` matched by exact equality, so ``apply_route`` returned
    ``unknown`` for an ordinary LinkedIn Apply posting as soon as the page
    finished rendering -- and ``linkedin_job_detail`` reported that to callers.

    WHY THE WHOLE SUITE STAYED GREEN WITH IT. Every fixture in this repo was
    captured mid-hydration and carries the SHORT spelling, so no test ever
    handed the classifier the string LinkedIn actually ends up serving. The
    suite could not fail on this. That is the reason this case is built from a
    LITERAL rather than from a fixture: the fixtures are exactly what missed
    it, so asserting against them again would reproduce the blind spot.
    """
    settled = "LinkedIn Apply to Senior Backend Engineer at Northwind Systems"
    assert settled.startswith(shape.LINKEDIN_APPLY_PREFIX)
    verdict = shape.apply_route(settled, LI_APPLY_HREF, count=1, job_id=LI_JOB_ID)
    assert verdict["route"] == "linkedin_apply", verdict["why"]
    assert verdict["destination"] == LI_APPLY_HREF


def test_the_prefix_did_not_widen_what_gets_identified():
    """Accepting a prefix must not turn the conjunction into a name check.

    The href and job-id agreement still have to hold. Without this, the fix
    above would be indistinguishable from deleting the guard.
    """
    settled = "LinkedIn Apply to Senior Backend Engineer at Northwind Systems"
    wrong_posting = shape.apply_route(
        settled, LI_APPLY_HREF, count=1, job_id="4600009999"
    )
    assert wrong_posting["route"] == shape.APPLY_UNKNOWN, wrong_posting["why"]

    # And a name that merely CONTAINS the prefix later in the string is not it.
    assert (
        shape.apply_route(
            "Tailor my resume for LinkedIn Apply to this job",
            LI_APPLY_HREF,
            count=1,
            job_id=LI_JOB_ID,
        )["route"]
        == shape.APPLY_UNKNOWN
    )


def test_the_linkedin_route_needs_its_label_and_the_postings_own_apply_url():
    """The first positive identification, and what it takes to earn it.

    Both fields have to agree before the route counts as identified, and the
    destination is reported so a caller can see where the application would be
    made rather than trusting the one-word answer.
    """
    verdict = shape.apply_route(LI_LABEL, LI_APPLY_HREF, count=1, job_id=LI_JOB_ID)
    assert verdict["route"] == "linkedin_apply"
    assert verdict["destination"] == LI_APPLY_HREF
    assert verdict["destination_host"] == "www.linkedin.com"
    assert repr(LI_LABEL) in verdict["why"], verdict["why"]


def test_a_control_pointing_at_a_different_posting_is_refused_and_names_both_ids():
    """THE MOST IMPORTANT REFUSAL IN THIS FILE.

    The label is right, the url is a valid LinkedIn apply url, and it belongs
    to a DIFFERENT job. Classifying this would put the operator one confirm
    away from applying to a posting he never opened. Both ids go into the
    reason: told only that something mismatched, he cannot tell a stale render
    from a reader that read the wrong element, and those want different
    responses.
    """
    verdict = shape.apply_route(LI_LABEL, LI_APPLY_HREF, count=1, job_id=OFF_JOB_ID)
    assert verdict["route"] == shape.APPLY_UNKNOWN
    assert LI_JOB_ID in verdict["why"], verdict["why"]
    assert OFF_JOB_ID in verdict["why"], verdict["why"]
    assert verdict["destination"] is None
    assert verdict["destination_host"] is None


@pytest.mark.parametrize(
    "href",
    [
        f"https://www.linkedin.com/jobs/view/{LI_JOB_ID}/",
        f"https://www.linkedin.com/jobs/view/{LI_JOB_ID}/apply-later/",
        f"https://www.linkedin.com/jobs/collections/apply/?currentJobId={LI_JOB_ID}",
        THIRD_PARTY,
        "",
        None,
    ],
)
def test_the_linkedin_label_on_a_non_apply_href_is_refused(href):
    """The label claims the LinkedIn-hosted route; the destination does not.

    A posting url is not an apply url, an off-site url under a LinkedIn label
    is a contradiction, and a missing href is a control that goes nowhere.
    Accepting any of them would let the accessible name classify on its own --
    which is the one field LinkedIn has already changed on this control.
    """
    verdict = shape.apply_route(LI_LABEL, href, count=1, job_id=LI_JOB_ID)
    assert verdict["route"] == shape.APPLY_UNKNOWN
    assert repr(str(href or "").strip()) in verdict["why"], verdict["why"]
    assert verdict["destination"] is None


def test_the_offsite_route_names_the_third_party_host():
    """The second positive identification: the application leaves LinkedIn.

    Naming the host is the point of the answer, not decoration. "Off-site" on
    its own tells him an application would be made somewhere; the host tells
    him where, which is the only form of the fact he can check before
    consenting to it.
    """
    verdict = shape.apply_route(
        OFF_LABEL, outbound(THIRD_PARTY), count=1, link_target="_blank"
    )
    assert verdict["route"] == "offsite"
    assert verdict["destination"] == THIRD_PARTY
    assert verdict["destination_host"] == THIRD_PARTY_HOST
    assert repr(OFF_LABEL) in verdict["why"], verdict["why"]
    assert THIRD_PARTY_HOST in verdict["why"], verdict["why"]


@pytest.mark.parametrize("link_target", [None, "", "_self", "_parent", "blank"])
def test_an_offsite_control_without_target_blank_is_refused(link_target):
    """Every off-site apply control measured opens in a new tab; this one does not.

    On its own that is a weak signal, and it is doing weak-signal work: the
    outbound wrapper is generic, so ``target="_blank"`` is one of the few
    things separating an apply control from any other external link on the
    page. The refusal still reports the destination it decoded -- a gate that
    declines to classify can still show him where the link went, and hiding
    that would make the refusal less useful than the evidence behind it.
    """
    verdict = shape.apply_route(
        OFF_LABEL, outbound(THIRD_PARTY), count=1, link_target=link_target
    )
    assert verdict["route"] == shape.APPLY_UNKNOWN
    assert verdict["destination"] == THIRD_PARTY
    assert verdict["destination_host"] == THIRD_PARTY_HOST
    assert 'target="_blank"' in verdict["why"], verdict["why"]


@pytest.mark.parametrize(
    "destination",
    [
        f"https://www.linkedin.com/jobs/view/{LI_JOB_ID}/apply/",
        "https://linkedin.com/jobs/",
        "https://careers.linkedin.com/openings",
        "https://lnkd.in/abc123",
    ],
)
def test_an_offsite_wrapper_that_resolves_back_to_linkedin_is_not_offsite(destination):
    """An off-site route whose destination is LinkedIn is not an off-site route.

    Calling it one would name the wrong owner for the application -- it would
    tell him a third party receives it when LinkedIn does. The subdomain case
    is here because a suffix check is the part that is easy to write wrongly,
    and ``careers.linkedin.com`` is still LinkedIn. ``lnkd.in`` is here because
    it is LinkedIn's own shortener and does not contain the string "linkedin",
    so a host check written as a substring search would wave it through.
    """
    verdict = shape.apply_route(
        OFF_LABEL, outbound(destination), count=1, link_target="_blank"
    )
    assert verdict["route"] == shape.APPLY_UNKNOWN
    assert verdict["destination"] == destination
    assert verdict["destination_host"] == destination.split("/")[2]
    assert "linkedin" in verdict["why"].casefold(), verdict["why"]


@pytest.mark.parametrize(
    "href",
    [
        THIRD_PARTY,
        "https://www.linkedin.com/safety/go/?isSdui=true",
        f"https://www.linkedin.com/jobs/view/{LI_JOB_ID}/apply/",
        "",
        None,
    ],
)
def test_the_offsite_label_without_a_decodable_wrapper_is_refused(href):
    """The label claims the off-site route and nothing says whose site it is.

    A bare third-party href is the interesting one: it looks like the right
    answer and it is not the shape LinkedIn serves, so accepting it would mean
    accepting an href this reader has never seen LinkedIn produce. A gate that
    cannot name the recipient of an application has not identified the route,
    so it reports no destination at all rather than the raw href.
    """
    verdict = shape.apply_route(OFF_LABEL, href, count=1, link_target="_blank")
    assert verdict["route"] == shape.APPLY_UNKNOWN
    assert verdict["destination"] is None
    assert verdict["destination_host"] is None


def test_the_refusal_is_spelled_unknown():
    """Callers on three surfaces have to agree that "could not tell" is an answer.

    Pinned against the literal word rather than against the constant, because
    a test comparing the constant to itself would survive it being renamed to
    something a caller silently treats as falsy -- at which point every
    refusal in this file starts reading as a negative.
    """
    assert shape.APPLY_UNKNOWN == "unknown"


# ---------------------------------------------------------------------------
# 2. The outbound wrapper, decoded
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "destination, host",
    [
        (THIRD_PARTY, THIRD_PARTY_HOST),
        (OTHER_THIRD_PARTY, OTHER_THIRD_PARTY_HOST),
    ],
)
def test_the_wrapper_round_trips_a_destination_whose_dots_are_encoded(
    destination, host
):
    """The decode LinkedIn's interstitial actually requires.

    The dots of the hostname arrive as ``%2E``, so a reader that split the raw
    parameter on ``.`` finds no hostname and one that used the parameter as-is
    yields a string that is not a url. Both failures produce a destination
    that cannot be checked, which is the same outcome as not decoding at all.
    The encoded form is asserted first so this cannot pass on a helper that
    quietly stopped encoding.
    """
    wrapped = outbound(destination)
    assert "%2E" in wrapped
    assert "%2F" in wrapped

    decoded = shape.decode_safety_go(wrapped)
    assert decoded == destination
    assert "%" not in str(decoded)

    verdict = shape.apply_route(OFF_LABEL, wrapped, count=1, link_target="_blank")
    assert verdict["destination_host"] == host


@pytest.mark.parametrize(
    "href",
    [
        # Not the wrapper at all.
        None,
        "",
        THIRD_PARTY,
        f"https://www.linkedin.com/jobs/view/{LI_JOB_ID}/apply/",
        "https://www.linkedin.com/safety/go/",
        # The wrapper with no destination in it.
        "https://www.linkedin.com/safety/go/?isSdui=true",
        "https://www.linkedin.com/safety/go/?url=&&&isSdui=true",
        # A destination that does not decode to an absolute http(s) url.
        "https://www.linkedin.com/safety/go/?url=openings%2F55&isSdui=true",
        "https://www.linkedin.com/safety/go/?url=%2Fjobs%2Fview%2F1&isSdui=true",
        "https://www.linkedin.com/safety/go/?url=mailto%3Ajobs%40x%2Etest&isSdui=true",
        "https://www.linkedin.com/safety/go/?url=https%3A%2F%2F&isSdui=true",
    ],
)
def test_the_decode_returns_none_rather_than_a_guess(href):
    """Three separate ways to have nothing, all answered the same way.

    Not the wrapper, the wrapper carrying no destination, and the wrapper
    carrying something that is not an absolute http(s) url. A scheme-less or
    relative value is the one worth spelling out: it is a string that reads
    like a destination and names no host, so returning it would let the
    off-site branch report a route whose owner it could not identify.

    The positive round-trip above is what stops this passing on a function
    that returns ``None`` for everything.
    """
    assert shape.decode_safety_go(href) is None


# ---------------------------------------------------------------------------
# 3. The real captures, through the real reader, in a real browser
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("which", LI_RENDERS)
@pytest.mark.asyncio
async def test_a_linkedin_route_posting_is_identified_from_the_rendered_control(which):
    """The LinkedIn-hosted route, read off the page LinkedIn served.

    The href is compared against the constant rather than against itself, so
    a re-capture that changed the posting's apply url shows up here instead of
    silently redefining what this module tests. Both renders are covered
    because the settled one carries a hydration attribute the other lacks.
    """
    control, verdict = await _apply_verdict(which, LI_JOB_ID)
    assert control["count"] == 1
    assert control["label"] == LI_LABEL
    assert control["href"] == LI_APPLY_HREF
    assert control["link_target"] is None

    assert verdict["route"] == "linkedin_apply"
    assert verdict["destination"] == LI_APPLY_HREF
    assert verdict["destination_host"] == "www.linkedin.com"


@pytest.mark.parametrize("which", OFF_RENDERS)
@pytest.mark.asyncio
async def test_an_offsite_posting_names_a_host_that_is_not_linkedin(which):
    """The off-site route, and the fact that makes it actionable.

    The host is not typed out -- it is the decode's own output, checked for
    the two properties that matter: that it decoded at all (no percent escapes
    survive, and its leading label is the invented employer's) and that it is
    not LinkedIn. A decode that silently stopped unescaping would leave
    ``%2E`` in the host and fail here rather than reporting a plausible-looking
    destination nobody can visit.
    """
    control, verdict = await _apply_verdict(which, OFF_JOB_ID)
    assert control["count"] == 1
    assert control["label"] == OFF_LABEL
    assert control["link_target"] == "_blank"

    assert verdict["route"] == "offsite"

    host = verdict["destination_host"]
    assert "%" not in host, host
    assert host == host.casefold()
    assert host.split(".")[0] == OFF_EMPLOYER_SLUG, host
    assert host not in ("linkedin.com", "www.linkedin.com", "lnkd.in"), host
    assert not host.endswith(".linkedin.com"), host

    assert verdict["destination"] != control["href"]
    assert verdict["destination"].startswith("https://" + host + "/")


@pytest.mark.asyncio
async def test_the_pre_hydration_shell_refuses_rather_than_reporting_no_route():
    """A posting whose content has not rendered is not a posting without an apply.

    The shell carries the document title and nothing else. Turning that into
    "this job cannot be applied to" would close a live posting on the strength
    of a slow network, so the answer has to be the refusal, and the refusal
    has to say that absence is not evidence.

    The settled renders are re-checked here so this "unknown" cannot be coming
    from a reader that only ever says unknown.
    """
    control, verdict = await _apply_verdict("shell", LI_JOB_ID)
    assert control["count"] == 0
    assert control["label"] is None
    assert control["href"] is None

    assert verdict["route"] == shape.APPLY_UNKNOWN
    assert "not evidence" in verdict["why"].casefold(), verdict["why"]

    _, settled = await _apply_verdict("li_hydrated", LI_JOB_ID)
    assert settled["route"] == "linkedin_apply"
    _, offsite = await _apply_verdict("off_hydrated", OFF_JOB_ID)
    assert offsite["route"] == "offsite"


@pytest.mark.parametrize(
    "pair, job_id",
    [(LI_RENDERS, LI_JOB_ID), (OFF_RENDERS, OFF_JOB_ID)],
    ids=["linkedin_apply", "offsite"],
)
@pytest.mark.asyncio
async def test_both_renders_of_a_posting_classify_identically(pair, job_id):
    """The hydration-independence property, asserted as an equality of verdicts.

    This repo has shipped the other outcome once: a reader anchored on a
    hydration-only attribute passes on the settled render and returns nothing
    on the other. ``data-view-name`` is exactly such an attribute -- present on
    the settled LinkedIn-route capture, absent from the off-site one -- so a
    reader that used it would disagree with itself here. The whole verdict is
    compared, not just the route, because a destination that differed between
    renders would be a different application.
    """
    before, first = await _apply_verdict(pair[0], job_id)
    after, second = await _apply_verdict(pair[1], job_id)
    assert before == after
    assert first == second
    assert first["route"] != shape.APPLY_UNKNOWN


# ---------------------------------------------------------------------------
# 4. Anti-drift: the two modules that never import each other
# ---------------------------------------------------------------------------


def _selector_would_match(selector: str, label: str) -> bool:
    """Would this CSS selector actually match an anchor with this aria-label?

    Written because the assertion it replaces did not ask that. It asked
    whether the literal text ``aria-label="<label>"`` APPEARED IN the selector
    string, which is a different question and a weaker one -- it passes for a
    selector that happens to contain the right characters and fails for a
    correct selector spelled another way. Both of those are wrong answers.
    """
    prefix_form = 'a[aria-label^="'
    exact_form = 'a[aria-label="'
    for clause in selector.split(", "):
        if not clause.endswith('"]'):
            continue
        if clause.startswith(prefix_form):
            if label.startswith(clause[len(prefix_form):-2]):
                return True
        elif clause.startswith(exact_form):
            if label == clause[len(exact_form):-2]:
                return True
    return False


def test_the_selector_and_the_vocabulary_cannot_drift_apart():
    """``dom`` builds the selector, ``shape`` owns the meaning.

    If they drift, the reader stops matching a route it claims to know: a
    label added to ``shape.APPLY_LABELS`` alone is a meaning nothing can ever
    find, and one added to ``dom.APPLY_LABELS_SEEN`` alone is a control that
    matches and then classifies as unknown. Both failures are invisible in a
    suite that tests each module on its own, and both are one-line edits. The
    duplicate check is here because a repeated entry would keep the sets equal
    while making the selector list a label twice.

    AMENDED 2026-08-25, twice over, and the docstring used to open "neither
    imports the other". That is no longer true: ``dom`` now imports ``shape``
    for ``LINKEDIN_APPLY_PREFIX``, so the prefix itself cannot drift -- there
    is one of it. The LABEL SETS still can, which is what this still guards.

    The per-label assertion also changed from a substring check to a real
    match test. It had to: the LinkedIn-hosted arm of the selector is now a
    PREFIX match, because the exact-equality version carried the same
    hydration defect found in ``shape.APPLY_LABELS`` -- LinkedIn serves that
    control as "LinkedIn Apply to this job" mid-hydration and "LinkedIn Apply
    to <TITLE> at <COMPANY>" once settled, so an exact selector finds ZERO
    controls on a rendered posting. A substring assertion cannot express
    "matches this label"; it can only express "contains these characters".
    """
    assert set(dom.APPLY_LABELS_SEEN) == set(shape.APPLY_LABELS), (
        sorted(dom.APPLY_LABELS_SEEN),
        sorted(shape.APPLY_LABELS),
    )
    assert len(dom.APPLY_LABELS_SEEN) == len(set(dom.APPLY_LABELS_SEEN))
    for label in dom.APPLY_LABELS_SEEN:
        assert _selector_would_match(dom.APPLY_CONTROL, label), label

    # AND the settled spelling, which is the whole reason the prefix exists.
    # Without this line the selector could quietly go back to exact matching
    # and every assertion above would still pass.
    settled = f"{shape.LINKEDIN_APPLY_PREFIX}Staff Engineer at Northwind"
    assert _selector_would_match(dom.APPLY_CONTROL, settled), settled

    # The off-site arm is deliberately NOT a prefix -- its label has never been
    # observed varying, and a prefix there would widen what counts as off-site
    # for no measured reason.
    assert not _selector_would_match(dom.APPLY_CONTROL, "Apply on company website x")


def test_the_drift_check_can_fail():
    """The matcher above is only worth having if it rejects things.

    A selector helper that returned True unconditionally would make every
    assertion in the test above vacuous while leaving it green -- the exact
    shape of defect this suite has already found twice in its own guards.
    """
    assert not _selector_would_match('a[aria-label="Apply on company website"]', "Nope")
    assert not _selector_would_match('a[aria-label^="LinkedIn Apply to "]', "Apply now")
    assert _selector_would_match('a[aria-label^="LinkedIn Apply to "]', "LinkedIn Apply to x")
    assert not _selector_would_match("", "anything")


def test_no_label_is_spelled_easy_apply():
    """The rename this reader must not "correct" back.

    LinkedIn renamed Easy Apply to LinkedIn Apply, and the accessible name
    followed. A future edit that helpfully restores the name everybody knows
    would produce a selector matching zero controls on every posting -- which
    reads as count 0, which reads as "could not tell", which is the quiet kind
    of wrong: no error, no exception, every job silently unclassifiable.

    Both modules are checked, and so is the selector string, because the
    selector is built by string join and could in principle be edited directly.
    """
    for label in shape.APPLY_LABELS:
        assert RENAMED_AWAY not in label.casefold(), label
    for label in dom.APPLY_LABELS_SEEN:
        assert RENAMED_AWAY not in label.casefold(), label
    assert RENAMED_AWAY not in dom.APPLY_CONTROL.casefold()

    assert shape.APPLY_LABELS == {
        "LinkedIn Apply to this job": "linkedin_apply",
        "Apply on company website": "offsite",
    }


@pytest.mark.parametrize("which", LI_RENDERS)
@pytest.mark.asyncio
async def test_the_phrase_is_on_the_page_and_in_none_of_its_accessible_names(which):
    """The evidence for the rule above, taken from the capture rather than asserted.

    This posting carries the phrase TWICE in prose -- LinkedIn's own banner
    announcing the rename, and the employer's application instructions -- and
    carries it in zero accessible names. That is the trap in one page: a
    substring search over the markup for "easy apply" finds two hits and
    neither is a control, so it would look like it worked. Only the accessible
    name of the anchor answers, which is the entire case for the reader taking
    a label instead of a page.
    """
    text = await _visible_text(which)
    assert text.casefold().count(RENAMED_AWAY) == 2

    names = await _accessible_names(which)
    assert names != []
    offenders = [name for name in names if name and RENAMED_AWAY in name.casefold()]
    assert offenders == []
    assert LI_LABEL in names


# ---------------------------------------------------------------------------
# 5. Can this module fail?
# ---------------------------------------------------------------------------


def test_the_classifier_identifies_both_routes():
    """THE CONTROL for every refusal above.

    Most of the tests in this file assert ``unknown``, and every one of them
    passes on a function that returns ``unknown`` unconditionally. This is the
    test that does not.
    """
    inside = shape.apply_route(LI_LABEL, LI_APPLY_HREF, count=1, job_id=LI_JOB_ID)
    assert inside["route"] == "linkedin_apply"

    away = shape.apply_route(
        OFF_LABEL, outbound(THIRD_PARTY), count=1, link_target="_blank"
    )
    assert away["route"] == "offsite"


@pytest.mark.asyncio
async def test_mutating_one_field_of_a_real_control_collapses_the_linkedin_route():
    """Take the control this repo actually captured, break one field, watch it refuse.

    The conjunction in ``apply_route`` is its whole design -- several fields
    must agree -- and a conjunction is only real if dropping any one term
    changes the answer. Each mutation below is a term: the label, the
    destination, how many controls rendered, and which posting is being read.
    A reader that had quietly collapsed to "the label says LinkedIn, ship it"
    would still pass every positive test in this file and would fail here.
    """
    control = await _apply_control("li_hydrated")
    assert _route_of(control, LI_JOB_ID)["route"] == "linkedin_apply"

    mutants = {
        "the other route's label": {**control, "label": OFF_LABEL},
        "a label nobody has seen": {**control, "label": "Apply now"},
        "no label at all": {**control, "label": None},
        "the posting url, not the apply url": {
            **control,
            "href": f"https://www.linkedin.com/jobs/view/{LI_JOB_ID}/",
        },
        "a third party's url": {**control, "href": THIRD_PARTY},
        "no href": {**control, "href": None},
        "nothing rendered": {**control, "count": 0},
        "two controls rendered": {**control, "count": 2},
    }
    for name, mutant in mutants.items():
        verdict = _route_of(mutant, LI_JOB_ID)
        assert verdict["route"] == shape.APPLY_UNKNOWN, (name, verdict["why"])

    wrong_posting = _route_of(control, OFF_JOB_ID)
    assert wrong_posting["route"] == shape.APPLY_UNKNOWN, wrong_posting["why"]


@pytest.mark.asyncio
async def test_mutating_one_field_of_a_real_control_collapses_the_offsite_route():
    """The same demonstration on the off-site control, whose terms differ.

    This route has one the other does not -- ``target="_blank"`` -- and it is
    the weakest of them, so it is the one most likely to be dropped by
    somebody simplifying the function. Dropping it would let any labelled
    control wrapping any outbound url classify as an apply, on a page that
    carries an unrelated outbound url of exactly that shape.
    """
    control = await _apply_control("off_hydrated")
    assert _route_of(control, OFF_JOB_ID)["route"] == "offsite"

    mutants = {
        "the other route's label": {**control, "label": LI_LABEL},
        "a label nobody has seen": {**control, "label": "Apply externally"},
        "no label at all": {**control, "label": None},
        "an unwrapped third-party url": {**control, "href": THIRD_PARTY},
        "the wrapper with its destination removed": {
            **control,
            "href": "https://www.linkedin.com/safety/go/?isSdui=true",
        },
        "a wrapper resolving back to linkedin": {
            **control,
            "href": outbound("https://www.linkedin.com/jobs/"),
        },
        "no href": {**control, "href": None},
        "not opened in a new tab": {**control, "link_target": None},
        "nothing rendered": {**control, "count": 0},
        "two controls rendered": {**control, "count": 2},
    }
    for name, mutant in mutants.items():
        verdict = _route_of(mutant, OFF_JOB_ID)
        assert verdict["route"] == shape.APPLY_UNKNOWN, (name, verdict["why"])
