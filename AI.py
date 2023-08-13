import math
import numpy as np
import copy
import time
from all_AI_iterations import save_game_result_to_csv

class MDP2:
    """
    The Monte Carlo-Powered Markov Decision Process AI described in the paper
    """
    def __init__(self, game, game_obj, core_params: np.ndarray = None, best_proportion = 1, verbose = False):
        """
        Args:
            game: Game object the AI should play
            game_obj (Game): uninitialized Game object
            core_params (np.ndarray): parameters for depth 2 dict generation according to below specification
            best_proportion (float):
            verbose (bool): whether to print intermediate technical results to terminal

        core_params accepts floats. will convert all (except last one) to ints as required

        # depth2 parameter vector needs to have:
        # 1 (1 - 3) scaled
        # 4 (4 - 6) scaled              # no higher than 1
        # 7 (7 - 9) scaled              # no higher than 4
        # 10 (10 - 15) same for all     # no higher than 7
        # 4_depth_scale: how much more powerful 2 should be than 4
        """

        self.main_game = game
        self.game_obj = game_obj
        self.verbose = verbose
        self.best_proportion = best_proportion
        self.core_params = core_params

        if core_params is None:
            core_params = np.array([500, 54, 18, 9, 6.25])

        if len(core_params) != 5:
            raise IndexError(f"{len(core_params)} parameters passed to core params:\n{core_params}\nExactly 5 required")

        self.depth_dict_2 = {
            15: int(core_params[3]),
            14: int(core_params[3]),
            13: int(core_params[3]),
            12: int(core_params[3]),
            11: int(core_params[3]),
            10: int(core_params[3]),
            9: int(core_params[2] // (9 / 7)),
            8: int(core_params[2] // (8 / 7)),
            7: int(core_params[2]),
            6: int(core_params[1] // (6 / 4)),
            5: int(core_params[1] // (5 / 4)),
            4: int(core_params[1]),
            3: int(core_params[0] // 3),
            2: int(core_params[0] // 2),
            1: int(core_params[0])
        }

        self.scaler_4 = core_params[4]
        self.depth_dict_4 = {key: math.ceil(value * 1 / self.scaler_4) for key, value in self.depth_dict_2.items()}

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
        projected_scores = []

        for direction in range(4):
            game_copy = copy.deepcopy(self.main_game)

            if not game_copy.move(direction, print_board=False, illegal_warn=False, add_tile=False):
                # print(f"illegal to move {move_dict[direction]}")  # illegal warn but specifies direction
                projected_scores.append(0)
            else:
                current_score = game_copy.score

                # take board we're currently working on, get list of all possible tiles that could spawn
                boards2, boards4 = self.get_possible_boards(game_copy.board)

                num_empty_tiles = len(boards2)
                direction_scores_to_avg2, direction_scores_to_avg4 = [], []
                for board in boards4:  # for each board, do necessary depth
                    inner_scores4 = []
                    for depth in range(self.depth_dict_4[num_empty_tiles]):
                        # make new game obj to play on where
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = current_score

                        current_inner_score = self.one_game(copy.deepcopy(current_game_obj))
                        inner_scores4.append(current_inner_score)
                    direction_scores_to_avg4.append(inner_scores4)

                for board in boards2:  # this can be condensed, only diff is *9 in second for statement
                    inner_scores2 = []
                    for depth in range(self.depth_dict_2[num_empty_tiles]):
                        # make new game obj
                        current_game_obj = self.game_obj(board=board, use_gui=False)
                        current_game_obj.score = current_score

                        current_inner_score = self.one_game(copy.deepcopy(current_game_obj))
                        inner_scores2.append(current_inner_score)
                    direction_scores_to_avg2.append(inner_scores2)


                projected_scores.append(self.expected_value(direction_scores_to_avg4, direction_scores_to_avg2, num_empty_tiles))

                # finish evaluation, then add piece (because we need to generate states assuming the piece isn't there)
                game_copy.add_new_tile()

        projected_scores = np.array(projected_scores)
        if np.all(projected_scores == self.main_game.score):  # if all direction projected_scores are equal to the current then its about to end, which can cause an error. this makes it randomly cycle thru picking each move, which guarantees a legal one will be made so the game can end
            best_direction = self.almost_lost_fix
            self.almost_lost_fix += 1
            self.almost_lost_fix = self.almost_lost_fix % 4
        else:  # the normal case
            best_direction = np.argmax(projected_scores)

        if self.verbose:
            print(f"{np.array(projected_scores).round()}\t"
                  f"going {move_dict[best_direction]}\t"
                  f"score: {self.main_game.score}\t"
                  f"proj score: {round(max(projected_scores))}\n")

        self.main_game.move(best_direction)  # make the move
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

        scores2_top = np.partition(scores2, -math.ceil((scores2.shape[1]) * self.best_proportion), axis=1)[:, -math.ceil((scores2.shape[1]) * self.best_proportion):]

        if scores4.shape[1] < 2:
            scores4_top = scores4
        else:
            scores4_top = np.partition(scores4, -math.ceil((scores4.shape[1]) * self.best_proportion), axis=1)[:, -math.ceil((scores4.shape[1]) * self.best_proportion):]

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

    def run(self) -> tuple[int, float]:
        """
        Returns: (score, time per move)
        """
        start_time = time.time()
        while not self.main_game.game_over_check():
            self.n_games()

            if self.main_game.use_gui and self.verbose:
                self.main_game.display_updated_board()
        total_time = time.time() - start_time
        print(f"GAME OVER: SCORE = {self.main_game.score}")

        save_game_result_to_csv("MDP2",
                                "MDP2",
                                self.main_game.score,
                                total_time,
                                self.main_game.board.board,
                                other_data={"num_moves": self.main_game.num_moves,
                                            "top_proportion": self.best_proportion,
                                            "core_param_0: (1-3)": self.core_params[0],
                                            "core_param_1: (4-6)": self.core_params[1],
                                            "core_param_2: (7-9)": self.core_params[2],
                                            "core_param_3: (10-15)": self.core_params[3],
                                            "core_param_4: 2/4 strength ratio": self.core_params[4]}
                                )
        return self.main_game.score, round(total_time/self.main_game.num_moves, 2)