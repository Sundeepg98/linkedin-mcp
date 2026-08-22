# LinkedIn parity, 2026-08-22 -- what he can do that this server cannot

| Gap | Bucket | Evidence |
|---|---|---|
| Apply, save, message/InMail, connect, endorse, follow, profile edit, Open To Work, mark-read | **1. WRITE -- out of scope** | Four enforcement mechanisms + launch boundary, all still passing; `test_server_surface.py` FORBIDDEN_TOOLS; LinkedIn writes separately blocked by the permission classifier |
| Job tracker **"In Progress"** -- and it holds his ONLY tracked row (count 1) | **1. PLATFORM -- needs a click** | MEASURED: the tab is `role="button" aria-expanded="false"` with no token and no url, and the live page renders **zero** `jobs-tracker` hrefs. `?stage=in_progress` does not exist. Allowlisting the guess would have rendered the *Saved* tab under an "In Progress" label |
| Tracker `?stage=interview` / `?stage=archived` | **2. DELIBERATE** | Stages enumerated at `readonly.py:50-69`; LinkedIn's own tokens confirm both are real, and both read 0/empty for him today, so neither earns a page load yet |
| Who a specific profile viewer is; anything about a third party beyond the row he is shown | **2. DELIBERATE** | 6 of 10 viewers are anonymous by their own choice; `shape.py` treats "no slug" as anonymous structurally |
| Notification badge left unread | **2. DELIBERATE** | Server-side on page serve; documented, unavoidable, and the reason not to call the tool |
| **One job posting in full** | **3. UNBUILT -> BUILT THIS PASS** | A 6-result live search returned 6 rows carrying **0 descriptions, 0 salaries, 0 applicant counts**. Every sibling server (naukri, uplers, instahyre) has a single-job read; linkedin had none |

**Built: `linkedin_job_detail(job_id)`** -- 1 page load, 1 posting. Returns pay range, LinkedIn's applicant count, workplace + employment type, hiring status, location, posted, and the description. Zero new injected scripts (`page.title()`, one `get_attribute`, `inner_text`). Allowlist admits `/jobs/view/<digits>` with **no query string** -- the url is built from an integer, so the slug and tracking-param forms are refused. Verified live on a *different* posting (4446036386) than the fixtures were cut from: every field correct, `salary` correctly `null` where that posting has none. 28 new tests, shown failing first; fixtures frozen at both hydration states plus an unrendered shell that proves a title alone never becomes an answer.

**Also closed:** the privacy-guard fixture list was hand-maintained, and its own comment recorded that scoping guards to remembered files had already let two real member urns through. It is now a glob, with a test that the glob is non-empty -- three new captures would have been exactly the old failure. The captures carried a "More jobs" rail naming 10 real employers plus "1 connection works here"; all are cut or renamed.

**Unbuilt reads worth having, ranked, each 1 page load unless noted:**
1. **Search appearances** (`/analytics/search-appearances/`) -- is his profile being *found*, and for what. Direct analog of `naukri_search_impressions`. ~1 wave: new surface, new parser, live capture at both hydration states.
2. **Skill endorsement counts** -- the `/details/skills/` page is *already loaded* by `linkedin_my_profile(include_skills=True)`; counts are dropped today. **0 extra page loads.** Smallest real win left.
3. **Job recommendations** (`/jobs/collections/recommended/`) -- overlaps the `linkedin-jobs` Gmail skill, which already reads the recommendation digests for free. Only worth it if the on-site set proves richer than the email.
4. Post/follower analytics -- he is not posting; no job-hunt value today. Not recommended.

**Flag:** the `linkedin-jobs` skill's Scope clause (`SKILL.md:341-342`, dated 2026-08-20) says *"do not revive `mcp-servers/linkedin/`"*. This wave's brief commissions the opposite. Treating the clause as stale, not overridden silently -- it needs a decision.
