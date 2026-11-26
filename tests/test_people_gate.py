"""PEOPLE-GATE v2 (scripts/people_gate.py), shown failing on SYNTHETIC copies
of the shapes rawsweep26 measured, and shown passing on his own page.

Everyone below is invented: the owner stand-in, the strangers, their member
tokens (the identity guard's declared SYNTHETIC_MEMBER_TOKENS), their slugs
(each with a declared synthetic token) and their photo asset ids. The
record is _audit/2026-11-26-infra26.md, section 4.

RED FIRST. The two pages that broke v1 -- an events page holding members by
urn, photo, picture label and social-proof line with no profile link, and a
list of names with no profile link -- are rebuilt here from their measured
SHAPES. v1's rule (count /in/ links that are not his) keeps both; v2
withholds both and names the rules that fired. Each rule has its own plant,
convicted, and its twin carrying HIS value, which passes; a page of his
own passes outright. No verdict ever carries a value from the page.
"""
from __future__ import annotations

import inspect
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import people_gate as pg  # noqa: E402

# --- the invented cast ---------------------------------------------------------
HIS_SLUG = "owner-example-0001"
HIS_NAME = "Owenly Selfmark"
HIS_TOKEN = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000001"
HIS_NUMERIC = "54321"
HIS_PHOTO = "D4E03AQSYNTHETICOWN01"
STRANGER_SLUG = "another-person-0003"
STRANGER_TOKENS = ("ACoAASYNTHETICSYNTHETICSYNTHETIC0000002",
                   "ACoAASYNTHETICSYNTHETICSYNTHETIC0000003")
STRANGER_PHOTOS = ("D4E03AQSYNTHETICOTHER2", "D4E03AQSYNTHETICOTHER3")
STRANGER_NAMES = ("Qorvex Plantwell", "Ysolde Fernquist")
EVENTS_URL = "https://www.linkedin.com/company/example-org/events/"
JOBS_URL = "https://www.linkedin.com/jobs/search/?keywords=example"

#: Every value no verdict may ever print.
VALUES = (HIS_SLUG, HIS_NAME, HIS_TOKEN, HIS_PHOTO, STRANGER_SLUG, *STRANGER_TOKENS,
          *STRANGER_PHOTOS, *STRANGER_NAMES) + tuple(
              t for n in (HIS_NAME,) + STRANGER_NAMES for t in n.split())


def _photo_url(asset: str) -> str:
    return "https://media.licdn.com/dms/image/v2/%s/profile-displayphoto-shrink_100_100/0/1" % asset


def _vector(asset: str) -> dict:
    return {"rootUrl": "https://media.licdn.com/dms/image/v2/%s/" % asset,
            "artifacts": [{"fileIdentifyingUrlPathSegment":
                           "profile-displayphoto-shrink_100_100/0/1?e=1"}]}


HIS_ENTITY = {
    "$type": "com.linkedin.voyager.dash.identity.profile.Profile",
    "entityUrn": "urn:li:fsd_profile:" + HIS_TOKEN,
    "objectUrn": "urn:li:member:" + HIS_NUMERIC,
    "publicIdentifier": HIS_SLUG,
    "firstName": HIS_NAME.split()[0],
    "lastName": HIS_NAME.split()[1],
    "profilePicture": {"displayImageReference": {"vectorImage": _vector(HIS_PHOTO)}},
}


def page(body: str = "", included: tuple = ()) -> str:
    """One of his pages: the navigation bar's own photo, a link to himself, a
    payload carrying his own entity, and whatever the test adds."""
    payload = json.dumps({"included": [HIS_ENTITY, *included]})
    return (
        "<html><head><title>LinkedIn</title></head><body>"
        '<header><img class="global-nav__me-photo evi-image" alt="%s" src="%s">'
        '<a href="/in/me/">Me</a><a href="https://www.linkedin.com/in/%s/">View profile</a>'
        "</header><main>%s</main>"
        '<code style="display: none" id="bpr-guid-1">%s</code>'
        "</body></html>" % (HIS_NAME, _photo_url(HIS_PHOTO), HIS_SLUG, body, payload)
    )


def judge(html: str, **kw) -> pg.Verdict:
    kw.setdefault("slug", HIS_SLUG)
    kw.setdefault("page_url", JOBS_URL)
    return pg.judge(html, **kw)


def v1_keeps(html: str, slug: str = HIS_SLUG) -> bool:
    """v1, session 11's MEMBER_LINKS_JS, on the string: keep at zero /in/ links
    that are neither /in/me/ nor his own."""
    seen = {m.group(1).lower() for m in re.finditer(
        r'href="(?:https://www\.linkedin\.com)?/in/([^/?#"]+)', html)}
    return not (seen - {"me", slug})


def fired(verdict: pg.Verdict) -> set:
    return {rule for rule, n in verdict.counts.items() if n}


def assert_names_nothing(verdict: pg.Verdict) -> None:
    printed = " | ".join([str(verdict), repr(verdict), verdict.own, *verdict.reasons,
                          *map(str, verdict.counts)])
    for value in VALUES:
        assert value not in printed, "the verdict printed a value from the page"


# --- the two pages that broke v1, rebuilt from their measured shapes ------------

def events_page() -> str:
    """company_events' SHAPES (rawsweep26, 14:05): an Ember page with 0 /in/
    links; two members by urn, photo and picture label; social-proof lines in
    the text and in the payload; an event entity."""
    strangers = [{
        "$type": "com.linkedin.voyager.dash.identity.profile.Profile",
        "entityUrn": "urn:li:fsd_profile:" + token,
        "profilePicture": {"displayImageReference": {"vectorImage": _vector(photo)}},
    } for token, photo in zip(STRANGER_TOKENS, STRANGER_PHOTOS)]
    pictures = [{"$type": "com.linkedin.voyager.dash.common.image.PhotoFilterPicture",
                 "a11yText": name} for name in STRANGER_NAMES]
    social = [{"$type": "com.linkedin.voyager.dash.feed.TextViewModel",
               "text": "%s & 5 other connections work here" % STRANGER_NAMES[1].split()[0]}]
    event = [{"$type": "com.linkedin.voyager.dash.events.ProfessionalEvent",
              "name": "An example event", "description": {"text": "Speakers to be announced"}}]
    body = ('<div class="ember-view"><h2>Upcoming events</h2>'
            '<span>%s and 12 others interested</span></div>' % STRANGER_NAMES[0])
    return page(body, tuple(strangers + pictures + social + event))


def name_list_page() -> str:
    """The unfollowed list's SHAPE: names in profile-card name elements, with
    no profile link and no member urn."""
    rows = "".join('<li><div data-test-profile-card-name="">%s</div>'
                   '<button>Follow</button></li>' % n for n in STRANGER_NAMES)
    return page("<ul>%s</ul>" % rows)


def test_RED_FIRST_v1_keeps_both_pages_that_held_people():
    assert v1_keeps(events_page()) and v1_keeps(name_list_page())


def test_v2_withholds_the_events_page_and_names_every_rule_that_fired():
    verdict = judge(events_page(), page_url=EVENTS_URL, page_key="company_events")
    assert verdict.word == pg.WITHHOLD and not verdict.keep_raw
    assert {"R1", "R2", "R3", "R4", "R5"} <= fired(verdict), verdict.counts
    assert verdict.counts["R1"] == 2 and verdict.counts["R2"] == 2 and verdict.counts["R3"] == 2
    assert verdict.counts["R4"] == 2, verdict.counts
    assert "by its address and by its payload" in str(verdict)
    assert_names_nothing(verdict)


def test_v2_withholds_the_name_list_page_on_its_name_slots():
    verdict = judge(name_list_page())
    assert fired(verdict) == {"N1"} and verdict.counts["N1"] == 2, verdict.counts
    assert_names_nothing(verdict)


def test_THIS_CONTROL_CAN_PASS_his_own_page_is_kept():
    verdict = judge(page("<section><h1>%s</h1><p>Software engineer</p></section>" % HIS_NAME))
    assert verdict.word == pg.KEEP and verdict.keep_raw and fired(verdict) == set(), verdict
    assert verdict.own == "Own(slug=set, member_ids=2, photo_ids=1, names=1)"
    assert_names_nothing(verdict)


# --- each rule, planted alone, and its twin carrying his own value --------------

PLANTS = {
    # rule: (planted page, his-value twin)
    "R1": (page('<div data-x="urn:li:fsd_profile:%s"></div>' % STRANGER_TOKENS[0]),
           page('<div data-x="urn:li:fsd_profile:%s"></div>' % HIS_TOKEN)),
    "R1-encoded": (page('<a href="/feed/?u=urn%%3Ali%%3Afsd_profile%%3A%s">x</a>' % STRANGER_TOKENS[0]),
                   page('<a href="/feed/?u=urn%%3Ali%%3Afsd_profile%%3A%s">x</a>' % HIS_TOKEN)),
    "R1-bare-token": (page('<div data-entity="%s"></div>' % STRANGER_TOKENS[1]),
                      page('<div data-entity="%s"></div>' % HIS_TOKEN)),
    "R1-numeric": (page("", ({"actor": "urn:li:member:12345"},)),
                   page("", ({"actor": "urn:li:member:" + HIS_NUMERIC},))),
    "R2-img": (page('<img src="%s" alt="">' % _photo_url(STRANGER_PHOTOS[0])),
               page('<img src="%s" alt="">' % _photo_url(HIS_PHOTO))),
    "R2-payload": (page("", ({"image": {"vectorImage": _vector(STRANGER_PHOTOS[1])}},)),
                   page("", ({"image": {"vectorImage": _vector(HIS_PHOTO)}},))),
    "R3": (page("", ({"$type": "x.PhotoFilterPicture", "a11yText": STRANGER_NAMES[0]},)),
           page("", ({"$type": "x.PhotoFilterPicture", "a11yText": HIS_NAME},))),
    "R4-and-n-others": (page("<span>%s and 12 others interested</span>" % STRANGER_NAMES[0]),
                        page("<span>%s and 12 others interested</span>" % HIS_NAME)),
    "R4-connections-work-here": (
        page("<span>%s &amp; 5 other connections work here</span>" % STRANGER_NAMES[1].split()[0]),
        page("<span>Xxxxxx &amp; 5 other connections work here</span>")),
    "R4-works-here": (page("<p>%s works here</p>" % STRANGER_NAMES[0]),
                      page("<p>%s works here</p>" % HIS_NAME)),
    "R4-is-hiring": (page('<div aria-label="%s is hiring"></div>' % STRANGER_NAMES[1]),
                     page('<div aria-label="%s is hiring"></div>' % HIS_NAME)),
    "R4-in-a-payload": (page("", ({"text": "%s and 3 others interested" % STRANGER_NAMES[0]},)),
                        page("", ({"text": "%s and 3 others interested" % HIS_NAME},))),
    "L1": (page('<a href="/in/%s/">x</a>' % STRANGER_SLUG),
           page('<a href="/in/%s/?miniProfile=1">x</a>' % HIS_SLUG)),
    "N1-member-link": (page('<a href="/in/me/"><span>%s</span></a>'
                            '<div data-test-profile-card-name="">%s</div>' % (HIS_NAME, STRANGER_NAMES[0])),
                       page('<div data-test-profile-card-name="">%s</div>' % HIS_NAME)),
}


@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_each_rule_convicts_its_plant_and_passes_his_own_value(plant):
    rule = plant.split("-")[0]
    planted, twin = PLANTS[plant]
    verdict = judge(planted)
    assert rule in fired(verdict) and not verdict.keep_raw, (plant, verdict.counts)
    assert any(r.startswith(rule + " ") for r in verdict.reasons), verdict.reasons
    assert_names_nothing(verdict)
    clean = judge(twin)
    assert clean.keep_raw and fired(clean) == set(), (plant, clean.counts)


def test_the_guards_own_slot_reader_counts_a_member_link_name():
    """N1 READS THE SHIPPED INSTRUMENT: the fixture guard's member-link slot,
    imported. The link fires L1 too; the slot is what N1 counts."""
    verdict = judge(page('<a href="/in/%s/"><span>%s</span></a>' % (STRANGER_SLUG, STRANGER_NAMES[0])))
    assert verdict.counts["N1"] == 1 and verdict.counts["L1"] == 1, verdict.counts


@pytest.mark.parametrize("quiet", [
    "<p>Your connection and 3 others follow this page</p>",
    "<p>3 connections work here</p>",
    "<p>Example Org Technologies is hiring</p>",
    '<a href="/company/1/"><img alt="Brindlecore logo" src="y"></a><p>Brindlecore is hiring</p>',
    "<p>Date posted</p><span class=\"visually-hidden\">Status is online</span>",
    '<div data-test-profile-card-name="">Xxxxxx Xxxxxxxx</div>',
    '<img src="https://media.licdn.com/dms/image/v2/D4E0BAQEXAMPLELOGO1/company-logo_100_100/0/1">',
])
def test_interface_text_organisations_and_shaped_names_stay_quiet(quiet):
    verdict = judge(page(quiet))
    assert verdict.keep_raw, (quiet, verdict.counts)


@pytest.mark.parametrize("url,key", [
    (EVENTS_URL, ""),
    ("https://www.linkedin.com/events/7400000000000000001/", ""),
    ("https://www.linkedin.com/search/results/events/?keywords=example", ""),
    (JOBS_URL, "company_events"),
])
def test_R5_an_events_page_is_skeleton_only_by_its_class(url, key):
    verdict = judge(page(), page_url=url, page_key=key)
    assert fired(verdict) == {"R5"} and "by its address" in str(verdict), verdict


def test_R5_an_event_entity_in_the_payload_withholds_too():
    verdict = judge(page("", ({"$type": "com.linkedin.voyager.dash.events.ProfessionalEvent"},)))
    assert fired(verdict) == {"R5"} and "by its payload" in str(verdict), verdict


def test_R6_the_verdict_covers_only_the_string_it_judged():
    html = page()
    verdict = judge(html)
    assert verdict.keep_raw and verdict.covers(html)
    late = html.replace("</main>", '<a href="/in/%s/">x</a></main>' % STRANGER_SLUG)
    assert not verdict.covers(late), "a string that changed after the verdict is not covered"
    assert not judge(late).keep_raw


def test_without_his_slug_his_own_ids_are_not_his_and_the_page_withholds():
    """FAIL CLOSED: an identity the gate cannot establish is nobody's."""
    verdict = judge(page(), slug="")
    assert not verdict.keep_raw and "R1" in fired(verdict), verdict.counts
    assert verdict.own.startswith("Own(slug=absent")


def test_an_unreadable_slot_reader_withholds(monkeypatch):
    monkeypatch.setitem(sys.modules, "tests.test_fixtures_hold_only_synthetic_people", None)
    verdict = judge(page())
    assert not verdict.keep_raw and fired(verdict) == {"N1"}
    assert "could not run" in str(verdict)


def test_the_runner_hand_off_keeps_its_contract():
    """The record's two-line change calls judge(html, slug=, page_url=,
    page_key=) and reads .keep_raw; those must keep existing."""
    params = inspect.signature(pg.judge).parameters
    assert {"slug", "page_url", "page_key"} <= set(params)
    assert all(params[p].kind is inspect.Parameter.KEYWORD_ONLY for p in ("slug", "page_url", "page_key"))
    assert isinstance(pg.Verdict.keep_raw, property)


def test_his_first_name_alone_is_somebody_elses():
    """"<first name> & N other connections work here" names a CONNECTION: his
    first name there is a stranger who shares it, and the raw is withheld."""
    verdict = judge(page("<span>%s &amp; 5 other connections work here</span>"
                         % HIS_NAME.split()[0]))
    assert fired(verdict) == {"R4"}, verdict.counts


@pytest.mark.parametrize("glued,mine", [
    (HIS_TOKEN + "ExperienceTopLevelSection", True),
    (HIS_TOKEN + "AboutSection", True),
    (STRANGER_TOKENS[0] + "ExperienceTopLevelSection", False),
    (HIS_TOKEN + STRANGER_TOKENS[0], False),
])
def test_a_section_name_glued_to_an_id_is_not_part_of_the_id(glued, mine):
    """MEASURED on his own experience page: server-driven component keys glue a
    section name straight onto his id. The id is the first 39 characters; a
    SECOND id glued after it is still found."""
    verdict = judge(page('<div id="com.linkedin.sdui.profile.card.ref%s"></div>' % glued))
    assert verdict.keep_raw is mine, verdict.counts
    assert pg.member_ids_in("ref" + glued) >= {glued[:pg.MEMBER_TOKEN_LENGTH]}


def sdui_page(body: str = "") -> str:
    """A server-driven page as session 11 measured four of them: hashed class
    names, no navigation photo class, no payload; his own avatar drawn."""
    return ('<html><body><nav><img class="ekf1a2 ekf3b4" src="%s" alt=""></nav>'
            "<main>%s</main></body></html>" % (_photo_url(HIS_PHOTO), body))


def test_his_identity_taught_by_one_page_clears_the_next_through_the_cache(tmp_path):
    cache = tmp_path / "people_gate_own.json"
    alone = judge(sdui_page("<p>Jobs for you</p>"))
    assert fired(alone) == {"R2"}, "judged alone, his own avatar is nobody's"
    taught = judge(page(), own_cache=cache)
    assert taught.keep_raw and cache.exists()
    held = cache.read_text(encoding="utf-8")
    for value in VALUES:
        assert value not in held, "the cache holds a value in the clear"
    assert held.count("sha256:") == 1 + 2 + 1 + 1, held   # slug, 2 ids, 1 photo, 1 name
    after = judge(sdui_page("<p>Jobs for you</p>"), own_cache=cache)
    assert after.keep_raw, after.counts
    assert not judge(sdui_page(), slug="someone-placeholder-0009", own_cache=cache).keep_raw
    assert cache.read_text(encoding="utf-8") == held, "a page that taught nothing rewrote it"


def test_without_a_cache_the_gate_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    judge(page())
    judge(events_page(), page_url=EVENTS_URL)
    assert list(tmp_path.iterdir()) == []


def test_the_module_imports_nothing_that_drives_a_browser_and_writes_one_file():
    """A gate decides; the caller writes the page. Its one write is the cache
    path the caller names. Read with ast, not grep."""
    import ast

    tree = ast.parse((REPO / "scripts" / "people_gate.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not imported & {"playwright", "linkedin_server", "asyncio", "subprocess", "os",
                           "shutil", "socket", "urllib3", "requests"}, imported
    where = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and isinstance(n.func, (ast.Name, ast.Attribute)):
                    name = n.func.id if isinstance(n.func, ast.Name) else n.func.attr
                    where.setdefault(name, set()).add(fn.name)
    assert where.get("open", set()) == {"read_own_cache", "write_own_cache"}, where.get("open")
    assert where.get("replace", set()) <= {"write_own_cache", "_as_self_links"}
    for name in ("write_text", "write_bytes", "goto", "evaluate", "content", "unlink", "remove"):
        assert name not in where, name
