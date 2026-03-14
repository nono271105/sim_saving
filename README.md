# Comparateur de Placements · France 🇫🇷
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/status-Active-brightgreen.svg)](#)

Un outil pour comparer des placements financiers en France, avec la  fiscalité 2026 appliquée.

---

## Ce que ça fait

Entrez votre capital, vos versements mensuels, votre durée et votre situation fiscale. L'outil simule et compare jusqu'à 15 produits en même temps, et permet de savoir  combien vous aurez en poche après impôts.

Il y a aussi un module de recommandation qui analyse votre profil (âge, objectif, tolérance au risque, TMI...) et vous suggère une allocation personnalisée avec un score de compatibilité pour chaque produit.

---

## Installation

```bash
pip install streamlit plotly pandas numpy
streamlit run comparateur_placements.py
```
---

## Les produits couverts

| Catégorie | Produits |
|---|---|
| Livrets réglementés | Livret A, LDDS, LEP |
| Livrets bancaires | Livret bancaire |
| Épargne logement | PEL, CEL |
| Assurance Vie | Fonds euros, Unités de compte |
| Actions | PEA, PEA-PME, CTO |
| Immobilier | SCPI |
| Obligataire | OAT 10 ans |
| Alternatifs | Cryptomonnaies, FCPI/FIP |

---

## La fiscalité appliquée

Tout est calculé selon la réglementation française 2026 :

- **PFU 30 %** (12,8 % IR + 17,2 % PS) — cas général
- **Option barème progressif** — activée automatiquement si votre TMI est inférieur à 12,8 %
- **Livrets réglementés** — exonération totale, rien à calculer
- **PEA après 5 ans** — 0 % IR, seulement 17,2 % PS sur les plus-values
- **Assurance Vie après 8 ans** — abattement 4 600 € (9 200 € en couple) + taux réduit 7,5 %
- **SCPI** — revenus fonciers au barème IR + PS, avec CSG déductible
- **FCPI/FIP** — réduction IR à l'entrée déduite du calcul final

Les taux sont ceux en vigueur début 2026 

---

## Les onglets

**EVOLUTION** — courbes du capital dans le temps pour chaque produit

**COMPARAISON** — barres côte à côte : brut, net, taxes

**FISCALITE** — donut par produit + détail IR / PS avec explication de la règle appliquée

**RENDEMENTS** — taux brut / net / réel (après inflation) + bulle risque-rendement

**TABLEAU** — tout en une ligne par produit, exportable en CSV

**FICHES** — fiche détaillée de chaque produit sélectionné

**RECOMMANDATION** — questionnaire profil investisseur → scoring → allocation → analyse

---

## Le module recommandation

Il pose 12 questions sur votre situation et score chaque produit sur 6 critères :

- Compatible avec votre horizon d'investissement ?
- Adapté à votre tolérance au risque ?
- Suffisamment liquide pour vos besoins ?
- Fiscalement optimisé pour votre TMI ?
- Cohérent avec votre objectif (retraite, projet, patrimoine...) ?
- Accessible avec votre capital ?

Il ressort un podium, une allocation suggérée en pourcentages, et une analyse rédigée qui explique pourquoi tel produit est recommandé ou déconseillé dans votre cas précis.

---

## Personnalisation

Dans la barre latérale, vous pouvez modifier manuellement le taux de rendement de chaque produit pour tester vos propres hypothèses.

---

## Limites à garder en tête

- Les rendements des produits risqués (PEA, UC, crypto) sont des **hypothèses neutres de long terme**, pas des garanties
- La fiscalité est simulée à la sortie en une seule fois — certains produits (fonds euros notamment) ont des prélèvements sociaux annuels déjà intégrés dans le taux servi
- Cet outil est fait pour comparer et apprendre, pas pour remplacer un conseiller

> Pour toute décision importante, consultez un conseiller en gestion de patrimoine (CGP) agréé AMF.
