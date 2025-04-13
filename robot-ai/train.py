import os
import neat
import numpy as np
from robot import WalkingRobotEnv

def eval_genomes(genomes, config):
    global best_log_data
    best_genome = None
    best_fitness = float('-inf')
    best_log_data = []

    for genome_id, genome in genomes:
        try:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            env = WalkingRobotEnv(render=False)
            obs, _ = env.reset()

            total_fitness = 0
            done = False
            log_data = []  # This stores actions and observations for this genome

            while not done:
                outputs = net.activate(obs)
                actions = np.array([0 if o < 0.33 else 1 if o < 0.66 else 2 for o in outputs], dtype=int)
                obs, fitness, done, _, _ = env.step(actions)
                if done:
                    total_fitness = fitness
                log_data.append((actions.tolist(), obs.tolist()))

            env.close()
            genome.fitness = total_fitness

            # Update the best genome if this one is better
            if total_fitness > best_fitness:
                best_fitness = total_fitness
                best_genome = genome
                best_log_data = log_data

        except Exception as e:
            print(f"Error evaluating genome {genome_id}: {e}")
            genome.fitness = 0.0

    return best_genome, best_fitness, best_log_data


def get_next_run_filename(models_dir):
    run_number = 1
    while os.path.exists(os.path.join(models_dir, f"run{run_number}.txt")):
        run_number += 1
    return os.path.join(models_dir, f"run{run_number}.txt")


def run_neat(config_file):
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)

    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run the NEAT algorithm and get the best genome (winner)
    winner = population.run(eval_genomes, 50)

    log_file_path = get_next_run_filename(models_dir)

    with open(log_file_path, "w") as log_file:
        log_file.write("Actions\tObservations\n")
        for actions, observations in best_log_data:
            log_file.write(f"{actions}\t{observations}\n")

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "utils", "neat-config.txt")
    run_neat(config_path)
