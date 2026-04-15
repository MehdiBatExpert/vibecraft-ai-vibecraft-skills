---
name: gtm-content-repurpose
description: "Prendre un post X existant et le developper en article long format journalistique. Amplifier les idees, pas les diluer."
version: 1
tags: [content, repurpose, gtm, article, x, twitter]
---

GTM Content Repurpose - Post X > Article

Quand utiliser
- Developper un post X de @MehdiBuilds en article long format
- Amplifier une idee qui a eu de la traction sociale
- Creer du contenu GTM (lead magnet, blog, newsletter) depuis du social

Regles absolues

Principe fondamental
AMPLIFIER, pas DILUER. L'article doit aller plus loin que le post, pas juste le paraphraser en 1000 mots.

Integrite
1. Memes regles que journalist-grade-content (zero chiffre invente, sources primaires)
2. Le post original est la SOURCE, pas le plan - l'article peut diverger
3. Si le post contient des claims, les sourcer dans l'article
4. Experience vecue = source valide, le signaler

Amplification
1. Contexte - pourquoi cette idee existe, quel probleme elle resout
2. Profondeur - details techniques que le post ne pouvait pas contenir
3. Exemples - cas concrets, workflow reel, captures d'ecran si possible
4. Contre-arguments - aborder les objections honnetement
5. Action - le lecteur repart avec quelque chose de concret

Process

1. Recuperer le tweet source - mcp_clix_get_tweet(id) + thread si applicable
2. Identifier la these - quelle est l'idee forte du post ?
3. Lister ce qui manque - quels details le format X n'a pas permis ?
4. Rechercher les sources - tweets lies, docs, articles cites
5. Structurer l'article - suivre le format journalist-grade-content
6. Rediger - en amplifiant chaque point du post original
7. Verifier - integrite des sources, ton coherent, 800-1200 mots
8. Decliner en social - utiliser social-content pour creer les posts de promo
9. Sauvegarder - article dans ~/workspace/content/articles/, posts dans ~/workspace/content/social/

Input attendu
- URL du tweet ou ID
- Contexte additionnel (optionnel) - ce que Mehdi veut amplifier
- Angle editorial (optionnel) - si different de l'angle original du tweet

Output
- Article complet format journalist-grade-content (800-1200 mots)
- 3-5 posts X de promotion (format social-content)
- Fichiers sauves dans ~/workspace/content/

Pitfalls
- Ne PAS juste paraphraser le tweet en plus long - c'est du padding, pas de l'amplification
- Verifier que le tweet existe encore et est public
- Si le tweet cite un article externe, lire l'article avant d'ecrire
- Ne pas inventer du contexte que Mehdi n'a pas donne
- Si le tweet a des reponses interessantes, les integrer comme data points
