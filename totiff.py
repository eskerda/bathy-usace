import sys

from warnings import warn

import shapely
import rasterio
import alphashape

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio.transform as rio_transform

from pyproj import CRS
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter


GRID_RES = 25  # meters
HULL_ALPHA = 0.01
HULL_BUFFER = GRID_RES
G_SMOOTH = 1.3

# NAD83
# IN_CRS = 'EPSG:2225'
IN_CRS = 'EPSG:2263'
# Web Mercator
OUT_CRS = 'EPSG:3857'


# XXX meh
def naive_read_csv(path, * args, ** kwargs):
    with open(path) as f:
        line = f.readline()
        if ',' in line:
            warn("%s is comma separated" % path)
            sep = ','
        elif ' ' in line:
            sep = r'\s+'
        else:
            raise ValueError("Unknown delimiter")
    return pd.read_csv(path, sep=sep, * args, ** kwargs)


# Load XYZ
files = sys.argv[1:]

df = pd.concat((naive_read_csv(f, names=["x", "y", "z"]) for f in files))

# Create GeoDataFrame with original CRS (EPSG:2263 = NAD83)
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['x'], df['y']), crs=IN_CRS)

# Reproject to Web Mercator (EPSG:3857)
gdf_proj = gdf.to_crs(OUT_CRS)

# Replace x, y with reprojected values
df['x'] = gdf_proj.geometry.x
df['y'] = gdf_proj.geometry.y

# feet to meters
df["z"] = df["z"] * 0.3048
print("x min/max:", df["x"].min(), df["x"].max())
print("y min/max:", df["y"].min(), df["y"].max())

# Define grid
xi = np.arange(df["x"].min(), df["x"].max(), GRID_RES)
yi = np.arange(df["y"].max(), df["y"].min(), - GRID_RES)
xi, yi = np.meshgrid(xi, yi)

# Interpolate
zi = griddata((df["x"], df["y"]), df["z"], (xi, yi), method="nearest")

# Apply Gaussian smoothing
zi = gaussian_filter(zi, sigma=G_SMOOTH)

print("masking")
# MASKING #########################################################
# Create alpha shape (concave hull)
hull = alphashape.alphashape(df[["x", "y"]].values, HULL_ALPHA)

# Flatten the grid coordinates
grid_points = np.c_[xi.ravel(), yi.ravel()]
mask = shapely.contains(hull.buffer(HULL_BUFFER), shapely.points(grid_points))
# 2D mask
mask = mask.reshape(xi.shape)
zi = np.where(mask, zi, np.nan)
###################################################################

# Save as GeoTIFF
xmin, xmax = xi.min(), xi.max()
ymin, ymax = yi.min(), yi.max()
height, width = zi.shape
transform = rio_transform.from_bounds(
    west=xmin, south=ymin, east=xmax, north=ymax, width=width, height=height
)

with rasterio.open(
    "output.tif",
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,
    dtype=zi.dtype,
    crs=OUT_CRS,
    transform=transform,
) as dst:
    dst.write(zi, 1)
