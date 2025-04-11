import pygame
import sys
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import time

class WalkingRobotEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render=True):
        super(WalkingRobotEnv, self).__init__()

        self.render_enabled = render
            
        self.WIDTH, self.HEIGHT = 800, 600
        self.ROBOT_WIDTH, self.ROBOT_HEIGHT = 40, 60
        self.GROUND_Y = self.HEIGHT - 60
        self.SCALE = 4  # pixels per position unit

        # Gravity and vertical position
        self.gravity = 9.8  # pixels per second^2
        self.vertical_velocity = 0  # initial vertical velocity
        self.robot_y_velocity = 0  # velocity of the robot's torso
        self.robot_y_position = self.GROUND_Y - self.ROBOT_HEIGHT  # initial torso position

        # Action and observation spaces
        self.action_space = spaces.MultiDiscrete([3, 3, 3, 3])
        self.observation_space = spaces.Box(
            low=np.array([-90, 0, -90, 0, 0], dtype=np.float32),  # Add an extra dimension for robot_y_position
            high=np.array([90, 150, 90, 150, self.GROUND_Y], dtype=np.float32)  # Add a limit for robot_y_position
        )

        # Initial joint angles
        self.joint_angles = np.array([0, 90, 0, 90], dtype=np.float32)

        if self.render_enabled:
            pygame.init()
            pygame.font.init()
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
            pygame.display.set_caption("Walking Robot")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 24)

    def reset(self, seed=None, options=None):
        self.position = 0
        self.start_time = time.time()
        self.total_fitness_score = 0  # Initialize here
        self.robot_y_position = self.GROUND_Y - self.ROBOT_HEIGHT
        self.robot_y_velocity = 0
        self.joint_angles = np.array([0, 90, 0, 90], dtype=np.float32)
        obs = np.concatenate((self.joint_angles, [self.robot_y_position]), axis=None)  # Ensure this matches observation_space
        self.prev_position = 0  # Reset this as well
        return obs, {}

    def step(self, action):
        # Update joint angles based on action
        for i in range(4):
            if action[i] == 1:
                self.joint_angles[i] += 5
            elif action[i] == 2:
                self.joint_angles[i] -= 5

        # Clip joint angles to observation space limits (only the first 4 dimensions)
        self.joint_angles = np.clip(
            self.joint_angles,
            self.observation_space.low[:4],  # Use only the first 4 values
            self.observation_space.high[:4]  # Use only the first 4 values
        )

        # Apply gravity to the robot's torso
        self.robot_y_velocity += self.gravity * 0.1  # Simulate gravity effect
        self.robot_y_position += self.robot_y_velocity * 0.1

        # Calculate the position of the robot's legs
        upper_leg = 20
        lower_leg = 20
        robot_x = self.WIDTH // 2 + int(self.position * self.SCALE)
        robot_y = self.robot_y_position

        l_hip_x = robot_x - 10
        l_hip_y = robot_y
        l_knee_x = l_hip_x + upper_leg * np.cos(np.radians(self.joint_angles[0]))
        l_knee_y = l_hip_y - upper_leg * np.sin(np.radians(self.joint_angles[0]))
        l_foot_x = l_knee_x + lower_leg * np.cos(np.radians(self.joint_angles[0] + self.joint_angles[1] - 90))
        l_foot_y = l_knee_y - lower_leg * np.sin(np.radians(self.joint_angles[0] + self.joint_angles[1] - 90))

        r_hip_x = robot_x + 10
        r_hip_y = robot_y
        r_knee_x = r_hip_x + upper_leg * np.cos(np.radians(self.joint_angles[2]))
        r_knee_y = r_hip_y - upper_leg * np.sin(np.radians(self.joint_angles[2]))
        r_foot_x = r_knee_x + lower_leg * np.cos(np.radians(self.joint_angles[2] + self.joint_angles[3] - 90))
        r_foot_y = r_knee_y - lower_leg * np.sin(np.radians(self.joint_angles[2] + self.joint_angles[3] - 90))

        # Check if the feet are on the ground
        lowest_foot_y = max(l_foot_y, r_foot_y)
        if lowest_foot_y > self.GROUND_Y:
            correction = lowest_foot_y - self.GROUND_Y
            self.robot_y_position -= correction
            self.robot_y_velocity = 0  # Reset velocity

        if self.robot_y_position > self.GROUND_Y:
            self.robot_y_position = self.GROUND_Y
            self.robot_y_velocity = 0

        # Simulate the robot's movement
        contact_threshold = 0.5   # Position threshold for foot contact
        step_power = 0.05

        left_foot_on_ground = abs(l_foot_y - self.GROUND_Y) < contact_threshold
        right_foot_on_ground = abs(r_foot_y - self.GROUND_Y) < contact_threshold

        if left_foot_on_ground and action[1] == 1:
            self.position += step_power
        if right_foot_on_ground and action[3] == 1:
            self.position += step_power
        if left_foot_on_ground and action[1] == 2:
            self.position -= step_power
        if right_foot_on_ground and action[3] == 2:
            self.position -= step_power

        # Observation
        obs = np.concatenate((self.joint_angles, [self.robot_y_position]), axis=None)

        # Reward 1: Total distance moved
        delta_position = self.position - getattr(self, 'prev_position', 0)
        self.prev_position = self.position
        fitness_score = delta_position * 10

        self.total_fitness_score += fitness_score

        info = {}
        done = (time.time() - self.start_time >= 10)
        return obs, fitness_score, done, False, info

    def render(self):
        if not self.render_enabled:
            return
        
        def to_int(pos):
            return int(pos[0]), int(pos[1])

        # Process Pygame events to prevent "not responding" issues
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill((255, 255, 255))

        # Draw ground
        pygame.draw.line(self.screen, (255, 0, 0), (0, self.GROUND_Y), (self.WIDTH, self.GROUND_Y), 4)

        # Draw torso
        robot_x = self.WIDTH // 2 + int(self.position * self.SCALE)
        robot_y = int(self.robot_y_position)

        pygame.draw.rect(self.screen, (0, 0, 255), (robot_x - 10, robot_y - 40, 20, 40))

        # Leg parameters
        upper_leg = 20
        lower_leg = 20

        # Joint angles
        l_hip, l_knee, r_hip, r_knee = self.joint_angles

        # Left leg
        l_hip_x = robot_x - 10
        l_hip_y = robot_y
        l_knee_x = l_hip_x + upper_leg * np.cos(np.radians(l_hip))
        l_knee_y = l_hip_y - upper_leg * np.sin(np.radians(l_hip))
        l_foot_x = l_knee_x + lower_leg * np.cos(np.radians(l_hip + l_knee - 90))
        l_foot_y = l_knee_y - lower_leg * np.sin(np.radians(l_hip + l_knee - 90))

        # Right leg
        r_hip_x = robot_x + 10
        r_hip_y = robot_y
        r_knee_x = r_hip_x + upper_leg * np.cos(np.radians(r_hip))
        r_knee_y = r_hip_y - upper_leg * np.sin(np.radians(r_hip))
        r_foot_x = r_knee_x + lower_leg * np.cos(np.radians(r_hip + r_knee - 90))
        r_foot_y = r_knee_y - lower_leg * np.sin(np.radians(r_hip + r_knee - 90))

        # Draw left leg
        pygame.draw.line(self.screen, (0, 0, 0), to_int((l_hip_x, l_hip_y)), to_int((l_knee_x, l_knee_y)), 4)
        pygame.draw.line(self.screen, (0, 0, 0), to_int((l_knee_x, l_knee_y)), to_int((l_foot_x, l_foot_y)), 4)

        # Draw right leg
        pygame.draw.line(self.screen, (0, 0, 0), to_int((r_hip_x, r_hip_y)), to_int((r_knee_x, r_knee_y)), 4)
        pygame.draw.line(self.screen, (0, 0, 0), to_int((r_knee_x, r_knee_y)), to_int((r_foot_x, r_foot_y)), 4)

        # Position text
        text = self.font.render(f"Position: {self.position}", True, (0, 0, 0))
        self.screen.blit(text, (10, 10))

        pygame.display.flip()
        self.clock.tick(60)  # Limit to 60 FPS

    def close(self):
        pygame.quit()
        pass

if __name__ == "__main__":
    env = WalkingRobotEnv()
    obs, _ = env.reset()
    total_fitness_score = 0

    start_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.close()
                sys.exit()

        # Check time elapsed
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time >= 10:
            break

        action = env.action_space.sample()
        obs, fitness_score, done, truncated, info = env.step(action)
        total_fitness_score += fitness_score

        env.render()

    print(f"Total fitness score: {total_fitness_score:.2f}")
    time.sleep(1)
    env.close()