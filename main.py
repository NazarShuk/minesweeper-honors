"""
Nazar Shukhardin
12/19

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

# game parameters, constant
BOARD_SIZE = 8
MINE_COUNT = 10

# Array of arrays representing each cell on the board
board = []

# If set to true, when the player finishes their move game ends
game_over = False

# Total move count, increments after player finishes their move
moves = 0

# Start time to record total time
start_time = time.perf_counter()

def is_in_bounds(x, y):
    """
    Check if the coordinate is on the board

    args:
        x - int, x coordinate
        y - int, y coordinate
    returns:
        bool - true if coordinate is in bounds, false if not
    """
    return (x >= 0 and x < BOARD_SIZE) and (y >= 0 and y < BOARD_SIZE)

def get_space():
    """
    Returns a string of spaces based on the board size. Used to equally separate the cells when displaying the board.

    returns:
        space - string of spaces
    """
    space = ""
    for i in range(BOARD_SIZE // 2):
        space += " "
    return space

def generate_board():
    """
    Fill the board with cells. SHOULD ONLY BE USED ONCE, OR IF THE BOARD IS EMPTY.
    """
    for row in range(BOARD_SIZE):
        current_column = []
        for column in range(BOARD_SIZE):
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
    
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if x == 0 and y == 0:
                continue

            if x1 + x == x2 and y1 + y == y2:
                return True
    
    return False

def fill_mines(ignore_x = -1, ignore_y = -1):
    for i in range(MINE_COUNT):
        random_x = random.randrange(0, BOARD_SIZE)
        random_y = random.randrange(0, BOARD_SIZE)

        while (ignore_x == random_x and ignore_y == random_y) or is_next_to(ignore_x,ignore_y,random_x,random_y, radius=2) or board[random_y][random_x]["has"] == "mine":
            random_x = random.randrange(0, BOARD_SIZE)
            random_y = random.randrange(0, BOARD_SIZE)
        
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
        return "\033[94m"
    elif num == 2:
        return "\033[32m"
    elif num == 3:
        return "\033[91m"
    elif num == 4:
        return "\033[34m"
    elif num == 5:
        return "\033[35m"
    elif num == 6:
        return "\033[96m"
    elif num == 7:
        return "\033[37m"
    elif num == 8:
        return "\033[90m"
    else:
        return "\033[95m"

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

    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            if not is_in_bounds(row_idx + x, column_idx + y):
                continue
            if x == 0 and y == 0:
                continue

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
    print(" ", end=" ")
    for i in range(BOARD_SIZE):
        print(i + 1, end=get_space())
    print("\n", end="")

    for row_idx in range(len(board)):
        row = board[row_idx]
        
        # print the numbers on the sides
        print(row_idx + 1, end=" ")


        for column_idx in range(len(row)):
            column = row[column_idx]

            # Non mine cells
            if column["revealed"] == True or (reveal == True and not column["has"] == "mine"):
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
    x = -1
    y = -1
    global moves
    while True:
        coordinates = input("Enter the coordinates for the next move separated by a space (eg: 6 7): ").strip()
      
        # Get the coordinates
        if len(coordinates.split(" ")) >= 2:
            coordinates = coordinates.split(" ")
            if coordinates[0].isdigit() and coordinates[1].isdigit():
                x = int(coordinates[0]) - 1
                y = int(coordinates[1]) - 1

                if not is_in_bounds(x, y):
                    clear_screen()
                    print("invalid coordinates")
                    print_info()
                    display_board()
                    continue

                while True:
                        action = ""
                        # If user put an action after the coordinates, skip the second input
                        if len(coordinates) > 2 and coordinates[2] in "open flag":
                            action = coordinates[2]
                        else:
                            # Ask the user for the action
                            clear_screen()
                            print_info()
                            display_board(highlight_x=x, highlight_y=y)
                            action = input("What do you want to do? (open, flag, cancel): ").lower().strip()


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
                            moves -= 1
                            break
                        else:
                            print("invalid input")
                break
            else:
                print("invalid input")
        else:
            print("invalid input")
    
    return (x, y)

def print_info():
    """
    Shows how many mines are left, how many moves the user did, and how much time has passed.
    """
    mines_left = 0
    for row in board:
        for column in row:
            if column["has"] == "mine":
                mines_left += 1
            if column["flagged"] == True:
                mines_left -= 1
    
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
    if not is_in_bounds(x, y):
        return
    if not force_fill:
        if board[y][x]["revealed"]:
            return

    board[y][x]["revealed"] = True

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

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

# Run the app
if __name__ == '__main__':
    # Fill the board once
    generate_board()

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
            break
        
        # User finished a move
        moves += 1
