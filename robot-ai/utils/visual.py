import sys
import os
import numpy as np
from robot import WalkingRobotEnv

def visualize_best_from_log(run_number):
    run_dir = os.path.join(os.path.dirname(__file__), "models", f"run{run_number}")
    log_file_path = os.path.join(run_dir, "training_log.txt")

    if not os.path.exists(log_file_path):
        print(f"No training log found in {run_dir}")
        return

    with open(log_file_path, "r") as log_file:
        lines = log_file.readlines()[1:]  # Skip header

    best_line = None
    best_fitness = float('-inf')

    for line in lines:
        parts = line.strip().split("\t")
        if len(parts) < 5:
            continue
        try:
            fitness = float(parts[2])
            if fitness > best_fitness:
                best_fitness = fitness
                best_line = parts
        except ValueError:
            continue

    if not best_line:
        print("No valid data found.")
        return

    # Replay the best robot
    env = WalkingRobotEnv(render=True)
    obs, _ = env.reset()
    print(f"Visualizing best robot from run{run_number} with fitness {best_fitness:.2f}")

    with open(log_file_path, "r") as log_file:
        lines = log_file.readlines()[1:]

    for line in lines:
        parts = line.strip().split("\t")
        if len(parts) < 5 or parts[2] != str(best_fitness):
            continue

        actions = np.array(eval(parts[3]))
        observations = np.array(eval(parts[4]))

        env.step(actions)
        env.render()

    env.close()

if __name__ == "__main__":
    run_number = 1  # <-- Change to visualize different runs
    visualize_best_from_log(run_number)
