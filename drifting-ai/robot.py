import neat
import os
import json
import shutil
from datetime import datetime

class Robot:
    def __init__(self, config_path, run_id):
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
        self.run_id = run_id
        self.population = neat.Population(self.config)
        self.run_folder = f"./drifting-ai/models/{run_id}"

    def train(self, generations=10):
        for generation in range(generations):
            generation_folder = f"{self.run_folder}/generation{generation}"
            os.makedirs(generation_folder, exist_ok=True)
            self.population.run(self.evaluate_genomes, 1)
            self.save_generation_results(generation)
            self.log_fitness(generation)

    def evaluate_genomes(self, genomes, config):
        """Beoordeel elk genoom (neuraal netwerk)"""
        for genome_id, genome in genomes:
            genome.fitness = self.run_simulation(genome, genome_id)
            self.save_robot_input(genome, genome_id)

    def run_simulation(self, genome, genome_id):
        fitness = 100
        return fitness

    def save_robot_input(self, genome, genome_id):
        generation_folder = f"{self.run_folder}/generation{self.population.generation}"
        robot_data = {
            'id': genome_id,
            'fitness': genome.fitness,
            'connections': {str(k): v.__dict__ for k, v in genome.connections.items()},  # Convert keys to strings and serialize values
            'nodes': {str(k): v.__dict__ for k, v in genome.nodes.items()}  # Convert nodes to dictionaries
        }
        os.makedirs(generation_folder, exist_ok=True)
        with open(f"{generation_folder}/robot_{genome_id}.json", 'w') as f:
            json.dump(robot_data, f)

    def save_generation_results(self, generation):
        generation_folder = f"{self.run_folder}/generation{generation}"
        results = []

        for filename in os.listdir(generation_folder):
            if filename.endswith(".json"):
                with open(f"{generation_folder}/{filename}", 'r') as f:
                    robot_data = json.load(f)
                    results.append(robot_data)

        results.sort(key=lambda x: x['fitness'], reverse=True)

        info_folder = f"{self.run_folder}/info"
        os.makedirs(info_folder, exist_ok=True)
        with open(f"{info_folder}/generation{generation}_info.json", 'w') as f:
            info = {
                'best_robot': results[0],
                'middle_robot': results[len(results) // 2],
                'worst_robot': results[-1]
            }
            json.dump(info, f)

    def log_fitness(self, generation):
        generation_folder = f"{self.run_folder}/generation{generation}"

        results = []
        for filename in os.listdir(generation_folder):
            if filename.endswith(".json"):
                with open(f"{generation_folder}/{filename}", 'r') as f:
                    robot_data = json.load(f)
                    results.append(robot_data)

        results.sort(key=lambda x: x['fitness'], reverse=True)

        best_robot = results[0]
        middle_robot = results[len(results) // 2]
        worst_robot = results[-1]

        info_folder = f"{self.run_folder}/info"
        os.makedirs(info_folder, exist_ok=True)
        with open(f"{info_folder}/generation{generation}_fitness_log.json", 'w') as f:
            log = {
                'best_robot_id': best_robot['id'],
                'best_robot_fitness': best_robot['fitness'],
                'middle_robot_id': middle_robot['id'],
                'middle_robot_fitness': middle_robot['fitness'],
                'worst_robot_id': worst_robot['id'],
                'worst_robot_fitness': worst_robot['fitness']
            }
            json.dump(log, f)

if __name__ == "__main__":
    robot = Robot(config_path="drifting-ai/utils/neat-config.txt", run_id=f"run{datetime.now().strftime('%Y%m%d%H%M%S')}")
    robot.train(generations=10)
