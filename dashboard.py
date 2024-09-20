import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Chargement des données
df_races = pd.read_csv('csv/races.csv')
df_constructor_results = pd.read_csv('csv/constructors.csv')
df_drivers = pd.read_csv('csv/drivers.csv')
df_circuits = pd.read_csv('csv/circuits.csv')
df_results = pd.read_csv('csv/results.csv')
df_qualifying = pd.read_csv('csv/qualifying.csv')
df_pit_stops = pd.read_csv('csv/pit_stops.csv')
df_driver_standings = pd.read_csv('csv/driver_standings.csv')

# Nettoyage des colonnes et conversion des types
df_pit_stops['milliseconds'] = pd.to_numeric(df_pit_stops['milliseconds'], errors='coerce')

# Titre du dashboard
st.title("🏎️ Dashboard de Prédiction F1")

# Sélection de thème
st.markdown("""
    <style>
        .main {
            background-color: #1E1E1E; 
            color: white;
        }
        h1 {
            color: #FF8C00;
        }
        .sidebar .sidebar-content {
            background-color: #2E2E2E;
        }
        .css-1v0mbdj {
            background-color: #2E2E2E;
        }
        .css-1kyxreq {
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

# Filtres dans la barre latérale
st.sidebar.title("🔧 Filtres")

# Filtre pour constructeur
if 'name' in df_constructor_results.columns:
    constructor_names = df_constructor_results['name'].unique()
    selected_constructor_name = st.sidebar.selectbox('Sélectionner un constructeur:', constructor_names)
    filtered_constructor_data = df_constructor_results[df_constructor_results['name'] == selected_constructor_name]
    st.sidebar.subheader(f"🔍 Données pour {selected_constructor_name}")
    st.sidebar.dataframe(filtered_constructor_data)

# Filtre pour pilotes actuels
if 'surname' in df_drivers.columns and 'driverId' in df_results.columns:
    latest_race_id = df_races['raceId'].max()
    drivers_in_latest_race = df_results[df_results['raceId'] == latest_race_id]['driverId'].unique()
    current_drivers = df_drivers[df_drivers['driverId'].isin(drivers_in_latest_race)]
    driver_standings = df_driver_standings[df_driver_standings['raceId'] == latest_race_id]
    top_23_drivers = driver_standings.nlargest(23, 'points')['driverId']
    current_drivers = current_drivers[current_drivers['driverId'].isin(top_23_drivers)]
    current_driver_surnames = current_drivers['surname'].unique()
    selected_driver_surname = st.sidebar.selectbox('Sélectionner un pilote:', current_driver_surnames)
    filtered_driver_data = current_drivers[current_drivers['surname'] == selected_driver_surname]
    st.sidebar.subheader(f"🚗 Données pour {selected_driver_surname}")
    st.sidebar.dataframe(filtered_driver_data)

# Filtre pour circuits
if 'name' in df_circuits.columns:
    circuit_names = df_circuits['name'].unique()
    selected_circuit_name = st.sidebar.selectbox('Sélectionner un circuit:', circuit_names)
    filtered_circuit_data = df_circuits[df_circuits['name'] == selected_circuit_name]
    st.sidebar.subheader(f"🌍 Données pour {selected_circuit_name}")
    st.sidebar.dataframe(filtered_circuit_data)

# Curseurs pour la météo
st.sidebar.subheader("🌤️ Conditions Météorologiques")
temperature = st.sidebar.slider("Température (°C)", min_value=-10, max_value=40, value=20)
humidity = st.sidebar.slider("Humidité (%)", min_value=0, max_value=100, value=50)
weather_condition = st.sidebar.selectbox("Condition Météorologique", ["Ensoleillé", "Nuageux", "Pluvieux"])

# Fonction pour calculer les probabilités avancées de victoire
def calculate_advanced_driver_probabilities(circuit_name, temp, hum, weather):
    circuit_id = df_circuits[df_circuits['name'] == circuit_name]['circuitId'].values[0]
    races_on_circuit = df_races[df_races['circuitId'] == circuit_id]['raceId'].unique()
    results_on_circuit = df_results[df_results['raceId'].isin(races_on_circuit)]

    # Calculer le classement moyen pour chaque pilote sur ce circuit
    average_positions = results_on_circuit.groupby('driverId')['positionOrder'].mean().reset_index()
    average_positions.columns = ['driverId', 'avg_position']

    # Ajouter les informations des pilotes (forename, surname)
    average_positions = average_positions.merge(df_drivers[['driverId', 'surname']], on='driverId', how='left')

    # Ajouter les performances en qualifications
    qualifying_on_circuit = df_qualifying[df_qualifying['raceId'].isin(races_on_circuit)]
    avg_qualifying_positions = qualifying_on_circuit.groupby('driverId')['position'].mean().reset_index()
    avg_qualifying_positions.columns = ['driverId', 'avg_qualifying_position']
    average_positions = average_positions.merge(avg_qualifying_positions, on='driverId', how='left')

    # Ajouter les arrêts au stand
    pit_stops_on_circuit = df_pit_stops[df_pit_stops['raceId'].isin(races_on_circuit)]
    avg_pit_stops = pit_stops_on_circuit.groupby('driverId')['milliseconds'].mean().reset_index()
    avg_pit_stops.columns = ['driverId', 'avg_pit_stop_duration_ms']
    average_positions = average_positions.merge(avg_pit_stops, on='driverId', how='left')

    # Ajouter les classements actuels des pilotes
    latest_race_id = df_races['raceId'].max()
    latest_driver_standings = df_driver_standings[df_driver_standings['raceId'] == latest_race_id]
    average_positions = average_positions.merge(latest_driver_standings[['driverId', 'points']], on='driverId', how='left')

    # Calculer la probabilité de victoire
    average_positions['win_probability'] = 1 / (average_positions['avg_position'] + 1)
    total_probability = average_positions['win_probability'].sum()
    average_positions['win_probability'] /= total_probability

    # Ajuster les probabilités en fonction de la météo
    if weather == "Pluvieux":
        temp *= 0.9  # Réduire l'impact de la température dans des conditions pluvieuses
    elif weather == "Nuageux":
        temp *= 0.95  # Réduire légèrement l'impact de la température pour les jours nuageux

    # Ajuster les probabilités avec la température et l'humidité
    average_positions['win_probability'] *= (temp / 20) * (hum / 50)
    
    # Normaliser les probabilités
    average_positions['win_probability'] = average_positions['win_probability'] / average_positions['win_probability'].sum()

    return average_positions

# Visualisation interactive : Prédiction du pilote le plus performant
st.subheader("🏆 Prédiction du Pilote avec la Meilleure Chance de Gagner")

if not filtered_circuit_data.empty:
    col1, col2 = st.columns(2)

    with col1:
        # Calculer les probabilités de victoire
        driver_probabilities = calculate_advanced_driver_probabilities(selected_circuit_name, temperature, humidity, weather_condition)

        # Trier les pilotes par probabilité de victoire décroissante
        driver_probabilities = driver_probabilities.sort_values(by='win_probability', ascending=False)

        # Afficher les pilotes avec leurs probabilités de victoire
        st.write("Voici les pilotes avec leurs chances estimées de victoire sur ce circuit :")
        st.dataframe(driver_probabilities[['surname', 'avg_position', 'win_probability']])

    with col2:
        # Afficher une visualisation des probabilités de victoire
        fig = px.bar(driver_probabilities, x='surname', y='win_probability', title="Probabilité de Victoire des Pilotes", labels={'win_probability': 'Probabilité de Victoire', 'surname': 'Pilote'}, color='win_probability', color_continuous_scale='Viridis')
        fig.update_layout(xaxis_title='Pilote', yaxis_title='Probabilité de Victoire', template='plotly_dark', xaxis=dict(tickangle=-45))
        fig.update_traces(texttemplate='%{y:.2%}', textposition='outside', marker=dict(line=dict(color='rgba(0,0,0,0.2)', width=1)))
        st.plotly_chart(fig)

    st.subheader("📊 Performance des Pilotes")
    col1, col2 = st.columns(2)

    with col1:
        # Ajouter un graphique de performance des pilotes
        fig_performance = go.Figure()

        # Ajouter la position moyenne
        fig_performance.add_trace(go.Bar(
            x=driver_probabilities['surname'], 
            y=driver_probabilities['avg_position'],
            name='Position Moyenne',
            marker=dict(color='blue'),
            text=[f"{pos:.1f}" for pos in driver_probabilities['avg_position']],
            textposition='outside'
        ))

        # Ajouter la position en qualification
        fig_performance.add_trace(go.Bar(
            x=driver_probabilities['surname'], 
            y=driver_probabilities['avg_qualifying_position'],
            name='Position Qualification',
            marker=dict(color='red'),
            text=[f"{pos:.1f}" for pos in driver_probabilities['avg_qualifying_position']],
            textposition='outside'
        ))

        fig_performance.update_layout(
            title="Performance des Pilotes",
            xaxis_title='Pilote',
            yaxis_title='Position',
            barmode='group',
            template='plotly_dark',
            xaxis=dict(tickangle=-45)
        )
        fig_performance.update_traces(
            marker_line=dict(color='rgba(0,0,0,0.2)', width=1)
        )
        st.plotly_chart(fig_performance)

    with col2:
        # Ajouter une comparaison entre deux pilotes
        st.subheader("⚔️ Comparaison entre Deux Pilotes")
        driver_options = driver_probabilities['surname'].unique()
        driver1 = st.selectbox('Sélectionner le Premier Pilote:', driver_options)
        driver2 = st.selectbox('Sélectionner le Deuxième Pilote:', driver_options)

        # Comparer les performances des deux pilotes
        if driver1 and driver2:
            comparison_data = driver_probabilities[driver_probabilities['surname'].isin([driver1, driver2])]
            st.write("Comparaison des Deux Pilotes Sélectionnés :")

            fig_comparison = go.Figure()
            fig_comparison.add_trace(go.Bar(
                x=comparison_data['surname'], 
                y=comparison_data['avg_position'],
                name='Position Moyenne',
                marker=dict(color='blue')
            ))
            fig_comparison.add_trace(go.Bar(
                x=comparison_data['surname'], 
                y=comparison_data['avg_qualifying_position'],
                name='Position Qualification',
                marker=dict(color='red')
            ))
            fig_comparison.update_layout(
                title="Comparaison des Performances des Pilotes",
                xaxis_title='Pilote',
                yaxis_title='Position',
                barmode='group',
                template='plotly_dark'
            )
            fig_comparison.update_traces(
                texttemplate='%{y:.0f}',
                textposition='outside',
                textfont=dict(size=12, color='white')
            )
            st.plotly_chart(fig_comparison)

    st.subheader("🏆 Répartition des Points")
    latest_race_id = df_races['raceId'].max()
    driver_standings = df_driver_standings[df_driver_standings['raceId'] == latest_race_id]

    if not driver_standings.empty:
        fig_points = px.pie(
            driver_standings, 
            names='driverId', 
            values='points', 
            title="Répartition des Points", 
            color='driverId', 
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig_points.update_layout(template='plotly_dark')
        st.plotly_chart(fig_points)
    else:
        st.write("Aucune donnée disponible pour la répartition des points.")

else:
    st.write("Les données du circuit sélectionné ne sont pas disponibles.")

st.write("Données issues des résultats des pilotes, des constructeurs, et des circuits F1.")
