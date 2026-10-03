---
name: niche-compass
description: >-
  Interviews a creator or founder who feels lost about what to make, and turns
  their answers into a designed Brand One Pager: who they are, their vision,
  personal name or brand, tagline, positioning, channels and platforms, three
  fixed content pillars, an idea filter that says yes or no to any future idea,
  how they'll work each week, how they'll make money, what they're giving up,
  10 ideas to start with, and ready bios for every platform. Use this
  whenever someone says they don't know their niche, can't decide between
  topics or channels, keeps changing direction, wants to "find my niche",
  "define my brand", "write my bio", "tagline", "personal brand or brand
  name", "what should my content be about", or
  writes it in Arabic ("مش عارف أعمل محتوى عن إيه", "تايه", "عايز ألاقي
  النيش بتاعي", "اكتبلي البايو") — even if they don't name the skill. Not for
  writing a single script, caption or post idea (use the idea and script
  skills), and not for visual identity (colours, logo, fonts).
---

# Niche Compass

> **Input:** a conversation with you → **Output:** the creator's **foundations** in a designed **One Pager** (`one-pager.html` + PDF) with a **Start tomorrow** kit: 10 filtered ideas and a first-week plan. People need something they can hold and act on, not just notes.

## When to use

- The creator has many interests (e.g. AI *and* gadgets *and* gaming) and can't choose.
- They keep changing direction, or feel "lost" / "تايه".
- They need a bio, positioning line or content pillars, and nothing is written down yet.
- They have a One Pager already and want to re-check it after a big life or business change.

Not for: one-off post ideas, scripts, captions, or logo/colour work.

## Principles (learned the hard way)

1. **Ask, don't pitch.** A lost person doesn't need a new direction every message. When they say they're lost, switch to questions. Propose a positioning only after Round 8.
2. **One decision per message.** Short messages, tappable options when the interface supports it (always allow a free answer).
3. **Reflect back before moving on.** One line: "So what I'm hearing is …". It catches misunderstandings early.
4. **Never shrink the person.** If they're an expert, the *audience* is the one who doesn't need expertise. Don't write "I'm not a specialist" for someone with years of experience.
5. **Watch for framing that people will misread.** Example: "I help you use AI to find a job" reads as "I find you jobs". Ask: "Could someone misunderstand what you offer?"
6. **Passion ≠ content.** Something they love (gaming, gadgets) can stay a hobby, a side account, or a later business. It doesn't have to be a pillar.
7. **Their words, not yours.** Keep their phrases, dialect and existing bio style. If they share a screenshot of their profile, keep its format and change only what the decisions require.
8. **Data beats opinion.** If they share analytics or a profile grid, note which posts performed and use it as evidence.
9. **One audience first.** The people who *watch* and the people who *pay* are often different (free learners vs. business owners). Name one primary audience, write every video for them, and list the others as later segments.
10. **Look for the origin story.** Ask what made them start. The problem they hit themselves ("I needed a team and had no money") is usually the positioning, the first video and the audience at once.

### Angles that keep a niche alive

Offer these when they ask "can I also post about X?". Each one lets a passion or a trend in without leaving the pillars:

- **The setting is background; the story is the content.** Talking to camera at the desk, while unboxing or mid-game is fine. The filter applies to what they *say*, not where they film.
- **Show the payoff.** People want the result, not the tool: time back for a hobby or family. Show proof of what the system really did, even if it needed a small fix.
- **News through their own work.** Not "today's news" but "my agent / my research found this overnight". Verify every link and claim before posting; one wrong "free certificate" costs trust.
- **Call out with "If you're…".** "If you're getting into ___, this will help" pulls the right people in, as long as it speaks to non-experts and the topic stays occasional when it's outside the main audience.

## Workflow

### Step 0 — Set the frame (one message)

Explain in two lines: 8 short rounds, ~20 minutes, and at the end they get their foundations on one designed page: who they are, where they're going, their brand, what they post, how they work and how they earn. Ask which language and dialect they want it in, and ask for a screenshot of any profile they already have.

### Step 1 — The interview (8 rounds)

Ask 1–4 questions per round. Use options from their own earlier answers whenever possible.

| Round | Goal | Questions |
|:-:|:--|:--|
| **1 · Who** | Background and credibility | What have you done for work, and for how long? Where have you lived or worked? What do people already come to you for? What made you want to start this? |
| **2 · I know** | Skills, now and next | What can you do better than most people around you? What are you ready to learn in the next 6 months? |
| **3 · I love** | Real passion | What do you do even when nobody pays or watches? What could you talk about for an hour without notes? |
| **4 · People need** | Audience and market | Think of yourself a few years ago: what do you know now that you wish you'd known then? Who is that person today, and what keeps them stuck? Who watches, and who would pay? Where is the market going? *(If web search is available, check 2–3 trends and cite them.)* |
| **5 · Money** | Believable income | Which income source do you actually believe you can get within 12 months: courses, affiliate, brand deals, services/systems, product? Any deals or affiliate codes already running? |
| **6 · Vision** | Where this goes | Where do you want to be in 1 year? In 5 years: where do you live, what do people call you, what do you own? |
| **7 · The cut** | Force the decision | If you could make only **one** type of video for a year, which? In 5 years people say "That's the ___ person." What are you willing to drop or postpone? |
| **8 · Brand & rhythm** | Make it real | Personal name, a brand name, or both (name + brand handle)? Do you already own a handle, domain or company? One account or a side account for the topics you love but parked? Which platforms, language and market? How many hours a week can you really give, and how many posts can you keep up? |

**Rounds 6 and 7 are where the answer is.** Their choices usually reveal the niche plainly (e.g. "one type = build with AI", "money = sell the system", "5 years = the business person").

If an answer contradicts an earlier one, say so gently and ask which one wins.

### Step 2 — Propose (one message, short)

Show only:
1. The one-line positioning and the vision in one sentence.
2. Personal or brand, with the handle, and 2–3 tagline options (recommend one).
3. The three pillars.
4. What they're giving up (a small "keep / drop / postpone" table), including where parked passions go (a side account, later, or a hobby).

Ask: "Does this feel like you?" Adjust until it does. Then build the One Pager.

### Step 3 — Build the One Pager

Write `one-pager.json` following `assets/one-pager.example.json` (same keys), then render it:

```bash
python scripts/render_one_pager.py one-pager.json --out out
```

It writes `out/one-pager.html` (responsive, prints cleanly) and `out/one-pager.pdf` when Chromium is available. Standard library only. Rules for the content:

- **`line`, `who`, `what`, `why`, `audience`:** two to four lines each. Plain words, their dialect. `audience` starts with **one** primary audience (mark it ⭐, often "you, N years ago"), then later segments.
- **`vision`:** `year1` (concrete: clients, followers, income) and `year5` (where they live, what people call them, what they own).
- **`identity`:** `type` (personal / brand / personal name on a brand handle), `name`, `handle`, `why` (one line on the choice), `tagline_options` (2–3) and `tagline` (leave it out if they haven't chosen: the page shows "still to decide"), `channels` (main account + any side account with its role), `platforms`, `language`, `market`. Keep handles and companies they already own; don't put a company in the bio if the audience doesn't need it.
- **`rhythm`:** `hours` per week, `cadence` (posts per week they can sustain, not hope for) and `workflow` (how a post gets made: batching, tools, agents, who approves).
- **`pillars`:** exactly 3. Each has a name, the question it answers, and the content types under it. No fixed weekday schedule unless they ask for one.
- **`filter`:** three yes/no questions plus 6–8 examples from *their* world: the topics they were tempted by as ❌, and the ✅ reframe of the same topic. `commit_months` is 3–6; `off_limits` lists what's parked.
- **`starter`:** the part that makes it useful tomorrow.
  - `ideas`: 10 concrete video titles, each passing the filter and tagged with its pillar, spread across all 3 pillars. Use real things from the interview (gear they own, projects they're doing).
  - `week`: the first 3 posts, in order, starting with the easiest to film.
- **`money`:** free → small product → course/workshop → service → deals/affiliate, rough prices, and `"focus": true` on the **one** to start with. Mention `#ad` for paid or affiliate posts in your message.
- **`kdp`:** keep / drop / postpone (with when to revisit), so parked ideas don't sneak back in.
- **`bios`:** Instagram (≤150, name ≤30), TikTok (≤80), X (≤160), LinkedIn headline (≤220). The page shows each length; fix anything over the limit. Keep their handle and existing bio style. Count with UTF-16 length (emoji count as 2). In your message, also give the profile setup around the bio: a searchable name field, 3–4 Highlights that match the pillars, 3 pinned posts (the origin story first), and what the link in bio points to.
- **`brand`** (optional): their colours if known; otherwise leave it out.

Before rendering, show a short preview of the starter ideas and ask if any feel wrong.

### Step 4 — Deliver

1. Share the HTML/PDF and keep `one-pager.json`.
2. Tell them to add the JSON (or the PDF) to their Claude Project knowledge: every other skill reads it, and any new idea gets checked against the filter.
3. Offer one next step: write the script for idea #1, or run the filter on ideas they already have.

## Quality checklist

- [ ] Every section of the template is filled; nothing generic like "provide value".
- [ ] The positioning line fits in one breath and names the audience.
- [ ] One primary audience is named; later segments are marked as later.
- [ ] The person sounds as experienced as they really are.
- [ ] Vision, brand type, tagline status, channels and weekly rhythm are filled from their answers, not guessed. Ask if hours per week is missing.
- [ ] No phrase can be misread as a promise they don't make (jobs, guaranteed income).
- [ ] Exactly 3 pillars, and the filter examples use their own tempting topics.
- [ ] 10 starter ideas, all passing the filter, covering all 3 pillars, built from real things in their life.
- [ ] Bio lengths were counted with code and are under each platform's limit.
- [ ] Output is in the user's language and dialect; platform terms (`Reel`, `Hook`, `Bio`) stay in Latin letters.

## Output

| File | Format | Notes |
|:--|:--|:--|
| `one-pager.json` | JSON | The source of truth. Re-run the skill to update it. |
| `one-pager.html` | HTML | Designed page with the Start tomorrow kit; mobile-friendly and printable. |
| `one-pager.pdf` | PDF | Same page, when Chromium is available. |

## Language

Reply in the user's language and dialect. Keep English platform and product terms in Latin letters rather than transliterating them.
