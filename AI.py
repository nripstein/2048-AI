import statistics
import copy
import time
import numpy as np
import pandas as pd
import os
import math


def save_game_result_to_csv(file_name, model, score, duration, board, other_data=None):
    """
    Save game results to a CSV file.

    Args:
        file_name (str): The name of the CSV file.
        model (str): The model used for the game.
        score (int): The score achieved in the game.
        duration (float): The duration of the game in seconds.
        board (list): 2d array of the board when the game ended
        other_data (dict): dictionary of other data to be added
    """
    # Create the 'saved games' folder if it doesn't exist
    folder_path = os.path.join(os.getcwd(), 'saved games')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Check if the CSV file exists
    file_path = os.path.join(folder_path, f"{file_name}.csv")
    if os.path.exists(file_path):
        print(f"FILE PATH EXISTS: {file_path}")
        # Load the existing CSV file
        df = pd.read_csv(file_path)
    else:
        # Create a new DataFrame
        df = pd.DataFrame(columns=['Model', 'Score', 'Duration', 'Board'])

    # Flatten the board into a 1D list
    flattened_board = np.array(board).flatten().tolist()

    if other_data is not None:
        # Add other_data columns to the DataFrame
        for key, value in other_data.items():
            df[key] = value

    # Create a new row with the provided data
    new_row = pd.Series({'Model': model, 'Score': score, 'Duration': duration, 'Board': flattened_board})
    df.loc[len(df)] = new_row

    # Save the DataFrame to the CSV file
    df.to_csv(f"{file_path}", index=False)


class RandomMoves:
    def __init__(self, game):
        self.game = game

    def run(self):
        while not self.game.game_over_check():
            self.game.move(np.random.randint(0, 4), illegal_warn=False)
        else:
            print("done")
            save_game_result_to_csv("MC5", "random", self.game.score, 0, self.game.board.board)


class Down2:
    def __init__(self, game, print_moves=False):
        self.print_moves = print_moves
        self.game = game
        self.game.setup_board()

    def run(self):
        # if down is legal, do until illegal
        # if left is legal, do until illegal, then start from top
        # if right is legal, do until illegal, then start from top
        # if up is legal, do until illegal, then start from top
        i = 0
        j = 1
        while True:
            # print(f"------------------i = {i}...j = {j}------------------")
            if self.print_moves:
                self.game.display_updated_board()

            if j % 2 != 0:
                if not self.game.down():    # does down until illegal
                    # print(f"i = {i}, j = {j}, down illegal")
                    j *= 2   # set j to 2, so we skip down
                    # if j % 7 == 0:
                    #     print(f"GAME OVER, i = {i}, j = {j}")
                    #     break
            elif j % 3 != 0:
                if not self.game.left():
                    # print(f"i = {i}, j = {j}, left illegal")
                    j *= 3
                    continue
                else:
                    j = 1
            elif j % 5 != 0:
                if not self.game.right():
                    # print(f"i = {i}, j = {j}, right illegal")
                    j *= 5
                    continue
                else:
                    j = 1
            elif j % 7 != 0:
                if not self.game.up():
                    # print(f"i = {i}, j = {j}, up illegal")
                    j *= 7
                    print(f"GAME OVER, i = {i}, j = {j}")
                    break
                    #continue
                else:
                    j = 1
            i += 1

    def reset(self):
        self.__init__(self.game) # wait I need a new game object


class DownBot:
    def __init__(self, game, print_moves=False):
        self.print_moves = print_moves
        self.game = game
        self.game.setup_board()

    def run(self):
        while True:
            print("----------------------------------------")
            if self.print_moves:
                self.game.display_updated_board()
                print("----------------------------------------")
            #print(self.game.down())
            if not self.game.down():
                if not self.game.left():
                    if not self.game.right():
                        if not self.game.up():
                            print(f"GAME OVER. {self.game.num_moves} moves, {self.game.score}, highest = {self.game.highest_tile}")
                            break

    def reset(self):
        self.__init__(self.game)


class ManyRuns:
    def __init__(self, bot_type, num_simulations, print_moves=False):
        #self.print_moves = print_moves
        self.num_simulations = num_simulations
        self.bot = bot_type(print_moves=print_moves)

    def run(self):
        num_moves = []
        scores = []
        highest_tiles = []
        for i in range(self.num_simulations):
            self.bot.run()
            num_moves.append(self.bot.game.num_moves)
            scores.append(self.bot.game.score)
            highest_tiles.append(self.bot.game.highest_tile)
            self.bot.reset()
        print(f"num moves: {num_moves}")
        print(f"scores: {scores}")
        print(f"highest tiles: {highest_tiles}")
        self.analysis(num_moves, scores, highest_tiles)

    def analysis(self, moves, scores, tiles):
        score_mean = statistics.mean(scores)
        score_SD = statistics.stdev(scores, score_mean)
        print(f"SCORES: mean = {score_mean}, SD = {score_SD}")
        print(f"tile: mean = {statistics.mean(tiles)}, SD = {statistics.stdev(tiles, statistics.mean(tiles))}")
        #plt.plot(scores)
        '''x = np.arange(0, 5000)
        plt.plot(x, norm.pdf(x, score_mean, score_SD))
        plt.show()'''


class MC2:
    """DOESNT WORK BC NO DEEPCOPY"""
    def __init__(self, game, sims_per_turn: int = 100, verbose: bool = True) -> None:
        self.main_game = game
        self.sims_per_turn = sims_per_turn
        self.verbose = verbose

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):
        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        for direction in range(4):

            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
            else:
                # print("ok")
                direction_scores_to_avg = []
                for sim in range(self.sims_per_turn):
                    # print(f"sim num {sim}")
                    current_score = self.one_game(game_copy)
                    direction_scores_to_avg.append(current_score)

                scores.append(np.average(np.array(direction_scores_to_avg)))
            # print(f"done direction {direction}")
        best_direction = scores.index(max(scores))

        if self.verbose:
            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(max(scores))}")

        # time.sleep(0.01)

        self.main_game.move(best_direction)
        # print("ok")

    def run(self):
        while not self.main_game.game_over_check():
            self.n_games()

            self.main_game.display_updated_board()
        else:
            if self.verbose:
                print(f"GAME OVER: SCORE = {self.main_game.score}")


class MC3:
    """
    same as MC2 but tracks projected scores. only selects moves which increase projected score
    Uses max score instead of average as projected score.

    seems to somehow be worse despite being much slower
    DOESNT WORK BECAUSE NO DEEPCOPY
    """
    def __init__(self, game, sims_per_turn: int = 100, verbose: bool = True) -> None:
        self.main_game = game
        self.sims_per_turn = sims_per_turn
        self.verbose = verbose
        self.projected_scores = [0]

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):
        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []

        num_beat_attempts = 0
        while num_beat_attempts < 100:
            for direction in range(4):
                game_copy = copy.deepcopy(self.main_game)

                if not game_copy.move(direction, print_board=False, illegal_warn=False):
                    # if it's illegal to move in the current direction, just add the current score to decision list
                    scores.append(game_copy.score)
                else:
                    direction_scores_to_avg = []
                    for sim in range(self.sims_per_turn):
                        current_score = self.one_game(game_copy)
                        direction_scores_to_avg.append(current_score)

                    scores.append(np.average(np.array(direction_scores_to_avg)))
            projected_score_current = max(scores)
            print(f"current projected score: {scores}, {projected_score_current}")

            if projected_score_current > self.projected_scores[-1]:
                break

            num_beat_attempts += 1
            if num_beat_attempts < 100:  # reset and try to beat score only if we're not on last attempt
                scores = []

        best_direction = scores.index(max(scores))

        if self.verbose:
            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(max(scores))}")

        self.projected_scores.append(max(scores))
        self.main_game.move(best_direction)

    def run(self):
        while not self.main_game.game_over_check():
            self.n_games()

            self.main_game.display_updated_board()
        else:
            if self.verbose:
                print(f"GAME OVER: SCORE = {self.main_game.score}")


class MC4:
    """
    same as the stackoverflow guy
    THIS IS ACTUALLY A GOOD MODEL! PROBABLY BETTER THAN up to and including MC9

    FIRST WORKING DESIGN BC USES DEEPCOPY ON INNER OBJECT
    same as MC2 but
    current_score = self.one_game(copy.deepcopy(game_copy)) instead of current_score = self.one_game(game_copy)
    one in MC2 resulted in direction_scores_to_avg being all the same number. this version doesn't
    """
    def __init__(self, game, sims_per_turn: int = 100, verbose: bool = True) -> None:
        self.main_game = game
        self.sims_per_turn = sims_per_turn
        self.verbose = verbose

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):
        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        for direction in range(4):
            game_copy = copy.deepcopy(self.main_game)
            if not game_copy.move(direction, print_board=False, illegal_warn=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
            else:
                direction_scores_to_avg = []
                for sim in range(self.sims_per_turn):
                    # print(f"sim num {sim}")
                    current_score = self.one_game(copy.deepcopy(game_copy))
                    direction_scores_to_avg.append(current_score)
                # print("------------------------direction_scores_to_avg------------------------")
                # print(direction_scores_to_avg)
                scores.append(np.average(np.array(direction_scores_to_avg)))


            # print(f"done direction {direction}")
        best_direction = scores.index(max(scores))
        scores = np.array(scores)
        if self.verbose:

            print(f"{scores.round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(max(scores))}")

        # time.sleep(0.01)
        # if np.all(scores == scores[0]):
            # save_game_result_to_csv("MC4", "MC4_ENCOUNTER ERROR", self.main_game.score, 0, self.main_game.board.board)
            # this just always ends up being the end, so no big deal AT ALL!!
        self.main_game.move(best_direction)

        # print("ok")

    def run(self):
        start_time = time.time()
        while not self.main_game.game_over_check():
            self.n_games()
            if self.main_game.use_gui:
                self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")
        save_game_result_to_csv("MC4", f"MC4_sims_{self.sims_per_turn}", self.main_game.score, total_time, self.main_game.board.board)


class MC5:
    """
    same as MC4 but picks move by highest average of top 50 moves, not highest of all 100

    keeps the high tile in the corner a bit more especially near the beginning but still hardly does

    next attempt could be to try switching to the MC4 strategy in critical positions where its close to losing to account for unlucky events

    could also try something where it attempts each possible next tile spawn 5 times or something, then do this eliminate bad attempts thing where it eliminates bad attempts given a certain next move
    that way we guarantee the

    could even maximize expected value := P(direction maximized) > P(all other directions maximize)
    or maximize sum top_5_score for direction P(getting it) (assumes we check each tile) this idea not fleshed out
    """
    def __init__(self, game, sims_per_turn: int = 100, verbose: bool = True) -> None:
        self.main_game = game
        self.sims_per_turn = sims_per_turn
        self.verbose = verbose

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):
        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        for direction in range(4):

            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
            else:
                direction_scores_to_avg = []
                for sim in range(self.sims_per_turn):
                    # print(f"sim num {sim}")
                    current_score = self.one_game(copy.deepcopy(game_copy))
                    direction_scores_to_avg.append(current_score)
                direction_scores_to_avg_upper_quantile = np.sort(np.array(direction_scores_to_avg))[::-1][:50]
                scores.append(np.average(direction_scores_to_avg_upper_quantile))


            # print(f"done direction {direction}")
        best_direction = scores.index(max(scores))

        if self.verbose:

            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(max(scores))}")

        # time.sleep(0.01)

        self.main_game.move(best_direction)
        # print("ok")

    def run(self):
        start_time = time.time()
        while not self.main_game.game_over_check():
            self.n_games()

            self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")
        save_game_result_to_csv("MC5", "MC5", self.main_game.score, total_time, self.main_game.board.board)


class MC6:
    """
    EVALUATES ALL POSSIBLE NEXT MOVES

    """
    def __init__(self, game, game_obj, sims_per_turn: int = 100, verbose: bool = True) -> None:
        self.main_game = game
        self.game_obj = game_obj
        self.sims_per_turn = sims_per_turn
        self.verbose = verbose

    def one_game(self, game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        i = 1 # get rid of i
        while not game.game_over_check():
            # print(f"DETECTED GAME OVER after {i} in one_game")
            # time.sleep(0.01)
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
            i += 1
        if type(game.score) != int:  # trying to make sure there's no NAN by replacing non int values which somehow seem to arise with current score
            return self.main_game.score
        return game.score

    def n_games(self):
        depth_dict_4 = {
            15: 1,
            14: 1,
            13: 1,
            12: 1,
            11: 1,
            10: 1,
            9: 1,
            8: 2,
            7: 2,  # 126 for 2
            6: 2,  # 108 for 2
            5: 3,  # 135 for 2
            4: 4,  # 144 for 2
            3: 5,  # 135 for 2
            2: 8,  # 144 for 2
            1: 15  # 135 for 2
        }

        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        for direction in range(4):

            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False, add_tile=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
            else:
                # THIS IS WHERE WE MAKE THE NODES START
                # take board we're currently working on, get list of all possible tiles that could spawn
                # print(f"There are {len(game_copy.board.get_empty_tiles())} empty squares")
                tmp = copy.deepcopy(game_copy.board)
                boards2, boards4 = self.get_possible_boards(tmp)  # will deepcopying the boardhlp?

                # print("BOARDS4 START")
                # print(boards4)
                # print("BOARDS4 END")
                num_open_tiles = len(boards2) # try increasing num open tiles to get rid of NAN?
                direction_scores_to_avg = []
                for board in boards4:  # for each board, do necessary depth
                    for depth in range(depth_dict_4[num_open_tiles]):

                        # make new game obj with same score as current game

                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score
                        # print("MADE OBJ IN LOOP OF BOARDS4")
                        # current_game_obj.display_updated_board()  # temp line!
                        # time.sleep(1)
                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        direction_scores_to_avg.append(current_score)
                        # print("DONE LOOP OF BOARDS4")
                if num_open_tiles == 0:  # I THINK THIS IS WHATS CAUSING IT
                    print("WARNING!! THIS IS CAUSING NAN PROBS")
                    print(f"num_open_tiles = {num_open_tiles}")
                    print("CANT HAVE 0 open tiles bc the dict cant understand that and it makes 0 sense")
                    print(f"SHOWING BOARD2 and 4 list. len board 2, 4 = {len(boards2), boards4}")  # boards2 and 4 have len0 is the problem!!


                    for board in boards2:
                        board.print()
                        print("---the above was from boards2---")
                    for board in boards4:
                        board.print()
                        print("---the above was from boards2---")
                    time.sleep(10)
                if len(boards4) == 0 or len(boards2) == 0 or depth_dict_4[num_open_tiles] == 0:
                    print("WARNING!! THIS IS CAUSING NAN PROBS")
                    print("NUM OPEN TILES:")
                    print(f"len boards4, 2, depth dict: {len(boards4)}, {len(boards2)}, {depth_dict_4[num_open_tiles]}")
                    time.sleep(10)
                for board in boards2:  # this can be condensed, only diff is *9 in second for statement
                    for depth in range(depth_dict_4[num_open_tiles] * 9):  # * 9 bc 90% chance of 2 spawning
                        # make new game obj
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        direction_scores_to_avg.append(current_score)

                # NOW ADD THE TILE ONCE ALL EVALUATING IS DONE??
                game_copy.add_new_tile()

                if self.verbose:
                    np.set_printoptions(linewidth=np.inf)
                    print(np.array(direction_scores_to_avg))  # getting nans from direction_scores_to_avg!!!!

                scores.append(np.average(np.array(direction_scores_to_avg)))  # DOES ALL, NOT JUST BETTER HALF, BUT THE WHOLE POINT OF THIS STRAT IS IT ENABLES BETTER USAGE OF UPPER HALF BC THE BAD SCORES WERE ELIMINATING AREN'T DUE TO LUCK BC WE ENSURE ALL POSSIBLE SPAWNS ARE CONSIDERED
                if len(direction_scores_to_avg) == 0:
                    print("len(direction_scores_to_avg) = 0!!")
                    print(f"len boards4, 2, depth dict: {len(boards4)}, {len(boards2)}, {depth_dict_4[num_open_tiles]}")
                    print(f"CURRENTLY ON DIRECTION {direction}, {move_dict[direction]}")
                    time.sleep(10)
        if self.verbose:
            print(np.array(scores).round())
        best_direction = scores.index(max(scores))  # THIS SHOULD BE UPDATED TO EXPECTED VALUE CALCULATION. DONE IN MC7

        if self.verbose:
            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(np.nanmax(scores))}, "  # BAND AID SOLN to ignore NANs but idk what causes them
                  f"#EVALs: {len(boards4)}")

        self.main_game.move(best_direction)
        if self.verbose:
            self.main_game.board.print()

    @staticmethod
    def get_possible_boards(board) -> tuple[list, list]:
        """
        takes current board, returns list of all possible board "responses"
        :param board: board of time (Board) (custom object),
        :return: ([boards with 2s], [boards with 4s])
        """

        # print("IN GET POSSIBLE BOARDS with baord =")
        # board.print(2)
        # print("DONE START OF IN GET POSSIBLE BOARDS with baord =")
        boards2, boards4 = [], []
        # print("------------------------new enter into get possible boards----------------------------")
        # print("BOARD IN THE FN = ")
        # board.print()
        for new_tile_value in (2, 4):
            # print(f"board.get_empty_tiles() = {board.get_empty_tiles()}")
            for y, x in board.get_empty_tiles():
                new_board = copy.deepcopy(board)  # THIS IS WHERE THE ERROR IS FROM
                new_board.add_tile(tile_value=new_tile_value, x_coord=x, y_coord=y)
                # print("MAGIC")
                # new_board.print(2)
                # time.sleep(1)
                if new_tile_value == 2:
                    boards2.append(new_board)
                else:
                    boards4.append(new_board)
        # print("DONE POSSIBLE BOARDS")
        return boards2, boards4  # MB the nan are caused by boards that cant get evaluated for some reason...?

    def run(self):
        start_time = time.time()
        while not self.main_game.game_over_check():
            self.n_games()
            if self.main_game.use_gui:
                self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")
        save_game_result_to_csv("MC6", "MC6", self.main_game.score, total_time, self.main_game.board.board)


class MC7:
    """
    EVALUATES ALL POSSIBLE NEXT MOVES. USES EXPECTED VALUE EVALUATION, WHICH TURNS OUT TO GIVE SAME ANSWER AS MC6 EVALUATION
    WHEN ALL POSSIBLE MOVES ARE CONSIDERED
    """
    def __init__(self, game, game_obj, sims_per_turn: int = 100, verbose: bool = True) -> None:
        self.main_game = game
        self.game_obj = game_obj
        self.sims_per_turn = sims_per_turn
        self.verbose = verbose

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):
        depth_dict_4 = {
            15: 1,
            14: 1,
            13: 1,
            12: 1,
            11: 1,
            10: 1,
            9: 1,
            8: 2,
            7: 2,  # 126 for 2
            6: 2,  # 108 for 2
            5: 3,  # 135 for 2
            4: 4,  # 144 for 2
            3: 5,  # 135 for 2
            2: 8,  # 144 for 2
            1: 15  # 135 for 2
        }

        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        mc6_scores = []
        for direction in range(4):
            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False, add_tile=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
            else:
                # THIS IS WHERE WE MAKE THE NODES START
                # take board we're currently working on, get list of all possible tiles that could spawn
                boards2, boards4 = self.get_possible_boards(game_copy.board)
                # print("GOT BOARDS")
                # print("BOARDS4 START")
                # print(boards4)
                # print("BOARDS4 END")
                num_empty_tiles = len(boards2)
                direction_scores_to_avg2, direction_scores_to_avg4 = [], []
                for board in boards4:  # for each board, do necessary depth
                    for depth in range(depth_dict_4[num_empty_tiles]):

                        # make new game obj

                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score
                        # print("MADE OBJ IN LOOP OF BOARDS4")
                        # current_game_obj.display_updated_board()  # temp line!
                        # time.sleep(1)
                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        direction_scores_to_avg4.append(current_score)
                        # print("DONE LOOP OF BOARDS4")
                for board in boards2:  # this can be condensed, only diff is *9 in second for statement
                    for depth in range(depth_dict_4[num_empty_tiles] * 9):  # * 9 bc 90% chance of 2 spawning
                        # make new game obj
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        direction_scores_to_avg2.append(current_score)


                scores.append(self.expected_value(direction_scores_to_avg4, direction_scores_to_avg2, num_empty_tiles))
                mc6_scores.append(np.average(np.array(direction_scores_to_avg4 + direction_scores_to_avg2)))
                # finish evaluation, then add piece
                game_copy.add_new_tile()
        if self.verbose:
            print(f"MC6 SCORES: {np.array(mc6_scores).round()}")
            print(f"MC7 SCORES: {np.array(scores).round()}")
        best_direction = scores.index(max(scores))  # THIS SHOULD BE UPDATED

        if self.verbose:
            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(np.nanmax(scores))}"
                  f"4,2 #EVALs: {len(boards4), len(boards2)}")

        self.main_game.move(best_direction)
        if self.verbose:
            self.main_game.board.print()

    @staticmethod
    def expected_value(scores4, scores2, num_empty):
        """DOES CALCULATION IN BLUE CIRCLE ON WHITEBOARD PIC JUN ^
        THIS COULD BE VECTORIZED FOR MORE SPEED
        SEEMS TO GIVE ALMOST THE EXACT SAME SCORE AS MC6 BUT SOMETIEMS ONE IS WAY LOWER
        """
        scores2, scores4 = np.array(scores2), np.array(scores4)
        output2 = 1 / num_empty
        # output2 += np.sum(scores4 * 0.1) / len(scores4)
        # output2 += np.sum(scores2 * 0.9) / len(scores2)
        output2 += np.mean(scores4) * 0.1  # DOES SAME THING AS ORIGINAL BUT FASTER
        output2 += np.mean(scores2) * 0.9
        # output = 1 / num_empty
        # for i in scores4:
        #     output += i * 0.1 / len(scores4) # divide by len to scale properly. wait but mb multiplying by 0.1 does the scaling bc len(scores4) = 0.1 len(scores2)
        # for i in scores2:
        #     output += np.average(scores2) * 0.9
            # output += i * 0.9 / len(scores2)
        # print(f"OUTPUT = {output}")
        # print(f"OUTPUT1=OUTPUT2: {round(output) == round(output2)}")
        # print(f"OUTPUT1 and 2: {output, output2}")
        return output2

    @staticmethod
    def get_possible_boards(board) -> tuple[list, list]:
        """
        takes current board, returns list of all possible board "responses"
        :param board: board of time (Board) (custom object),
        :return: ([boards with 2s], [boards with 4s])
        """
        # print("IN GET POSSIBLE BOARDS with baord =")
        # board.print(2)
        # print("DONE START OF IN GET POSSIBLE BOARDS with baord =")
        boards2, boards4 = [], []
        for new_tile_value in (2, 4):
            for y, x in board.get_empty_tiles():
                new_board = copy.deepcopy(board)  # THIS IS WHERE THE ERROR IS FROM
                new_board.add_tile(tile_value=2, x_coord=x, y_coord=y)
                # print("MAGIC")
                # new_board.print(2)
                # time.sleep(1)
                if new_tile_value == 2:
                    boards2.append(new_board)
                else:
                    boards4.append(new_board)
        return boards2, boards4

    def run(self):
        start_time = time.time()
        while not self.main_game.game_over_check():
            self.n_games()
            if self.verbose:
                self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")
        save_game_result_to_csv("MC7", "MC7", self.main_game.score, total_time, self.main_game.board.board)


class MC8:
    """
    MC7 but evaluates top half of moves
    Gets very fast when the board starts filling up
    still not fantastic

    try max instead of avg bc all nodes are covered
    wait I think this eliminates whole nodes bc its not seperate lists
    """
    def __init__(self, game, game_obj, sims_per_turn: int = 100, verbose: bool = True) -> None:
        self.main_game = game
        self.game_obj = game_obj
        self.sims_per_turn = sims_per_turn
        self.verbose = verbose

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):
        depth_dict_4 = {
            15: 1,  # 135 for 2; total: 138
            14: 1,  # 126 for 2; total: 141
            13: 1,  # 117 for 2; total: 130
            12: 1,  # 108 for 2; total: 123
            11: 1,  # 99 for 2; total: 114
            10: 1,  # 90 for 2; total: 103
            9: 1,  # 81 for 2; total: 92
            8: 2,  # 144 for 2; total: 154
            7: 2,  # 126 for 2; total: 135
            6: 2,  # 108 for 2; total: 116
            5: 3,  # 135 for 2; total: 143
            4: 4,  # 144 for 2; total: 152
            3: 5,  # 135 for 2; total: 143
            2: 8,  # 144 for 2; total: 154
            1: 15  # 135 for 2; total: 151
        }

        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        mc6_scores = []
        for direction in range(4):
            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False, add_tile=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
            else:
                # THIS IS WHERE WE MAKE THE NODES START
                # take board we're currently working on, get list of all possible tiles that could spawn
                boards2, boards4 = self.get_possible_boards(game_copy.board)
                # print("GOT BOARDS")
                # print("BOARDS4 START")
                # print(boards4)
                # print("BOARDS4 END")
                num_empty_tiles = len(boards2)
                direction_scores_to_avg2, direction_scores_to_avg4 = [], []
                for board in boards4:  # for each board, do necessary depth
                    for depth in range(depth_dict_4[num_empty_tiles]):

                        # make new game obj

                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score
                        # print("MADE OBJ IN LOOP OF BOARDS4")
                        # current_game_obj.display_updated_board()  # temp line!
                        # time.sleep(1)
                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        direction_scores_to_avg4.append(current_score)
                        # print("DONE LOOP OF BOARDS4")
                for board in boards2:  # this can be condensed, only diff is *9 in second for statement
                    for depth in range(depth_dict_4[num_empty_tiles] * 9):  # * 9 bc 90% chance of 2 spawning
                        # make new game obj
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        direction_scores_to_avg2.append(current_score)


                scores.append(self.expected_value(direction_scores_to_avg4, direction_scores_to_avg2, num_empty_tiles))
                mc6_scores.append(np.average(np.array(direction_scores_to_avg4 + direction_scores_to_avg2)))
                # finish evaluation, then add piece
                game_copy.add_new_tile()
        if self.verbose:
            print(f"MC6 SCORES: {np.array(mc6_scores).round()}")
            print(f"MC8 SCORES: {np.array(scores).round()}")
        best_direction = scores.index(max(scores))  # THIS SHOULD BE UPDATED

        if self.verbose:
            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(np.nanmax(scores))}\n")

        self.main_game.move(best_direction)
        if self.verbose:
            self.main_game.board.print()

    @staticmethod
    def expected_value(scores4, scores2, num_empty):
        """
        Calculate the expected value based on scores4 and scores2 arrays.
        WHITEBOARD CALCULATION
        Args:
            scores4 (list or ndarray): Scores monte carlo tree got for 4 spawning next.
            scores2 (list or ndarray): Scores monte carlo tree got for 2 spawning next.
            num_empty (int): Number of empty cells in the game board.

        Returns:
            float: The expected value.
        """
        scores2, scores4 = np.array(scores2), np.array(scores4)
        # scores2, scores4 = np.sort(scores2)[::-1], np.sort(scores4)[::-1]
        # output2 = 1 / num_empty
        #
        # output2 += np.mean(scores4[:math.ceil(len(scores4)/2)]) * 0.1  # DOES SAME THING AS ORIGINAL BUT FASTER
        # output2 += np.mean(scores2[:math.ceil(len(scores2)/2)]) * 0.9
        #

        # OUTPUT 2 and 3 are equivalent but output 3 is faster
        # Compute the mean of the top half of scores4 and scores2
        len_scores_4 = len(scores4)
        len_scores_2 = len_scores_4 * 9
        top_scores4_mean = np.mean(scores4[np.argsort(-scores4)[:math.ceil(len_scores_4 / 2)]])
        top_scores2_mean = np.mean(scores2[np.argsort(-scores2)[:math.ceil(len_scores_2 / 2)]])

        output3 = 1 / num_empty
        output3 += top_scores4_mean * 0.1
        output3 += top_scores2_mean * 0.9
        # print(f"OUTPUT3 {output3}")
        # print(f"OUTPUT2 {output2}")
        # print(f"OUTPUT3=2 {output2.round(2) == output3.round(2)}")
        # print(f"Len scores4, len scores2, empty {len(scores2), len(scores4), num_empty}"
        #       f"16-len = num_empty {16 - len(scores4) == num_empty}")
        return output3

    @staticmethod
    def get_possible_boards(board) -> tuple[list, list]:
        """
        takes current board, returns list of all possible board "responses"
        :param board: board of time (Board) (custom object),
        :return: ([boards with 2s], [boards with 4s])
        """
        # print("IN GET POSSIBLE BOARDS with baord =")
        # board.print(2)
        # print("DONE START OF IN GET POSSIBLE BOARDS with baord =")
        boards2, boards4 = [], []
        for new_tile_value in (2, 4):
            for y, x in board.get_empty_tiles():
                new_board = copy.deepcopy(board)  # THIS IS WHERE THE ERROR IS FROM
                new_board.add_tile(tile_value=2, x_coord=x, y_coord=y)
                # print("MAGIC")
                # new_board.print(2)
                # time.sleep(1)
                if new_tile_value == 2:
                    boards2.append(new_board)
                else:
                    boards4.append(new_board)
        return boards2, boards4

    def run(self):
        start_time = time.time()
        while not self.main_game.game_over_check():
            self.n_games()
            if self.main_game.use_gui:
                self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")
        save_game_result_to_csv("MC8", "MC8", self.main_game.score, total_time, self.main_game.board.board)


class MC9:
    """
    LIKE MC8 but only does top 2 moves
    mistake (as is MC8) bc doesn't use different lists for different nodes
    """
    def __init__(self, game, game_obj, verbose: bool = True) -> None:
        self.main_game = game
        self.game_obj = game_obj
        self.verbose = verbose  # got rid of sims_per_turn

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):
        depth_dict_4 = {
            15: 1,  # 135 for 2; total: 138
            14: 1,  # 126 for 2; total: 141
            13: 1,  # 117 for 2; total: 130
            12: 1,  # 108 for 2; total: 123
            11: 1,  # 99 for 2; total: 114
            10: 1,  # 90 for 2; total: 103
            9: 1,  # 81 for 2; total: 92
            8: 2,  # 144 for 2; total: 154
            7: 2,  # 126 for 2; total: 135
            6: 2,  # 108 for 2; total: 116
            5: 3,  # 135 for 2; total: 143
            4: 4,  # 144 for 2; total: 152
            3: 5,  # 135 for 2; total: 143
            2: 8,  # 144 for 2; total: 154
            1: 15  # 135 for 2; total: 151
        }

        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        mc6_scores = []
        for direction in range(4):
            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False, add_tile=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
            else:

                # take board we're currently working on, get list of all possible tiles that could spawn
                boards2, boards4 = self.get_possible_boards(game_copy.board)

                num_empty_tiles = len(boards2)
                direction_scores_to_avg2, direction_scores_to_avg4 = [], []
                for board in boards4:  # for each board, do necessary depth
                    for depth in range(depth_dict_4[num_empty_tiles]):
                        # make new game obj to play on where
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score
                        # print("MADE OBJ IN LOOP OF BOARDS4")
                        # current_game_obj.display_updated_board()  # temp line!
                        # time.sleep(1)
                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        direction_scores_to_avg4.append(current_score)
                        # print("DONE LOOP OF BOARDS4")
                for board in boards2:  # this can be condensed, only diff is *9 in second for statement
                    for depth in range(depth_dict_4[num_empty_tiles] * 9):  # * 9 bc 90% chance of 2 spawning
                        # make new game obj
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        direction_scores_to_avg2.append(current_score)  # NEED TO GET IT SO THAT IT HAS A LIST FOR EACH NODE MAYBE ON A NEXT ITERATION IF THIS WORKS WELL


                scores.append(self.expected_value(direction_scores_to_avg4, direction_scores_to_avg2, num_empty_tiles))
                mc6_scores.append(np.average(np.array(direction_scores_to_avg4 + direction_scores_to_avg2)))
                # finish evaluation, then add piece
                game_copy.add_new_tile()
        if self.verbose:
            print(f"MC6 SCORES: {np.array(mc6_scores).round()}")
            print(f"MC8 SCORES: {np.array(scores).round()}")
        best_direction = scores.index(max(scores))

        if self.verbose:
            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(max(scores))}\n")

        self.main_game.move(best_direction)
        if self.verbose:
            self.main_game.board.print()

    @staticmethod
    def expected_value(scores4, scores2, num_empty):
        """
        Calculate the expected value based on scores4 and scores2 arrays. Uses top 2 values only
        WHITEBOARD CALCULATION
        Args:
            scores4 (list or ndarray): Scores monte carlo tree got for 4 spawning next.
            scores2 (list or ndarray): Scores monte carlo tree got for 2 spawning next.
            num_empty (int): Number of empty cells in the game board.

        Returns:
            float: The expected value.
        """
        scores2, scores4 = np.array(scores2), np.array(scores4)

        top_scores4_mean_top2 = np.mean(scores4[np.argsort(-scores4)[:2]])
        top_scores2_mean_top2 = np.mean(scores2[np.argsort(-scores2)[:2]])

        output = 1 / num_empty
        output += top_scores4_mean_top2 * 0.1
        output += top_scores2_mean_top2 * 0.9

        return output

    @staticmethod
    def get_possible_boards(board) -> tuple[list, list]:
        """
        takes current board, returns list of all possible board "responses"
        :param board: board of time (Board) (custom object),
        :return: ([boards with 2s], [boards with 4s])
        """
        # print("IN GET POSSIBLE BOARDS with baord =")
        # board.print(2)
        # print("DONE START OF IN GET POSSIBLE BOARDS with baord =")
        boards2, boards4 = [], []
        for new_tile_value in (2, 4):
            for y, x in board.get_empty_tiles():
                new_board = copy.deepcopy(board)  # THIS IS WHERE THE ERROR IS FROM
                new_board.add_tile(tile_value=2, x_coord=x, y_coord=y)
                # print("MAGIC")
                # new_board.print(2)
                # time.sleep(1)
                if new_tile_value == 2:
                    boards2.append(new_board)
                else:
                    boards4.append(new_board)
        return boards2, boards4

    def run(self):
        start_time = time.time()
        while not self.main_game.game_over_check():
            self.n_games()
            if self.main_game.use_gui:
                self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")
        save_game_result_to_csv("MC9", "MC9", self.main_game.score, total_time, self.main_game.board.board)


class MC10:
    """
    Aim to make list for each node to get expected value
    this is super fast. should increase number of bots for
    """
    def __init__(self, game, game_obj, best_proportion: float = 0.5, verbose: bool = True) -> None:
        self.main_game = game
        self.game_obj = game_obj
        self.verbose = verbose
        self.best_proportion = best_proportion

        self.almost_lost_fix = 0

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):
        depth_dict_4 = {
            15: 1,  # 135 for 2; total: 138
            14: 1,  # 126 for 2; total: 141
            13: 1,  # 117 for 2; total: 130
            12: 1,  # 108 for 2; total: 123
            11: 1,  # 99 for 2; total: 114
            10: 1,  # 90 for 2; total: 103
            9: 1,  # 81 for 2; total: 92
            8: 2,  # 144 for 2; total: 154
            7: 2,  # 126 for 2; total: 135
            6: 2,  # 108 for 2; total: 116
            5: 4,  # 180 for 2; total: 200
            4: 6,  # 216 for 2; total: 240
            3: 9,  # 243 for 2; total: 270
            2: 13,  # 234 for 2; total: 260
            1: 25  # 225 for 2; total: 250
        }

        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        for direction in range(4):
            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False, add_tile=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
            else:

                # take board we're currently working on, get list of all possible tiles that could spawn
                boards2, boards4 = self.get_possible_boards(game_copy.board)

                num_empty_tiles = len(boards2)
                direction_scores_to_avg2, direction_scores_to_avg4 = [], []
                for board in boards4:  # for each board, do necessary depth
                    inner_scores4 = []
                    for depth in range(depth_dict_4[num_empty_tiles]):
                        # make new game obj to play on where
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        inner_scores4.append(current_score)
                    direction_scores_to_avg4.append(inner_scores4)

                for board in boards2:  # this can be condensed, only diff is *9 in second for statement
                    inner_scores2 = []
                    for depth in range(depth_dict_4[num_empty_tiles] * 9):  # * 9 bc 90% chance of 2 spawning
                        # make new game obj
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        inner_scores2.append(current_score)
                    direction_scores_to_avg2.append(inner_scores2)


                scores.append(self.expected_value(direction_scores_to_avg4, direction_scores_to_avg2, num_empty_tiles))
                # mc6_scores.append(np.average(np.array(direction_scores_to_avg4 + direction_scores_to_avg2)))
                # finish evaluation, then add piece
                game_copy.add_new_tile()

        if np.all(scores == self.main_game.score):  # if all direction scores are equal to the current then its about to end, which can cause an error. this makes it randomly cycle thru picking each move, which guarantees a legal one will be made so the game can end
            best_direction = scores[self.almost_lost_fix]
            self.almost_lost_fix += 1
            self.almost_lost_fix = self.almost_lost_fix % 4
            # this didn't seem to work, so for the sake of time, I'll return false early and end the sim
            return False  # returns false for early termination
        else:  # the normal case
            best_direction = scores.index(max(scores))

        if self.verbose:
            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(max(scores))}\n")

        self.main_game.move(best_direction)
        if self.verbose and self.main_game.use_gui:
            self.main_game.board.print()
        return True  # returns true for continuing


    def expected_value(self, scores4, scores2, num_empty):
        """
        Calculate the expected value based on scores4 and scores2 arrays. Uses top 2 values only
        WHITEBOARD CALCULATION
        Args:
            scores4 (list or ndarray): Scores monte carlo tree got for 4 spawning next.
            scores2 (list or ndarray): Scores monte carlo tree got for 2 spawning next.
            num_empty (int): Number of empty cells in the game board.

        Returns:
            float: The expected value.
        """
        scores2, scores4 = np.array(scores2), np.array(scores4)
        # for arr in scores2:
        #     sorted_arr = arr[np.argsort(-arr)]
        #     if len(arr) >= 2:
        #         current = sorted_arr[:2]
        #     else:
        #         current = sorted_arr

        # print("scores 2, 4")
        # sorted_indices = np.argsort(-scores2, axis=1)
        # sorted_scores2 = np.take_along_axis(scores2, sorted_indices, axis=1)
        # print(sorted_scores2)
        # print(scores4.sort()[::-1])
        # print("------------------------NOW CURRENT scores2_top------------------------------------------------------------------------------------------------")
        # print(scores2_top)
        # print("------------------------NOW CURRENT ARR2 on scores4------------------------------------------------------------------------------------------------")
        scores2_top = np.partition(scores2, -math.ceil((scores2.shape[1]) * self.best_proportion), axis=1)[:, -math.ceil((scores2.shape[1]) * self.best_proportion):]  # had the math.ceil... has 2 so it would take the top 2. now it takes top half

        if scores4.shape[1] < 2:
            scores4_top = scores4
        else:
            scores4_top = np.partition(scores4, -math.ceil((scores4.shape[1]) * self.best_proportion), axis=1)[:, -math.ceil((scores4.shape[1]) * self.best_proportion):]  # replace the 2s with whatever length needed


        # time.sleep(10)
        # top_scores4_mean_top2 = np.mean(scores4[np.argsort(-scores4)[:2]])
        # top_scores2_mean_top2 = np.mean(scores2[np.argsort(-scores2)[:2]])

        # THIS IS WHATS GOOD
        # expected_value = 1 / num_empty
        # for node_scores in scores2_top:
        #     expected_value += 0.9 * np.average(node_scores)
        # for node_scores in scores4_top:
        #     expected_value += 0.1 * np.average(node_scores)
        # end this is whats good

        # score += 1 / (empty * 2) * 0.1 *  avg_of_top2# times 2 in denom bc there's one for each of . wait but one of the above ones gave same answers as one that didn't use expcted value fn and it didnt use /2
        # makes sense bc above line happens once for each empty tile, then needs to happen again for the 4s
        # do 0.1 and 0.9 need to be divided by 2? I dont think so

        # FOR DEBUG PURPOSES HERE
        # print(scores2_top)
        # time.sleep(1)


        expected_value = 0
        for node_scores in scores2_top:
            expected_value += np.average(node_scores) * 0.9 * 1/ num_empty
        # print(f"EXPECTED AFTER 2s {expected_value}")
        for node_scores in scores4_top:
            expected_value += np.average(node_scores) * 0.1 * 1/ num_empty
        # print(f"EXPECTED AFTER 4s {expected_value}")
        # time.sleep(10)
        return expected_value

    @staticmethod
    def get_possible_boards(board) -> tuple[list, list]:
        """
        takes current board, returns list of all possible board "responses"
        :param board: board of time (Board) (custom object),
        :return: ([boards with 2s], [boards with 4s])
        """
        # print("IN GET POSSIBLE BOARDS with baord =")
        # board.print(2)
        # print("DONE START OF IN GET POSSIBLE BOARDS with baord =")
        boards2, boards4 = [], []
        for new_tile_value in (2, 4):
            for y, x in board.get_empty_tiles():
                new_board = copy.deepcopy(board)  # THIS IS WHERE THE ERROR IS FROM
                new_board.add_tile(tile_value=2, x_coord=x, y_coord=y)
                # print("MAGIC")
                # new_board.print(2)
                # time.sleep(1)
                if new_tile_value == 2:
                    boards2.append(new_board)
                else:
                    boards4.append(new_board)
        return boards2, boards4

    def run(self):
        start_time = time.time()
        while not self.main_game.game_over_check():
            if not self.n_games():  # if it returns false, that's a signal to terminate early
                break
            if self.main_game.use_gui:
                self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")
        save_game_result_to_csv("MC10", f"MC10_top_{self.best_proportion*100:.1f}%", self.main_game.score, total_time, self.main_game.board.board)


class MC11:
    """
    MC10 but has reward for highest tile in the corner

    clearly sucks (at least with corner_reward: float = 0.1, best_proportion: float = 0.5)
    """
    def __init__(self, game, game_obj, corner_reward: float = 0.05, best_proportion: float = 0.5, verbose: bool = True) -> None:
        self.main_game = game
        self.game_obj = game_obj
        self.verbose = verbose
        self.best_proportion = best_proportion
        self.corner_reward = 1 + corner_reward

        self.almost_lost_fix = 0

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):
        depth_dict_4 = {
            15: 1,  # 135 for 2; total: 138
            14: 1,  # 126 for 2; total: 141
            13: 1,  # 117 for 2; total: 130
            12: 1,  # 108 for 2; total: 123
            11: 1,  # 99 for 2; total: 114
            10: 1,  # 90 for 2; total: 103
            9: 1,  # 81 for 2; total: 92
            8: 2,  # 144 for 2; total: 154
            7: 2,  # 126 for 2; total: 135
            6: 2,  # 108 for 2; total: 116
            5: 4,  # 180 for 2; total: 200
            4: 6,  # 216 for 2; total: 240
            3: 9,  # 243 for 2; total: 270
            2: 13,  # 234 for 2; total: 260
            1: 25  # 225 for 2; total: 250
        }

        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        highest_tile_locations = []
        for direction in range(4):
            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False, add_tile=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
                highest_tile_locations.append((42, 42))  # if we can't move in a direction, don't give honest high tile location, because we don't want bonus to apply (would enable looping illegal moves)
            else:
                highest_tile_value = game_copy.highest_tile
                highest_tile_location = game_copy.board.tile_coords(tile_value=highest_tile_value)
                highest_tile_locations.append(highest_tile_location)

                # take board we're currently working on, get list of all possible tiles that could spawn
                boards2, boards4 = self.get_possible_boards(game_copy.board)

                num_empty_tiles = len(boards2)
                direction_scores_to_avg2, direction_scores_to_avg4 = [], []
                for board in boards4:  # for each board, do necessary depth
                    inner_scores4 = []
                    for depth in range(depth_dict_4[num_empty_tiles]):
                        # make new game obj to play on where
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        inner_scores4.append(current_score)
                    direction_scores_to_avg4.append(inner_scores4)

                for board in boards2:  # this can be condensed, only diff is *9 in second for statement
                    inner_scores2 = []
                    for depth in range(depth_dict_4[num_empty_tiles] * 9):  # * 9 bc 90% chance of 2 spawning
                        # make new game obj
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        inner_scores2.append(current_score)
                    direction_scores_to_avg2.append(inner_scores2)


                scores.append(self.expected_value(direction_scores_to_avg4, direction_scores_to_avg2, num_empty_tiles))
                # finish evaluation, then add piece
                game_copy.add_new_tile()

        scores = np.array(scores)  # turn it into array for faster stuff
        if np.all(scores == self.main_game.score):  # if all direction scores are equal to the current then its about to end, which can cause an error. this makes it randomly cycle thru picking each move, which guarantees a legal one will be made so the game can end
            best_direction = scores[self.almost_lost_fix]
            self.almost_lost_fix += 1
            self.almost_lost_fix = self.almost_lost_fix % 4
        else:  # the normal case
            scores = self.high_tile_corner_bonus(scores, highest_tile_locations)
            best_direction = np.argmax(scores)

        if self.verbose:
            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(max(scores))}\n")

        self.main_game.move(best_direction)
        highest_from_horses_mouth = self.main_game.highest_tile
        print(
            f"highest tile after move= {highest_from_horses_mouth} at {self.main_game.board.tile_coords(highest_from_horses_mouth)}")
        if self.verbose and self.main_game.use_gui:
            self.main_game.board.print(len(str(self.main_game.highest_tile)))

    def high_tile_corner_bonus(self, scores: np.ndarray, highest_tile_value_locations: list):
        """
        If a move results in the highest tile staying in a corner, a reward multiple of self.corner_reward is applied
        :param scores: scores according to each direction
        :param highest_tile_value_locations: location of highest tile after the move (index matches scores param)
        :return:
        """

        for direction, score in enumerate(scores):
            print("high tile:")
            print(highest_tile_value_locations)
            # highest_from_horses_mouth = self.main_game.highest_tile
            # print(f"highest tile = {highest_from_horses_mouth} at {self.main_game.board.tile_coords(highest_from_horses_mouth)}")
            print("----")
            if highest_tile_value_locations[direction] in ((0, 0), (0, 3), (3, 0), (3, 3)):
                print("GET CORNER REWARD")
                scores[direction] *= self.corner_reward
        return scores

    def expected_value(self, scores4, scores2, num_empty):
        """
        Calculate the expected value based on scores4 and scores2 arrays. Uses top 2 values only
        WHITEBOARD CALCULATION
        Args:
            scores4 (list or ndarray): Scores monte carlo tree got for 4 spawning next.
            scores2 (list or ndarray): Scores monte carlo tree got for 2 spawning next.
            num_empty (int): Number of empty cells in the game board.

        Returns:
            float: The expected value.
        """
        scores2, scores4 = np.array(scores2), np.array(scores4)

        scores2_top2 = np.partition(scores2, -math.ceil((scores2.shape[1]) * self.best_proportion), axis=1)[:, -math.ceil((scores2.shape[1]) * self.best_proportion):]  # had the math.ceil... has 2 so it would take the top 2. now it takes top half

        if scores4.shape[1] < 2:
            scores4_top2 = scores4
        else:
            scores4_top2 = np.partition(scores4, -math.ceil((scores4.shape[1]) * self.best_proportion), axis=1)[:, -math.ceil((scores4.shape[1]) * self.best_proportion):]  # replace the 2s with whatever length needed

        expected_value = 0
        for node_scores in scores2_top2:
            expected_value += np.average(node_scores) * 0.9 * 1/ num_empty
        # print(f"EXPECTED AFTER 2s {expected_value}")
        for node_scores in scores4_top2:
            expected_value += np.average(node_scores) * 0.1 * 1/ num_empty
        # print(f"EXPECTED AFTER 4s {expected_value}")
        return expected_value

    @staticmethod
    def get_possible_boards(board) -> tuple[list, list]:
        """
        takes current board, returns list of all possible board "responses"
        :param board: board of time (Board) (custom object),
        :return: ([boards with 2s], [boards with 4s])
        """
        # print("IN GET POSSIBLE BOARDS with baord =")
        # board.print(2)
        # print("DONE START OF IN GET POSSIBLE BOARDS with baord =")
        boards2, boards4 = [], []
        for new_tile_value in (2, 4):
            for y, x in board.get_empty_tiles():
                new_board = copy.deepcopy(board)  # THIS IS WHERE THE ERROR IS FROM
                new_board.add_tile(tile_value=2, x_coord=x, y_coord=y)
                # print("MAGIC")
                # new_board.print(2)
                # time.sleep(1)
                if new_tile_value == 2:
                    boards2.append(new_board)
                else:
                    boards4.append(new_board)
        return boards2, boards4

    def run(self):
        start_time = time.time()
        while not self.main_game.game_over_check():
            self.n_games()
            if self.main_game.use_gui:
                self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")
        save_game_result_to_csv("MC11",
                                f"MC11_top_{self.best_proportion*100:.1f}_rwd_{self.corner_reward - 1}",
                                self.main_game.score, total_time,
                                self.main_game.board.board)



class MC12:
    """
    Same as MC10 but customizable depth dicts for 2 and 4 (and higher defaults for all 4s)
    HOLY SHIT REALIZED MC10 AND 12 SPAWN 2S WHEN I MEAN TO SPAWN 4S. SHOULD INCREASE PERFORMANCE WITH NOW IMPLIMENTED FIX!!
    """
    def __init__(self, game, game_obj, depth4: dict = None, depth2: dict = None, best_proportion: float = 1, verbose: bool = True) -> None:
        self.main_game = game
        self.game_obj = game_obj
        self.verbose = verbose
        self.best_proportion = best_proportion
        if depth4 is None:
            self.depth_dict_4 = {
                15: 3,
                14: 3,
                13: 3,
                12: 3,
                11: 3,
                10: 3,
                9: 3,
                8: 3,
                7: 3,
                6: 3,
                5: 5,
                4: 7,
                3: 20,
                2: 40,
                1: 80
            }
        else:
            self.depth_dict_4 = depth4
        if depth2 is None:
            self.depth_dict_2 = {
                15: 9,  # 135
                14: 9,  # 126
                13: 9,  # 117
                12: 9,  # 108
                11: 9,  # 99
                10: 9,  # 90
                9: 9,  # 81
                8: 18,  # 144
                7: 18,  # 126
                6: 18,  # 108
                5: 36,  # 180
                4: 54,  # 216
                3: 125,  # 243
                2: 250,  # 234
                1: 500  # 225
            }
        else:
            self.depth_dict_2 = depth2
        self.normal_strength = depth2 is None or depth4 is None

        self.almost_lost_fix = 0

    @staticmethod
    def one_game(game):
        """
        Where all the magic happens: plays random moves until the game is over
        args:
            game (Game): game object to manipulate
        """
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            game.move(current_direction, print_board=False, illegal_warn=False)
        else:
            return game.score

    def n_games(self):


        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        for direction in range(4):
            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False, add_tile=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                scores.append(game_copy.score)
            else:

                # take board we're currently working on, get list of all possible tiles that could spawn
                boards2, boards4 = self.get_possible_boards(game_copy.board)

                num_empty_tiles = len(boards2)
                direction_scores_to_avg2, direction_scores_to_avg4 = [], []
                for board in boards4:  # for each board, do necessary depth
                    inner_scores4 = []
                    for depth in range(self.depth_dict_4[num_empty_tiles]):
                        # make new game obj to play on where
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        inner_scores4.append(current_score)
                    direction_scores_to_avg4.append(inner_scores4)

                for board in boards2:  # this can be condensed, only diff is *9 in second for statement
                    inner_scores2 = []
                    for depth in range(self.depth_dict_2[num_empty_tiles]):
                        # make new game obj
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = game_copy.score

                        current_score = self.one_game(copy.deepcopy(current_game_obj))
                        inner_scores2.append(current_score)
                    direction_scores_to_avg2.append(inner_scores2)


                scores.append(self.expected_value(direction_scores_to_avg4, direction_scores_to_avg2, num_empty_tiles))
                # mc6_scores.append(np.average(np.array(direction_scores_to_avg4 + direction_scores_to_avg2)))
                # finish evaluation, then add piece
                game_copy.add_new_tile()

        scores = np.array(scores)
        if np.all(scores == self.main_game.score):  # if all direction scores are equal to the current then its about to end, which can cause an error. this makes it randomly cycle thru picking each move, which guarantees a legal one will be made so the game can end
            print("MADE IT IN")

            best_direction = self.almost_lost_fix
            self.almost_lost_fix += 1
            self.almost_lost_fix = self.almost_lost_fix % 4
        else:  # the normal case
            best_direction = np.argmax(scores)


        if self.verbose:
            print(f"{np.array(scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(max(scores))}\n")

        self.main_game.move(best_direction)
        if self.verbose and self.main_game.use_gui:
            self.main_game.board.print()
        return True  # returns true for continuing


    def expected_value(self, scores4, scores2, num_empty):
        """
        Calculate the expected value based on scores4 and scores2 arrays. Uses top 2 values only
        WHITEBOARD CALCULATION
        Args:
            scores4 (list or ndarray): Scores monte carlo tree got for 4 spawning next.
            scores2 (list or ndarray): Scores monte carlo tree got for 2 spawning next.
            num_empty (int): Number of empty cells in the game board.

        Returns:
            float: The expected value.
        """
        scores2, scores4 = np.array(scores2), np.array(scores4)

        scores2_top = np.partition(scores2, -math.ceil((scores2.shape[1]) * self.best_proportion), axis=1)[:, -math.ceil((scores2.shape[1]) * self.best_proportion):]  # had the math.ceil... has 2 so it would take the top 2. now it takes top half

        if scores4.shape[1] < 2:
            scores4_top = scores4
        else:
            scores4_top = np.partition(scores4, -math.ceil((scores4.shape[1]) * self.best_proportion), axis=1)[:, -math.ceil((scores4.shape[1]) * self.best_proportion):]  # replace the 2s with whatever length needed

        expected_value = 0
        for node_scores in scores2_top:
            expected_value += np.average(node_scores) * 0.9 * 1/ num_empty
        # print(f"EXPECTED AFTER 2s {expected_value}")
        for node_scores in scores4_top:
            expected_value += np.average(node_scores) * 0.1 * 1/ num_empty
        # print(f"EXPECTED AFTER 4s {expected_value}")
        return expected_value

    @staticmethod
    def get_possible_boards(board) -> tuple[list, list]:
        """
        takes current board, returns list of all possible board "responses"
        :param board: board of time (Board) (custom object),
        :return: ([boards with 2s], [boards with 4s])
        """

        boards2, boards4 = [], []
        for new_tile_value in (2, 4):
            for y, x in board.get_empty_tiles():
                new_board = copy.deepcopy(board)
                new_board.add_tile(tile_value=2, x_coord=x, y_coord=y)

                if new_tile_value == 2:
                    boards2.append(new_board)
                else:
                    boards4.append(new_board)
        return boards2, boards4

    def run(self):
        start_time = time.time()
        while not self.main_game.game_over_check():
            self.n_games()

            if self.main_game.use_gui and self.verbose:
                self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")
        if self.normal_strength:
            strength = "normal"
        else:
            strength = "strong"
        save_game_result_to_csv("MC12",
                                f"MC12_top_{self.best_proportion*100:.1f}_{strength}%",
                                self.main_game.score,
                                total_time, self.main_game.board.board,
                                # other_data={"2dict": self.depth_dict_2, "4dict": self.depth_dict_4},
                                )




class ExplicitTree1:
    def __init__(self, game, game_obj, depth):
        self.main_game = game
        self.game_obj = game_obj
        self.depth = depth

    @staticmethod
    def get_possible_boards(board) -> tuple[list, list]:
        """
        takes current board, returns list of all possible game "responses"
        :param board: board of time (Board) (custom object),
        :return: ([boards with 2s], [boards with 4s])
        """
        boards2, boards4 = [], []
        for new_tile_value in (2, 4):
            for y, x in board.get_empty_tiles():
                new_board = copy.deepcopy(board)
                new_board.add_tile(tile_value=new_tile_value, x_coord=x, y_coord=y)

                if new_tile_value == 2:
                    boards2.append(new_board)
                else:
                    boards4.append(new_board)
        return boards2, boards4

    def tmp(self):
        boards2, boards4 = self.get_possible_boards(self.main_game.board)
        for board in boards2:
            for move_direction in range(4):
                current_obj = self.game_obj(board=board, use_gui=False)
        # for i in boards4:
        #     i.print()
        #     print("--")



