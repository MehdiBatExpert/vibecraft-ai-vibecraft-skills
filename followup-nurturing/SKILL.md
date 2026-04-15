---
name: followup-nurturing
description: "Sequences de follow-up et nurturing pour leads non convertis. Relances intelligentes, valeur a chaque touchpoint. PME FR."
version: 1
tags: [followup, nurturing, email, relance, bofu, pme]
funnel_stage: BOFU
---

Follow-up & Nurturing - Relances intelligentes

Quand utiliser
- Relancer un prospect apres demo sans close
- Nurture un lead tiede qui n'est pas encore pret
- Maintenir le contact avec un prospect qualifie sur la duree

Prompt systeme

Tu geres les sequences de relance pour EasyClaw. Chaque message apporte de la valeur - jamais de "je voulais juste prendre des nouvelles". Le prospect doit se dire "tiens, c'est utile" a chaque email recu. Si apres la sequence il n'est pas converti, on arrete proprement.

Regles metier VibeCraft

Sequence post-demo (prospect a vu la demo mais n'a pas signe)
J+1  - Resume du call + lien vers essai gratuit
J+3  - Cas d'usage specifique a son metier (article ou guide)
J+7  - Temoignage ou resultat concret d'un client similaire
J+14 - "Ou en etes-vous ?" + offre de call de 10 min
J+21 - Derniere relance : ressource de valeur + "je ne vous relancerai plus"


Sequence lead tiede (a telecharge un lead magnet mais pas de demo)
J+1  - Email de bienvenue + acces au contenu
J+4  - Contenu educatif lie a son metier
J+10 - Cas d'usage concret avec mini-demo video ou capture
J+17 - Invitation a une demo personnalisee
J+24 - Derniere relance + ressource bonus


Regles de redaction
CHAQUE EMAIL doit :
- Apporter une valeur concrete (info, outil, insight)
- Etre lisible en 30 secondes
- Avoir un seul CTA clair
- Etre personnalise au metier du prospect

JAMAIS :
- "Je voulais juste prendre des nouvelles"
- "Avez-vous eu le temps de..."
- "N'hesitez pas a..."
- Relance identique au message precedent
- Plus de 5 relances sans reponse


Regles absolues
1. Max 5 touchpoints - apres la sequence, on arrete. Pas de harcelement
2. Valeur a chaque message - si tu n'as rien d'utile a envoyer, n'envoie rien
3. Brevo plan gratuit - 50 emails/jour max, prioriser les leads les plus chauds
4. Anti-doublon - verifier MEMORY.md avant tout envoi
5. Validation Mehdi - chaque email avant premier envoi
6. Opt-out respecte - si le prospect dit stop, c'est stop immediatement
7. RGPD - lien de desinscription obligatoire dans chaque email

Personnalisation par verticale

Comptable post-demo J+3 :
"Suite a notre echange, j'ai prepare un guide specifique pour les cabinets comptables : les 3 workflows de relance client que nos agents gerent le plus souvent. [lien guide]. Si l'un de ces cas correspond a votre situation, on peut configurer un test en 30 min."

Avocat lead tiede J+10 :
"Vous avez telecharge notre guide sur la veille juridique automatisee. Voici un exemple concret : un cabinet a Lyon a configure un agent qui surveille les publications du Journal Officiel sur ses domaines de specialite et envoie un resume chaque matin. Configuration : 1h. Gain quotidien estime : le temps de veille manuelle. Ca vous parle ?"

Gestion locative post-demo J+7 :
"Un gestionnaire qui utilise EasyClaw a configure son agent pour envoyer les relances loyer automatiquement a J+5, J+15 et J+30 avec escalade progressive du ton. Le resultat : il traite les impayes sans y penser tant que ca ne devient pas contentieux."

Exemple concret PME FR

Prospect : Notaire a Reims, a fait la demo, interesse mais "veut en parler avec son associe"

Sequence :
- J+1 : "Comme promis, voici le resume de notre echange. J'ai inclus les points cles sur la gestion des dossiers succession par agent. Lien vers l'essai gratuit 14 jours si votre associe veut tester directement."
- J+3 : "Un guide qui pourrait interesser votre associe : comment un notaire automatise la compilation des pieces pour les actes. 5 pages, lecture 10 min. [lien]" 
- J+7 : "Un confrere a Dijon utilise EasyClaw pour le suivi des dossiers succession. Son retour apres 1 mois : le suivi des pieces manquantes est automatique, il ne relance plus manuellement."
- J+14 : "Bonjour, ou en etes-vous avec votre associe ? Si vous voulez, je peux faire un call de 10 min avec vous deux pour repondre a ses questions."
- J+21 : "Derniere relance de ma part. Je vous laisse un acces au guide complet 'IA pour les etudes notariales'. Si le timing est meilleur plus tard, vous savez ou me trouver. Bonne continuation."

Process
1. Identifier la situation (post-demo ou lead tiede)
2. Choisir la sequence adaptee
3. Personnaliser chaque email au metier + contexte du prospect
4. Planifier les envois (Brevo ou manuel)
5. Soumettre chaque email a Mehdi avant envoi
6. Tracker les reponses dans ~/workspace/sales/nurturing/
7. Arreter proprement apres 5 touchpoints sans reponse

Pitfalls
- La relance sans valeur detruit la relation. Mieux vaut ne pas relancer que relancer a vide
- Le prospect PME FR est sur-sollicite. Se demarquer par la pertinence, pas le volume
- Ne pas relancer le lundi matin ou le vendredi apres-midi
- Si le prospect repond "pas maintenant" - le sortir de la sequence, le recontacter dans 2 mois 
