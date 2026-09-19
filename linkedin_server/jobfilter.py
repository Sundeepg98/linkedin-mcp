"""The company filter for a job search, and the one thing it must never echo.

``J 10`` -- filter a job search by company -- was filed against
``COMPANY-ID-RESOLVER`` on the reasoning that ``f_C`` needs a numeric Page id
while a posting only yields a slug. **Both halves of that blocker are now
built** and the row is still GAP, because nothing joined them:

* ``/jobs/search/?f_C=<numeric id>`` has been on the read allowlist since the
  first commit -- ``f_C`` is one more query key on a root this server has always
  opened. Measured, not assumed: ``readonly.is_read_url`` returns True for it at
  29 patterns.
* ``shape.company_id_from_insight_cards`` resolves the id, and
  ``linkedin_job_detail`` already returns it as a VERDICT rather than a bare
  value -- state ``resolved`` only when exactly one card agrees.

So this module is the wire, and it is deliberately a separate file: ``server.py``
has been contended by a dozen waves all day, and two documented incidents this
afternoon swept a neighbour's lines into a commit inside
``linkedin_search_jobs`` specifically.

## WHY THE REFUSAL NAMES A SHAPE AND NEVER THE VALUE

This package's standing rule is that a refusal must report **what it SAW**, not
only what it failed to match -- three rounds were lost to "zero matched" before
that was written down.

**This function is the exception that proves it needs care, and the reason is
the failure mode itself.** The overwhelmingly likely wrong value for ``f_C`` is
a company SLUG, because that is exactly what a posting hands you and exactly
what the blocker was named for. A slug is a third-party organisation's name. So
the obvious, rule-following implementation --

    f"company_id must be digits, got {company_id!r}"

-- publishes a third-party name verbatim into a tool result, every time a caller
makes the single most probable mistake. **A rule about naming what you saw and a
rule about never emitting an identifier collide here, and the collision is won
by the identity rule**, which is the one this repository treats as absolute.

The refusal therefore reports the SHAPE: how many characters, and which
character classes were present. That is enough for a caller to know why
``acme-corp`` was refused (it has letters and a hyphen) without this process
ever putting ``acme-corp`` in an output. ``tests/test_company_job_filter.py``
asserts the value does not survive, using an input whose refusal would otherwise
carry it.

**A digits-only value IS echoed**, and that is a deliberate, narrow exception:
once the value is known to be all digits it is a LinkedIn Page id and nothing
else -- it cannot be a name, because a name cannot be digits. The one case that
can carry a name is the one case that is refused.
"""

from __future__ import annotations

from typing import Any

#: LinkedIn's company filter key on ``/jobs/search/``. Named once so the
#: parameter name and the test that pins it cannot drift apart silently.
COMPANY_FILTER_KEY = "f_C"

#: A Page id is digits. The longest real id seen in this repository's fixtures
#: is seven characters; the ceiling here is deliberately loose because an
#: arbitrary cap would refuse a valid id on a guess, and the harm being guarded
#: against is a NAME reaching an output, which a length cap does not address.
_MAX_ID_LEN = 20


def describe_shape(value: str) -> str:
    """Describe a string by its character classes and length. Never its content.

    Factored OUT of the refusal that consumes it, so it has a handle and can be
    aimed at a known-bad sample directly -- logic living inside an ``assert``
    can never be tested against the input it was written for.
    """

    text = str(value or "")
    classes: list[str] = []
    if any(character.isdigit() for character in text):
        classes.append("digits")
    if any(character.isalpha() for character in text):
        classes.append("letters")
    if any(character in "-_" for character in text):
        classes.append("hyphen-or-underscore")
    if any(character.isspace() for character in text):
        classes.append("whitespace")
    if any(
        not character.isalnum() and character not in "-_" and not character.isspace()
        for character in text
    ):
        classes.append("punctuation")
    if not classes:
        classes.append("empty")
    return f"{len(text)} characters, containing {' + '.join(classes)}"


def company_filter_param(company_id: str) -> dict[str, Any]:
    """Turn a company id into an ``f_C`` query parameter, or refuse it.

    Returns a VERDICT and not a bare value, matching the shape
    ``linkedin_job_detail`` already returns for ``company_id`` -- three states,
    each of which a caller must handle differently:

    ``absent``
        nothing was supplied. Not an error: the filter is optional, and this is
        how "no company filter" arrives. ``param`` is None.
    ``resolved``
        the value is a Page id and ``param`` is the pair to append.
    ``refused``
        the value cannot be a Page id. ``param`` is None and ``why`` describes
        the SHAPE that was rejected, never the value -- see the module
        docstring for why that inverts this package's usual refusal rule.
    """

    text = str(company_id or "").strip()

    if not text:
        return {
            "state": "absent",
            "param": None,
            "why": "no company_id was supplied, so no company filter is applied",
        }

    if not text.isdigit():
        return {
            "state": "refused",
            "param": None,
            "why": (
                "company_id must be a numeric LinkedIn Page id; the value "
                f"supplied is {describe_shape(text)}. A company SLUG is not a "
                "Page id -- resolve one with linkedin_job_detail, whose "
                "company_id verdict reads 'resolved' only when exactly one "
                "insight card agrees. The value is described rather than "
                "quoted because a non-numeric value here is most often an "
                "organisation's name."
            ),
        }

    if len(text) > _MAX_ID_LEN:
        return {
            "state": "refused",
            "param": None,
            "why": (
                f"company_id is {len(text)} digits, longer than the {_MAX_ID_LEN} "
                "this accepts; no LinkedIn Page id of that length is known here"
            ),
        }

    return {
        "state": "resolved",
        "param": (COMPANY_FILTER_KEY, text),
        "why": f"a {len(text)}-digit Page id, appended as {COMPANY_FILTER_KEY}",
    }
