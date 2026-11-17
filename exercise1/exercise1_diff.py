"""Show that cover.png and stego.png differ, even though they look the same."""
from PIL import Image, ImageChops

a = Image.open("cover.png").convert("RGB")
b = Image.open("stego.png").convert("RGB")

diff = ImageChops.difference(a, b)
changed = sum(1 for p in diff.getdata() if p != (0, 0, 0))
max_delta = max(max(p) for p in diff.getdata())
print(f"pixels changed: {changed} of {a.width * a.height}")
print(f"max change per channel: {max_delta} (out of 255)")

# Amplify the difference so it becomes visible
diff.point(lambda v: 255 if v else 0).save("diff_amplified.png")
# LSB plane of the stego image: first rows look like noise-coded data
b.point(lambda v: 255 if v & 1 else 0).save("stego_lsb_plane.png")
print("wrote diff_amplified.png and stego_lsb_plane.png")
