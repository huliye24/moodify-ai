# Session Protocol: Silent Comprehension Test

**Date:** 2026-08-19
**Package:** 06 - External Comprehension Validation
**Type:** User research — Phase 1 (Before explanation)

---

## Purpose

Test what people understand about Moodify **without any explanation from us**.

This is the most important test. If Moodify only "works" when we explain it, the Public Form has failed.

---

## Participant Criteria

| Attribute | Requirement |
|---|---|
| Familiarity with Moodify | ❌ None — never heard of it |
| Industry connection | ❌ None in music/audio/AI |
| Age range | 18-55 |
| Language | Chinese or English (record which) |
| Device | Their own laptop/phone |

**Recruit 5 participants minimum per wave.**

---

## Pre-Session Setup

1. Open comprehension lab (`lab/comprehension_lab.html`) or production URL
2. Clear browser history/cache for the test domain
3. Prepare session record file from `sessions/TEMPLATE.json`
4. Have a timer ready
5. **Do NOT explain what Moodify is before starting**

---

## Protocol Steps

### Step 1: Landing (2 minutes)

```
INSTRUCTIONS TO PARTICIPANT:
"请打开这个网站，用你平时上网的方式随意浏览。
我会记录你的反应，但不会帮你或回答问题。
想停随时告诉我。"
```

**Record:**
- First click location
- Time to first scroll
- Facial expression (confused / curious / bored)
- Any verbal reaction
- Where they spend most time

### Step 2: Free Exploration (3 minutes)

Let them browse freely.

**Intervene ONLY if:**
- They ask a direct question → "先按你的理解来，待会再讨论"
- They look stuck → do not help, note the friction point

**Record:**
- Pages/routes they visit
- Time on each section
- What they click / don't click
- Any confusion signals

### Step 3: First Impressions (5 minutes)

Ask these questions **without leading**:

```
Q1: 你觉得这个网站是做什么的？
Q2: 如果用一个词描述它，你会用什么词？
Q3: 你觉得这是给谁用的？
Q4: 你看到了什么让你想留下来？如果想离开，为什么？
Q5: 你觉得"Moodify"是什么？
```

**CRITICAL:** Record verbatim. Do not paraphrase.

### Step 4: Action Probe (3 minutes)

```
Q6: 如果你只能做一个动作，你会做什么？
Q7: [If they haven't clicked Play] 这个页面上有一个播放按钮，你注意到了吗？
    [If they clicked Play] 播放之后你觉得发生了什么？
Q8: 你愿意把这个网站分享给朋友吗？为什么？
```

### Step 5: Identity Probe (5 minutes)

```
Q9: 你觉得运营这个网站的是一家什么样的公司/团队？
Q10: 他们是怎么赚钱的？（如果有的话）
Q11: 这让你想起了什么类似的产品或服务？
Q12: 你会把这归类为：音乐APP / AI工具 / 创作者平台 / 其他？
```

### Step 6: Belief Reading (3 minutes)

Show them the belief text (if visible on site):

> "每一种声音，都值得被世界听见。"

```
Q13: 你怎么理解这句话？
Q14: 这句话让你觉得这个产品更想吸引哪类用户？
```

---

## Post-Session

1. Thank participant
2. Ask if they have any questions NOW (answer honestly)
3. Record session duration
4. Save session file with format: `SESSION-YYYYMMDD-PARTICIPANT-XX.json`
5. Classify responses using `schemas/classifier_rules.json`

---

## What We're Measuring

| Metric | Why It Matters |
|---|---|
| **Identity guess accuracy** | Does the site communicate what it is? |
| **Time to "get it"** | How long before correct understanding? |
| **First action** | Is Play the natural first action? |
| **Commercial inference** | Do they assume it's free/paid/API/etc? |
| **Emotional response** | Curious? Confused? Bored? Intrigued? |
| **Comparison set** | What existing product do they map it to? |
| **Belief interpretation** | Does the brand belief resonate or confuse? |

---

## Red Flags (Immediate Product Problem)

Stop and escalate if **≥3 participants**:

- Think it's an API / developer tool
- Can't find the play button within 60 seconds
- Assume it's a charity / nonprofit
- Confuse it with Spotify / Apple Music / generic music app
- Say "I don't understand what this is" as primary response
