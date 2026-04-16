# wiki/scoring-leads.md
> Template basé sur un fichier en production réelle.
> Adapter les seuils et critères à ton contexte.
> Dernière mise à jour : [DATE]

---

## Principe

Score de 0 à 10. Chaque critère est évalué indépendamment.
Score final = moyenne pondérée des 5 critères.
**Jamais arrondir vers le haut. En cas de doute, scorer bas.**

---

## Les 5 critères

### Critère 1 — Intent explicite (poids : 30%)

| Signal | Score |
|---|---|
| Demande directe d'aide / d'outil / de solution | 10 |
| Frustration explicite avec douleur nommée | 8-9 |
| Question ouverte sur comment résoudre X | 7 |
| Curiosité générale sans douleur | 5 |
| Contenu éducatif / informatif | 2 |
| Promotion de son propre produit | 0 |

### Critère 2 — Fit ICP (poids : 25%)

| Profil | Score |
|---|---|
| ICP A exact (profil + taille + secteur confirmés) | 10 |
| ICP B exact | 9 |
| ICP C (agence / revendeur) | 7 |
| Profil adjacent — potentiellement intéressé | 5 |
| Hors ICP mais pas anti-ICP | 3 |
| Anti-ICP confirmé | 0 |

### Critère 3 — Urgence / Timing (poids : 20%)

| Signal | Score |
|---|---|
| "maintenant" / "cette semaine" / "urgent" | 10 |
| Signal récent (< 7 jours) + douleur active | 8 |
| Recherche active d'alternatives | 7 |
| Exploration sans deadline | 5 |
| Contenu vieux (> 30 jours) | 1 |

### Critère 4 — Budget signal (poids : 15%)

| Signal | Score |
|---|---|
| Mention d'un outil payant concurrent | 10 |
| Profil founder / décideur confirmé | 8 |
| Équipe identifiable (pas solo sans budget) | 6 |
| Freelance / solopreneur | 5 |
| Étudiant / débutant | 2 |

### Critère 5 — Accessibilité (poids : 10%)

| Signal | Score |
|---|---|
| Compte public + DMs ouverts + actif < 7 jours | 10 |
| Actif + répond aux replies | 8 |
| Actif mais DMs probablement fermés | 5 |
| Inactif > 30 jours | 1 |

---

## Seuils de décision

| Score final | Action | Label |
|---|---|---|
| >= 9.0 | Contact immédiat — priorité absolue | 🔴 HOT |
| 7.0 - 8.9 | Soumettre à validation manuelle | 🟡 REVIEW |
| 5.0 - 6.9 | Séquence nurture longue | 🟢 NURTURE |
| < 5.0 | Ignorer — ne pas contacter | ⚫ DISCARD |

---

## Règles absolues

1. **Jamais HOT sans intent explicite** — un profil ICP parfait sans signal d'achat = max 6.5
2. **Jamais > 5.0 si anti-ICP** — même si le tweet semble pertinent
3. **Builder qui montre sa stack = INTEL, score 0 pour lead** — logger dans section Intel séparée
4. **Tweet > 30 jours = max 4.0** — le signal est périmé
5. **Promo de produit concurrent = score 0** — c'est un concurrent, pas un lead

---

## Format de sortie attendu

Pour chaque lead qualifié (>= 7.0), l'agent produit :

```
Handle : @[handle]
Score : [X.X]/10
Label : [HOT/REVIEW/NURTURE]
Critères : Intent [X] · ICP [X] · Urgence [X] · Budget [X] · Accès [X]
Signal détecté : [Citation exacte du tweet]
Lien : [URL tweet]
Draft reply proposé : [Texte]
```

---

## Intel Competitive (section séparée)

Les builders qui décrivent leurs stacks, les annonces produit concurrentes : ne pas scorer comme leads. Logger dans un rapport Intel séparé avec format :

```
Compte : @[handle]
Outil/stack mentionné : [Nom]
Info utile : [Ce qui est exploitable — pricing, feature, gap]
Lien : [URL]
```
