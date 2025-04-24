import pygame

class Track:
    def __init__(self):
        self.start = (100, 100)
        self.checkpoints = [(300, 300), (500, 500)]
        self.track_edges = [(100, 100), (200, 200), (400, 400), (600, 600)]

    def draw(self, screen):
        """Teken de track op het scherm"""
        for point in self.track_edges:
            pygame.draw.circle(screen, (0, 255, 0), point, 5)

    def get_checkpoints(self):
        """Retourneer de posities van de checkpoints"""
        return self.checkpoints
