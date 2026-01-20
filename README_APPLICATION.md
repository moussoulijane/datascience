# 💰 Application de Suivi Financier Personnel

Application web interactive créée avec Streamlit pour suivre vos finances personnelles.

## 📋 Description

Cette application remplace le fichier Excel et offre une interface moderne et interactive pour gérer:
- 💰 Revenus mensuels
- 🏠 Dépenses fixes et variables
- 💎 Épargne personnelle et familiale
- 📈 Investissements en bourse
- 💎 Patrimoine global

## 🚀 Installation

Les dépendances sont déjà installées, mais si nécessaire:

```bash
pip install streamlit plotly pandas
```

## 💻 Utilisation

### Lancer l'application

```bash
streamlit run app_financiere.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse: `http://localhost:8501`

### Navigation

L'application contient 6 pages principales accessibles via la barre latérale:

#### 1. 🏠 Dashboard
- Vue d'ensemble de votre situation financière
- Graphique de répartition du salaire
- Évolution du patrimoine
- Indicateurs clés (taux d'épargne, mois d'urgence, performance bourse)

#### 2. 💰 Revenus
- Tableau des revenus mensuels
- Statistiques (total annuel, moyenne)
- Formulaire pour ajouter de nouveaux revenus

#### 3. 🏠 Dépenses Fixes
- Liste des dépenses fixes mensuelles
- Graphique de répartition
- Modification des montants

#### 4. 💎 Épargne
- Suivi de l'épargne personnelle et familiale
- Progression vers l'objectif du fonds d'urgence
- Graphique d'évolution

#### 5. 📈 Investissements
- Portefeuille d'actions et ETF
- Performance du portefeuille
- Répartition par secteur
- Ajout de nouvelles positions

#### 6. 💎 Patrimoine Global
- Vue consolidée du patrimoine total
- Évolution mensuelle
- Statistiques et projections

## 💾 Sauvegarde des Données

Les données sont automatiquement sauvegardées dans le fichier `donnees_financieres.json` à chaque modification.

**Important**: Ne supprimez pas ce fichier, il contient toutes vos données!

## 🎨 Fonctionnalités

### Graphiques Interactifs
- Camemberts pour la répartition
- Graphiques en ligne pour les évolutions
- Barres pour les comparaisons
- Tous les graphiques sont interactifs (zoom, survol, etc.)

### Mise à Jour en Temps Réel
- Les données sont sauvegardées automatiquement
- Les graphiques se mettent à jour instantanément
- Calculs automatiques du patrimoine et des performances

### Indicateurs Calculés Automatiquement
- Taux d'épargne
- Mois d'épargne d'urgence disponibles
- Performance du portefeuille boursier
- Projection fin d'année

## 📊 Données Pré-remplies

L'application est initialisée avec vos données:
- Salaire: 14 000 MAD
- Dépenses fixes: 2 795 MAD
- Épargne personnelle: 2 000 MAD/mois
- Épargne famille: 2 000 MAD/mois
- Investissements: 1 000 MAD/mois minimum
- Données pour Janvier-Mars 2025

## 🔧 Personnalisation

Vous pouvez personnaliser:
- Les montants de toutes les dépenses
- Ajouter/modifier les revenus
- Ajouter des positions dans le portefeuille
- Modifier l'objectif du fonds d'urgence

## 💡 Conseils d'Utilisation

1. **Mettez à jour régulièrement**: Ajoutez vos revenus et dépenses chaque mois
2. **Suivez votre portefeuille**: Mettez à jour les prix actuels de vos investissements
3. **Consultez le Dashboard**: Pour une vue d'ensemble rapide de votre situation
4. **Sauvegardez le fichier JSON**: Faites des copies de sauvegarde régulières

## 🆚 Avantages vs Excel

| Critère | Application Streamlit | Excel |
|---------|---------------------|-------|
| Interface | ✅ Moderne et intuitive | ⚠️ Classique |
| Graphiques | ✅ Interactifs | ⚠️ Statiques |
| Mise à jour | ✅ Temps réel | ⚠️ Manuel |
| Accessibilité | ✅ Navigateur web | ⚠️ Logiciel requis |
| Saisie | ✅ Formulaires guidés | ⚠️ Cellules |
| Calculs | ✅ Automatiques | ✅ Formules |

## 🐛 Résolution de Problèmes

### L'application ne se lance pas
```bash
# Vérifier que Streamlit est installé
pip install streamlit

# Relancer l'application
streamlit run app_financiere.py
```

### Les données ne se sauvegardent pas
- Vérifiez que vous avez les droits d'écriture dans le dossier
- Le fichier `donnees_financieres.json` doit être dans le même dossier

### Le navigateur ne s'ouvre pas automatiquement
- Ouvrez manuellement: `http://localhost:8501`

## 📱 Utilisation Mobile

L'application est responsive et fonctionne sur mobile/tablette via le navigateur.

## 🔒 Sécurité

- Les données sont stockées localement sur votre ordinateur
- Aucune connexion internet requise
- Vos données financières restent privées

## 🎯 Prochaines Étapes

Pour aller plus loin:
1. Ajoutez vos données réelles
2. Mettez à jour mensuellement
3. Analysez vos tendances
4. Ajustez votre budget selon vos objectifs

---

**Créé avec ❤️ pour votre succès financier**
