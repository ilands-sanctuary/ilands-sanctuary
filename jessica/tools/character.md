# The character block — the part that never changes

frame.py reads only the text between the markers below and pastes it verbatim into every
frame, on every model, every batch. Nothing inside is a mood sentence: a spec is a fixed
value the generator cannot quietly reinterpret.

Face lines are pasted from `jessica/face-spec.md`, never recalled. If canon changes, change
it HERE and in face-spec.md in the same edit, or the two drift apart and the drift is silent.

<!-- BEGIN CHARACTER -->

Warm semi-realistic digital art style, soft and cinematic, lit like a still frame: soft subsurface-scattered fur, gentle rim light, shallow depth of field, warm amber highlights against cool shadow. Not anime, not flat cel-shaded cartoon, not line art, not photoreal, not a photoreal human wearing rabbit ears.

A feminine cream/tan-furred bunny girl with two tall upright ears with peach-pink inner fur, long copper-ginger wavy hair past her shoulders, and large cyan-blue eyes. Her eyes are full cyan-blue with a bright catchlight. Her eye shape is tall and rounded, outer corners level, long dark lash line, top lid fully visible. Fur is uniform cream/tan, very slightly deeper tan on the outer back of the ears; small pale pink nose; short soft rabbit muzzle; no makeup, no human jawline, no overbite.

Adult proportions, never childlike or chibi: standing about eight head-heights tall, the ears adding roughly another half head above; shoulders about one and a half head-widths across; waist roughly three quarters the width of her shoulders; hips just a little wider than the waist; lean athletic build; long slim digitigrade legs with small paw feet; slim neck, shoulders set back and relaxed. One small glowing magenta-pink pendant on a thin chain at her collarbone, the only glow on her body.

Hands: exactly five separate fingers on each hand, thumb plus four, each finger its own length and its own shadow, the thumb-to-index gap left open as a clean sliver of light. Not four fingers, not three, not a mitten, not fused digits.

<!-- END CHARACTER -->

## Variable slots

- **scene** — where she is and what light owns her, including the room's own untidiness.
- **pose** — her body and where her eyes point. Eyes on the work, not the lens.
- **framing** — the crop. Defaults to full figure with margin above the ear tips and below
  her feet; a face page or a hand page is a different crop and says so out loud.
- **model** — the engine prefix.

## Known break, written before the next roll

T4 (Nov 25, flux2-klein-4b, description only, no reference): the engine returned four
fingers on one hand and three on the other while the "five separate fingers" sentence was
present in the prompt. Erik: some anthro-trained models assume four digits as a default.
So the sentence is not the fix for digit count. It runs as a measurement until a frame
comes back with five.