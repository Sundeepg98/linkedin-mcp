"""'I'm interested': privately signalling interest in one employer (census ``P I14``).

## WHAT THE ACT IS, AND WHO SEES IT

LinkedIn draws an "I'm interested" control in the About-the-company card of a
job posting, under the heading "Interested in working with us in the future?"
and beside a link to its own Help article ``a1380509``. Pressing it tells THAT
EMPLOYER'S RECRUITERS he is interested in working there. It is not a post and
it notifies nobody in his network, but it is not private to him either: the
people it is FOR are other people, which is why the ruling
``OPERATOR-NAMES-THE-TARGET`` governs its live proof -- the operator names the
posting, never this package or an agent.

## WHAT IS MEASURED, AND WHERE

The OFF control is in THREE tracked captures of a posting
(``tests/fixtures/job_detail.html``, ``job_detail_hydrated.html`` and
``job_detail_following_hydrated.html``): a plain ``<button>`` whose only name
is its own text, ``I'm interested`` with LinkedIn's typographic apostrophe
(U+2019, ``shape.APOSTROPHE``), inside ``div[componentkey^=
"JobDetails_AboutTheCompany"]``. ``linkedin_job_detail`` already reports that
the card draws it (``interest_control``); nothing ever pressed it.

## WHAT IS NOT MEASURED, AND WHICH WAY EACH GAP FAILS

* **The ON label.** Every capture was of an employer he had not signalled, so
  the control an already-signalled interest wears has never been seen. A card
  whose interest section draws a control that is NOT the OFF label therefore
  reads UNKNOWN and is REFUSED -- never reported as signalled, never pressed.
* **Whether one press completes the act.** LinkedIn may ask for more (a
  confirmation, a choice of job categories). The verification is a fresh
  render of the posting: the OFF label still drawn there means the interest
  was NOT signalled, and the write says ``performed: false`` rather than
  hoping. The first supervised press is the measurement of the second step.
* **The undo.** ``P I15`` (remove the interest) needs the ON label this
  action's first live proof will draw; it is not built.

## THE ANCHOR, READ ON THE PAGE

Identity comes from the card and not from the control: the control's name
carries no company, so the card must open by naming the POSTING'S OWN
EMPLOYER -- ``shape.company_about_card``'s ``unnamed`` rule, the same rule
``linkedin_job_detail`` applies -- and exactly ONE control in that card may
wear the OFF label. Nothing here returns page text: the reader returns counts,
and every ``why`` is built from counts and constants.
"""
from __future__ import annotations

from typing import Any

from linkedin_server import coerce, dom, shape

#: The OFF label, with LinkedIn's own apostrophe. Built from the code point so
#: this file stays ASCII.
OFF_LABEL: str = "I" + shape.APOSTROPHE + "m interested"

#: The card the control lives in -- the same container ``linkedin_job_detail``
#: and ``follow_company`` read.
CARD: str = dom.ABOUT_COMPANY_CONTAINER

#: LinkedIn's own Help article for this feature, linked from the section's
#: heading on every capture. An ADDRESS, used as the section's structural
#: marker so no page text is read to find it.
HELP_ARTICLE_FRAGMENT: str = "/answer/a1380509"

#: The OFF control inside the card: a button named EXACTLY the OFF label. The
#: ``s`` suffix is Playwright's case-sensitive whole-name match. This is the
#: click selector too, and strict mode holds the click to one element.
OFF_CONTROL_IN_CARD: str = (
    "css=" + CARD + ' >> role=button[name="' + OFF_LABEL + '"s]'
)

#: The same label anywhere on the page. A FACT reported beside the verdict,
#: never an aim.
OFF_CONTROL_ANYWHERE: str = 'role=button[name="' + OFF_LABEL + '"s]'

#: The interest section's marker inside the card, and every button in the
#: section's own block. An ON-state control, if LinkedIn draws one, is one of
#: these.
#:
#: THE BLOCK IS BOUNDED, and the first version was not. It took "the nearest
#: ancestor of the Help link that holds a button", and when the section drew
#: no button at all that climb kept going -- to the card, whose Follow control
#: and 'more' toggle it then counted as the section's. Its own test caught it:
#: a card with the interest control removed read "the section draws 2
#: controls", which at the verification would have read as a control that
#: MOVED. Now the block is the innermost ``div[componentkey]`` INSIDE the card
#: that holds the Help link -- the shape all three tracked captures draw -- so
#: a missing control counts zero, and a block LinkedIn stops keying counts zero
#: too, which fails towards "unknown".
SECTION_MARKER_IN_CARD: str = (
    "css=" + CARD + ' a[href*="' + HELP_ARTICLE_FRAGMENT + '"]'
)
_HOLDS_HELP_LINK: str = '[.//a[contains(@href, "' + HELP_ARTICLE_FRAGMENT + '")]]'
SECTION_BUTTONS_IN_CARD: str = (
    "css=" + CARD
    + " >> xpath=.//div[@componentkey]" + _HOLDS_HELP_LINK
    + "[not(.//div[@componentkey]" + _HOLDS_HELP_LINK + ")]//button"
)

#: The two states this action knows. The OFF state is measured; the ON state
#: is the state it moves TO, never one it claims to read at preview.
NOT_SIGNALLED: str = "not_signalled"
SIGNALLED: str = "interest_signalled"
UNKNOWN: str = "unknown"


async def read_interest_control(page: Any) -> dict[str, Any]:
    """COUNTS ONLY, off the posting already open. Never raises.

    ``error`` is an exception TYPE name, never its message: a Playwright
    message can quote a selector and, through it, page content.
    """
    out: dict[str, Any] = {
        "card": 0,
        "section": 0,
        "section_buttons": 0,
        "off_in_card": 0,
        "off_anywhere": 0,
        "error": None,
    }
    try:
        out["card"] = coerce.as_count(await page.locator(CARD).count())
        out["section"] = coerce.as_count(
            await page.locator(SECTION_MARKER_IN_CARD).count()
        )
        out["section_buttons"] = coerce.as_count(
            await page.locator(SECTION_BUTTONS_IN_CARD).count()
        )
        out["off_in_card"] = coerce.as_count(
            await page.locator(OFF_CONTROL_IN_CARD).count()
        )
        out["off_anywhere"] = coerce.as_count(
            await page.locator(OFF_CONTROL_ANYWHERE).count()
        )
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


#: The card states ``shape.company_about_card`` returns that establish nothing
#: about WHOSE card this is. ``partial`` and ``read`` both mean the card opened
#: by naming the posting's employer.
_UNATTRIBUTED_CARD_STATES: frozenset[str] = frozenset({"absent", "unhydrated", "unnamed"})


def interest_verdict(
    card: dict[str, Any], reading: dict[str, Any], *, company: Any
) -> tuple[dict[str, Any], str, str]:
    """``(facts, state, why)`` for one posting's interest control.

    ``card`` is ``shape.company_about_card(...)`` for the posting's own
    employer; ``reading`` is :func:`read_interest_control`. The states:

        not_signalled   the card is the employer's, and exactly one control in
                        it wears the OFF label
        unknown         everything else -- and the why says which, in counts

    ``interest_signalled`` is NEVER returned here. It is the destination, and
    the label that would mean it has never been captured.
    """
    facts: dict[str, Any] = {
        "company": company,
        "card": str((card or {}).get("state") or "absent"),
        "off_controls_in_card": coerce.as_count((reading or {}).get("off_in_card")),
        "off_controls_on_page": coerce.as_count((reading or {}).get("off_anywhere")),
        "section_controls": coerce.as_count((reading or {}).get("section_buttons")),
    }
    if (reading or {}).get("error"):
        return (
            facts,
            UNKNOWN,
            "the interest control could not be read "
            f"({str(reading.get('error'))[:64]}), so nothing is known about its "
            "state. Refused rather than guessed.",
        )
    if facts["card"] in _UNATTRIBUTED_CARD_STATES:
        return (
            facts,
            UNKNOWN,
            f"the About-the-company card reads {facts['card']!r}: it was not "
            "drawn, not yet filled in, or does not open by naming this "
            "posting's employer. A signal pressed on a card nobody can "
            "attribute could reach a different company's recruiters, so this "
            "is refused.",
        )
    off = facts["off_controls_in_card"]
    if off > 1:
        return (
            facts,
            UNKNOWN,
            f"{off} controls in this employer's card wear the OFF label, where "
            "exactly one is required. Pressing one of several would be "
            "pressing by position.",
        )
    if off == 1:
        return (
            facts,
            NOT_SIGNALLED,
            "exactly one control in this employer's card wears the OFF label "
            "LinkedIn draws before an interest is signalled, and the card opens "
            "by naming the posting's own employer.",
        )
    if facts["section_controls"] > 0:
        return (
            facts,
            UNKNOWN,
            f"the card's interest section draws {facts['section_controls']} "
            "control(s) and none wears the OFF label. That is the shape an "
            "ALREADY-SIGNALLED interest would take -- and the label LinkedIn "
            "draws then has never been captured, so this server cannot "
            "recognise it. Refused, never reported as signalled.",
        )
    return (
        facts,
        UNKNOWN,
        "this employer's card draws no interest control at all. LinkedIn does "
        "not draw the section on every posting, and a card still filling in "
        "looks the same; either way there is nothing to press.",
    )


async def read_state(page: Any, *, company: Any) -> tuple[dict[str, Any], str, str]:
    """The preview's and the click's reading, off the posting already open.

    ``company`` is the employer the posting itself names (``writes``' posting
    facts); the card must open by naming it. One call to the shipped card
    reader, one to :func:`read_interest_control`, and the verdict.
    """
    observation = await dom.read_company_about_card(page)
    card = shape.company_about_card(observation, company=company)
    reading = await read_interest_control(page)
    return interest_verdict(card, reading, company=company)


#: Visible dialogs on the page, for the after-press measurement. Role
#: selectors skip hidden elements, so a dialog template left in the markup
#: does not count.
_VISIBLE_DIALOGS: str = "role=dialog"


async def read_after_press(page: Any) -> dict[str, Any]:
    """What the press left on the page, BEFORE the verification navigates.

    COUNTS ONLY: the card's OFF controls, its section's controls, and visible
    dialogs. It decides nothing -- the fresh render does -- but it is the one
    reading that can say a further step OPENED (a dialog appeared) rather than
    merely that the interest did not land. That is the measurement a first
    supervised press exists to take.
    """
    out = await read_interest_control(page)
    try:
        out["dialogs"] = coerce.as_count(await page.locator(_VISIBLE_DIALOGS).count())
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["dialogs"] = None
        out["error"] = out.get("error") or type(exc).__name__
    return out


def verification_verdict(reading: dict[str, Any], card: dict[str, Any]) -> tuple[str, str]:
    """``(state, why)`` after the press, off a FRESH render of the posting.

    THE NEGATIVE IS THE STRONG ANSWER. The OFF label still drawn in the
    employer's card means the interest was not signalled -- whatever the
    press did, including opening a step this server did not take. The
    positive is weaker and said so: the OFF label GONE while the section still
    draws a control means the control moved, which is what a signal does and
    what nothing else here explains; what it moved TO is recorded as a count,
    because the ON label has never been captured.
    """
    if (reading or {}).get("error"):
        return (UNKNOWN, "the posting's interest control could not be re-read after the press.")
    if str((card or {}).get("state") or "absent") in _UNATTRIBUTED_CARD_STATES:
        return (
            UNKNOWN,
            "on the fresh render the About-the-company card could not be "
            "attributed to this posting's employer, so the control there says "
            "nothing about this signal.",
        )
    off = coerce.as_count(reading.get("off_in_card"))
    section = coerce.as_count(reading.get("section_buttons"))
    if off == 1:
        return (
            NOT_SIGNALLED,
            "the employer's card still draws its OFF control on a fresh render, "
            "so the interest was NOT signalled. If the press opened a further "
            "step, that step was not taken, and the navigation discarded it.",
        )
    if off == 0 and section > 0:
        return (
            SIGNALLED,
            f"the OFF control is gone from the employer's card on a fresh render "
            f"and the interest section still draws {section} control(s): the "
            "control MOVED. What it moved to is not named here -- that label has "
            "never been captured, and recording it is what this first press is "
            "for.",
        )
    return (
        UNKNOWN,
        f"the fresh render drew {off} OFF control(s) and {section} section "
        "control(s) in the employer's card, which is neither the state this "
        "write started from nor a moved control.",
    )
