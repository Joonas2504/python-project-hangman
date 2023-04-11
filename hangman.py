import random
import time
import requests
import re
from datetime import timedelta

def main():
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
    # Open the "words.txt" file and read the lines into a list
    with open("words.txt", "r") as f:
        words = [line.strip() for line in f]
    # Return the list of words
    return words

def is_valid_guess(guess, guessed_letters):
    # Check if the guess is valid
    if len(guess) != 1 or not guess.isalpha(): # Check if guess is a single alphabetic character
        print("Invalid guess. Please enter a single letter.")
        return False
    if guess in guessed_letters: # Check if guess has already been guessed
        print("You've already guessed that letter. Try again.")
        return False
    return True

def update_word_display(guess, secret_word, word_display):
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
    # Add guessed letter to guessed_letters set
    guessed_letters.add(guess)
    # Increment incorrect_guesses count if guess is not in secret_word
    if guess not in secret_word:
        incorrect_guesses += 1
        draw_gallow(incorrect_guesses)
    # Return updated guessed_letters set and incorrect_guesses count
    return guessed_letters, incorrect_guesses

def is_game_over(secret_word, word_display, incorrect_guesses, max_guesses, start_time):
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
    if not type(name) is str:
        raise TypeError("Only strings are allowed")

    name_regex = "[A-ZÖÄÅ][a-zäöå]+"
    name_with_dashes_regex = "[A-ZÖÄÅ][a-zäöå]+\-[A-ZÖÄÅ][a-zäöå]+"
    regex = f"^({name_regex}|{name_with_dashes_regex}) ({name_regex}|{name_with_dashes_regex})$"
    if re.match(regex, name):
        return name
    return False

# Function to send a high score to the server
def send_highscore(name, time):
    # Convert time to an integer
    time_in_seconds = int(time)
    # Convert seconds to minutes and seconds
    minutes, seconds = divmod(time_in_seconds, 60)
    # Format the time string as "MM:SS"
    time_str = f"{minutes:02d}:{seconds:02d}"
    # Set the URL for the high score API endpoint
    url = 'http://localhost:5000/highscores'
    # Create a dictionary containing the name and time data
    data = {'name': name, 'time': time_str}
    # Send a POST request to the server with the high score data
    response = requests.post(url, json=data)
    # Check the response status code to see if the high score was successfully sent
    if response.status_code == 200:
        print('High score sent successfully!')
    else:
        print(f'Error sending high score: {response.content}')

def high_scores():
    # Send a GET request to the high scores API endpoint
    response = requests.get('http://localhost:5000/highscores')
    # Parse the JSON response into a Python list
    highscores = response.json()
    # Display the high scores in the console
    print("High Scores:")
    for score in highscores:
        name = score['name']
        time = int(score['time'])
        if time >= 60:
            minutes = time // 60
            seconds = time % 60
            print(f"{minutes}min {seconds}sec, {name}")
        else:
            print(f"{time}sec, {name}")

main()