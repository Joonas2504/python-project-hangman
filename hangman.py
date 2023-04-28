"""
Hangman game module.

This module contains functions to run a command-line implementation of the Hangman game,
including starting a new game, getting user input, checking user guesses, and displaying
game information.

"""
import random
import time
import requests
import re
from datetime import timedelta
import os
import json

def main():
    """
    Displays a menu for the user to choose between playing the game, displaying high scores, or exiting the program.

    """
    exit_menu = False

    while not exit_menu:
        print(f"Welcome to play Hangman: Animal Edition" "\n" "1) Play game" "\n" "2) Display high scores" "\n" "3) Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            hangman()
        elif choice == "2":
            high_scores()
        elif choice == "3":
            exit_menu = True
        else:
            print("Invalid input. Please enter a valid choice.")

def hangman():
    """
    Executes the Hangman game.

    The player is prompted to guess a letter to determine a word. If the letter is in the word, the letter is revealed in
    the word. If the letter is not in the word, a part of the hangman is drawn on the screen. The game ends when the player
    has guessed three words, or the hangman has been fully drawn.

    """
    # Select three random words from the list
    words = random.sample(words_to_list(), 3)

    # Initialize game state variables
    guessed_letters = set()
    incorrect_guesses = 0
    max_guesses = 6
    start_time = time.time()
    end_time = None
    word_display = "-" * len(words[0])
    guesses_remaining = max_guesses - incorrect_guesses
    rounds = 1

    # Game loop
    while rounds <= 3:
        secret_word = words[rounds - 1]
        game_over = False  # reset game_over variable
        print(f"\nRound {rounds}")
        while not game_over:  # keep playing until the game is over
            draw_gallow(incorrect_guesses)
            print_game_state(word_display, guesses_remaining)  # display the current game state
            guess = input("Guess a letter: ").upper()  # get user input for a guess and convert to uppercase
            if not is_valid_guess(guess, guessed_letters):  # if the guess is invalid, skip to the next iteration of the loop
                continue
            if guess not in secret_word:
                incorrect_guesses += 1
                guesses_remaining = max_guesses - incorrect_guesses  # update the number of remaining guesses
                if incorrect_guesses == max_guesses: # Checks if the number of incorrect guesses equals the maximum number of allowed guesses.
                    draw_gallow(incorrect_guesses) # Displays the final state of the hangman figure based on the number of incorrect guesses the player made.
                    print_game_state(secret_word, guesses_remaining) #Displays the secret word and the number of remaining guesses the player had when they lost the game.
                    print("\nGame over! You ran out of guesses.")
                    print("Returning to main menu...\n")
                    time.sleep(2)
                    return # Ends the hangman function and returns control back to the main program.
            word_display = update_word_display(guess, secret_word, word_display)  # update the word display to show the guessed letter(s)
            guessed_letters.add(guess) # add guessed letter to guessed_letters set
            game_over = is_game_over(secret_word, word_display, incorrect_guesses, max_guesses, start_time)  # check if the game is over
            
        rounds += 1
        if rounds > 3:  # if all rounds have been completed, break out of the game loop
            end_time = time.time()
            total_time = int(end_time - start_time)
            print(f"\nCongratulations! You completed all three rounds.")
            player_name = input("Enter your name: ") # Prompt the player to enter their name
            is_name(player_name)
            send_highscore(player_name, total_time)
            print("Returning to main menu...\n")
            time.sleep(2)
            return
        word_display = "-" * len(words[rounds - 1])
        guessed_letters.clear()
        incorrect_guesses = 0

def words_to_list():
    """
    This function reads words from a text file and returns a list of the words.

    Returns:
        list: A list of words read from the file.

    """
    # Open the "words.txt" file and read the lines into a list
    with open("words.txt", "r") as f:
        words = [line.strip() for line in f]
    # Return the list of words
    return words

def is_valid_guess(guess, guessed_letters):
    """
    Checks if the user's guess is a valid guess.

    Args:
        guess (str): A string representing the user's guess.
        guessed_letters (set): A set containing all the letters the user has guessed so far.

    Returns:
        bool: Returns True if the guess is valid, otherwise False.

    """
    # Check if the guess is valid
    if guess is None or len(guess) != 1 or not guess.isalpha(): # Check if guess is a single alphabetic character
        print("Invalid guess. Please enter a single letter.")
        return False
    if guess in guessed_letters: # Check if guess has already been guessed
        print("You've already guessed that letter. Try again.")
        return False
    return True
    
def update_word_display(guess, secret_word, word_display):
    """
    This function takes three arguments, guess (a string), secret_word (a string), and word_display (a string).

    The function updates word_display to show the guessed letter(s) by iterating over the characters in secret_word, and checking if each character is equal to guess, a space, or a hyphen. 
    If the character is equal to guess, word_display is updated to reveal the guessed letter. If the character is a space or a hyphen, word_display is updated to reveal the space or hyphen.

    Returns:
        The updated word_display string.

    """
    # Update word_display to show the guessed letter(s)
    for i in range(len(secret_word)):
        if secret_word[i] == guess:  # if the guessed letter is found in the secret word
            # update word_display to reveal the guessed letter
            word_display = word_display[:i] + guess + word_display[i+1:]
        elif secret_word[i] == " ":  # if the current character in secret_word is a space
            # update word_display to reveal the space
            word_display = word_display[:i] + " " + word_display[i+1:]
        elif secret_word[i] == "-":  # if the current character in secret_word is a hyphen
            # update word_display to reveal the space
            word_display = word_display[:i] + "-" + word_display[i+1:]
    return word_display

def update_game_state(guess, secret_word, guessed_letters, incorrect_guesses):
    """
    Updates the game state by adding the guessed letter to the guessed_letters set and incrementing the 
    incorrect_guesses count if the guess is not in the secret_word.

    Args:
        guess (str): The letter that the player has guessed.
        secret_word (str): The word that the player is trying to guess.
        guessed_letters (set): A set of letters that the player has already guessed.
        incorrect_guesses (int): The number of incorrect guesses the player has made so far.

    Returns:
        tuple: A tuple containing the updated guessed_letters set and incorrect_guesses count.

    """
    # Add guessed letter to guessed_letters set
    guessed_letters.add(guess)
    # Increment incorrect_guesses count if guess is not in secret_word
    if guess not in secret_word:
        incorrect_guesses += 1
        draw_gallow(incorrect_guesses)
    # Return updated guessed_letters set and incorrect_guesses count
    return guessed_letters, incorrect_guesses

def is_game_over(secret_word, word_display, incorrect_guesses, max_guesses, start_time):
    """
    Check if the game is over by either checking if the player has exceeded the maximum number of guesses
    or if the player has successfully guessed the word.

    Args:
        secret_word (str): The word to be guessed by the player.
        word_display (str): The current state of the word display.
        incorrect_guesses (int): The number of incorrect guesses made by the player.
        max_guesses (int): The maximum number of guesses allowed for the player.
        start_time (float): The start time of the game.

    Returns:
        bool: Returns True if the game is over, otherwise returns False.

    """
    if incorrect_guesses >= max_guesses:
        print("Game over! You ran out of guesses.")
        return True
    elif "-" not in word_display:
        end_time = time.time()
        total_time = int(end_time - start_time)
        print(f"Congratulations! You guessed the word '{secret_word}' in {total_time} seconds.")
        return True
    else:
        return False

def print_game_state(word_display, guesses_remaining):
    """
    Prints the current game state to the console, including the word display and number of guesses remaining.

    Args:
        word_display (str): The current state of the word display, with correctly guessed letters filled in and unknown letters represented by hyphens.
        guesses_remaining (int): The number of guesses remaining before the game ends.

    """
    # Print the current game state, including the word display and number of guesses remaining.
    print(f"\nWord: {word_display}")
    print(f"Guesses remaining: {guesses_remaining}")

def draw_gallow(num_wrong_guesses):
    """
    Draw the gallow based on the number of wrong guesses made so far.

    """
    if num_wrong_guesses == 0:
        print("""  _______
 |       |
 |
 |
 |
 |
_|___""")
    elif num_wrong_guesses == 1:
        print("""  _______
 |       |
 |       O
 |
 |
 |
_|___""")
    elif num_wrong_guesses == 2:
        print("""  _______
 |       |
 |       O
 |       |
 |
 |
_|___""")
    elif num_wrong_guesses == 3:
        print("""  _______
 |       |
 |       O
 |      /|
 |
 |
_|___""")
    elif num_wrong_guesses == 4:
        print("""  _______
 |       |
 |       O
 |      /|\\
 |
 |
_|___""")
    elif num_wrong_guesses == 5:
        print("""  _______
 |       |
 |       O
 |      /|\\
 |      /
 |
_|___""")
    else:
        print("""  _______
 |       |
 |       O
 |      /|\\
 |      / \\
 |
_|___""")

def is_name(name):
    """
    Check if a given name is valid.
    The name is considered valid if it is a string with length between 2 and 20 characters and contains only
    alphanumeric characters, underscores (_), hyphens (-), or special characters (!, @, #, $, %, ^, &, *).

    Args:
        name (str): The name to be checked.

    Returns:
        str: The name if it is valid.
        False: If the name is not valid.

    """
    # Regular expression to check if name is valid
    regex = r'^[a-zA-Z0-9_-]{2,20}$|^[a-zA-Z0-9_!@-]{2,20}$'
    if re.match(regex, name):
        return name
    return False

# Function to send a high score to the server
def send_highscore(name, time):
    """
    Sends the user's high score to the high score API endpoint and updates the local high score file.

    Args:
        name (str): The name of the player.
        time (float): The time it took the player to guess the word.

    """
    # Check if the high_scores.json file exists, if not create an empty file
    if not os.path.exists('high_scores.json'):
        with open('high_scores.json', 'w') as f:
            json.dump([], f)
    
    # Convert time to an integer
    time_in_seconds = int(time)
    # Convert seconds to minutes and seconds
    minutes, seconds = divmod(time_in_seconds, 60)
    # Format the time string as "MM:SS"
    time_str = f"{minutes:02d}:{seconds:02d}"
    # Set the URL for the high score API endpoint
    url = 'https://python-project-hangman-46b9.onrender.com/highscores?password=hirttoukko'
    # Create a dictionary containing the name and time data
    data = {'name': name, 'time': time_str}

    # If the high scores file doesn't exist, create an empty list
    if not os.path.isfile('high_scores.json'):
        high_scores = []
    else:
        # Otherwise, load the existing high scores from the file
        with open('high_scores.json', 'r') as f:
            high_scores = json.load(f)

    # Add the new high score to the list
    high_scores.append(data)
    # Sort the high scores by time (in ascending order)
    high_scores = sorted(high_scores, key=lambda x: x['time'])
    # Limit the number of high scores to 50
    high_scores = high_scores[:50]
    # Assign IDs to the high scores
    for i, score in enumerate(high_scores):
        score['id'] = i + 1

    # Write the high scores to the JSON file
    with open('high_scores.json', 'w') as f:
        json.dump(high_scores, f, indent=4)

    # Send a POST request to the server with the high score data
    response = requests.post(url, json=data)
    # Check the response status code to see if the high score was successfully sent
    if response.status_code == 200:
        print('High score sent successfully!')
    else:
        print(f'Error sending high score: {response.content}')

def high_scores():
    """
    This function retrieves the high scores from an API endpoint and provides the user with a menu to display the scores.
    
    """
    while True:
        # Send a GET request to the high scores API endpoint
        response = requests.get('https://python-project-hangman-46b9.onrender.com/highscores?password=hirttoukko')
        # Parse the JSON response into a Python list
        highscores = response.json()

        # Display the high scores according to user's choice
        print("1) Display all scores")
        print("2) Display scores in descending order")
        print("3) Display score by ID")
        print("4) Display top scores")
        print("5) Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            display_all_scores(highscores)
        elif choice == "2":
            display_scores_descending(highscores)
        elif choice == "3":
            display_score_by_id(highscores)
        elif choice == "4":
            display_top_scores(highscores)
        elif choice == "5":
            break
        else:
            print("Invalid input. Please enter a valid choice.")

def display_all_scores(highscores):
    """
    Displays all high scores in the console.

    Args:
        highscores (list): A list containing highscores in JSON format

    """
    # Display all high scores in the console
    print("High Scores:")
    for score in highscores:
        id = score['id']
        name = score['name']
        time_parts = score['time'].split(':')
        time = int(time_parts[0]) * 60 + int(time_parts[1])
        if time >= 60:
            minutes = time // 60
            seconds = time % 60
            print(f"{id}: {minutes}min {seconds}sec, {name}")
        else:
            print(f"{id}: {time}sec, {name}")

def display_scores_descending(highscores):
    """
    display_all_scores(highscores)

    Displays all high scores in descending order in the console.

    Args:
        highscores (list): A list containing highscores in JSON format

    """
    # Display high scores in descending order in the console
    sorted_scores = sorted(highscores, key=lambda score: int(score['time'].replace(':', '')), reverse=True)
    print("High Scores (descending order):")
    for score in sorted_scores:
        id = score['id']
        name = score['name']
        time_parts = score['time'].split(':')
        time = int(time_parts[0]) * 60 + int(time_parts[1])
        if time >= 60:
            minutes = time // 60
            seconds = time % 60
            print(f"{id}: {minutes}min {seconds}sec, {name}")
        else:
            print(f"{id}: {time}sec, {name}")

# Display a high score by ID in the console
def display_score_by_id(highscores):
    """
    Display a high score by ID in the console
    
    Args:
        highscores (list): A list containing highscores in JSON format
    
    """
    while True:
        score_id = input("Enter the score ID: ")
        if not score_id.isdigit():
            print("Invalid input. Please enter a positive integer")
        else:
            score_id = int(score_id)
            break
    for score in highscores:
        if score['id'] == score_id:
            name = score['name']
            time_parts = score['time'].split(':')
            time = int(time_parts[0]) * 60 + int(time_parts[1])
            if time >= 60:
                minutes = time // 60
                seconds = time % 60
                print(f"{minutes}min {seconds}sec, {name}, ID: {score['id']}")
            else:
                print(f"{time}sec, {name}, ID: {score['id']}")
            return

    print("Score not found.")

# Display top high scores in the console
def display_top_scores(highscores):
    """
    Displays top high scores in the console
    
    Args:
        highscores (list): A list containing highscores in JSON format
    
    """
    while True:
        n = input("Enter the number of top scores to display: ")
        if n.isdigit():
            n = int(n)
            break
        else:
            print("Invalid input. Please enter a positive integer.")

    # If there are fewer than n high scores, display a message indicating this
    if len(highscores) < n:
        print(f"There are only {len(highscores)} high scores to display.")

    else:
        # Sort the high scores by time in ascending order
        highscores.sort(key=lambda score: score['time'])

        # Display the top n high scores in the console
        print(f"Top {n} High Scores:")
        for i, score in enumerate(highscores[:n]):
            id = score['id']
            name = score['name']
            time_parts = score['time'].split(':')
            time = int(time_parts[0]) * 60 + int(time_parts[1])
            if time >= 60:
                minutes = time // 60
                seconds = time % 60
                print(f"{i+1}. {id}: {minutes}min {seconds}sec, {name}")
            else:
                print(f"{i+1}. {id}: {time}sec, {name}")

if __name__ == '__main__':
    main()
