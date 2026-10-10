"""Write the live proof's benign test image into the declared upload root.

Lane U, 2026-10-10. The live proof of ``linkedin_send_attachment`` (record:
``_audit/2026-09-28-lane-u-uploads.md`` section 7) sends ONE image GENERATED
FOR THE TEST -- never one of the operator's files. This writes it, byte for
byte the same on every run, so the proof's expected readings are exact before
anything is loaded: the size, the digest prefix, the type read from its bytes.

THE IMAGE: a 96 x 32 PNG of one flat light grey, no text, no metadata, named
``linkedin-tool-test.png``. Standard library only (``zlib``, ``struct``).

IT CREATES NOTHING BUT THE FILE. The upload root is created by hand -- that
act is the consent ``config.UPLOAD_ROOT``'s comment describes -- so a missing
root is refused by name, and an existing file of the same name with OTHER
bytes is refused rather than overwritten.

    python scripts/make_benign_upload_image.py           # write, then report
    python scripts/make_benign_upload_image.py --check   # report only
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

NAME = "linkedin-tool-test.png"
WIDTH, HEIGHT = 96, 32
GREY = (0xEE, 0xEE, 0xEE)


def png_bytes() -> bytes:
    """The image, deterministically: signature, IHDR, one IDAT, IEND."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    header = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    row = b"\x00" + bytes(GREY) * WIDTH
    pixels = zlib.compress(row * HEIGHT, 9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", pixels)
        + chunk(b"IEND", b"")
    )


def report(data: bytes) -> str:
    from linkedin_server import uploads

    digest = hashlib.sha256(data).hexdigest()[: uploads.DIGEST_CHARS]
    return f"{NAME}: {len(data)} bytes, sha256 prefix {digest}, image/png"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report only")
    args = parser.parse_args(argv)
    data = png_bytes()
    if args.check:
        print(report(data))
        return 0
    from linkedin_server import config, uploads

    root = uploads.upload_root()
    if not root.is_dir():
        print(
            "the upload root does not exist: "
            f"{config.display(root)}. Create it by hand -- that is the act "
            "that makes a file uploadable -- and run this again.",
            file=sys.stderr,
        )
        return 1
    target = root / NAME
    if target.exists() and target.read_bytes() != data:
        print(
            f"{config.display(target)} exists with OTHER bytes; refusing to "
            "overwrite it. Move it aside and run this again.",
            file=sys.stderr,
        )
        return 1
    target.write_bytes(data)
    print(report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
