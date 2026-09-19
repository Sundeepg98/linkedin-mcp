# The newsletter create route is a third address, and the page named it

**CORRECTS:** `_audit/INSTRUMENTS.md` -- register 9.1's hypothesis that census row `M C50` may need no boundary change is refuted: the create route is a third address and it is refused.

Section 9.1 costed `M C50` "create a newsletter" at zero boundary change on the
grounds that `/article/new/` is already on the read allowlist.

Written 2026-09-05 by the `newsletter-build` wave, off the first live load of
`/mynetwork/network-manager/newsletters/`.

## The claim being corrected, quoted so nobody has to hunt it

Register 9.1, written the same day by the `newsletter-surface` wave:

> **AND IT FOUND A ROW COSTED AGAINST AN ADDRESS IT MAY NOT USE.**
> `/article/new/` is ALLOWED at HEAD and `/article/new/?isNewsletter=true` is
> refused FOR THE QUERY STRING ALONE. So `M C50` "create a newsletter" may need
> no boundary change at all. That is reported as a hypothesis with the read
> that settles it, not as a move.

**The discipline in that entry is not what is wrong with it.** It named itself a
hypothesis, it named the read that would settle it, and it declined to move the
row. That is the correct shape and it is why this correction is cheap to write:
the claim was falsifiable and it has been falsified.

## The measurement

The newsletters page draws an anchor to a **third** address, which neither the
census nor the route probe had:

    /article/newsletter/new/          3 path segments, no query, no identifier
    readonly.is_read_url(...)  ->     False

Refused for want of a pattern. It contains no `/create` substring, so unlike
`/newsletters/create/` it is refused ONCE rather than twice -- a distinction
that matters, because a single refusal is one boundary change and a double one
is two.

Controls in the same run, both behaving:

    /article/new/            is_read_url -> True     (known allowed)
    /newsletters/create/     is_read_url -> False    (known refused)

The address was read off the live page, shaped through `census_substitute`
before being printed, and printed only after that shaping was verified not to
have changed it -- so what is quoted above carries no identifier.

## What changes, stated narrowly

**WHAT IS REFUTED:** `M C50` as a PLANNING ASSUMPTION costing zero boundary
change. LinkedIn's own newsletter surface links to a dedicated create address
and that address is refused. A row costed at zero on the strength of
`/article/new/` being the create route is costed wrong.

**WHAT IS NOT REFUTED, and the difference is not pedantry.** Nothing here proves
`/article/new/` CANNOT create a newsletter. It proves there is a dedicated
address for it and that this is the one LinkedIn links to. Both can be true, and
a correction that claimed more than it measured would need its own corrector.

**WHAT ALSO CHANGES, AND IT IS THE PART A PLANNER WILL CARE ABOUT.** 9.1 named
the read that would settle the question: re-census `/article/new/` with its
menus pressed. That read is no longer the cheapest route to the answer and it
is no longer free of cost -- `/article/new/` is a COMPOSER, and opening one may
autosave a draft this server has no surface to detect. The page has answered
the question from the outside for nothing. **A live anchor beat a menu-press
census, which is the same lesson the route audit keeps producing: ask where a
capability GOES before enumerating what a page draws.**

## What `M C50`, `M C81` and `P L3` now need

One allowlist pattern for `/article/newsletter/new/`, anchored and with no
query string, PLUS a WriteSpec, PLUS a ruling. Three things, not zero, and the
first of them was previously believed to be already paid for.

None of the three is proposed here. This document corrects a cost; it does not
spend one.

## Why this is a document and not a line in the register

Register entries are STANDING INSTRUCTIONS. 9.1 is true about what it measured
-- `/article/new/` really is allowed and the query string really is what refuses
the variant -- and only its INFERENCE is wrong. Rewriting it would erase a
correct measurement to remove an incorrect conclusion, and a reader would lose
the sequence. So 9.1 keeps its text and gains a back-pointer, which is the
mechanism 9.7 was added under on the same day.
