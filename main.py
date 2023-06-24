import pandas as pd
import plotly.express as px
import os
import streamlit as st
import warnings

warnings.filterwarnings('ignore')

# Configuration
st.set_page_config(page_title="Tableau de bord", page_icon=":bar_chart:", layout="wide")

# Entête du tableau de bord
st.title(":bar_chart: TABLEAU DE BORD DES VENTES ")
st.write('Tableau de bord réalisé avec Streamlit et Plotly')
st.markdown("Auteur: PARFAIT TANOH, Data Scientist")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Chargement du fichier
file_path = st.sidebar.file_uploader("Choisir un fichier CSV", type="csv")
if file_path is not None:
    df = pd.read_csv(file_path, encoding="ISO-8859-1")
else:
    st.sidebar.write("Veuillez charger un fichier CSV.")
    st.stop()

col1, col2 = st.columns(2)
df["Order Date"] = pd.to_datetime(df["Order Date"])

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Date Debut", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("Date fin", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choisissez votre filtre :")
region = st.sidebar.multiselect("Choisissez votre région", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Filtrer par état
state = st.sidebar.multiselect("Choisissez l'état", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Filtrer par ville
city = st.sidebar.multiselect("Choisissez la ville", df3["City"].unique())

# Filtrer la base de données par région, état et ville
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif not state and not city:
    filtered_df = df3[df["State"].isin(region) & df3["City"].isin(city)]
elif not region and not city:
    filtered_df = df3[df["State"].isin(region) & df3["City"].isin(city)]
elif not region and not state:
    filtered_df = df3[df["State"].isin(region) & df3["City"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Ventes par Catégorie")
    fig = px.bar(category_df, x="Category", y="Sales", template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Ventes par Région")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"].astype(str), textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Données par Catégorie"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger les données", data=csv, file_name="Category.csv", mime="text/csv", help='Cliquez ici pour télécharger les données au format CSV')

with cl2:
    with st.expander("Données par Région"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger les données", data=csv, file_name="Region.csv", mime="text/csv", help='Cliquez ici pour télécharger les données au format CSV')

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Analyse de séries temporelles')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Montant"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Données de la série temporelle"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger les données", data=csv, file_name="timeseries.csv", mime="text/csv", help='Cliquez ici pour télécharger les données au format CSV')

# Créer un treemap basé sur la région, la catégorie et la sous-catégorie
st.subheader("Vue hiérarchique des ventes")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)
with chart1:
    st.subheader('Ventes par Segment')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Catégorie par Segment')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="plotly_dark")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff

st.subheader(":point_right: Résumé des ventes par sous-catégorie")
with st.expander("Tableau de résumé"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("Tableau des sous-catégories par mois")
filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
sub_category_year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
st.write(sub_category_year.style.background_gradient(cmap="Blues"))

# Créer un scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1['layout'].update(title="Relation entre Vente et profit", titlefont=dict(size=20),
                       xaxis=dict(title="Sales", titlefont=dict(size=19)),
                       yaxis=dict(title="Profit", titlefont=dict(size=19)))
st.plotly_chart(data1, use_container_width=True)

with st.expander("Voir les données"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Télécharger le jeu de données original
st.markdown("Auteur: PARFAIT TANOH, Data Scientist")
st.markdown("Pour charger votre propre jeu de données, veuillez sélectionner un fichier CSV dans la barre latérale.")
