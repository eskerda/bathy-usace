import sys

import alphashape
import rasterio

import numpy as np
import pandas as pd
import rasterio.transform as rio_transform

from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from shapely.geometry import Point, Polygon, MultiPolygon


GRID_RES = 25  # meters
HULL_ALPHA = 0.01
HULL_BUFFER = 0.0
G_SMOOTH = 1.3

# NAD83
# IN_CRS = 'EPSG:2225'
IN_CRS = 'EPSG:2263'
# Web Mercator
OUT_CRS = 'EPSG:3857'


def point_in_poly_mask(points, polygon):
    """Return boolean mask of which points are inside the polygon."""
    if isinstance(polygon, Polygon):
        return np.array([polygon.contains(Point(xy)) for xy in points])
    elif isinstance(polygon, MultiPolygon):
        return np.array(
            [any(poly.contains(Point(xy)) for poly in polygon.geoms) for xy in points]
        )


# Load XYZ
files = sys.argv[1:]

df = pd.concat(
    (pd.read_csv(f, sep=r'\s+', names=["x", "y", "z"]) for f in files)
)

import pandas as pd
import geopandas as gpd
from pyproj import CRS

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
inside_mask_flat = point_in_poly_mask(grid_points, hull.buffer(HULL_BUFFER))
inside_mask = inside_mask_flat.reshape(xi.shape)

# fill outside with NaN or a nodata value
zi_masked = np.where(inside_mask, zi, np.nan)

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
    dst.write(zi_masked, 1)
