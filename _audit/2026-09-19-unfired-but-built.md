# BUILT-BUT-UNFIRED: THE WRITE ROWS WERE ALREADY BANKED. ZERO GAP ROWS MOVED.

Measured 2026-09-19, 14:05-14:15 by the box, at HEAD `744a1f4`.

**CORRECTS:** `_audit/_census/jobs.md` -- rows 103 and 104 were banked
COVERED-PROVEN on a PERFORMABILITY verdict quoted as though it were a live-fire
receipt; both move to COVERED-UNFIRED, and the slice's count block gains a delta
rather than a rewrite. Section 4 below holds the four readings.

**THE HEADLINE IS A NULL RESULT IN THE DIRECTION I WAS SENT, AND A DEFECT IN THE
OPPOSITE ONE.** I was sent to bank `COVERED-UNFIRED` on GAP write rows served by
the twelve shipped performable actions. **Every one of the twelve already has its
capability banked by an earlier wave.** No GAP row in the census is served by any
of them. **0 rows banked out of GAP; 296 GAP rows left where they are.**

What I found instead, looking at the same twelve actions from the coverage side:
**two rows banked COVERED-PROVEN on evidence that does not say what the rows say
it says.** Both are corrected here, and both corrections move the campaign's
number DOWN.

---

## 1. THE PREMISE I WAS GIVEN, RE-MEASURED

| claim in the brief | measured | verdict |
|---|---|---|
| `writes.PERFORMABLE` holds 12 actions | 12, by import at 14:12 | CONFIRMED |
| `writes._NINE_REFUSALS` is empty | `len() == 0` | CONFIRMED |
| all 12 are wired as tools | 12 of 12 `def linkedin_<action>` in `server.py`; `set_open_to_work` 0, as expected | CONFIRMED |
| `set_open_to_work` is NOT performable | not in `PERFORMABLE`, `url_template is None`, no tool | CONFIRMED |
| "nobody banked it" | **FALSE.** 13 W rows COVERED-UNFIRED, 6 W rows COVERED-CANNOT-DELIVER, plus the jobs slice's own CP/CU rows | **REFUTED** |

Instrument: `venv/Scripts/python.exe` importing `linkedin_server.writes` and
enumerating `SANCTIONED_WRITES`; `grep -c "def linkedin_<action>"` over
`linkedin_server/server.py`. `tests/test_writes.py` holds 130 tests.

### The row-count denominators I could and could not reproduce

The brief states **181 W rows and 15 R+W rows at GAP**. I could not reproduce
either number and I am recording that rather than quoting one I did not take.

    GAP rows in the five census slices, measured 14:08   296
      jobs.md                  61     (its own frozen count block says 99)
      messaging-and-content    84
      network.md               88
      profile.md               63
      mcp-inventory.md          0     (a TOOL inventory; carries no capability rows)

    of the 296, W-marked                               159
    R+W / R/W marked                                     2
    carrying no R/W column at all (jobs.md)             61

    blocker-map.tsv, a FROZEN spine of 409 rows,
    state_today == GAP                                 310

The three denominators disagree because they are three different sets: the
census `.md` files are today's rows, `blocker-map.tsv` is the 2026-09-03 frozen
set carrying today's state, and jobs.md's count block is a frozen block its own
slice deliberately does not rewrite. **I examined all 296 individually**, which
is the number that matters here regardless of which denominator is quoted.

---

## 2. WHERE EACH OF THE TWELVE IS ALREADY BANKED

One row per action, with the slice and the state it is already in. This is the
table the brief's premise needs and that nothing in the repository held.

| # | action | already banked at | state |
|---|---|---|---|
| 1 | `save_job` | `jobs.md` row 43 | CP -- and it genuinely landed, see s5 |
| 2 | `unsave_job` | `jobs.md` row 44 | CU |
| 3 | `follow_company` | `network.md` row 46 / `jobs.md` row 103 | **CU / CP -- CONTRADICTORY, see s4** |
| 4 | `unfollow_company` | `network.md` row 48 / `jobs.md` row 104 | **CU / CP -- CONTRADICTORY, see s4** |
| 5 | `apply_job` | `jobs.md` row 59 | CP (fired live, did not submit) |
| 6 | `update_setting` | `profile.md` N2 | CU |
| 7 | `publish_post` | `messaging-and-content.md` C1 | CU |
| 8 | `comment_on_item` | `messaging-and-content.md` C25 | CU |
| 9 | `react_to_item` | `messaging-and-content.md` C32 | CU |
| 10 | `update_profile_field` | `profile.md` A8, A11, A13, A17, A19, A21 | CU (six fields) |
| | | `profile.md` A2, A4, A6 | COVERED-CANNOT-DELIVER |
| 11 | `send_invitation` | `network.md` row 1 | CU |
| 12 | `send_message` | `messaging-and-content.md` M1, M2; `network.md` row 155 | COVERED-CANNOT-DELIVER |

**Twelve of twelve.** The finding "built and nobody banked it" was true of the
LEDGER's narrative and false of the CENSUS's rows.

---

## 3. THE 296 I DID NOT BANK, AND WHY

Every GAP row fails at least one of three tests. **The discriminator is not my
invention -- it is the census's own**, set by `network.md` rows 46 and 47:
*"Follow the company attached to a job posting"* is banked and *"Follow an
organization's Page from the Page itself"* stays GAP, on the stated ground
*"no `/company/` pattern"*. The same act at a different address is a different
row. I applied that uniformly.

### 3.1 WRONG OBJECT -- the action addresses a different kind of thing

| row | what it asks | the action people would reach for | why it fails |
|---|---|---|---|
| `M C36` / `M C37` | save / unsave a POST | `save_job` / `unsave_job` | `target_kind='job_id'`, `url_pattern ^.../jobs/view/\d{6,}/$`. A post is not a job |
| `M C26` | reply to a COMMENT | `comment_on_item` | gate requires exactly one `Text editor for creating comment` on the item permalink; a reply box is a different control, and no comment identifier is read anywhere |
| `M C34` | react to a COMMENT | `react_to_item` | gate requires exactly ONE reaction control on the permalink; the one drawn is the post's |
| `M M48` | react to a MESSAGE | `react_to_item` | `url_pattern` is `/feed/update/urn:li:<type>:<digits>/`; a message is not a feed item |
| `N 37`, `N 40`, `N 41`, `N 42` | follow / unfollow a PERSON | `follow_company` / `unfollow_company` | `target_kind` is `job_id` and `company_id`; a member is neither |

### 3.2 WRONG ADDRESS -- the capability exists, the route is not the shipped one

| rows | the address they need | the shipped pattern |
|---|---|---|
| `N 4`, `N 6`, `N 166` | a people-search result, the Sent manager, a group roster | `send_invitation`: `^https://www\.linkedin\.com/in/me/$` |
| `N 47`, `N 49` | `/company/<slug>/`, a skills Page | `follow_company`: `^.../jobs/view/\d{6,}/$` |
| `M M10`, `M M11`, `M M13` | `/messaging/thread/...` | `send_message`: `^.../messaging/compose/$` |
| `P A26`-`A29` | `/in/me/overlay/contact-info/` | `update_profile_field`: `^.../in/me/edit/intro/$` |
| `P B4`, `P C2`-`C6` | `/public-profile/settings` | see s6 -- ruled by the operator, not mine |
| `M M35`, `M M36`, `N 176`, `P N12` | other settings pages | `update_setting`: `^.../mypreferences/d/dark-mode/?$`, ONE address |
| `M C61`-`C68`, `C91`, `N 63`, `N 64`, `N 163`-`N 176` | `/groups/...` | not admitted; a live ruling elsewhere today |
| `M C57`, `C58`, `C92`, `N 181`-`N 193` | `/events/...` | not admitted |

`update_setting`'s own `residue` is why the settings family cannot be stretched:
*"TWO OF THE THIRTY-THREE ADDRESSES ARE ACCOUNT DESTRUCTION ... a setting has to
be admitted BY NAME or not at all."*

### 3.3 MISSING PARAMETER -- the right action, a thing its spec does not have

| row | asks for | the spec |
|---|---|---|
| `N 5` | a personalised note on an invitation | `linkedin_send_invitation(member, confirm_token)` takes no note parameter |
| `M C2` | choose the post's audience | `publish_post.audiences == {}` |
| `M C3`-`C9`, `C27`, `M M14`-`M M18` | photo, video, document, poll, GIF, files | `target_kind='post_text'` / `'item_and_text'`; no upload is sanctioned |
| `M C33` (already XR) | choose WHICH reaction | the toggle applies LinkedIn's unmeasured default |

These three are the `COVERED-CANNOT-DELIVER` SHAPE, not `COVERED-UNFIRED`. I did
not bank them, because my mandate was UNFIRED and because banking
CANNOT-DELIVER needs the refusal MEASURED, not inferred. **Flagged for whoever
owns those slices**: `PUBLISH-POST-AUDIENCE-PARAM` (1 row), `INVITE-NOTE-PARAM`
(1 row) and `MISSING-PARAM-MESSAGING` (1 row) are blocker names that already say
exactly this.

### 3.4 THE THREE I LOOKED AT HARDEST AND STILL LEFT GAP

**`P A14` (postal code), `P A15` (location display choice), `P A22` (primary
position).** These are intro-editor fields, and `update_profile_field` addresses
the intro editor. Six of their siblings (`A8`, `A11`, `A13`, `A17`, `A19`,
`A21`) are banked CU on the stated ground *"aimable by `label-for`"* /
*"aimable by `aria-label`"*; three others (`A2`, `A4`, `A6`) are
COVERED-CANNOT-DELIVER on a measurement that they are **unaimable**.

`A14` and `A22` are **neither**. `linkedin_server.intro_fields.signature`
returns a TRI-STATE and both read `unknown`: no label matched, AND four controls
in that container have no accessible name at all, so the field may sit behind
one of them. The action's aiming branch *"refuses unless EXACTLY ONE control is
named as asked"* -- so whether it would refuse is **the thing that is not
known**. Banking CU would assert the gate would not refuse. **That assertion has
no measurement behind it, and it is exactly the inflation this wave was sent to
prevent. They stay GAP.** `A15` moved partly forward (`city` and
`country_region` read present) but those are `A13` and `A11`'s fields, already
banked; the display CHOICE control is still unidentified.

**A CORRECTION OWED TO THOSE THREE ROWS, REPORTED AND NOT EDITED** (they belong
to today's intro-editor pass, and rewriting another wave's cell is how
attribution is lost): all three end *"STILL A WRITE EITHER WAY -- it needs a
WriteSpec, a gate and a ruling."* **The WriteSpec and the gate exist.**
`update_profile_field` is in `PERFORMABLE`, holds
`url_template='https://www.linkedin.com/in/me/edit/intro/'`, an
`exempt_substring='/edit/'`, and ships. What those rows lack is a NAMEABLE
CONTROL, which is a narrower and more actionable blocker than the one written.
The state does not move; the reason should.

**`M M6` (send a message request).** `send_message` reaches the same compose
surface, and `M1` records it **fired live 2026-09-03 and refused at
`_recipient_gate`**. So `M6` is CANNOT-DELIVER-shaped, never UNFIRED. Its
assigned blocker is `MESSAGE-REQUESTS-SURFACE`, which names a surface while the
SEND half is already measured refusing. Reported, not moved.

---

## 4. THE DEFECT: TWO ROWS BANKED COVERED-PROVEN ON A PERFORMABILITY VERDICT

`_audit/_census/jobs.md` rows 103 and 104:

    | 103 | Follow a company   | CP | `linkedin_follow_company`;
    |     |   `2026-08-31-linkedin-perform.md:1318` -- "**PERFORMS** | verified
    |     |   by re-reading the followed list" |
    | 104 | Unfollow a company | CP | `linkedin_unfollow_company`; same table |

**`PERFORMS` in that document is a statement about the GATE, not about a fire.**
Four independent readings, all taken 14:18-14:22:

1. The table those rows quote is `## 29. THE THIRTEEN-ROW LEDGER`, whose stated
   subject is *"`writes.SANCTIONED_WRITES` holds thirteen actions"* and whose
   closing line is *"Rows 7-12 are the six refusals a caller can reach through a
   tool."* It is a refuses/performs ledger.
2. The same file's `## 10. THE LEDGER -- performable before, performable after`
   carries the identical verdicts under columns literally headed
   `before | after`.
3. **`apply_job` reads `PERFORMS` in that same ledger**, and `jobs.md` row 59
   records *"zero applications have ever landed."* So `PERFORMS` is
   demonstrably not a landing claim, by that slice's own row.
4. The receipts of the very document being cited, at `:1058-1059`, `:1462` and
   `:1794`: `confirm_tokens used 0`, `writes performed 0`, **"Nothing was
   fired."** A write cannot be performed without a confirm token.

There is no live-fire receipt for either action anywhere in `_audit/`. I
searched for one.

**AND `jobs.md` ALREADY KNEW THIS.** Its own section *"THE SECOND CORRECTION:
what 'live-fire' means for the three writes"* exists to separate a ledger
verdict from a fire, and applies it to three actions -- giving `unsave_job`
**NO. NEVER FIRED.** Rows 103 and 104 are the same error, two hundred rows later
in the same file, on the two actions that section did not cover.

**CORRECTED HERE: 103 and 104 move CP -> CU**, which is what the NETWORK census
slice has held all along in its rows 46 and 48. The two slices now agree.

    jobs.md state counts       CP 21 -> 19        CU 7 -> 9

Following `profile.md`'s convention, the frozen count block is **not
rewritten** -- a delta is recorded beneath it, because a count that silently
rewrites itself cannot be cited.

---

## 5. WHAT I DID NOT TOUCH, HAVING CHECKED IT

**`save_job` row 43, "the one write proven to land", STANDS.** The blanket
statements elsewhere in `_audit/` that no confirm token was ever used are scoped
to their own sessions: `_audit/2026-08-30-linkedin-undo.md:433` records a
redeemed save producing `newly_observed_save_label: "Unsave the job"` -- an ON
label that could only exist because a real save produced it. That is a landed
write and the row is right.

**`apply_job` row 59 STANDS.** It was fired live, end to end, and reported
honestly that it did not submit. Its row already carries the effect qualifier.

---

## 6. ONE FAMILY I REFUSED ON THE OPERATOR'S STANDING RULING

`P B4`, `P C2`, `P C3`, `P C4`, `P C5`, `P C6` and two siblings -- eight rows
under `FORBIDDEN-CLASS-FIX-LANDED` -- all sit at `/public-profile/settings`.
They are not mine and not cheap. `readonly.py` records the operator's ruling of
2026-08-31 at the `/mypreferences/d/dark-mode` entry: *"ONE NAMED PAGE AT A
TIME, NEVER THE FAMILY, NEVER A WILDCARD"*, and it names two pages deliberately
refused because admitting them *"would each have required `/settings/` to be
narrowed to buy one page, WHICH IS TRADING A STANDING REFUSAL FOR A SINGLE
READ."* `/public-profile/settings` contains `/settings`. **They stay GAP and
only he can revisit it.**

---

## 7. NOTHING WAS FIRED FROM THIS SEAT

    browser opened            0
    write tools called        0
    confirm_tokens minted     0
    grants minted             0
    writes flag               untouched
    page loads                0
    census rows moved out of GAP   0
    census rows corrected downward 2
