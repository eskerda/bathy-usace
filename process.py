import sys

import alphashape

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.geometry import Point


def point_in_poly_mask(points, polygon):
    """Return boolean mask of which points are inside the polygon."""
    if isinstance(polygon, Polygon):
        return np.array([polygon.contains(Point(xy)) for xy in points])
    elif isinstance(polygon, MultiPolygon):
        return np.array(
            [any(poly.contains(Point(xy)) for poly in polygon.geoms)
             for xy in points]
        )


# EPSG:3104
GEOM = 3104
XYZ_PATH = sys.argv[1]
GRID_RES = 50.0
# linear, cubic, nearest
INTP = "nearest"
G_SMOOTH = 2.0
# smaller = tighter hull
HULL_ALPHA = 0.01
HULL_BUFFER = 0.0

# Set to None for auto
CONTOUR_LEVELS = [-10, -5, -4, -3, -2, -1, -0.5, 0]

df = pd.read_csv(XYZ_PATH, sep=r"\s+", header=None, names=["x", "y", "z"])
print(df.head())

# feet to meters
df["z"] = df["z"] * 0.3048

# # RAW viz ################################
# 
# plt.figure(figsize=(8, 6))
# plt.scatter(df["x"], df["y"], c=df["z"], cmap="Blues_r", s=1)
# plt.title("Raw XYZ Depth Points")
# plt.xlabel("X")
# plt.ylabel("Y")
# plt.colorbar(label="Depth (m)")
# plt.show()

#########################################
# Interpolate to create DEM grid ########
print(f"Interpolating ({INTP}) at {GRID_RES}")

# Create grid
xi = np.arange(df["x"].min() - HULL_BUFFER, df["x"].max() + HULL_BUFFER, GRID_RES)
yi = np.arange(df["y"].min() - HULL_BUFFER, df["y"].max() + HULL_BUFFER, GRID_RES)
# XXX Pretty sure this has more options
xi, yi = np.meshgrid(xi, yi)

# Interpolate Z values to regular grid
zi = griddata((df["x"], df["y"]), df["z"], (xi, yi), method=INTP)

# Apply Gaussian smoothing
zi = gaussian_filter(zi, sigma=G_SMOOTH)


# MASKING #########################################################
# Create alpha shape (concave hull)
hull = alphashape.alphashape(df[["x", "y"]].values, HULL_ALPHA)

# Flatten the grid coordinates
grid_points = np.c_[xi.ravel(), yi.ravel()]
inside_mask_flat = point_in_poly_mask(grid_points, hull.buffer(HULL_BUFFER))
inside_mask = inside_mask_flat.reshape(xi.shape)

zi = np.ma.array(zi, mask=~inside_mask)
###################################################################

print("Done")

# Maybe try log. steps or something more visually interesting ?
levels = None

# Plot
plt.figure(figsize=(8, 6))
plt.scatter(df["x"], df["y"], c=df["z"], s=0.1, marker=',', alpha=0.4)
CS = plt.contour(xi, yi, zi, levels=CONTOUR_LEVELS, colors="black", linestyles="solid", linewidths=0.8, alpha=0.5, ) # , cmap="Blues")
plt.clabel(CS, inline=True, fontsize=6, inline_spacing=0.1)
plt.imshow(zi, extent=(xi.min(), xi.max(), yi.min(), yi.max()), origin="lower", cmap="Blues_r", alpha=0.8,)
plt.title(f"Bathymetry Contours ({INTP} - {GRID_RES})")
plt.colorbar(label="Depth")

plt.show()

# Export to polygons

import pdb; pdb.set_trace()
