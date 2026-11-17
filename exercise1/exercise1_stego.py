"""Exercise 1: hide a text in an image (LSB steganography) and extract it again.

Usage:
    python3 exercise1_stego.py generate            # create cover.png
    python3 exercise1_stego.py embed "text"        # cover.png -> stego.png
    python3 exercise1_stego.py extract             # read text from stego.png
"""
import math
import random
import struct
import sys

from PIL import Image

COVER, STEGO = "cover.png", "stego.png"
MAGIC = b"STEG"  # marks the start of the hidden payload


def generate(w=800, h=600):
    """Procedural sunset/hills image with slight noise (looks natural)."""
    rnd = random.Random(1)
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = y / h
            r, g, b = 255 * (1 - 0.3 * t), 140 + 60 * (1 - t), 60 + 150 * t
            hill = h * 0.65 + 40 * math.sin(x / 90) + 25 * math.sin(x / 31 + 1)
            if y > hill:
                r, g, b = 20, 70 + 40 * (y - hill) / h, 40
            n = rnd.randint(-3, 3)
            px[x, y] = tuple(max(0, min(255, int(c + n))) for c in (r, g, b))
    img.save(COVER)


def to_bits(data):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1


def embed(text):
    payload = MAGIC + struct.pack(">I", len(text.encode())) + text.encode()
    img = Image.open(COVER).convert("RGB")
    flat = [c for p in img.getdata() for c in p]
    bits = list(to_bits(payload))
    if len(bits) > len(flat):
        sys.exit("message too long for cover image")
    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & ~1) | bit
    out = Image.new("RGB", img.size)
    out.putdata([tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)])
    out.save(STEGO)
    print(f"embedded {len(payload)} bytes ({len(bits)} bits) into {STEGO}")


def extract():
    img = Image.open(STEGO).convert("RGB")
    lsbs = [c & 1 for p in img.getdata() for c in p]

    def read(n, off):
        return bytes(
            int("".join(map(str, lsbs[off + 8 * i:off + 8 * i + 8])), 2)
            for i in range(n)
        )

    if read(4, 0) != MAGIC:
        sys.exit("no hidden message found")
    length = struct.unpack(">I", read(4, 32))[0]
    print(read(length, 64).decode())


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "generate":
        generate()
    elif cmd == "embed":
        embed(sys.argv[2])
    elif cmd == "extract":
        extract()
    else:
        print(__doc__)
