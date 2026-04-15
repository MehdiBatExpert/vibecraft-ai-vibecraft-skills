---
name: competitive-intel
description: Competitive intelligence and product monitoring for VibeCraft/EasyClaw. Track competitors, market movements, and strategic opportunities.
tags: [competitive, intelligence, monitoring, strategy, market]
related_skills: [social-intelligence-recon, reply-drafting, duckduckgo-search]
---

Competitive Intelligence

When to Use
- Monitor competitor products, launches, pricing changes
- Before a strategic call or partnership discussion
- Weekly veille (KPI: 1 rapport veille/semaine)
- When a new competitor is identified

Targets

Primary (VibeCraft context)
- Gooseworks (@shivsakhuja, @0xhbam) - gooseworks.ai - AI coworkers for GTM, YC-backed
- Add new competitors as identified

Secondary (EasyClaw context)
- KiloClaw, Hermes ecosystem entrants
- AI agent platforms targeting FR/EU SMBs

Phase 1: Product Monitoring

Website scraping
Python

browser_navigate(url="https://competitor.com")
browser_snapshot(full=True)
Capture: pricing, features, positioning, team, integrations, blog posts

X/Twitter monitoring
Bash

source /home/hermes/.hermes/.env && clix user <handle> tweets <handle> -n 20 --json
Track: new features announced, partnerships, hiring signals, user testimonials RT'd

Search for mentions
Python

mcp_clix_search(query="competitor_name", type="Latest", count=20)
Track: who talks about them, sentiment, complaints, praise

Product Hunt / Launch monitoring
browser_navigate(url="https://www.producthunt.com/products/competitor")

Phase 2: Analysis Framework

For each competitor, maintain:

Identity Card
- Company name, URL, handles
- Founders + backgrounds
- Funding (YC batch, raised amount)
- Team size (LinkedIn, about page)

Product
- Core value prop (their words)
- Features list
- Tech stack (visible: LLM backend, integrations, APIs)
- Pricing model
- Target ICP

GTM Strategy
- Content strategy (build in public? thought leadership? paid?)
- Distribution channels (X, Reddit, HN, Product Hunt, paid ads)
- Community (Discord, Slack, subreddit)
- Partnership strategy

Strengths vs Weaknesses
- What they do better than VibeCraft/EasyClaw
- What they don't address (EU market, RGPD, FR language, non-dev users)
- Where they're vulnerable

Signals to Watch
- Pricing changes = market pressure
- Hiring posts = growth areas
- Pivot signals = what's not working
- User complaints = product gaps
- Fundraising news = runway/ambition

Phase 3: Strategic Insights

Differentiation Matrix
For each competitor, answer:
1. What do THEY do that WE don't?
2. What do WE do that THEY don't?
3. Where is the overlap?
4. Where is the whitespace?

Opportunity Mapping
- Features to copy (validated by competitor's traction)
- Angles to avoid (competitor already dominant)
- Market segments to own (FR/EU, RGPD, PME, non-dev)

Phase 4: Output

Weekly Report Template
# Veille Competitive - Semaine du [date]

## Mouvements cles
- [Competitor] a lance [feature/product]
- [Competitor] a leve [amount]
- [New entrant] identifie: [description]

## Signaux
- [Signal positif/negatif pour VibeCraft/EasyClaw]

## Opportunites
- [Action concrete a prendre]

## Menaces
- [Risque a surveiller]

Save to: ~/workspace/<project>/veille/veille_YYYY-MM-DD.md

Automation

Cron job for weekly monitoring
Python

cronjob(
    action="create",
    name="competitive-intel-weekly",
    schedule="0 9 * * 1",  # Monday 9am
    prompt="Run competitive intelligence scan on Gooseworks (gooseworks.ai, @shivsakhuja, @0xhbam). Check their latest tweets, website changes, and new features. Save report to ~/workspace/vibecraft/veille/veille_$(date +%Y-%m-%d).md",
    deliver="origin"
)

Pitfalls
- Never engage publicly with competitor criticism (can backfire) 
- Don't scrape pricing pages too frequently (may get blocked)
- Verify intel before acting on it (screenshots > memory)
- Keep reports factual, not emotional
- Separate VibeCraft intel from EasyClaw intel (different projects)
- Never share competitive intel publicly or in X replies 
