"""
Nazar Shukhardin
1/7/2026

This is a simple recreation of the game Minesweeper. The board is displayed in the terminal, and you pick the coordinates in the terminal.
To display colors, ANSI codes are used.

One thing that surprised me while making this is how powerful ANSI codes are. Not only can you change the colors of the text, but you can also use effects, like blink.
Some challenges I faced were indexing the board array when checking for mines around the cell, for example, but after some debugging, I solved it.
I coded this on my own, with a bit of Google help for ANSI codes.
I feel proud of my project; I didn't use any AI, which is kind of rare today. 
If I had more time to work on this project, I would probably add a better way for input, because entering coordinates manually kind of sucks.
"""

# imports
import random
import os
import time
import json
from hashlib import sha256

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

# game parameters, constant
board_size = 8
mine_count = 10

# Array of arrays representing each cell on the board
board = []

# If set to true, when the player finishes their move game ends
game_over = False

# Total move count, increments after player finishes their move
moves = 0

# Start time to record total time
start_time = time.perf_counter()

# Logged in user data
logged_in_user = None
logged_in_highscore = None

def calculate_score(board_size, mines, time_seconds):
    """
    Calculate a score for the highscore.
    
    args:
        board_size - int, board size
        mines - int, number of mines
        time_seconds - float, the time elapsed
        
    returns:
        int - The final calculated score.
    """

    # make sure the time is atleast 1 second
    time_seconds = max(time_seconds, 1)
    
    # calculate the area of the board
    area = board_size * board_size
    
    # how difficult the board was depending on the mines and area
    difficulty_factor = (mines ** 2) / area
    
    # how fast the user cleared the board
    safe_tiles = area - mines
    efficiency_factor = safe_tiles / time_seconds
    
    # combine both factors and multiply by 1000 for precision
    final_score = difficulty_factor * efficiency_factor * 1000
    
    return int(final_score)

def is_in_bounds(x, y):
    """
    Check if the coordinate is on the board

    args:
        x - int, x coordinate
        y - int, y coordinate
    returns:
        bool - true if coordinate is in bounds, false if not
    """
    
    return (x >= 0 and x < board_size) and (y >= 0 and y < board_size)

def get_space():
    """
    Returns a string of spaces based on the board size. Used to equally separate the cells when displaying the board.

    returns:
        space - string of spaces
    """

    space = ""

    for i in range(board_size // 2):
        space += " "
    return space

def generate_board():
    """
    Fill the board with cells. SHOULD ONLY BE USED ONCE, OR IF THE BOARD IS EMPTY.
    """

    for row in range(board_size):
        # create an empty column
        current_column = []

        for column in range(board_size):
            # add a clear cell
            current_column.append({
                "has":"nothing",
                "revealed": False,
                "flagged": False
            })
        # add the column to the board
        board.append(current_column)

def is_next_to(x1, y1, x2, y2, radius=1):
    """
    Checks if a coordinate is right next to another coordinate

    args:
        x1 - int, x of the first coordinate
        y1 - int, y of the first coordinate
        x2 - int, x of the second coordinate
        y2 - int, y of the second coordinate
        radius - int, radius to check around
    
    returns:
        bool
    """
    
    # check x
    for x in range(-radius, radius + 1):
        # check y
        for y in range(-radius, radius + 1):

            # skip the middle cell
            if x == 0 and y == 0:
                continue
            
            # check surrounding cells
            if x1 + x == x2 and y1 + y == y2:
                return True
    
    # default case if not found
    return False

def fill_mines(ignore_x = -1, ignore_y = -1):
    """
    Fill the board with mines, but make sure to not fill around a specified area.
    
    args:
        ignore_x - integer, the x coordinate of no fill area
        ignore_y - integer, the x coordinate of no fill area
    """


    for i in range(mine_count):

        # generate initial random coordinates
        random_x = random.randrange(0, board_size)
        random_y = random.randrange(0, board_size)

        # keep regenerating coordinates until all conditions are met
        # the mines shouldn't be next to the ignore position in 2 cell radius 
        while (ignore_x == random_x and ignore_y == random_y) or is_next_to(ignore_x,ignore_y,random_x,random_y, radius=2) or board[random_y][random_x]["has"] == "mine":
            random_x = random.randrange(0, board_size)
            random_y = random.randrange(0, board_size)
        
        # set the final chosen coordinate to be a mine
        board[random_y][random_x]["has"] = "mine"

def get_color_by_number(num):
    """
    Returns an ANSI color code based on the given number of mines. Colors are taken from the Windows XP Minesweeper.

    args:
        num - integer, number of mines around a cell
    
    returns:
        ANSI color based on the mines
    """

    if num == 1:
        return "\033[94m" # blue
    elif num == 2:
        return "\033[32m" # green
    elif num == 3:
        return "\033[91m" # red
    elif num == 4:
        return "\033[34m" # dark blue
    elif num == 5:
        return "\033[35m" # dark red
    elif num == 6:
        return "\033[96m" # cyan
    elif num == 7:
        return "\033[37m" # dark
    elif num == 8:
        return "\033[90m" # gray
    else:
        return "\033[95m" # any other number will be very pink (shouldn't normally happen in the game)

def get_mines_around(column_idx, row_idx):
    """
    Get the number of mines around a cell

    args:
        column_idx - int, Y coordinate of the cell
        row_idx - int, X coordinate of the cell
    
    returns:
        mines_around - Amount of mines around the cell
    """
    row = board[row_idx]
    column = row[column_idx]
    mines_around = 0

    # for surrounding x
    for x in [-1, 0, 1]:
        # for surrounding y
        for y in [-1, 0, 1]:
            # make sure the coordinate is on the board
            if not is_in_bounds(row_idx + x, column_idx + y):
                continue
            # skip the middle cell
            if x == 0 and y == 0:
                continue
            
            # check if the coordinate has a mine
            if board[row_idx + x][column_idx + y]["has"] == "mine":
                mines_around += 1

    return mines_around

def display_board(reveal = False, highlight_x=-1,highlight_y=-1):
    """
    Shows the board on the screen. Every cell can be revealed. One cell can be highlighted

    args:
        reveal - optional bool, if True, every non-mine cell will show the number of mines around it, and all mines will be shown
        highlight_x - optional int, only works if highlight_y is also set. Highlights the cell at the given coordinate.
        highlight_y - optional int, only works if highlight_x is also set. Highlights the cell at the given coordinate.
    """

    # print the numbers in the top
    print("\033[8m00\033[0m", end=" ")
    for i in range(board_size):
        print(ALPHABET[i], end=get_space())
    print("\n", end="")

    # for each row (Y)
    for row_idx in range(len(board)):
        row = board[row_idx]
        
        # print the numbers on the sides
        displayed_number = row_idx + 1
        print(f"{displayed_number:02d}", end=" ")

        # for each column (X)
        for column_idx in range(len(row)):
            column = row[column_idx]

            # Non mine cells display logic
            if column["revealed"] == True or (reveal == True and not column["has"] == "mine"):
                # Get the amount of mines around the cell
                mines_around = get_mines_around(column_idx, row_idx)

                # Show the mines around if there are any
                if mines_around > 0:
                    print(get_color_by_number(mines_around) + str(mines_around) + "\033[0m", end=get_space())
                else:
                    print("\033[90m.\033[0m", end=get_space())

            # Mark the mines with an X when the whole board is revealed
            elif column["has"] == "mine" and reveal:
                print("X", end=get_space())
            
            # Show flagged mines with an F
            elif column["flagged"]:
                # Highlight
                if highlight_x == column_idx and highlight_y == row_idx:
                    print("\033[91;40;6mF\033[0m", end=get_space())
                else:
                    print("\033[90mF\033[0m", end=get_space())
            
            # Show unopened cells
            else:
                # Highlight
                if highlight_x == column_idx and highlight_y == row_idx:
                    print("\033[91;40;6m■\033[0m", end=get_space())
                else:
                    print("\033[90m■\033[0m", end=get_space())
        print("\n")

def get_input():
    """
    Let the user pick a coordinate and open or flag a cell. If the user opens a mine, game_over is set to true.

    returns
        tuple (int, int) the coordinates that user picked
    """
    # set default choice
    x = -1
    y = -1
    
    global moves

    while True:
        user_input = input("Enter the coordinates for the next move (eg: f7): ").strip()
        user_input = user_input.split(" ")

        # Get the coordinates
        x = None
        y = None

        # parse the user input (first character should be a letter and second is a number)
        try:
            x = ALPHABET.index(user_input[0][0])
            y = int(user_input[0][1]) - 1
        except:
            # do it again until input is valid
            continue

        # check if the user coordinates are on the board
        if not is_in_bounds(x, y):
            clear_screen()
            print_info()
            display_board()
            print("invalid coordinates")
            continue
        
        # loop until action is selected
        while True:
                action = ""
                # If user put an action after the coordinates, skip the second input
                if len(user_input) > 1 and user_input[1] in "open flag":
                    action = user_input[1]
                else:
                    # Ask the user for the action
                    clear_screen()
                    print_info()
                    display_board(highlight_x=x, highlight_y=y)
                    action = input("What do you want to do? (open, flag, cancel): ").lower().strip()
                
                # Reveal the selected cell or blow up D:
                if action == "open":
                    # If the cell has the mine, end the game
                    if board[y][x]["has"] == "mine":
                        global game_over
                        game_over = True
                        break
                    else:
                        # If cell is empty reveal it
                        if moves > 0:
                            flood_open(x, y)
                        board[y][x]["revealed"] = True
                        board[y][x]["flagged"] = False
                        break
                
                # Flag the cell or unflag if it's flagged
                elif action == "flag":
                    if board[y][x]["revealed"] != True:
                        board[y][x]["flagged"] = not board[y][x]["flagged"]
                    break

                # Cancel
                elif action == "cancel":
                    if moves != 0:
                        moves -= 1
                        break
                    else:
                        print("You cannot cancel your first move.")
                else:
                    print("invalid input")
        break
    
    return (x, y)

def print_info():
    """
    Shows how many mines are left, how many moves the user did, and how much time has passed.
    """

    mines_left = 0

    # get the amount of mines left on the board
    for row in board:
        for column in row:
            if column["has"] == "mine":
                mines_left += 1
            if column["flagged"] == True:
                mines_left -= 1
    
    # since there aren't any mines on the first move, set it artificially
    if moves == 0:
        mines_left = mine_count

    # calculate the time passed
    current_time = time.perf_counter()
    elapsed = current_time - start_time

    print(f"{mines_left} Mines left || {moves} Moves || {elapsed:.0f} seconds")

def flood_open(x, y, force_fill=False):
    """
    A recursive function to open all empty cells around a cell.

    args:
        x - int, the x coordinate of the cell
        y - int, the y coordinate of the cell
        force_fill - bool, fill even if the cell is already revealed 
    """

    # check if coordinate is on the board
    if not is_in_bounds(x, y):
        return
    
    # stop if the cell is already revealed. force fill is only used for the first move
    if not force_fill:
        if board[y][x]["revealed"]:
            return

    # reveal the current cell
    board[y][x]["revealed"] = True

    # flood open cells around
    if get_mines_around(x, y) == 0:
        for x_around in [-1, 0, 1]:
            for y_around in [-1, 0, 1]:

                flood_open(x + x_around, y + y_around)

def check_win():
    """
    Check if all the mines have been flagged

    returns:
        bool, True if all mines are flagged
    """

    for row in board:
        for cell in row:
            if cell["has"] == "mine" and not cell["flagged"]:
                return False
    return True

def clear_screen():
    """
    Crossplatform cls
    """

    # if user is on windows
    if os.name == "nt":
        os.system("cls")
    else:
        # any other system uses clear instead of cls
        os.system("clear")

SETTINGS_TEXT = """
   _____      __  __  _                 
  / ___/___  / /_/ /_(_)___  ____ ______
  \__ \/ _ \/ __/ __/ / __ \/ __ `/ ___/
 ___/ /  __/ /_/ /_/ / / / / /_/ (__  ) 
/____/\___/\__/\__/_/_/ /_/\__, /____/  
                          /____/        
"""

def settings_menu():
    """
    Show the setting menu to allow the user to change board size and mine count
    """

    global board_size
    global mine_count
    
    while True:
        # display the settings menu
        clear_screen()
        print(SETTINGS_TEXT)
        print(f"Board size: {board_size}x{board_size}")
        print(f"Mine count: {mine_count}")
        print()
        print("1. Change board size\n2. Change mine count\n3. Go back to main menu")
        
        # take input from user
        choice = input().strip()
        
        # make sure the choice is a number
        if choice.isdigit():
            choice = int(choice)

            # change the board size 
            if choice == 1:
                clear_screen()
                print(f"Board size: {board_size}x{board_size}")
                print(f"Maximum: {len(ALPHABET) - 1}, minimum: 2")
                print()
                
                new_board_size = input("Enter new board size (ex 10): ").strip()
                
                if new_board_size.isdigit():
                    new_board_size = int(new_board_size)
                    if new_board_size > 1 and new_board_size < len(ALPHABET):
                        board_size = new_board_size

            # change the mine count
            elif choice == 2:
                new_mine_count = input("Enter new mine count: ").strip()

                if new_mine_count.isdigit():
                    new_mine_count = int(new_mine_count)
                    if new_mine_count > 0 and new_mine_count < (board_size**2):
                        mine_count = new_mine_count
            
            # exit out of settings
            elif choice == 3:
                break 

TITLE_TEXT = """
    __  ____                                                       __  __                           
   /  |/  (_)___  ___  ______      _____  ___  ____  ___  _____   / / / /___  ____  ____  __________
  / /|_/ / / __ \/ _ \/ ___/ | /| / / _ \/ _ \/ __ \/ _ \/ ___/  / /_/ / __ \/ __ \/ __ \/ ___/ ___/
 / /  / / / / / /  __(__  )| |/ |/ /  __/  __/ /_/ /  __/ /     / __  / /_/ / / / / /_/ / /  (__  ) 
/_/  /_/_/_/ /_/\___/____/ |__/|__/\___/\___/ .___/\___/_/     /_/ /_/\____/_/ /_/\____/_/  /____/  
                                           /_/                                                      
    """
BUTTONS_TEXT = """
                    .-----------------. .----------------. .-------.
                    |1. Start the game| |2. Game Settings| |3. Quit|
                    '-----------------' '----------------' '-------'
    """

def main_menu():
    """
    Display the main menu and wait for input.
    """

    # Show the title and buttons
    clear_screen()
    print(TITLE_TEXT)
    print(f"Welcome back, {logged_in_user}. Your high score is {logged_in_highscore}")
    print(BUTTONS_TEXT)
    
    while True:
        choice = input().strip()
        
        if choice.isdigit():
            choice = int(choice)
            if choice == 1:
                # User chose to start the game, exit out of the loop
                break
            elif choice == 2:
                # User chose to open the settings menu
                settings_menu()
                clear_screen()
                print(TITLE_TEXT)
                print(BUTTONS_TEXT)

            elif choice == 3:
                # User chose to quit
                os.abort()

def password_protect():
    """
    This is a simple account system that stores users in a JSON file. Each user has a password and a high score.
    The password is hashed so you can't just look up someones password easily.
    """

    users = {}
    
    # Load existing users if they exist
    try:
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                users = json.loads(f.read())
    except:
        print("Failed to load accounts from a file, ignoring the file.")
    
    clear_screen()

    global logged_in_user
    global logged_in_highscore

    while True:
        # Ask user if they have an account
        has_account = input("Do you have an account? (Y, n): ").strip().lower()

        # User has an account, log in
        if has_account in ["y", "yes"] or has_account == "":
            # ask for username and password
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            # make sure username and password is not empty
            if not username or not password: continue

            # check if account exists
            if users.get(username) != None:
                # check if password is correct
                if users[username]["password"] == sha256(password.encode()).hexdigest():
                    # set the logged in variables
                    logged_in_user = username
                    logged_in_highscore = users[username]["high_score"]

                    break
                else:
                    print("Incorrect password")
            else:
                print("Account doesn't exist")

        # User doesn't have an account, make a new one
        elif has_account in ["n", "no"]:
            print("Enter the credentials for a new account:")

            # ask for username and password
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            # make sure username and password is not empty
            if not username or not password: continue

            # make a new account in the dictionary
            users[username] = {
                "password": sha256(password.encode()).hexdigest(),
                "high_score": 0
            }

            # set logged in variables
            logged_in_user = username
            logged_in_highscore = 0
            
            # save new dictionary to the file
            with open("users.json", "w") as f:
                f.write(json.dumps(users))
            
            break
        else:
            print("Invalid input")
            continue

def save_high_score(new_score):
    """
    Save a new high score for the user in user.json file
    
    args:
        new_score - int, the new high score to save
    """
    users = {}
    try:
        with open("users.json", "r") as f:
            users = json.loads(f.read())
        
        users[logged_in_user]["high_score"] = new_score
        
        with open("users.json", "w") as f:
            f.write(json.dumps(users))
    except:
        print("Failed to save the new high score.")

# Run the app
if __name__ == '__main__':
    # User login
    password_protect()

    # Wait for user in the main menu
    main_menu()

    # Fill the board once
    generate_board()
    start_time = time.perf_counter()
    # Main loop
    while True:
        # clear the screen
        clear_screen()

        # Display the board and the info
        print_info()
        display_board()

        # User time
        x, y = get_input()
        if moves == 0:
            fill_mines(x,y)
            flood_open(x, y, force_fill=True)

        # Stop the game if a mine has been opened and reveal the board
        if game_over:
            clear_screen()
            display_board(True)
            print("Whoops that was a mine. Game over, thx for playing")
            break

        # Check if the user flagged all the mines and reveal the board
        if check_win():
            clear_screen()
            display_board(True)

            # Calculate total time
            end_time = time.perf_counter()
            elapsed = end_time - start_time

            print(f"You won! Total moves: {moves}, total time: {elapsed:.0f} seconds")

            score = calculate_score(board_size, mine_count, elapsed)
            if score > logged_in_highscore:
                print(f"NEW HIGH SCORE! {score}")
                save_high_score(score)

            break
        
        # User finished a move
        moves += 1
