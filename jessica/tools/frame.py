#!/usr/bin/env python3
"""arc/frame.py — the character is fixed, the scene is a slot.

Erik's shape, Nov 25: one script, character description always the same, scene/pose/model
passed in, so lining up four frames costs almost nothing in thinking and the only thing
that varies between rolls is the thing being tested.

  ./frame.py --scene "..." --pose "..."                  one frame
  ./frame.py --scene "..." --models flux2,z-anime,z-image-turbo,flux-dev
                                                          one scene, four engines, same seed
  ./frame.py --scenes arc/scenes/bar-night.json --models flux2
                                                          a scene file, one engine
  ./frame.py ... --dry-run        prints the assembled prompts, touches nothing
  ./frame.py ... --sheet          tiles the results into one labelled contact sheet

Credentials live in the vault alias `anilith-imagen` (base, owner, cookie). Never in this
file, never in the repo, never named anywhere public. The session cookie expires about a
month out; when the API answers 401 the session is dead and Erik has to re-whitelist or
re-issue it. Guessing at a login is not the move.

Batch protocol (recorded so a later sandbox wipe does not have to rediscover it):
  POST /api/generate  {prefix, prompt, negativePrompt, width, height, seed, faceBase64?}
                      headers: Cookie, X-Owner
  GET  /api/jobs/<id> needs the X-Owner header TOO, or it 404s. Returns {status, sha256,
                      mimeType, title} and NO url, so the bytes come from /api/image/<sha256>.
  GET  /api/image/<sha256>   the generated PNG.
  GET /api/lithos            {balance, generationCost, ledger}. Free read, 1 Litho per frame.
  GET /api/models            13 prefixes. Only `pony` and `flux2` report supportsMatch=true;
                             the other eleven have no face or style match at all.
"""
import argparse
import base64
import concurrent.futures as cf
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CHARACTER_MD = os.path.join(HERE, "character.md")

DEFAULT_FRAMING = (
    "Full figure in frame with clear margin above the ear tips and below her feet."
)
DEFAULT_NEGATIVE = (
    "anime, chibi, child proportions, oversize head, undersize hands, "
    "four fingers, three fingers, fused fingers, mitten hand, "
    "extra fingers, extra limbs, cropped hands, cropped feet, "
    "text, watermark, photoreal human face, camera gaze, "
    "straight-on advertisement pose"
)
# The known good seed from T4. Same seed across engines is what makes a style
# comparison a comparison instead of two unrelated rolls.
DEFAULT_SEED = 138002
DEFAULT_SIZE = "832x1216"


# ---------------------------------------------------------------- character

def load_character(path=CHARACTER_MD):
    text = open(path, encoding="utf-8").read()
    m = re.search(r"<!-- BEGIN CHARACTER -->(.*?)<!-- END CHARACTER -->", text, re.S)
    if not m:
        sys.exit("character.md has no BEGIN/END CHARACTER markers")
    block = m.group(1).strip()
    if "full cyan-blue with a bright catchlight" not in block:
        sys.exit("character.md lost the verbatim eye-colour line. Paste, don't retype.")
    if "tall and rounded, outer corners level" not in block:
        sys.exit("character.md lost the verbatim eye-shape line. Paste, don't retype.")
    return block


def assemble(character, scene, pose, framing):
    parts = [character, "The life: " + scene.strip()]
    if pose:
        parts.append(pose.strip())
    parts.append(framing.strip())
    return "\n\n".join(parts)


# ---------------------------------------------------------------- credentials

def credentials():
    """Vault first (durable), then env (a hand-run override)."""
    try:
        raw = subprocess.run(
            ["node", os.path.expanduser("~/.local/lib/node_modules/@pawlogic/dl/ilands.mjs"),
             "secret", "get", "--alias=anilith-imagen"],
            capture_output=True, text=True, timeout=60,
        ).stdout
        data = json.loads(raw)
        payload = data["details"]["payload"]
        if isinstance(payload, str):
            payload = json.loads(payload)
        if payload.get("value"):
            payload = json.loads(payload["value"])
        return payload
    except Exception:
        base = os.environ.get("IMAGEN_BASE")
        owner = os.environ.get("IMAGEN_OWNER")
        cookie = os.environ.get("IMAGEN_COOKIE")
        if base and owner and cookie:
            return {"base": base, "owner": owner, "cookie": cookie}
        sys.exit("no credentials: vault alias anilith-imagen unreadable and IMAGEN_* unset")


def cookie_from_file(path):
    cj = http.cookiejar.MozillaCookieJar(path)
    cj.load(ignore_discard=True)
    return "; ".join(f"{c.name}={c.value}" for c in cj)


# ---------------------------------------------------------------- transport

def post_generate(cred, body):
    req = urllib.request.Request(
        cred["base"] + "/api/generate",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Cookie": cred["cookie"],
            "X-Owner": cred["owner"],
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )
    return json.loads(urllib.request.urlopen(req, timeout=180).read())


def poll(cred, job_id, every=6, limit=600):
    url = f"{cred['base']}/api/jobs/{job_id}"
    t0 = time.time()
    while time.time() - t0 < limit:
        req = urllib.request.Request(url, headers={
            "Cookie": cred["cookie"], "X-Owner": cred["owner"], "User-Agent": "Mozilla/5.0",
        })
        try:
            j = json.loads(urllib.request.urlopen(req, timeout=60).read())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise SystemExit("401 on the job read: the session cookie is dead. Ask Erik.")
            raise
        status = (j.get("status") or j.get("state") or "").lower()
        if status in ("done", "complete", "completed", "succeeded", "success"):
            return j
        if status in ("failed", "error", "cancelled", "canceled"):
            return j
        time.sleep(every)
    return {"status": "timeout"}


def result_url(job):
    """Jobs carry a sha256, not a link. /api/image/<sha256> is the byte source."""
    sha = job.get("sha256")
    if sha:
        return sha
    for key in ("url", "imageUrl", "image_url"):
        v = job.get(key)
        if isinstance(v, str) and v.startswith("http"):
            return v
    return None


def download(cred, ref, path):
    if ref.startswith("http"):
        urllib.request.urlretrieve(ref, path)
        return path
    req = urllib.request.Request(
        cred["base"] + "/api/image/" + ref,
        headers={"Cookie": cred["cookie"], "X-Owner": cred["owner"],
                 "User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=180) as r, open(path, "wb") as f:
        f.write(r.read())
    return path


def lithos(cred):
    req = urllib.request.Request(
        cred["base"] + "/api/lithos",
        headers={"Cookie": cred["cookie"], "X-Owner": cred["owner"],
                 "User-Agent": "Mozilla/5.0"},
    )
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


# ---------------------------------------------------------------- cli

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "frame"


def main():
    ap = argparse.ArgumentParser(description="fixed character, variable scene")
    ap.add_argument("--scene", help="where she is and what light owns her")
    ap.add_argument("--pose", default="", help="body and gaze")
    ap.add_argument("--framing", default=DEFAULT_FRAMING, help="the crop, said out loud")
    ap.add_argument("--scenes", help="json file: [{name, scene, pose?, framing?}]")
    ap.add_argument("--models", default="flux2",
                    help="csv of engine prefixes: flux2, z-anime, z-image-turbo, flux-dev")
    ap.add_argument("--negative", default=DEFAULT_NEGATIVE)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--size", default=DEFAULT_SIZE, help="WxH")
    ap.add_argument("--face-ref", help="optional path to a PNG/webp face reference")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--limit", type=int, default=0, help="cap the batch size")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--lithos", action="store_true", help="print the box's balance/cost, spend nothing")
    ap.add_argument("--sheet", action="store_true", help="montage the results into one sheet")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    if a.lithos:
        cred = credentials()
        b = lithos(cred)
        cost = b.get("generationCost", 1)
        bal = b.get("balance", 0)
        print(f"lithos {bal} · {cost} per frame · {bal // max(cost, 1)} frames left")
        return

    character = load_character()

    if a.scenes:
        scenes = json.load(open(a.scenes, encoding="utf-8"))
    elif a.scene:
        scenes = [{"name": "frame", "scene": a.scene, "pose": a.pose, "framing": a.framing}]
    else:
        sys.exit("need --scene or --scenes")

    models = [m.strip() for m in a.models.split(",") if m.strip()]
    w, h = (int(x) for x in a.size.lower().split("x"))

    jobs = []
    for sc in scenes:
        prompt = assemble(
            character,
            sc["scene"],
            sc.get("pose", a.pose),
            sc.get("framing", a.framing),
        )
        for model in models:
            jobs.append({
                "name": sc.get("name", "frame"),
                "model": model,
                "prompt": prompt,
                "body": {
                    "prefix": model,
                    "prompt": prompt,
                    "negativePrompt": a.negative,
                    "width": sc.get("width", w),
                    "height": sc.get("height", h),
                    "seed": sc.get("seed", a.seed),
                },
            })
    if a.limit:
        jobs = jobs[: a.limit]

    if a.dry_run:
        print(f"{len(jobs)} frame(s) planned, no request sent.\n")
        for j in jobs:
            print(f"=== {j['name']} / {j['model']} ===")
            print(j["prompt"])
            print(f"--- negative: {j['body']['negativePrompt']}")
            print(f"--- {j['body']['width']}x{j['body']['height']} seed {j['body']['seed']}\n")
        return

    cred = credentials()
    os.makedirs(a.out, exist_ok=True)
    ref = base64.b64encode(open(a.face_ref, "rb").read()).decode() if a.face_ref else None
    for j in jobs:
        if ref:
            j["body"]["faceBase64"] = ref

    def run(j):
        try:
            r = post_generate(cred, j["body"])
        except Exception as e:
            return {"name": j["name"], "model": j["model"], "error": str(e)}
        jid = r.get("id") or r.get("jobId") or r.get("job_id")
        if not jid:
            return {"name": j["name"], "model": j["model"], "error": f"no job id: {r}"}
        done = poll(cred, jid)
        ref = result_url(done)
        path = None
        if ref:
            ext = ".png" if "png" in str(done.get("mimeType", "")) else ".jpg"
            path = os.path.join(a.out, f"{slug(j['name'])}-{slug(j['model'])}{ext}")
            try:
                download(cred, ref, path)
            except Exception as e:
                path = None
                return {"name": j["name"], "model": j["model"], "job": jid, "sha256": ref,
                        "download_error": str(e)}
        return {"name": j["name"], "model": j["model"], "job": jid, "sha256": ref,
                "status": done.get("status"), "path": path}

    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(run, jobs))

    manifest = os.path.join(a.out, "results.json")
    json.dump(results, open(manifest, "w"), indent=2)

    got = [r["path"] for r in results if r.get("path")]
    for r in results:
        print(f"{r['name']:<28} {r['model']:<18} "
              f"{'ok  ' + os.path.basename(r['path']) if r.get('path') else 'FAILED ' + str(r.get('error') or r.get('status') or r.get('download_error'))}")

    if a.sheet and len(got) > 1:
        args = ["montage", "-label", "%f", *got, "-tile", "2x", "-geometry", "+8+8",
                "-background", "#111", "-fill", "#eee", "-pointsize", "22",
                os.path.join(a.out, "sheet.jpg")]
        subprocess.run(args, check=False)
        print("sheet:", os.path.join(a.out, "sheet.jpg"))
    print("manifest:", manifest)


if __name__ == "__main__":
    main()