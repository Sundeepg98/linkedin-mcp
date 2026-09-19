"""The SDUI action resolver, held to the register's second law.

**An instrument enters the register only if it has been SHOWN FAILING** -- and
shown failing on the DISTINCT SHAPES of the defect it claims to cover rather
than on one of them. One demonstration proves a check can fire and says nothing
about what it is silent on. That law was earned in this repository by an
instrument that passed two mutations and was deaf to the third, which was the
shape with the most consequence.

## What the resolver claims, so the shapes below are a list and not a mood

It claims to answer ONE question -- *given a control, what does this page say
pressing it does* -- through the React flight row graph, and to REFUSE rather
than guess everywhere it cannot. So the shapes it must be shown failing on are
the shapes of a wrong ATTRIBUTION and the shapes of a false REFUSAL, and both
directions are exercised below:

    a main-tree row read as if it were a control        must REFUSE
    a container's children attributed to one button     must REFUSE
    two mechanisms both claiming the attribution        must REFUSE
    a reference resolving to no row, or to two          must REFUSE
    an all-zero reading, which is the shape of consent  must REFUSE
    two renderings of one control that DISAGREE         must REFUSE
    a partial reading, some sites unread                must REFUSE
    ...and shape A and shape B, which must ANSWER, because an instrument that
    only ever refuses is not an instrument.

## The corpus can lie, and it did

**Every backslash below is built from ``chr(92)``, never typed**, and the first
test asserts the corpus really is escaped. That is not fastidiousness: the
first smoke run of this resolver used a corpus written through a shell heredoc,
which collapsed each ``\\n`` into a real newline. **The corpus for an ESCAPED
payload was silently an UNESCAPED one and the smoke still passed**, because the
literal-newline anchor happened to cover it. The reading proved the wrong half
and looked exactly like proving the right one.

That is this repository's oldest failure -- a partial view treated as the whole
thing -- arriving in the test corpus rather than in the instrument, which is
the one place nothing else is watching.

## What is NOT tested here, said plainly

Nothing in this file runs a browser or reaches LinkedIn. Every payload is
invented, carries no identity, and is shaped by hand. **So this proves the
resolver's LOGIC and proves nothing about what LinkedIn's page contains** --
that is what running it does, and the run reports its own limits.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_RESOLVER_PATH = _ROOT / "scripts" / "_probe_sdui_action_resolver.py"
_PROBE_PATH = _ROOT / "scripts" / "_probe_open_to_work_payload.py"


def _load(name: str, path: pathlib.Path):
    """Import a script by path. ``scripts/`` is not a package.

    Safe for the reason the scripts' own guards exist -- module scope does
    nothing, and ``tests/test_scripts_are_import_safe.py`` asserts that for
    every script in the directory.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


res = _load("_sdui_resolver", _RESOLVER_PATH)
probe = _load("_otw_probe_for_differential", _PROBE_PATH)


# ---------------------------------------------------------------------------
# The corpus. Backslashes are BUILT, never typed.
# ---------------------------------------------------------------------------

BS = chr(92)
NL = BS + "n"  # a stream newline as it is written inside a JS string literal
CORE = "proto.sdui.actions.core."


def esc(text: str) -> str:
    """JSON as it is written inside a JS string literal: every quote doubled."""
    return text.replace('"', BS + '"')


def push(rows: list[str]) -> str:
    """One flight chunk: a script tag carrying rows joined by escaped newlines."""
    return (
        '<script>self.__next_f.push([1,"' + NL.join(rows) + NL + '"])</script>'
    )


def doc(*chunks: str, head: str = "") -> str:
    """A document: optional markup, then flight chunks. Always one line."""
    return "<html><body>" + head + "".join(chunks) + "</body></html>"


def row(row_id: str, json_text: str) -> str:
    """One flight row, ``<hexid>:<json>``, with the json escaped."""
    return row_id + ":" + esc(json_text)


def actions(*kinds: str) -> str:
    """An SDUI action list naming the given kinds, in order."""
    return (
        '"onTap":{"actions":['
        + ",".join('{"$type":"' + CORE + kind + '"}' for kind in kinds)
        + "]}"
    )


def button(label: str, tail: str = "") -> str:
    """A component object carrying an aria-label, plus whatever follows."""
    return '["$","button",null,{"aria-label":"' + label + '"' + (
        "," + tail if tail else ""
    ) + "}]"


#: SHAPE B -- the parent names the child row; label and actions share that row.
#: This is the shape the census recorded, at line 243 and in its table.
SHAPE_B = doc(
    push([
        row("1a", '["$","div",null,{"children":["$L2b"]}]'),
        row("2b", button("Show details", actions("Navigate"))),
    ])
)

#: SHAPE A -- the label's own object names a row that holds the actions.
SHAPE_A = doc(
    push([
        row("1a", button("Edit", '"onTap":"$L3c"')),
        row("3c", '{"actions":[{"$type":"' + CORE + 'SetState"},'
                  '{"$type":"' + CORE + 'ServerRequest"}]}'),
    ])
)

#: A CONTAINER'S CHILDREN -- three references in one array, the exact shape
#: the census recorded for the Open-to menu.
CHILDREN = doc(
    push([
        row("1a", '["$","div",null,{"aria-label":"Open to",'
                  '"children":["$L153","$L154","$L155"]}]'),
        row("153", '{"$type":"' + CORE + 'Navigate"}'),
    ])
)

#: A MAIN-TREE SLAB -- the label and a ServerRequest in one row that NOTHING
#: names. The kinds are real and must not be reported: they are the page
#: section's.
MAIN_TREE = doc(
    push([
        row("1a", button("Edit", actions("SetState", "ServerRequest"))),
    ])
)

CORPORA = {
    "shape_b": SHAPE_B,
    "shape_a": SHAPE_A,
    "children": CHILDREN,
    "main_tree": MAIN_TREE,
}


def read(payload: str, label: str, extra: tuple[str, ...] = ()) -> dict:
    """Resolve one label against one payload, index built fresh."""
    return res.resolve(payload, label, res._row_index(payload), extra_kinds=extra)


def lines(payload: str, label: str, extra: tuple[str, ...] = ()) -> str:
    """Everything a run would PRINT for one label, as one string."""
    return "\n".join(res.render(read(payload, label, extra)))


# ---------------------------------------------------------------------------
# THE CORPUS'S OWN CAN-IT-DISCRIMINATE CHECK
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(CORPORA))
def test_the_corpus_is_actually_escaped(name):
    """THE DEFECT THE FIRST SMOKE RUN HID, pinned before anything rests on it.

    A corpus written through a shell heredoc lost its backslashes, so a
    document meant to carry an ESCAPED flight payload carried an unescaped one
    -- and the run passed, because a different anchor covered it. A corpus that
    cannot carry the shape under test proves the wrong half and looks identical
    to proving the right one.

    THE COLLAPSE PRODUCES A REAL NEWLINE, so that is what is asserted against
    -- exactly, over the whole document, rather than through an anchor count
    that a single-row corpus legitimately reads zero for. The delimiter anchor
    is then checked only where there IS a delimiter to find.
    """
    payload = CORPORA[name]
    assert BS + '"' in payload, ("not escaped at all", name)
    assert chr(10) not in payload, ("a backslash-n collapsed to a newline", name)
    index = res._row_index(payload)
    assert index["anchors"]["literal newline"] == 0, name
    assert index["rows"] >= 1, name
    if index["rows"] > 1:
        assert index["anchors"]["escaped newline"] > 0, name


# ---------------------------------------------------------------------------
# THE DIFFERENTIAL -- this file duplicates three of the probe's primitives, and
# pays for the duplication with a check rather than with an inspection.
# ---------------------------------------------------------------------------

_DIFFERENTIAL_LABELS = ("Edit", "Show details", "Open to", "Nowhere At All")


@pytest.mark.parametrize("name", sorted(CORPORA))
@pytest.mark.parametrize("label", _DIFFERENTIAL_LABELS)
def test_the_two_locators_return_identical_answers(name, label):
    """"IDENTICAL REFUSALS" AS A CHECKED CLAIM RATHER THAN A SENTENCE.

    The resolver re-implements the probe's locator rather than importing it --
    a general instrument must not depend on a specific probe, and the probe is
    committed and being gated. The cost of that duplication is DRIFT: two
    locators that silently disagree about which bytes they describe would make
    "the componentkey walk refused and the row walk answered" a statement about
    two different controls.

    So the claim is asserted on the whole dict, refusal texts included, across
    four labels and four corpora -- present once, present twice, absent, and
    bare-only. A divergence fails and names itself.
    """
    assert res._locate_label(CORPORA[name], label) == probe._locate_label(
        CORPORA[name], label
    )


@pytest.mark.parametrize("name", sorted(CORPORA))
def test_the_two_enclosure_walks_return_identical_regions(name):
    """The walk-out is duplicated too, and drifts the same way.

    Every offset in the corpus, not a sampled few: a walk that agreed at the
    offsets somebody thought to check and diverged elsewhere would be the
    partial-view failure inside the instrument built to detect it.
    """
    payload = CORPORA[name]
    for at in range(len(payload)):
        assert res._enclosing_object(payload, at) == probe._enclosing_object(
            payload, at
        ), at


def test_the_two_token_counters_agree():
    """Including on the corpus that broke the naive one.

    ``str.count("edit")`` matches inside ``isEditFlow``, ``edited``, ``editor``,
    ``credit`` and ``editorial``. Asserting the two implementations agree is
    only meaningful if at least one input distinguishes them from the broken
    version, so the disagreement with ``str.count`` is asserted too.
    """
    corpus = "isEditFlow edited editor credit editorial creditCard edit"
    assert corpus.count("edit") == 6
    assert res._occurrences(corpus, "edit") == 1
    assert res._occurrences(corpus, "edit") == probe._occurrences(corpus, "edit")


# ---------------------------------------------------------------------------
# THE ROW INDEX -- three anchors, and the third is the one nearly missed
# ---------------------------------------------------------------------------


def test_a_row_beginning_a_chunk_is_found_only_by_the_third_anchor():
    """THE ANCHOR THAT WAS NEARLY LEFT OUT, and what leaving it out would cost.

    A flight stream is served in pieces, one ``push`` per script tag. A row
    that begins a chunk has an HTML tag before it, not a newline -- so an
    anchor on the delimiter alone cannot see it, and a reference into that row
    would come back "no row carries that id". **A fact about the reader,
    reported in the grammar of a fact about the page**, which is the failure
    this whole family keeps rediscovering.

    Asserted as a DIVISION, not a total: the escaped anchor must find the row
    that follows a newline and MISS the one that starts a chunk, and the chunk
    anchor the reverse. A total would pass with one anchor doing all the work.
    """
    payload = doc(
        push([row("1a", "{}"), row("2b", "{}")]),
        push([row("3c", button("Edit", actions("Navigate")))]),
    )
    index = res._row_index(payload)
    # `2b` follows a delimiter; `1a` and `3c` each OPEN a chunk and no
    # delimiter precedes either. One anchor could not have found all three.
    assert index["anchors"]["escaped newline"] == 1, index["anchors"]
    assert index["anchors"]["chunk start"] == 2, index["anchors"]
    assert index["rows"] == 3
    # And the row that starts the second chunk really is reachable: a reference
    # to it resolves, which is the only thing the anchor exists to buy.
    referring = doc(
        push([row("1a", '{"children":["$L3c"]}')]),
        push([row("3c", button("Edit", actions("Navigate")))]),
    )
    found = read(referring, "Edit")
    assert found["refused"] is None, found["refused"]
    assert found["kinds"]["Navigate"] == 1


def test_a_doubled_backslash_is_not_a_row_delimiter():
    """A DISCRIMINATOR MUST NOT MATCH INSIDE A STRING YOU DID NOT MEAN.

    Inside a JS string literal a stream newline is ``\\n``; a literal
    backslash-n in the DATA is ``\\\\n``. Without the lookbehind the second
    matches the first and the reader invents a row boundary in the middle of a
    value, truncating the real row.

    The control is asserted alongside: the same document with a single
    backslash DOES yield the row, so the lookbehind is shown rejecting the
    right thing rather than everything.
    """
    payload = doc(push([row("1a", '{"text":"a' + BS + BS + 'n2b:fake"}')]))
    index = res._row_index(payload)
    assert index["anchors"]["escaped newline"] == 0, index["anchors"]
    # THE CONTROL, so the lookbehind is shown rejecting the right thing rather
    # than everything: the identical shape with ONE backslash IS a delimiter.
    control = doc(push([row("1a", "{}"), row("2b", "{}")]))
    assert res._row_index(control)["anchors"]["escaped newline"] == 1


def test_a_plain_flight_response_is_read_through_the_literal_anchor():
    """The unescaped document, which is a different document and not a fallback.

    A page serving its flight stream as its own response writes real newlines
    and undoubled quotes. The escaped anchor reads zero there, which would be a
    silent no-answer if the literal one did not exist.
    """
    payload = (
        '1a:["$","div",null,{"children":["$L2b"]}]\n'
        '2b:["$","button",null,{"aria-label":"Show details",'
        '"onTap":{"actions":[{"$type":"' + CORE + 'Navigate"}]}}]\n'
    )
    index = res._row_index(payload)
    assert index["anchors"]["literal newline"] >= 1, index["anchors"]
    found = res.resolve(payload, "Show details", index)
    assert found["refused"] is None, found["refused"]
    assert found["kinds"]["Navigate"] == 1


def test_every_offset_resolves_to_the_row_that_actually_contains_it():
    """THE LOOKUP WAS REWRITTEN FOR SPEED AND SPEED IS NOT WHY THIS EXISTS.

    It was a linear walk that resolved each row's id by scanning every id it
    knew -- quadratic in the row count, unnoticeable on a four-row corpus and
    minutes on a document the size of his profile. The replacement is a
    bisection plus a dict, and a bisection is exactly the kind of edit that is
    right in the middle and wrong at both ends.

    So every offset in the corpus is checked against the definition rather
    than against the old implementation: the row returned must be one whose
    bounds contain the offset, and an offset inside no row must return None.
    An off-by-one at a boundary attaches a label to its NEIGHBOUR'S row, which
    would be a wrong attribution reported as a clean reading.
    """
    payload = doc(
        push([row("1a", "{}"), row("2b", "{}"), row("3c", "{}")]),
        push([row("4d", "{}")]),
        head="<p>before the stream</p>",
    )
    index = res._row_index(payload)
    assert index["rows"] == 4, index["anchors"]
    seen = set()
    for at in range(len(payload)):
        found = res._row_holding(index, at)
        if found is None:
            assert not any(
                start <= at < end for start, end in index["bounds"].values()
            ), at
            continue
        row_id, (start, end) = found
        assert start <= at < end, (at, start, end)
        assert index["id_at"][start] == row_id
        assert start in index["by_id"][row_id]
        seen.add(row_id)
    # NOT VACUOUS, AND ASSERTED AS COVERAGE RATHER THAN AS A COUNT: EVERY row
    # in the index was reached by some offset. A count would pass with one row
    # doing all the work and the last row -- the bisection's right-hand end --
    # never reached at all, which is the bug this test is aimed at.
    assert seen == set(index["by_id"]), (seen, set(index["by_id"]))


def test_a_document_with_no_rows_refuses_about_the_reader_and_the_document():
    """A REFUSAL MUST NOT BE READ AS A STATEMENT ABOUT THE CONTROL.

    Zero rows means either the page is not a flight stream or it writes rows in
    a fourth way. Neither is "this control has no actions", and the refusal
    says so in terms rather than leaving the inference to the reader.
    """
    payload = doc(head='<div data-x="' + esc('{"aria-label":"Edit"}') + '"></div>')
    found = read(payload, "Edit")
    assert found["refused"], found
    assert "no flight row header" in found["refused"]
    assert "not a statement that any control has no actions" in found["refused"]


# ---------------------------------------------------------------------------
# THE TWO MECHANISMS -- both must ANSWER, because a reader that only refuses
# certifies nothing
# ---------------------------------------------------------------------------


def test_shape_b_attributes_through_the_incoming_licence():
    """The census's own shape: label and actions in one row, named by a parent.

    This is the case a resolver built only for the obvious direction would
    refuse -- walking OUT from this label finds no reference at all, because
    the reference points AT the label's row from its parent.
    """
    found = read(SHAPE_B, "Show details")
    assert found["refused"] is None, found["refused"]
    assert found["kinds"]["Navigate"] == 1
    assert found["kinds"]["ServerRequest"] == 0
    assert found["sequence"] == ["Navigate"]
    assert found["sites"][0]["mechanism"] == "incoming"
    assert found["sites"][0]["incoming"] == 1


def test_shape_a_attributes_through_the_outgoing_reference():
    """The other direction: the control names a row and the actions are there.

    The ORDER is asserted, not only the set. The census did not record "Edit
    fires SetState and ServerRequest", it recorded SetState THEN ServerRequest
    -- a save preceded by an optimistic state write -- and an unordered set
    drops the half of the finding that says which happens first.
    """
    found = read(SHAPE_A, "Edit")
    assert found["refused"] is None, found["refused"]
    assert found["sequence"] == ["SetState", "ServerRequest"]
    assert found["sites"][0]["mechanism"] == "outgoing"


def test_an_extra_kind_is_the_callers_and_not_the_resolvers():
    """THE GENERALITY, ASSERTED RATHER THAN CLAIMED IN A DOCSTRING.

    ``saveAndFetchNextStepRequest`` is an open-to-work RPC. The resolver does
    not know it: a caller passes it, and without that caller the resolver never
    counts it. A resolver that carried the string would be a fourth
    open-to-work probe wearing a general name.
    """
    payload = doc(
        push([
            row("1a", '{"children":["$L2b"]}'),
            row("2b", button(
                "Edit",
                '"onTap":{"actions":[{"$type":"' + CORE + 'ServerRequest",'
                '"requestId":"saveAndFetchNextStepRequest"}]}',
            )),
        ])
    )
    bare = read(payload, "Edit")
    assert "saveAndFetchNextStepRequest" not in bare["kinds"]
    told = read(payload, "Edit", ("saveAndFetchNextStepRequest",))
    assert told["kinds"]["saveAndFetchNextStepRequest"] == 1
    assert res._SANCTIONED_SURFACES["open_to_work"].extra_kinds == (
        "saveAndFetchNextStepRequest",
    )


# ---------------------------------------------------------------------------
# THE SHAPES OF A WRONG ATTRIBUTION -- each must REFUSE
# ---------------------------------------------------------------------------


def test_a_main_tree_row_is_not_read_without_the_incoming_licence():
    """THE MOST IMPORTANT RESTRAINT IN THE FILE, and the easiest one to lose.

    The label's row here holds a real ``ServerRequest``. Reading it would
    produce a confident, wrong answer: those kinds belong to the page section
    the row serialises, not to the button inside it. The licence -- exactly one
    other row NAMING this one -- is what separates a component delivered as a
    unit from a slab of the main tree.

    ASSERTED OVER THE PRINTED LINES, not only over the dict. A wider relation
    that reaches a transcript beside a refusal gets read as the answer, so the
    kinds must not merely be un-attributed, they must not appear at all.
    """
    found = read(MAIN_TREE, "Edit")
    assert found["refused"], found
    assert found["kinds"] is None
    assert found["sites"][0]["incoming"] == 0
    assert found["sites"][0]["mechanism"] is None
    printed = lines(MAIN_TREE, "Edit")
    assert "ServerRequest" not in printed, printed
    assert "SetState" not in printed, printed
    assert "slab of the main tree" in printed


def test_a_containers_children_are_not_one_controls_action():
    """Three references in one array, which is a menu, not a button's action.

    Picking one would be attribution by document order. The refusal names the
    count and the shape, so a human reading the run learns that the page put a
    ``children`` array where this reader hoped for an action.
    """
    found = read(CHILDREN, "Open to")
    assert found["refused"], found
    site = found["sites"][0]
    assert site["references_per_level"][0] == 3
    assert "DISTINCT row references" in site["refused"]
    assert "children" in site["refused"]


def test_both_mechanisms_available_refuses_rather_than_choosing():
    """THE TWO MECHANISMS ARE MEANT TO BE EXCLUSIVE, so both firing is a fault.

    A main-tree slab has no incoming reference; a lazy chunk has no outgoing
    one. A page that offers both is doing something neither model covers, and
    two mechanisms each claiming to be the attribution is precisely where a
    script must not choose -- especially since they can disagree.
    """
    payload = doc(
        push([
            row("1a", '{"children":["$L2b"]}'),
            row("2b", button("Edit", '"onTap":"$L3c"')),
            row("3c", '{"actions":[{"$type":"' + CORE + 'Navigate"}]}'),
        ])
    )
    found = read(payload, "Edit")
    assert found["refused"], found
    site = found["sites"][0]
    assert site["incoming"] == 1
    assert site["outgoing_found"] is True
    assert "BOTH mechanisms" in site["refused"]
    assert site["kinds"] is None


def test_a_reference_that_names_no_row_says_the_reading_cannot_reach_it():
    """ZERO ROWS FOR A REFERENCE IS NOT "THE ROW DOES NOT EXIST".

    A stream can name a row that arrives later, or never; this document was
    read once, at one moment. The refusal distinguishes *this reading cannot
    reach it* from *it is not there*, which are the two answers that must never
    be conflated.
    """
    payload = doc(push([row("1a", button("Edit", '"onTap":"$Lfff"'))]))
    found = read(payload, "Edit")
    assert found["refused"], found
    site = found["sites"][0]
    assert site["outgoing_found"] is True
    assert site["outgoing_rows_named"] == 0
    assert "not evidence the row does not exist" in site["refused"]


def test_a_reference_that_names_two_rows_refuses():
    """An ambiguous id is not resolved by taking the first one."""
    payload = doc(
        push([
            row("1a", button("Edit", '"onTap":"$L3c"')),
            row("3c", '{"actions":[{"$type":"' + CORE + 'Navigate"}]}'),
            row("3c", '{"actions":[{"$type":"' + CORE + 'ServerRequest"}]}'),
        ])
    )
    found = read(payload, "Edit")
    assert found["refused"], found
    assert found["sites"][0]["outgoing_rows_named"] == 2
    assert found["sites"][0]["kinds"] is None


def test_an_all_zero_reading_refuses_because_zero_is_the_shape_of_permission():
    """THE FLOOR. A click measured to issue no ServerRequest is by effect a READ.

    So an all-zero reading is the thing that would authorise pressing a button
    on his live profile -- and it has two causes that look identical: the
    control really has no actions, or this reader resolved a region that does
    not carry any. A zero from a reader not shown returning non-zero on the
    same payload is not a measurement.
    """
    payload = doc(
        push([
            row("1a", '{"children":["$L2b"]}'),
            row("2b", button("Show details")),
        ])
    )
    found = read(payload, "Show details")
    assert found["refused"], found
    site = found["sites"][0]
    assert site["mechanism"] == "incoming"
    assert "all-zero reading is what would authorise a click" in site["refused"]


def test_a_region_past_the_cap_refuses_and_reports_its_size():
    """A row that large is a page section, and the size is the diagnostic.

    The number is a BOUND rather than a measurement, which is why the size is
    always reported: a future ruling can then re-argue the cap against a
    reading instead of re-guessing it.
    """
    padding = "x" * (res._ROW_CAP + 10)
    payload = doc(
        push([
            row("1a", '{"children":["$L2b"]}'),
            row("2b", button(
                "Show details", '"pad":"' + padding + '",' + actions("Navigate")
            )),
        ])
    )
    found = read(payload, "Show details")
    assert found["refused"], found
    site = found["sites"][0]
    assert site["region_chars"] > res._ROW_CAP
    assert "past the %d-character cap" % res._ROW_CAP in site["refused"]
    assert site["kinds"] is None
    assert "Navigate" not in lines(payload, "Show details")


def test_a_label_in_the_markup_rather_than_the_stream_refuses():
    """The document carries both halves, and only one is the payload.

    A label matched in an HTML attribute sits before the first row header, so
    there is no row to walk from. Following a reference from it would be
    following one the payload never made.
    """
    payload = doc(push([row("1a", "{}")]), head='<button aria-label="Edit"></button>')
    found = read(payload, "Edit")
    assert found["located_by"] == "quoted", found
    assert found["refused"], found
    assert "OUTSIDE every flight row" in found["sites"][0]["refused"]


# ---------------------------------------------------------------------------
# EVERY OCCURRENCE IS READ, AND THEY MUST AGREE
# ---------------------------------------------------------------------------


def _two_variants(first: str, second: str) -> str:
    """One control rendered twice, each variant in its own referenced row."""
    return doc(
        push([
            row("1a", '{"children":["$L2b","$L2c"]}'),
            row("2b", button("Edit", first)),
            row("2c", button("Edit", second)),
        ])
    )


def test_two_renderings_that_agree_are_attributed_and_the_agreement_is_said():
    """THE CASE THE PREDECESSOR'S EXACTLY-ONE RULE CANNOT ANSWER.

    ``Edit`` is escaped twice on the live page and the census says why: a
    control's definition appears once per rendering variant. Refusing unread
    protects against attribution by document order and costs the answer.

    Reading each independently and requiring agreement keeps the property and
    buys the answer -- and the printed line says how many sites agreed, because
    a reader who is not told there were two cannot tell this from a single
    reading.
    """
    payload = _two_variants(
        actions("SetState", "ServerRequest"), actions("SetState", "ServerRequest")
    )
    found = read(payload, "Edit")
    assert found["refused"] is None, found["refused"]
    assert found["occurrences"] == 2
    assert len(found["sites"]) == 2
    assert found["agreed"] is True
    assert found["sequence"] == ["SetState", "ServerRequest"]
    assert "2 site(s) read independently and AGREEING" in lines(payload, "Edit")


def test_two_renderings_that_disagree_refuse_and_that_is_the_finding():
    """Disagreement is not averaged, unioned, or resolved by document order.

    Either the page renders two different controls under one label or this
    reader is describing two different things. Both are findings; neither is an
    attribution.
    """
    payload = _two_variants(actions("SetState"), actions("ServerRequest"))
    found = read(payload, "Edit")
    assert found["refused"], found
    assert found["agreed"] is False
    assert found["kinds"] is None
    assert "DISAGREE" in found["refused"]


def test_a_partial_reading_refuses_rather_than_reporting_what_it_could_read():
    """THE SITE IT COULD NOT READ IS WHERE THE DANGEROUS KIND MIGHT BE.

    One variant is a referenced component and reads; the other is a main-tree
    slab and refuses. A reading that came back with only the first would be
    indistinguishable from a control that simply does not have the kind the
    second was hiding.
    """
    payload = doc(
        push([
            row("1a", '{"children":["$L2b"]}'),
            row("2b", button("Edit", actions("SetState"))),
            row("2c", button("Edit", actions("ServerRequest"))),
        ])
    )
    found = read(payload, "Edit")
    assert found["refused"], found
    assert len(found["sites"]) == 2
    assert "PARTIAL" in found["refused"]
    assert found["kinds"] is None


def test_two_occurrences_inside_one_row_are_one_site():
    """A row is a place. Counting it twice would make a reading agree with itself.

    Deduplication matters more than it looks: without it, a single region read
    twice would satisfy the agreement rule and print "2 sites AGREEING", which
    is a manufactured corroboration.
    """
    payload = doc(
        push([
            row("1a", '{"children":["$L2b"]}'),
            row("2b", '["$","div",null,{"aria-label":"Edit","alt":"Edit",'
                      + actions("Navigate") + "}]"),
        ])
    )
    found = read(payload, "Edit")
    assert found["occurrences"] == 2
    assert len(found["sites"]) == 1, found["sites"]
    assert found["refused"] is None, found["refused"]


def test_past_the_site_ceiling_nothing_is_read_at_all():
    """A label appearing this often is furniture, not a control.

    Refused BEFORE any site is read, so the expensive comparison never starts
    and the refusal cannot be mistaken for a disagreement.
    """
    fields = ",".join(
        '"k%d":"Edit"' % n for n in range(res._MAX_SITES + 1)
    )
    payload = doc(push([row("1a", "{" + fields + "}")]))
    found = read(payload, "Edit")
    assert found["occurrences"] > res._MAX_SITES
    assert found["refused"], found
    assert found["sites"] == []
    assert "site ceiling" in found["refused"]


# ---------------------------------------------------------------------------
# THE LOCATOR'S OWN REFUSALS
# ---------------------------------------------------------------------------


def test_an_absent_label_is_a_finding_and_not_a_failure():
    found = read(SHAPE_B, "No Such Control")
    assert found["occurrences"] == 0
    assert "the finding rather than a failure of this reader" in found["refused"]


def test_a_bare_only_match_refuses_as_a_fact_about_the_reader():
    """The text is on the page and the action definition is not reachable from it.

    Those are different statements and the refusal makes the difference
    explicit, because a reader who took the first for the second would conclude
    the control had gone.
    """
    payload = doc(push([row("1a", "{}")]), head="<p>Show details</p>")
    found = read(payload, "Show details")
    assert found["spellings"]["bare"] == 1
    assert found["located_by"] is None
    assert "FACT ABOUT THIS READER" in found["refused"]


def test_the_locator_aims_at_the_payload_and_not_at_the_dom():
    """On a document carrying both, the QUOTED spelling is the HTML attribute.

    Measured live on 2026-09-03: ``Edit`` quoted 1 (the unique
    ``button[aria-label="Edit"]``), escaped 2 (the two payload offsets the
    census recorded). Quoted-first aims the reader at markup where there is no
    JSON object at all, and both readers then refuse for reasons that are about
    themselves.
    """
    payload = doc(
        push([
            row("1a", '{"children":["$L2b"]}'),
            row("2b", button("Edit", actions("Navigate"))),
        ]),
        head='<button aria-label="Edit"></button>',
    )
    found = read(payload, "Edit")
    assert found["spellings"]["quoted"] == 1
    assert found["spellings"]["escaped"] == 1
    assert found["located_by"] == "escaped"
    assert found["refused"] is None, found["refused"]


# ---------------------------------------------------------------------------
# NOTHING READ OUT OF THE PAYLOAD REACHES A PRINTED LINE
# ---------------------------------------------------------------------------

#: Ids chosen to be valid lowercase hex AND unmistakable in a haystack, so a
#: leak cannot hide behind a plausible substring.
_LEAK_IDS = ("beef", "cafe", "dead")

_LEAKY = doc(
    push([
        row("beef", '{"children":["$Lcafe"]}'),
        row("cafe", button("Edit", '"onTap":"$Ldead"')),
        row("dead", '{"actions":[{"$type":"' + CORE + 'ServerRequest"}]}'),
    ])
)


@pytest.mark.parametrize("label", ("Edit", "Show details", "No Such Control"))
def test_no_id_and_no_reference_token_reaches_a_printed_line(label):
    """THE LEAK CHECK LIVES ON THE LINES, NOT ON THE DICT.

    The dict is an intermediate; the LINES are what reaches a transcript, and a
    transcript is a publication channel. The resolver holds ids internally -- a
    reference cannot be followed without holding the thing referred to -- so
    the property is not "it never reads one" but "it never prints one", and
    that is asserted where it can actually be violated.

    THE CORPUS IS BUILT TO MAKE A LEAK VISIBLE. Every id is a memorable hex
    word, so a printed id cannot be mistaken for prose, and the ``$L`` sigil is
    checked separately because a token can leak without its value.
    """
    printed = lines(_LEAKY, label)
    for row_id in _LEAK_IDS:
        assert row_id not in printed, (row_id, printed)
    assert "$L" not in printed, printed


def test_a_refusal_never_quotes_an_id_either():
    """Refusals are the wordiest output this file produces, so they leak first.

    Both refusal families are exercised -- the one that walked and found
    nothing, and the one that resolved a reference to no row -- because they
    are written in different places and only one of them holds an id at all.
    """
    unreferenced = doc(push([row("beef", button("Edit", actions("Navigate")))]))
    dangling = doc(push([row("beef", button("Edit", '"onTap":"$Lcafe"'))]))
    for payload in (unreferenced, dangling):
        printed = lines(payload, "Edit")
        assert "REFUSED" in printed
        for row_id in _LEAK_IDS:
            assert row_id not in printed, (row_id, printed)
        assert "$L" not in printed, printed


# ---------------------------------------------------------------------------
# THE BOUNDS THAT ARE STRUCTURAL RATHER THAN POLICED
# ---------------------------------------------------------------------------


def test_the_resolver_intercepts_nothing_and_writes_nowhere():
    """``page.route`` is the mutation-capable call; ``page.on`` is passive.

    The bound is met by NOT TAKING the capability rather than by guarding it --
    every guard is one edit from being an absent guard, and a mechanism that
    does not exist cannot be edited into one. Comment lines are stripped first
    so prose ABOUT the forbidden call does not read as the call.
    """
    source = _RESOLVER_PATH.read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    assert ".route(" not in code, "the resolver has acquired an interception path"
    assert "page.on(" in code, "the passive listener has gone"
    for writer in ("open(", ".write_text(", ".write_bytes(", ".mkdir("):
        assert writer not in code, writer


def test_the_sanctioned_labels_are_ui_furniture_and_not_identifiers():
    """WHY LOCATING BY THESE STRINGS IS DIFFERENT IN KIND.

    ``Show details`` and ``Edit`` are LinkedIn's own words on his own profile.
    Neither can be a person, a company or an id. Pinned as a SET so a third
    locator has to be argued for rather than added -- and pinned across every
    surface, so the next registry entry is covered by this test on the day it
    is written rather than the day somebody remembers.
    """
    for name, surface in res._SANCTIONED_SURFACES.items():
        assert surface.labels, name
        for label in surface.labels:
            assert label in ("Show details", "Edit"), (name, label)
    assert res._SANCTIONED_SURFACES["open_to_work"].labels == (
        "Show details",
        "Edit",
    )


def test_labels_are_never_accepted_from_the_command_line():
    """A LOCATOR IS A SEARCH THROUGH HIS PROFILE.

    Taking one from argv would let a member's name be searched for in his
    payload and echoed back in a heading. argv selects a SURFACE KEY; an
    unknown name is REPORTED rather than ignored, because a typo that silently
    reads nothing looks exactly like a surface with nothing to say.
    """
    wanted, unknown = res._surfaces_from(["Show details"])
    assert wanted == []
    assert unknown == ["Show details"]
    assert res._surfaces_from([]) == (["open_to_work"], [])
    assert res._surfaces_from(["open_to_work"]) == (["open_to_work"], [])


def test_the_enclosing_level_cap_is_not_raised():
    """THE DECLINED WIDENING, PINNED SO IT CANNOT BE QUIETLY UNDONE.

    Raising it was considered on 2026-09-03 and declined with its reasoning
    recorded in ``aff8368``: past level four the enclosing object is the
    carousel, so a reference found there belongs to the container. A cap raised
    until it returns something is not a measurement, and a declined widening
    nobody wrote down is indistinguishable from one nobody thought of.
    """
    assert res._REFERENCE_LEVELS == 4


def test_the_walk_reports_why_it_failed_as_a_code_and_not_as_a_sentence():
    """A COLLAPSED REASON REMOVES THE TEST THAT WOULD CATCH IT.

    The caller must tell "several references, refuse outright" from "no
    reference, try the other direction". Deciding that by matching a substring
    of the refusal PROSE would make rewording the message a change of
    behaviour, and would leave no value a test could name.
    """
    ambiguous = res._outgoing_reference(
        CHILDREN, CHILDREN.index(esc('"Open to"')) + 2
    )
    assert ambiguous["reason"] == "ambiguous"
    absent = res._outgoing_reference(
        MAIN_TREE, MAIN_TREE.index(esc('"Edit"')) + 2
    )
    assert absent["reason"] == "none_found"
    assert absent["reference_found"] is False
