import random
import colr
from copy import copy
import tkinter as tk
import copy


class Board:
    def __init__(self, window=None, initial_board=None):
        if initial_board is None:
            self.board: list = [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ]
        else:
            self.board: list = initial_board

        if window is None:
            window = new_window()

        self.window = window

        # for i in range(4):
        #     self.score_label = tk.Label(self.window, text="Score: 0")
        #     self.score_label.grid(row=0, column=i)
        self.score_label = tk.Label(self.window, text="Score: 0")
        self.score_label.grid(row=0)

        self.tiles = [[None for _ in range(4)] for _ in range(4)]

        for i in range(1, 5):
            for j in range(4):
                self.tiles[i - 1][j] = tk.Canvas(self.window, width=100, height=100)
                self.tiles[i - 1][j].grid(row=i, column=j)

    def __deepcopy__(self, memo):
        # print("IN __deepcopy__")
        # create a new game instance
        cls = self.__class__
        new_game = cls.__new__(cls)

        memo[id(self)] = new_game

        # copy all attributes, but ignore the Tkinter ones
        for k, v in self.__dict__.items():
            if k in ("window", "tiles", "score_label"):
                setattr(new_game, k, None)
            else:
                setattr(new_game, k, copy.deepcopy(v, memo))
        return new_game

    def add_tile(self, tile_value: int, x_coord: int, y_coord: int):
        self.board[y_coord][x_coord] = tile_value

    def value_of_position(self, x_coord: int, y_coord: int) -> int:
        return self.board[y_coord][x_coord]

    # this fn untested! it's important tho
    def move_tile(self, square1: tuple, square2: tuple, eat: bool = False) -> int:
        """returns how much score to add"""
        x1, y1 = square1
        x2, y2 = square2
        tile_value = self.value_of_position(x1, y1)
        # remove from old location
        self.board[y1][x1] = 0
        # place in new location no eat
        if not eat:
            self.board[y2][x2] = tile_value
        else:
            self.board[y2][x2] = tile_value * 2
            return tile_value * 2
        return 0

    def print(self, highest=2):
        tile_colours = {
            2048: "EDC22E",
            1024: "#EDC23F",
            512: "#EDC850",
            256: "#EDCC61",
            128: "#EDCF72",
            64: "#F65E3B",
            32: "#F67C5F",
            16: "#F59563",
            8: "#F2B179",
            4: "#EDE0C8",
            2: "#EEE4DA",
            0: "#CCC0B3"
        }

        highest2 = copy.copy(highest)
        #print(f"highest2 = {highest2}, highest = {highest}")
        for row in self.board:
            #print(f"higest2 = {highest2}")
            for tile in row:

                # FFFFFF is white, 000000 is black
                print(colr.color(f"{tile}\t".expandtabs(highest2 + 2), back=tile_colours[tile], fore="000000"), end=" ")
                # print(colr.color("32", back=tile_colours[32], fore="FFFFFF"))
            print("")

    def tkinter_print(self, score):
        tile_colours = {
            65536: "569BE0",
            32768: "#6BAED5",
            16384: "#F0513B",
            8192: "#27B053",
            4096: "#FB736D",
            2048: "#EDC22E",
            1024: "#EDC23F",
            512: "#EDC850",
            256: "#EDCC61",
            128: "#EDCF72",
            64: "#F65E3B",
            32: "#F67C5F",
            16: "#F59563",
            8: "#F2B179",
            4: "#EDE0C8",
            2: "#EEE4DA",
            0: "#CCC0B3"
        }
        for i in range(4):
            for j in range(4):
                tile = self.board[i][j]
                if tile not in tile_colours:
                    colour = "#2E2C26"
                else:
                    colour = tile_colours[tile]
                text_colour = "#000000" if tile > 0 else "#FFFFFF"
                self.tiles[i][j].create_rectangle(10, 10, 90, 90, fill=colour)
                self.tiles[i][j].create_text(50, 50, text=str(tile) if tile != 0 else '', fill=text_colour,
                                             font=("Helvetica", 24))
        self.score_label.config(text="Score: " + str(score))
        self.window.update()

    def __getitem__(self, coordinate: tuple) -> int:
        x, y = coordinate
        return self.board[y][x]

    def __setitem__(self, coordinate: tuple, value: int):
        x, y = coordinate
        self.board[y][x] = value


def new_window():
    window = tk.Tk()
    window.title("2048 Game")
    return window

class Game:
    def __init__(self, track_primes: bool = False, board: Board = None, use_gui: bool = True) -> None:
        self.track_primes: bool = track_primes
        self.prime_tracker: int = 1
        self.score: int = 0
        self.use_gui = use_gui

        if board is None:
            self.board: Board = Board()
        else:
            self.board = board
        self.num_moves: int = 0
        self.highest_tile: int = 0

    def __deepcopy__(self, memo):
        # print("IN __deepcopy__")
        # create a new game instance
        cls = self.__class__
        new_game = cls.__new__(cls)

        memo[id(self)] = new_game

        # copy all attributes, but ignore the Tkinter window
        for k, v in self.__dict__.items():
            if k == 'window':
                # print("in if")
                setattr(new_game, k, None)  # or whatever default value you prefer
                # print("done if")
            else:
                # print(f"GAME in else for {k}: {v}")
                setattr(new_game, k, copy.deepcopy(v, memo))
                # print(f"GAME dn else for {k}: {v}")

        return new_game

    def return_prime(self):
        if not self.track_primes:
            return False
        else:
            return self.prime_tracker

    def setup_board(self) -> None:
        # this fn should be called in __init__

        # pick which squares to use
        x1, y1 = random.randint(0, 3), random.randint(0, 3)
        # this thing with the loop prevents duplicates of the same square
        x2, y2 = x1, y1
        while x2 == x1 and y2 == y1:
            x2, y2 = random.randint(0, 3), random.randint(0, 3)

        # 90% chance of a tile being 2
        # weird that this makes a list and I need to take the first element from it. can clean up later
        tile1_value = random.choices([2, 4], weights=(0.9, 0.1))[0]
        tile2_value = random.choices([2, 4], weights=(0.9, 0.1))[0]
        # print(f"tile1 = {tile1_value}, tile2 = {tile2_value}")
        self.board.add_tile(tile1_value, x1, y1)
        self.board.add_tile(tile2_value, x2, y2)

    def add_new_tile(self) -> None:
        tile_value = random.choices([2, 4], weights=(0.9, 0.1))[0]

        x, y = random.randint(0, 3), random.randint(0, 3)
        square_coord = [x, y]
        while self.board[square_coord] != 0:
            x, y = random.randint(0, 3), random.randint(0, 3)
            square_coord = [x, y]
        self.board.add_tile(tile_value, x, y)

    def display_updated_board(self):
        if self.use_gui:
            self.board.tkinter_print(self.score)
        else:
            print(f"--------------------SCORE: {self.score}--------------------")
            self.board.print(highest=len(str(self.highest_tile)))

    def left(self):
        return self.move(1)

    def right(self):
        return self.move(0)

    def up(self):
        return self.move(2)

    def down(self):
        return self.move(3)

    def move(self, direction: int, print_board: bool = True, illegal_warn: bool = True) -> bool:
        """returns whether it was successful"""
        # 0 = right, 1 = left, 2 = up, 3 = down
        if direction not in (0, 1, 2, 3):
            raise ValueError("Only directions 0-3 are allowed. 0 = right, 1 = left, 2 = up, 3 = down")

        square_coord_list = []
        if direction in (1, 2):  # left or up
            # generate list of squares from left to right one row at a time, starting from top
            for row_num in range(len(self.board.board)):
                # print(row_num)
                for i in range(4):
                    # print(3 - i)
                    # print(f"({i}, {row_num})")
                    square_coord_list.append((i, row_num))
        elif direction in (0, 3):    # right or down
            for row_num in range(len(self.board.board)):
                # print(row_num)
                for i in range(4):
                    # print(3 - i)
                    # print(f"({i}, {row_num})")
                    square_coord_list.append((3 - i, 3 - row_num))

        # removes empty tiles
        tiles_to_move = []
        for square in square_coord_list:
            if self.board.value_of_position(square[0], square[1]) != 0:
                tiles_to_move.append(square)

        not_moving_list = set()
        for tile in tiles_to_move:
            #print(f"---tile is {tile}--")
            traverse = self.traverse_list(tile, direction, self.board)
            # print(f"traverse of {tile}= {traverse}")
            if not traverse[0]:
                # print(f"{tile} not moving")
                not_moving_list.add(tile)
            else:
                #print(f"{tile} moving to {traverse[0][-1]}")
                #print(f"{tile}'s traverse = {traverse}")
                xf, yf = traverse[0][-1]
                add_to_score = self.board.move_tile(tile, (xf, yf), traverse[-1])
                self.score += add_to_score
                if add_to_score > self.highest_tile:
                    self.highest_tile = add_to_score

        illegal_move = False
        if set(not_moving_list) == set(tiles_to_move):
            if illegal_warn:
                print("ILLEGAL MOVE!")
            return False

        if not illegal_move:
            self.add_new_tile()

            # prime stuff. disabled by default because it would slow things down on large simulations
            if self.track_primes:
                prime_direction_dict = {
                    0: 2,  # right
                    1: 3,  # left
                    2: 5,  # up
                    3: 7  # down
                }
                self.prime_tracker *= prime_direction_dict[direction]
        if print_board:
            self.display_updated_board()

        self.num_moves += 1
        return True

    def traverse_list(self, square: tuple, direction: int, board=None) -> list:
        if board is None:
            board = self.board
        # makes ordered list of squares to traverse for a given square
        # 0 = right, 1 = left, 2 = up, 3 = down
        # square is a tuple of form (x, y)
        output_list: list = []
        final_capture: bool = False
        x, y = square
        square_value: int = board.value_of_position(x, y)

        # print(f"starting square x = ({x}, {y})")
        next_square: list = [x, y]
        if direction == 0:  # right
            while next_square[0] < 3:
                next_square[0] += 1
                if self.empty_square(next_square):
                    #print(f"next_square = {next_square}")
                    output_list.append(next_square[:])
                else:
                    #print(f"{next_square} isn't empty")
                    if board.value_of_position(next_square[0], next_square[1]) == square_value:
                        # print(f"we gon eat on {next_square}")
                        output_list.append(next_square[:])
                        final_capture: bool = True
                    break
        elif direction == 1: # left. this and others could be condensed into 1 loop for all of them if I switch next square [0 to 1] and += 1 to -1 in the right places
            while next_square[0] > 0:
                #print(f"next square before = {next_square} ---- ---- ---- ----")
                next_square[0] -= 1
                #print(f"next square = {next_square} ---- ---- ---- ----")
                if self.empty_square(next_square):
                    #print(f"next_square = {next_square}")
                    output_list.append(next_square[:])

                else:
                    #print(f"{next_square} isn't empty")
                    if board.value_of_position(next_square[0], next_square[1]) == square_value:
                        # print(f"we gon eat on {next_square}. traverse = {output_list}")
                        output_list.append(next_square[:])
                        final_capture: bool = True

                    break
        elif direction == 2: # up. this and others could be condensed into 1 loop for all of them if I switch next square [0 to 1] and += 1 to -1 in the right places
            while next_square[1] > 0:
                next_square[1] -= 1
                if self.empty_square(next_square):
                    #print(f"next_square = {next_square}")
                    output_list.append(next_square[:])
                else:
                    #print(f"{next_square} isn't empty")
                    if board.value_of_position(next_square[0], next_square[1]) == square_value:
                        # print(f"we gon eat on {next_square}")
                        output_list.append(next_square[:])
                        final_capture: bool = True
                    break
        elif direction == 3:  # down
            while next_square[1] < 3:
                next_square[1] += 1
                if self.empty_square(next_square):
                    #print(f"next_square = {next_square}")
                    output_list.append(next_square[:])
                else:
                    #print(f"{next_square} isn't empty")
                    if board.value_of_position(next_square[0], next_square[1]) == square_value:
                        # print(f"we gon eat on {next_square}")
                        output_list.append(next_square[:])
                        final_capture: bool = True
                    break
        if output_list:
            output: list = [output_list, final_capture]
        else:
            output: list = [[], final_capture]
        # print(f"output = {output}")
        return output

    def empty_square(self, square: tuple) -> bool:
        """returns true if empty, false if not"""
        x, y = square
        # print(f"in empty sq, will return {self.board.value_of_position(x, y) == 0}")
        return self.board.value_of_position(x, y) == 0

    def game_over_check(self) -> bool:
        for y in range(4):
            for x in range(4):
                if self.board.value_of_position(x, y) == 0:
                    # Found an empty tile
                    return False
                if x < 3 and self.board.value_of_position(x, y) == self.board.value_of_position(x + 1, y):
                    # Found adjacent tiles with the same value
                    return False
                if y < 3 and self.board.value_of_position(x, y) == self.board.value_of_position(x, y + 1):
                    # Found adjacent tiles with the same value
                    return False
        # No empty tiles and no adjacent tiles with the same value
        return True






#global latest_key
# latest_key = "NONE"




# keyboard_input()

def run_game(track_primes=False):
    # new start
    window = tk.Tk()
    window.title("2048 Game")

    running_game = Game(track_primes=track_primes)
    print(f"on any move, enter 'p' to return prime tracker")
    running_game.setup_board()
    running_game.display_updated_board()
    # new end

    # running_game = Game(track_primes)
    # print(f"on any move, enter 'p' to return prime tracker")
    # running_game.setup_board()
    # running_game.print_board()

    while True:
        #running_game.print_board()
        move = input("direction (w, a, s, d): ")
        # 0 = right, 1 = left, 2 = up, 3 = down

        if move == "s":
            running_game.down()
        elif move == "w":
            running_game.up()
        elif move == "a":
            running_game.left()
        elif move == "d":
            running_game.right()
        elif move == "p":
            print(running_game.return_prime())
        elif move == "exit":
            exit()

def save_game_result_to_csv(file_name, model, score, duration, board):
    import numpy as np
    import os
    import pandas as pd
    """
    Save game results to a CSV file.

    Args:
        file_name (str): The name of the CSV file.
        model (str): The model used for the game.
        score (int): The score achieved in the game.
        duration (float): The duration of the game in seconds.
        board (list): 2d array of the board when the game ended
    """
    # Create the 'saved games' folder if it doesn't exist
    folder_path = os.path.join(os.getcwd(), 'saved games')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Check if the CSV file exists
    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path):
        # Load the existing CSV file
        df = pd.read_csv(file_path)
    else:
        # Create a new DataFrame
        df = pd.DataFrame(columns=['Model', 'Score', 'Duration', 'Board'])

    # Flatten the board into a 1D list
    flattened_board = np.array(board).flatten().tolist()

    # Create a new row with the provided data
    new_row = pd.Series({'Model': model, 'Score': score, 'Duration': duration, 'Board': flattened_board})
    df.loc[len(df)] = new_row

    # Save the DataFrame to the CSV file
    df.to_csv(file_path, index=False)





if __name__ == '__main__':
    # from AI import MC2

    # g = Game()
    # g.setup_board()
    # m = MC2(g, verbose=True, sims_per_turn=100)
    # m.run()
    # g.board.window.mainloop()
    # run_game()
    # import time
    # start_time = time.time()
    # g = Game()
    # g.setup_board()
    # m = MC2(g, verbose=True, sims_per_turn=100)
    # m.run()
    # print(f"IT TOOK {time.time() - start_time}s to run")
    # g.board.window.mainloop()
    run_game()

