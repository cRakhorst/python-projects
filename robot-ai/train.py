import neat
import os
import numpy as np
from robot import WalkingRobotEnv
import time
import pickle

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        try:
            # Create a neural network from the genome
            net = neat.nn.FeedForwardNetwork.create(genome, config)

            # Create a new environment
            env = WalkingRobotEnv(render=False) # fix the rendering problem FOR FUCKS SAKE
            obs, _ = env.reset()

            total_fitness = 0
            done = False
            start_time = time.time()

            while not done:
                # Get the action from the network (output has 4 values for 4 joints)
                actions = net.activate(obs)
                action = np.clip(np.round(actions), 0, 2).astype(int)

                # Perform the action in the environment
                obs, fitness, done, _, _ = env.step(action)
                total_fitness += fitness

                # Stop the loop after 10 seconds to avoid long evaluation times
                if time.time() - start_time > 10:
                    break

            env.close()

            # Assign the total fitness to the genome
            genome.fitness = total_fitness
    
        except Exception as e:
            print(f"Error evaluating genome {genome_id}: {e}")
            genome.fitness = 0.0

def run_neat(config_file):
    # Load the configuration
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file
    )

    # Create a population
    population = neat.Population(config)

    # Add statistics reporters
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run the evolution process (50 generations in this case)
    winner = population.run(eval_genomes, 2)

    # Display the best genome
    print('\nBest genome:\n{!s}'.format(winner))

    # Save the winner's genome to a file
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)  # Make sure the directory exists
    winner_path = os.path.join(model_dir, "winner.pkl")
    with open(winner_path, "wb") as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    # Path to the configuration file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "utils", "neat-config.txt")
    run_neat(config_path)
