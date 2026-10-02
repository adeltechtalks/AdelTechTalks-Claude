# Motion library

Every move the skill knows. Moves live in `engine/moves.py`, share one signature
`move(f, t, spr, cx, cy, t0, **options)`, and take colours and fonts from the brand.
Preview any of them with `python templates/lab/moves_demo.py render <name>`.

## Reusable moves (`engine/moves.py`)

| Move | Looks like | Best for | Length | Added | Learned from |
|:--|:--|:--|:--|:--|:--|
| `pop_in` | Scales 0.96 → 1.03 → 1.0 while fading in | headlines, CTA | 0.42 s | v1.2 | Style A headlines |
| `slide_in` | Enters from a side on the ENTER curve | chips, cards, alternating text | 0.30 s | v1.2 | Style A headlines |
| `slide_out` | Leaves to a side on the EXIT curve | clearing a scene | 0.20 s | v1.2 | Brand motion tokens |
| `spring_drop` | Falls in and settles with a small bounce | balls, stickers, badges | 0.90 s | v1.2 | Style E ball drop |
| `slap_in` | Lands big and rotated, snaps flat | paper stickers, labels | 0.32 s | v1.2 | Paper Collage |
| `fold_open` | Unfolds like a paper card | cards, photos, notes | 0.67 s | v1.2 | Paper Collage |

## Signature moves inside the templates

Not extracted yet — reuse them by copying from the template, or extract one into `moves.py` when a second template needs it.

| Move | Template | What it does |
|:--|:--|:--|
| Morphing shape | Style A | One rounded shape morphs chat → files → code → phone |
| Ambient layer | Style A (`ambient()`) | Dot grid, colour blobs, chip marquees, floating widgets — no empty frame |
| Ball split / merge | Style E | A glossy ball splits into labelled balls, then merges into a phone |
| Half-bar type | Style F | One phrase per half-bar: big, box, strike, outline, counter layouts |
| Glass panel (`glass()`) | Liquid Glass | Frosted, blurred rounded panel over a moving background |
| Extruded objects (`extrude()`) | Isometric 3D | Flat sprites become 3D phones, laptops and tiles; one scene per bar |
| One-shape morph | Shape Morph | One white shape morphs into icon after icon |
| Cut-out in front of words | Editorial Depth | Person cut-out in front of giant words, step cards, counters |

## Motion DNA template

Fill this in before writing a new move (see "Learn a new motion" in `SKILL.md`):

```
Name:          snake_case verb_direction (e.g. stretch_in)
Reference:     file / link + the exact seconds the user likes
What moves:    text · card · logo · photo · shape · camera
From → to:     position, scale, rotation, opacity, blur, colour — start and end values
Duration:      seconds (and frames at 30 fps)
Curve:         ENTER / EXIT / MOVE, spring (freq, damping), overshoot %, or a custom cubic-bezier
Beat:          on a bar, half-bar, or the drop? hit sound?
Extras:        motion blur, squash/stretch, trails, shadow, stagger between items
Best for:      where it fits in a reel
```
