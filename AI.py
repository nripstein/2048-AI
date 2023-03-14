import statistics

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