import pandas as pd
from geopy.distance import geodesic
from tkinter import Tk, Label, Button, PhotoImage, Toplevel, messagebox

# Load dataset
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

# Calculate match score
def calculate_match_score(person, candidate, weights, traits):
    score = 0
    
    # Matching categories and specific categories
    if person["Category"] == candidate["Category"]:
        score += weights["category"]
        if person["Spesific category"] == candidate["Spesific category"]:
            score += weights["specific_category"]

    # Matching interests (number of traits overlapping)
    overlapping_interests = len(set(traits[person["ID"]]) & set(traits[candidate["ID"]]))
    score += weights["multiple_interests"] * overlapping_interests

    # Distance
    person_loc = tuple(map(float, person["Coordinate"].split(',')))
    candidate_loc = tuple(map(float, candidate["Coordinate"].split(',')))
    distance = geodesic(person_loc, candidate_loc).kilometers
    score += max(0, weights["distance"] / (1 + distance))  # Penalize farther distances

    # Former matches
    if candidate["ID"] in person["Former Matched"].split(';'):
        score += weights["former_match"]

    return score

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
        self.current_user = self.data[self.data["ID"] == user_id].iloc[0]
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
        if self.current_match_index < len(self.match_queue):
            # Get the current candidate
            candidate = self.match_queue[self.current_match_index]

            # Extract candidate details
            candidate_name = candidate['Name']
            candidate_gender = "Woman" if candidate['Gender'] == "F" else "Man"
            candidate_category = candidate['Category']
            candidate_specific_category = candidate['Spesific_category']
            candidate_description = candidate['Descriptions']

            # Update the labels with candidate details
            self.candidate_label.config(
                text=f"Name: {candidate_name}\n"
                     f"Gender: {candidate_gender}\n"
                     f"Category: {candidate_category}\n"
                     f"Specific Category: {candidate_specific_category}\n"
                     f"Description: {candidate_description}"
            )
        else:
            # No more candidates
            self.candidate_label.config(text="No more matches available!")
            messagebox.showinfo("End of Matches", "You've viewed all matches!")

    def next_candidate(self):
        self.current_candidate_index += 1
        self.show_candidate()

    def like_candidate(self):
        candidate, score = self.matches[self.current_candidate_index]
        messagebox.showinfo("Match", f"You liked {candidate['Name']}!")
        self.next_candidate()

# Main program
if __name__ == "__main__":
    file_path = "people_dataset.csv"  # Replace with your dataset file path

    # Define weights
    weights = {
        "category": 10,
        "specific_category": 20,
        "multiple_interests": 5,
        "distance": 100,
        "former_match": -10  # Penalize if they matched before
    }

    # Example trait mapping (for testing purposes)
    traits = {
        "U01": {"Music", "Movies"},
        "U02": {"Movies", "Gaming"},
        "U03": {"Gaming", "Swimming"},
        # Add more traits
    }

    # Load data
    data = load_data(file_path)

    # Start GUI
    root = Tk()
    app = MatchingApp(root, data, weights, traits)
    app.set_user("U01")  # Set initial user (change as needed)
    root.mainloop()
