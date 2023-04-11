from flask import Flask, request, jsonify, render_template
import json
from datetime import timedelta

app = Flask(__name__)

# Define the path to the high scores file
high_scores_file = "high_scores.json"

def load_high_scores():
    try:
        with open(high_scores_file) as f:
            high_scores = json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist, create an empty dictionary to store the high scores
        high_scores = {}

    return high_scores

def get_sorted_high_scores():
    # Load the high scores from the file
    high_scores = load_high_scores()

    # Convert the time strings in the high scores to integers in seconds
    for score in high_scores.values():
        time_str = score['time']
        minutes, seconds = time_str.split(':')
        score['time'] = int(minutes) * 60 + int(seconds)

    # Sort the high scores by time in ascending order
    sorted_scores = sorted(high_scores.values(), key=lambda x: x['time'])

    # Format the time strings in the high scores as "MM:SS"
    for score in sorted_scores:
        time_in_seconds = score['time']
        minutes, seconds = divmod(time_in_seconds, 60)
        score['time'] = f"{minutes:02d}:{seconds:02d}"

    return sorted_scores


@app.route('/highscores')
def get_high_scores():
    # Return the sorted high scores as JSON
    sorted_scores = get_sorted_high_scores()
    return jsonify(sorted_scores)

@app.route('/highscores', methods=['POST'])
def add_high_score():
    # Load the existing high scores from the file
    high_scores = load_high_scores()

    # Get the name and time from the request body
    name = request.json.get('name')
    time = request.json.get('time')

    # Compute the new max ID for the new high score
    max_id = max(int(k) for k in high_scores.keys()) if high_scores else 0
    new_id = max_id + 1

    # Add the new high score to the existing scores
    high_scores[str(new_id)] = {'name': name, 'time': time}

    # Save the updated high scores to the file
    with open(high_scores_file, 'w') as f:
        json.dump(high_scores, f)

    return jsonify({'id': new_id})

@app.route('/')
def display_high_scores():
    sorted_scores = get_sorted_high_scores()
    high_scores_sorted = [(id, data['name'], timedelta(seconds=data['time'])) for id, data in enumerate(sorted_scores, 1)]

    high_scores_formatted = []
    for score in high_scores_sorted:
        if score[2] < timedelta(seconds=60):
            formatted_time = str(score[2].seconds) + "sec"
        else:
            formatted_time = str(score[2].minutes) + "min " + str(score[2].seconds % 60) + "sec"
        high_scores_formatted.append((score[0], score[1], formatted_time))

    # Pass the high_scores_formatted variable to the render_template function
    return render_template('high_scores.html', high_scores=high_scores_formatted)


if __name__ == '__main__':
    app.run()
