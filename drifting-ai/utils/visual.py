import pygame
import argparse
import os
import sys
from car import Car
from track import Track
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from robot import Robot

def main(run, generation, robot_id):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    track = Track()
    car = Car(x=track.start[0], y=track.start[1])

    model_path = f"models/{run}/generation{generation}/robot{robot_id}.txt"
    robot = Robot(config_path="utils/neat-config.txt")
    
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        steering = 0.1
        throttle = 1
        brake = 0
        car.update(clock.get_time() / 1000.0, steering, throttle, brake)
        
        track.draw(screen)
        car.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualiseer een robottraining")
    parser.add_argument('--run', type=str, required=True, help="De run die getoond moet worden")
    parser.add_argument('--generation', type=int, required=True, help="De generatie die getoond moet worden")
    parser.add_argument('--robot', type=int, required=True, help="De robot ID die getoond moet worden")
    args = parser.parse_args()

    main(args.run, args.generation, args.robot)
