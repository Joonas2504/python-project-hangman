from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

# Define the path to the high scores file
high_scores_file = "high_scores.json"

# Load the high scores from the file
try:
    with open(high_scores_file) as f:
        high_scores = json.load(f)
except FileNotFoundError:
    # If the file doesn't exist, create an empty dictionary to store the high scores
    high_scores = {}

# Define the endpoint to get the high scores
@app.route('/highscores')
def get_high_scores():
    with open('high_scores.json', 'r') as f:
        highscores = json.load(f)
    return jsonify(highscores)


# Define the endpoint to add a new high score
@app.route('/highscores', methods=['POST'])
def add_high_score():
    # Get the name and time from the request data
    data = request.json
    name = data['name']
    time = data['time']
    
    # Add the new high score to the dictionary
    high_scores[name] = time
    
    # Write the updated high scores to the file
    with open(high_scores_file, 'w') as f:
        json.dump(high_scores, f)
    
    # Return a success message
    return 'High score added successfully'

# Define the endpoint to display the high scores in an HTML table
@app.route('/')
def display_high_scores():
    response = requests.get('http://localhost:5000/highscores')
    high_scores = sorted(response.json().items(), key=lambda x: x[1])

    # Render the high scores in an HTML table
    return render_template('index.html', high_scores=high_scores)

if __name__ == '__main__':
    app.run()
