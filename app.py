from flask import Flask, request, jsonify, render_template, abort, make_response
import json
from datetime import timedelta
import os

app = Flask(__name__)

# Define the path to the high scores file
high_scores_file = "high_scores.json"

def load_high_scores(reverse=False, limit=None):
    # Check if the high scores file exists
    if os.path.exists("high_scores.json"):
        # Open the high scores file
        with open("high_scores.json", "r") as f:
            # Load the high scores from the file using the json module
            high_scores = json.load(f)
    else:
        # Create a new high scores file with an empty list
        high_scores = []

    # If reverse is True, sort the high scores in reverse order
    if reverse:
        high_scores = sorted(high_scores, key=lambda k: k['time'], reverse=True)

    # If limit is specified, slice the list of high scores to include only the top n
    if limit:
        high_scores = high_scores[:limit]

    # Return the list of high scores
    return high_scores


@app.route('/highscores', methods=['GET'])
def get_high_scores():
    # Get the values of the "sort" and "limit" query parameters
    sort_param = request.args.get("sort")
    limit_param = request.args.get("limit")

    # Load the high scores from the file, sorting in descending order if requested
    if sort_param == "desc":
        high_scores = load_high_scores(reverse=True)
    else:
        high_scores = load_high_scores()

    # Check if limit parameter is provided and valid
    if limit_param and limit_param.isdigit():
        limit = int(limit_param)
    else:
        limit = None

    # Apply the limit if provided
    if limit:
        high_scores = high_scores[:limit]

    # Return the high scores in JSON format
    return jsonify(high_scores)

@app.route('/highscores/<int:id>', methods=['GET'])
def get_high_score(id):
    # Load the high scores from the file
    high_scores = load_high_scores()

    # Search for the high score with the specified ID
    for score in high_scores:
        if score['id'] == id:
            # Return the high score in JSON format
            return jsonify(score)

    # If the high score with the specified ID doesn't exist, return a 404 error
    abort(404)

@app.route('/highscores', methods=['POST'])
def add_high_score():
    # Get the name and time from the request body
    name = request.json.get('name')
    time = request.json.get('time')
    # Load the existing high scores from the file
    high_scores = load_high_scores()
    # Add the new high score to the existing scores
    high_scores.append({'name': name, 'time': time})
    # Sort the high scores by time in ascending order
    high_scores = sorted(high_scores, key=lambda x: x["time"])
    # Truncate the list to the top 50 high scores
    high_scores = high_scores[:50]
    # Assign IDs to the high scores
    for i, score in enumerate(high_scores):
        score['id'] = i + 1
    # Save the updated high scores to the file with newlines
    with open(high_scores_file, 'w') as f:
        for score in high_scores:
            json.dump(score, f)
            f.write('\n')

    return jsonify({'id': high_scores[-1]['id']})

@app.route('/highscores/<int:id>', methods=['DELETE'])
def delete_high_score(id):
    # Load the list of high scores from the JSON file
    high_scores = load_high_scores()

    # Check if the specified ID exists in the list of high scores
    if any(score['id'] == id for score in high_scores):
        # Remove the high score with the specified ID from the list
        high_scores = [score for score in high_scores if score['id'] != id]

        # Write the updated list of high scores back to the JSON file
        try:
            with open(high_scores_file, 'w') as f:
                json.dump(high_scores, f)
        except Exception as e:
            # If there is an error writing to the file, return a 500 Internal Server Error
            print(e)
            abort(500)

        # Return a successful response with a 204 No Content status code
        return make_response("", 204)
    else:
        # If the specified ID does not exist in the list of high scores, return a 404 Not Found error
        abort(404)

@app.route('/')
def display_high_scores():
    # Load the high scores from the high_scores_file
    sorted_scores = load_high_scores()
    # Check if there are any high scores
    # If there are no high scores, return a 404 error
    if not sorted_scores:
        abort(404)

    high_scores_sorted = [(score['id'], score['name'], timedelta(seconds=int(score['time'].split(':')[1]))) for score in sorted_scores]

    # Format the time and append each score to a new list
    high_scores_formatted = []
    for score in high_scores_sorted:
        if score[2] < timedelta(seconds=60):
            formatted_time = str(score[2].seconds) + "sec"
        else:
            formatted_time = str(score[2].minutes) + "min " + str(score[2].seconds % 60) + "sec"
        high_scores_formatted.append((score[0], score[1], formatted_time))

    # Pass the high_scores_formatted variable to the render_template function
    # This function generates an HTML page using the high_scores.html template and the high_scores_formatted data
    return render_template('high_scores.html', high_scores=high_scores_formatted)

if __name__ == '__main__':
    app.run()