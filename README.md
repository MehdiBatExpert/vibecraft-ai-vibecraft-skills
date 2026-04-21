# vibecraft-ai-vibecraft-skills

Claude skills for French SMBs — TOFU/MOFU/BOFU outbound funnel.

Each skill is a standalone Claude command that handles one step of the B2B sales process. Install individually or chain them into a full workflow.

---

## Skills

| Skill | What it does |
|---|---|
| `fr-cold-email-outreach` | Draft personalized cold emails in French, 3 variants per lead |
| `fr-lead-qualification` | Score a B2B lead on 10 points, recommend next action |
| `fr-prospect-scraper` | Generate search queries to find leads on Reddit, LinkedIn, X |
| `fr-meeting-brief` | Prepare a discovery call with MEDDIC questions |
| `fr-competitor-intel` | Build a competitor analysis from public sources |
| `followup-nurturing` | Plan a 4-touch follow-up sequence over 14 days |
| `churn-radar` | Identify churn signals from customer conversations |
| `blog-newsletter` | Repurpose sales content into newsletter or blog posts |
| `gtm-content-repurpose` | Turn one piece of content into 5 channel-specific formats |
| `lead-magnet-builder` | Create a lead magnet outline from an ICP description |
| `seo-geo-content` | Generate geo-targeted SEO content for local B2B |
| `support-triage` | Classify and route inbound support messages |
| `wiki-templates` | Generate internal documentation templates |
| `products/score-leads` | Production-ready lead scoring script (Python) |

---

## Install

**Claude.ai / Claude Code :**

Each folder contains a `SKILL.md`. Install directly from Claude settings or drop into your Claude Code skills directory.

**Claude Code (CLI) :**

```bash
/skill install <path-to-skill-folder>
```

---

## Stack

Built for Claude (Anthropic). No external APIs required. Skills run entirely in your Claude session.

Compatible with Claude.ai, Claude Code, and OpenClaw/Hermes via dynamic skill registry.

---

## License

MIT — free to use, modify, and distribute. Attribution appreciated.

---

Built by [Mehdi Derradji](https://x.com/MehdiBuilds) · VibeCraft · Normandie, France
