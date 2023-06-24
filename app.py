import pandas as pd
import plotly.express as px
import os
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Configuration
st.set_page_config(page_title="Dashbord", page_icon=":bar_chart:", layout="wide")

# Entête du tableau de bord
st.title(":bar_chart: TABLEAU DE BORD DES VENTES ")
st.write('Tableau de bord réalisé avec streamlit et plotly')
st.markdown('Auteur: Parfait Ngoran')
st.markdown('email: parfaittanoh42@gmail.com')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Chargement du fichier
os.chdir(r"/home/ngoran/DataScience/Tableau de bord")
df = pd.read_csv("data.csv", encoding="ISO-8859-1")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Date Debut", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("Date fin", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
region = st.sidebar.multiselect("Pick la Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create for state
state = st.sidebar.multiselect("Pick l'État", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Create city
city = st.sidebar.multiselect("Pick la Ville", df3["City"].unique())

# Filter the database on region, state and city
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif not state and not city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
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
    st.subheader("Ventes par Category")
    fig = px.bar(category_df, x="Category", y="Sales", template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Ventes par Region")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"].astype(str), textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 =st.columns((2))
with cl1:
    with st.expander("Donnée par Category"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv= category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data= csv, file_name="Category.csv", mime="text/csv",help='click here to download the data as a CSV file')


with cl2:
    with st.expander("Donnée par Region"):
        region=filtered_df.groupby(by ="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv =region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data= csv, file_name="Region.csv", mime="text/csv",help='Cliquer ici pour télécharger le fichier en csv')


filtered_df["month_year"]=filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time series Analysis')

linechart =pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2=px.line(linechart, x="month_year", y="Sales", labels={"Sales":"Amount"},height=500, width=1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("les Données de temps"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv=linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data= csv, file_name="timeseries.csv", mime="text/csv",help='Cliquer ici pour télécharger le fichier en csv')
    
    
#Create a treem based on region, category, sub-category
st.subheader("Vue hiérarchique des ventes")
fig3=px.treemap(filtered_df, path=["Region","Category","Sub-Category"],values="Sales",hover_data=["Sales"],color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3,use_container_width=True)

chart1, chart2= st.columns((2))
with chart1:
    st.subheader('Vente par Segement')
    fig=px.pie(filtered_df, values="Sales",names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category par Segement')
    fig=px.pie(filtered_df, values="Sales",names="Category", template="plotly_dark")
    fig.update_traces(text=filtered_df["Category"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)
    
import plotly.figure_factory as ff
st.subheader(":point_right: Resumé des des ventes par sous category")
with st.expander("Summary_Table"):
    df_sample= df[0:5][["Region","State","City","Category","Profit","Quantity"]]
    fig=ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig,use_container_width=True)
    
st.markdown("Table des sous category par mois")
filtered_df["month"]=filtered_df["Order Date"].dt.month_name()
sub_category_year = pd.pivot_table(data=filtered_df, values="Sales",index=["Sub-Category"],columns= "month")
st.write(sub_category_year.style.background_gradient(cmap="Blues"))


#Create scatter plot
data1=px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1['layout'].update(title="Relation entre Vente et profit", titlefont=dict(size=20),xaxis=dict(title="Sales",titlefont=dict(size=19)),yaxis=dict(title="Profit",titlefont=dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("Voir les Données"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))
    
#Telecherger la dataset originale

st.write('Auteur: PARFAIT TANOH, Data Scientist')