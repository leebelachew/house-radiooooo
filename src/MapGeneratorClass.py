import plotly.express as px
import pandas as pd
from PIL import Image

class MapGenerator:
    def __init__(self, audio_features_file, metadata_file):
        self.audio_features_file = audio_features_file
        self.metadata_file = metadata_file
        self.city_to_country = {
            "Chicago": "USA", "Detroit": "USA", "New York": "USA", "Los Angeles": "USA",
            "Berlin": "Germany", "Paris": "France", "London": "UK", "Ibiza": "Spain",
            "Barcelona": "Spain", "Amsterdam": "Netherlands", "Stockholm": "Sweden",
            "Rio de Janeiro": "Brazil", "Bogota": "Colombia", "Lagos": "Nigeria",
            "Cape Town": "South Africa", "Johannesburg": "South Africa"
        }

    def load_and_process_data(self): #(accessing csv and extracting from csv) inspired by 'https://www.geeksforgeeks.org/working-csv-files-python/' and https://docs.python.org/3/library/csv.html and ChatGPT
        audio_features = pd.read_csv(self.audio_features_file)
        metadata = pd.read_csv(self.metadata_file)
        combined_data = pd.merge(metadata, audio_features, on=["Title", "Artist"], how="inner")
        combined_data["Country"] = combined_data["City"].map(self.city_to_country)
        return combined_data

    def calculate_similarity(self, user_vector):
        combined_data = self.load_and_process_data()
        feature_columns = ['Popularity', 'Energy', 'Danceability', 'Positiveness',
                           'Speechiness', 'Liveness', 'Acousticness', 'Instrumentalness', 'Tempo']

        def cosine_similarity(vector1, vector2): #Use of Nested Function inspired by 112 Lecture
            print(vector1)
            print(vector2)
            dotProduct = 0
            for i in range(len(vector1)):
                dotProduct += vector1[i] * vector2[i]
            magnitude1 = (sum(a * a for a in vector1))**0.5
            magnitude2 = (sum(b * b for b in vector2))**0.5
            
            return dotProduct / (magnitude1 * magnitude2) if magnitude1 > 0 and magnitude2 > 0 else 0
            
        combined_data["Similarity"] = combined_data[feature_columns].apply(
            lambda row: cosine_similarity(user_vector, row.values), axis=1
        )
        country_scores = combined_data.groupby("Country")["Similarity"].mean().reset_index() #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html
        return country_scores

    def generate_map(self, country_scores, output_image="user_similarity_map.png"): #Inspired by https://plotly.com/python/choropleth-maps/, debugs inspired by chatGTP
        fig = px.choropleth(
            country_scores,
            locations="Country",
            locationmode="country names",
            color="Similarity",
            color_continuous_scale="Blues",
            scope="world",
            labels={"Similarity": "Match Score"}
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            geo=dict(showframe=False, showcoastlines=True, 
                    projection_type="equirectangular", lataxis=dict(range=[-60, 90])),
            coloraxis_colorbar=dict(
                orientation="h", x=0.5, y=-0.2, xanchor="center", len=0.9,
                thickness=15, tickfont=dict(size=12, color="white"),
                titlefont=dict(size=14, color="white")
            )
        )
        raw_image = "raw_map.png"
        fig.write_image(raw_image, width=800, height=800)
        print(f"Raw map saved as {raw_image}")

        with Image.open(raw_image) as img: #https://www.geeksforgeeks.org/python-pil-image-save-method/
            img.save(output_image)
        print(f"Map saved as {output_image}")

    def generate_map_for_user(self, user_vector, output_image="user_similarity_map.png"):
        country_scores = self.calculate_similarity(user_vector)
        self.generate_map(country_scores, output_image)