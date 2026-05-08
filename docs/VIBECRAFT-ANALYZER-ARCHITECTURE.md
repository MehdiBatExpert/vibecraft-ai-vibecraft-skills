# VibeCraft Business Analyzer - Architecture Phase 0
> Date : 09/05/2026 | Status : EN ATTENTE VALIDATION MEHDI
> Stop absolu : zero code fonctionnel avant validation

---

## 1. DECISION CRITIQUE : CHOIX SDK

### Contexte technique identifie

L'**Agent SDK** (`@anthropic-ai/claude-agent-sdk` v0.2.136) bundle un **binaire natif Node.js** (Claude Code executable). Ce binaire :
- Fonctionne sur Vercel Serverless Functions (runtime Node.js)
- **Incompatible Vercel Edge Functions** (V8 isolate, pas de binaires natifs)
- Incompatible browser/client-side
- Cold start plus lourd (~30-60s premiere requete)

L'**Anthropic Client SDK** (`@anthropic-ai/sdk` v0.95.1) :
- Fonctionne partout : Node.js, browser, Edge Functions
- Pas d'outils integres (pas de WebFetch autonome)
- Cold start rapide (<2s)

### Implication pour le Business Analyzer

| Mode | URL en input ? | Outils SDK utiles ? | SDK recommande |
|------|---------------|---------------------|----------------|
| MODE 1 - Prospect pre-call | Non | Non (texte pur) | Client SDK |
| MODE 2 - Analyse concurrent | Oui (URL concurrent) | **Oui (WebFetch)** | Agent SDK |
| MODE 3 - Viabilite offre | Non | Non | Client SDK |
| MODE 4 - Evaluation outil/repo | Oui (URL GitHub/SaaS) | **Oui (WebFetch, WebSearch)** | Agent SDK |
| MODE 5 - Analyse segment marche | Non | Non | Client SDK |
| MODE 6 - Revenue pipeline | Non | Non | Client SDK |

---

## 2. OPTIONS ARCHITECTURE

### Option A - Agent SDK (Vercel Serverless Node.js)

```
[React Frontend]
     |
     v HTTP (streaming SSE)
[Next.js API Routes /api/analyze/[mode]]
     |
     v in-process
[Agent SDK query()]
     |
     v Anthropic API (+ WebFetch/WebSearch tools pour modes 2 et 4)
```

**Avantages**
- Modes 2 et 4 : Claude browse l'URL lui-meme et produit l'analyse (zero preprocessing)
- Streaming natif vers le frontend (affichage progressif des tabs)
- Un seul SDK, coherence codebase
- Outils autonomes : WebSearch sur concurrents, WebFetch sur GitHub repos

**Inconvenients**
- Cold start lourd sur Vercel (premiere analyse lente)
- Timeout Vercel : 10s (Hobby) / 300s (Pro) - une analyse complete peut depasser 60s
- Binaire natif : `@anthropic-ai/claude-agent-sdk` = ~100MB deploye
- Complexity : gestion du streaming SSE entre Agent SDK et React

**Contrainte critique** : Il faut un **plan Vercel Pro** pour les timeouts > 10s.

---

### Option B - Anthropic Client SDK + Next.js API Routes (RECOMMANDE)

```
[React Frontend]
     |
     v HTTP (streaming SSE ou batch)
[Next.js API Routes /api/analyze/[mode]]
     |
     v Promise.all() x N agents
[Anthropic Client SDK messages.create()]
     |
     v Anthropic API
```

**Avantages**
- Cold start <2s
- Fonctionne sur Vercel Hobby (timeouts 60s suffisants par call)
- Deploy leger, pas de binaire natif
- Promise.all() simple pour agents paralleles
- Compatible Vercel Edge Functions si besoin

**Inconvenients**
- Modes 2 et 4 : l'URL doit etre pre-fetchee cote serveur avant le call Claude (etape supplementaire)
- Pas de WebSearch autonome - compenser avec des prompts contextuels

**Solution pour modes 2 et 4** : Ajouter un `fetch()` server-side dans l'API route pour recuperer le contenu HTML de l'URL, puis passer le contenu comme contexte au prompt Claude.

---

### RECOMMANDATION

**Option B (Anthropic Client SDK)** pour v1 car :
- Viable sur Vercel Hobby (budget controle)
- Rapide a deployer
- Modes 2 et 4 : pre-fetch URL server-side + context injection = resultat equivalent
- Migration vers Agent SDK possible en v2 si besoin du WebSearch autonome

**Si modes 2 et 4 sont prioritaires** -> Option A + Vercel Pro obligatoire.

---

## 3. ARCHITECTURE TECHNIQUE RETENUE (Option B)

### Stack

```
vibecraft-business-analyzer/
├── Next.js 15 (App Router)
├── React 18 + TypeScript 5
├── Tailwind CSS 3
├── @anthropic-ai/sdk v0.95.1
├── shadcn/ui (composants)
└── Vercel (deploy prive)
```

### Flux par mode

```
User selectionne mode + remplit form
     |
     v
handleAnalyze() [React state]
     |
     v POST /api/analyze
[API Route Next.js]
     |
     v Promise.all([agent1, agent2, ...agentN])
     |
     v responses JSON
     |
     v setResults(data) [React state]
     |
     v Tabs affichent les blocs structures
     |
     v Bouton "Export JSON" -> download local
```

---

## 4. PROMPT SKELETONS PAR MODE

### Conventions
- Chaque "agent" = 1 call `messages.create()` avec un prompt specialise
- Les agents d'un meme mode tournent en `Promise.all()`
- Format de sortie : JSON structure pour permettre le rendu par tab
- Modele : `claude-sonnet-4-5` (rapport qualite/cout optimal)

---

### MODE 1 - Prospect pre-call (5 tabs, 3 agents paralleles)

**Input** : nom, secteur, taille, URL, notes

**Agent 1 - IA-Readiness + Quick Wins** (tabs 1 et 2)
```
SYSTEM: Tu es un expert VibeCraft en evaluation IA-readiness des PME francaises.
VibeCraft vend des solutions vibe-code verticalisees IA-powered pour TPE/PME, ticket 79-499 EUR.

TASK: Analyse la readiness IA de ce prospect et identifie 3 quick wins immediats.

OUTPUT JSON:
{
  "ia_readiness": {
    "score": 0-10,
    "niveau": "Debutant|Intermediaire|Avance",
    "signaux_positifs": ["..."],
    "freins_identifies": ["..."],
    "synthese": "..."
  },
  "quick_wins": [
    { "action": "...", "impact": "Fort|Moyen|Faible", "effort": "Fort|Moyen|Faible", "delai": "..." }
  ]
}
```

**Agent 2 - ROI estime + Objections** (tabs 3 et 4)
```
SYSTEM: Tu es un expert ROI et objections handling pour solutions IA B2B francaises. Ticket cible VibeCraft : 79-499 EUR/mois.

TASK: Estime le ROI realiste et anticipe les 5 principales objections.

OUTPUT JSON:
{
  "roi": {
    "gain_temps_mensuel_heures": 0,
    "valeur_monetaire_estimee": "...",
    "payback_mois": 0,
    "hypotheses": ["..."]
  },
  "objections": [
    { "objection": "...", "reponse_recommandee": "...", "probabilite": "Haute|Moyenne|Faible" }
  ]
}
```

**Agent 3 - Decision GO/PASS** (tab 5)
```
SYSTEM: Tu es le decision-maker VibeCraft. Synthese finale go/pass basee sur le profil prospect.

TASK: Rends un verdict GO ou PASS avec justification structuree.

OUTPUT JSON:
{
  "verdict": "GO|PASS|QUALIFIED_WATCH",
  "score_global": 0-10,
  "top_3_raisons": ["..."],
  "prochaine_action": "...",
  "pitch_accroche": "..."
}
```

---

### MODE 2 - Analyse concurrent (5 tabs, 3 agents paralleles)

**Input** : URL concurrent (pre-fetchee server-side)

**Agent 1 - Positioning + Pricing** (tabs 1 et 2)
```
SYSTEM: Tu es un expert competitive intelligence pour solutions IA B2B francaises.

TASK: A partir du contenu de ce site concurrent, analyse le positionnement et la structure de prix.

OUTPUT JSON:
{
  "positioning": {
    "proposition_valeur": "...",
    "cible_declaree": "...",
    "differenciants_cles": ["..."],
    "ton_communication": "..."
  },
  "pricing": {
    "modele": "Freemium|Abonnement|Usage|Projet",
    "fourchette": "...",
    "tiers": [{ "nom": "...", "prix": "...", "features_cles": ["..."] }]
  }
}
```

**Agent 2 - Forces + Faiblesses** (tabs 3 et 4)
```
SYSTEM: Analyse SWOT competitor focusee sur les forces et faiblesses vs VibeCraft.

OUTPUT JSON:
{
  "forces": [{ "point": "...", "impact_concurrentiel": "Elevé|Moyen|Faible" }],
  "faiblesses": [{ "point": "...", "opportunite_vibecraft": "..." }]
}
```

**Agent 3 - Battle Card VibeCraft** (tab 5)
```
SYSTEM: Tu es le Sales Enablement de VibeCraft. Cree une battle card actionnable.

OUTPUT JSON:
{
  "avantages_vibecraft": ["..."],
  "arguments_vs_concurrent": [{ "leur_claim": "...", "notre_reponse": "..." }],
  "scenarios_gagner": ["..."],
  "scenarios_perdre": ["..."],
  "one_liner_pitch": "..."
}
```

---

### MODE 3 - Viabilite offre (5 tabs, 3 agents paralleles)

**Input** : description offre, prix, ICP cible

**Agent 1 - Fit marche + Pricing check** (tabs 1 et 2)
```
OUTPUT JSON:
{
  "fit_marche": {
    "score": 0-10,
    "adéquation_probleme_solution": "...",
    "taille_marche_accessible": "...",
    "timing_marche": "Trop tot|Bon|Trop tard"
  },
  "pricing": {
    "verdict": "Sous-value|Optimal|Sur-value",
    "prix_recommande_min": 0,
    "prix_recommande_max": 0,
    "justification": "...",
    "comparables_marche": ["..."]
  }
}
```

**Agent 2 - Canaux + Risques** (tabs 3 et 4)
```
OUTPUT JSON:
{
  "canaux": [
    { "canal": "...", "priorite": 1-5, "effort": "Fort|Moyen|Faible", "cac_estime": "..." }
  ],
  "risques": [
    { "risque": "...", "probabilite": "Haute|Moyenne|Faible", "mitigation": "..." }
  ]
}
```

**Agent 3 - Verdict** (tab 5)
```
OUTPUT JSON:
{
  "verdict": "GO|WATCH|PASS",
  "score_viabilite": 0-10,
  "condition_go": "...",
  "next_step_immediat": "...",
  "hypothesis_critique_a_tester": "..."
}
```

---

### MODE 4 - Evaluation outil/repo (4 tabs, 2 agents paralleles)

**Input** : URL GitHub ou SaaS (pre-fetchee server-side)

**Agent 1 - Pertinence VibeCraft + Stack fit** (tabs 1 et 2)
```
SYSTEM: Tu evalues des outils/repos pour integration dans l'ecosysteme VibeCraft.
VibeCraft stack : React/TypeScript, Python, Node.js, Vercel, APIs REST, RGPD-first.

OUTPUT JSON:
{
  "pertinence_vibecraft": {
    "score": 0-10,
    "cas_usage_identifies": ["..."],
    "clients_cibles_impactes": ["..."],
    "valeur_ajoutee_concrete": "..."
  },
  "stack_fit": {
    "compatible": true|false,
    "langages": ["..."],
    "dependances_majeures": ["..."],
    "conflits_potentiels": ["..."]
  }
}
```

**Agent 2 - Effort integration + Verdict** (tabs 3 et 4)
```
OUTPUT JSON:
{
  "effort_integration": {
    "complexite": "Faible|Moyenne|Elevee",
    "jours_estimation": 0,
    "prerequis": ["..."],
    "risques_techniques": ["..."]
  },
  "verdict": {
    "decision": "ADOPT|WATCH|SKIP",
    "score_final": 0-10,
    "justification": "...",
    "conditions_adoption": ["..."]
  }
}
```

---

### MODE 5 - Analyse segment marche (5 tabs, 3 agents paralleles)

**Input** : secteur, taille entreprises, zone geo

**Agent 1 - TAM estime + Concurrence** (tabs 1 et 2)
```
OUTPUT JSON:
{
  "tam": {
    "estimation_entreprises_fr": 0,
    "estimation_revenu_annuel_total": "...",
    "sam_vibecraft": "...",
    "som_12mois": "...",
    "sources_hypotheses": ["..."]
  },
  "concurrence": {
    "acteurs_principaux": [{ "nom": "...", "part_marche_estimee": "...", "positionnement": "..." }],
    "intensite_concurrentielle": "Faible|Moderate|Elevee",
    "barriere_entree": "..."
  }
}
```

**Agent 2 - ICP fit + Canaux** (tabs 3 et 4)
```
OUTPUT JSON:
{
  "icp_fit": {
    "score_adéquation": 0-10,
    "profil_ideal": { "taille": "...", "secteur": "...", "trigger_achat": "...", "decision_maker": "..." },
    "signaux_achat": ["..."]
  },
  "canaux": [
    { "canal": "...", "efficacite_estimee": "Haute|Moyenne|Faible", "cac_range": "..." }
  ]
}
```

**Agent 3 - Potentiel MRR** (tab 5)
```
OUTPUT JSON:
{
  "mrr_potentiel": {
    "scenario_conservateur": { "clients_12mois": 0, "mrr": 0 },
    "scenario_realiste": { "clients_12mois": 0, "mrr": 0 },
    "scenario_optimiste": { "clients_12mois": 0, "mrr": 0 }
  },
  "recommandation_priorite": "Haute|Moyenne|Faible",
  "next_action": "..."
}
```

---

### MODE 6 - Revenue pipeline (4 tabs, 3 agents paralleles)

**Input** : deals en cours (JSON ou saisie manuelle)

**Agent 1 - Funnel state** (tab 1)
```
OUTPUT JSON:
{
  "funnel": {
    "total_deals": 0,
    "par_stage": [{ "stage": "...", "count": 0, "valeur_totale": 0 }],
    "deals_stales": [{ "nom": "...", "dernier_contact": "...", "valeur": 0 }],
    "taux_conversion_estime": "..."
  }
}
```

**Agent 2 - MRR projete + Risques** (tabs 2 et 3)
```
OUTPUT JSON:
{
  "mrr_projete": {
    "best_case_30j": 0,
    "worst_case_30j": 0,
    "most_likely_30j": 0,
    "deals_closes_probables": ["..."]
  },
  "risques_pipeline": [
    { "deal": "...", "risque": "...", "probabilite_perte": "Haute|Moyenne|Faible", "action_recommandee": "..." }
  ]
}
```

**Agent 3 - Actions prioritaires** (tab 4)
```
OUTPUT JSON:
{
  "actions": [
    { "priorite": 1, "action": "...", "deal_cible": "...", "deadline": "...", "impact_mrr": 0 }
  ],
  "focus_semaine": "...",
  "deal_a_fermer_en_urgence": "..."
}
```

---

## 5. STRUCTURE FICHIERS RECOMMANDEE

```
vibecraft-business-analyzer/
├── .env.local                        # ANTHROPIC_API_KEY (jamais commite)
├── .env.example                      # Template
├── .gitignore
├── next.config.ts
├── tsconfig.json
├── package.json
│
├── src/
│   ├── app/
│   │   ├── layout.tsx               # Layout global dark mode
│   │   ├── page.tsx                 # Page principale (mode selector + form)
│   │   └── api/
│   │       └── analyze/
│   │           └── route.ts         # POST handler : mode + input -> agents paralleles
│   │
│   ├── components/
│   │   ├── ModeSelector.tsx         # Dropdown/pills 6 modes
│   │   ├── forms/
│   │   │   ├── ProspectForm.tsx     # MODE 1
│   │   │   ├── ConcurrentForm.tsx   # MODE 2
│   │   │   ├── OffreForm.tsx        # MODE 3
│   │   │   ├── OutilForm.tsx        # MODE 4
│   │   │   ├── SegmentForm.tsx      # MODE 5
│   │   │   └── PipelineForm.tsx     # MODE 6
│   │   ├── results/
│   │   │   ├── ResultTabs.tsx       # Tabs horizontaux style Roxabi
│   │   │   ├── VerdictBadge.tsx     # Badge GO/PASS/WATCH/ADOPT/SKIP
│   │   │   └── ExportButton.tsx     # Export JSON local
│   │   └── ui/
│   │       ├── LoadingSpinner.tsx
│   │       └── ScoreBar.tsx
│   │
│   ├── lib/
│   │   ├── anthropic.ts             # Client SDK init + helper runParallelAgents()
│   │   ├── prompts/
│   │   │   ├── mode1-prospect.ts    # Prompts MODE 1
│   │   │   ├── mode2-concurrent.ts  # Prompts MODE 2
│   │   │   ├── mode3-offre.ts       # Prompts MODE 3
│   │   │   ├── mode4-outil.ts       # Prompts MODE 4
│   │   │   ├── mode5-segment.ts     # Prompts MODE 5
│   │   │   └── mode6-pipeline.ts   # Prompts MODE 6
│   │   └── url-fetcher.ts           # Pre-fetch URL pour modes 2 et 4
│   │
│   └── types/
│       ├── modes.ts                 # Types input par mode
│       └── results.ts               # Types output JSON par mode
│
├── public/
└── docs/
    └── VIBECRAFT-ANALYZER-ARCHITECTURE.md  # Ce fichier
```

---

## 6. ESTIMATION COUT TOKENS PAR MODE

**Modele retenu** : `claude-sonnet-4-5`
**Tarif** : $3/MTok input | $15/MTok output (mai 2026)

| Mode | Agents | Input tokens (est.) | Output tokens (est.) | Cout ($) |
|------|--------|--------------------|-----------------------|----------|
| MODE 1 - Prospect | 3 | ~4 500 | ~3 000 | ~$0.058 |
| MODE 2 - Concurrent | 3 | ~8 000* | ~3 500 | ~$0.076 |
| MODE 3 - Offre | 3 | ~3 500 | ~3 000 | ~$0.055 |
| MODE 4 - Outil/repo | 2 | ~7 000* | ~2 500 | ~$0.058 |
| MODE 5 - Segment | 3 | ~4 000 | ~3 500 | ~$0.064 |
| MODE 6 - Pipeline | 3 | ~5 000 | ~3 000 | ~$0.060 |

*Modes 2 et 4 : input plus lourd car contenu URL injecte en contexte.

**Budget mensuel estimé pour usage Mehdi seul** :
- 5 analyses/jour = 150/mois
- Cout moyen $0.065/analyse
- **Total : ~$9.75/mois** (negligeable)

---

## 7. RISQUES IDENTIFIES

### Risque 1 - SECURITE API KEY (CRITIQUE)
**Probleme** : Cle Anthropic jamais exposee cote browser.
**Mitigation** : API key uniquement dans les variables d'environnement Vercel (ANTHROPIC_API_KEY). Le call Claude se fait uniquement dans les API routes Next.js (server-side). Zero call direct depuis le browser.
**Status** : Architecture B resolves this nativement.

### Risque 2 - TIMEOUT VERCEL (MOYEN)
**Probleme** : 3 agents en Promise.all() + fetch URL = potentiellement 20-40s.
**Mitigation** : Vercel Hobby permet 60s max sur les Serverless Functions (pas Edge). Ca devrait suffire. Si un mode depasse, optimiser le prompt ou splitter en 2 requetes.
**Fallback** : Passer a Vercel Pro (300s) si necessaire.

### Risque 3 - QUALITE ANALYSE URL (MOYEN)
**Probleme** : Pre-fetch HTML brut = beaucoup de bruit (nav, footer, scripts).
**Mitigation** : Server-side, utiliser `cheerio` ou regex basique pour extraire le texte pertinent avant injection dans le prompt. Limiter a 3000 tokens de contenu.

### Risque 4 - JSON PARSING (FAIBLE)
**Probleme** : Claude ne retourne pas toujours du JSON valide.
**Mitigation** : Wrapper `extractJson()` avec regex + JSON.parse() + fallback message d'erreur utilisateur. Utiliser le parametre `response_format: { type: "json_object" }` si disponible.

### Risque 5 - COLD START VERCEL (FAIBLE)
**Probleme** : Premiere requete lente apres periode d'inactivite.
**Mitigation** : Acceptable pour usage personnel Mehdi uniquement. Pas de SLA a tenir.

### Risque 6 - RGPD (FAIBLE)
**Probleme** : Les inputs contiennent des noms de prospects/entreprises.
**Mitigation** : Zero stockage base de donnees. State React ephemere + export JSON local. Aucune retention cote Anthropic API au-dela de la requete. Conforme RGPD pour usage interne.

---

## 8. DECISION REQUISE MEHDI

**Questions avant Phase 1 :**

1. **Architecture** : Option B (Client SDK) est recommandee. Valides-tu ?
   - Option A (Agent SDK) si tu veux le WebSearch autonome pour modes 2/4.

2. **Modele** : `claude-sonnet-4-5` confirme ? (ou `claude-haiku-4-5` pour encore moins cher ?)

3. **Modes 2 et 4** : Pre-fetch URL server-side suffit, ou tu veux un vrai agent autonome qui browse ?

4. **Design** : shadcn/ui comme base composants ? (Tailwind compatible, dark mode natif)

5. **Package manager** : npm (defaut) ou pnpm ?

---

## 9. PLAN DE PHASES (apres validation)

| Phase | Contenu | Livrable | Validation |
|-------|---------|----------|------------|
| **Phase 0** | Architecture | Ce document | Mehdi ✓ |
| **Phase 1** | Setup Next.js + skeleton UI + API route | App vide deployee sur Vercel | Mehdi |
| **Phase 2** | MODE 1 complet (form + agents + tabs) | Mode 1 fonctionnel | Mehdi |
| **Phase 3** | MODES 2-3 | 3 modes fonctionnels | Mehdi |
| **Phase 4** | MODES 4-5-6 | App complete 6 modes | Mehdi |
| **Phase 5** | Polish design (Roxabi feel) + export JSON | V1 finale | Mehdi |

---

*Document genere par Claude Code - VibeCraft Business Analyzer - Phase 0*
*Ne pas commencer Phase 1 sans validation explicite Mehdi*
