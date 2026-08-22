"""The dependency declarations, asserted rather than trusted.

THE HAZARD THIS GUARDS
----------------------
On 2026-08-20 the sibling naukri server's build went red for a breakage no local
run could show. naukri declared `mcp[cli]>=1.25.0` with no upper bound. `mcp
2.0.0` shipped, relocating `mcp/server/fastmcp` to `mcp/server/mcpserver`, and
naukri imports the old path unconditionally -- so a CLEAN resolve picked 2.0.0
and all 55 of its test modules died at collection: "5 deselected, 55 errors",
zero tests run. Every LOCAL naukri run stayed green, because that venv held an
mcp installed before 2.0.0 existed.

This server is exposed to precisely that move, and unlike the instahyre sibling
it is exposed on the measured evidence rather than in theory: after `import
linkedin_server.server` (measured 2026-08-21) sys.modules holds 92 mcp.*
submodules INCLUDING mcp.server.fastmcp, the exact module mcp 2.0.0 relocated.
What holds it safe is a transitive cap -- fastmcp 3.4.2 requires
fastmcp-slim[client,server]==3.4.2, which declares `mcp<2.0,>=1.24.0` -- and a
cap that lives in somebody else's metadata is a cap a future fastmcp major can
change without telling us. Hence the bound on fastmcp itself, and hence these
tests, which hold it in place.

WHY THESE TESTS READ FILES AS TEXT
----------------------------------
Because the alternative is the check that already failed to fail. Asserting
against the INSTALLED version would pass happily in exactly the venv that hides
the bug -- which is what happened to naukri for a full day. The DECLARATION is
the thing under test here, not the cache of a resolve that happened months ago.
The install itself is a different question, answered by
scripts/clean_install_check.py, which throws the cached resolve away and starts
from the declared requirements.

Pure: no network, no install, two small reads of repo files.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REQUIREMENTS = REPO / "requirements.txt"
PYPROJECT = REPO / "pyproject.toml"

# The major this server is measured to import under. Bumping this line is a
# claim that the server has been RUN on the newer major, not a formality.
# Measured 2026-08-21: `import linkedin_server.server` succeeds on fastmcp
# 3.4.2, CPython 3.13.14.
FASTMCP_TESTED_MAJOR = 3

# Everything below parses TOML with regexes instead of tomllib on purpose:
# pyproject declares `requires-python = ">=3.10"`, and tomllib only arrives in
# 3.11. A test that guards the 3.10 floor must itself be runnable on 3.10.
_NAME_HEAD = re.compile(r"^\s*[A-Za-z][A-Za-z0-9_.\-]*(\[[^\]]*\])?")
_DEPENDENCIES_ARRAY = re.compile(r"^dependencies\s*=\s*\[(.*?)\]", re.M | re.S)
_OPTIONAL_SECTION = re.compile(
    r"^\[project\.optional-dependencies\]\s*?$(.*?)(?=^\[|\Z)", re.M | re.S
)
_ANY_ARRAY = re.compile(r"=\s*\[(.*?)\]", re.S)


def _requirement_lines(path):
    """Yield the non-comment, non-blank requirement lines of a pip file."""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line and not line.startswith("-"):
            yield line


def _name_of(requirement):
    """The distribution name at the head of a requirement string, normalized."""
    return re.split(r"[<>=\[!~;@\s]", requirement, maxsplit=1)[0].strip().lower()


def _specifiers(requirement):
    """The version clauses of a requirement, as a comparable set.

    `fastmcp>=2.0,<4` -> {">=2.0", "<4"}. Whitespace is squeezed out and any
    environment marker after `;` is dropped, so the two files can be written
    with different spacing and still compare equal. Returning a SET rather than
    a string is what makes the comparison catch a changed FLOOR as well as a
    changed cap: `>=2.1,<4` and `>=2.0,<4` are different sets.
    """
    tail = _NAME_HEAD.sub("", requirement, count=1).split(";", 1)[0]
    return frozenset(part.replace(" ", "") for part in tail.split(",") if part.strip())


def _upper_bound(requirement):
    """The integer major in a `<N` clause, or None if the requirement has no cap."""
    match = re.search(r"<\s*(\d+)", requirement)
    return int(match.group(1)) if match else None


def _requirements_txt():
    """{name: [requirement string, ...]} as declared in requirements.txt."""
    found = {}
    for line in _requirement_lines(REQUIREMENTS):
        found.setdefault(_name_of(line), []).append(line)
    return found


def _declared_in(blocks):
    """{name: [requirement string, ...]} for the quoted entries of TOML arrays."""
    found = {}
    for block in blocks:
        for quoted in re.findall(r'"([^"]+)"', block):
            found.setdefault(_name_of(quoted), []).append(quoted)
    return found


def _pyproject_main_requirements():
    """{name: [...]} from the top-level `dependencies` array of pyproject.toml."""
    text = PYPROJECT.read_text(encoding="utf-8")
    main = _DEPENDENCIES_ARRAY.search(text)
    assert main, (
        "no top-level `dependencies = [...]` array was found in pyproject.toml. "
        "Either it was removed -- in which case `pip install linkedin-mcp` "
        "now installs a server with no fastmcp and no playwright -- or it was "
        "reformatted in a way this parser cannot see, which is just as bad "
        "because every test below would then be asserting about nothing."
    )
    return _declared_in([main.group(1)])


def _pyproject_extra_requirements():
    """{name: [...]} from every array under [project.optional-dependencies].

    Only the ARRAY INTERIORS are scanned, never the section's raw text, and that
    distinction was earned rather than reasoned about: the first version of
    test_playwright_is_a_hard_dependency_and_not_an_extra searched the section
    text for the substring "playwright" and went red on a first run, matching
    the word inside the CODE COMMENT that explains why playwright is not an
    extra. A guard that fires on prose is a guard nobody will keep.
    """
    text = PYPROJECT.read_text(encoding="utf-8")
    extras = _OPTIONAL_SECTION.search(text)
    if not extras:
        return {}
    return _declared_in(_ANY_ARRAY.findall(extras.group(1)))


def _pyproject_requirements():
    """{name: [requirement string, ...]} from `dependencies` plus every extra.

    Scoped to those two places deliberately. The looser sweep of every `= [...]`
    array in the file -- which is what the instahyre sibling does -- also drags
    in `requires = ["setuptools>=61"]` from [build-system] and the bare word out
    of `authors = [{ name = "Sundeep" }]`, both of which get mistaken for
    requirements. That is harmless while the comparison only looks at names
    present in BOTH files, but this module asserts the two name sets are EQUAL
    in both directions, and under that stronger claim the stray entries would
    make it fail for reasons that have nothing to do with dependencies.
    """
    found = {name: list(lines) for name, lines in _pyproject_main_requirements().items()}
    for name, lines in _pyproject_extra_requirements().items():
        found.setdefault(name, []).extend(lines)
    return found


def test_fastmcp_has_an_upper_bound():
    """Unbounded on a framework package is how naukri's build got broken."""
    lines = _requirements_txt().get("fastmcp", [])
    assert lines, "the fastmcp requirement disappeared from requirements.txt"
    assert all(_upper_bound(ln) is not None for ln in lines), (
        "fastmcp must carry an upper bound: its next major is code nobody has "
        "run this server against, and fastmcp 2.0 was itself a rewrite of the "
        "library that became mcp.server.fastmcp -- which IS in this server's "
        "import graph. Found: %r" % lines
    )


def test_the_fastmcp_cap_is_not_narrowed_below_the_major_this_server_runs_on():
    """<3 would be naukri's fix cargo-culted onto a repo that does not need it.

    Measured 2026-08-21: `import linkedin_server.server` succeeds on fastmcp
    3.4.2. Capping below that pins a working server to an older major for no
    reason anyone could point at. The bound belongs at the next UNTESTED major.
    """
    for line in _requirements_txt().get("fastmcp", []):
        cap = _upper_bound(line)
        assert cap > FASTMCP_TESTED_MAJOR, (
            "this server is measured working on fastmcp %d.x, so the cap must "
            "sit ABOVE it at the next untested major: %r"
            % (FASTMCP_TESTED_MAJOR, line)
        )


def test_the_two_files_declare_the_same_dependencies():
    """A dependency in one file and not the other is a half-declared dependency.

    requirements.txt is what a developer installs; pyproject.toml is what `pip
    install linkedin-mcp` resolves. A package listed in only one of them is
    present on one of those paths and absent on the other, and nothing in the
    resulting failure says which path you took.
    """
    from_requirements = set(_requirements_txt())
    from_pyproject = set(_pyproject_requirements())
    assert from_requirements == from_pyproject, (
        "requirements.txt and pyproject.toml disagree about WHICH packages this "
        "server depends on. Only in requirements.txt: %s. Only in pyproject: %s"
        % (
            sorted(from_requirements - from_pyproject) or "none",
            sorted(from_pyproject - from_requirements) or "none",
        )
    )


def test_the_two_files_declare_the_same_bounds():
    """Two sources of truth for versions is how a cap gets applied to one of them.

    Checks the whole specifier set, floor included, not just the ceiling: a
    floor that drifts in one file is the same class of bug as a cap that does,
    and it fails in the same silent way -- on somebody else's machine.
    """
    from_pyproject = _pyproject_requirements()
    for name, lines in _requirements_txt().items():
        if name not in from_pyproject:
            continue  # already reported, loudly, by the test above
        for line in lines:
            for other in from_pyproject[name]:
                assert _specifiers(other) == _specifiers(line), (
                    "%s is bounded differently in the two files: "
                    "requirements.txt says %r, pyproject.toml says %r"
                    % (name, line, other)
                )


def test_playwright_is_a_hard_dependency_and_not_an_extra():
    """The browser IS the data path here; an optional browser is an optional server.

    This is the one place linkedin must NOT copy instahyre, where playwright
    guards a login-only side path and every byte of data arrives over plain
    HTTP. Every tool in this server reads LinkedIn through a signed-in Chrome,
    and the playwright import is lazy, so demoting it to an extra would not fail
    at install or at import -- it would fail at the first tool call, which is
    the worst of the three places to find out.
    """
    assert "playwright" in _pyproject_main_requirements(), (
        "playwright must sit in the top-level `dependencies` array of "
        "pyproject.toml, not in an extra"
    )
    assert "playwright" not in _pyproject_extra_requirements(), (
        "playwright is also declared as an extra; two declarations of the same "
        "package is a disagreement waiting to happen"
    )


def test_mcp_is_not_declared_directly():
    """This server talks to `fastmcp`, and `mcp` is fastmcp's dependency to manage.

    Measured 2026-08-21: `fastmcp` 3.4.2 requires
    `fastmcp-slim[client,server]==3.4.2`, which declares `mcp<2.0,>=1.24.0`. A
    direct `mcp` line here could only fight that cap or duplicate it, and a
    duplicated cap is a second source of truth waiting to drift out of step with
    the first.
    """
    for name in _requirements_txt():
        assert name != "mcp", (
            "mcp arrives transitively through fastmcp, which caps it itself"
        )
    for name in _pyproject_requirements():
        assert name != "mcp", (
            "mcp arrives transitively through fastmcp, which caps it itself"
        )


def test_the_install_recipe_can_actually_run_the_tests():
    """`pip install -r requirements.txt` then `pytest` has to survive both lines.

    That two-line recipe is what scripts/clean_install_check.py runs verbatim,
    and it is what any new developer will type. If pytest is not in that file,
    the second line dies with ModuleNotFoundError on every fresh clone. It did
    exactly that in the instahyre sibling until 2026-08-20.
    """
    assert _requirements_txt().get("pytest"), (
        "pytest has to be in requirements.txt: the documented install recipe "
        "runs it immediately after installing from that file"
    )


def test_every_requirement_declares_a_floor():
    """A bare package name pins nothing and resolves to whatever shipped today.

    Deliberately a FLOOR check, not a ceiling check. Capping every dependency
    would be cargo-culting; only the framework package carries a ceiling here,
    because only the framework package has a demonstrated history of moving the
    modules this server imports.
    """
    for line in _requirement_lines(REQUIREMENTS):
        assert re.search(r"[<>=~!]", line), "%r declares no version at all" % line
