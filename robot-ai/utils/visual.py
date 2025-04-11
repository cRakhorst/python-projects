import sys
import os
import numpy as np
import time
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from robot import WalkingRobotEnv

def get_latest_run_file():
    # Define the path to the models directory, one level down
    models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    
    # Get all existing run files with '.txt' extension
    existing_runs = [f for f in os.listdir(models_dir) if f.startswith("run") and f.endswith(".txt")]
    
    # Extract run numbers, then find the latest one
    run_numbers = [int(f[3:-4]) for f in existing_runs if f[3:-4].isdigit()]  # Remove "run" prefix and ".txt" suffix
    latest_run_number = max(run_numbers, default=0)  # Default 0 if no runs exist
    
    latest_run_file = os.path.join(models_dir, f"run{latest_run_number}.txt")
    return latest_run_file

def visualize_best_from_log():
    # Get the latest run file
    run_file = get_latest_run_file()
    
    if not os.path.exists(run_file):
        print(f"No run file found at {run_file}")
        return

    print(f"Visualizing winner from {run_file}")

    # Load the best robot data directly from the run file (runX.txt)
    with open(run_file, "r") as log_file:
        lines = log_file.readlines()[1:]  # Skip header

    if not lines:
        print("No valid data found.")
        return

    # Replay the robot's actions over the entire log
    env = WalkingRobotEnv(render=True)
    obs, _ = env.reset()

    print(f"Visualizing robot from {run_file}")

    # Iterate through each line in the log file
    for line in lines:
        parts = line.strip().split("\t")
        if len(parts) < 2:  # Ensure there are at least actions and observations
            continue

        # Parse actions and observations
        actions = np.array(eval(parts[0]))
        observations = np.array(eval(parts[1]))

        # Perform the action in the environment and render the frame
        obs, _, done, _, _ = env.step(actions)
        env.render()

    env.close()

if __name__ == "__main__":
    visualize_best_from_log()
