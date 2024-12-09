import pandas as pd
from geopy.distance import geodesic
import folium
from IPython.display import display

# Load dataset
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

# Generate traits from Category and Specific_category
def generate_traits(data):
    traits = {}
    for _, row in data.iterrows():
        user_id = row["ID"]
        category = row["Category"]
        specific_category = row["Spesific_category"]
        traits[user_id] = {category, specific_category}
    return traits

# Find nearest match with the desired interest
def find_nearest_with_interest(data, user_id, interest, traits):
    user_data = data[data["ID"] == user_id]
    if user_data.empty:
        raise ValueError(f"No user found with ID: {user_id}")
    
    user = user_data.iloc[0]
    user_loc = tuple(map(float, user["Locations"].split(';')))
    
    matches = []
    for _, candidate in data.iterrows():
        if candidate["ID"] == user["ID"]:
            continue
        candidate_traits = traits[candidate["ID"]]
        if interest in candidate_traits:
            candidate_loc = tuple(map(float, candidate["Locations"].split(';')))
            distance = geodesic(user_loc, candidate_loc).kilometers
            matches.append((candidate, distance))
    
    if not matches:
        return None, None
    
    # Find the closest candidate
    closest_candidate, min_distance = min(matches, key=lambda x: x[1])
    return closest_candidate, min_distance

# Visualize matches on map and print details
def visualize_matches(data, user_id, interest, weights, traits):
    closest_candidate, min_distance = find_nearest_with_interest(data, user_id, interest, traits)
    
    if closest_candidate is None:
        print(f"No matches found for interest '{interest}'.")
        return None
    
    user_data = data[data["ID"] == user_id].iloc[0]
    user_loc = tuple(map(float, user_data["Locations"].split(';')))
    candidate_loc = tuple(map(float, closest_candidate["Locations"].split(';')))
    
    # Display details of the closest candidate
    print("\n" + "-"*40)
    print("Details of the Nearest Match".center(40))
    print("-"*40)
    print(f"ID:            {closest_candidate['ID']}")
    print(f"Name:          {closest_candidate['Name']}")
    print(f"Gender:        {closest_candidate['Gender']}")
    print(f"Category:      {closest_candidate['Category']}")
    print(f"Specific Category: {closest_candidate['Spesific_category']}")
    print(f"Description:   {closest_candidate['Descriptions']}")
    print(f"Distance:      {min_distance:.2f} km")
    print("-"*40)
    print("\n")
    
    # Create map centered on the user's location
    user_map = folium.Map(location=user_loc, zoom_start=13)
    
    # Add user's marker
    folium.Marker(user_loc, popup=f"User: {user_data['Name']}", icon=folium.Icon(color="blue")).add_to(user_map)
    
    # Add closest candidate's marker
    folium.Marker(
        candidate_loc,
        popup=f"Candidate: {closest_candidate['Name']} (Distance: {min_distance:.2f} km)",
        icon=folium.Icon(color="green"),
    ).add_to(user_map)
    
    # Draw a line to the closest candidate
    folium.PolyLine([user_loc, candidate_loc], color="red", weight=2.5).add_to(user_map)
    
    return user_map

# Main program
if __name__ == "__main__":
    file_path = "/content/drive/MyDrive/Colab Notebooks/Datasets/Datasets_Informatch.csv"  # Replace with your dataset file path in Colab

    # Load data
    data = load_data(file_path)

    # Generate traits from the loaded data
    traits = generate_traits(data)

    # Interactive input
    user_id = input("Enter your User ID: ")
    interest = input("Enter the desired interest (Category/Specific Category): ")

    # Visualize matches for a specific user and interest
    user_map = visualize_matches(data, user_id, interest, None, traits)

    # Display the map directly in the Colab notebook
    if user_map:
        display(user_map)
