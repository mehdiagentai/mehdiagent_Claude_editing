"""Cross-platform presenter matte (Windows / Linux, or macOS with MEHDIAGENT_PORTABLE=1).

Two open models, same idea as the Apple Vision path:
  rembg u2net_human_seg     -> soft, detailed edges (hair, glasses) but can leak furniture touching the body
  MediaPipe selfie_multiclass -> knows what is a person (hair/skin/clothes/held accessories), coarse edges
alpha = min(rembg, MediaPipe person mask thresholded at 0.5 and feathered 4 px) - removes leaks such as a chair
behind the shoulder or a door frame, keeps the held mic. Tested against a room with a red chair, door and clothes pile.

Writes edit/mask_person.mkv and edit/mask_subject.mkv (same mask, 8-bit gray ffv1) so render.py needs no change.
Usage (run with the venv python, see setup.sh):   python personmask_rembg.py edit/matte-src.mp4 edit 1080 1920
First run downloads u2net_human_seg (~170 MB, into ~/.u2net) and selfie_multiclass (~16 MB, into ~/.mehdiagent/models).
"""
import subprocess, sys, time, urllib.request
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from rembg import new_session, remove
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

MP_URL = "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite"
MP_PATH = Path.home() / ".mehdiagent/models/selfie_multiclass_256x256.tflite"

def mp_model() -> str:
    if not MP_PATH.is_file():
        MP_PATH.parent.mkdir(parents=True, exist_ok=True)
        print("  downloading MediaPipe person model (~16 MB, once)…", flush=True)
        tmp = MP_PATH.with_suffix(".part")
        try:
            urllib.request.urlretrieve(MP_URL, tmp)
        except Exception:                       # python.org builds without certificates: fall back to curl
            subprocess.run(["curl", "-fsSL", "--retry", "3", "-o", str(tmp), MP_URL], check=True)
        tmp.rename(MP_PATH)
    return str(MP_PATH)

src, out_dir, W, H = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rembg_session = new_session("u2net_human_seg")
segmenter = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=mp_model()), output_confidence_masks=True))
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
encs = [subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                          "-c:v", "ffv1", f"{out_dir}/mask_{name}.mkv"], stdin=subprocess.PIPE) for name in ("person", "subject")]
n, t0, prev = 0, time.time(), None
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    edges = np.asarray(remove(Image.fromarray(rgb), session=rembg_session, only_mask=True, post_process_mask=False).convert("L"), np.float32)
    bgconf = np.squeeze(segmenter.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))).confidence_masks[0].numpy_view())
    person = Image.fromarray(((bgconf < 0.5) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    gate = np.asarray(person.point(lambda v: 255 if v > 127 else 0).filter(ImageFilter.GaussianBlur(4)), np.float32)
    m = np.minimum(edges, gate)
    if prev is not None:                       # light temporal smoothing against edge flicker
        m = 0.7 * m + 0.3 * prev
    prev = m
    data = np.clip(m, 0, 255).astype(np.uint8).tobytes()
    for e in encs:
        e.stdin.write(data)
    n += 1
    if n % 60 == 0:
        print(f"  matte {n} frames ({n / (time.time() - t0):.1f} fps)", flush=True)
for e in encs:
    e.stdin.close(); e.wait()
dec.wait()
print(f"  matte done: {n} frames")
