# %% [markdown]
# ## Cellule
# La cellule suivante est dédiée aux imports de fonction

# %%
import pandas as pd
import os
from fastparquet import ParquetFile

# %%
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from category_encoders import TargetEncoder
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score


# %% [markdown]
# ## Description de la cellule
# La cellule suivant permet d'importer un fichier .csv

# %%
def read_csv(file):
    return pd.read_csv(file)

# %% [markdown]
# ## Description
# Importation des fichiers

# %%
csv_data = {}

for file in os.listdir("csv"):
    csv_data[file.split('.')[0]]=read_csv("csv/"+file)

# %% [markdown]
# ## Description de la cellule
# Importation du fichier parquet

# %%
dp = ParquetFile('weather.parquet')
weather = dp.to_pandas()

# %% [markdown]
# # ATTENTION
# On va maintenant rassembler les données et construire le dataSet

# %% [markdown]
# ### Construction principale

# %%
data_set = pd.DataFrame({
        "driverId": csv_data['results']['driverId'],
        "constructorId": csv_data['results']['constructorId'],
        "position": csv_data['results']['position'],
        "positionOrder": csv_data['results']['positionOrder'],
        "circuitId": csv_data['circuits']['circuitId'],
        "circuitName": csv_data['circuits']['name'],
        "circuitsLocation": csv_data['circuits']['location'],
        "lat": csv_data['circuits']['lat'],
        "lng": csv_data['circuits']['lng'],
        "raceId": csv_data['races']['raceId']
})

# %% [markdown]
# ## Ajout et adaptation

# %%
csv_data['constructor_results']['constructor_points_moy'] = csv_data['constructor_results'].groupby('constructorId')['points'].transform('mean')

# %%
csv_data['circuits'].drop(columns=['circuitRef', 'location', 'country', 'alt', 'url'], axis=1, inplace=True)
csv_data['constructors'].drop(columns=['constructorRef', 'nationality', 'url'], axis=1, inplace=True)
csv_data['constructor_results'].drop(columns=['points', 'status'], axis=1, inplace=True)
csv_data['constructor_standings'].drop(columns=['points', 'positionText',  'wins'], axis=1, inplace=True)
csv_data['drivers'].drop(columns=['driverRef', 'number', 'nationality', 'dob', 'forename', 'code', 'url'], axis=1, inplace=True)
csv_data['driver_standings'].drop(columns=['positionText', 'points', 'wins'], axis=1, inplace=True)
csv_data['lap_times'].drop(columns=['time', 'milliseconds'], axis=1, inplace=True)
csv_data['pit_stops'].drop(columns=['time', 'duration', 'milliseconds'], axis=1, inplace=True)
csv_data['qualifying'].drop(columns=['number', 'position', 'q1', 'q2', 'q3'], axis=1, inplace=True)
csv_data['races'].drop(columns=['date', 'time', 'url', 'fp1_date','fp1_time','fp2_date','fp2_time','fp3_date','fp3_time','quali_date','quali_time','sprint_date','sprint_time'], axis=1, inplace=True)

# %%
pd.merge(data_set, csv_data['circuits'], on='circuitId', how='inner')
pd.merge(data_set, csv_data['constructors'], on='constructorId', how='inner')
pd.merge(data_set, csv_data['constructor_results'], on='constructorId', how='inner')
pd.merge(data_set, csv_data['constructor_standings'], on='constructorId', how='inner')
pd.merge(data_set, csv_data['drivers'], on='driverId', how='inner')
pd.merge(data_set, csv_data['driver_standings'], on='driverId', how='inner')
pd.merge(data_set, csv_data['lap_times'], on='driverId', how='inner')
pd.merge(data_set, csv_data['pit_stops'], on='driverId', how='inner')
pd.merge(data_set, csv_data['qualifying'], on='driverId', how='inner')
pd.merge(data_set, csv_data['races'], on='raceId', how='inner')

# %%
data_set.drop_duplicates(inplace=True)

# %% [markdown]
# ### On retire les pilotes qui ne sont plus en activité

# %%
active_driver_ids = [1, 3, 4, 5, 6, 7, 10, 14, 16, 18, 20, 22, 23, 24, 27, 31, 44, 55, 63, 77]
data_set = data_set[data_set['driverId'].isin(active_driver_ids)]

# %% [markdown]
# On converti les valeurs qui nécessite de l'être

# %%
data_set['position'] = data_set['position'].apply(lambda x: 0 if pd.isna(x) or isinstance(x, str) else x)

# %% [markdown]
# ## On mets tous les identifiants en tant que chaîne de caractère

# %%
data_set['driverId'] = data_set['driverId'].astype('str')
data_set['constructorId'] = data_set['constructorId'].astype('str')

# %% [markdown]
# ## On encode les valeurs str

# %%
data_set

# %%
y_bis = data_set.loc[:,:"position"]
y_bis.drop(["driverId", "constructorId"], axis=1, inplace=True)

# %%
target_encoder = TargetEncoder()
data_set['driverId_encoded'] = target_encoder.fit_transform(data_set['driverId'], y_bis['position'])
data_set['constructorId_encoded'] = target_encoder.fit_transform(data_set['constructorId'], y_bis['position'])

# %% [markdown]
# ## On défini x et y

# %%
X = data_set[['driverId_encoded', 'constructorId_encoded', 'position', 'positionOrder']]
y = data_set['position']

# %% [markdown]
# # Division
# 

# %%
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# %%
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)


# %%
y_test_pred = model.predict(X_test)
y_train_pred = model.predict(X_train)

# %%
accuracy_score_test = accuracy_score(y_test, y_test_pred)
accuracy_score_train = accuracy_score(y_train, y_train_pred)

# %%
print(accuracy_score_train)
print(accuracy_score_test)

# %%
x_test


