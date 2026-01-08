import math
import tempfile
from typing import Optional
import logging

import numpy as np

# matplotlib fallback
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# try optional faster renderer
try:
    import trimesh
    import pyrender
    from PIL import Image
    HAVE_PYRENDER = True
except Exception:
    HAVE_PYRENDER = False


def _matplotlib_render(shape: str, size: float, fname: str) -> None:
    # lower resolution mesh for speed
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection="3d")

    if shape == "sphere":
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 20)
        x = size * np.outer(np.cos(u), np.sin(v))
        y = size * np.outer(np.sin(u), np.sin(v))
        z = size * np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(x, y, z, rstride=1, cstride=1, color="#1f77b4", linewidth=0, antialiased=False)

    elif shape == "cube":
        r = size / 2.0
        points = np.array([[-r, -r, -r], [r, -r, -r], [r, r, -r], [-r, r, -r],
                           [-r, -r, r], [r, -r, r], [r, r, r], [-r, r, r]])
        faces = [[0,1,2,3], [4,5,6,7], [0,1,5,4], [2,3,7,6], [1,2,6,5], [4,7,3,0]]
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        poly3d = [[points[idx] for idx in face] for face in faces]
        ax.add_collection3d(Poly3DCollection(poly3d, facecolors="#ff7f0e", linewidths=0.5, edgecolors="k", alpha=0.9))
        ax.auto_scale_xyz(points[:,0], points[:,1], points[:,2])

    elif shape == "cone":
        height = size * 2
        radius = size
        z = np.linspace(0, height, 20)
        theta = np.linspace(0, 2 * np.pi, 40)
        Z, Theta = np.meshgrid(z, theta)
        R = (1 - Z / height) * radius
        X = R * np.cos(Theta)
        Y = R * np.sin(Theta)
        ax.plot_surface(X, Y, Z - height/2, color="#2ca02c", linewidth=0, antialiased=False)

    elif shape == "cylinder":
        height = size * 2
        radius = size
        z = np.linspace(-height / 2, height / 2, 20)
        theta = np.linspace(0, 2 * np.pi, 40)
        Z, Theta = np.meshgrid(z, theta)
        X = radius * np.cos(Theta)
        Y = radius * np.sin(Theta)
        ax.plot_surface(X, Y, Z, color="#d62728", linewidth=0, antialiased=False)

    else:
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 20)
        x = size * np.outer(np.cos(u), np.sin(v))
        y = size * np.outer(np.sin(u), np.sin(v))
        z = size * np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(x, y, z, rstride=1, cstride=1, color="#1f77b4", linewidth=0, antialiased=False)

    ax.set_box_aspect([1,1,1])
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(fname, dpi=100, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def _pyrender_render(shape: str, size: float, fname: str) -> None:
    # create trimesh primitive
    if shape == "sphere":
        mesh = trimesh.creation.icosphere(subdivisions=3, radius=size)
    elif shape == "cube":
        mesh = trimesh.creation.box(extents=(size, size, size))
    elif shape == "cone":
        mesh = trimesh.creation.cone(radius=size, height=size * 2, sections=64)
    elif shape == "cylinder":
        mesh = trimesh.creation.cylinder(radius=size, height=size * 2, sections=64)
    else:
        mesh = trimesh.creation.icosphere(subdivisions=3, radius=size)

    scene = pyrender.Scene(bg_color=[255,255,255,0], ambient_light=[0.3,0.3,0.3])
    render_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=False)
    node = scene.add(render_mesh)

    camera = pyrender.PerspectiveCamera(yfov=(math.pi / 3.0))
    cam_node = scene.add(camera, pose=pyrender.matrix44.create_translation_matrix([0, 0, 3.0]))

    light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=2.0)
    scene.add(light, pose=pyrender.matrix44.create_translation_matrix([5, 5, 5]))

    r = pyrender.OffscreenRenderer(viewport_width=800, viewport_height=800)
    color, depth = r.render(scene)
    r.delete()

    img = Image.fromarray(color)
    img.save(fname)


def render_shape(shape: str, size: float = 1.0, fname: Optional[str] = None, backend: str = "auto") -> str:
    """Render a simple 3D shape to a PNG file and return the file path.

    backend: 'auto' | 'pyrender' | 'matplotlib'
    """
    shape = (shape or "").lower()
    if fname is None:
        f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        fname = f.name
        f.close()

    # choose backend
    use_pyrender = False
    if backend == "pyrender":
        use_pyrender = HAVE_PYRENDER
    elif backend == "matplotlib":
        use_pyrender = False
    else:  # auto
        use_pyrender = HAVE_PYRENDER

    if use_pyrender:
        try:
            _pyrender_render(shape, size, fname)
            return fname
        except Exception as exc:
            logging.exception("pyrender render failed, falling back to matplotlib: %s", exc)

    # fallback
    _matplotlib_render(shape, size, fname)
    return fname
