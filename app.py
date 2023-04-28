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
    """Load and sort the high scores from the 'high_scores.json' file.

    Args:
        reverse (bool, optional): If True, sort the high scores in descending order (highest score first).
            If False, sort the high scores in ascending order (lowest score first). Defaults to False.

    Returns:
        list: A list of high score dictionaries, sorted by score.

    """
    # Check if the high scores file exists
    if not os.path.exists('high_scores.json'):
        with open('high_scores.json', 'w') as f:
            json.dump([], f)

    # Load the existing high scores from the file and sort them
    with open('high_scores.json', 'r') as f:
        high_scores = json.load(f)
        high_scores.sort(key=lambda score: score['time'], reverse=reverse)

    return high_scores


@app.route('/highscores', methods=['GET'])
def get_high_scores():
    """
    This function handles GET requests to retrieve high scores.
    
    The function first checks if the provided password matches the pre-defined password
    by getting the password from the query parameters. If the password is invalid, it returns
    an error response with status code 401 (Unauthorized).
    
    Then, it gets the values of the "sort" and "limit" query parameters.
    The function loads the high scores from the file, sorting in descending order if requested.
    
    If the limit parameter is provided and valid, it applies the limit to the high scores.
    
    Finally, the function returns the high scores in JSON format.
    
    Returns:
        A JSON response containing the high scores.
    """
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

@app.route('/<int:id>', methods=['GET'])
def get_high_score(id):
    """
    Retrieve a specific high score from the high scores file by ID.

    Args:
        id (int): The ID of the high score to retrieve.

    Returns:
        A rendered HTML page containing the high score data.

    Raises:
        404: If the high score with the specified ID is not found in the file.
        401: If the provided password does not match the pre-defined password.
    """
    password = request.args.get("password") # Get the password from the query parameters
    # Check if the provided password matches the pre-defined password
    if password != password_store.password:
        return jsonify({"error": "Invalid password"}), 401 # Return an error response with status code 401 (Unauthorized)
    # Load the high scores from the file
    high_scores = load_high_scores()

    # Search for the high score with the specified ID
    for score in high_scores:
        if score['id'] == id:
            # Return the high score in HTML format
            formatted_time = score['time']
            if len(formatted_time) == 4:
                formatted_time = "0" + formatted_time
            high_score_formatted = [(score['id'], score['name'], formatted_time)]
            return render_template('high_scores.html', high_scores=high_score_formatted)

    # If the high score with the specified ID doesn't exist, return a 404 error
    abort(404)


@app.route('/highscores', methods=['POST'])
def add_high_score():
    """
    Add a new high score to the list of high scores.
    
    Requires a valid password to authenticate the request. Expects a JSON payload with 
    'name' and 'time' fields representing the name of the player and their score, respectively. 

    Request Parameters:
        password: str - A password to authenticate the request.

    JSON Payload:
        name: str - The name of the player.
        time: float - The time in seconds for the high score.

    Returns:
        JSON response with the ID of the added high score.
    """
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
    """
    Deletes a high score with the specified ID.

    Args:
        id (int): The ID of the high score to be deleted.

    Returns:
        Response: A 204 No Content response if the high score is successfully deleted.

    Raises:
        HTTPException: A 401 Unauthorized error if the provided password is incorrect.
        HTTPException: A 404 Not Found error if the specified ID does not exist in the list of high scores.
    """
    password = request.args.get("password") # Get the password from the query parameters
    # Check if the provided password matches the pre-defined password
    if password != password_store.password:
        return jsonify({"error": "Invalid password"}), 401 # Return an error response with status code 401 (Unauthorized)

    # Load the list of high scores from the JSON file
    with open('high_scores.json', 'r') as f:
        high_scores = json.load(f)

    # Find the index of the high score with the specified ID
    index = next((i for i, score in enumerate(high_scores) if score['id'] == id), None)

    if index is not None:
        # Remove the high score with the specified ID
        del high_scores[index]

        # Write the updated list of high scores back to the JSON file
        with open('high_scores.json', 'w') as f:
            json.dump(high_scores, f, indent=4)

        # Return a successful response with a 204 No Content status code
        return make_response("", 204)
    else:
        # If the specified ID does not exist in the list of high scores, return a 404 Not Found error
        abort(404)

@app.route('/', methods=['GET'])
def display_high_scores():
    """
    Display the high scores on an HTML page, with a password protection mechanism.

    Returns:
        str: The rendered HTML page with the high scores.

    Raises:
        HTTPException: A 401 Unauthorized error if the provided password is incorrect.
    """

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

    # Get the values of the "sort" and "limit" query parameters
    sort_param = request.args.get("sort")
    limit_param = request.args.get("limit")
    
    # Sort the high scores in descending order if requested
    if sort_param == "desc":
        sorted_scores = sorted(sorted_scores, key=lambda x: x['time'], reverse=True)

    # Check if limit parameter is provided and valid
    if limit_param and limit_param.isdigit():
        limit = int(limit_param)
    else:
        limit = None

    # Apply the limit if provided
    if limit:
        sorted_scores = sorted_scores[:limit]

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