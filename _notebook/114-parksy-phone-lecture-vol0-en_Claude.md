---
date: 2026-09-22
agent: Claude Code
mark: _Claude
type: lecture-draft
format: blackboard + full script
language: en
duration: 12–15 min (8 min cut listed in Appendix A)
status: ready-to-record
source:
  - 40-lecture-draft-s21-voice-vol0_Grok.md
  - 110-content-manufacturing-os_Claude.md
  - 113-factory-gift-distribution-model_Claude.md
---

# Parksy Phone — Vol.0
## One Phone, One Studio — Why the Phone Is the Whole Factory

> **Use:** share the screen / read the blackboard while **screen recording**
> **Shape:** each slide = `[Blackboard]` + `(Script)`
> **Recording:** blackboard at full screen, your voice on the mic
> **Rule of this lecture:** every number below was measured on the device. No estimates.

---

# Pre-Roll Setup (30 seconds)

1. Browser full screen
2. Tab 1: this lecture (or the blackboard-only view)
3. Tab 2: the live proof page (a real, deployed site)
4. Notifications off · charging · brightness locked

**One line to keep off-camera:**
`one phone · ~$20/month · no render farm`

---

# SLIDE 00 — Title

### Blackboard
```
Parksy Phone · Vol.0

One Phone, One Studio
Why the phone is the whole factory

measured on a Galaxy S25 Ultra · 2026-09
```

### Script
Hi.

This series is about one claim, and I want to state it before I defend it:
**a single phone is enough to run a one-person media studio.**

Not "a phone can post a video."
A phone that *builds, edits, publishes and ships* — the whole line.

Twelve to fifteen minutes. Every number I say was measured on the device in my hand.

---

# SLIDE 01 — Today's Question

### Blackboard
```
The question

Does a one-person studio need
a desktop, a render farm,
a subscription stack?

Today's answer:
「The expensive parts were never
  the computer.」
```

### Script
Here is the question I keep getting.

*"You need a real machine for this. A PC. A Mac. Something with a GPU."*

So let me separate two things people always merge:
what a studio **computes**, and what a studio **is**.

Computing is cheap now and lives in the cloud.
What a studio actually is — is a **line**: things arriving, getting cut, getting named, getting shipped.

My claim today: the line is the hard part, and the line fits in a pocket.

---

# SLIDE 02 — Measured Specs

### Blackboard
```
Galaxy S25 Ultra (measured)

CPU     Snapdragon 8 Elite
Runtime Termux + proot Ubuntu (aarch64)
Root    none
Storage ample · battery daily
GPU     Adreno 830 — present, unreachable
NPU     Hexagon — present, unreachable
Cost    ~$20 / month total
```

### Script
The machine is a Galaxy S25 Ultra.

What runs on it is Termux, and inside Termux a proot Ubuntu. No root. That matters — everything I show you works on a phone you did not modify.

Now the honest part, and I will come back to it on the limits slide:
the GPU is there. The NPU is there. **And I cannot reach either of them.**

That is not a bug I failed to fix. It is an architecture boundary — and the whole design of this studio is built *around* it rather than against it.

---

# SLIDE 03 — The Beautiful Problem

### Blackboard
```
Why local AI is blocked here

proot speaks  glibc
Android speaks bionic

They cannot link.
GPU and NPU sit on the far side.

So: heavy work leaves the phone.
The phone does the *thinking*, not the *burning*.
```

### Script
This is the single most useful thing I learned, so I will say it plainly.

Inside proot, everything is glibc — normal Linux.
Android's own libraries are bionic — a different C runtime.

They do not talk. It is not a permissions problem, it is not a root problem.
It is a **linking** problem, which means you cannot fix it by trying harder.

So the design writes itself:
anything that needs the silicon — voice training, video generation — **goes to the cloud**.
Everything else — the coordination, the editing decisions, the publishing — stays on the phone.

The phone becomes the director, not the render farm.

---

# SLIDE 04 — What Actually Runs Here

### Blackboard
```
Live on the phone right now

6 local services, all answering
  voice synthesis
  audio cleanup + concat
  embeddings + language model
  telegram delivery
  web page factory
  song + alarm machine

localhost, 6 ports, always on
```

### Script
I want to show you this is not a diagram, so here is what is actually listening on this phone.

Six services. All on localhost. All answering right now.

One makes voice. One cleans and joins audio. One does embeddings and talks to a language model. One delivers to Telegram. One is a whole web page factory. One turns text into a sung alarm.

They survive reboots because a watchdog restarts anything that dies.

**This is the studio's nervous system, and it is inside the phone.**

---

# SLIDE 05 — The Cloud Is Three Containers

### Blackboard
```
Heavy jobs = containers, built by GitHub

voice training      16.07 GB
video generation     2.00 GB
video editing        0.58 GB

Phone has no Docker.
Phone *triggers* the build.
```

### Script
Now the other half.

The heavy jobs are three containers, and I want you to notice the size of the third one.

Voice training: sixteen gigabytes.
Deepfake-style video generation: two gigabytes.
**Video editing: five hundred and eighty-one megabytes.**

Why does that matter?

Because the first thing that kills a new person is the download.
If the only thing you need is a cutter and a joiner, you should not be pulling sixteen gigabytes to get it.

A phone cannot build a container — Docker dies here, I tested it. But a phone can *push the button*. GitHub builds it. The registry stores it.

So the phone is the foreman of a factory it does not physically contain.

---

# SLIDE 06 — The Editing Lane (the core demo)

### Blackboard
```
One recording in → one YouTube cut out

step 1  drop the system bars       top 9.0% / bottom 4.0%
step 2  choose the canvas          16:9 or 9:16
step 3  blur backdrop — ONCE       a single still, reused
step 4  loudness to spec           -16 LUFS · -1.5 TP · 11 LRA
```

### Script
Here is the part I actually use every day.

A phone screen recording has the status bar, the navigation bar, and the wrong shape.
So the lane does four things, in this order.

It crops the system bars — nine percent off the top, four off the bottom. Those numbers are not guesses; they came out of an app that was already doing this on this exact device.

It picks the canvas: wide for a lecture, tall for a short.

It builds the blurred background — and this is the trick I am proudest of.

---

# SLIDE 07 — The Optimisation That Actually Mattered

### Blackboard
```
The blur was the whole cost

blur every frame      38 s
blur ONE still, reuse 12 s

Nothing behind is moving.
So nothing behind should be recomputed.
```

### Script
When I first ran the edit, the command was slow and I assumed it was the encoder.

It was not the encoder.
**The blur was being recomputed on every single frame**, for a background that never moves.

So I generate one blurred still, then loop that single image for the whole clip.

Thirty-eight seconds became twelve. Same output.

And the general lesson is worth more than the trick:
when something is slow, measure *which stage* is slow. I was about to go buy a faster phone for a problem that was one line of ordering.

---

# SLIDE 08 — The Same Lesson, Bigger

### Blackboard
```
15-minute video, measured on this phone

no filters      9 min
with filters   33 min

The encode was never the problem.
The filters were — 4× the cost.
```

### Script
Same lesson, bigger scale.

A fifteen minute video: with no filters, nine minutes to encode. With filters, thirty-three.

Filters cost four times what encoding costs.

So all of this studio's speed comes from one discipline: **do the expensive thing once, not per frame.**
That is not a phone trick. That is just engineering — and the phone is what forced me to learn it.

---

# SLIDE 09 — Publishing

### Blackboard
```
Phone → the world

GitHub Pages     a real site, free
YouTube          the recording
Telegram         the delivery
a public catalog 68 entries, live

No server bill.
```

### Script
Now the last stage: shipping.

Everything goes out over free rails. GitHub Pages hosts the site. The catalog — sixty-eight entries right now — is public and live.

But I want to be careful here, because this is where people start exaggerating.

There is a gate. Before anything deploys, a check counts how many written pages have no web page. If that number is not zero, **the deploy is blocked.**

That is not decoration. It is the difference between a studio and a folder of files.

---

# SLIDE 10 — What It Costs

### Blackboard
```
The bill

hosting        $0     Pages · Actions · registry
delivery       $0     Telegram · open APIs
heavy compute  $0     on-demand containers
the model      ~$20/mo

A studio for the price of two coffees
— but only if the line is real
```

### Script
Let me not oversell.

The model access costs about twenty dollars a month. That is the bill.

Everything else — hosting, builds, container storage, delivery — is free tier, and I am not being cute: the work is small enough that it fits.

But the number is only impressive if the output is real. Cheap infrastructure in front of an empty pipeline is just a cheap empty pipeline.

So the rest of this series is about the pipeline.

---

# SLIDE 11 — Limits, Honestly

### Blackboard
```
What this does NOT do

✗ local AI — GPUs and NPUs are unreachable
✗ heavy Blender-class rendering
✗ on-phone Docker builds
✗ long 4K sessions — it is a phone

But: none of these are the bottleneck.
The bottleneck was always the line.
```

### Script
I said I would come back to the limits, and here they are.

You cannot run real local AI here. The hardware is present and unreachable — that is the glibc and bionic wall from earlier.

You cannot build containers here. You trigger them.

It is a phone. Long high-resolution sessions are not what it is for.

But notice what is *not* on this list.
Not editing. Not publishing. Not coordination. Not the actual daily work.

**The things I cannot do were never the bottleneck.** The bottleneck was always the line — and the line fits.

---

# SLIDE 12 — Conclusion + Next

### Blackboard
```
Conclusion

The expensive parts were never the computer.

One phone + cloud + a real line
= a one-person media studio

Next: Vol.1 — building the line
```

### Script
So, the conclusion, once.

The expensive parts were never the computer.

A phone. A few free services. A cloud that builds what the phone cannot.
And one honest design decision — put the heavy work where the silicon is, and keep the judgment where the person is.

That is a studio.

Next time I will build the line with you, step by step.

Thanks for watching.

---

# Appendix A — 8-Minute Cut

| Time | Slide | The one sentence |
|------|-------|------------------|
| 0:00 | 00 | One phone is a whole studio |
| 0:30 | 01 | Computing was never the hard part |
| 1:00 | 02 | No root; GPU and NPU are present but unreachable |
| 2:00 | 03 | glibc vs bionic — so heavy work leaves the phone |
| 3:00 | 04 | Six services live on localhost |
| 4:00 | 05 | Cloud is three containers; editing is the small one |
| 5:00 | 06 | The editing lane: crop, canvas, still blur, loudness |
| 5:45 | 07 | 38 s → 12 s by doing it once |
| 6:30 | 08 | Filters cost 4× the encode |
| 7:00 | 09 | Publishing with a real gate |
| 7:30 | 11–12 | Limits, then the conclusion |

---

# Appendix B — Cue Sheet (copy-paste)

```
00  Parksy Phone · Vol.0 · One Phone, One Studio
01  Question: does a studio need a desktop? → the computer was never the cost
02  Specs: S25 Ultra · Termux+proot · no root · GPU/NPU unreachable
03  glibc vs bionic → heavy work goes to cloud
04  6 local services, 6 ports, always on
05  3 containers: 16.07 GB / 2.00 GB / 0.58 GB
06  Lane: crop 9.0/4.0 · canvas · still blur · -16 LUFS
07  38 s → 12 s · do it once
08  15-min video: 9 min vs 33 min · filters are 4×
09  Publishing: Pages · catalog 68 · gate blocks deploy
10  The bill: ~$20/month
11  Limits, honestly
12  Conclusion + Vol.1
```

---

# Appendix C — Screen Layout

| Section | On screen |
|---------|-----------|
| 00–05, 10–12 | Blackboard blocks, browser zoomed to 150% |
| 06–08 | The real editing run — terminal output, then the file |
| 09 | The live public page, scrolled |

---

# Appendix D — Links

| Item | URL |
|------|-----|
| Public catalog | https://dtslib1979.github.io/dtslib-cloud-appstore/ |
| Previous series (Korean, Vol.0) | https://helena751107.github.io/helena_phone/notebook/40-lecture-draft-s21-voice-vol0_Grok.html |

---

*Lecture draft (blackboard + script) · Vol.0 · English · agent **`_Claude`** · 2026-09-22*
*Scroll this file while recording.*

> **Note (not for the recording):** the numbers in slides 05, 07 and 08 are device measurements
> from 2026-09-22 (container sizes read from the registry manifest; encode times from the real
> lane runs). If any of them drift, re-measure before recording — this lecture's whole
> credibility is that nothing in it is estimated.
