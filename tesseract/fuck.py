import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def create_tesseract():
    points = []
    for i in range(16):
        x = (i & 1) * 2 - 1
        y = ((i >> 1) & 1) * 2 - 1
        z = ((i >> 2) & 1) * 2 - 1
        w = ((i >> 3) & 1) * 2 - 1
        points.append([x, y, z, w])
    return np.array(points)

def project_to_3d(points, angle):
    """Voer een 4D -> 3D projectie uit door rotatie in de 4D-ruimte."""
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle), 0, 0],
        [np.sin(angle), np.cos(angle), 0, 0],
        [0, 0, np.cos(angle), -np.sin(angle)],
        [0, 0, np.sin(angle), np.cos(angle)]
    ])
    rotated = points @ rotation_matrix.T
    return rotated[:, :3]  # Projecteer naar 3D

def connect_edges(points):
    """Definieer de verbindingen tussen de punten."""
    edges = []
    for i, p1 in enumerate(points):
        for j, p2 in enumerate(points):
            if np.sum(np.abs(p1 - p2)) == 2:  # Verschil in slechts één dimensie
                edges.append((i, j))
    return edges

def update(frame):
    ax.clear()
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-2, 2)
    ax.axis('off')

    rotated_points = project_to_3d(points, angle=frame / 20)

    for edge in edges:
        p1 = rotated_points[edge[0]]
        p2 = rotated_points[edge[1]]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='blue')


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
points = create_tesseract()
edges = connect_edges(points)

ani = FuncAnimation(fig, update, frames=200, interval=50)
plt.show()