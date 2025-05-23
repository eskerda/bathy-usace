"""stdout a CSV of all USACE surveys"""

import csv
import sys
import json
import argparse

import requests
from tqdm import tqdm


PAGE_SIZE = 100
ENDPOINT = "https://services7.arcgis.com/n1YM8pTrFmm7L4hs/arcgis/rest/services/eHydro_Survey_Data/FeatureServer/0/query"


def arcgis_q(query, offset=0, count=100, **kwargs):
    args = {
        "f": "json",
        "resultOffset": offset,
        "resultRecordCount": count,
        "where": query,
        "outFields": "*",
        "resultType": "standard",
        "returnGeometry": False,
        "orderByFields": "OBJECTID",
    }
    r = requests.get(ENDPOINT, params=dict(args, **kwargs)).json()

    if 'error' in r:
        raise Exception(r)

    return r


def arcgis_q_count(*args, **kwargs):
    r = arcgis_q(*args, returnCountOnly=True, **kwargs)
    return r["count"]


def main(args, extra):
    if args.outfile and args.outfile != '-':
        out = open(args.outfile, 'w')
    else:
        out = sys.stdout

    writer = csv.DictWriter(out or sys.stdout, fieldnames={})

    query = args.query or "1=1"

    total = arcgis_q_count(query, ** extra)
    total = min(args.total or total, total)
    page = min(total, PAGE_SIZE)

    # XXX use asyncio to parallelize
    for i in tqdm(range(0, total, page)):
        surveys = [
            f["attributes"] for f in
                arcgis_q(query, i, page, ** extra)["features"]
        ]

        if i == 0:
            writer.fieldnames = sorted(surveys[0].keys())
            if args.header:
                writer.writeheader()

        writer.writerows(surveys)

    if out:
        out.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', dest='outfile', help='CSV output file (stdout)')
    parser.add_argument('-n', dest='total', help='limit to N surveys', default=0, type=int)
    parser.add_argument('--query', dest='query', help='ArcGIS filter query')
    parser.add_argument('--no-header', dest='header', action='store_false', default=True)

    args, unk = parser.parse_known_args()

    # arbitrary ArcGIS query parameters.
    # see: https://developers.arcgis.com/documentation/portal-and-data-services/data-services/feature-services/query-features/
    # ie: --orderByFields dateuploaded --outFields OBJECTID,sourcedatalocation
    iter_unk = iter(unk)
    extra = {k.strip('--'): v for k, v in zip(iter_unk, iter_unk)}

    main(args, extra)
