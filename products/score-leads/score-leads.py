#!/usr/bin/env python3
# ---------------------------------------------------------------
# .env.example — Expected environment variables
#
# (No API keys, tokens, or emails are used in this script.
#  All scoring is done locally with file-based I/O.)
#
# If future versions add external API calls, declare vars here:
#   TELEGRAM_BOT_TOKEN=
#   BREVO_API_KEY=
#   STRIPE_SECRET_KEY=
# ---------------------------------------------------------------
"""
score-leads.py v2.0 — Synapse v5.0 Revenue Machine — ENRICHER
===============================================================
Weighted intent scoring + business vertical detection + SHA-256 deduplication

Improvements v2 vs v1:
  1. Weighted scoring by source (Reddit karma, engagement)
  2. Subreddit-aware scoring (bonus per relevant sub)
  3. Improved niche detection + fallback + business pain points
  4. Telegram-ready export (formatted summary for alerts)
  5. --batch morning|evening mode (avoids reprocessing)
  6. Multi-format leads (Reddit, X/Twitter, Google Maps)
  7. Persistent JSON stats for the Analyst

Usage:
    python3 score-leads.py                          # Process all unenriched leads for today
    python3 score-leads.py --file leads/08.json     # Process a specific file
    python3 score-leads.py --batch morning           # Morning batch (files 00-13)
    python3 score-leads.py --batch evening           # Evening batch (files 13-23)
    python3 score-leads.py --dry-run                 # Simulate without writing
    python3 score-leads.py --dry-run --verbose       # Simulate with scoring details

Output:  ~/workspace/leads/enriched/YYYY-MM-DD.json
Stats:   ~/workspace/stats/YYYY-MM-DD.json
Logs:    ~/workspace/logs/YYYY-MM-DD.log
Telegram: ~/workspace/outreach/telegram-alert-YYYY-MM-DD-HHmm.md
"""

import json
import hashlib
import os
import sys
import glob
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

# === CONFIGURATION ===
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
LEADS_DIR = os.path.join(WORKSPACE, "leads")
ENRICHED_DIR = os.path.join(WORKSPACE, "leads", "enriched")
CRM_FILE = os.path.join(WORKSPACE, "crm", "deals.json")
MEMORY_FILE = os.path.join(WORKSPACE, "MEMORY.md")
LOG_DIR = os.path.join(WORKSPACE, "logs")
STATS_DIR = os.path.join(WORKSPACE, "stats")
TELEGRAM_DIR = os.path.join(WORKSPACE, "outreach")

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
NOW_SHORT = datetime.now(timezone.utc).strftime("%H%M")

# === SCORING RULES v2 (weighted) ===

# --- Base intent signals ---
SCORE_OPENCLAW_EXPLICIT = 3.0
SCORE_HOSTING_MANAGED = 3.0
SCORE_NON_TECHNICAL = 2.0
SCORE_BUDGET_BUSINESS = 2.0
SCORE_RECENT_ACTIVITY = 1.0
SCORE_COMPETITOR_MENTION = 2.5   # NEW: mentions SimpleClaw or competitor
SCORE_URGENCY_SIGNAL = 1.5      # NEW: "need now", "ASAP", "urgent"

# --- Negative signals ---
SCORE_DEVELOPER_DIY = -3.5     # Increased v2: strong DIY signal = poor fit
SCORE_ALREADY_CONTACTED = -3.0

# --- Source quality multipliers (NEW v2) ---
SOURCE_KARMA_BONUS = {
    # Reddit karma thresholds → bonus points
    "high":   1.5,   # score >= 20
    "medium": 0.5,   # score >= 5
    "low":    0.0,   # score < 5
}

# --- Subreddit relevance bonuses (NEW v2) ---
SUBREDDIT_SCORES = {
    # Tier 1 — High intent subs
    "selfhosted":              2.0,
    "saas":                    2.0,
    "entrepreneur":            1.5,
    "startups":                1.5,
    "smallbusiness":           1.5,
    # Tier 2 — Medium intent
    "sideproject":             1.0,
    "indiehackers":            1.0,
    "nocode":                  1.0,
    "webdev":                  0.5,
    "artificial":              0.5,
    "artificialintelligence":  0.5,
    "machinelearning":         0.0,  # Too academic
    # Tier 3 — Niche verticals (NEW: business verticals)
    "realestateinvesting":     1.5,
    "landlord":                1.5,
    "ecommerce":               1.5,
    "shopify":                 1.5,
    "dropship":                1.0,
    "digital_marketing":       1.0,
    "contentcreation":         1.0,
    "freelance":               1.0,
    "accounting":              1.0,
    "legaladvice":             0.5,
    "PropertyManagement":      1.5,
}

# --- Thresholds ---
THRESHOLD_AUTO_SEND = 8.5
THRESHOLD_MANUAL_REVIEW = 7.0
THRESHOLD_LOW_PRIORITY = 5.0

# === KEYWORD PATTERNS ===

KEYWORDS_OPENCLAW = [
    r"\bopenclaw\b", r"\bopen[\s\-_]?claw\b",
]

KEYWORDS_HOSTING = [
    r"\bhost(?:ing|ed)\b", r"\bmanaged\b", r"\bhébergé\b", r"\bhébergement\b",
    r"\bdeploy\b", r"\bdéployer\b", r"\bsaas\b", r"\bcloud\b",
    r"\bno[\s\-]?server\b", r"\bserverless\b",
    r"don'?t want to manage", r"without (?:a )?vps", r"sans vps",
    r"\bclé en main\b", r"\bturnkey\b", r"\bone[\s\-]?click\b",
    r"\bplug[\s\-]?and[\s\-]?play\b", r"\bout[\s\-]?of[\s\-]?the[\s\-]?box\b",
]

KEYWORDS_NON_TECH = [
    r"\bnon[\s\-]?tech\b", r"\bno[\s\-]?code\b",
    r"pas (?:un )?développeur", r"not a developer",
    r"\bentrepreneur\b", r"\bbusiness owner\b", r"\bsmall business\b",
    r"\bfreelance[r]?\b", r"\bpme\b", r"\bsolopreneur\b",
    r"\bagenc[ey]\b", r"\bconsultant\b", r"\bcoach\b",
    r"\bnon[\s\-]?technical\b", r"\bnot technical\b",
]

KEYWORDS_BUDGET = [
    r"\bbudget\b", r"\bpricing\b", r"\bprice\b", r"\bcost\b",
    r"\bpay(?:ing)?\b", r"\binvest\b", r"\bsubscription\b",
    r"\bmonthly\b", r"\brevenue\b", r"\bbusiness\b",
    r"\bclient[s]?\b", r"\bcustomer[s]?\b",
    r"\b(?:e[\s\-]?)?commerce\b", r"\bshopify\b",
    r"\bstripe\b", r"\bmrr\b", r"\barr\b",
]

KEYWORDS_DEVELOPER = [
    r"\bself[\s\-]?host(?:ing|ed)?\b", r"\bdocker\b",
    r"\bkubernetes\b", r"\bk8s\b", r"\bdevops\b",
    r"i'?ll set it up", r"my own server",
    r"\bvps setup\b", r"\blinux admin\b", r"\bsysadmin\b",
    r"\bterraform\b", r"\bansible\b", r"\bnginx\b",
    r"\bdocker[\s\-]?compose\b", r"\bci[\s/]cd\b",
]

KEYWORDS_COMPETITOR = [
    r"\bsimpleclaw\b", r"\bsimple[\s\-]?claw\b",
    r"\bkiloclaw\b", r"\bkilo[\s\-]?claw\b",
    r"\bzeroclaw\b", r"\bpicoclaw\b", r"\bnanoclaw\b",
    r"\bopenclaw alternative\b", r"\balternative.{0,20}openclaw\b",
]

KEYWORDS_URGENCY = [
    r"\burgent\b", r"\basap\b", r"\bneed.{0,10}now\b",
    r"\bimmediately\b", r"\btoday\b", r"\bthis week\b",
    r"\bdead ?line\b", r"\brunning out of time\b",
    r"\bfed up\b", r"\bfrustrat\b", r"\btired of\b",
    r"\bgave up\b", r"\bcan'?t figure out\b",
]


# ================================================================
# BUSINESS VERTICALS — NICHE DETECTION v2 (deep business context)
# ================================================================
VERTICALS = {
    "cold_outreach_closer": {
        "keywords": [
            r"\boutreach\b", r"\bprospect(?:ion|ing)\b",
            r"\bcold[\s\-]?email\b", r"\blead[\s\-]?gen\b",
            r"\bsales\b", r"\bsdr\b", r"\bbdr\b",
            r"\bpipeline\b", r"\bcrm\b", r"\bhubspot\b",
            r"\bcold[\s\-]?call\b", r"\bbook(?:ing)? meetings?\b",
        ],
        "pain_signals": [
            r"spend(?:ing)? hours on (?:outreach|prospecting)",
            r"manual(?:ly)? (?:sending|prospecting|scraping)",
            r"(?:tired|sick) of (?:cold|manual)",
            r"automat(?:e|ing) (?:my |our )?(?:outreach|sales|prospecting)",
            r"need more leads",
            r"scale (?:my |our )?outreach",
        ],
        "bonus": 1.5,
        "icp_label": "Commercial B2B / Freelance Sales",
        "email_angle": "Automatise ta prospection 24/7 sans coder",
    },
    "ecommerce_operator": {
        "keywords": [
            r"\b(?:e[\s\-]?)?commerce\b", r"\bshopify\b",
            r"\bwoocommerce\b", r"\bdropship(?:ping)?\b",
            r"\bpanier\b", r"\bcart\b", r"\bcheckout\b",
            r"\bamazon[\s\-]?seller\b", r"\bfba\b",
            r"\bstore\b", r"\bboutique en ligne\b",
            r"\bproduct listing\b", r"\binventory\b",
        ],
        "pain_signals": [
            r"(?:abandon|recover).{0,20}cart",
            r"customer (?:support|service).{0,20}(?:overwhelm|scale|24.?7)",
            r"(?:track|monitor).{0,20}(?:compet|price|stock)",
            r"automat.{0,20}(?:relance|followup|follow[\s\-]?up)",
            r"too many (?:orders|tickets|returns)",
            r"can'?t keep up with",
        ],
        "bonus": 1.5,
        "icp_label": "E-commerçant / Shopify / Dropshipper",
        "email_angle": "Un agent qui gère ton SAV, relances panier et veille prix 24/7",
    },
    "deal_flow_analyst": {
        "keywords": [
            r"\binvest(?:ment|or|ing)?\b", r"\bdeal[\s\-]?flow\b",
            r"\bportfolio\b", r"\bangel\b", r"\bvc\b",
            r"\bfund\b", r"\bdue[\s\-]?diligence\b",
            r"\bmarket[\s\-]?research\b", r"\banalys(?:is|t)\b",
            r"\breporting\b", r"\bdashboard\b",
        ],
        "pain_signals": [
            r"too (?:much|many) (?:data|information|deals|sources)",
            r"miss(?:ing|ed) (?:deals|opportunities)",
            r"manual(?:ly)? (?:tracking|monitoring|reporting)",
            r"can'?t keep up with (?:deal|market|news)",
            r"need.{0,20}automat.{0,20}(?:report|analysis|monitor)",
            r"information overload",
        ],
        "bonus": 1.0,
        "icp_label": "Investisseur / Business Angel / Analyste",
        "email_angle": "Un agent qui surveille et analyse ton deal flow 24/7",
    },
    "property_manager": {
        "keywords": [
            r"\bproperty\b", r"\bimmobilier\b",
            r"\blocataire\b", r"\breal[\s\-]?estate\b",
            r"\brental\b", r"\bgestion locative\b",
            r"\blandlord\b", r"\btenant\b",
            r"\bproperty manag\b", r"\bbail\b",
            r"\bloyer\b", r"\brent(?:al|s)?\b",
            r"\bcopropriété\b", r"\bsyndic\b",
        ],
        "pain_signals": [
            r"(?:manage|managing) (?:\d+|many|multiple|several) (?:propert|unit|rental|bien)",
            r"(?:relance|remind|chase).{0,20}(?:tenant|locataire|loyer|rent)",
            r"(?:automat|simplif).{0,20}(?:gestion|management|admin)",
            r"(?:tired|sick) of (?:paperwork|admin|chasing)",
            r"état des lieux",
            r"vacant.{0,10}(?:unit|propert)",
        ],
        "bonus": 2.0,
        "icp_label": "Gestionnaire immobilier / Agence immo",
        "email_angle": "Un agent qui gère tes locataires, relances loyer et admin 24/7",
    },
    "content_machine": {
        "keywords": [
            r"\bcontent\b", r"\bblog(?:ging)?\b",
            r"\bsocial[\s\-]?media\b", r"\bnewsletter\b",
            r"\brédaction\b", r"\bwriting\b", r"\bcopywriting\b",
            r"\bseo\b", r"\bpublish(?:ing)?\b",
            r"\bcontent[\s\-]?market\b", r"\bcreator\b",
            r"\binfluencer\b", r"\byoutub\b", r"\btiktok\b",
        ],
        "pain_signals": [
            r"(?:publish|post).{0,20}(?:consistently|regularly|daily|weekly)",
            r"(?:burn|burning|burnt) ?out.{0,20}(?:content|creat|writ)",
            r"(?:automat|schedul).{0,20}(?:post|publish|content)",
            r"(?:repurpos|recycl).{0,20}content",
            r"can'?t (?:keep up|produce enough)",
            r"(?:content|editorial) calendar",
        ],
        "bonus": 1.0,
        "icp_label": "Créateur de contenu / Agence marketing",
        "email_angle": "Un agent éditorial qui veille, rédige et publie pour toi",
    },
    "website_sales": {
        "keywords": [
            r"\bwebsite\b", r"\bsite web\b",
            r"\bweb[\s\-]?agenc[ey]\b", r"\bweb[\s\-]?design\b",
            r"\bfreelance[\s\-]?web\b", r"\bweb[\s\-]?dev\b",
            r"\blanding[\s\-]?page\b", r"\bwordpress\b",
        ],
        "pain_signals": [
            r"find(?:ing)? (?:client|customer|lead|pme|business)",
            r"(?:automat|scal).{0,20}(?:prospection|outreach|client)",
            r"(?:build|creat).{0,20}(?:website|site).{0,20}(?:for|pour)",
            r"(?:no|don'?t have a?) website",
            r"pme sans site",
        ],
        "bonus": 1.0,
        "icp_label": "Freelance web / Agence web",
        "email_angle": "Un agent qui trouve des PME sans site et leur propose le tien",
    },
    "legal_assistant": {
        "keywords": [
            r"\blegal\b", r"\blawyer\b", r"\bavocat\b",
            r"\blaw[\s\-]?firm\b", r"\bcabinet\b",
            r"\bcontract\b", r"\bcontrat\b",
            r"\bcompliance\b", r"\brgpd\b", r"\bgdpr\b",
            r"\bjuridique\b", r"\bjuriste\b",
        ],
        "pain_signals": [
            r"(?:review|analyz).{0,20}(?:contract|document|dossier)",
            r"(?:too many|overwhelm).{0,20}(?:case|dossier|client)",
            r"(?:automat|simplif).{0,20}(?:legal|juridique|contrat)",
            r"(?:research|recherche).{0,20}(?:jurisprudence|case law)",
            r"billable hours",
        ],
        "bonus": 2.0,
        "icp_label": "Cabinet juridique / Juriste / Avocat",
        "email_angle": "Un agent qui analyse contrats et dossiers pendant que tu plaides",
    },
    "healthcare_admin": {
        "keywords": [
            r"\bhealthcare\b", r"\bmedical\b", r"\bclinic\b",
            r"\bpatient\b", r"\bdoctor\b", r"\bmedecin\b",
            r"\bsanté\b", r"\bcabinet médical\b",
            r"\bappointment\b", r"\brdv\b", r"\brendez[\s\-]?vous\b",
            r"\bpharmac\b", r"\bdentist\b", r"\bdentaire\b",
        ],
        "pain_signals": [
            r"(?:schedul|book|manag).{0,20}(?:appointment|rdv|patient)",
            r"(?:no[\s\-]?show|absent|annul)",
            r"(?:admin|paperwork|dossier).{0,20}(?:overwhelm|too much|burden)",
            r"(?:automat|simplif).{0,20}(?:admin|booking|reminder|rappel)",
            r"patient (?:followup|follow[\s\-]?up|relance|rappel)",
        ],
        "bonus": 2.0,
        "icp_label": "Cabinet médical / Clinique / Professionnel de santé",
        "email_angle": "Un agent qui gère RDV, rappels patients et admin médicale 24/7",
    },
    "recruitment_agency": {
        "keywords": [
            r"\brecruit(?:ment|er|ing)?\b", r"\brecrutement\b",
            r"\bhiring\b", r"\btalent\b", r"\bcandidat[es]?\b",
            r"\bhr\b", r"\brh\b", r"\bstaffing\b",
            r"\bjob[\s\-]?board\b", r"\blinkedin\b",
            r"\bsourc(?:ing|e)\b",
        ],
        "pain_signals": [
            r"(?:screen|trier|filter).{0,20}(?:cv|resume|candidat|application)",
            r"(?:too many|overwhelm).{0,20}(?:cv|candidat|application)",
            r"(?:automat|scal).{0,20}(?:sourc|recruit|hiring)",
            r"(?:fill|pourvoir).{0,20}(?:position|poste)",
            r"talent (?:shortage|pénurie)",
        ],
        "bonus": 1.5,
        "icp_label": "Cabinet de recrutement / RH / Staffing",
        "email_angle": "Un agent qui trie les CV et source les candidats 24/7",
    },
    "financial_advisor": {
        "keywords": [
            r"\bfinancial\b", r"\bfinance\b", r"\bcomptab\b",
            r"\baccounting\b", r"\baccountant\b",
            r"\bbookkeep\b", r"\bexpert[\s\-]?comptable\b",
            r"\btax\b", r"\bfiscal\b", r"\baudit\b",
            r"\bbanque\b", r"\bbank(?:ing)?\b",
        ],
        "pain_signals": [
            r"(?:automat|simplif).{0,20}(?:compta|accounting|bookkeep|factur)",
            r"(?:too many|overwhelm).{0,20}(?:invoice|facture|transaction)",
            r"(?:track|follow|suivre).{0,20}(?:expense|dépense|cash[\s\-]?flow)",
            r"(?:report|bilan).{0,20}(?:automat|monthly|mensuel)",
            r"(?:client|dossier).{0,20}(?:manage|gestion)",
        ],
        "bonus": 1.5,
        "icp_label": "Expert-comptable / Conseiller financier",
        "email_angle": "Un agent qui automatise tes rapports et suivi clients financiers",
    },
    "education_training": {
        "keywords": [
            r"\beducation\b", r"\bformation\b", r"\btraining\b",
            r"\bteach\b", r"\benseignant\b", r"\btutoring\b",
            r"\bcours\b", r"\be[\s\-]?learning\b", r"\blms\b",
            r"\bcoaching\b", r"\bmentor\b",
            r"\bonboarding\b",
        ],
        "pain_signals": [
            r"(?:personali[sz]|adapt).{0,20}(?:learning|formation|cours)",
            r"(?:automat|scal).{0,20}(?:training|formation|onboarding)",
            r"(?:too many|overwhelm).{0,20}(?:student|élève|apprenant)",
            r"(?:assess|évaluer|quiz|exam).{0,20}(?:automat|corrig)",
            r"(?:content|module).{0,20}(?:creat|produc)",
        ],
        "bonus": 1.0,
        "icp_label": "Formateur / Organisme de formation / Coach",
        "email_angle": "Un agent qui personnalise et délivre tes formations 24/7",
    },
}


# === UTILITY FUNCTIONS ===

def log_action(message, level="INFO"):
    """Write to audit trail — NEVER log emails or PII in clear."""
    log_file = os.path.join(LOG_DIR, f"{TODAY}.log")
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{timestamp}] ENRICHER_{level} — {message}\n"
    with open(log_file, "a") as f:
        f.write(line)
    if level in ("WARNING", "ERROR"):
        print(f"  {message}", file=sys.stderr)


def compute_hash(source, contact_id):
    """SHA-256 hash — GDPR compliant."""
    raw = f"{source}:{contact_id}"
    return hashlib.sha256(raw.encode()).hexdigest()


def is_duplicate(contact_hash):
    """Check MEMORY.md + CRM for existing hash."""
    for path in [MEMORY_FILE, CRM_FILE]:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    if contact_hash in f.read():
                        return True
            except IOError:
                pass
    return False


def matches_keywords(text, patterns):
    """Check if text matches any regex pattern."""
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def count_keyword_matches(text, patterns):
    """Count how many distinct patterns match — for weighted scoring."""
    text_lower = text.lower()
    return sum(1 for p in patterns if re.search(p, text_lower))


# === NORMALIZER ===

def normalize_lead(raw_lead):
    """Normalize leads from different sources into common format."""
    source = raw_lead.get("source", "unknown").lower()

    normalized = {
        "source": source,
        "url": raw_lead.get("url", ""),
        "timestamp": None,
        "title": "",
        "body": "",
        "author_id": "",
        "engagement": 0,
        "subreddit": "",
        "extra": {},
    }

    if source == "reddit":
        normalized["title"] = raw_lead.get("title", "")
        normalized["body"] = raw_lead.get("body", "") or raw_lead.get("selftext", "")
        normalized["author_id"] = raw_lead.get("author", "")
        normalized["engagement"] = raw_lead.get("score", 0)
        normalized["subreddit"] = raw_lead.get("subreddit", "").lower()
        normalized["timestamp"] = raw_lead.get("created_utc")
        normalized["extra"] = {
            "num_comments": raw_lead.get("num_comments", 0),
            "subreddit_subscribers": raw_lead.get("subreddit_subscribers", 0),
        }

    elif source in ("x_twitter", "twitter", "x"):
        normalized["source"] = "x_twitter"
        normalized["title"] = raw_lead.get("title", "") or raw_lead.get("text", "")
        normalized["body"] = raw_lead.get("body", "") or raw_lead.get("text", "")
        normalized["author_id"] = raw_lead.get("author", "") or raw_lead.get("username", "")
        normalized["engagement"] = (
            raw_lead.get("likes", 0) +
            raw_lead.get("retweets", 0) * 2 +
            raw_lead.get("replies", 0) * 3
        )
        normalized["timestamp"] = raw_lead.get("created_utc") or raw_lead.get("timestamp")

    elif source in ("google_maps", "gmaps"):
        normalized["source"] = "google_maps"
        normalized["title"] = raw_lead.get("business_name", "") or raw_lead.get("title", "")
        normalized["body"] = " ".join([
            raw_lead.get("description", ""),
            raw_lead.get("category", ""),
            raw_lead.get("website", ""),
        ])
        normalized["author_id"] = raw_lead.get("place_id", "") or raw_lead.get("business_name", "")
        normalized["engagement"] = raw_lead.get("rating", 0) * raw_lead.get("reviews_count", 0)
        phone_raw = raw_lead.get("phone", "")
        normalized["extra"] = {
            "phone": hashlib.sha256(phone_raw.encode()).hexdigest() if phone_raw else "",
            "website": raw_lead.get("website", ""),
            "category": raw_lead.get("category", ""),
            "city": raw_lead.get("city", ""),
            "rating": raw_lead.get("rating", 0),
            "reviews_count": raw_lead.get("reviews_count", 0),
        }

    elif source == "linkedin":
        normalized["title"] = raw_lead.get("title", "") or raw_lead.get("headline", "")
        normalized["body"] = raw_lead.get("body", "") or raw_lead.get("post_text", "")
        normalized["author_id"] = raw_lead.get("author", "") or raw_lead.get("profile_url", "")
        normalized["engagement"] = raw_lead.get("reactions", 0) + raw_lead.get("comments", 0) * 2

    else:
        normalized["title"] = raw_lead.get("title", "")
        normalized["body"] = raw_lead.get("body", "") or raw_lead.get("description", "") or raw_lead.get("text", "")
        normalized["author_id"] = raw_lead.get("author", "") or raw_lead.get("contact_id", "")

    return normalized


# === NICHE DETECTION v2 ===

def detect_niche(text, subreddit=""):
    """
    Detect niche with deep vertical scoring.
    Returns (niche_key, confidence, pain_detected, vertical_info).
    """
    text_lower = text.lower()
    best_niche = "unknown"
    best_score = 0
    pain_detected = False
    best_vertical = None

    for niche_key, vertical in VERTICALS.items():
        kw_matches = count_keyword_matches(text_lower, vertical["keywords"])
        pain_matches = count_keyword_matches(text_lower, vertical["pain_signals"])

        niche_score = kw_matches + (pain_matches * 2)

        if niche_score > best_score:
            best_score = niche_score
            best_niche = niche_key
            pain_detected = pain_matches > 0
            best_vertical = vertical

    if best_score == 0 and subreddit:
        subreddit_niche_map = {
            "realestateinvesting": "property_manager",
            "landlord": "property_manager",
            "PropertyManagement": "property_manager",
            "ecommerce": "ecommerce_operator",
            "shopify": "ecommerce_operator",
            "dropship": "ecommerce_operator",
            "digital_marketing": "content_machine",
            "contentcreation": "content_machine",
            "freelance": "website_sales",
            "accounting": "financial_advisor",
            "legaladvice": "legal_assistant",
        }
        if subreddit.lower() in subreddit_niche_map:
            best_niche = subreddit_niche_map[subreddit.lower()]
            best_vertical = VERTICALS.get(best_niche)

    confidence = min(best_score / 4.0, 1.0)

    return best_niche, confidence, pain_detected, best_vertical


# === SCORING ENGINE v2 ===

def score_lead(normalized_lead):
    """
    Score lead with v2 weighted system.
    Returns (score, breakdown, action, contact_hash, niche_info).
    """
    score = 0.0
    breakdown = []

    combined_text = f"{normalized_lead['title']} {normalized_lead['body']}"
    source = normalized_lead["source"]
    subreddit = normalized_lead["subreddit"]

    # --- Intent signals ---
    if matches_keywords(combined_text, KEYWORDS_OPENCLAW):
        score += SCORE_OPENCLAW_EXPLICIT
        breakdown.append(f"+{SCORE_OPENCLAW_EXPLICIT} openclaw_explicit")

    if matches_keywords(combined_text, KEYWORDS_HOSTING):
        score += SCORE_HOSTING_MANAGED
        breakdown.append(f"+{SCORE_HOSTING_MANAGED} hosting_managed")

    if matches_keywords(combined_text, KEYWORDS_NON_TECH):
        score += SCORE_NON_TECHNICAL
        breakdown.append(f"+{SCORE_NON_TECHNICAL} non_technical")

    if matches_keywords(combined_text, KEYWORDS_BUDGET):
        score += SCORE_BUDGET_BUSINESS
        breakdown.append(f"+{SCORE_BUDGET_BUSINESS} budget_business")

    if matches_keywords(combined_text, KEYWORDS_COMPETITOR):
        score += SCORE_COMPETITOR_MENTION
        breakdown.append(f"+{SCORE_COMPETITOR_MENTION} competitor_mention")

    if matches_keywords(combined_text, KEYWORDS_URGENCY):
        score += SCORE_URGENCY_SIGNAL
        breakdown.append(f"+{SCORE_URGENCY_SIGNAL} urgency_signal")

    # Recent activity (48h)
    ts = normalized_lead["timestamp"]
    if ts:
        try:
            if isinstance(ts, (int, float)):
                age_hours = (datetime.now(timezone.utc).timestamp() - ts) / 3600
            else:
                dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                age_hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
            if age_hours <= 48:
                score += SCORE_RECENT_ACTIVITY
                breakdown.append(f"+{SCORE_RECENT_ACTIVITY} recent_48h")
        except (ValueError, TypeError):
            pass

    # --- Negative signals ---
    if matches_keywords(combined_text, KEYWORDS_DEVELOPER):
        score += SCORE_DEVELOPER_DIY
        breakdown.append(f"{SCORE_DEVELOPER_DIY} developer_diy")

    # --- Source quality ---
    engagement = normalized_lead["engagement"]
    if source == "reddit":
        if engagement >= 20:
            bonus = SOURCE_KARMA_BONUS["high"]
        elif engagement >= 5:
            bonus = SOURCE_KARMA_BONUS["medium"]
        else:
            bonus = SOURCE_KARMA_BONUS["low"]
        if bonus > 0:
            score += bonus
            breakdown.append(f"+{bonus} karma_{engagement}")
    elif source == "x_twitter" and engagement >= 10:
        score += 1.0
        breakdown.append(f"+1.0 x_engagement_{engagement}")
    elif source == "google_maps" and engagement >= 50:
        score += 0.5
        breakdown.append(f"+0.5 gmaps_engagement")
    if source == "google_maps":
        score += 1.5
        breakdown.append("+1.5 gmaps_business_implicit")

    # --- Subreddit bonus ---
    if subreddit and subreddit in SUBREDDIT_SCORES:
        sub_bonus = SUBREDDIT_SCORES[subreddit]
        if sub_bonus > 0:
            score += sub_bonus
            breakdown.append(f"+{sub_bonus} subreddit_{subreddit}")

    # --- Niche detection + pain bonus ---
    niche_key, niche_confidence, pain_detected, vertical_info = detect_niche(
        combined_text, subreddit
    )
    if pain_detected and vertical_info:
        pain_bonus = vertical_info["bonus"]
        score += pain_bonus
        breakdown.append(f"+{pain_bonus} pain_signal_{niche_key}")

    # --- Deduplication ---
    contact_hash = compute_hash(source, normalized_lead["author_id"])
    if is_duplicate(contact_hash):
        score += SCORE_ALREADY_CONTACTED
        breakdown.append(f"{SCORE_ALREADY_CONTACTED} already_contacted")

    # --- Action classification ---
    if score >= THRESHOLD_AUTO_SEND:
        action = "AUTO_SEND"
    elif score >= THRESHOLD_MANUAL_REVIEW:
        action = "MANUAL_REVIEW"
    elif score >= THRESHOLD_LOW_PRIORITY:
        action = "LOW_PRIORITY"
    else:
        action = "ARCHIVED"

    niche_info = {
        "key": niche_key,
        "confidence": round(niche_confidence, 2),
        "pain_detected": pain_detected,
        "icp_label": vertical_info["icp_label"] if vertical_info else "Unknown",
        "email_angle": vertical_info["email_angle"] if vertical_info else "",
    }

    return round(score, 1), breakdown, action, contact_hash, niche_info


# === FILE LOADING with batch support ===

def load_leads_files(specific_file=None, batch=None):
    """
    Load leads. batch='morning' = files 00-13, 'evening' = 13-23.
    """
    leads = []

    if specific_file:
        filepath = specific_file if os.path.isabs(specific_file) else os.path.join(WORKSPACE, specific_file)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                leads.extend(data if isinstance(data, list) else [data])
        else:
            log_action(f"File not found: {filepath}", "ERROR")
        return leads

    patterns = [
        os.path.join(LEADS_DIR, f"{TODAY}*.json"),
        os.path.join(LEADS_DIR, "*.json"),
    ]

    all_files = set()
    for pattern in patterns:
        for f in glob.glob(pattern):
            if "enriched" not in f:
                fname = os.path.basename(f)
                if fname.startswith(TODAY) or \
                   datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d") == TODAY:
                    all_files.add(f)

    if batch:
        filtered = set()
        for f in all_files:
            fname = os.path.basename(f)
            hour_match = re.search(r'(\d{2})\.json', fname)
            if hour_match:
                hour = int(hour_match.group(1))
                if batch == "morning" and hour < 13:
                    filtered.add(f)
                elif batch == "evening" and hour >= 13:
                    filtered.add(f)
            else:
                mtime_hour = datetime.fromtimestamp(os.path.getmtime(f)).hour
                if batch == "morning" and mtime_hour < 13:
                    filtered.add(f)
                elif batch == "evening" and mtime_hour >= 13:
                    filtered.add(f)
        all_files = filtered

    for filepath in sorted(all_files):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                leads.extend(data if isinstance(data, list) else [data])
            log_action(f"Loaded {filepath} — {len(data) if isinstance(data, list) else 1} leads")
        except (json.JSONDecodeError, IOError) as e:
            log_action(f"Error loading {filepath}: {e}", "ERROR")

    return leads


# === OUTPUT WRITERS ===

def write_enriched_output(enriched_leads, dry_run=False):
    """Write/merge enriched leads."""
    os.makedirs(ENRICHED_DIR, exist_ok=True)
    output_file = os.path.join(ENRICHED_DIR, f"{TODAY}.json")

    existing = []
    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = []

    existing_hashes = {l.get("contact_hash") for l in existing}
    new_leads = [l for l in enriched_leads if l.get("contact_hash") not in existing_hashes]
    merged = existing + new_leads

    if not dry_run:
        with open(output_file, "w") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)

    log_action(f"ENRICHER_OUTPUT — file:{output_file} — new:{len(new_leads)} — total:{len(merged)}")
    return output_file, len(new_leads), len(merged)


def write_telegram_alert(enriched_leads):
    """Generate Telegram-ready alert for AUTO_SEND + MANUAL_REVIEW leads."""
    os.makedirs(TELEGRAM_DIR, exist_ok=True)

    auto_leads = [l for l in enriched_leads if l["action"] == "AUTO_SEND"]
    manual_leads = [l for l in enriched_leads if l["action"] == "MANUAL_REVIEW"]

    if not auto_leads and not manual_leads:
        return None

    lines = [f"ENRICHER BATCH — {TODAY} {NOW_SHORT}\n"]

    if auto_leads:
        lines.append(f"AUTO-SEND ({len(auto_leads)} leads):")
        for lead in auto_leads[:10]:
            lines.append(
                f"  [{lead['intent_score']}] {lead['niche']['icp_label']}\n"
                f"    Signal: {lead['pain_signal'][:80]}\n"
                f"    Source: {lead['source']} | Hash: {lead['contact_hash'][:12]}..."
            )

    if manual_leads:
        lines.append(f"\nA VALIDER ({len(manual_leads)} leads):")
        for lead in manual_leads[:10]:
            lines.append(
                f"  [{lead['intent_score']}] {lead['niche']['icp_label']}\n"
                f"    Signal: {lead['pain_signal'][:80]}\n"
                f"    Angle: {lead['niche']['email_angle']}\n"
                f"    Hash: {lead['contact_hash'][:12]}...\n"
                f"    -> Repondre OUI/NON (timeout 2h)"
            )

    lines.append(f"\nOutput: ~/workspace/leads/enriched/{TODAY}.json")

    alert_text = "\n".join(lines)
    alert_file = os.path.join(TELEGRAM_DIR, f"telegram-alert-{TODAY}-{NOW_SHORT}.md")
    with open(alert_file, "w") as f:
        f.write(alert_text)

    log_action(f"TELEGRAM_ALERT — auto:{len(auto_leads)} manual:{len(manual_leads)} — file:{alert_file}")
    return alert_file


def write_stats(enriched_leads, stats, batch=None):
    """Persistent stats JSON for Analyst."""
    os.makedirs(STATS_DIR, exist_ok=True)
    stats_file = os.path.join(STATS_DIR, f"{TODAY}.json")

    existing_stats = {}
    if os.path.exists(stats_file):
        try:
            with open(stats_file, "r") as f:
                existing_stats = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing_stats = {}

    niche_dist = {}
    for lead in enriched_leads:
        niche = lead.get("niche", {}).get("key", "unknown")
        niche_dist[niche] = niche_dist.get(niche, 0) + 1

    source_dist = {}
    for lead in enriched_leads:
        src = lead.get("source", "unknown")
        source_dist[src] = source_dist.get(src, 0) + 1

    scores = [l["intent_score"] for l in enriched_leads]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    pain_count = sum(1 for l in enriched_leads if l.get("niche", {}).get("pain_detected", False))

    batch_key = f"batch_{batch or 'all'}_{NOW_SHORT}"
    batch_stats = {
        "timestamp": NOW,
        "batch": batch or "all",
        "total_processed": stats["total"],
        "auto_send": stats["auto_send"],
        "manual_review": stats["manual_review"],
        "low_priority": stats["low_priority"],
        "archived": stats["archived"],
        "duplicates": stats["duplicate"],
        "avg_score": avg_score,
        "pain_signal_rate": round(pain_count / len(enriched_leads) * 100, 1) if enriched_leads else 0,
        "niche_distribution": niche_dist,
        "source_distribution": source_dist,
    }

    if "batches" not in existing_stats:
        existing_stats["batches"] = {}
    existing_stats["batches"][batch_key] = batch_stats

    daily = {"total": 0, "auto_send": 0, "manual_review": 0, "low_priority": 0, "archived": 0, "duplicates": 0}
    for b in existing_stats["batches"].values():
        for key in daily:
            daily[key] = daily.get(key, 0) + b.get(key, b.get("total_processed", 0) if key == "total" else 0)
    existing_stats["daily_totals"] = daily
    existing_stats["date"] = TODAY
    existing_stats["last_updated"] = NOW

    with open(stats_file, "w") as f:
        json.dump(existing_stats, f, indent=2, ensure_ascii=False)

    log_action(f"STATS_WRITTEN — file:{stats_file}")
    return stats_file


def register_in_memory(contact_hash, niche_key, source, action):
    """Write hash to MEMORY.md."""
    if not os.path.exists(MEMORY_FILE):
        log_action(f"MEMORY.md not found at {MEMORY_FILE}", "WARNING")
        return

    entry = f"| {TODAY} | {contact_hash[:16]}... | {niche_key} | {action} | {source} |"

    with open(MEMORY_FILE, "r") as f:
        content = f.read()

    marker = "<!-- Agent écrit ici AVANT tout envoi email -->"
    if marker in content:
        content = content.replace(marker, f"{marker}\n{entry}")
    else:
        content += f"\n{entry}"

    with open(MEMORY_FILE, "w") as f:
        f.write(content)

    log_action(f"MEMORY_REGISTERED — hash:{contact_hash[:16]}... — niche:{niche_key}")


# === MAIN ===

def main():
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv
    batch = None
    specific_file = None

    for i, arg in enumerate(sys.argv):
        if arg == "--file" and i + 1 < len(sys.argv):
            specific_file = sys.argv[i + 1]
        if arg == "--batch" and i + 1 < len(sys.argv):
            batch = sys.argv[i + 1]

    mode_label = f"{'DRY RUN' if dry_run else 'LIVE'} | batch:{batch or 'all'}"
    print(f"{'DRY' if dry_run else 'LIVE'} ENRICHER v2.0 — {mode_label} — {NOW}")
    print(f"{'=' * 60}")

    log_action(f"ENRICHER_START — mode:{mode_label} — file:{specific_file or 'auto'}")

    leads = load_leads_files(specific_file, batch)
    if not leads:
        msg = f"No leads found (batch={batch or 'all'})"
        print(f"  {msg}")
        log_action(f"ENRICHER_EMPTY — {msg}", "WARNING")
        sys.exit(0)

    print(f"Loaded {len(leads)} leads to process\n")

    enriched = []
    stats = {"total": len(leads), "auto_send": 0, "manual_review": 0, "low_priority": 0, "archived": 0, "duplicate": 0}

    for lead in leads:
        normalized = normalize_lead(lead)
        intent_score, breakdown, action, contact_hash, niche_info = score_lead(normalized)

        enriched_lead = {
            "deal_id": str(uuid.uuid4())[:8],
            "source": normalized["source"],
            "url": normalized["url"],
            "pain_signal": normalized["title"] or normalized["body"][:100],
            "intent_score": intent_score,
            "score_breakdown": breakdown,
            "contact_hash": contact_hash,
            "niche": niche_info,
            "action": action,
            "enriched": True,
            "enriched_at": NOW,
            "original_data": {
                "title": normalized["title"][:200],
                "subreddit": normalized["subreddit"],
                "engagement": normalized["engagement"],
            }
        }
        enriched.append(enriched_lead)

        if "already_contacted" in str(breakdown):
            stats["duplicate"] += 1
        elif action == "AUTO_SEND":
            stats["auto_send"] += 1
        elif action == "MANUAL_REVIEW":
            stats["manual_review"] += 1
        elif action == "LOW_PRIORITY":
            stats["low_priority"] += 1
        else:
            stats["archived"] += 1

        if not dry_run and action in ("AUTO_SEND", "MANUAL_REVIEW"):
            register_in_memory(contact_hash, niche_info["key"], normalized["source"], action)

        icon = {"AUTO_SEND": ">>", "MANUAL_REVIEW": ">>", "LOW_PRIORITY": "--", "ARCHIVED": "xx"}.get(action, "?")
        niche_label = f"{niche_info['key']}" + (" PAIN" if niche_info['pain_detected'] else "")
        print(f"  {icon} [{intent_score:>5.1f}] {action:<15} | {niche_label:<30} | {normalized['title'][:50]}")
        if verbose and breakdown:
            print(f"         -> {', '.join(breakdown)}")

    print(f"\n{'=' * 60}")

    output_file, new_count, total_count = write_enriched_output(enriched, dry_run)

    if not dry_run:
        alert_file = write_telegram_alert(enriched)
        stats_file = write_stats(enriched, stats, batch)
    else:
        alert_file = None
        stats_file = None
        print(f"\nDRY RUN — would write {new_count} new leads (total: {total_count})")

    pain_count = sum(1 for l in enriched if l.get("niche", {}).get("pain_detected", False))
    print(f"\nENRICHER v2.0 SUMMARY — {TODAY} ({batch or 'all'})")
    print(f"   Total processed  : {len(leads)}")
    print(f"   Auto-send        : {stats['auto_send']}")
    print(f"   Manual review    : {stats['manual_review']}")
    print(f"   Low priority     : {stats['low_priority']}")
    print(f"   Archived         : {stats['archived']}")
    print(f"   Duplicates       : {stats['duplicate']}")
    print(f"   Pain signals     : {pain_count}/{len(leads)} ({round(pain_count/len(leads)*100) if leads else 0}%)")
    print(f"   Enriched         : {output_file}")
    if alert_file:
        print(f"   Telegram         : {alert_file}")
    if stats_file:
        print(f"   Stats            : {stats_file}")

    log_action(
        f"ENRICHER_COMPLETE — processed:{len(leads)} — "
        f"auto:{stats['auto_send']} manual:{stats['manual_review']} "
        f"low:{stats['low_priority']} archived:{stats['archived']} "
        f"dupes:{stats['duplicate']} pain:{pain_count}"
    )

    return stats


if __name__ == "__main__":
    stats = main()
