import pandas as pd
from geopy.distance import geodesic
from tkinter import Tk, Label, Button, messagebox

# Load dataset
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

# Generate traits from Category and Specific_category
def generate_traits(data):
    traits = {}
    for _, row in data.iterrows():
        # Create a set of traits for each user (could be expanded as needed)
        user_id = row["ID"]
        category = row["Category"]
        specific_category = row["Spesific_category"]
        traits[user_id] = {category, specific_category}
    return traits

def validate_coordinates(data):
    for index, row in data.iterrows():
        lat, lon = map(float, row["Locations"].split(','))
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude at row {index}: {lat}")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Invalid longitude at row {index}: {lon}")

# Calculate match score
def calculate_match_score(person, candidate, weights, traits):
    score = 0
    
    # Matching categories and specific categories
    if person["Category"] == candidate["Category"]:
        score += weights["category"]
        if person["Spesific_category"] == candidate["Spesific_category"]:
            score += weights["specific_category"]

    # Matching interests (number of traits overlapping)
    overlapping_interests = len(set(traits[person["ID"]]) & set(traits[candidate["ID"]]))
    score += weights["multiple_interests"] * overlapping_interests

    # Distance
    person_loc = tuple(map(float, person["Locations"].split(';')))
    candidate_loc = tuple(map(float, candidate["Locations"].split(';')))
    distance = geodesic(person_loc, candidate_loc).kilometers
    score += max(0, weights["distance"] / (1 + distance))  # Penalize farther distances

    # Former matches
    if candidate["ID"] in person["Former_matched"].split(';'):
        score += weights["former_match"]

    return score

# GUI Application
# GUI Application
class MatchingApp:
    def __init__(self, master, data, weights, traits):
        self.master = master
        self.data = data
        self.weights = weights
        self.traits = traits
        self.current_user = None
        self.current_candidate_index = 0
        self.matches = []

        self.master.title("Tinder Matching Simulator")
        self.master.geometry("400x600")

        # Displaying current user's info
        self.user_label = Label(self.master, text="", font=("Helvetica", 16))
        self.user_label.pack(pady=10)

        # Display candidate info
        self.candidate_label = Label(self.master, text="", font=("Helvetica", 14))
        self.candidate_label.pack(pady=20)

        # Buttons
        self.like_button = Button(self.master, text="Like", command=self.like_candidate, bg="green", fg="white", width=10)
        self.like_button.pack(side="left", padx=50, pady=10)

        self.dislike_button = Button(self.master, text="Dislike", command=self.next_candidate, bg="red", fg="white", width=10)
        self.dislike_button.pack(side="right", padx=50, pady=10)

    def set_user(self, user_id):
        user_data = self.data[self.data["ID"] == user_id]
        if user_data.empty:
            raise ValueError(f"No ID With: {user_id}")
        self.current_user = user_data.iloc[0]
        self.user_label.config(text=f"Logged in as: {self.current_user['Name']} ({self.current_user['Category']})")
        self.prepare_matches()

    def prepare_matches(self):
        self.matches = []
        for i, candidate in self.data.iterrows():
            if candidate["ID"] == self.current_user["ID"]:
                continue

            score = calculate_match_score(self.current_user, candidate, self.weights, self.traits)
            self.matches.append((candidate, score))

        self.matches = sorted(self.matches, key=lambda x: x[1], reverse=True)
        self.current_candidate_index = 0
        self.show_candidate()

    def show_candidate(self):
        """Displays the current candidate's details in the GUI."""
        if self.current_candidate_index < len(self.matches):
            # Get the current candidate
            candidate, _ = self.matches[self.current_candidate_index]

            # Extract candidate details
            candidate_name = candidate['Name']
            candidate_gender = "Woman" if candidate['Gender'] == "F" else "Man"
            candidate_category = candidate['Category']
            candidate_specific_category = candidate['Spesific_category']
            candidate_description = candidate['Descriptions']

            # Calculate distance
            user_loc = tuple(map(float, self.current_user["Locations"].split(';')))
            candidate_loc = tuple(map(float, candidate["Locations"].split(';')))
            distance = geodesic(user_loc, candidate_loc).kilometers

            # Update the labels with candidate details
            self.candidate_label.config(
                text=f"Name: {candidate_name}\n"
                     f"Gender: {candidate_gender}\n"
                     f"Category: {candidate_category}\n"
                     f"Specific Category: {candidate_specific_category}\n"
                     f"Description: {candidate_description}\n"
                     f"Distance: {distance:.2f} km"
            )
        else:
            # No more candidates
            self.candidate_label.config(text="No more matches available!")
            messagebox.showinfo("End of Matches", "You've viewed all matches!")

    def next_candidate(self):
        self.current_candidate_index += 1
        self.show_candidate()

    def like_candidate(self):
        candidate, _ = self.matches[self.current_candidate_index]
        messagebox.showinfo("Match", f"You liked {candidate['Name']}!")
        self.next_candidate()

# Main program
if __name__ == "__main__":
    file_path = r"Datasets_Informatch.csv"  # Replace with your dataset file path

    # Define weights
    weights = {
        "category": 10,
        "specific_category": 20,
        "multiple_interests": 5,
        "distance": 50,
        "former_match": -10  # Penalize if they matched before
    }

    # Load data
    data = load_data(file_path)
    print(data.head())
    # Generate traits from the loaded data
    traits = generate_traits(data)

    # Start GUI
    root = Tk()
    app = MatchingApp(root, data, weights, traits)
    app.set_user("S029")  # Set initial user (change as needed)
    root.mainloop()
