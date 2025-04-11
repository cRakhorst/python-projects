import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pickle
import neat
import os
from robot import WalkingRobotEnv
import numpy as np
import time

def visualize_winner(config_path, genome_path):
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    net = neat.nn.FeedForwardNetwork.create(genome, config)
    env = WalkingRobotEnv()
    obs, _ = env.reset()

    done = False
    total_fitness = 0
    start_time = time.time()

    while not done:
        action = [np.argmax(net.activate(obs)) for _ in range(4)]
        obs, fitness, done, _, _ = env.step(action)
        total_fitness += fitness
        env.render()

    print(f"Total fitness of winner: {total_fitness:.2f}")
    time.sleep(2)
    env.close()

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "utils", "neat-config.txt")
    genome_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "winner.pkl")
    visualize_winner(config_path, genome_path)