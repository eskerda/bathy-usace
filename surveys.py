"""stdout a CSV of all USACE surveys"""

import csv
import sys
import json

import requests
from tqdm import tqdm


PAGE_SIZE = 100
ENDPOINT = "https://services7.arcgis.com/n1YM8pTrFmm7L4hs/arcgis/rest/services/eHydro_Survey_Data/FeatureServer/0/query"


def arcgis_q(offset=0, count=100, q="1=1", **kwargs):
    args = {
        "f": "json",
        "resultOffset": offset,
        "resultRecordCount": count,
        "where": q,
        "outFields": "*",
        "resultType": "standard",
        "returnGeometry": False,
        "orderByFields": "OBJECTID",
    }
    return requests.get(ENDPOINT, params=dict(args, **kwargs)).json()


def arcgis_q_count(*args, **kwargs):
    r = arcgis_q(*args, returnCountOnly=True, **kwargs)
    return r["count"]


q = "1=1"
# q = "(usacedistrictcode='CENAN') AND (channelareaidfk='CENAN_JI_01_INL')"
total = arcgis_q_count(q=q)

writer = csv.DictWriter(sys.stdout, fieldnames={})

# XXX use asyncio to parallelize
# XXX move to main()
# XXX use argparse
for i in tqdm(range(0, total, PAGE_SIZE)):
    surveys = [f["attributes"] for f in arcgis_q(i, PAGE_SIZE, q=q)["features"]]

    if i == 0:
        writer.fieldnames = sorted(surveys[0].keys())
        writer.writeheader()

    writer.writerows(surveys)
