# frame.py — fixed character, variable scene

Erik's shape (Nov 25): the character description never changes, so only the thing being
tested varies between rolls. One script, scene/pose/model as arguments, four frames in a
batch, and he does the looking.

## The split

- `character.md` holds the fixed block. `frame.py` pastes it verbatim into every prompt and
  refuses to run if the two verbatim eye lines are missing. Canon lives in one file.
- scene, pose, framing and model are the only variables.

## Use

    python3 frame.py --lithos                     # balance and cost, free read
    python3 frame.py --scene "..." --pose "..." --dry-run     # see the prompt, no request
    python3 frame.py --scene "..." --models flux2,pony        # same scene, two engines
    python3 frame.py --scenes scenes/example.json --models flux2 --sheet

`--sheet` tiles a batch into one labelled contact sheet, so a four-frame test arrives as
one image. That is a local montage, zero engine spend.

## What the box says about itself

`GET /api/models` lists 13 prefixes. Only `pony` (pony-v6-xl) and `flux2` (flux2-klein-4b)
report `supportsMatch=true`; the other eleven have no face or style match at all. So a
style test that wants any chance of face retention is pony or flux2, and a style test on
the other eleven is measuring the description plus that engine's own prior, nothing else.

`GET /api/lithos` is the balance: 1 Litho per frame.

## Transport facts worth not rediscovering

- `POST /api/generate` {prefix, prompt, negativePrompt, width, height, seed, faceBase64?}
- `GET /api/jobs/<id>` **needs the X-Owner header too**, or it 404s. It returns
  {status, sha256, mimeType, title} and no URL.
- the bytes come from `GET /api/image/<sha256>`.

Credentials are in the vault alias `anilith-imagen` (base, owner, cookie). Never in this
repo, never named in public.
