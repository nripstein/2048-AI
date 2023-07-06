import numpy as np
from ax.service.ax_client import AxClient
from ax.service.utils.instantiation import ObjectiveProperties
import statistics
from tqdm import tqdm
from main import Game
from AI import MDP2

ax_client = AxClient(random_seed=42)


ax_client.create_experiment(
    name="moo_experiment1",
    parameters=[
        {
            "name": f"m1-3",
            "type": "range",
            "bounds": [250, 750],
            "value_type": "int"},
        {
            "name": f"m4-6",
            "type": "range",
            "bounds": [25, 100],
            "value_type": "int"},
        {
            "name": f"m7-9",
            "type": "range",
            "bounds": [8, 50],
            "value_type": "int"},
        {
            "name": f"m10-15",
            "type": "range",
            "bounds": [5, 20],
            "value_type": "int"},
        {
            "name": f"depth_scale",
            "type": "range",
            "bounds": [2, 9],
            "value_type": "float"},

    ],
    objectives={
        "score": ObjectiveProperties(minimize=False),
        "time_per_move": ObjectiveProperties(minimize=True)
    },
    parameter_constraints=["m1-3 >= m4-6", "m4-6 >= m7-9", "m7-9 >= m10-15"],
    overwrite_existing_experiment=False,
    is_test=False,
)

def evaluate(parameters):
    param_array = np.array([
        parameters["m1-3"],
        parameters["m4-6"],
        parameters["m7-9"],
        parameters["m10-15"],
        parameters["depth_scale"],
    ])


    scores = []
    time_per_moves = []

    num_runs = 3
    for game_run in range(num_runs):
        g = Game(use_gui=False, no_display=True)
        g.setup_board()
        m = MDP2(g, game_obj=Game, verbose=False, best_proportion=1, core_params=param_array)
        print(f"starting run {game_run} with parameter array {param_array}")
        current_score, current_time_per_move = m.run()
        scores.append(current_score)
        time_per_moves.append(current_time_per_move)
    to_return = {"score": statistics.mean(scores),
                 "time_per_move": statistics.mean(time_per_moves)}

    return to_return


if __name__ == '__main__':
    for i in tqdm(range(15)):
        print(f"starting parameter iteration {i}")
        parameters, trial_index = ax_client.get_next_trial()
        ax_client.complete_trial(trial_index=trial_index, raw_data=evaluate(parameters))


