"""The path guard, every refusal shown firing, and the positive control beside it.

WHAT THIS FILE IS FOR. On 2026-09-04 the operator opened file upload -- profile
photo, post media, message attachments -- and `readonly.SANCTIONED_MUTATIONS`
gained `set_input_files` as its fifth entry. The sanction is one line. The
RISK is not in that line at all: every other act this package performs works on
something already on the page, and this one takes a path naming a file on this
machine and hands its bytes to a remote party. `linkedin_server/uploads.py` is
what stands between "a caller passed a string" and that happening, so every
check in it is exercised here.

TWO RULES SHAPE EVERY TEST BELOW, and neither is decoration:

**A REFUSAL TEST WITHOUT A POSITIVE CONTROL PROVES NOTHING.** A guard that
refused every file on earth would pass every `pytest.raises` in this file. So
there is ONE fixture -- a real, ordinary file inside the root -- which is
asserted to RESOLVE, and every refusal below is that same file with exactly
one property changed. What each test then shows is not "it refused" but "it
refused THIS, and accepted the same thing without it".

**A REFUSAL MUST SAY WHAT IT SAW.** A guard that says "refused" teaches
nothing and gets worked around by guessing. Each refusal is asserted on its
substance -- that the message names a directory as a directory, a link as a
link, the size as a number -- rather than merely on the exception type.

AND ONE THING THAT IS NOT ABOUT THE GUARD AT ALL: no absolute path may appear
in any message. A path on this machine carries a username, and these messages
are built as f-strings that go straight into a tool result. `test_no_refusal_
leaks_an_absolute_path` sweeps every refusal this file produces.
"""

from __future__ import annotations

import ast
import os
import pathlib

import pytest

from linkedin_server import config, uploads, writes
from linkedin_server.errors import WriteAttemptError


# ---------------------------------------------------------------------------
# The fixture, and the positive control that makes the rest mean something
# ---------------------------------------------------------------------------


@pytest.fixture()
def root(tmp_path, monkeypatch):
    """A declared upload root pointed at a temp directory.

    Pointed by MONKEYPATCHING ``config.UPLOAD_ROOT`` rather than by setting the
    environment variable, and that is a real difference: the env var is read
    ONCE at import, so a test setting it would be testing the directory that
    existed when the interpreter started. ``uploads.upload_root()`` reads the
    config attribute on every call precisely so this works -- see its
    docstring, which names this case.
    """
    directory = tmp_path / "uploads"
    directory.mkdir()
    monkeypatch.setattr(config, "UPLOAD_ROOT", directory)
    return directory


@pytest.fixture()
def good_file(root):
    """An ordinary file inside the root. THE CONTROL for everything below."""
    path = root / "headshot.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"pixels" * 100)
    return path


def test_an_ordinary_file_inside_the_root_resolves(good_file):
    """THE POSITIVE CONTROL. Without this, every refusal below is vacuous.

    A guard that refused everything would satisfy every ``pytest.raises`` in
    this file and would look, from the report, exactly like a working one.
    """
    resolved = uploads.resolve_upload_file(str(good_file))
    assert resolved.name == "headshot.png"
    assert resolved.suffix == ".png"
    assert resolved.size_bytes == good_file.stat().st_size
    assert resolved.path == pathlib.Path(os.path.realpath(str(good_file)))


def test_the_facts_a_human_needs_are_in_the_block(good_file):
    """He is approving an UPLOAD, and "a file" is not something to approve.

    The name, the extension and the exact byte count are the three things that
    let him tell the file he meant from the file he typed. The block also has
    to distinguish ATTACHING from SENDING and say that an upload cannot be
    recalled -- both were conditions of the ruling, not garnish.
    """
    resolved = uploads.resolve_upload_file(str(good_file))
    block = resolved.as_block(digest=uploads.digest_of(resolved))

    assert block["file_name"] == "headshot.png"
    assert block["extension"] == ".png"
    assert str(good_file.stat().st_size) in block["size"]
    # BOTH FORMS OF THE SIZE. A rounded number is what he can judge; the exact
    # one is what he can check against his own file listing.
    assert "bytes exactly" in block["size"]
    assert block["sha256_prefix"] == uploads.digest_of(resolved)

    assert "does not submit" in block["attaching_is_not_sending"]
    assert "CANNOT BE UN-SENT" in block["cannot_be_unsent"]
    assert "left this machine" in block["cannot_be_unsent"]
    # AND THE ROOT IT WAS MEASURED AGAINST, because a containment check is
    # only as good as the directory it checked against.
    assert block["checked_against_root"]


def test_a_file_with_no_extension_says_so_rather_than_being_refused(root):
    """The operator opened photo, video, document and attachment paths.

    An extension allowlist here would be this server re-deciding a question he
    already answered -- narrower than his ruling rather than safer than it. So
    a file with no extension is REPORTED as having none and accepted.
    """
    path = root / "resume"
    path.write_bytes(b"%PDF-1.7 pretend")
    resolved = uploads.resolve_upload_file(str(path))
    assert resolved.suffix == ""
    assert "NONE" in resolved.as_block()["extension"]


# ---------------------------------------------------------------------------
# 1. The string, before the filesystem is consulted
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("blank", ["", "   ", None])
def test_a_blank_path_names_nothing(root, blank):
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(blank)
    assert "empty string names nothing" in str(excinfo.value)


@pytest.mark.parametrize("character", ["\n", "\r", "\t"])
def test_a_control_character_in_the_path_is_refused(root, character):
    """A path ends up inside a block a human reads.

    A newline in one is how a reader is shown one path while another is
    opened. ``writes._clean_target_part`` refuses the same thing for the same
    reason; this module repeats it rather than relying on it, because this
    module is callable on its own.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(f"a{character}b.png")
    assert "control character" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 2. The link chain -- the check every other check here is blind without
# ---------------------------------------------------------------------------


def _symlink_or_skip(link: pathlib.Path, target: pathlib.Path) -> None:
    """Make a symlink, or skip -- and NEVER pass by silently doing neither.

    Windows refuses symlink creation without Developer Mode or elevation, and
    a test that swallowed that would report green while proving nothing. It
    skips loudly instead, and the containment tests below cover the same
    escape by a different route, so the SUITE never loses the property even on
    a box where this particular test cannot run.
    """
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError) as exc:  # pragma: no cover - platform
        pytest.skip(f"this platform will not create a symlink here: {exc}")


def test_a_symlink_inside_the_root_is_refused_even_pointing_at_a_fine_file(
    root, good_file
):
    """THE CASE THAT LOOKS HARMLESS AND IS THE WHOLE POINT.

    The link is in the root, the target is in the root, and the bytes are the
    bytes of a file that resolves cleanly one test above. It is still refused,
    because what was approved and what would be sent are decided in two
    different places -- and a rule that allowed the benign case would have to
    read the target to know it was benign, which is the read the link controls.
    """
    link = root / "link-to-headshot.png"
    _symlink_or_skip(link, good_file)
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(link))
    message = str(excinfo.value)
    assert "symbolic link" in message
    assert "names one file and would read another" in message


def test_a_symlink_pointing_out_of_the_root_is_refused(root, tmp_path):
    """The escape the root exists to stop, spelled as a link.

    Note what would happen WITHOUT the link check: the name is inside the
    root, so a textual containment test passes, and the bytes come from
    outside it.
    """
    outside = tmp_path / "id_rsa"
    outside.write_bytes(b"-----BEGIN PRIVATE KEY-----")
    link = root / "innocent.png"
    _symlink_or_skip(link, outside)
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(link))
    assert "symbolic link" in str(excinfo.value)


def test_a_link_in_a_PARENT_directory_is_refused_too(root, tmp_path):
    """The chain, not just the leaf.

    A link one directory up redirects the file just as completely as a link on
    the file itself, and a check that looked only at the final component would
    see an ordinary png.
    """
    real_dir = tmp_path / "elsewhere"
    real_dir.mkdir()
    (real_dir / "photo.png").write_bytes(b"pixels")
    linked_dir = root / "album"
    _symlink_or_skip(linked_dir, real_dir)
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(linked_dir / "photo.png"))
    assert "symbolic link" in str(excinfo.value)


def test_the_link_branch_fires_on_every_platform(root, good_file, monkeypatch):
    """THE THREE TESTS ABOVE SKIP ON A STOCK WINDOWS BOX, AND A SKIP IS NOT A RED.

    Creating a symlink on Windows needs Developer Mode or elevation --
    MEASURED here, ``WinError 1314: A required privilege is not held by the
    client`` -- so on the machine this package is developed on, the entire
    link guard would sit unexercised while the report showed green. That is
    the shape this repo calls a check that certifies nothing.

    So the branch is fired directly: ``is_symlink`` is made to answer True for
    ONE component of an otherwise perfectly ordinary file, and the refusal
    must appear. It proves the branch, not the platform -- which is exactly
    the half the skipped tests were carrying.
    """
    original = pathlib.Path.is_symlink

    def only_this_one(self):
        return self == good_file or original(self)

    monkeypatch.setattr(pathlib.Path, "is_symlink", only_this_one)
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(good_file))
    assert "is a symbolic link" in str(excinfo.value)

    # AND THE CONTROL, in the same test so it cannot drift apart from it: with
    # the patch lifted the identical call resolves. The refusal is about the
    # link answer and nothing else.
    monkeypatch.setattr(pathlib.Path, "is_symlink", original)
    assert uploads.resolve_upload_file(str(good_file)).name == "headshot.png"


def test_the_parent_branch_fires_on_every_platform(root, monkeypatch):
    """The same, one directory up -- the chain walk rather than the leaf."""
    album = root / "album"
    album.mkdir()
    photo = album / "photo.png"
    photo.write_bytes(b"pixels")
    assert uploads.resolve_upload_file(str(photo)).name == "photo.png"

    original = pathlib.Path.is_symlink
    monkeypatch.setattr(
        pathlib.Path, "is_symlink", lambda self: self == album or original(self)
    )
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(photo))
    assert "is a symbolic link" in str(excinfo.value)


def test_the_walk_stops_at_the_root_and_does_not_audit_above_it(root, monkeypatch):
    """A link ABOVE the declared root is not a fact about this upload.

    Those are directories the operator did not choose for this, and refusing
    on them would make the guard fail on any box whose temp directory -- or
    whose ``/tmp`` -- happens to sit behind a link. The chain walk stops at
    the root, and this is that boundary shown holding.
    """
    good = root / "photo.png"
    good.write_bytes(b"pixels")
    original = pathlib.Path.is_symlink
    monkeypatch.setattr(
        pathlib.Path,
        "is_symlink",
        lambda self: self == root.parent or original(self),
    )
    assert uploads.resolve_upload_file(str(good)).name == "photo.png"


@pytest.mark.skipif(os.name != "nt", reason="a junction is a Windows reparse point")
def test_a_windows_junction_out_of_the_root_is_caught_by_containment(root, tmp_path):
    """THE CASE THE LINK CHECK CANNOT SEE, and the reason there are two checks.

    MEASURED 2026-09-04 on this box: a directory junction is creatable with no
    elevation at all, ``Path.is_symlink()`` answers **False** for it, and
    ``os.path.realpath`` follows it straight out of the root. So a junction
    planted inside the declared root would pass a per-component link scan
    cleanly and serve bytes from anywhere on the disk.

    What stops it is that containment is measured on the REAL path against the
    REAL root rather than on the spelling. This is that second check doing the
    work the first one provably cannot, on the one platform where the gap
    exists -- not belt and braces.
    """
    import subprocess

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "id_rsa").write_bytes(b"-----BEGIN PRIVATE KEY-----")
    junction = root / "album"
    made = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        capture_output=True,
        text=True,
    )
    if made.returncode != 0:  # pragma: no cover - platform
        pytest.skip(f"mklink /J unavailable: {made.stderr.strip()}")

    # THE PREMISE OF THIS TEST, ASSERTED RATHER THAN ASSUMED. If a future
    # Python starts reporting junctions as links, this test would otherwise
    # keep passing while testing the OTHER guard, and the gap it documents
    # would silently stop being real.
    assert junction.is_symlink() is False, (
        "this platform now reports a junction as a symlink -- the link check "
        "covers this case and this test is no longer about containment"
    )

    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(junction / "id_rsa"))
    assert "outside the directory this server may upload from" in str(excinfo.value)


def test_the_link_check_is_shown_NOT_firing_on_the_same_shape(root, good_file):
    """The control for the three tests above: an ordinary file in an ordinary
    directory, one level deep, resolves. So the refusals above are about the
    LINK and not about depth or about a subdirectory."""
    album = root / "album"
    album.mkdir()
    photo = album / "photo.png"
    photo.write_bytes(b"pixels")
    assert uploads.resolve_upload_file(str(photo)).name == "photo.png"


# ---------------------------------------------------------------------------
# 3. Containment -- and it is measured on the real path, not the spelling
# ---------------------------------------------------------------------------


def test_a_dot_dot_escape_is_refused_even_though_it_reads_as_inside(root, tmp_path):
    """Textually inside the root; actually outside it.

    This is why containment is measured after resolution rather than as a
    string prefix. It also runs on every platform, which is what keeps the
    escape covered on a box where the symlink tests skip.
    """
    secret = tmp_path / "id_rsa"
    secret.write_bytes(b"-----BEGIN PRIVATE KEY-----")
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(root / ".." / "id_rsa"))
    message = str(excinfo.value)
    assert "outside the directory this server may upload from" in message
    assert "declared root" in message
    assert secret.exists(), "the guard must not have touched the file at all"


def test_an_absolute_path_outside_the_root_is_refused(root, tmp_path):
    outside = tmp_path / "somewhere" / "photo.png"
    outside.parent.mkdir()
    outside.write_bytes(b"pixels")
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(outside))
    assert "outside the directory" in str(excinfo.value)


def test_a_sibling_directory_sharing_the_roots_prefix_is_refused(tmp_path, monkeypatch):
    """``<root>-backup`` has the root's spelling as a prefix and is not in it.

    A string-prefix containment check passes this and it must not. Named
    because it is the specific bug a `startswith` would have.
    """
    root = tmp_path / "uploads"
    root.mkdir()
    sibling = tmp_path / "uploads-backup"
    sibling.mkdir()
    decoy = sibling / "photo.png"
    decoy.write_bytes(b"pixels")
    monkeypatch.setattr(config, "UPLOAD_ROOT", root)
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(decoy))
    assert "outside the directory" in str(excinfo.value)


def test_the_root_itself_is_not_a_file_to_upload(root):
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(root))
    assert "outside the directory" in str(excinfo.value)


def test_a_relative_path_is_joined_onto_the_root_and_not_the_working_directory(
    root, good_file, monkeypatch, tmp_path
):
    """WHERE a relative path lands is a safety property, not a convenience.

    Resolved against the process working directory, ``headshot.png`` would
    mean different files in different sessions and would escape the root the
    moment the server was started one directory up. Joined onto the root it
    can only leave through ``..``, which the test above catches.

    The working directory is moved somewhere else entirely for this test, so
    a passing result cannot be an accident of the two happening to coincide.
    """
    monkeypatch.chdir(tmp_path)
    resolved = uploads.resolve_upload_file("headshot.png")
    assert resolved.path == pathlib.Path(os.path.realpath(str(good_file)))


# ---------------------------------------------------------------------------
# 4. Exists, is a regular file, is readable
# ---------------------------------------------------------------------------


def test_a_missing_file_is_refused_and_says_nothing_was_opened(root):
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(root / "not-here.png"))
    message = str(excinfo.value)
    assert "there is no file at" in message
    assert "nothing was opened" in message


def test_a_directory_is_refused_as_a_directory(root):
    """Not as "cannot use that file". The reason is the actionable part."""
    album = root / "album"
    album.mkdir()
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(album))
    assert "is a directory" in str(excinfo.value)


def test_the_upload_root_missing_is_its_own_refusal_and_names_the_directory(
    tmp_path, monkeypatch
):
    """The answer to "where do I put it" belongs in the refusal.

    And the directory is NOT created here: a guard that makes its own subject
    exist is a guard with a side effect, and putting the file there by hand is
    the consent no string comparison can fake.
    """
    absent = tmp_path / "nowhere"
    monkeypatch.setattr(config, "UPLOAD_ROOT", absent)
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file("photo.png")
    assert "upload directory does not exist" in str(excinfo.value)
    assert not absent.exists(), "the guard created the directory it refused for"


# ---------------------------------------------------------------------------
# 5. Size
# ---------------------------------------------------------------------------


def test_an_empty_file_is_refused(root):
    """An empty file is almost always a half-written one, and uploading it
    looks exactly like uploading the file that was meant."""
    path = root / "empty.png"
    path.write_bytes(b"")
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(path))
    assert "0 bytes" in str(excinfo.value)


def test_a_file_over_the_cap_is_refused_and_the_cap_is_named_as_OURS(
    root, monkeypatch
):
    """THE CAP IS THIS SERVER'S, NOT LINKEDIN'S, and the message says so.

    A number presented as LinkedIn's when it is ours is an unmeasured claim
    wearing somebody else's authority -- the same defect as an unmeasured
    reversibility verdict, one layer down.
    """
    monkeypatch.setattr(uploads, "MAX_UPLOAD_BYTES", 64)
    path = root / "big.png"
    path.write_bytes(b"x" * 65)
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.resolve_upload_file(str(path))
    message = str(excinfo.value)
    assert "65 bytes" in message
    assert "cap is 64" in message
    assert "NOT LINKEDIN'S" in message
    # AND THE CONTROL: one byte under the cap is accepted, so the refusal is
    # about the size rather than about the file.
    path.write_bytes(b"x" * 64)
    assert uploads.resolve_upload_file(str(path)).size_bytes == 64


# ---------------------------------------------------------------------------
# 6. The digest -- what makes "the bytes he saw" a property and not a hope
# ---------------------------------------------------------------------------


def test_the_digest_moves_when_the_bytes_move_under_the_same_path(root, good_file):
    """THE HOLE THE GRANT CANNOT CLOSE, shown open.

    A grant binds the PATH. ``consume`` refuses a token whose target does not
    match, so the file NAMED is provably the file he was shown -- and that is
    a different claim from the file being the same file. This is the gap, and
    the two digests are what closes it.
    """
    resolved = uploads.resolve_upload_file(str(good_file))
    before = uploads.digest_of(resolved)

    good_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"OTHER!" * 100)
    after = uploads.digest_of(resolved)

    assert before != after, (
        "the digest did not move when the file's contents were replaced under "
        "the same path -- which is the entire situation it exists to detect"
    )
    # The PATH, meanwhile, is unchanged -- so a check on the target alone
    # would have seen nothing at all.
    assert uploads.resolve_upload_file(str(good_file)).path == resolved.path


def test_the_digest_is_stable_when_nothing_changes(root, good_file):
    """The control. A digest that moved on every read would fail the test
    above for the wrong reason and refuse every legitimate upload."""
    resolved = uploads.resolve_upload_file(str(good_file))
    assert uploads.digest_of(resolved) == uploads.digest_of(resolved)


def test_the_digest_refuses_rather_than_raising_an_OSError_from_inside(
    root, good_file
):
    """The file can vanish between the check and the hash.

    Reading it here without saying so would raise an OSError from inside the
    drain point -- inside the function whose job is telling him what happened.
    """
    resolved = uploads.resolve_upload_file(str(good_file))
    good_file.unlink()
    with pytest.raises(WriteAttemptError) as excinfo:
        uploads.digest_of(resolved)
    assert "was a readable file when it was checked" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 7. No identity in any output
# ---------------------------------------------------------------------------


def test_no_refusal_leaks_an_absolute_path(root, tmp_path, monkeypatch):
    """A path on this machine carries a username, and these are f-strings.

    Every refusal this module can produce is collected and swept. The messages
    are built by interpolating paths into prose, which is exactly the shape a
    rendered FIELD cannot protect -- ``config.scrub`` is what does, and this
    asserts it is actually reached on every branch rather than on most.
    """
    album = root / "album"
    album.mkdir()
    empty = root / "empty.png"
    empty.write_bytes(b"")

    messages: list[str] = []
    for bad in (
        "",
        "a\nb.png",
        str(root / ".." / "id_rsa"),
        str(root),
        str(album),
        str(root / "not-here.png"),
        str(empty),
    ):
        with pytest.raises(WriteAttemptError) as excinfo:
            uploads.resolve_upload_file(bad)
        messages.append(str(excinfo.value))

    assert len(messages) == 7
    home = str(pathlib.Path.home())
    for message in messages:
        assert home not in message, message
        assert str(tmp_path) not in message, message
        # Neither spelling: an OSError stringifies its filename through
        # repr(), which doubles backslashes on Windows -- the case that got
        # past an exact substring check once already.
        assert str(tmp_path).replace("\\", "\\\\") not in message, message


# ---------------------------------------------------------------------------
# 8. The wiring: what writes.py is allowed to hand to a browser
# ---------------------------------------------------------------------------


_WRITES_SOURCE = pathlib.Path(writes.__file__).read_text(encoding="utf-8")
_WRITES_TREE = ast.parse(_WRITES_SOURCE)


def _set_input_files_calls() -> list[ast.Call]:
    return [
        node
        for node in ast.walk(_WRITES_TREE)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "set_input_files"
    ]


def test_there_is_exactly_one_place_in_this_package_that_uploads():
    """ONE DRAIN POINT, which is the whole design of the allowlist entry.

    ``readonly.SANCTIONED_MUTATIONS`` is keyed by (path, function, kind) and
    the scanner counts CALL SITES, so a second literal ``set_input_files``
    would be a second place to audit while matching the same triple. This is
    the same property from the other side: it fails here, naming the line,
    before the scanner is consulted.
    """
    calls = _set_input_files_calls()
    assert len(calls) == 1, [node.lineno for node in calls]


def test_the_upload_hands_over_the_resolved_path_and_never_a_callers_string():
    """STRUCTURAL: the path argument is ``str(<name>.path)`` off an UploadFile.

    Not a string a caller supplied, not an f-string, not a join. The only way
    an ``UploadFile`` exists is ``uploads.resolve_upload_file``, which has
    already refused a link, a directory, a missing file and anything outside
    the declared root -- so pinning the ARGUMENT to that object's ``.path`` is
    what makes those refusals reach the browser call rather than merely having
    run earlier.
    """
    call = _set_input_files_calls()[0]
    assert len(call.args) >= 2, ast.unparse(call)
    path_arg = call.args[1]
    assert isinstance(path_arg, ast.Call), ast.unparse(call)
    assert isinstance(path_arg.func, ast.Name) and path_arg.func.id == "str", (
        ast.unparse(call)
    )
    inner = path_arg.args[0]
    assert isinstance(inner, ast.Attribute) and inner.attr == "path", (
        ast.unparse(call)
    )

    # AND THE QUEUE IT DRAINS IS FED BY THE EXTRACTOR AND BY NOTHING ELSE.
    appended = [
        node
        for node in ast.walk(_WRITES_TREE)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "append"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "upload_plan"
    ]
    assert len(appended) == 1, [node.lineno for node in appended]
    element = appended[0].args[0]
    assert isinstance(element, ast.Tuple) and len(element.elts) == 2
    source = element.elts[1]
    assert isinstance(source, ast.Call), ast.unparse(appended[0])
    assert isinstance(source.func, ast.Name), ast.unparse(appended[0])
    assert source.func.id == "_file_component_of", ast.unparse(appended[0])
    assert ast.unparse(source) == "_file_component_of(spec, grant.target)"


def test_no_action_uploads_yet_and_that_is_the_declared_state():
    """The ruling landed; the surfaces did not.

    Pinned so that the first action to join arrives in a diff a reviewer reads
    beside the paragraph explaining what it costs -- rather than as a side
    effect of some other change to ``perform``.
    """
    assert writes.UPLOAD_ACTIONS == frozenset()


def test_the_file_extractor_refuses_a_target_it_cannot_split():
    """Refuse rather than guess -- the same rule as its two siblings.

    A ``job_id`` target has no content component, so there is nothing measured
    to upload, and building a path out of the whole target would be this
    server naming a file the operator never did.
    """
    spec = writes.spec_for_action("save_job")
    assert spec.target_kind not in writes._COMPOSITE_TARGET_KINDS
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._file_component_of(spec, "4012345678")
    message = str(excinfo.value)
    assert "no content component" in message
    assert "cannot split" in message


def test_the_extractor_takes_the_content_half_of_a_two_part_target(
    root, good_file
):
    """The path is a SLICE OF THE GRANT, never composed here.

    Driven at a synthetic composite target, because no shipped action uploads
    yet -- the same order this package used for its confinement rule, so that
    the day an action joins ``UPLOAD_ACTIONS`` the extractor is already
    load-bearing rather than newly written.
    """
    spec = writes.spec_for_action("comment_on_item")
    assert spec.target_kind in writes._COMPOSITE_TARGET_KINDS
    # THE SUBJECT IS THE REPO'S OWN SUBSTITUTION TOKEN, not a urn-shaped
    # string. Nothing here goes through the write door, so no shape is needed
    # -- and tests/test_no_committed_identity.py flags an undeclared urn in a
    # tracked file whether it is real or invented, which is the correct
    # default and not something to widen an allowlist for.
    target = f"<item>{writes.TARGET_JOIN}{good_file}"
    resolved = writes._file_component_of(spec, target)
    assert resolved.name == "headshot.png"

    # AND THE SUBJECT HALF IS NEVER TREATED AS A PATH: a target whose content
    # half names nothing usable is refused, not fallen back on.
    bad = f"<item>{writes.TARGET_JOIN}absent.png"
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._file_component_of(spec, bad)
    assert "there is no file at" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 9. The sanction's TRIPLE, shown refusing an upload -- each part separately
# ---------------------------------------------------------------------------
#
# THE POINT OF THIS SECTION, and it is a correction. Everything above tests
# the GUARD -- what may be uploaded. Nothing above tested the SANCTION -- where
# an upload may be written. A file-upload sanction that has never refused an
# upload has not been tested; it has only been written, and the entry admits
# `(writes.py, perform, set_input_files)` by three parts that each have to
# refuse something on their own.


@pytest.mark.parametrize(
    "label, path, source",
    [
        (
            "wrong file",
            "linkedin_server/dom.py",
            "async def perform(page, grant):\n"
            "    await page.set_input_files('#f', p)\n",
        ),
        (
            "wrong function",
            "linkedin_server/writes.py",
            "async def _helper(page, grant):\n"
            "    await page.set_input_files('#f', p)\n",
        ),
        (
            "nested inside the sanctioned function",
            "linkedin_server/writes.py",
            "async def perform(page, grant):\n"
            "    async def _go():\n"
            "        await page.set_input_files('#f', p)\n"
            "    return _go\n",
        ),
        (
            "module level",
            "linkedin_server/writes.py",
            "page.set_input_files('#f', p)\n",
        ),
    ],
)
def test_an_upload_written_anywhere_else_is_refused(label, path, source):
    """Each of the triple's three parts, refusing an UPLOAD specifically.

    ``test_the_exception_does_not_widen`` in tests/test_readonly.py already
    parametrises this shape over clicks, types and presses. It does NOT cover
    ``set_input_files``, and "the same mechanism, so presumably the same
    answer" is the reasoning this repo refuses everywhere else -- an invariant
    that holds because nobody has violated it yet is a coincidence.

    The closure case is the one worth reading twice: attribution is to the
    INNERMOST enclosing function, so burying an upload one scope down inside
    ``perform`` does not inherit ``perform``'s exemption.
    """
    from linkedin_server import readonly

    sanctioned, unsanctioned = readonly.partition_mutation_hits(path, source)
    assert sanctioned == [], (label, sanctioned)
    assert [kind for _l, kind, _s in unsanctioned] == ["set_input_files"], (
        label,
        unsanctioned,
    )


def test_the_triple_accepts_the_one_place_it_is_meant_to():
    """THE POSITIVE CONTROL for the four refusals above.

    Without it they would all pass against a partition that sanctioned
    nothing at all, which is the same defect as a guard that refuses every
    file on earth.
    """
    from linkedin_server import readonly

    sanctioned, unsanctioned = readonly.partition_mutation_hits(
        "linkedin_server/writes.py",
        "async def perform(page, grant):\n"
        "    await page.set_input_files('#f', p)\n",
    )
    assert unsanctioned == []
    assert [kind for _l, kind, _s in sanctioned] == ["set_input_files"]


def test_a_second_upload_inside_perform_is_still_caught():
    """THE HARDEST EDIT, on the real file, mirroring the click's own control.

    A second ``set_input_files`` inside ``perform`` is in the sanctioned file,
    the sanctioned function and of the sanctioned kind -- so it matches the
    allowlist entry exactly and the PARTITION cannot see it. That is asserted
    here rather than hidden, because a control that concealed it would be
    worse than none.

    What catches it is the COUNT: the package is asserted to contain exactly
    as many mutating calls as the list has entries. This reproduces that
    arithmetic against the doubled source and shows it going red.
    """
    from linkedin_server import readonly
    from tests.test_readonly import MODULES

    source = pathlib.Path(writes.__file__).read_text(encoding="utf-8")
    call_site = (
        "await page.set_input_files(\n"
        "                upload_selector, str(upload_file.path), "
        "timeout=CLICK_TIMEOUT_MS\n"
        "            )"
    )
    assert call_site in source, (
        "the upload call site has been rewritten. Update this literal to "
        "match it -- and do NOT relax the assertion below, which is the only "
        "thing stopping this control from testing nothing at all."
    )
    doubled = source.replace(call_site, call_site + "\n            " + call_site, 1)
    assert doubled != source
    # AND IT MUST STILL PARSE, or the partition below is answering about a
    # file it could not read rather than about a duplicated upload. This is
    # the assertion whose absence once let an indent bug look like a boundary
    # failure on the click's twin of this test.
    ast.parse(doubled)

    # The partition is BLIND to it, and that is asserted rather than hidden.
    _sanctioned, unsanctioned = readonly.partition_mutation_hits(
        "linkedin_server/writes.py", doubled
    )
    assert unsanctioned == [], "the partition sees a duplicate -- update this test"

    # The count is not. Counted the way the REAL check counts: across the
    # whole package, not this one file.
    package_total = 0
    for module in MODULES:
        text = (
            doubled
            if module.name == "writes.py"
            else module.read_text(encoding="utf-8")
        )
        package_total += len(readonly.scan_source_for_mutations(text))
    assert package_total == len(readonly.SANCTIONED_MUTATIONS) + 1, package_total
    assert package_total != len(readonly.SANCTIONED_MUTATIONS), (
        "the count check would not fire on a doubled upload"
    )


# ---------------------------------------------------------------------------
# 10. THE GATE, DRIVEN. An upload actually refused, on a real browser page.
# ---------------------------------------------------------------------------
#
# EVERYTHING ABOVE IS STATIC. Section 9 reads source; sections 1-7 call the
# guard directly. Neither runs the code inside ``writes.perform`` that decides
# whether a file reaches a browser -- and a gate whose branches have never
# executed is written rather than tested. Every instrument built in this
# session to catch a specific defect turned out to have that defect on its
# first run, so this section drives ``preview`` -> ``consume`` -> ``perform``
# for real, over frozen pages in headless Chromium, and watches the refusals.
#
# NO ACTION SHIPS WITH AN UPLOAD (``writes.UPLOAD_ACTIONS`` is empty), so the
# vehicle is ``publish_post`` MONKEYPATCHED INTO that set. Three properties
# make that a fair test rather than a convenient one: its ``target_kind`` is
# ``post_text``, a one-component composite, so the whole canonical target IS
# the path and no third component has to be invented; its ``url_template`` is
# a constant carrying no ``{target}``, so a path can never reach a url; and it
# is genuinely PERFORMABLE, so mint, consume and every gate before the upload
# run unmodified.
#
# EACH OF THE THREE SHOWN FAILING, on the real ``writes.py``, 2026-09-04. A
# test that has never gone red on the defect it names is a claim, not a check:
#
#   M1  ``if current != approved:``  ->  ``if False:``
#       the digest COMPARISON removed, so a swapped file uploads
#       -> test_perform_REFUSES_when_the_bytes_moved_under_the_approved_path
#          RED (1 failed)
#   M2  ``if not approved:``  ->  ``if False:``
#       the MISSING-digest check removed, so a grant with no digest passes
#       -> test_perform_REFUSES_a_grant_that_carries_no_digest_at_all
#          RED (1 failed)
#   M3  the ``upload_plan.append(...)`` removed
#       the drain point made unreachable, so nothing is ever handed over
#       -> test_an_unchanged_file_gets_PAST_the_digest_gate  RED (1 failed)
#
# Unmutated baseline in the same run: 43 passed, 3 skipped. ``writes.py`` was
# restored after each mutation and the restore verified by sha256, not by
# assumption.

from tests.test_writes import (  # noqa: E402,F401 - fixtures used by injection
    FixtureNavigator,
    browser_page,
    writes_on,
)
from tests.test_writes_nine import FEED_MARKUP  # noqa: E402
from tests.test_result_verification_block import SHAREBOX_MARKUP  # noqa: E402

SHAREBOX_URL = "https://www.linkedin.com/preload/sharebox/"


async def _granted_upload(page, root, monkeypatch, *, name="photo.png"):
    """Preview a publish_post whose target is a FILE, and burn its token.

    Returns ``(grant, path, preview_block)``. The grant is real: minted by
    ``preview`` off a live read and redeemed by ``consume``, exactly as a
    caller's second call would produce it.
    """
    monkeypatch.setattr(writes, "UPLOAD_ACTIONS", frozenset({"publish_post"}))
    path = root / name
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"pixels" * 40)
    spec = writes.spec_for_action("publish_post")
    block = await writes.preview(
        spec,
        target=str(path),
        navigator=FixtureNavigator({writes.FEED_URL: FEED_MARKUP}),
        page=page,
    )
    grant = writes.consume(
        block["to_confirm"], action="publish_post", target=str(path)
    )
    return grant, path, block


async def test_the_preview_shows_him_the_file_before_any_token_is_spent(
    writes_on, browser_page, root, monkeypatch
):
    """THE CONTROL for this whole section, and a claim in its own right.

    A refusal test that could not first produce a WORKING preview would prove
    only that something went wrong somewhere. This asserts the block he reads
    actually carries what the ruling required -- the name, the extension, the
    exact size, the root and the digest -- and that a confirm token was minted
    against it.
    """
    _grant, path, block = await _granted_upload(browser_page, root, monkeypatch)
    assert block["file"]["file_name"] == "photo.png"
    assert block["file"]["extension"] == ".png"
    assert str(path.stat().st_size) in block["file"]["size"]
    assert len(block["file"]["sha256_prefix"]) == uploads.DIGEST_CHARS
    assert "CANNOT BE UN-SENT" in block["file"]["cannot_be_unsent"]
    assert "does not submit" in block["file"]["attaching_is_not_sending"]
    # AND NO ABSOLUTE PATH IN THE BLOCK HE READS.
    assert str(pathlib.Path.home()) not in block["file"]["path"]


async def test_perform_REFUSES_when_the_bytes_moved_under_the_approved_path(
    writes_on, browser_page, root, monkeypatch
):
    """**THE UPLOAD GATE, SHOWN REFUSING AN UPLOAD.**

    The grant binds the PATH and ``consume`` has already matched it, so every
    check before this one passes: same action, same target, same file name,
    live token. What changed is the CONTENT, which no part of the token
    mechanism can see -- and this is the branch that does.

    WHAT IS ASSERTED BESIDES THE REFUSAL, because "it refused" is the least
    interesting half: NOTHING WAS DISPATCHED. The upload queue drains before
    the click queue, so a refusal here means zero clicks and no ``uploaded``
    block -- the run stopped with the composer untouched rather than half
    done.
    """
    grant, path, block = await _granted_upload(browser_page, root, monkeypatch)
    approved_digest = block["file"]["sha256_prefix"]

    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"SOMETHING ELSE" * 40)

    out = await writes.perform(
        FixtureNavigator({SHAREBOX_URL: SHAREBOX_MARKUP}), browser_page, grant
    )
    error = str(out["clicked"]["error"])
    assert "the file at that path has changed since you were shown it" in error
    # IT NAMES BOTH READINGS. A refusal that says only "changed" cannot be
    # checked by the person reading it.
    assert approved_digest in error
    assert uploads.digest_of(uploads.resolve_upload_file(str(path))) in error
    assert "Nothing was uploaded and nothing was clicked." in error

    assert out["clicked"]["clicks_made"] == 0
    assert out["uploaded"] is None

    # ``performed`` IS DELIBERATELY NOT ASSERTED HERE, and the reason is worth
    # writing down because the obvious assertion is wrong. It comes back
    # ``"unknown"`` rather than ``False`` -- ``publish_post`` declares its
    # outcome UNVERIFIABLE, so ``_verify_after`` short-circuits and this
    # server will not claim either way. That is a property of the VEHICLE this
    # test borrowed, not of the upload gate, and asserting it would pin
    # somebody else's semantics into this file.
    #
    # The two facts above are the ones that mean "nothing was dispatched" and
    # they hold whatever action carries the upload: no click was made, and no
    # file was handed over.
    assert out["clicked"]["error"], "a refusal must be reported, not swallowed"


async def test_perform_REFUSES_a_grant_that_carries_no_digest_at_all(
    writes_on, browser_page, root, monkeypatch
):
    """The other half of the same gate: nothing to compare against.

    A grant reaches ``perform`` only through a preview, and a preview for an
    uploading action reads and prints a digest -- so an absent one means the
    grant was made some other way. The branch FAILS CLOSED rather than
    treating a missing digest as "no objection", which is the difference
    between a check and a decoration.
    """
    grant, _path, _block = await _granted_upload(browser_page, root, monkeypatch)
    grant.preview = {}

    out = await writes.perform(
        FixtureNavigator({SHAREBOX_URL: SHAREBOX_MARKUP}), browser_page, grant
    )
    error = str(out["clicked"]["error"])
    assert "carries no file digest" in error
    assert out["clicked"]["clicks_made"] == 0
    assert out["uploaded"] is None


async def test_an_unchanged_file_gets_PAST_the_digest_gate(
    writes_on, browser_page, root, monkeypatch
):
    """**THE POSITIVE CONTROL, and without it the two refusals prove nothing.**

    A gate that refused every upload unconditionally would pass both tests
    above and would look identical in the report. So: same setup, file NOT
    touched, and the run must fail somewhere ELSE.

    WHERE IT FAILS IS THE EVIDENCE. ``page.set_input_files`` is reached and
    Chromium rejects the node -- ``publish_post``'s ``_live_control`` returns
    the POST EDITOR, a contenteditable div, because nothing in ``dom.py``
    resolves a file input yet. So the error names the CALL rather than the
    digest, which proves two things at once: the digest comparison passed
    rather than being skipped, and the one sanctioned call site genuinely
    executed against a real browser with the resolved path.

    AND IT PINS THE REASON ``UPLOAD_ACTIONS`` IS EMPTY, as a measurement
    rather than a promise. There is no ``_live_control`` arm that returns a
    file input, so even with an action forced into the set the drain point
    cannot land -- which is exactly the per-composer work each of the three
    surfaces still needs. If somebody adds that arm, this test goes red and
    they come here to say so.
    """
    grant, _path, block = await _granted_upload(browser_page, root, monkeypatch)

    out = await writes.perform(
        FixtureNavigator({SHAREBOX_URL: SHAREBOX_MARKUP}), browser_page, grant
    )
    error = str(out["clicked"]["error"])

    assert "has changed since you were shown it" not in error
    assert "carries no file digest" not in error
    assert block["file"]["sha256_prefix"] not in error
    # THE CALL WAS REACHED. Playwright names the method it refused.
    assert "set_input_files" in error
    assert out["clicked"]["clicks_made"] == 0
