import sys
import rasterio
import matplotlib.pyplot as plt

import geopandas as gpd

with rasterio.open(sys.argv[1]) as src:
    img = src.read(1)  # read the first band
    extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

if len(sys.argv) > 2:
    gdf = gpd.read_file(sys.argv[2])

plt.figure(figsize=(8, 6))
plt.imshow(img, cmap='Blues_r', extent=extent)

if len(sys.argv) > 2:
    gdf.plot(ax=plt.gca(), edgecolor='black', linewidth=0.8, alpha=0.8, aspect=1)
plt.colorbar(label="Depth (m)")
plt.title("Bathymetry")
plt.xlabel("X")
plt.ylabel("Y")
plt.axis('equal')
plt.show()
