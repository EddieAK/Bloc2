import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page
st.set_page_config(
    page_title="Dashboard NovaRetail",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("📊 Tableau de Bord Marketing - NovaRetail")
st.markdown("**Période : Octobre 2025**")

# Chargement des données
@st.cache_data
def load_data():
    return pd.read_csv('df_selected.csv')

df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔧 Filtres")
    
    # Filtre par canal
    canaux = st.multiselect(
        "Canal marketing",
        options=df['channel'].unique(),
        default=df['channel'].unique()
    )
    
    # Filtre par taille d'entreprise
    tailles = st.multiselect(
        "Taille d'entreprise",
        options=df['company_size'].unique(),
        default=df['company_size'].unique()
    )
    
    # Filtre par secteur
    secteurs = st.multiselect(
        "Secteur d'activité",
        options=df['sector'].unique(),
        default=df['sector'].unique()
    )
    
    # Filtre par statut
    statuts = st.multiselect(
        "Statut CRM",
        options=df['status'].unique(),
        default=df['status'].unique()
    )

# Application des filtres
df_filtre = df.copy()
if canaux:
    df_filtre = df_filtre[df_filtre['channel'].isin(canaux)]
if tailles:
    df_filtre = df_filtre[df_filtre['company_size'].isin(tailles)]
if secteurs:
    df_filtre = df_filtre[df_filtre['sector'].isin(secteurs)]
if statuts:
    df_filtre = df_filtre[df_filtre['status'].isin(statuts)]

# --- KPI PRINCIPAUX ---
st.markdown("## 📊 Indicateurs Clés de Performance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_leads = len(df_filtre)
    leads_mql = len(df_filtre[df_filtre['status'] == 'MQL'])
    leads_sql = len(df_filtre[df_filtre['status'] == 'SQL'])
    leads_client = len(df_filtre[df_filtre['status'] == 'Client'])
    
    st.metric(
        label="🎯 Leads Totaux",
        value=total_leads,
        delta=f"{leads_client} clients"
    )

with col2:
    taux_conversion = (leads_client / total_leads * 100) if total_leads > 0 else 0
    taux_progression = (leads_sql / total_leads * 100) if total_leads > 0 else 0
    
    st.metric(
        label="📈 Taux de Conversion",
        value=f"{taux_conversion:.1f}%",
        delta=f"{taux_progression:.1f}% en progression"
    )

with col3:
    # Calcul du CTR moyen pondéré
    ctr_total = (df_filtre['clicks'].sum() / df_filtre['impressions'].sum() * 100) \
        if df_filtre['impressions'].sum() > 0 else 0
    ctr_prev = 2.5  # Valeur de référence hypothétique
    
    st.metric(
        label="👆 CTR Moyen",
        value=f"{ctr_total:.2f}%",
        delta=f"{ctr_total - ctr_prev:.2f}% vs référence"
    )

with col4:
    # Coût par lead
    cout_total = df_filtre['cost'].sum() / 3  # Divisé par 3 car chaque ligne répète le coût du canal
    cout_par_lead = cout_total / total_leads if total_leads > 0 else 0
    cout_par_client = cout_total / leads_client if leads_client > 0 else 0
    
    st.metric(
        label="💰 Coût par Client",
        value=f"{cout_par_client:.2f}€",
        delta=f"{cout_par_lead:.2f}€ par lead"
    )

# --- PREMIÈRE LIGNE DE VISUALISATIONS ---
st.markdown("---")
st.markdown("## 📊 Performance par Canal")

col1, col2 = st.columns(2)

with col1:
    # Graphique 1: Performance des canaux (CTR et Conversion)
    canal_stats = df_filtre.groupby('channel').agg({
        'clicks': 'mean',
        'impressions': 'mean',
        'conversions': 'mean',
        'cost': 'mean',
        'lead_id': 'count'
    }).reset_index()
    
    canal_stats['CTR'] = canal_stats['clicks'] / canal_stats['impressions'] * 100
    canal_stats['Taux_Conversion'] = canal_stats['conversions'] / canal_stats['clicks'] * 100
    canal_stats['Cout_Par_Conversion'] = canal_stats['cost'] / canal_stats['conversions']
    
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig1.add_trace(
        go.Bar(
            x=canal_stats['channel'],
            y=canal_stats['CTR'],
            name="CTR (%)",
            marker_color='#636EFA'
        ),
        secondary_y=False
    )
    
    fig1.add_trace(
        go.Scatter(
            x=canal_stats['channel'],
            y=canal_stats['Taux_Conversion'],
            name="Conversion (%)",
            mode='lines+markers',
            line=dict(color='#EF553B', width=3),
            marker=dict(size=10)
        ),
        secondary_y=True
    )
    
    fig1.update_layout(
        title="CTR et Taux de Conversion par Canal",
        xaxis_title="Canal Marketing",
        hovermode="x unified"
    )
    
    fig1.update_yaxes(title_text="CTR (%)", secondary_y=False)
    fig1.update_yaxes(title_text="Conversion (%)", secondary_y=True)
    
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Graphique 2: Répartition des leads par canal et statut
    canal_status = pd.crosstab(
        df_filtre['channel'], 
        df_filtre['status'],
        normalize='index'
    ).round(3) * 100
    
    fig2 = px.bar(
        canal_status,
        barmode='stack',
        title="Répartition des Statuts par Canal (%)",
        color_discrete_map={
            'MQL': '#FFA15A',
            'SQL': '#00CC96',
            'Client': '#AB63FA'
        }
    )
    
    fig2.update_layout(
        xaxis_title="Canal Marketing",
        yaxis_title="Pourcentage",
        legend_title="Statut"
    )
    
    st.plotly_chart(fig2, use_container_width=True)

# --- DEUXIÈME LIGNE DE VISUALISATIONS ---
st.markdown("---")
st.markdown("## 🏢 Analyse par Taille d'Entreprise et Secteur")

col1, col2 = st.columns(2)

with col1:
    # Graphique 3: Taux de conversion par taille d'entreprise
    taille_stats = df_filtre.groupby('company_size').agg({
        'lead_id': 'count',
        'status': lambda x: (x == 'Client').sum()
    }).reset_index()
    
    taille_stats['Taux_Conversion'] = (taille_stats['status'] / taille_stats['lead_id'] * 100).round(1)
    
    # Ordonner par taille logique
    ordre_taille = ['1-10', '10-50', '50-100', '100-500']
    taille_stats['company_size'] = pd.Categorical(
        taille_stats['company_size'], 
        categories=ordre_taille, 
        ordered=True
    )
    taille_stats = taille_stats.sort_values('company_size')
    
    fig3 = px.bar(
        taille_stats,
        x='company_size',
        y='Taux_Conversion',
        title="Taux de Conversion par Taille d'Entreprise",
        text='Taux_Conversion',
        color='Taux_Conversion',
        color_continuous_scale='Viridis'
    )
    
    fig3.update_traces(
        texttemplate='%{text}%',
        textposition='outside'
    )
    
    fig3.update_layout(
        xaxis_title="Taille d'Entreprise (salariés)",
        yaxis_title="Taux de Conversion (%)",
        showlegend=False
    )
    
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    # Graphique 4: Performance par secteur
    secteur_stats = df_filtre.groupby('sector').agg({
        'lead_id': 'count',
        'status': lambda x: (x == 'Client').sum()
    }).reset_index()
    
    secteur_stats['Taux_Conversion'] = (secteur_stats['status'] / secteur_stats['lead_id'] * 100).round(1)
    secteur_stats = secteur_stats.sort_values('Taux_Conversion', ascending=False)
    
    fig4 = px.scatter(
        secteur_stats,
        x='lead_id',
        y='Taux_Conversion',
        size='status',
        color='sector',
        title="Performance par Secteur",
        text='sector',
        size_max=60
    )
    
    fig4.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=2, color='DarkSlateGrey'))
    )
    
    fig4.update_layout(
        xaxis_title="Nombre de Leads",
        yaxis_title="Taux de Conversion (%)",
        showlegend=False
    )
    
    st.plotly_chart(fig4, use_container_width=True)

# --- TROISIÈME LIGNE DE VISUALISATIONS ---
st.markdown("---")
st.markdown("## 🗺️ Analyse Géographique et Détails")

col1, col2 = st.columns([2, 1])

with col1:
    # Graphique 5: Répartition géographique
    region_stats = df_filtre['region'].value_counts().reset_index()
    region_stats.columns = ['Région', 'Nombre de Leads']
    
    # Top 5 régions + Autres
    top_5 = region_stats.head(5)
    autres = pd.DataFrame({
        'Région': ['Autres'],
        'Nombre de Leads': [region_stats['Nombre de Leads'].iloc[5:].sum()]
    })
    region_pie = pd.concat([top_5, autres])
    
    fig5 = px.pie(
        region_pie,
        values='Nombre de Leads',
        names='Région',
        title="Répartition des Leads par Région",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    
    fig5.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    # Tableau de synthèse
    st.markdown("### 📋 Synthèse des Canaux")
    
    synthèse_canaux = canal_stats[['channel', 'CTR', 'Taux_Conversion', 'Cout_Par_Conversion']].copy()
    synthèse_canaux['CTR'] = synthèse_canaux['CTR'].round(2)
    synthèse_canaux['Taux_Conversion'] = synthèse_canaux['Taux_Conversion'].round(1)
    synthèse_canaux['Cout_Par_Conversion'] = synthèse_canaux['Cout_Par_Conversion'].round(2)
    
    synthèse_canaux.columns = ['Canal', 'CTR (%)', 'Conversion (%)', 'Coût/Conv. (€)']
    
    # Mise en forme conditionnelle
    def colorize(val):
        if val > 2.5:
            return 'background-color: #90EE90'  # Vert clair
        elif val < 1.5:
            return 'background-color: #FFB6C1'  # Rouge clair
        else:
            return ''
    
    styled_table = synthèse_canaux.style.map(
        colorize, 
        subset=['CTR (%)', 'Conversion (%)']
    ).format({
        'CTR (%)': '{:.2f}%',
        'Conversion (%)': '{:.1f}%',
        'Coût/Conv. (€)': '{:.2f}€'
    })
    
    st.dataframe(
        styled_table,
        use_container_width=True,
        hide_index=True
    )
    
    # Recommandation rapide
    st.markdown("#### 🎯 Recommandation")
    meilleur_canal = synthèse_canaux.loc[synthèse_canaux['Conversion (%)'].idxmax(), 'Canal']
    st.info(f"Prioriser le canal **{meilleur_canal}** qui montre le meilleur taux de conversion.")

# --- PIED DE PAGE ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.9em;">
    📅 Données : Octobre 2025 | 📊 Tableau de Bord NovaRetail | 🔄 Mise à jour : Mensuelle
</div>
""", unsafe_allow_html=True)

# --- FONCTIONNALITÉS SUPPLEMENTAIRES ---
with st.expander("📥 Télécharger les données"):
    csv = df_filtre.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Télécharger les données filtrées (CSV)",
        data=csv,
        file_name="nova_retail_octobre_2025.csv",
        mime="text/csv"
    )

with st.expander("ℹ️ Notes méthodologiques"):
    st.markdown("""
    **Méthodologie :**
    - **CTR** : Clics ÷ Impressions × 100
    - **Taux de conversion** : Conversions ÷ Clics × 100 (campagne) ou Clients ÷ Leads × 100 (CRM)
    - **Coût par conversion** : Coût total ÷ Conversions
    
    **Données :**
    - Période : Octobre 2025 uniquement
    - Source : CRM NovaRetail + Données marketing
    - Leads analysés : 31 leads uniques
    
    **Limitations :**
    - Données mensuelles uniquement
    - Pas de segmentation temporelle intra-mois
    - Données de coût répliquées par lead pour agrégation
    """)