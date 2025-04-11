import os
import neat
import numpy as np
from robot import WalkingRobotEnv
from datetime import datetime

def eval_genomes(genomes, config, generation, run_dir):
    best_genome = None
    best_fitness = float('-inf')
    best_log_data = []
    best_genome_id = None

    generation_dir = os.path.join(run_dir, f"generation{generation}")
    os.makedirs(generation_dir, exist_ok=True)

    for genome_id, genome in genomes:
        try:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            env = WalkingRobotEnv(render=False)
            obs, _ = env.reset()

            total_fitness = 0
            done = False
            log_data = []

            while not done:
                outputs = net.activate(obs)
                actions = np.array([0 if o < 0.33 else 1 if o < 0.66 else 2 for o in outputs], dtype=int)
                obs, fitness, done, _, _ = env.step(actions)
                if done:
                    total_fitness = fitness
                log_data.append((actions.tolist(), obs.tolist()))

            env.close()
            genome.fitness = total_fitness

            # Save robot's log
            robot_log_path = os.path.join(generation_dir, f"robot_{genome_id}.txt")
            with open(robot_log_path, "w") as f:
                f.write(f"Fitness: {total_fitness:.2f}\n")
                for actions, observations in log_data:
                    f.write(f"{actions}\t{observations}\n")

            if total_fitness > best_fitness:
                best_fitness = total_fitness
                best_genome = genome
                best_log_data = log_data
                best_genome_id = genome_id

        except Exception as e:
            print(f"Error evaluating genome {genome_id}: {e}")
            genome.fitness = 0.0

    # Log best genome of this generation
    log_file_path = os.path.join(run_dir, "training_log.txt")
    with open(log_file_path, "a") as log_file:
        if generation == 0:
            log_file.write("Generation\tRobot ID\tFitness\tActions\tObservations\n")
        for actions, observations in best_log_data:
            log_file.write(f"{generation}\t{best_genome_id}\t{best_fitness:.2f}\t{actions}\t{observations}\n")

    return best_genome, best_fitness

def run_neat(config_file, run_number):
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

    # Make run folder
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    run_dir = os.path.join(models_dir, f"run{run_number}")
    os.makedirs(run_dir, exist_ok=True)

    generation = 0
    def eval_with_generation(genomes, config):
        nonlocal generation
        eval_genomes(genomes, config, generation, run_dir)
        generation += 1

    winner = population.run(eval_with_generation, 50)

    # Save winner as a plain text file (no pickle)
    winner_path = os.path.join(run_dir, "winner.txt")
    with open(winner_path, "w") as f:
        f.write(str(winner))

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "utils", "neat-config.txt")
    run_number = 1  # <-- Change this per run or make dynamic
    run_neat(config_path, run_number)
