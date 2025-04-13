import sys
import os
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from robot import WalkingRobotEnv

def get_latest_run_file():
    models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    existing_runs = [f for f in os.listdir(models_dir) if f.startswith("run") and f.endswith(".txt")]

    run_numbers = [int(f[3:-4]) for f in existing_runs if f[3:-4].isdigit()]
    latest_run_number = max(run_numbers, default=0) # put in a designated run number if you don't want the latest one

    latest_run_file = os.path.join(models_dir, f"run{latest_run_number}.txt")
    return latest_run_file

def visualize_best_from_log():
    run_file = get_latest_run_file()
    
    if not os.path.exists(run_file):
        print(f"No run file found at {run_file}")
        return

    with open(run_file, "r") as log_file:
        lines = log_file.readlines()[1:]

    if not lines:
        print("No valid data found.")
        return

    # Replay the robot's actions over the entire log
    env = WalkingRobotEnv(render=True)
    obs, _ = env.reset()

    # Iterate through each line in the log file
    for line in lines:
        parts = line.strip().split("\t")
        if len(parts) < 2:
            continue

        actions = np.array(eval(parts[0]))
        observations = np.array(eval(parts[1]))

        # Perform the action in the environment and render the frame
        obs, _, done, _, _ = env.step(actions)
        env.render()

    env.close()

if __name__ == "__main__":
    visualize_best_from_log()
