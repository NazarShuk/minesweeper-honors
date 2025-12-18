import random
import os
import time

BOARD_SIZE = 8
DIFFICULTY = 1

board = []
game_over = False
moves = 0
start_time = time.perf_counter()


def get_space():
    space = ""
    for i in range(BOARD_SIZE // 2):
        space += " "
    return space

def generate_board():
    for row in range(BOARD_SIZE):
        current_column = []
        for column in range(BOARD_SIZE):
            if random.randint(1, 20) <= DIFFICULTY:
                current_column.append({
                    "has":"mine",
                    "revealed": False,
                    "flagged": False
                })
            else:
                current_column.append({
                    "has":"nothing",
                    "revealed": False,
                    "flagged": False
                })
        board.append(current_column)

def get_color_by_number(num):
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
    row = board[row_idx]
    column = row[column_idx]
    mines_around = 0

    if row_idx != 0:
        # top left
        if column_idx != 0:
            if board[row_idx - 1][column_idx - 1]["has"] == "mine":
                mines_around += 1
        
        # top center
        if board[row_idx - 1][column_idx]["has"] == "mine":
            mines_around += 1
        
        # top right
        if column_idx != len(row) - 1:
          if board[row_idx - 1][column_idx + 1]["has"] == "mine":
            mines_around += 1
    
    # left
    if column_idx != 0:
        if board[row_idx][column_idx - 1]["has"] == "mine":
            mines_around += 1
    
    # right
    if column_idx != len(row) - 1:
        if board[row_idx][column_idx + 1]["has"] == "mine":
            mines_around += 1
    
    if row_idx != len(board) - 1:
        # bottom left
        if column_idx != 0:
            if board[row_idx + 1][column_idx - 1]["has"] == "mine":
                mines_around += 1
        
        # bottom center
        if board[row_idx + 1][column_idx]["has"] == "mine":
            mines_around += 1
        
        # bottom right
        if column_idx != len(row) - 1:
          if board[row_idx + 1][column_idx + 1]["has"] == "mine":
            mines_around += 1
    return mines_around

def display_board(reveal = False, highlight_x=-1,highlight_y=-1):
    print(" ", end=" ")
    for i in range(BOARD_SIZE):
        print(i + 1, end=get_space())
    print("\n", end="")
    for row_idx in range(len(board)):
        row = board[row_idx]
        print(row_idx + 1, end=" ")
        for column_idx in range(len(row)):
            column = row[column_idx]
            if column["revealed"] == True or (reveal == True and not column["has"] == "mine"):
                mines_around = get_mines_around(column_idx, row_idx)
                if mines_around > 0:
                  print(get_color_by_number(mines_around) + str(mines_around) + "\033[0m", end=get_space())
                else:
                    print("\033[90m.\033[0m", end=get_space())
            elif column["has"] == "mine" and reveal:
                print("X", end=get_space())
            elif column["flagged"]:
                if highlight_x == column_idx and highlight_y == row_idx:
                    print("\033[91;40;6mF\033[0m", end=get_space())
                else:
                    print("\033[90mF\033[0m", end=get_space())
            else:
                if highlight_x == column_idx and highlight_y == row_idx:
                    print("\033[91;40;6m■\033[0m", end=get_space())
                else:
                    print("\033[90m■\033[0m", end=get_space())
        print("\n")

def get_input():
    while True:
      coordinates = input("Enter the coordinates for the next move separated by a space (eg: 6 7): ").strip()
      
      if len(coordinates.split(" ")) >= 2:
          coordinates = coordinates.split(" ")
          if coordinates[0].isdigit() and coordinates[1].isdigit():
              x = int(coordinates[0]) - 1
              y = int(coordinates[1]) - 1

              while True:
                    action = ""
                    if len(coordinates) > 2 and coordinates[2] in "open flag":
                        action = coordinates[2]
                    else:
                            os.system("cls")
                            print_info()
                            display_board(highlight_x=x, highlight_y=y)

                            action = input("What do you want to do? (open, flag, cancel): ").lower().strip()

                    if action == "open":
                        
                        if board[y][x]["has"] == "mine":
                            global game_over
                            game_over = True
                            break
                        else:
                            flood_open(x, y)
                            board[y][x]["revealed"] = True
                            board[y][x]["flagged"] = False
                            break
                    elif action == "flag":
                        if board[y][x]["revealed"] != True:
                            board[y][x]["flagged"] = not board[y][x]["flagged"]
                        break
                    elif action == "cancel":
                        global moves
                        moves -= 1
                        break
                    else:
                        print("invalid input")
              break
          else:
              print("invalid input")
      else:
          print("invalid input")

def print_info():
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

def flood_open(x, y):
    if x == -1 or x >= len(board) or y == -1 or y >= len(board):
        return
    if board[y][x]["revealed"]:
        return

    board[y][x]["revealed"] = True

    if get_mines_around(x, y) == 0:        
        flood_open(x - 1, y - 1)
        flood_open(x, y - 1)
        flood_open(x + 1, y - 1)

        flood_open(x - 1, y)
        flood_open(x + 1, y)

        flood_open(x - 1, y + 1)
        flood_open(x, y + 1)
        flood_open(x + 1, y + 1)

def check_win():
    for row in board:
        for cell in row:
            if cell["has"] == "mine" and not cell["flagged"]:
                return False
    return True


if __name__ == '__main__':
    generate_board()

    while True:
        os.system("cls")

        print_info()
        display_board()
        get_input()

        if game_over:
            os.system("cls")
            display_board(True)
            print("Whoops that was a mine. Game over, thx for playing")
            break

        if check_win():
            os.system("cls")
            display_board(True)


            end_time = time.perf_counter()
            elapsed = end_time - start_time
            print(f"You won! Total moves: {moves}, total time: {elapsed:.0f} seconds")
            break

        moves += 1
