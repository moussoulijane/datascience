#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Streamlit de Suivi Financier Personnel
Auteur: Assistant IA
Date: 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="💰 Suivi Financier Personnel",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
FICHIER_DONNEES = "donnees_financieres.json"
SALAIRE_NET = 14000
DEPENSES_FIXES_DEFAULT = {
    "Loyer": 2250,
    "Électricité": 200,
    "Eau": 250,
    "Internet": 45,
    "Téléphone": 30,
    "Autre": 20
}
EPARGNE_PERSONNELLE_DEFAULT = 2000
EPARGNE_FAMILLE_DEFAULT = 2000
INVESTISSEMENT_MIN_DEFAULT = 1000

# Couleurs
COULEUR_BLEU = "#1a365d"
COULEUR_VERT = "#38a169"
COULEUR_ROUGE = "#e53e3e"
COULEUR_ORANGE = "#dd6b20"
COULEUR_BLEU_CLAIR = "#4299e1"

# ==================== GESTION DES DONNÉES ====================

def charger_donnees():
    """Charge les données depuis le fichier JSON"""
    if os.path.exists(FICHIER_DONNEES):
        with open(FICHIER_DONNEES, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Données par défaut
        return {
            "revenus": [
                {"mois": "Janvier 2025", "salaire": 14000, "primes": 0, "autres": 0},
                {"mois": "Février 2025", "salaire": 14000, "primes": 0, "autres": 0},
                {"mois": "Mars 2025", "salaire": 14000, "primes": 0, "autres": 0}
            ],
            "depenses_fixes": DEPENSES_FIXES_DEFAULT,
            "depenses_variables": [],
            "epargne_personnelle": [
                {"mois": "Janvier 2025", "versement": 2000, "retrait": 0},
                {"mois": "Février 2025", "versement": 2000, "retrait": 0},
                {"mois": "Mars 2025", "versement": 2000, "retrait": 0}
            ],
            "epargne_famille": [
                {"mois": "Janvier 2025", "versement": 2000},
                {"mois": "Février 2025", "versement": 2000},
                {"mois": "Mars 2025", "versement": 2000}
            ],
            "investissements": {
                "versements": [
                    {"mois": "Janvier 2025", "prevu": 1000, "effectue": 1000, "extra": 0},
                    {"mois": "Février 2025", "prevu": 1000, "effectue": 1000, "extra": 0},
                    {"mois": "Mars 2025", "prevu": 1000, "effectue": 1000, "extra": 0}
                ],
                "portefeuille": [
                    {"date": "15/01/2025", "ticker": "EXEMPLE ETF", "secteur": "Indices",
                     "quantite": 10, "prix_achat": 100, "prix_actuel": 105},
                    {"date": "20/01/2025", "ticker": "EXEMPLE ACTION", "secteur": "Tech",
                     "quantite": 5, "prix_achat": 200, "prix_actuel": 210}
                ]
            },
            "objectifs": {
                "fonds_urgence": 84000,  # 6 mois de salaire
                "taux_epargne_cible": 0.285
            }
        }

def sauvegarder_donnees(donnees):
    """Sauvegarde les données dans le fichier JSON"""
    with open(FICHIER_DONNEES, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

# ==================== FONCTIONS DE CALCUL ====================

def calculer_total_revenus(donnees):
    """Calcule le total des revenus"""
    total = 0
    for revenu in donnees["revenus"]:
        total += revenu["salaire"] + revenu["primes"] + revenu["autres"]
    return total

def calculer_total_depenses_fixes(depenses):
    """Calcule le total des dépenses fixes"""
    return sum(depenses.values())

def calculer_epargne_totale(donnees):
    """Calcule l'épargne totale cumulée"""
    epargne_perso = sum([e["versement"] - e["retrait"] for e in donnees["epargne_personnelle"]])
    epargne_famille = sum([e["versement"] for e in donnees["epargne_famille"]])
    return epargne_perso, epargne_famille

def calculer_valeur_portefeuille(portefeuille):
    """Calcule la valeur du portefeuille"""
    valeur_achat = sum([p["quantite"] * p["prix_achat"] for p in portefeuille])
    valeur_actuelle = sum([p["quantite"] * p["prix_actuel"] for p in portefeuille])
    return valeur_achat, valeur_actuelle

def calculer_patrimoine_total(donnees):
    """Calcule le patrimoine total"""
    epargne_perso, epargne_famille = calculer_epargne_totale(donnees)
    _, valeur_portefeuille = calculer_valeur_portefeuille(donnees["investissements"]["portefeuille"])
    return epargne_perso + epargne_famille + valeur_portefeuille

# ==================== PAGE DASHBOARD ====================

def afficher_dashboard(donnees):
    """Affiche le tableau de bord"""
    st.title("📊 Tableau de Bord Financier")
    st.markdown(f"*Mise à jour : {datetime.now().strftime('%d/%m/%Y à %H:%M')}*")

    # KPIs en haut
    col1, col2, col3, col4 = st.columns(4)

    total_depenses_fixes = calculer_total_depenses_fixes(donnees["depenses_fixes"])
    epargne_totale_mois = EPARGNE_PERSONNELLE_DEFAULT + EPARGNE_FAMILLE_DEFAULT

    with col1:
        st.metric("💰 Salaire Mensuel", f"{SALAIRE_NET:,} MAD")

    with col2:
        st.metric("📉 Dépenses Fixes", f"{total_depenses_fixes:,} MAD",
                 delta=f"-{(total_depenses_fixes/SALAIRE_NET)*100:.1f}%")

    with col3:
        st.metric("💎 Épargne Totale/Mois", f"{epargne_totale_mois:,} MAD",
                 delta=f"{(epargne_totale_mois/SALAIRE_NET)*100:.1f}%")

    with col4:
        patrimoine = calculer_patrimoine_total(donnees)
        st.metric("🏆 Patrimoine Total", f"{patrimoine:,} MAD")

    st.divider()

    # Graphiques
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Répartition du Salaire")

        # Données pour le graphique
        reste_a_vivre = SALAIRE_NET - total_depenses_fixes - epargne_totale_mois - INVESTISSEMENT_MIN_DEFAULT

        labels = ['Dépenses Fixes', 'Épargne Personnelle', 'Épargne Famille',
                 'Investissements', 'Reste à Vivre']
        values = [total_depenses_fixes, EPARGNE_PERSONNELLE_DEFAULT,
                 EPARGNE_FAMILLE_DEFAULT, INVESTISSEMENT_MIN_DEFAULT, reste_a_vivre]
        colors = [COULEUR_ROUGE, COULEUR_VERT, COULEUR_BLEU_CLAIR,
                 COULEUR_ORANGE, COULEUR_BLEU]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='auto'
        )])

        fig.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=30, b=30, l=30, r=30)
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📈 Évolution du Patrimoine")

        # Calcul de l'évolution
        mois = [r["mois"] for r in donnees["revenus"]]
        patrimoine_evolution = []
        cumul = 0

        for i in range(len(donnees["revenus"])):
            if i < len(donnees["epargne_personnelle"]):
                cumul += donnees["epargne_personnelle"][i]["versement"] - donnees["epargne_personnelle"][i]["retrait"]
            if i < len(donnees["epargne_famille"]):
                cumul += donnees["epargne_famille"][i]["versement"]
            patrimoine_evolution.append(cumul)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=mois,
            y=patrimoine_evolution,
            mode='lines+markers',
            name='Patrimoine',
            line=dict(color=COULEUR_VERT, width=3),
            marker=dict(size=8)
        ))

        fig.update_layout(
            xaxis_title="Mois",
            yaxis_title="Patrimoine (MAD)",
            height=400,
            hovermode='x unified',
            margin=dict(t=30, b=30, l=30, r=30)
        )

        st.plotly_chart(fig, use_container_width=True)

    # Indicateurs clés
    st.divider()
    st.subheader("🎯 Indicateurs Clés")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        taux_epargne = (epargne_totale_mois / SALAIRE_NET) * 100
        st.metric("Taux d'Épargne", f"{taux_epargne:.1f}%",
                 delta="✓ Objectif atteint!" if taux_epargne >= 28.5 else "⚠️ Sous l'objectif")

    with col2:
        epargne_perso, _ = calculer_epargne_totale(donnees)
        mois_urgence = epargne_perso / SALAIRE_NET
        st.metric("Mois d'Urgence", f"{mois_urgence:.1f} mois",
                 delta="✓ Sécurisé" if mois_urgence >= 3 else "⚠️ Insuffisant")

    with col3:
        valeur_achat, valeur_actuelle = calculer_valeur_portefeuille(donnees["investissements"]["portefeuille"])
        if valeur_achat > 0:
            perf_bourse = ((valeur_actuelle - valeur_achat) / valeur_achat) * 100
            st.metric("Performance Bourse", f"{perf_bourse:+.2f}%",
                     delta=f"{valeur_actuelle - valeur_achat:+,.0f} MAD")
        else:
            st.metric("Performance Bourse", "N/A")

    with col4:
        objectif_fin_annee = patrimoine + (9 * epargne_totale_mois)
        st.metric("Projection Fin 2025", f"{objectif_fin_annee:,} MAD")

# ==================== PAGE REVENUS ====================

def afficher_revenus(donnees):
    """Affiche la page des revenus"""
    st.title("💰 Suivi des Revenus")

    # Tableau des revenus
    st.subheader("Revenus Mensuels")

    df_revenus = pd.DataFrame(donnees["revenus"])
    df_revenus["Total"] = df_revenus["salaire"] + df_revenus["primes"] + df_revenus["autres"]

    # Affichage formaté
    st.dataframe(
        df_revenus.style.format({
            "salaire": "{:,.0f} MAD",
            "primes": "{:,.0f} MAD",
            "autres": "{:,.0f} MAD",
            "Total": "{:,.0f} MAD"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Statistiques
    col1, col2, col3 = st.columns(3)

    with col1:
        total_annuel = df_revenus["Total"].sum()
        st.metric("Total Annuel", f"{total_annuel:,} MAD")

    with col2:
        moyenne = df_revenus["Total"].mean()
        st.metric("Moyenne Mensuelle", f"{moyenne:,.0f} MAD")

    with col3:
        total_primes = df_revenus["primes"].sum()
        st.metric("Total Primes", f"{total_primes:,} MAD")

    # Ajouter un nouveau revenu
    st.divider()
    st.subheader("➕ Ajouter un Revenu")

    with st.form("form_revenu"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            nouveau_mois = st.text_input("Mois", placeholder="Ex: Avril 2025")
        with col2:
            nouveau_salaire = st.number_input("Salaire Net", value=14000, step=100)
        with col3:
            nouvelles_primes = st.number_input("Primes/Bonus", value=0, step=100)
        with col4:
            autres_revenus = st.number_input("Autres Revenus", value=0, step=100)

        submitted = st.form_submit_button("Ajouter")

        if submitted and nouveau_mois:
            donnees["revenus"].append({
                "mois": nouveau_mois,
                "salaire": nouveau_salaire,
                "primes": nouvelles_primes,
                "autres": autres_revenus
            })
            sauvegarder_donnees(donnees)
            st.success(f"✅ Revenu ajouté pour {nouveau_mois}")
            st.rerun()

# ==================== PAGE DÉPENSES FIXES ====================

def afficher_depenses_fixes(donnees):
    """Affiche la page des dépenses fixes"""
    st.title("🏠 Dépenses Fixes Mensuelles")

    # Tableau des dépenses
    st.subheader("Dépenses Fixes")

    df_depenses = pd.DataFrame([
        {"Catégorie": k, "Montant": v}
        for k, v in donnees["depenses_fixes"].items()
    ])

    total_depenses = df_depenses["Montant"].sum()

    # Affichage
    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(
            df_depenses.style.format({"Montant": "{:,.0f} MAD"}),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.metric("Total Mensuel", f"{total_depenses:,} MAD")
        st.metric("% du Salaire", f"{(total_depenses/SALAIRE_NET)*100:.1f}%")
        st.metric("Budget Restant", f"{SALAIRE_NET - total_depenses:,} MAD")

    # Graphique
    st.divider()
    st.subheader("📊 Répartition des Dépenses Fixes")

    fig = px.bar(
        df_depenses,
        x="Catégorie",
        y="Montant",
        color="Montant",
        color_continuous_scale="Reds",
        text="Montant"
    )

    fig.update_traces(texttemplate='%{text:,.0f} MAD', textposition='outside')
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Montant (MAD)",
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Modifier les dépenses
    st.divider()
    st.subheader("✏️ Modifier les Dépenses Fixes")

    with st.form("form_depenses_fixes"):
        cols = st.columns(3)

        nouvelles_depenses = {}
        for i, (categorie, montant) in enumerate(donnees["depenses_fixes"].items()):
            with cols[i % 3]:
                nouvelles_depenses[categorie] = st.number_input(
                    categorie,
                    value=montant,
                    step=10,
                    key=f"dep_{categorie}"
                )

        submitted = st.form_submit_button("Mettre à jour")

        if submitted:
            donnees["depenses_fixes"] = nouvelles_depenses
            sauvegarder_donnees(donnees)
            st.success("✅ Dépenses fixes mises à jour")
            st.rerun()

# ==================== PAGE ÉPARGNE ====================

def afficher_epargne(donnees):
    """Affiche la page de l'épargne"""
    st.title("💎 Suivi de l'Épargne")

    # Statistiques générales
    epargne_perso, epargne_famille = calculer_epargne_totale(donnees)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Épargne Personnelle", f"{epargne_perso:,} MAD")

    with col2:
        st.metric("Épargne Famille", f"{epargne_famille:,} MAD")

    with col3:
        total_epargne = epargne_perso + epargne_famille
        st.metric("Total Épargné", f"{total_epargne:,} MAD")

    with col4:
        taux_epargne = ((EPARGNE_PERSONNELLE_DEFAULT + EPARGNE_FAMILLE_DEFAULT) / SALAIRE_NET) * 100
        st.metric("Taux d'Épargne", f"{taux_epargne:.1f}%")

    st.divider()

    # Deux colonnes pour les deux types d'épargne
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Épargne Personnelle")

        df_perso = pd.DataFrame(donnees["epargne_personnelle"])
        df_perso["Net"] = df_perso["versement"] - df_perso["retrait"]
        df_perso["Solde Cumulé"] = df_perso["Net"].cumsum()

        st.dataframe(
            df_perso.style.format({
                "versement": "{:,.0f} MAD",
                "retrait": "{:,.0f} MAD",
                "Net": "{:,.0f} MAD",
                "Solde Cumulé": "{:,.0f} MAD"
            }),
            use_container_width=True,
            hide_index=True
        )

        # Progression objectif
        objectif = donnees["objectifs"]["fonds_urgence"]
        progression = (epargne_perso / objectif) * 100

        st.progress(min(progression / 100, 1.0))
        st.caption(f"Objectif fonds d'urgence: {objectif:,} MAD ({progression:.1f}% atteint)")

    with col2:
        st.subheader("👨‍👩‍👧‍👦 Épargne Famille")

        df_famille = pd.DataFrame(donnees["epargne_famille"])
        df_famille["Total Versé"] = df_famille["versement"].cumsum()

        st.dataframe(
            df_famille.style.format({
                "versement": "{:,.0f} MAD",
                "Total Versé": "{:,.0f} MAD"
            }),
            use_container_width=True,
            hide_index=True
        )

    # Graphique évolution
    st.divider()
    st.subheader("📈 Évolution de l'Épargne")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_perso["mois"],
        y=df_perso["Solde Cumulé"],
        name="Épargne Personnelle",
        mode='lines+markers',
        line=dict(color=COULEUR_VERT, width=3)
    ))

    fig.add_trace(go.Scatter(
        x=df_famille["mois"],
        y=df_famille["Total Versé"],
        name="Épargne Famille",
        mode='lines+markers',
        line=dict(color=COULEUR_BLEU_CLAIR, width=3)
    ))

    fig.update_layout(
        xaxis_title="Mois",
        yaxis_title="Montant (MAD)",
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE INVESTISSEMENTS ====================

def afficher_investissements(donnees):
    """Affiche la page des investissements"""
    st.title("📈 Investissements Bourse")

    # Statistiques du portefeuille
    valeur_achat, valeur_actuelle = calculer_valeur_portefeuille(donnees["investissements"]["portefeuille"])
    gain_perte = valeur_actuelle - valeur_achat
    performance = (gain_perte / valeur_achat * 100) if valeur_achat > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Valeur Investie", f"{valeur_achat:,} MAD")

    with col2:
        st.metric("Valeur Actuelle", f"{valeur_actuelle:,} MAD")

    with col3:
        st.metric("Gain/Perte", f"{gain_perte:+,.0f} MAD",
                 delta=f"{performance:+.2f}%")

    with col4:
        total_verse = sum([v["effectue"] + v["extra"] for v in donnees["investissements"]["versements"]])
        st.metric("Total Versé", f"{total_verse:,} MAD")

    st.divider()

    # Portefeuille
    st.subheader("📊 Portefeuille d'Actions/ETF")

    if donnees["investissements"]["portefeuille"]:
        df_port = pd.DataFrame(donnees["investissements"]["portefeuille"])
        df_port["Valeur Achat"] = df_port["quantite"] * df_port["prix_achat"]
        df_port["Valeur Actuelle"] = df_port["quantite"] * df_port["prix_actuel"]
        df_port["+/- Value"] = df_port["Valeur Actuelle"] - df_port["Valeur Achat"]
        df_port["% Gain/Perte"] = (df_port["+/- Value"] / df_port["Valeur Achat"]) * 100

        st.dataframe(
            df_port.style.format({
                "quantite": "{:.0f}",
                "prix_achat": "{:,.0f} MAD",
                "prix_actuel": "{:,.0f} MAD",
                "Valeur Achat": "{:,.0f} MAD",
                "Valeur Actuelle": "{:,.0f} MAD",
                "+/- Value": "{:+,.0f} MAD",
                "% Gain/Perte": "{:+.2f}%"
            }).applymap(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                subset=["+/- Value", "% Gain/Perte"]
            ),
            use_container_width=True,
            hide_index=True
        )

        # Graphiques
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Répartition par Secteur")

            df_secteur = df_port.groupby("secteur")["Valeur Actuelle"].sum().reset_index()

            fig = px.pie(
                df_secteur,
                values="Valeur Actuelle",
                names="secteur",
                color_discrete_sequence=px.colors.qualitative.Set3
            )

            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Performance par Position")

            fig = px.bar(
                df_port,
                x="ticker",
                y="% Gain/Perte",
                color="% Gain/Perte",
                color_continuous_scale=["red", "yellow", "green"],
                text="% Gain/Perte"
            )

            fig.update_traces(texttemplate='%{text:+.2f}%', textposition='outside')
            fig.update_layout(height=300, xaxis_title="", yaxis_title="Performance (%)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune position dans le portefeuille. Ajoutez votre première position ci-dessous.")

    # Ajouter une position
    st.divider()
    st.subheader("➕ Ajouter une Position")

    with st.form("form_position"):
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            date = st.text_input("Date", placeholder="01/04/2025")
        with col2:
            ticker = st.text_input("Ticker/Nom")
        with col3:
            secteur = st.text_input("Secteur")
        with col4:
            quantite = st.number_input("Quantité", min_value=1, value=1)
        with col5:
            prix_achat = st.number_input("Prix Achat", min_value=0.0, value=100.0, step=10.0)
        with col6:
            prix_actuel = st.number_input("Prix Actuel", min_value=0.0, value=100.0, step=10.0)

        submitted = st.form_submit_button("Ajouter la Position")

        if submitted and ticker:
            donnees["investissements"]["portefeuille"].append({
                "date": date,
                "ticker": ticker,
                "secteur": secteur,
                "quantite": quantite,
                "prix_achat": prix_achat,
                "prix_actuel": prix_actuel
            })
            sauvegarder_donnees(donnees)
            st.success(f"✅ Position {ticker} ajoutée")
            st.rerun()

# ==================== PAGE PATRIMOINE ====================

def afficher_patrimoine(donnees):
    """Affiche la page du patrimoine global"""
    st.title("💎 Patrimoine Global")

    # Calculs
    epargne_perso, epargne_famille = calculer_epargne_totale(donnees)
    _, valeur_portefeuille = calculer_valeur_portefeuille(donnees["investissements"]["portefeuille"])
    patrimoine_total = epargne_perso + epargne_famille + valeur_portefeuille

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Épargne Personnelle", f"{epargne_perso:,} MAD")

    with col2:
        st.metric("Épargne Famille", f"{epargne_famille:,} MAD")

    with col3:
        st.metric("Portefeuille Bourse", f"{valeur_portefeuille:,} MAD")

    with col4:
        st.metric("TOTAL PATRIMOINE", f"{patrimoine_total:,} MAD",
                 delta="💎")

    st.divider()

    # Tableau récapitulatif
    st.subheader("📊 Évolution Mensuelle du Patrimoine")

    # Construire le DataFrame
    mois = [r["mois"] for r in donnees["revenus"]]
    patrimoine_data = []

    cumul_perso = 0
    cumul_famille = 0

    for i in range(len(mois)):
        if i < len(donnees["epargne_personnelle"]):
            cumul_perso += donnees["epargne_personnelle"][i]["versement"] - donnees["epargne_personnelle"][i]["retrait"]

        if i < len(donnees["epargne_famille"]):
            cumul_famille += donnees["epargne_famille"][i]["versement"]

        patrimoine_data.append({
            "Mois": mois[i],
            "Épargne Perso": cumul_perso,
            "Épargne Famille": cumul_famille,
            "Portefeuille": valeur_portefeuille,
            "TOTAL": cumul_perso + cumul_famille + valeur_portefeuille
        })

    df_patrimoine = pd.DataFrame(patrimoine_data)
    df_patrimoine["Variation"] = df_patrimoine["TOTAL"].diff().fillna(0)

    st.dataframe(
        df_patrimoine.style.format({
            "Épargne Perso": "{:,.0f} MAD",
            "Épargne Famille": "{:,.0f} MAD",
            "Portefeuille": "{:,.0f} MAD",
            "TOTAL": "{:,.0f} MAD",
            "Variation": "{:+,.0f} MAD"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Graphique d'évolution
    st.divider()
    st.subheader("📈 Évolution du Patrimoine Total")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_patrimoine["Mois"],
        y=df_patrimoine["Épargne Perso"],
        name="Épargne Personnelle",
        mode='lines',
        stackgroup='one',
        fillcolor=COULEUR_VERT
    ))

    fig.add_trace(go.Scatter(
        x=df_patrimoine["Mois"],
        y=df_patrimoine["Épargne Famille"],
        name="Épargne Famille",
        mode='lines',
        stackgroup='one',
        fillcolor=COULEUR_BLEU_CLAIR
    ))

    fig.add_trace(go.Scatter(
        x=df_patrimoine["Mois"],
        y=df_patrimoine["Portefeuille"],
        name="Portefeuille Bourse",
        mode='lines',
        stackgroup='one',
        fillcolor=COULEUR_ORANGE
    ))

    fig.update_layout(
        xaxis_title="Mois",
        yaxis_title="Patrimoine (MAD)",
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Statistiques
    st.divider()
    st.subheader("📊 Statistiques")

    col1, col2, col3 = st.columns(3)

    with col1:
        croissance_moy = df_patrimoine["Variation"].mean()
        st.metric("Croissance Moyenne/Mois", f"{croissance_moy:+,.0f} MAD")

    with col2:
        mois_urgence = epargne_perso / SALAIRE_NET
        st.metric("Mois d'Épargne d'Urgence", f"{mois_urgence:.1f} mois")

    with col3:
        projection_fin_annee = patrimoine_total + (9 * 4000)  # 9 mois restants
        st.metric("Projection Fin 2025", f"{projection_fin_annee:,} MAD")

# ==================== NAVIGATION ====================

def main():
    """Fonction principale"""

    # Charger les données
    donnees = charger_donnees()

    # CSS personnalisé
    st.markdown("""
        <style>
        .main > div {
            padding-top: 2rem;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar pour la navigation
    st.sidebar.title("💰 Navigation")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Choisissez une page:",
        ["🏠 Dashboard", "💰 Revenus", "🏠 Dépenses Fixes",
         "💎 Épargne", "📈 Investissements", "💎 Patrimoine Global"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Résumé Rapide")
    patrimoine = calculer_patrimoine_total(donnees)
    st.sidebar.metric("Patrimoine Total", f"{patrimoine:,} MAD")

    taux_epargne = ((EPARGNE_PERSONNELLE_DEFAULT + EPARGNE_FAMILLE_DEFAULT) / SALAIRE_NET) * 100
    st.sidebar.metric("Taux d'Épargne", f"{taux_epargne:.1f}%")

    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Astuce**: Les données sont sauvegardées automatiquement.")

    # Affichage de la page sélectionnée
    if page == "🏠 Dashboard":
        afficher_dashboard(donnees)
    elif page == "💰 Revenus":
        afficher_revenus(donnees)
    elif page == "🏠 Dépenses Fixes":
        afficher_depenses_fixes(donnees)
    elif page == "💎 Épargne":
        afficher_epargne(donnees)
    elif page == "📈 Investissements":
        afficher_investissements(donnees)
    elif page == "💎 Patrimoine Global":
        afficher_patrimoine(donnees)

if __name__ == "__main__":
    main()
