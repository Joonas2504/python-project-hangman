from flask import Flask, request, jsonify, render_template, abort, make_response
import json
from datetime import timedelta
import os
import password_store
import bcrypt

app = Flask(__name__)

# Define the path to the high scores file
high_scores_file = "high_scores.json"

def load_high_scores(reverse=False):
    # Check if the high scores file exists
    if not os.path.exists('high_scores.json'):
        with open('high_scores.json', 'w') as f:
            json.dump([], f)

    # Load the existing high scores from the file and sort them
    with open('high_scores.json', 'r') as f:
        high_scores = json.load(f)
        high_scores.sort(key=lambda score: score['time'], reverse=reverse)

    return high_scores


def hash_password(password):
    # Generate a salt for the password
    salt = bcrypt.gensalt()
    # Hash the password using the salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Return the hashed password and the salt
    return hashed_password, salt

def verify_password(password, salt, hashed_password):
    # Hash the password using the salt
    secret_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Compare the hashed input password to the hashed password
    return secret_password == hashed_password


@app.route('/highscores', methods=['GET'])
def get_high_scores():
    password = request.args.get("password") # Get the password from the query parameters
    # Check if the provided password matches the pre-defined password
    if password != password_store.password:
        return jsonify({"error": "Invalid password"}), 401 # Return an error response with status code 401 (Unauthorized)

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
    password = request.args.get("password") # Get the password from the query parameters
    # Check if the provided password matches the pre-defined password
    if password != password_store.password:
        return jsonify({"error": "Invalid password"}), 401 # Return an error response with status code 401 (Unauthorized)
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
    password = request.args.get("password") # Get the password from the query parameters
    # Check if the provided password matches the pre-defined password
    if password != password_store.password:
        return jsonify({"error": "Invalid password"}), 401 # Return an error response with status code 401 (Unauthorized)
    # Load the existing high scores from the file
    high_scores = load_high_scores()
    # Get the name and time from the request body
    name = request.json.get('name')
    time = request.json.get('time')
    # Add the new high score to the existing scores
    high_scores.append({'name': name, 'time': time})
    # Sort the high scores by time in ascending order
    high_scores = sorted(high_scores, key=lambda x: x["time"])
    # Truncate the list to the top 50 high scores
    high_scores = high_scores[:50]
    # Assign IDs to the high scores
    for i, score in enumerate(high_scores):
        score['id'] = i + 1

    # Save the updated high scores to the local file
    with open('high_scores.json', "w") as f:
        json.dump(high_scores, f)

    # Send the response to the client
    return jsonify({'id': high_scores[-1]['id']})


@app.route('/highscores/<int:id>', methods=['DELETE'])
def delete_high_score(id):
    password = request.args.get("password") # Get the password from the query parameters
    # Check if the provided password matches the pre-defined password
    if password != password_store.password:
        return jsonify({"error": "Invalid password"}), 401 # Return an error response with status code 401 (Unauthorized)

    # Load the list of high scores from the JSON file
    high_scores = load_high_scores()

    # Find the index of the high score with the specified ID
    index = next((i for i, score in enumerate(high_scores) if score['id'] == id), None)

    if index is not None:
        # Remove the high score with the specified ID
        del high_scores[index]

        # Write the updated list of high scores back to the JSON file
        try:
            with open('high_scores.json', 'w') as f:
                json.dump(high_scores, f, indent=4)
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
    password = request.args.get("password") # Get the password from the query parameters
    # Check if the provided password matches the pre-defined password
    if password != password_store.password:
        return jsonify({"error": "Invalid password"}), 401 # Return an error response with status code 401 (Unauthorized)
    # Load the high scores from the high_scores_file
    sorted_scores = load_high_scores()
    # Check if there are any high scores
    # If there are no high scores, return empty list
    if not sorted_scores:
        high_scores_formatted = []

    high_scores_sorted = [(score['id'], score['name'], score['time']) for score in sorted_scores]

    # Format the time and append each score to a new list
    high_scores_formatted = []
    for score in high_scores_sorted:
        formatted_time = score[2]
        if len(formatted_time) == 4:
            formatted_time = "0" + formatted_time
        high_scores_formatted.append((score[0], score[1], formatted_time))

    # Pass the high_scores_formatted variable to the render_template function
    # This function generates an HTML page using the high_scores.html template and the high_scores_formatted data
    return render_template('high_scores.html', high_scores=high_scores_formatted)


if __name__ == '__main__':
    app.run()