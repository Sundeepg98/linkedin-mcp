# Ruling, 2026-10-10: the detail pages of a profile he names

## The question

The live lane's session 7 (2026-10-10, 11:38 to 11:45) read the profile of a
first-degree member the operator named, once, behind its single-use grant
(`linkedin_read_named_profile`, ruling NAMED-PROFILE-READ-BEHIND-A-GRANT). The
first render drew no Interests section and no group link: 0 'Interests', 0
group links, 0 links to a `details/interests` page. Census rows `N 178` (which
groups a member belongs to) and `N 65` (a member's Interests section) are about
exactly that section, and on a profile LinkedIn draws it, in full, on the
profile's own detail page, `/in/<slug>/details/interests/`.

The read boundary admits only HIS OWN detail pages (`/in/me/details/...`), and
the named-profile door admits exactly `https://www.linkedin.com/in/<segment>/`:
no sub-page. So a detail page of the member he names was reachable by no door,
whatever he confirmed.

## The ruling

RULED: (orchestrator, 2026-10-10, applying the operator's 08:01 YES to reading profiles he names) "the read of a profile he names includes that SAME profile's own detail pages (/in/<the same slug>/details/<section>/), one load per call, behind the same single-use grant and the same preview warning."

Registered as `NAMED-PROFILE-DETAIL-PAGES`. It APPLIES
NAMED-PROFILE-READ-BEHIND-A-GRANT (the operator, 2026-09-28 08:01, verbatim in
`_audit/2026-09-28-rulings-named-profile-read.md`: "Yes, I'm giving you
permission.") and narrows nothing in it.

## What it permits, and what it does not

- ONE address shape, and only for the segment the caller named:
  `https://www.linkedin.com/in/<the same segment>/details/<section>/`, with
  `<section>` one word of a CLOSED vocabulary
  (`readonly.NAMED_PROFILE_DETAIL_SECTIONS`), no query, no fragment, no deeper
  path, LinkedIn's own host, the trailing slash.
- One load per call, behind the same single-use grant
  (`named_profile.ReadGrant`), bound to that exact address, two minutes, once.
- The same preview warning: LinkedIn may show the member the view, and a view
  cannot be taken back. The preview loads nothing.
- The forbidden-substring list applies WITHOUT exemption, as at the named-profile
  door.
- It does NOT admit: any other member's segment, any non-details path under the
  profile (`/overlay/...`, `/recent-activity/...`, an edit address), a query (an
  Interests tab index, say), or any address the page draws. It is not a
  read-door allowlist line: the read door still refuses every third-party
  profile address.
- Never for a measurement, never aimed by a name read off a page -- the parent
  ruling's conditions, unchanged.

## Where it is enforced

- `linkedin_server/readonly.py`: `named_profile_details_url(segment, section)`
  composes the one address; `assert_named_profile_details_url(url, segment)`
  admits it only for that segment and a section of the closed vocabulary.
- `linkedin_server/named_profile.py`: the preview and the grant for a details
  read; the one load, through the navigator's named-profile door.
- `tests/test_named_profile_detail_pages.py`: the admitted shape, and the
  controls shown failing -- another segment, a non-details path, a section off
  the vocabulary, a query, a deeper path -- each refused.

## What is not built, and why

The capture of the Interests detail page does not exist (no tracked skeleton of
it), so no reader of its entries is built: a reader built on synthetic markup
moves no row and failed live once already. The capture spec and the reader
design for `N 178` and `N 65` are in
`_audit/2026-10-10-lane-np-named-profile.md`, sections D.2 and D.3.
