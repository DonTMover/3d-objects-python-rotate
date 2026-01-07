import math
import tempfile
from typing import Optional

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib import cm


def render_shape(shape: str, size: float = 1.0, fname: Optional[str] = None) -> str:
    """Render a simple 3D shape to a PNG file and return the file path.

    Supported shapes: sphere, cube, cone, cylinder
    """
    shape = (shape or "").lower()
    if fname is None:
        f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        fname = f.name
        f.close()

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")

    if shape == "sphere":
        u = np.linspace(0, 2 * np.pi, 60)
        v = np.linspace(0, np.pi, 30)
        x = size * np.outer(np.cos(u), np.sin(v))
        y = size * np.outer(np.sin(u), np.sin(v))
        z = size * np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(x, y, z, rstride=1, cstride=1, color="#1f77b4", linewidth=0, antialiased=True)

    elif shape == "cube":
        # draw a cube centered at origin
        r = size / 2.0
        points = np.array([[-r, -r, -r], [r, -r, -r], [r, r, -r], [-r, r, -r],
                           [-r, -r, r], [r, -r, r], [r, r, r], [-r, r, r]])
        faces = [[0,1,2,3], [4,5,6,7], [0,1,5,4], [2,3,7,6], [1,2,6,5], [4,7,3,0]]
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        poly3d = [[points[idx] for idx in face] for face in faces]
        ax.add_collection3d(Poly3DCollection(poly3d, facecolors="#ff7f0e", linewidths=0.5, edgecolors="k", alpha=0.9))
        ax.auto_scale_xyz(points[:,0], points[:,1], points[:,2])

    elif shape == "cone":
        # cone along z axis
        height = size * 2
        radius = size
        z = np.linspace(0, height, 30)
        theta = np.linspace(0, 2 * np.pi, 60)
        Z, Theta = np.meshgrid(z, theta)
        R = (1 - Z / height) * radius
        X = R * np.cos(Theta)
        Y = R * np.sin(Theta)
        ax.plot_surface(X, Y, Z - height/2, color="#2ca02c", linewidth=0, antialiased=True)

    elif shape == "cylinder":
        height = size * 2
        radius = size
        z = np.linspace(-height / 2, height / 2, 30)
        theta = np.linspace(0, 2 * np.pi, 60)
        Z, Theta = np.meshgrid(z, theta)
        X = radius * np.cos(Theta)
        Y = radius * np.sin(Theta)
        ax.plot_surface(X, Y, Z, color="#d62728", linewidth=0, antialiased=True)

    else:
        # fallback: small sphere
        u = np.linspace(0, 2 * np.pi, 60)
        v = np.linspace(0, np.pi, 30)
        x = size * np.outer(np.cos(u), np.sin(v))
        y = size * np.outer(np.sin(u), np.sin(v))
        z = size * np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(x, y, z, rstride=1, cstride=1, color="#1f77b4", linewidth=0, antialiased=True)

    ax.set_box_aspect([1,1,1])
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(fname, dpi=150, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    return fname
