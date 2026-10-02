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
| `ghost_words` | Words land one by one: big blurred ghost → sharp, small set-up line over a big punch line | hooks, quotes, punch lines | 0.26 s / word | v1.3 | Editorial poster reel (user reference) |
| `marquee_word` | Giant word repeated edge to edge, rows sliding in opposite directions | behind a cut-out subject | continuous | v1.3 | Editorial poster reel (user reference) |
| `push_in` | Slow camera push with a small drift; stack layers with different amounts for parallax | every poster scene | scene length | v1.3 | Editorial poster reel (user reference) |
| `focus_in` | Focus pull: starts big, soft and faint, settles sharp | titles, objects | 0.5 s | v1.5 | Studio stage reel (user reference) |
| `blur_rise` | Flies in from off-screen with a motion smear and a small overshoot | objects entering a stage | 0.55 s | v1.5 | Studio stage reel (user reference) |
| `orbit_dots` | Orbit rings grow in around a centre, dots travel on them (bigger on the near side) | a central object or icon | 0.5 s + loop | v1.5 | Studio stage reel (user reference) |
| `roll_in` | Rolls in and stops; the spin matches the distance | balls, eyes, coins, bulbs | 0.7 s | v1.5 | Studio stage reel (user reference) |
| `whip` *(transition)* | Both frames slide with a strong directional smear peaking mid-way | every cut in Style H | 0.26 s | v1.5 | Studio stage reel (user reference) |
| `word_turn` | New word slams in; the previous one turns 90° and parks beside it | numbers, two-word hooks | 0.45 s / word | v1.6 | Doc collage reel (user reference) |
| `scribble_strike` | Hand-drawn dashed line strikes through a word | corrections, "not this" | 0.45 s | v1.6 | Doc collage reel (user reference) |
| `echo_rows` | Rows of a repeated word, fainter and drifting, like an echo | dark backgrounds, emphasis | continuous | v1.6 | Doc collage reel (user reference) |
| `glow_underline` | Hand-drawn underline draws on with a glow | the key phrase | 0.4 s | v1.6 | Doc collage reel (user reference) |
| `sunburst` | Thick rays spin behind a disc | a big idea, a reveal | 0.45 s + loop | v1.6 | Doc collage reel (user reference) |
| `clock_face` | A clock grows in, hands race | time passing | 0.4 s + loop | v1.6 | Doc collage reel (user reference) |
| `count_up` | A number rolls up and lands with a pop | years, prices, stats | 0.8 s | v1.6 | Doc collage reel (user reference) |
| `fan_out` | Copies fan open around a pivot | cards, tickets, notes | 0.5 s | v1.6 | Doc collage reel (user reference) |
| `torn_photo` *(helper)* | A photo in a torn-paper hole with a paper rim | collage on wood/paper | — | v1.6 | Doc collage reel (user reference) |
| `split_reveal` | The name parts in the middle and fades back; the logo pops into the gap | endings, brand reveal | 0.7 s | v1.3 | Editorial poster reel (user reference) |

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
| Poster scene | Lab: `poster_demo.py` | Colour disc + B&W cut-out + giant word behind + poster furniture (rules, dotted orbit, barcode), hard cuts on the bar |
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
