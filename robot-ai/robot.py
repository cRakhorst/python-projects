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
        self.delta_time = 1 / 60
            
        self.WIDTH, self.HEIGHT = 800, 600
        self.ROBOT_WIDTH, self.ROBOT_HEIGHT = 40, 60
        self.GROUND_Y = self.HEIGHT - 60
        self.SCALE = 4

        # Gravity and vertical position
        self.gravity = 9.8
        self.vertical_velocity = 0
        self.robot_y_velocity = 0
        self.robot_y_position = self.GROUND_Y - self.ROBOT_HEIGHT
        self.jump_force = -5

        self.action_space = spaces.MultiDiscrete([3, 3, 3, 3, 2])
        self.observation_space = spaces.Box(
            low=np.array([-90, 0, -90, 0, 0], dtype=np.float32),
            high=np.array([90, 150, 90, 150, self.GROUND_Y], dtype=np.float32)
        )

        self.joint_angles = np.array([0, 90, 0, 90], dtype=np.float32)

        if self.render_enabled:
            try:
                pygame.init()
                pygame.font.init()
                self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
                pygame.display.set_caption("Walking Robot")
                self.clock = pygame.time.Clock()
                self.font = pygame.font.Font(None, 24)
            except Exception as e:
                print(f"Error initializing Pygame: {e}")
        else:
            self.screen = None
            self.clock = None
            self.font = None

    def reset(self, seed=None, options=None):
        self.simulated_time = 0
        self.position = 0
        self.start_time = time.time()
        self.total_fitness_score = 0
        self.robot_y_position = self.GROUND_Y - self.ROBOT_HEIGHT
        self.robot_y_velocity = 0
        self.joint_angles = np.array([0, 90, 0, 90], dtype=np.float32)
        obs = np.concatenate((self.joint_angles, [self.robot_y_position]), axis=None)
        self.last_foot_used = 0
        self.prev_position = 0
        return obs, {}

    def step(self, action):
        # Update joint angles based on action
        for i in range(4):
            if action[i] == 1:
                self.joint_angles[i] += 5
            elif action[i] == 2:
                self.joint_angles[i] -= 5

        self.joint_angles = np.clip(
            self.joint_angles,
            self.observation_space.low[:4],
            self.observation_space.high[:4]
        )

        # Apply gravity to the robot's torso
        self.robot_y_velocity += self.gravity * self.delta_time * 10
        self.robot_y_position += self.robot_y_velocity * self.delta_time * 10
        self.simulated_time += self.delta_time

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
            self.robot_y_velocity = 0

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
        if self.robot_y_position == self.GROUND_Y and action[4] == 1:
            self.robot_y_velocity = self.jump_force

        if self.robot_y_position > self.GROUND_Y:
            self.robot_y_position = self.GROUND_Y
            self.robot_y_velocity = 0

        # Observation
        normalized_obs = self.joint_angles / 90.0
        normalized_y = self.robot_y_position / self.GROUND_Y
        obs = np.concatenate((normalized_obs, [normalized_y]), axis=None)

        # Reward 1: Total distance moved
        fitness_score = self.position * 10
        self.total_fitness_score += fitness_score

        # reward 2: torso height
        # if the torso is above a certain height, reward the robot
        if self.GROUND_Y - 30 <= self.robot_y_position <= self.GROUND_Y - 25:
            fitness_score += 10
        else:
            fitness_score -= 10
        self.total_fitness_score += fitness_score

        # Reward 3: alternating foot usage
        if left_foot_on_ground and self.last_foot_used == 2 and action[1] == 1:
            fitness_score += 2000
            self.last_foot_used = 1
        elif right_foot_on_ground and self.last_foot_used == 1 and action[3] == 1:
            fitness_score += 2000
            self.last_foot_used = 2
        else:
            fitness_score -= 1000 
        self.total_fitness_score += fitness_score

        # Reward 4: smooth movement
        if abs(self.position - self.prev_position) < 0.1:
            fitness_score += 5
        else:
            fitness_score -= 5
        self.total_fitness_score += fitness_score
        self.prev_position = self.position

        info = {}
        done = (self.simulated_time >= 10)
        return obs, fitness_score, done, False, info

    def render(self):
        if not self.render_enabled:
            return
        
        def to_int(pos):
            return int(pos[0]), int(pos[1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill((255, 255, 255))
        pygame.draw.line(self.screen, (255, 0, 0), (0, self.GROUND_Y), (self.WIDTH, self.GROUND_Y), 4)

        robot_x = self.WIDTH // 2 + int(self.position * self.SCALE)
        robot_y = int(self.robot_y_position)
        pygame.draw.rect(self.screen, (0, 0, 255), (robot_x - 10, robot_y - 40, 20, 40))

        upper_leg = 20
        lower_leg = 20

        l_hip, l_knee, r_hip, r_knee = self.joint_angles

        l_hip_x = robot_x - 10
        l_hip_y = robot_y
        l_knee_x = l_hip_x + upper_leg * np.cos(np.radians(l_hip))
        l_knee_y = l_hip_y - upper_leg * np.sin(np.radians(l_hip))
        l_foot_x = l_knee_x + lower_leg * np.cos(np.radians(l_hip + l_knee - 90))
        l_foot_y = l_knee_y - lower_leg * np.sin(np.radians(l_hip + l_knee - 90))

        r_hip_x = robot_x + 10
        r_hip_y = robot_y
        r_knee_x = r_hip_x + upper_leg * np.cos(np.radians(r_hip))
        r_knee_y = r_hip_y - upper_leg * np.sin(np.radians(r_hip))
        r_foot_x = r_knee_x + lower_leg * np.cos(np.radians(r_hip + r_knee - 90))
        r_foot_y = r_knee_y - lower_leg * np.sin(np.radians(r_hip + r_knee - 90))

        pygame.draw.line(self.screen, (0, 0, 0), to_int((l_hip_x, l_hip_y)), to_int((l_knee_x, l_knee_y)), 4)
        pygame.draw.line(self.screen, (0, 0, 0), to_int((l_knee_x, l_knee_y)), to_int((l_foot_x, l_foot_y)), 4)

        pygame.draw.line(self.screen, (0, 0, 0), to_int((r_hip_x, r_hip_y)), to_int((r_knee_x, r_knee_y)), 4)
        pygame.draw.line(self.screen, (0, 0, 0), to_int((r_knee_x, r_knee_y)), to_int((r_foot_x, r_foot_y)), 4)

        text = self.font.render(f"Position: {self.position}", True, (0, 0, 0))
        self.screen.blit(text, (10, 10))

        pygame.display.flip()
        self.clock.tick(60)

    def close(self):
        pygame.quit()