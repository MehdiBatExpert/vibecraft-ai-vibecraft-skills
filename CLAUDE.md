# CLAUDE.md — VibeCraft Global
> Mis à jour : 03/05/2026 | Source de vérité pour Claude Code sur toutes les sessions VibeCraft
> Ce fichier remplace entièrement l'ancien CLAUDE.md EasyClaw.

---

## QUI EST MEHDI

Mehdi est solo founder de **VibeCraft** (brand : MehdiBuilds / @MehdiBuilds / @VibeCraftAgent).
VibeCraft = solutions vibe-code verticalisées par métier, IA-powered GTM et SDR automation pour TPE/PME françaises.
Stack locale-first, RGPD-native, low-ticket (79-499 EUR). Opère sous AVANTIS Partner & Conseils.
GitHub : MehdiBatExpert

**Mehdi ne tape pas de commandes.** Claude Code exécute tout. Mehdi décide, valide, oriente.

---

## SEPARATION DES ROLES — CRITIQUE

| Outil | Role |
|---|---|
| **Claude chat** (claude.ai) | Planification, strategie, decisions, analyse |
| **Claude Code** | Execution skills SDR/marketing, pipelines, VPS, fichiers |
| **Notion** | Source de verite (accessible depuis les deux via MCP) |
| **Mistral Workflows** | Orchestration agents durables (remplace Hermes) |

Quand une tache appartient a Claude chat (strategie, positionnement, arbitrage) : le signaler plutot que l'executer.
Quand une tache est un pipeline SDR ou marketing : l'executer directement avec les skills disponibles.

---

## REGLES ABSOLUES

1. **Jamais le tiret long** (`—`) dans aucune reponse. Utiliser `-` uniquement.
2. **Jamais toucher au VPS** sans demande explicite de Mehdi.
3. **Jamais creer une page Notion** sans verifier qu'elle n'existe pas d'abord.
4. **Jamais melanger** les stacks VibeCraft et EasyClaw/Synapse/Hermes-EasyClaw.
5. **Securite RGPD absolue** : aucun outil US early-stage ne touche aux donnees clients, leads, strategie ou workspaces Avantis/MehdiBuilds.
6. **Documentation avant execution** : lire les guides avant de coder ou deployer.
7. **Un livrable a la fois** : valider avec Mehdi avant de continuer.
8. **Ne jamais inventer** : verifier dans Notion ou les fichiers locaux.
9. **Credentials** : jamais dans les prompts ou dans Claude chat.
10. **ZohoWorkDrive** (`~/Library/CloudStorage/ZohoWorkDriveTrueSync-RENOVATECH76`) : ne jamais toucher, appartient a RENOVATECH76.

---

## STACK ACTIVE (mai 2026)

### Infra

- **VPS Hostinger** : `root@31.97.178.87` | SSH key : `~/.ssh/id_vps_new` (sans passphrase)
- **Oracle A1 Flex** : `ubuntu@141.253.121.181` | SSH key : `~/.ssh/id_vps_new`
- **Agent framework** : Mistral Workflows (public preview depuis 28/04/2026, base Temporal)
- **Hermes/Synapse** : OFFLINE - service arrete, desactive, ne pas relancer
- **ANTHROPIC_API_KEY** : utiliser uniquement via claude.ai, ne pas mettre sur le VPS

### Mac local

- **Claude Code** : CLI + Desktop (ce fichier est lu par les deux)
- **Mistral Code** : `~/.mistralcode/`
- **Warp** : terminal principal, configs dans `~/.warp/tab_configs/` (TOML)
- **Git** : branche par defaut `main`, GitHub MehdiBatExpert
- **SSH** : `~/.ssh/id_vps_new` pour les deux VPS

### Services connectes

- **Notion MCP** : acces handoffs + CRM + Mission Control
- **Brevo** : SMTP outreach
- **Postiz** : scheduling social
- **Telegram** : interface agent
- **X** : @VibeCraftAgent (veille intel + posts), @MehdiBuilds (personnel, Mehdi valide)

### Google Drive

- Chemin correct Mac : `~/Library/CloudStorage/GoogleDrive-mehdi@avantispartner.fr/Mon Drive/`
- Ne pas utiliser "My Drive" comme chemin

---

## REPOS ET SKILLS LOCAUX

### Repos actifs

```
~/vibecraft-ai-vibecraft-skills/   - Skills generiques MIT (outreach, prospect, churn...)
~/foundersales/                    - Skills SDR (fs-find, fs-qualify, fs-outreach...)
~/MarketingPilot-private/          - Sprint MarketingPilot en cours (Gumroad 79 EUR)
~/MehdiBatExpert/                  - Repo GitHub principal
```

### A ignorer / ne pas toucher

```
~/foundersales 2/                  - Doublon de ~/foundersales/ - a supprimer
~/SYNAPSE_VPS_CONFIG/              - EasyClaw mort, archive
~/mob-ia-hybrid/                   - Ancien projet
~/whisper_test/                    - Test isole
~/tools/archive/                   - Archives, ne pas modifier
```

### Skills SDR disponibles (~/foundersales/commands/)

```
fs-find      - Identifier 20-50 leads B2B qualifies sur un canal
fs-qualify   - Scorer un lead B2B sur 10 points
fs-outreach  - Rediger 3 variantes cold message personnalise
fs-sequence  - Planifier relances 4 touches sur 14 jours
fs-prep      - Preparer un call decouverte avec agenda MEDDIC
fs-debrief   - Debriefer un call avec score MEDDIC + next steps
fs-offer     - Generer une proposition commerciale post-call
fs-icp       - Definir ICP B2B actionnable
```

### Skills generiques disponibles (~/vibecraft-ai-vibecraft-skills/)

```
fr-cold-email-outreach   - Cold emails en francais, 3 variantes
fr-lead-qualification    - Qualification lead 10 points
fr-prospect-scraper      - Requetes sourcing leads (Reddit, LinkedIn, X)
fr-meeting-brief         - Brief call decouverte MEDDIC
fr-competitor-intel      - Analyse concurrentielle sources publiques
followup-nurturing       - Sequence relance 4 touches 14 jours
churn-radar              - Detection signaux churn
blog-newsletter          - Repurpose contenu sales -> newsletter
gtm-content-repurpose    - 1 contenu -> 5 formats canaux
lead-magnet-builder      - Outline lead magnet depuis ICP
seo-geo-content          - Contenu SEO geo-cible B2B local
support-triage           - Classification messages support entrant
```

---

## NOTION — IDS STABLES

```
Mission Control parent    : 337d6526dc038105b9cdd18b9626d653
Sprint Board Kanban       : 337d6526dc03818a8148e77fe290936a
CRON JOBS doc             : 343d6526dc0381d9a4cfd224b9f57efd
CRM natif                 : 572d6526dc03821c9fdf0102aa8590c1
Rapports Veille X         : 349d6526dc03814a8a45c282d5662ae0
VibeCraft Hub             : 337d6526dc0381578cded3bde96f89f6
```

### Protocole Notion

- Toujours `notion-search` avant `notion-create-pages`
- Nouvelles pages handoff : parent `337d6526dc038105b9cdd18b9626d653`
- Format handoff standard : CE QUI A ETE FAIT / ETAT VPS / ETAT CRONS / DETTE TECHNIQUE / PLAN SESSION SUIVANTE / COMMANDE REPRISE RAPIDE / LIENS UTILES
- Fetch par raw page ID (sans tirets requis)

---

## PROTOCOLE DEBUT DE SESSION CLAUDE CODE

1. Lire ce fichier (deja fait si tu lis ceci)
2. Verifier le CLAUDE.md du repo courant s'il existe
3. Fetcher le dernier handoff Notion via MCP
4. Lister les taches du jour issues du handoff
5. Proposer un plan sequenced, attendre validation Mehdi

---

## PIPELINES SDR/MARKETING — EXECUTION DIRECTE

Ces pipelines s'executent dans Claude Code sans passer par Claude chat :

### Pipeline Outreach complet

```
1. fs-find      -> sourcer les leads (LinkedIn prioritaire, X pour intel)
2. fs-qualify   -> scorer chaque lead /10
3. fs-outreach  -> 3 variantes cold message
4. fs-sequence  -> relances 4 touches 14 jours
```

### Pipeline Email batch (Brevo)

```
Skill : brevo-outreach
Input : liste leads qualifies + contexte ICP
Output : campagne Brevo configuree + tracking
```

### Pipeline Content Marketing

```
gtm-content-repurpose -> 1 contenu -> X, LinkedIn, Reddit, Discord, Newsletter
blog-newsletter       -> contenu sales -> format publication
```

### Pipeline Nurturing

```
followup-nurturing -> sequence relance post-premier contact
```

---

## REGLES PYTHON / BASH

- `pip install` : toujours avec `--break-system-packages` sur le VPS
- Variables sensibles : lire depuis `.env` via `python-dotenv`, jamais hardcodees
- Verifier port libre avant service : `ss -tlnp | grep PORT`
- Backup avant modification fichier critique : `cp fichier fichier.bak.$(date +%Y%m%d_%H%M%S)`

---

## PROTOCOLE AVANT DE CODER - OBLIGATOIRE

Avant tout nouveau composant, script ou pipeline, appliquer dans l'ordre :

1. ARCHITECTURE D'ABORD
   "Voici l'architecture que je propose (Worker / Agent pur / Script standalone).
   Valide avant que je commence a coder."
   - Exposer 2 options max avec trade-offs clairs
   - Attendre validation Mehdi

2. STRUCTURE RECOMMANDEE
   - Clean Code : fonctions courtes, noms explicites, separation des responsabilites
   - Pattern Nick : directives/ (SOPs) + execution/ (scripts deterministes) + .tmp/ (intermediaires)
   - Fichiers sensibles : lecture depuis .env, jamais hardcodes

3. TESTS + MONITORING + DOCUMENTATION
   - Ajouter un test de smoke avant de declarer "done"
   - Logger les etapes critiques (pas tout, juste les points de defaillance probables)
   - Documenter le "pourquoi" du choix architectural dans un commentaire de tete de fichier

---

## STYLE DE REPONSE

- Langue : francais exclusivement sauf si Mehdi ecrit en anglais
- Format : pragmatique, direct, oriente action
- Commandes VPS : toujours dans des blocs de code
- Jamais "exactement", "parfaitement" en debut de reponse
- Un bloc valide avant le suivant
- Prompts techniques complexes : appliquer CHATBOT R.T.C.R.O.S. (Role, Tache, Contexte, Raisonnement, Sortie, Stop)

---

## FIN DE SESSION — CHECKLIST

Avant de terminer, toujours produire :

```
- Ce qui a ete fait (fichiers modifies + commandes executees)
- Ce qui reste (prochaine session)
- Notion a mettre a jour ? (oui/non + quelle page)
- Points d'attention (risques, choses a surveiller)
```

Creer un handoff Notion sous Mission Control si session > 30 min ou changement infrastructure.

---

*VibeCraft Global CLAUDE.md - v1.1 - 03/05/2026*
*Remplace entierement l'ancien CLAUDE.md EasyClaw (ref : geteasyclaw.app / Synapse OpenClaw)*
*Ne pas versionner dans un repo public.*
