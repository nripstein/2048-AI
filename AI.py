import statistics
import copy
import time

import numpy as np

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
                self.game.print_board()

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
                self.game.print_board()
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



class MonteCarloTree:
    def __init__(self, game, depth: int = 50):
        self.game = game

        if type(depth) != int:
            raise TypeError(f"Depth must be an integer, {depth} was entered")
        self.depth = depth

    def simulate_1_game(self, game) -> int:
        """
        simulates one game
        :return: score of the game
        """
        # 1 left, 0 right, up 2, down 3


        # for i in range(100): # this outer loop made it worse
        #     best_score = 0
        #     while True:
        #
        #         if game.game_over_check():
        #             # print("done")
        #             current_score = game.score
        #             if current_score > best_score:
        #                 best_score = current_score
        #                 # print(f"game over with {current_score}")
        #                 # print("------")
        #                 # print(game.print_board())
        #                 # print("------")
        #             break
        #         print("not game over")
        #         current_direction = np.random.randint(0, 4)
        #         if not game.move(current_direction, print_board=False, illegal_warn=False):
        #             # print("illegal move boss")
        #             continue
        #     if i < 3:
        #         print(f"best score on {i} = {best_score}")


        best_score = 0
        while True:
            if game.game_over_check():
                current_score = game.score
                if current_score > best_score:
                    best_score = current_score
                break

            current_direction = np.random.randint(0, 4)
            if not game.move(current_direction, print_board=False, illegal_warn=False):
                # print("illegal move boss")
                continue
        return best_score
    def simulate_1_game2(self, game) -> int:
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            if not game.move(current_direction, print_board=False, illegal_warn=False):
                continue
        return game.score

    def sim3(self, game):
        num_attempts = 50
        best = 0
        scores = []
        for attempt in range(num_attempts):
            game_copy = copy.deepcopy(game)
            while not game_copy.game_over_check():
                current_direction = np.random.randint(0, 4)
                if not game_copy.move(current_direction, print_board=False, illegal_warn=False):
                    continue
            else:
                current_score = game_copy.score
                scores.append(current_score)
                if current_score > best:
                    # print(f"{best} < {current_score}")
                    best = current_score
                    # print(best, current_score)
        # print(scores)
        return best

    def run_simulation(self):
        candidate_scores = []

        for direction in range(4):
            print(direction)
            current_game_copy = copy.deepcopy(self.game)
            current_game_copy.move(direction, print_board=False, illegal_warn=True)
            candidate_scores.append(self.sim3(current_game_copy)) # simulate_1_game can get 1024 but can get stuck

        best_direction = candidate_scores.index(max(candidate_scores))
        self.game.move(best_direction)
        print(best_direction, candidate_scores)

        while not self.game.game_over_check():
            candidate_scores = []
            for direction in range(4):
                # print(direction)
                current_game_copy = copy.deepcopy(self.game)
                current_game_copy.move(direction, print_board=False, illegal_warn=True)
                candidate_scores.append(self.sim3(current_game_copy))

            best_direction = candidate_scores.index(max(candidate_scores))
            self.game.move(best_direction, illegal_warn=False, print_board=True)
            print(best_direction, candidate_scores)

        # current_game_copy = copy.deepcopy(self.game)
        # current_game_copy.right()
        # candidate_scores.append(self.simulate_1_game(current_game_copy))
        #
        # current_game_copy = copy.deepcopy(self.game)
        # current_game_copy.left()
        # # print(current_game_copy)
        # candidate_scores.append(self.simulate_1_game(current_game_copy))
        #
        # current_game_copy = copy.deepcopy(self.game)
        # current_game_copy.up()
        # candidate_scores.append(self.simulate_1_game(current_game_copy))
        #
        # current_game_copy = copy.deepcopy(self.game)
        # current_game_copy.down()
        # candidate_scores.append(self.simulate_1_game(current_game_copy))

class MC2:
    def __init__(self, game, sims_per_turn: int = 100) -> None:
        self.master_game = game
        self.sims_per_turn = sims_per_turn

    @staticmethod
    def one_game(game):
        # print("in one game")
        while not game.game_over_check():
            current_direction = np.random.randint(0, 4)
            # print(current_direction)
            # game.print_board()
            game.move(current_direction, print_board=False, illegal_warn=False)
            # print("uh")
        else:
            return game.score

    def n_games(self):
        move_dict = {0: "right", 1: "left", 2: "up", 3: "down"}
        scores = []
        for direction in range(4):
            # print(f"start direction {direction}")

            # TEMP ADD
            # print(self.master_game.__dict__)
            # for i in self.master_game.__dict__:
            #     print(i, self.master_game.__dict__[i], type(self.master_game.__dict__[i]))
            # delattr(self.master_game, "window")
            # print("--------")
            # master_dict = self.master_game.__dict__
            # for i in master_dict:
            #     print(i, master_dict[i], type(master_dict[i]))
            # TMP ADD END

            game_copy = copy.deepcopy(self.master_game)  # I THINK GETTING RID OF DEEPCOPY BROKE IT SO ALL THE SCORES BECOME THE SAME
            # TEMP BIG TEST
            # game_copy = self.master_game
            # TMP BIG TEST END
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
                print(f"ADDED SCORE of {np.average(np.array(direction_scores_to_avg))} from going {move_dict[direction]}")
            # print(f"done direction {direction}")
        best_direction = scores.index(max(scores))

        print(scores, move_dict[best_direction])

        # print("START")
        time.sleep(0.01)
        # print("END")
        self.master_game.move(best_direction)
        # print("ok")

    def tmp(self):
        while not self.master_game.game_over_check():
            self.n_games()

            self.master_game.print_board()


class RandomMoves:
    def __init__(self, game):
        self.game = game

    def run(self):
        while not self.game.game_over_check():
            self.game.move(np.random.randint(1, 4), illegal_warn=False)
        else:
            print("done")




