claude-opus-5-5[1m]

# The completeness probe -- does the census know every address LinkedIn rendered?

Lane Y, 2026-09-23. Worktree branch off master `b0d3ab8`. Offline: no LinkedIn
access, no Chrome, no port 9224, no `_state/chrome-profile`.

STATUS: IN PROGRESS -- written as it goes. A section with no body has not run yet.

## The question

`scripts/census_completion.py` cannot find a capability nobody enumerated. On
2026-09-03, 23 unenumerated gaps were found by accident. Completeness has never
been MEASURED. This probe measures it: harvest what LinkedIn itself rendered in
the captures already on disk, normalise every address to a path SHAPE, and diff
the shapes against every address the census records. Axis-hunting: fitness is a
class the census lacks; the saturation criterion is a measured flattening of the
discovery curve, capture by capture, in chronological order.

## Method

Written BEFORE the first full run, so the criteria below could not be fitted to
the result.

1. **Captures.** Every raw page capture on disk from earlier live fires, found by
   explicit globs that never enter a `chrome-profile*` directory: the main
   checkout's `_state/` (and one level of its subdirectories), its gitignored
   `_audit/_probe-*.html`, the `_state/` directories sibling worktrees left
   behind, and the TRACKED sanitised fixtures under `tests/fixtures/` whose own
   header does not declare them invented, derived or synthetic. Byte-identical
   files are one capture. Nothing is copied out of any of them.
2. **Harvest, drawn only.** Bundles are stripped first with the SHIPPED
   `drawn_route_corpus.strip_bundles` (scripts, styles, `<code>` model payloads,
   templates, noscript), because a needle in the source is not a needle on the
   page. From what remains: every `<a href>`, every `<form action>` with its
   method, and every interactive control -- `button`, `select`, `textarea`,
   non-hidden `input`, and any element whose `role` is a control role -- with
   its accessible name (`aria-label`, else `title`, else `placeholder`, else its
   text).
3. **Shape.** Every address is reduced by the SHIPPED
   `_probe_premium_surfaces_shape.shape_path` at depth 6 (the depth
   `drawn_route_corpus.py` argues for), then hardened: a few more families whose
   next segment is content rather than route (`products`, `pulse`, `posts`,
   `hashtag`, `topics`) are reduced the same way, query VALUES are dropped and
   only parameter NAMES are kept beside the pattern, and the whole pattern is
   vetoed against the exact-value identity wordlist when the key is on disk.
4. **Census addresses.** Every address-shaped token in every census file
   (the four slices, `mcp-inventory.md`, and every `.tsv` under `_audit/_census/`
   including `read-addresses.tsv`), located to its row id where it sits in a
   capability row and to its line where it sits in prose. Census placeholders
   (`<id>`, `{id}`, `<slug>`, `NUMERIC-ID`, ...) are driven through the same
   reducer so both sides speak one alphabet; a placeholder segment on the census
   side matches any one segment.
5. **Classes.** `ROW` -- a census capability row carries the pattern exactly.
   `PROSE` -- only census prose or a census table note carries it.
   `FAMILY` -- no exact match, but a census address is a segment-prefix of it or
   it of one. `NEW` -- no census address shares even its first segment.
   **CANDIDATES are PROSE + FAMILY + NEW**, reported by class so the reader can
   draw the line elsewhere.
6. **Controls** are a second, noisier axis and are reported apart from
   addresses. A label is reduced to a TEMPLATE -- the leading literal words, one
   `<X>` for the varying middle, the trailing literal words -- where a word
   survives only if it is lowercase, or is the first word of two or more
   distinct labels; digits become `<n>`; a label with non-ASCII left after
   punctuation folding is withheld and counted. A template is RECORDED when some
   census capability row carries every one of its content words; otherwise it is
   a candidate.
7. **THE SATURATION CRITERION, DECLARED HERE BEFORE ANY CURVE WAS COMPUTED.**
   Captures are ordered by capture time and repeat captures of one surface are
   folded into that surface's first appearance, so a re-capture cannot flatten
   the curve by construction. **The curve has flattened if the LAST FIVE
   distinct surfaces, in capture order, added ZERO new candidate address
   patterns.** Anything else is "not flattened", and the per-surface counts are
   printed either way. A permutation-averaged accumulation curve and the
   singleton count are printed beside it, because capture order was chosen by
   earlier waves for their own reasons and one ordering can flatten by accident.

## Captures found

(pending)

## Harvest

(pending)

## Diff against the census

(pending)

## The discovery curve

(pending)

## Candidates per slice

(pending)

## Live-capture list

(pending)

## The instrument and its control

(pending)

## Cold verification

(pending)

## Gates

(pending)
