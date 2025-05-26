import os
import sys
import logging
import argparse

import shapely
import rasterio

import numpy as np
import pandas as pd
import rasterio.transform as rio_transform

from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter


GRID_RES = int(os.getenv('GRID_RES', 25))  # meters
HULL_ALPHA = float(os.getenv('HULL_ALPHA', 0.01))
HULL_BUFFER = GRID_RES
G_SMOOTH = float(os.getenv('G_SMOOTH', 1.3))
# linear, cubic, nearest
INTP_M = os.getenv('INTP_M', 'nearest')
C_MASK = str(os.getenv('C_MASK', 0)).lower() in ['true', '1']
D_MASK = str(os.getenv('D_MASK', 1)).lower() in ['true', '1']
S_MASK = str(os.getenv('S_MASK', 1)).lower() in ['true', '1']
M_DIST = float(os.getenv('M_DIST', GRID_RES * 2))
M_SIGMA = float(os.getenv('M_SIGMA', 1.5))
M_CUTOFF = float(os.getenv('M_CUTOFF', 0.3))

log = logging.getLogger("totiff")


# XXX meh
def naive_read_csv(path, * args, ** kwargs):
    with open(path) as f:
        line = f.readline()
        if ',' in line:
            log.warning("%s is comma separated", path)
            sep = ','
        elif ' ' in line:
            sep = r'\s+'
        else:
            raise ValueError("Unknown delimiter")
    return pd.read_csv(path, sep=sep, * args, ** kwargs)


def preview(df, xi, yi, zi, args, ** kwargs):
    import matplotlib.pyplot as plt

    # Maybe try log. steps or something more visually interesting ?
    # levels = [-10, -5, -4, -3, -2, -1, -0.5, 0]
    levels = None

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(df["x"], df["y"], c=df["z"], s=0.1, marker=',', alpha=0.4)
    CS = plt.contour(xi, yi, zi, levels=levels, colors="black", linestyles="solid", linewidths=0.8, alpha=0.5)
    plt.clabel(CS, inline=True, fontsize=6, inline_spacing=0.1)
    plt.imshow(zi, extent=(xi.min(), xi.max(), yi.min(), yi.max()), cmap="Blues_r", alpha=0.8)
    plt.title(f"Bathymetry Contours ({args.intp_m} - {args.grid_res})")
    plt.colorbar(label="Depth")

    if args.outfile:
        plt.savefig(args.outfile, dpi=300)
    else:
        plt.show()


def concave_mask(xys, xyi, alpha=HULL_ALPHA, buffer=HULL_BUFFER):
    """ Generates a mask based on the concave hull of scattered points """
    from alphashape import alphashape

    hull = alphashape(xys, alpha)
    mask = shapely.contains(hull.buffer(buffer), shapely.points(xyi))

    return mask

def distance_mask(xys, xyi, distance=HULL_BUFFER*2):
    """ Generates a mask based on the distance to nearest point """
    from scipy.spatial import cKDTree
    tree = cKDTree(xys)
    dist, _ = tree.query(xyi)

    # XXX tune these params
    # XXX make this proportional to point density
    mask = dist < distance

    return mask


def main(args):
    GRID_RES = args.grid_res
    HULL_ALPHA = args.hull_alpha
    HULL_BUFFER = args.hull_buffer
    G_SMOOTH = args.g_smooth
    M_DIST = args.m_dist
    M_SIGMA = args.m_sigma
    M_CUTOFF = args.m_cutoff

    files = args.files
    outfile = args.outfile or "output.tif"

    log.info("Reading CSV")
    df = pd.concat((naive_read_csv(f, names=["x", "y", "z"]) for f in files))
    dupes = df.duplicated(subset=['x', 'y'], keep=False)
    if dupes.any():
        # XXX what should we do with duplicates, mean, min, max?
        log.warning("Found %d dupes in dataset, averaging", dupes.sum())
        df = df.groupby(['x', 'y'], as_index=False).agg({'z': 'mean'})

    # feet to meters
    df["z"] = df["z"] * 0.3048

    # use negative depth
    if df['z'].min() > 0:
        log.warning("input z in positive depth, negating")
        df['z'] = - df['z']

    log.info("x min/max: %s %s", df["x"].min(), df["x"].max())
    log.info("y min/max: %s %s", df["y"].min(), df["y"].max())
    log.info("z min/max: %s %s", df["z"].min(), df["z"].max())
    log.info("Size %s", df.size)

    log.info("Interpolating: %s x %s", GRID_RES, GRID_RES)
    # Define grid
    xi = np.arange(df["x"].min(), df["x"].max(), GRID_RES)
    yi = np.arange(df["y"].max(), df["y"].min(), - GRID_RES)
    xi, yi = np.meshgrid(xi, yi)

    # Interpolate
    zi = griddata((df["x"], df["y"]), df["z"], (xi, yi), method=args.intp_m)
    # Apply Gaussian smoothing
    zi = gaussian_filter(zi, sigma=G_SMOOTH)

    # Mask
    if any([args.c_mask, args.d_mask]):
        log.info("Generating mask")
        if args.c_mask:
            log.warning("concave mask filtering is slow, please wait")
            log.info("Concave mask: %s, %f, %f", args.c_mask, HULL_ALPHA, HULL_BUFFER)
            mask = concave_mask(
                df[["x", "y"]].values,
                np.c_[xi.ravel(), yi.ravel()],
                HULL_ALPHA, HULL_BUFFER,
            )
        elif args.d_mask:
            log.info("Distance mask: %s, %f", args.d_mask, M_DIST)
            mask = distance_mask(
                df[["x", "y"]].values,
                np.c_[xi.ravel(), yi.ravel()],
                M_DIST,
            )

        if args.s_mask:
            log.info("Smoothing mask: sigma %f, cutoff %f", M_SIGMA, M_CUTOFF)
            mask = gaussian_filter(mask.astype(float), sigma=M_SIGMA) > M_CUTOFF

        mask = mask.reshape(xi.shape)
        log.info("Applying mask")
        zi = np.where(mask, zi, np.nan)

    if args.preview:
        return preview(** locals())

    log.info("generating %s", outfile)
    # Save as GeoTIFF
    xmin, xmax = xi.min(), xi.max()
    ymin, ymax = yi.min(), yi.max()
    height, width = zi.shape
    transform = rio_transform.from_bounds(
        west=xmin, south=ymin,
        east=xmax, north=ymax,
        width=width,
        height=height,
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

    parser.add_argument('--grid-res', dest='grid_res', default=GRID_RES, type=int)
    parser.add_argument('--interpolate', dest='intp_m', default=INTP_M)
    parser.add_argument('--interpolate-smooth-sigma', dest='g_smooth', default=G_SMOOTH, type=float)

    parser.add_argument('--concave-mask', dest='c_mask', action='store_true', default=C_MASK, help="precise concave mask (slow)")
    parser.add_argument('--concave-mask-alpha', dest='hull_alpha', default=HULL_ALPHA, type=float, help="1.0 concave - 0.0 convex")
    parser.add_argument('--concave-mask-buffer', dest='hull_buffer', default=HULL_BUFFER, type=float)

    parser.add_argument('--distance-mask', dest='d_mask', action='store_true', default=D_MASK, help="distance mask (fast)")
    parser.add_argument('--distance-filter', dest='m_dist', type=float, default=M_DIST)

    parser.add_argument('--smooth-mask', dest='s_mask', action='store_true', default=S_MASK, help="smooth mask")
    parser.add_argument('--smooth-mask-sigma', dest='m_sigma', type=float, default=M_SIGMA)
    parser.add_argument('--smooth-mask-cutoff', dest='m_cutoff', type=float, default=M_CUTOFF)

    parser.add_argument('-o', dest='outfile', help='output file')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(stream=sys.stderr)],
        datefmt='%H:%M:%S',
    )

    main(args)
