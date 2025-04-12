import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import io


url = "https://en.wikipedia.org/wiki/List_of_most-streamed_songs_on_Spotify"
response = requests.get(url)

if response.status_code != 200:
    raise Exception(f"Error accediendo la pagina: {response.status_code}")

# Check the response
print("Status:", response.status_code)

# Transformamos el html

#Extraemos las tablas con pandas
html = io.StringIO(response.text)  # Convert the HTML to a text file

# Leemos el html y damos el numero de tablas
tables = pd.read_html(html)
print(f"se encontro {len(tables)} tablas.")

# Inspeccionas las primeras filas de la tabla
df = tables[0]  # Extraemos la primera tabla de las 27
df.head()  

#Guardamos la informacion en sqlite
# Creamos la base de datos
conn = sqlite3.connect("spotify_top_songs.db")

# Creamos la tabla en sqlite
df.to_sql("most_streamed", conn, if_exists="replace", index=False)
cursor = conn.cursor()

# Insertamos la info en la base de datos
cursor.execute("SELECT COUNT(*) FROM most_streamed")
print("Filas insertadas:", cursor.fetchone()[0])

conn.commit()
conn.close()

#Visualizacion de la info

# Asegúrate de convertir la columna a tipo numérico
df["Streams (billions)"] = pd.to_numeric(df["Streams (billions)"], errors='coerce')

# Luego puedes continuar con el gráfico
top10 = df.nlargest(10, "Streams (billions)")
plt.figure(figsize=(12, 6))
sns.barplot(data=top10, x="Streams (billions)", y="Song", hue="Song", palette="viridis", legend=False)
plt.title("Top 10 Canciones en Spotify")
plt.xlabel("Streams (en billones)")
plt.ylabel("Canciones")
plt.tight_layout()
plt.show()

# Primero convertimos la columna "Release date" a formato datetime
df["Release date"] = pd.to_datetime(df["Release date"], errors='coerce')

# Ahora extraemos el año en una nueva columna
df["Year"] = df["Release date"].dt.year

plt.figure(figsize=(10, 5))
sns.countplot(data=df, x="Year", order=sorted(df["Year"].dropna().unique()))
plt.title("Número de canciones más reproducidas por año")
plt.xlabel("Año")
plt.ylabel("Número de canciones")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

artistas = df["Artist(s)"].value_counts().nlargest(10)

plt.figure(figsize=(10, 6))
sns.barplot(x=artistas.values, y=artistas.index, hue=artistas.index, palette="coolwarm", legend=False)
plt.title("Artistas con mas Canciones")
plt.xlabel("Numero de Canciones")
plt.ylabel("Artista")
plt.tight_layout()
plt.show()

