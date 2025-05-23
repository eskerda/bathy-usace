import sys
import argparse

from warnings import warn

import shapely
import rasterio
import alphashape

import numpy as np
import pandas as pd
import rasterio.transform as rio_transform

from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter


GRID_RES = 25  # meters
HULL_ALPHA = 0.01
HULL_BUFFER = GRID_RES
G_SMOOTH = 1.3


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


def preview(df, xi, yi, zi, args, ** kwargs):
    import matplotlib.pyplot as plt

    # Maybe try log. steps or something more visually interesting ?
    levels = None

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(df["x"], df["y"], c=df["z"], s=0.1, marker=',', alpha=0.4)
    CS = plt.contour(xi, yi, zi, levels=levels, colors="black", linestyles="solid", linewidths=0.8, alpha=0.5, ) # , cmap="Blues")
    plt.clabel(CS, inline=True, fontsize=6, inline_spacing=0.1)
    plt.imshow(zi, extent=(xi.min(), xi.max(), yi.min(), yi.max()), cmap="Blues_r", alpha=0.8,)
    # plt.title(f"Bathymetry Contours ({INTP} - {GRID_RES})")
    plt.colorbar(label="Depth")

    if args.outfile:
        plt.savefig(args.outfile, dpi=300)
    else:
        plt.show()


def main(args):
    GRID_RES = args.grid_res
    HULL_ALPHA = args.hull_alpha
    HULL_BUFFER = args.hull_buffer
    G_SMOOTH = args.g_smooth
    files = args.files

    df = pd.concat((naive_read_csv(f, names=["x", "y", "z"]) for f in files))
    dupes = df.duplicated(subset=['x', 'y'], keep=False)
    if dupes.any():
        warn(f"Found {dupes.sum()} dupes in dataset, averaging")
        # warn on duplicates, get min
        df = df.groupby(['x', 'y'], as_index=False).mean()
        # Or get min
        # df = df.groupby(['x', 'y'], as_index=False).agg({'z': 'min'})

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
    # smoothed = gaussian_filter(mask.astype(float), sigma=2)
    # # Threshold to get back to binary
    # mask = smoothed > 0.1

    zi = np.where(mask, zi, np.nan)
    ###################################################################

    if args.preview:
        return preview(** locals())

    # Save as GeoTIFF
    xmin, xmax = xi.min(), xi.max()
    ymin, ymax = yi.min(), yi.max()
    height, width = zi.shape
    transform = rio_transform.from_bounds(
        west=xmin, south=ymin, east=xmax, north=ymax, width=width, height=height
    )

    with rasterio.open(
        args.outfile or "output.tif",
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=zi.dtype,
        crs=None,
        transform=transform,
    ) as dst:
        dst.write(zi, 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    parser.add_argument('--preview', action='store_true', default=False)
    parser.add_argument('--grid-res', dest='grid_res', default=GRID_RES)
    parser.add_argument('--hull-alpha', dest='hull_alpha', default=HULL_ALPHA, type=float)
    parser.add_argument('--hull-buffer', dest='hull_buffer', default=HULL_BUFFER, type=float)
    parser.add_argument('--g-smooth-sigma', dest='g_smooth', default=G_SMOOTH, type=float)
    parser.add_argument('-o', dest='outfile', help='output file')

    args = parser.parse_args()

    main(args)
