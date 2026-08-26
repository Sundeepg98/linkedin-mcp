"""A session the SERVER owns, so Chrome cannot throw it away.

WHY THIS EXISTS, and it is a measured failure rather than a precaution.

The operator had to sign in to LinkedIn again and again while his Naukri and
Instahyre sessions survived for days across restarts. Measured 2026-08-25:

    linkedin/_state/chrome-profile/Last Version   151.0.7922.34
    naukri/chrome-profile/Last Version            145.0.7632.6
    playwright chromium builds installed          1208, 1223, 1228, 1234

His OWN Chrome 151 opened the LinkedIn profile at some point and stamped it.
Playwright's chromium is older, so every launch since reads that stamp as a
DOWNGRADE, runs ``downgrade_utils.cc``, moves the profile aside into a
``.CHROME_DELETE`` directory and starts clean -- taking the cookies with it.
That is the ``exitCode=33`` that killed launch after launch, and it is why the
sign-in never survived. Naukri's profile carries playwright's own stamp, so it
never runs that path, which is the whole of the difference between the two.

THE POINT IS THAT NOTHING OWNED THE SESSION. It lived inside the Chrome
profile, so Chrome decided its lifetime, and Chrome decided to discard it.
Instahyre does not have this problem because its session lives in a file its
own server writes -- six days across multiple restarts, measured -- and the
profile is only a place to re-harvest FROM.

WHAT THIS MODULE IS, AND WHAT IT DELIBERATELY IS NOT.

It is ADDITIVE. The Chrome profile stays exactly as it is and stays the
primary source: nothing here deletes it, moves it, or writes into it. This
adds a SECOND copy of the cookies, in a file this server owns, and puts them
back only when the profile has lost them.

RESTORE IS CONDITIONAL, and that condition matters. Cookies are injected only
when the live context has NO session cookie -- never over a working one. A
profile that still holds a good session is the fresher source, and clobbering
it with an older saved jar would turn this from a safety net into a way to
resurrect a stale session.

FAILURE IS ALWAYS DOWNGRADE, NEVER ERROR. A missing file, a truncated file,
unreadable JSON, a jar with no session cookie -- every one of them returns
"nothing restored" and leaves the server behaving exactly as it did before
this module existed. This is a net beneath the current behaviour and it may
never become a new way to fail.

COOKIE VALUES ARE NEVER LOGGED OR RETURNED. Names, counts and timestamps only.
The file is written with owner-only permissions where the platform supports
it, exactly as the sibling server does.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

from linkedin_server.config import CHROME_PROFILE, logger

#: The session cookie whose presence means "signed in". Same name auth.py
#: uses; imported there rather than duplicated as a literal.
SESSION_COOKIE = "li_at"

#: Beside the profile, not inside it. Inside would put the one artifact that
#: survives a profile reset INTO the thing that gets reset.
SESSION_PATH = Path(CHROME_PROFILE).parent / "session.json"

#: Older than this and a saved jar is not offered for restore. LinkedIn's own
#: li_at runs far longer, so this is not an expiry -- it is a guard against
#: resurrecting a jar from a machine state nobody remembers.
MAX_AGE_S = 60 * 60 * 24 * 30

#: Older than this and a saved jar is REPLACED by a live harvest, rather than
#: left alone as a good store. Derived from MAX_AGE_S, never typed as its own
#: number, because the whole point is a fixed relationship between the two.
#:
#: IT MUST BE STRICTLY SHORTER THAN MAX_AGE_S, and that is the defect this
#: constant exists to close. The re-arm errand used to skip any store that was
#: present and held a session cookie, full stop -- so a jar became eligible for
#: replacement only once it was ALREADY past the restore ceiling. Both rules
#: were individually right and together they were a deadlock: too old to
#: restore, too present to replace. Worse, a re-arm needs a LIVE session to
#: harvest from, and the disaster this store exists for -- Chrome discarding
#: the profile -- is exactly the thing that takes the live session away. Waiting
#: for expiry means re-arming only in the window where there is nothing left to
#: re-arm from.
#:
#: HALF, and half specifically. At the half-way mark the replacement jar has a
#: full term against the old one's remaining half, so a re-arm at least DOUBLES
#: the jar's remaining restorable life. That is the evidence the "never over a
#: good store" rule was written to demand: not a vague preference for newer,
#: but a jar of identical provenance -- harvested from a session LinkedIn has
#: just answered 200-with-identity for -- carrying strictly more life. Below
#: half the trade buys less than a doubling and is not worth touching a working
#: store for. Above half it buys more, at the cost of leaving less headroom.
#:
#: The write cost is one harvest per 15 days at most, since a successful
#: re-arm resets the age to zero. That is nowhere near the "not on every call"
#: rule the errand also has to keep.
REARM_AFTER_S = MAX_AGE_S // 2


def is_linkedin_cookie(cookie: Any) -> bool:
    """Does this cookie belong to LinkedIn? Everything else is not ours.

    THIS GUARD EXISTS BECAUSE ITS ABSENCE SHIPPED, and it is the most serious
    of the four defects this module has had. ``context.cookies()`` returns the
    WHOLE browser jar, not this site's rows. The first working harvest wrote
    92 cookies, of which 68 were foreign:

        17  .google.com          17  .linkedin.com
        11  .youtube.com         10  .google.co.in
         8  accounts.google.com   6  .www.linkedin.com
        + rubiconproject, adnxs, demdex, doubleclick, facebook, bing, ...

    The ``.google.com`` and ``accounts.google.com`` rows include ``SID``,
    ``LSID`` and the ``__Host-`` prefixed ones -- live authentication for his
    Google account, not analytics.

    AND CHROME KEEPS THOSE ENCRYPTED. It seals its cookie store with
    AES-256-GCM; this file is plaintext JSON. So the harvest was taking
    credentials Chrome deliberately protects and writing them out in the
    clear, in a project directory, on a machine that runs agents all day.

    The filter is at the WRITE, so a foreign cookie never reaches disk at all.
    The restore path filters too, as a belt: an older or hand-edited file may
    still carry rows this version would never have written.

    Matching is on the registrable domain rather than a substring, so
    ``evil-linkedin.com`` and ``linkedin.com.attacker.net`` do not qualify.
    """
    if not isinstance(cookie, dict):
        return False
    domain = str(cookie.get("domain") or "").strip().lstrip(".").lower()
    return domain == "linkedin.com" or domain.endswith(".linkedin.com")


def _restrict(path: Path) -> None:
    """Owner-only where the platform supports it. Never fatal."""
    try:
        os.chmod(path, 0o600)
    except OSError:  # pragma: no cover - platform dependent
        pass


class SessionStore:
    """A cookie jar on disk. Cookies only, never a credential."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path else SESSION_PATH

    # -- reading ----------------------------------------------------------

    def read(self) -> dict:
        """The stored payload, or ``{}`` for every failure mode there is."""
        try:
            if not self.path.exists():
                return {}
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            logger.debug("session store unreadable: %s", type(exc).__name__)
            return {}
        return data if isinstance(data, dict) else {}

    def describe(self) -> dict[str, Any]:
        """What is stored, for reporting. NAMES AND COUNTS, never values."""
        data = self.read()
        if not data:
            return {"present": False, "why": "no session file has been written yet"}
        cookies = data.get("cookies") or []
        names = sorted({c.get("name") for c in cookies if isinstance(c, dict)})
        saved_at = data.get("saved_at")
        age = (time.time() - saved_at) if isinstance(saved_at, (int, float)) else None
        return {
            "present": True,
            "cookie_count": len(cookies),
            "cookie_names": names,
            "has_session_cookie": SESSION_COOKIE in names,
            "saved_at": saved_at,
            "age_seconds": int(age) if age is not None else None,
            "stale": bool(age is not None and age > MAX_AGE_S),
            # BOTH AGE VERDICTS COME OFF THE SAME `age`, deliberately. The
            # re-arm guard needs a different threshold from the restore
            # refusal, and the obvious way to give it one is a second age
            # computed at the call site -- which is how the guard and the
            # message it prints drift apart. There is one clock here and it
            # publishes both answers.
            #
            # An UNDATABLE jar (`age is None`: no saved_at, or a saved_at that
            # is not a number) reads as due. It is not stale -- nothing says it
            # is old -- but nothing bounds its remaining life either, and a jar
            # whose life cannot be bounded is exactly what the re-arm is for.
            # Replacing it from a confirmed live session also gives it the
            # timestamp it was missing.
            "due_for_rearm": bool(age is None or age > REARM_AFTER_S),
            "method": data.get("method"),
        }

    # -- writing ----------------------------------------------------------

    async def save_from_context(self, context: Any, *, method: str) -> dict[str, Any]:
        """Harvest the live cookies into the store. Atomic, or not at all.

        THE WRITE IS TEMP-PLUS-RENAME on purpose. A harvest interrupted
        halfway through a plain write leaves a truncated file, and a truncated
        file that still parses is the worst possible outcome here -- a store
        that reads as a session and is not one. ``os.replace`` is atomic on
        both platforms this runs on, so a reader sees either the old file or
        the whole new one.
        """
        try:
            cookies = await context.cookies()
        except Exception as exc:  # noqa: BLE001 - a harvest, never a gate
            logger.debug("cookie harvest failed: %s", type(exc).__name__)
            return {"saved": False, "why": f"could not read cookies ({type(exc).__name__})"}

        # ONLY STORE WHAT CAN ACTUALLY BE PUT BACK.
        #
        # THIS GUARD EXISTS BECAUSE ITS ABSENCE SHIPPED. The first version
        # kept any dict with a name, and a test's FakePage -- whose cookies
        # are {"li_at": "pending"} -- wrote a 7-character value with no
        # domain into the real store. `add_cookies` cannot use a cookie
        # without a domain and a path, so that jar was unrestorable: the
        # store looked populated and could never have worked.
        #
        # It was invisible precisely BECAUSE the degrade rules are good. Every
        # restore path returns restored:false with a reason, and a store that
        # always declines is indistinguishable from a store that is not needed
        # yet. Graceful degradation hides a broken mechanism perfectly, which
        # is why the thing being degraded to has to be validated at the point
        # it is WRITTEN rather than trusted at the point it is read.
        # LINKEDIN ROWS ONLY, decided before anything is written. See
        # is_linkedin_cookie: the whole browser jar arrives here, and it
        # contains his Google, YouTube and Facebook sessions.
        ours = [c for c in cookies if is_linkedin_cookie(c)]
        foreign = len(cookies) - len(ours)

        keep = [
            c
            for c in ours
            if c.get("name")
            and c.get("path")
            and isinstance(c.get("value"), str)
        ]
        rejected = len(ours) - len(keep)
        if foreign:
            logger.debug(
                "session store: dropped %d cookie(s) belonging to other sites",
                foreign,
            )
        if rejected:
            logger.debug(
                "session store: %d cookie(s) lack domain/path and cannot be "
                "restored, so they are not stored",
                rejected,
            )
        names = sorted({c["name"] for c in keep})
        if SESSION_COOKIE not in names:
            # Refusing to write is the right move: a jar with no session
            # cookie would overwrite a GOOD stored jar with a useless one,
            # which is how a safety net becomes the thing that loses the
            # session.
            return {
                "saved": False,
                "dropped_foreign": foreign,
                "rejected_unrestorable": rejected,
                "why": (
                    f"no restorable {SESSION_COOKIE} in the live context, so "
                    "there is no session to store. The existing store, if any, "
                    "is left alone rather than replaced with a useless jar. "
                    f"Dropped {foreign} cookie(s) belonging to other sites and "
                    f"{rejected} that lacked the path add_cookies requires."
                ),
            }

        payload = {
            "saved_at": time.time(),
            "method": method,
            "cookies": keep,
            "has_session": True,
            "scope": "linkedin.com only",
        }
        tmp = self.path.with_suffix(".json.tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            os.replace(tmp, self.path)
            _restrict(self.path)
        except OSError as exc:
            logger.debug("session store write failed: %s", type(exc).__name__)
            try:
                tmp.unlink()
            except OSError:
                pass
            return {"saved": False, "why": f"write failed ({type(exc).__name__})"}

        logger.info("session store: saved %d cookies (%s)", len(keep), method)
        return {"saved": True, "cookie_count": len(keep), "method": method}

    # -- restoring --------------------------------------------------------

    async def restore_into_context(self, context: Any) -> dict[str, Any]:
        """Put the stored cookies back, but ONLY into a context that lost them.

        The condition is the design. Injecting over a live session would make
        this a way to resurrect a stale jar; injecting into an emptied profile
        is the entire reason the file exists.
        """
        try:
            live = await context.cookies()
        except Exception as exc:  # noqa: BLE001
            return {"restored": False, "why": f"could not read live cookies ({type(exc).__name__})"}

        live_names = {c.get("name") for c in live if isinstance(c, dict)}
        if SESSION_COOKIE in live_names:
            return {
                "restored": False,
                "why": (
                    "the profile already holds a session cookie, which is the "
                    "fresher source. Nothing was injected."
                ),
            }

        info = self.describe()
        if not info.get("present"):
            return {"restored": False, "why": info.get("why", "no stored session")}
        if not info.get("has_session_cookie"):
            return {"restored": False, "why": "the stored jar has no session cookie"}
        if info.get("stale"):
            return {
                "restored": False,
                "why": (
                    f"the stored session is {info.get('age_seconds')}s old, past "
                    f"the {MAX_AGE_S}s ceiling. Sign in rather than resurrect it."
                ),
            }

        # THE BELT. The write filter is the fix; this is here because a file
        # written by an older version -- or edited by hand -- may still carry
        # rows for other sites, and injecting somebody's Google session into a
        # browser context is not something this server should be capable of
        # even from a bad input.
        cookies = [c for c in (self.read().get("cookies") or []) if is_linkedin_cookie(c)]
        if not cookies:
            return {
                "restored": False,
                "why": "the stored jar holds no linkedin.com cookies",
            }
        try:
            await context.add_cookies(cookies)
        except Exception as exc:  # noqa: BLE001
            return {"restored": False, "why": f"injection failed ({type(exc).__name__})"}

        logger.info(
            "session store: restored %d cookies into an emptied profile", len(cookies)
        )
        return {
            "restored": True,
            "cookie_count": len(cookies),
            "why": (
                "the profile had lost its session cookie and the store had one. "
                "This is the case the store exists for -- Chrome discards this "
                "profile on launch because it carries a newer Chrome's version "
                "stamp than playwright's chromium."
            ),
        }
