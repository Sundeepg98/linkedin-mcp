"""NOTHING HERE REACHES A NETWORK, so it can follow, invite or send nothing.

It builds one string: the embed code LinkedIn documents for its Follow
Company Plugin, which a Page administrator pastes into their own website. No
browser session is opened, no request leaves this process, and no LinkedIn
state is touched in either direction.

## WHY A GENERATOR AND NOT A READER

Census row ``N A6`` -- "Build a Page Follow button for your organization's
website" -- is the ONE row of ``ADMIN-RIGHTS-NOT-HELD``'s fifteen that is not
an act on LinkedIn at all. The other fourteen need an address; this one needs
a template and an id. So it is the only one of the fifteen that can be
delivered with no navigation-allowlist entry, no write grant, and no second
consenting human.

**AND IT IS THE ONE THAT MEASURES THE BOUNDARY IT SITS BEHIND.** The plugin
needs a numeric Company ID, and the cited document names exactly one place to
find it::

    "As a company page administrator, your Company ID can be retrieved by
    navigating to the admin section of your company page. For example, the
    LinkedIn Company Admin Page is https://www.linkedin.com/company/<the
    numeric id>/admin/." -- the document's own example spells that id as
    four zeros.

That address is REFUSED by this package's navigation boundary -- measured
2026-09-20 against the shipped predicate, refused by allowlist silence, no
pattern matching it at all. So the id this module needs is one this server
cannot read, and the caller must supply it by hand. That is not a defect to
be engineered around; it is the honest shape of the row, and
``tests/test_page_plugin.py`` asserts the refusal so the day the address is
admitted, the coupling is re-measured rather than remembered.

## THE OUTPUT ALPHABET IS CLOSED, AND THAT IS THE SAFETY PROPERTY

Copied deliberately from ``groups.py`` and ``menus.py``, including the reason.
Everything this module emits is a literal defined in this file, EXCEPT the id
-- and the id is admitted only as a run of ASCII digits. So:

    THE ONLY CALLER-SUPPLIED BYTES THAT CAN REACH THE OUTPUT ARE THE TEN
    CHARACTERS ``0123456789``.

That is structural rather than filtered. A filter has to keep up with what a
caller passes tomorrow; an alphabet does not. ``test_page_plugin.py`` asserts
it over adversarial input rather than trusting this paragraph.

**A PAGE'S VANITY NAME IS ROUTINELY A PERSON'S NAME, WHICH IS WHY A SLUG IS
REFUSED RATHER THAN SHAPED.** ``readonly.py`` already records the same finding
one surface over, for newsletters: a slug "is ROUTINELY ITS AUTHOR'S NAME".
Personal-brand Pages and one-person consultancies are the ordinary case, not
the adversarial one. The plugin's own contract wants the NUMERIC id, so
refusing the slug costs the caller nothing and closes the hole by
construction.

**AND ``str.isdigit()`` IS NOT THE TEN CHARACTERS.** It is True for
Arabic-Indic, Extended Arabic-Indic and superscript runs -- ``groups.py``
measured three scripts, all True, with ``int()`` unable to parse the
superscript form. A membership test against a literal frozenset cannot widen
behind anybody's back, so that is what is used here.

## A REFUSAL REPORTS WHAT IT SAW, NOT ONLY WHAT IT DID NOT MATCH

The rule is ``groups.group_identifier``'s and ``menus.py``'s, inherited rather
than restated: a refusal that reports only the miss is half a measurement.
:func:`page_identifier` returns SHAPE FACTS about the rejected input -- a
coarse length band, whether it held ASCII digits, whether it held digits from
some OTHER script, whether it held a hyphen or a space -- which is what
separates "the caller pasted a slug" from "the caller pasted a url" from "the
caller pasted an id with a stray space".

**THE SHAPE FACTS ARE LOSSY ON PURPOSE AND THERE IS NO DIGEST.** Length is
BANDED, never exact. A hash would be a lookup table over a small domain
wearing a redaction's clothes; ``groups.py`` rejected exactly that for group
identifiers and the reasoning transfers without change.

## WHAT IS VERBATIM FROM THE DOCUMENT, AND WHAT IS NOT OFFERED

Every literal below is quoted from the cited document. What that document does
NOT enumerate is not offered here:

* it shows ``data-counter="bottom"`` and no other value, so no other value is
  a parameter of anything in this module;
* it shows ``lang: en_US`` and no other, likewise.

Shipping ``top`` or ``right`` because sibling plugins use them would be
inference wearing a measurement's clothes. When somebody measures another
value, they add it here with what they measured.

## THE DOCUMENT'S AGE IS PART OF THE PAYLOAD, NOT A FOOTNOTE

:data:`SOURCE_DOC_UPDATED` travels in every answer. The contract is quoted
from a page whose own metadata says it was authored 2019-02-27 and last
updated 2022-03-31, and **no live verification was performed** -- this wave
opened no browser by instruction. A caller who pastes this into a production
site is relying on a four-year-old document, and the honest thing is to say so
in the payload rather than in a comment nobody reads.

**SUBRESOURCE INTEGRITY WAS CONSIDERED AND DELIBERATELY NOT ADDED.** The
obvious hardening is an ``integrity=`` attribute on the script tag. It is
refused because this module's whole contract is *reproduce LinkedIn's
documented snippet*: the document specifies no digest, LinkedIn re-publishes
that script at will, and a pinned digest would break the widget silently the
first time they did. A generator that improves on the contract it claims to
reproduce is not safer, it is wrong in a way the caller cannot see. The risk
is real and belongs in the payload, which is what :data:`ADVISORY` is for.

## WHAT THIS MODULE IS NOT

* It is **not** a Page reader. It learns nothing about the Page and cannot
  check that the id names one.
* It **does not open a page**, and contains no code that could.
* It makes **no claim that the plugin still works.** It reproduces a
  documented contract and says how old the document is.
"""
from __future__ import annotations

from typing import Any, Optional

#: VERBATIM from the cited document's sample request. Each of these is a
#: literal that document prints, not a value this package chose.
PLUGIN_SCRIPT_SRC = "https://platform.linkedin.com/in.js"
PLUGIN_SCRIPT_TYPE = "text/javascript"
PLUGIN_TYPE = "IN/FollowCompany"

#: The ONE counter position the document shows, and therefore the only one
#: this module knows. See the module docstring on why no sibling value is
#: offered.
PLUGIN_COUNTER = "bottom"

#: The ONE language token the document shows.
PLUGIN_LANG = "en_US"

#: WHERE THE CONTRACT COMES FROM, and how old it is. Both travel in the
#: payload; see the module docstring.
SOURCE_DOC = (
    "https://learn.microsoft.com/en-us/linkedin/consumer/integrations"
    "/self-serve/plugins/follow-company-plugin"
)
SOURCE_DOC_AUTHORED = "2019-02-27"
SOURCE_DOC_UPDATED = "2022-03-31"

#: The document closes by binding the reader to these terms. It is reproduced
#: because a generator that hands somebody a snippet without the licence it
#: arrives under has quietly dropped half the contract.
TERMS_OF_USE = "https://developer.linkedin.com/legal/plugin-terms-of-use"

#: What a caller is taking on, stated where they meet it. Not a warning about
#: this module -- a fact about the artefact it hands over.
ADVISORY = (
    "this snippet loads a third-party script at runtime and carries no "
    "subresource integrity digest, because the cited document specifies "
    "none; the contract is reproduced rather than improved on"
)

#: THE TEN ASCII DIGITS, WRITTEN OUT, because ``str.isdigit()`` is not this.
#: Same constant and same reason as ``groups._ASCII_DIGITS``.
_ASCII_DIGITS = frozenset("0123456789")

#: Bounded above because an unbounded repetition on caller-shaped input is a
#: cost nobody chose. Twenty is ``groups._MAX_IDENTIFIER_DIGITS``'s number,
#: reused rather than invented, and is far above any Company ID observed.
_MAX_ID_DIGITS = 20

#: THE CLOSED SET OF REFUSAL TERMS. Every string :func:`page_identifier` can
#: put in ``refused`` is one of these literals. A caller can branch on them;
#: none of them is derived from the input.
REFUSALS = (
    "empty",
    "not_ascii_digits",
    "too_long",
)

#: The coarse length bands a refusal reports instead of an exact length. An
#: exact length over a known vocabulary is itself an identifier.
_LENGTH_BANDS = ((0, "empty"), (8, "1-8"), (20, "9-20"), (64, "21-64"))
_LENGTH_BAND_OVER = "over-64"


def _length_band(n: int) -> str:
    """A coarse band, never the exact length. See the module docstring."""
    for upper, label in _LENGTH_BANDS:
        if n <= upper:
            return label
    return _LENGTH_BAND_OVER


def _shape_facts(raw: str) -> dict[str, Any]:
    """WHAT WAS SEEN, in this module's own vocabulary and never the value.

    Every value in the returned mapping is a bool, an int, or one of
    :data:`_LENGTH_BANDS`' own labels. No substring of ``raw`` is returned,
    and no digest of it either.
    """
    non_ascii_digits = sum(
        1 for ch in raw if ch.isdigit() and ch not in _ASCII_DIGITS
    )
    return {
        "length_band": _length_band(len(raw)),
        "ascii_digits": sum(1 for ch in raw if ch in _ASCII_DIGITS),
        # THE TRAP, REPORTED RATHER THAN ONLY REFUSED. A caller who pasted a
        # run of Arabic-Indic digits sees WHY it was refused instead of
        # concluding this module cannot count.
        "digits_from_another_script": non_ascii_digits,
        "letters": sum(1 for ch in raw if ch.isalpha()),
        "hyphens": raw.count("-"),
        "slashes": raw.count("/"),
        "spaces": sum(1 for ch in raw if ch.isspace()),
        "looks_like_a_url": "//" in raw,
        "all_ascii": all(ord(ch) < 128 for ch in raw),
    }


def page_identifier(raw: Optional[str]) -> dict[str, Any]:
    """Admit a Company ID, or refuse it and say what was seen.

    Returns ``{"id": <str of ASCII digits>, "refused": None, "saw": {...}}``
    on admission, and ``{"id": None, "refused": <a REFUSALS term>,
    "saw": {...}}`` otherwise.

    **THE VALUE NEVER COMES BACK ON A REFUSAL.** ``saw`` holds shape facts in
    this module's own vocabulary; a rejected slug is a person's name often
    enough that echoing it back in an error is the whole hazard.

    Surrounding whitespace is stripped before the test, and nothing else is.
    A caller who pastes an id with a trailing newline meant the id; a caller
    who pastes a url did not, and gets ``looks_like_a_url``.
    """
    text = "" if raw is None else str(raw).strip()
    saw = _shape_facts(text)
    if not text:
        return {"id": None, "refused": "empty", "saw": saw}
    # ORDER MATTERS AND IS DELIBERATE: alphabet before length. A 400-character
    # slug should be refused for being a slug, which is the fact its author
    # needs, not for being long.
    if any(ch not in _ASCII_DIGITS for ch in text):
        return {"id": None, "refused": "not_ascii_digits", "saw": saw}
    if len(text) > _MAX_ID_DIGITS:
        return {"id": None, "refused": "too_long", "saw": saw}
    return {"id": text, "refused": None, "saw": saw}


def follow_plugin_snippet(page_id: Optional[str]) -> dict[str, Any]:
    """Build the documented embed code, or return the refusal unchanged.

    On admission the payload carries ``html`` -- two script tags, the second
    holding the id -- plus the provenance of the contract it reproduces. On
    refusal it carries ``html: None`` and :func:`page_identifier`'s verdict,
    so a caller branches on one shape either way.
    """
    verdict = page_identifier(page_id)
    provenance = {
        "source_doc": SOURCE_DOC,
        "source_doc_authored": SOURCE_DOC_AUTHORED,
        "source_doc_updated": SOURCE_DOC_UPDATED,
        "terms_of_use": TERMS_OF_USE,
        "advisory": ADVISORY,
        # STATED IN THE PAYLOAD BECAUSE IT IS THE HONEST STATE OF THIS ROW.
        # The contract is quoted from a document; nothing in this package has
        # seen the plugin render.
        "verified_live": False,
    }
    if verdict["refused"] is not None:
        return {"html": None, **verdict, **provenance}
    return {
        "html": (
            '<script src="%s" type="%s"> lang: %s</script>\n'
            '<script type="%s" data-id="%s" data-counter="%s"></script>'
            % (
                PLUGIN_SCRIPT_SRC,
                PLUGIN_SCRIPT_TYPE,
                PLUGIN_LANG,
                PLUGIN_TYPE,
                verdict["id"],
                PLUGIN_COUNTER,
            )
        ),
        **verdict,
        **provenance,
    }
