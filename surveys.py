"""stdout a CSV of all USACE surveys"""

import csv
import sys
import json
import argparse

import requests
from tqdm import tqdm


PAGE_SIZE = 100
ENDPOINT = "https://services7.arcgis.com/n1YM8pTrFmm7L4hs/arcgis/rest/services/eHydro_Survey_Data/FeatureServer/0/query"


def arcgis_q(query="1=1", offset=0, count=100, order=None, **kwargs):
    args = {
        "f": "json",
        "resultOffset": offset,
        "resultRecordCount": count,
        "where": query,
        "outFields": "*",
        "resultType": "standard",
        "returnGeometry": False,
        "orderByFields": order or "OBJECTID",
    }
    r = requests.get(ENDPOINT, params=dict(args, **kwargs)).json()

    if 'error' in r:
        raise Exception(r)

    return r


def arcgis_q_count(*args, **kwargs):
    r = arcgis_q(*args, returnCountOnly=True, **kwargs)
    return r["count"]


def main(args):
    if args.outfile and args.outfile != '-':
        out = open(args.outfile, 'w')
    else:
        out = sys.stdout

    writer = csv.DictWriter(out or sys.stdout, fieldnames={})

    queries = []
    if args.query:
        queries.append(f"({args.query})")
    if args.district:
        queries.append(f"(usacedistrictcode='{args.district}')")
    if args.channel:
        queries.append(f"(channelareaidfk='{args.channel}')")
    query = ' AND '.join(queries)
    query = query or "1=1"

    total = arcgis_q_count(query, order=args.order)
    total = min(args.total or total, total)
    page = min(total, PAGE_SIZE)

    # XXX use asyncio to parallelize
    for i in tqdm(range(0, total, page)):
        surveys = [
            f["attributes"] for f in
                arcgis_q(query, i, page, order=args.order)["features"]
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
    parser.add_argument('-o', dest='outfile', help='CSV output file')
    parser.add_argument('-n', dest='total', help='limit to N surveys', default=0, type=int)
    parser.add_argument('--query', dest='query', help='ArcGIS filter query')
    parser.add_argument('--district', dest='district', help='filter by district code (ex: CENAN)')
    parser.add_argument('--channel-area-id', dest='channel', help='filter by channel area id (ex: CENAN_JI_01_INL)')
    parser.add_argument('--no-header', dest='header', action='store_false', default=True)
    parser.add_argument('--order-by', dest='order', help='order by feature fields')
    args = parser.parse_args()

    main(args)
