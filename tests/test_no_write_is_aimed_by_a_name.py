"""No write is aimed by a name, and no debt is left.

THE RULING. ``PEOPLE-DATA-MITIGATIONS``, mitigation 6, NOT A TARGET BY ITSELF
(``_audit/2026-09-24-rulings-names-at-runtime.md``): "A name read off a page is
never used on its own to compose outward content or to choose a target;
MENTION-COMPOSITION-RULING stands. An outward act fires at the exact member the
operator names, by link or id, and the tool reports whom it resolved before it
acts." The orchestrator's order for lane G: no write spec may take a name as
its target; targets are links or ids the caller supplies.

WHAT THIS FILE HOLDS, on the write registry and on the tool surface:

1. Every ``target_kind`` in ``writes.SANCTIONED_WRITES`` is classified into the
   closed vocabulary ``TARGET_CLASSES``, one line of reason each. A new kind
   fails until somebody classifies it; a classified kind that left the
   registry fails as stale.
2. The actions whose kind is classified ``NAME`` are EXACTLY the keys of
   ``NAME_AIMED_DEBT`` -- EMPTY since 2026-09-27, and pinned empty by
   ``test_no_debt_is_left``: a new name-aimed write fails, and declaring it
   debt fails too. The machinery that held two debts stays, shown failing on
   plants, for the day a ruling declares one.
3. No field of a kind -- the kind itself, or each half of a composite -- is
   name-shaped unless the kind is classified ``NAME``, so a person-shaped field
   cannot be classified as an id to get past (2).
4. No write TOOL in ``server.py`` takes a name-shaped parameter beyond
   ``DEBT_PARAMETERS``, asserted exactly.

THE DEBT IS PAID -- both entries, 2026-09-27, lane L5, on the orchestrator's
order of 23:36. Two writes predated the ruling and were declared here, and a
declaration was a debt, not a waiver:

* ``send_invitation`` was aimed by ``member``, his own word for the person,
  matched against the invitation controls' labels. CONVERTED: it takes the
  person's profile link, compared in the page against each rail card's own
  link, and this file stayed red until its entry went, which is the design
  working.
* ``send_message`` was aimed by the ``member`` half of its target, a name
  typed into the recipient typeahead -- measured to commit nobody. RETIRED in
  favour of ``message_from_profile``, which reaches a person by their profile
  link: the tool, the spec and the name-aimed gates are gone.

HOW A WRITE TOOL IS FOUND, off ``server.py``'s syntax tree: an ``@mcp.tool()``
function whose body calls ``_write_tool``, the one function that reaches
``writes.preview``/``perform``/``consume``/``mint`` -- a second caller of those
fails here. Two more routes must agree with it: a decorated function whose name
is a registry ``tool_name``, and what ``mcp.list_tools()`` registers, whose
parameters must equal the syntax tree's.

THE LIMIT, plainly:

* It reads parameter NAMES and DECLARED kinds, not semantics. A name smuggled
  through a parameter called ``id`` or ``item``, or a kind classified ``id``
  whose values are really names, passes. The classification is a human claim;
  what is checked is that it exists, is complete, and agrees with field names.
* The name-shaped vocabulary is closed (plus any ``*_name`` or ``*_names``). A
  synonym outside it passes.
* It reads ``server.py`` and the registry only. A write reached another way is
  outside it; ``tests/test_readonly.py``'s mutation scanner watches mutating
  calls package-wide.
* It cannot stop a CLIENT copying a name a people read returned into a write's
  argument. It makes true that no write has a parameter through which a name
  is the aim.
* Mitigation 6's second sentence, reporting whom it resolved before acting, is
  behaviour and is not asserted here. ``send_invitation``'s preview names the
  person on the one rail card its link matched
  (``writes._name_the_invitation_recipient``, exercised in
  ``tests/test_writes_nine.py`` and
  ``tests/test_an_invitation_is_aimed_by_a_link.py``).
* MENTION-COMPOSITION-RULING's source rule -- a mention is never assembled from
  a name read off a page -- is held elsewhere: ``tests/test_typed_bytes.py``
  (every typed string is a bare slice of the caller's own target, never
  composed) and ``tests/test_no_write_tool_names_a_third_party.py`` (no tool
  takes a mention, tag or collaborator parameter).
"""

from __future__ import annotations

import ast
import dataclasses
import functools
import pathlib

import pytest

from linkedin_server import writes

REPO = pathlib.Path(__file__).resolve().parent.parent
SERVER = REPO / "linkedin_server" / "server.py"

# ---------------------------------------------------------------------------
# The declarations
# ---------------------------------------------------------------------------

#: The class meaning the target is CHOSEN BY A NAME.
NAME_CLASS = "NAME"

#: THE CLOSED VOCABULARY a target kind is classified into, each class saying
#: what the write fires at and who chose it.
TARGET_CLASSES: dict[str, str] = {
    "id": "an identifier the caller supplies: a numeric id or a urn",
    "self": "his own profile or account; no third party is chosen at all",
    "own_text": "his own words, which are the whole target",
    "id_and_own_text": "an identifier the caller supplies, and his own words",
    "own_field_and_value": "a field of HIS OWN profile, and the value he gives it",
    "closed_setting_and_value": (
        "one of his own settings, admitted by name, and a state from a closed set"
    ),
    # ADDED AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), for the two
    # named-person acts: a PERSON chosen by the caller, by an address or an
    # id -- not "id" above, which names no person, and not NAME, which is
    # the word the parser refuses.
    "profile_link_or_member_id": (
        "a person's profile link or member id the caller supplies; a bare "
        "word, which could be a name, is refused before a browser opens"
    ),
    "profile_link_or_member_id_and_own_text": (
        "a person's profile link or member id the caller supplies, and his "
        "own words"
    ),
    # ADDED BY LANE U (2026-10-10), for send_attachment: an identifier the
    # caller supplies and a FILE he put in the declared upload root -- not
    # his words, and not a person.
    "id_and_own_file": (
        "an identifier the caller supplies, and a file of his own from the "
        "declared upload root"
    ),
    NAME_CLASS: "a word for a person, matched against what the page draws",
}

#: EVERY target_kind in writes.SANCTIONED_WRITES, classified, one line each.
TARGET_KIND_CLASS: dict[str, tuple[str, str]] = {
    "job_id": (
        "id",
        "a posting id; writes._target_for refuses anything but six or more digits",
    ),
    "company_id": (
        "id",
        "a company id; writes._target_for refuses a name outright, as names collide",
    ),
    "item_urn": (
        "id",
        "a feed item urn; the spec's url_pattern refuses any other shape at the door",
    ),
    "self": (
        "self",
        "his own profile; writes._target_for accepts only self, me or empty",
    ),
    "post_text": (
        "own_text",
        "the post itself, typed as a bare slice of the target and never composed",
    ),
    "item_and_text": (
        "id_and_own_text",
        "an item urn, pattern-checked where it enters the url, and his comment",
    ),
    "field_and_value": (
        "own_field_and_value",
        "a control in his OWN intro editor, and the value he supplies for it",
    ),
    "setting_and_value": (
        "closed_setting_and_value",
        "dark mode, admitted by name at the tool, and one of its three states",
    ),
    "thread_and_text": (
        "id_and_own_text",
        "send_reply: a thread id the caller supplies, shape-checked, never read off a page",
    ),
    "thread_and_file": (
        "id_and_own_file",
        "send_attachment: the same thread id, and a file in the declared root, held root-relative",
    ),
    "group_id": (
        "id",
        "withdraw_from_group: a numeric group id the caller supplies, 1 to 20 ASCII digits",
    ),
    # 2026-11-25, lane build-jmn26 (census J 31): the search-alert pair. The
    # target is wholly his own words -- keywords and a location, composed by
    # search_alert_switch.query_for into one query -- and it addresses his own
    # alert on that search; it chooses no person.
    "job_search": (
        "own_text",
        "set_search_job_alert / unset_search_job_alert: his own keywords and "
        "location, composed into one search's query, which picks no person",
    ),
    # LANE L5'S TWO, classified at its merge of master 52b55b6 (2026-09-27).
    # The parser is writes._target_for -> named_profile.parse_profile_target.
    "profile": (
        "profile_link_or_member_id",
        "connect_from_profile: /in/<segment>/ or an ACoAA member id; a bare word is refused",
    ),
    "profile_and_text": (
        "profile_link_or_member_id_and_own_text",
        "message_from_profile: the same parser for the profile half, and his own one line",
    ),
    # 2026-11-24, lane builds-26: the endorsement pair. The person is chosen
    # by the link, through the same parser; the skill chooses one of THEIR
    # skills, compared in the page, and never chooses a person.
    "profile_and_skill": (
        "profile_link_or_member_id_and_own_text",
        "endorse_skill / withdraw_endorsement: the same parser for the profile "
        "half, and his own words for the skill, which picks no person",
    ),
    # PAID 2026-09-27 (lane L5, the orchestrator's order of 23:36): the
    # ``member`` kind -- send_invitation's needle, his word for a person,
    # matched against labels -- left the registry. Its replacement is here.
    "rail_profile": (
        "profile_link_or_member_id",
        "send_invitation: /in/<segment>/ or an ACoAA id, compared in the page with each rail card's link",
    ),
    # 2026-11-26, lane build-net2 (N 15, N 16, N 10): the three invitation
    # answers. The parser is writes._target_for -> named_profile.profile_segment.
    "invitation_profile": (
        "profile_link_or_member_id",
        "accept / ignore / withdraw an invitation: /in/<segment>/ or an ACoAA id, compared in the page with the manager row's own links",
    ),
    # PAID 2026-09-27: ``member_and_text`` -- send_message's subject half, a
    # name typed into the recipient typeahead -- left the registry with that
    # action, which was retired rather than converted.
}

#: THE NAME-AIMED WRITES THAT EXIST TODAY. Declared, not waived.
#:
#: EMPTY SINCE 2026-09-27, both entries paid on lane L5's order of 23:36:
#: ``send_invitation``'s by conversion (the person's profile link, kind
#: ``rail_profile``) and ``send_message``'s by retirement. ``test_no_debt_is_left``
#: pins it empty -- a new entry is a ruling change, not an edit here.
NAME_AIMED_DEBT: dict[str, str] = {}

#: The (tool, parameter) through which each debt write takes its name. Empty
#: with the table above: ``("linkedin_send_invitation", "member")`` and
#: ``("linkedin_send_message", "member")`` went with their entries.
DEBT_PARAMETERS: frozenset[tuple[str, str]] = frozenset()

#: PARAMETER NAMES THAT SAY THEY HOLD A PERSON, and say nothing of a link or
#: an id. Compared exactly, lower-cased. ``member`` is here because THIS
#: registry used it for a name needle (``linkedin_send_invitation`` until
#: 2026-09-27); a write taking a member link or id says so in its
#: parameter's name -- ``profile``, as the three named-person writes do.
NAME_SHAPED_PARAMETERS = frozenset(
    {
        "name",
        "names",
        "full_name",
        "display_name",
        "first_name",
        "last_name",
        "person",
        "persons",
        "people",
        "person_name",
        "recipient",
        "recipients",
        "recipient_name",
        "member",
        "members",
        "member_name",
        "who",
        "author",
        "authors",
        "mention",
        "mentions",
    }
)

#: And any parameter that calls itself a name, whatever it is the name of.
NAME_SHAPED_SUFFIXES = ("_name", "_names")

#: The write tools on this tree, measured 2026-09-27 off server.py and
#: mcp.list_tools(): fourteen, for fifteen sanctioned actions --
#: set_open_to_work registers no tool. Re-measured the same day on lane G's
#: merge of master 2eb90ad: fifteen, for sixteen, with lane L5's send_reply;
#: and on its merge of master 7986ae3: sixteen, for seventeen, with lane L8's
#: withdraw_from_group; and on lane L5's merge of master 52b55b6: eighteen,
#: for nineteen, with connect_from_profile and message_from_profile; and on
#: lane L5's order of 2026-09-27 23:36: seventeen, for eighteen, with
#: send_message retired.
KNOWN_WRITE_TOOLS = frozenset(
    {
        "linkedin_connect_from_profile",
        "linkedin_message_from_profile",
        "linkedin_withdraw_from_group",
        "linkedin_send_reply",
        "linkedin_save_job",
        "linkedin_unsave_job",
        "linkedin_apply_job",
        "linkedin_unfollow_company",
        "linkedin_follow_company",
        "linkedin_follow_company_page",
        "linkedin_mark_company_interest",
        "linkedin_set_similar_jobs_alert",
        "linkedin_unset_similar_jobs_alert",
        "linkedin_set_search_job_alert",
        "linkedin_unset_search_job_alert",
        # Lane build-net2, 2026-11-26: the three invitation answers.
        "linkedin_accept_invitation_to_connect",
        "linkedin_ignore_invitation_to_connect",
        "linkedin_withdraw_invitation",
        "linkedin_publish_post",
        "linkedin_comment_on_item",
        "linkedin_react_to_item",
        "linkedin_update_profile_field",
        "linkedin_update_setting",
        "linkedin_send_invitation",
    }
)

#: The one function in server.py that reaches the write path, and the calls
#: on ``writes`` that ARE the write path.
WRITE_DOOR = "_write_tool"
WRITE_PATH = frozenset({"preview", "perform", "consume", "mint"})

# ---------------------------------------------------------------------------
# The instruments -- pure functions, so every control runs the same code
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ToolDef:
    """One ``@mcp.tool()`` function, as its syntax tree states it."""

    name: str
    parameters: tuple[str, ...]
    #: One entry per call to the door in its body: the action literal, or
    #: None where the action is not a string literal.
    door_actions: tuple[str | None, ...]


@functools.lru_cache(maxsize=1)
def _server_tree() -> ast.Module:
    return ast.parse(SERVER.read_text(encoding="utf-8"))


def _is_tool_decorator(node: ast.expr) -> bool:
    target = node.func if isinstance(node, ast.Call) else node
    return (
        isinstance(target, ast.Attribute)
        and target.attr == "tool"
        and isinstance(target.value, ast.Name)
        and target.value.id == "mcp"
    )


def _parameters(function: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, ...]:
    args = function.args
    names = [a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)]
    if args.vararg is not None:
        names.append(args.vararg.arg)
    if args.kwarg is not None:
        names.append(args.kwarg.arg)
    return tuple(names)


def _door_action(call: ast.Call) -> str | None:
    if call.args:
        first = call.args[0]
    else:
        first = next((k.value for k in call.keywords if k.arg == "action"), None)
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return None


def tool_definitions(tree: ast.Module) -> dict[str, ToolDef]:
    """Every ``@mcp.tool()`` function in ``tree``, with its door calls."""
    out: dict[str, ToolDef] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(_is_tool_decorator(d) for d in node.decorator_list):
            continue
        door = tuple(
            _door_action(call)
            for call in ast.walk(node)
            if isinstance(call, ast.Call)
            and isinstance(call.func, ast.Name)
            and call.func.id == WRITE_DOOR
        )
        out[node.name] = ToolDef(node.name, _parameters(node), door)
    return out


def _registry_tool_names(registry) -> set[str]:
    return {spec.tool_name for spec in registry.values()}


def write_tools(tools: dict[str, ToolDef], registry) -> dict[str, ToolDef]:
    """The UNION of both routes, so a tool found by only one is still checked."""
    named = _registry_tool_names(registry)
    return {n: t for n, t in tools.items() if t.door_actions or n in named}


def route_disagreements(tools: dict[str, ToolDef], registry) -> tuple[list[str], list[str]]:
    """(calls the door but no spec is named after it, named after a spec but
    does not call the door)."""
    by_door = {n for n, t in tools.items() if t.door_actions}
    by_name = {n for n in tools if n in _registry_tool_names(registry)}
    return sorted(by_door - by_name), sorted(by_name - by_door)


def door_pairing_defects(tools: dict[str, ToolDef], registry) -> list[str]:
    """A write tool must hand the door its OWN spec's action, as a literal.

    The classification is per ACTION and the signature check per TOOL; this
    pairing is what joins the two.
    """
    by_tool = {spec.tool_name: spec for spec in registry.values()}
    out: list[str] = []
    for name, tool in sorted(tools.items()):
        if not tool.door_actions:
            continue
        spec = by_tool.get(name)
        expected = {spec.action} if spec is not None else set()
        if set(tool.door_actions) != expected:
            out.append(
                "%s hands the door %s; its spec's action is %s"
                % (name, list(tool.door_actions), sorted(expected))
            )
    return out


def direct_write_path_callers(tree: ast.Module) -> list[str]:
    """Every function calling ``writes.<preview|perform|consume|mint>`` itself."""
    callers: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for call in ast.walk(node):
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr in WRITE_PATH
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "writes"
            ):
                callers.add(node.name)
    return sorted(callers)


def is_name_shaped(parameter: str) -> bool:
    lowered = parameter.lower()
    return lowered in NAME_SHAPED_PARAMETERS or lowered.endswith(NAME_SHAPED_SUFFIXES)


def name_shaped_parameters(tools: dict[str, ToolDef]) -> set[tuple[str, str]]:
    return {
        (tool.name, parameter)
        for tool in tools.values()
        for parameter in tool.parameters
        if is_name_shaped(parameter)
    }


def classification_drift(registry, classification) -> tuple[list[str], list[str]]:
    """(kinds in the registry nobody classified, classified kinds it no longer has)."""
    present = {spec.target_kind for spec in registry.values()}
    declared = set(classification)
    return sorted(present - declared), sorted(declared - present)


def vocabulary_defects(classification, vocabulary) -> list[str]:
    out: list[str] = []
    for kind, (klass, reason) in sorted(classification.items()):
        if klass not in vocabulary:
            out.append("%s: class %r is not in TARGET_CLASSES" % (kind, klass))
        if not reason.strip() or "\n" in reason:
            out.append("%s: needs a one-line reason" % kind)
    return out


def name_aimed_actions(registry, classification) -> set[str]:
    return {
        spec.action
        for spec in registry.values()
        if classification.get(spec.target_kind, ("", ""))[0] == NAME_CLASS
    }


def debt_drift(registry, classification, debt) -> tuple[list[str], list[str]]:
    """(aimed by a name and not declared, declared and no longer aimed by one)."""
    aimed = name_aimed_actions(registry, classification)
    return sorted(aimed - set(debt)), sorted(set(debt) - aimed)


#: What every debt entry must say, compared case-insensitively.
DEBT_ENTRY_MUST_SAY = (
    "PEOPLE-DATA-MITIGATIONS",
    "mitigation 6",
    "debt, not a waiver",
    "link or member id",
)


def debt_entry_defects(debt) -> list[str]:
    out: list[str] = []
    for action, entry in sorted(debt.items()):
        for phrase in DEBT_ENTRY_MUST_SAY:
            if phrase.lower() not in entry.lower():
                out.append("%s: its entry does not say %r" % (action, phrase))
    return out


def _fields_of(kind: str, composite) -> tuple[str, ...]:
    """The names a target kind's values arrive under: each half of a
    composite, or the kind itself for a one-part target."""
    parts = composite.get(kind)
    if parts is None:
        return (kind,)
    return tuple(part for part in parts if part)


def misclassified_name_fields(registry, classification, composite) -> list[tuple[str, str]]:
    """Name-shaped fields on a kind NOT classified NAME."""
    kinds = sorted({spec.target_kind for spec in registry.values()})
    return [
        (kind, field)
        for kind in kinds
        for field in _fields_of(kind, composite)
        if is_name_shaped(field)
        and classification.get(kind, ("", ""))[0] != NAME_CLASS
    ]


def surface_disagreements(ast_side: dict, live_side: dict) -> list[str]:
    """Where the syntax tree's write tools and the registered ones differ."""
    out: list[str] = []
    for name in sorted(set(ast_side) | set(live_side)):
        if name not in live_side:
            out.append("%s: in server.py's syntax tree, not registered" % name)
        elif name not in ast_side:
            out.append("%s: registered, not found in server.py's syntax tree" % name)
        elif sorted(ast_side[name]) != sorted(live_side[name]):
            out.append(
                "%s: syntax tree %s, registered %s"
                % (name, sorted(ast_side[name]), sorted(live_side[name]))
            )
    return out


def _live_parameter_names(tool) -> tuple[str, ...]:
    schema = getattr(tool, "parameters", None)
    if schema is None:
        schema = getattr(tool, "inputSchema", None)
    assert isinstance(schema, dict), (
        "cannot read the registered input schema of %s" % getattr(tool, "name", tool)
    )
    return tuple(sorted(schema.get("properties", {})))


def _real_write_tools() -> dict[str, ToolDef]:
    return write_tools(tool_definitions(_server_tree()), writes.SANCTIONED_WRITES)


# ---------------------------------------------------------------------------
# The rule, on this repository
# ---------------------------------------------------------------------------


def test_every_target_kind_in_the_registry_is_classified():
    unclassified, stale = classification_drift(
        writes.SANCTIONED_WRITES, TARGET_KIND_CLASS
    )
    assert not unclassified, (
        "target_kind %s is in writes.SANCTIONED_WRITES and not in "
        "TARGET_KIND_CLASS. Classify it, with a one-line reason: does the "
        "write fire at a link or id the caller supplies, or is the target "
        "chosen by a name? PEOPLE-DATA-MITIGATIONS mitigation 6 allows only "
        "the first." % unclassified
    )
    assert not stale, (
        "TARGET_KIND_CLASS classifies %s, which no spec in "
        "writes.SANCTIONED_WRITES uses any more. Delete the stale entry." % stale
    )


def test_every_classification_is_in_the_closed_vocabulary():
    defects = vocabulary_defects(TARGET_KIND_CLASS, TARGET_CLASSES)
    assert defects == [], (
        "TARGET_KIND_CLASS: %s. A class is one of TARGET_CLASSES, and a new "
        "class is a vocabulary change argued for there, not a spelling." % defects
    )


def test_the_name_aimed_writes_are_exactly_the_declared_debt():
    undeclared, converted = debt_drift(
        writes.SANCTIONED_WRITES, TARGET_KIND_CLASS, NAME_AIMED_DEBT
    )
    assert not undeclared, (
        "%s is aimed by a name: its target_kind is classified NAME. "
        "PEOPLE-DATA-MITIGATIONS mitigation 6: an outward act fires at the "
        "exact member the operator names, by link or id. Take a link or member "
        "id the caller supplies. Adding it to NAME_AIMED_DEBT is a ruling "
        "change, not a fix." % undeclared
    )
    assert not converted, (
        "%s is no longer aimed by a name. The debt is paid: delete its "
        "NAME_AIMED_DEBT entry and its DEBT_PARAMETERS pair." % converted
    )


def test_no_debt_is_left():
    """THE ORDER OF 2026-09-27 23:36, held: no write is aimed by a name, so
    nothing is declared. Both declarations are EMPTY. A name-aimed write fails
    ``test_the_name_aimed_writes_are_exactly_the_declared_debt``; declaring it
    here to get past that fails this -- a debt is a ruling change, argued in
    the rulings register, not an edit to this table."""
    assert NAME_AIMED_DEBT == {}, sorted(NAME_AIMED_DEBT)
    assert DEBT_PARAMETERS == frozenset(), sorted(DEBT_PARAMETERS)
    assert name_aimed_actions(writes.SANCTIONED_WRITES, TARGET_KIND_CLASS) == set()


def test_each_debt_entry_names_the_ruling_and_is_not_a_waiver():
    defects = debt_entry_defects(NAME_AIMED_DEBT)
    assert defects == [], (
        "NAME_AIMED_DEBT: %s. An entry that stops naming its ruling, or stops "
        "saying it is debt, reads as a waiver." % defects
    )


def test_the_debt_parameters_belong_to_the_debt_writes():
    debt_tools = {
        spec.tool_name
        for spec in writes.SANCTIONED_WRITES.values()
        if spec.action in NAME_AIMED_DEBT
    }
    declared = {tool for tool, _ in DEBT_PARAMETERS}
    assert declared == debt_tools, (
        "DEBT_PARAMETERS names tools %s; the NAME_AIMED_DEBT actions' tools are "
        "%s. The two declarations of one debt must agree."
        % (sorted(declared), sorted(debt_tools))
    )


def test_no_name_shaped_field_sits_on_a_kind_not_classified_name():
    offenders = misclassified_name_fields(
        writes.SANCTIONED_WRITES, TARGET_KIND_CLASS, writes._COMPOSITE_TARGET_KINDS
    )
    assert offenders == [], (
        "(kind, field) %s: a name-shaped field on a kind classified as "
        "something other than NAME. Either the field takes a link or id and "
        "its name should say so, or the kind is aimed by a name and its "
        "classification is wrong." % offenders
    )


def test_the_write_door_is_the_only_caller_of_the_write_path():
    callers = direct_write_path_callers(_server_tree())
    assert callers == [WRITE_DOOR], (
        "server.py functions calling writes.%s directly: %s. The write-tool "
        "finder recognises a write by its call to %s; a second door would hide "
        "its tools from it. Route through %s, or teach the finder the new door."
        % ("/".join(sorted(WRITE_PATH)), callers, WRITE_DOOR, WRITE_DOOR)
    )


def test_the_finder_finds_the_known_write_tools():
    """The finder's control on the real tree: EACH route finds every write
    tool measured today, and each tool hands the door its own spec's action.

    Per route, not on the union: with the door renamed the name route alone
    still finds all fourteen, and a union-only check would stay green.
    """
    tools = tool_definitions(_server_tree())
    by_door = {n for n, t in tools.items() if t.door_actions}
    by_name = {n for n in tools if n in _registry_tool_names(writes.SANCTIONED_WRITES)}
    for route, found in (("door", by_door), ("name", by_name)):
        missing = sorted(KNOWN_WRITE_TOOLS - found)
        assert not missing, (
            "the %s route of the write-tool finder no longer finds %s. A finder "
            "that finds nothing checks nothing: was %s renamed, or a tool "
            "registered some other way?" % (route, missing, WRITE_DOOR)
        )
    assert {tool for tool, _ in DEBT_PARAMETERS} <= by_door
    pairing = door_pairing_defects(tools, writes.SANCTIONED_WRITES)
    assert pairing == [], (
        "%s. The classification is per action and the signature check per "
        "tool; a tool handing the door another action, or no literal, "
        "separates the two." % pairing
    )


def test_the_door_route_and_the_name_route_agree():
    door_only, name_only = route_disagreements(
        tool_definitions(_server_tree()), writes.SANCTIONED_WRITES
    )
    assert not door_only, (
        "%s call %s and no spec in writes.SANCTIONED_WRITES is named after "
        "them" % (door_only, WRITE_DOOR)
    )
    assert not name_only, (
        "%s carry a registry tool_name and never call %s. Both are still "
        "checked for name-shaped parameters, but the finder no longer "
        "describes the surface: teach it this route." % (name_only, WRITE_DOOR)
    )


async def test_the_syntax_tree_reads_the_surface_the_server_registers():
    """What a client sees is the registered schema. Its write tools and their
    parameters must be the ones read off the syntax tree."""
    from linkedin_server.server import mcp

    registry_names = _registry_tool_names(writes.SANCTIONED_WRITES)
    live = {
        tool.name: _live_parameter_names(tool)
        for tool in await mcp.list_tools()
        if tool.name in registry_names
    }
    ast_side = {name: tool.parameters for name, tool in _real_write_tools().items()}
    assert live, "no registered tool carries a registry tool_name"
    disagreements = surface_disagreements(ast_side, live)
    assert disagreements == [], (
        "%s. The signature check reads server.py's syntax tree; a client reads "
        "the registered schema. Where they differ, the check is not reading "
        "what a caller is offered." % disagreements
    )


def test_no_write_tool_takes_a_name_shaped_parameter_beyond_the_debt():
    found = name_shaped_parameters(_real_write_tools())
    extra = sorted(found - DEBT_PARAMETERS)
    gone = sorted(DEBT_PARAMETERS - found)
    assert not extra, (
        "(tool, parameter) %s: a write tool takes a name-shaped parameter. "
        "PEOPLE-DATA-MITIGATIONS mitigation 6: targets are links or ids the "
        "caller supplies. Take one, and name the parameter for it -- "
        "member_id, profile_link. Renaming a name-carrying parameter to get "
        "past this is the failure, not the fix." % extra
    )
    assert not gone, (
        "(tool, parameter) %s no longer takes a name. The debt is paid: delete "
        "the pair from DEBT_PARAMETERS and the action from NAME_AIMED_DEBT."
        % gone
    )


# ---------------------------------------------------------------------------
# Controls -- each check shown failing on a plant built here, never by
# editing product code
# ---------------------------------------------------------------------------

#: A spec to copy. Only ``action``, ``tool_name`` and ``target_kind`` are
#: read by the checks above.
_TEMPLATE = next(iter(writes.SANCTIONED_WRITES.values()))


def _planted_spec(action: str, kind: str) -> writes.WriteSpec:
    return dataclasses.replace(
        _TEMPLATE, action=action, tool_name="linkedin_" + action, target_kind=kind
    )


def _registry_with(action: str, kind: str) -> dict:
    planted = dict(writes.SANCTIONED_WRITES)
    planted["linkedin_" + action] = _planted_spec(action, kind)
    return planted


#: A NAME-CLASSIFIED KIND, planted in a COPY of the classification and never in
#: ``TARGET_KIND_CLASS``. The controls below stood on the real debt entries
#: until 2026-09-27, when the first was paid; built on this plant instead,
#: each keeps failing where it should whether the real table holds one entry
#: or none.
_PLANTED_NAME_KIND = "planted_name"


def _classification_with_a_name_kind() -> dict:
    classification = dict(TARGET_KIND_CLASS)
    classification[_PLANTED_NAME_KIND] = (NAME_CLASS, "a planted word for a person")
    return classification


#: A planted debt entry that says everything an entry must.
_PLANTED_DEBT = {
    "planted_write": (
        "PEOPLE-DATA-MITIGATIONS, mitigation 6: planted. Debt, not a waiver: "
        "converting this write to a link or member id supplied by the caller "
        "fails this file until the entry goes."
    )
}


#: A server source, planted. PARAM is replaced per case. The read tool and the
#: undecorated helper are there to be NOT found.
_PLANTED_SERVER = '''
@mcp.tool()
async def linkedin_planted_write(PARAM: str, confirm_token: str = ""):
    return await _write_tool("planted_write", PARAM, confirm_token)


@mcp.tool()
async def linkedin_planted_read(name: str):
    return {"read": name}


async def _planted_helper(name: str):
    return await _write_tool("planted_write", name, "")
'''


def test_control_an_unclassified_kind_fails_and_so_does_a_stale_one():
    planted = _registry_with("planted_write", "planted_kind")
    assert classification_drift(planted, TARGET_KIND_CLASS) == (["planted_kind"], [])

    without = {
        key: spec
        for key, spec in writes.SANCTIONED_WRITES.items()
        if spec.target_kind != "item_urn"
    }
    assert classification_drift(without, TARGET_KIND_CLASS) == ([], ["item_urn"])

    assert classification_drift(writes.SANCTIONED_WRITES, TARGET_KIND_CLASS) == ([], [])


def test_control_a_class_outside_the_vocabulary_fails():
    typo = dict(TARGET_KIND_CLASS)
    typo["rail_profile"] = ("Name", "the name class, misspelled")
    assert vocabulary_defects(typo, TARGET_CLASSES) == [
        "rail_profile: class 'Name' is not in TARGET_CLASSES"
    ]
    two_lines = dict(TARGET_KIND_CLASS)
    two_lines["job_id"] = ("id", "a reason\nthat runs on")
    assert vocabulary_defects(two_lines, TARGET_CLASSES) == [
        "job_id: needs a one-line reason"
    ]


def test_control_a_name_aimed_write_outside_the_debt_fails():
    planted = _registry_with("planted_write", _PLANTED_NAME_KIND)
    classification = _classification_with_a_name_kind()
    assert debt_drift(planted, classification, NAME_AIMED_DEBT) == (
        ["planted_write"],
        [],
    )
    # Declared, the same plant passes: the check reads the table.
    declared = {**NAME_AIMED_DEBT, **_PLANTED_DEBT}
    assert debt_drift(planted, classification, declared) == ([], [])
    assert debt_drift(
        writes.SANCTIONED_WRITES, TARGET_KIND_CLASS, NAME_AIMED_DEBT
    ) == ([], [])


def test_control_the_debt_table_with_an_entry_removed_fails():
    planted = _registry_with("planted_write", _PLANTED_NAME_KIND)
    classification = _classification_with_a_name_kind()
    declared = {**NAME_AIMED_DEBT, **_PLANTED_DEBT}
    assert debt_drift(planted, classification, declared) == ([], [])
    shrunk = {k: v for k, v in declared.items() if k != "planted_write"}
    assert debt_drift(planted, classification, shrunk) == (["planted_write"], [])
    # The signature half: a planted tool taking ``member``, its pair declared
    # and then removed.
    tools = write_tools(
        tool_definitions(ast.parse(_PLANTED_SERVER.replace("PARAM", "member"))),
        writes.SANCTIONED_WRITES,
    )
    pair = ("linkedin_planted_write", "member")
    assert sorted(name_shaped_parameters(tools) - (DEBT_PARAMETERS | {pair})) == []
    assert sorted(name_shaped_parameters(tools) - DEBT_PARAMETERS) == [pair]
    # And on this tree the declared pairs are exactly what the tools take.
    assert name_shaped_parameters(_real_write_tools()) == DEBT_PARAMETERS


def test_control_a_converted_debt_write_fails_until_its_entry_goes():
    """The debt has to be paid in the table, not only in the code -- which
    is what happened for real on 2026-09-27, when ``send_invitation`` took a
    profile link and this file stayed red until its entry went."""
    # A declared debt whose write is aimed by a profile link now.
    planted = _registry_with("planted_write", "profile")
    declared = {**NAME_AIMED_DEBT, **_PLANTED_DEBT}
    assert debt_drift(planted, TARGET_KIND_CLASS, declared) == ([], ["planted_write"])

    # The signature half: the pair declared, the tool's parameter renamed.
    pair = ("linkedin_planted_write", "member")
    tools = write_tools(
        tool_definitions(ast.parse(_PLANTED_SERVER.replace("PARAM", "member_link"))),
        writes.SANCTIONED_WRITES,
    )
    found = name_shaped_parameters(tools)
    assert pair not in found
    assert sorted((DEBT_PARAMETERS | {pair}) - found) == sorted(DEBT_PARAMETERS | {pair})


@pytest.mark.parametrize("parameter", ["name", "member", "recipient_full_name"])
def test_control_a_name_parameter_on_a_planted_write_tool_fails(parameter):
    tools = tool_definitions(ast.parse(_PLANTED_SERVER.replace("PARAM", parameter)))
    found = write_tools(tools, writes.SANCTIONED_WRITES)
    # The finder: the write tool, and neither the read tool nor the helper.
    assert sorted(found) == ["linkedin_planted_write"]
    assert found["linkedin_planted_write"].door_actions == ("planted_write",)
    assert name_shaped_parameters(found) == {("linkedin_planted_write", parameter)}


@pytest.mark.parametrize("parameter", ["member_id", "member_link", "profile_url", "item"])
def test_a_link_or_id_parameter_is_not_name_shaped(parameter):
    """The discriminating half: what a converted write looks like passes."""
    tools = tool_definitions(ast.parse(_PLANTED_SERVER.replace("PARAM", parameter)))
    assert name_shaped_parameters(write_tools(tools, writes.SANCTIONED_WRITES)) == set()


def test_control_a_name_field_classified_as_an_id_fails():
    planted = _registry_with("planted_write", "person_and_text")
    composite = dict(writes._COMPOSITE_TARGET_KINDS)
    composite["person_and_text"] = ("person", "text")
    classification = dict(TARGET_KIND_CLASS)
    classification["person_and_text"] = ("id_and_own_text", "claimed to be an id")
    assert misclassified_name_fields(planted, classification, composite) == [
        ("person_and_text", "person")
    ]
    # The debt check alone passes this plant, which is why the check above exists.
    assert debt_drift(planted, classification, NAME_AIMED_DEBT) == ([], [])


def test_control_a_second_door_fails():
    tree = ast.parse(
        "async def _write_tool(action, target, confirm_token):\n"
        "    return await writes.perform(None, None, None)\n"
        "\n"
        "async def _second_door(grant):\n"
        "    return await writes.perform(None, None, grant)\n"
    )
    assert direct_write_path_callers(tree) == ["_second_door", "_write_tool"]


def test_control_the_two_routes_disagreeing_fails():
    tree = ast.parse(
        "@mcp.tool()\n"
        "async def linkedin_save_job(job_id: str, confirm_token: str = ''):\n"
        "    return await _another_door('save_job', job_id, confirm_token)\n"
        "\n"
        "@mcp.tool()\n"
        "async def linkedin_planted_write(item: str, confirm_token: str = ''):\n"
        "    return await _write_tool('planted_write', item, confirm_token)\n"
    )
    tools = tool_definitions(tree)
    assert route_disagreements(tools, writes.SANCTIONED_WRITES) == (
        ["linkedin_planted_write"],
        ["linkedin_save_job"],
    )
    # Both are still checked for name-shaped parameters: the union.
    assert sorted(write_tools(tools, writes.SANCTIONED_WRITES)) == [
        "linkedin_planted_write",
        "linkedin_save_job",
    ]


def test_control_a_tool_handing_the_door_another_action_fails():
    tree = ast.parse(
        "@mcp.tool()\n"
        "async def linkedin_save_job(job_id: str, confirm_token: str = ''):\n"
        "    return await _write_tool('unsave_job', job_id, confirm_token)\n"
        "\n"
        "@mcp.tool()\n"
        "async def linkedin_unsave_job(job_id: str, confirm_token: str = ''):\n"
        "    return await _write_tool(ACTION, job_id, confirm_token)\n"
    )
    assert door_pairing_defects(tool_definitions(tree), writes.SANCTIONED_WRITES) == [
        "linkedin_save_job hands the door ['unsave_job']; its spec's action is "
        "['save_job']",
        "linkedin_unsave_job hands the door [None]; its spec's action is "
        "['unsave_job']",
    ]


def test_control_a_surface_disagreement_fails():
    ast_side = {"linkedin_planted_write": ("item", "confirm_token")}
    assert surface_disagreements(ast_side, ast_side) == []
    assert surface_disagreements(
        ast_side, {"linkedin_planted_write": ("name", "confirm_token")}
    ) == [
        "linkedin_planted_write: syntax tree ['confirm_token', 'item'], "
        "registered ['confirm_token', 'name']"
    ]
    assert surface_disagreements(ast_side, {}) == [
        "linkedin_planted_write: in server.py's syntax tree, not registered"
    ]


def test_control_a_debt_entry_that_forgets_its_ruling_fails():
    assert debt_entry_defects(_PLANTED_DEBT) == []
    weakened = dict(_PLANTED_DEBT)
    weakened["planted_write"] = "legacy, fine as it is"
    assert debt_entry_defects(weakened) == [
        "planted_write: its entry does not say %r" % phrase
        for phrase in DEBT_ENTRY_MUST_SAY
    ]
