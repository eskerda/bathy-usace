# USACE Bathymetry ingestion pipeline

## Requirements

This repo requires [GDAL](https://gdal.org/en/stable/) and python

```bash
pip install -r requirements.txt
brew install gdal
```

## Quickstart

The following will start dependent services, download a set of sample USACE
data, generate contours and push them into a postgis instance. Finally open
the demo website to see the map at http://localhost:1337

```bash
python3 -m venv venv
source venv/bin/activate
make install

make contours
docker compose up -d postgis
make push-contours
docker compose up -d
open http://localhost:1337
```

## Usage

### Generate a CSV of USACE surveys feature data from arcgis

Get survey information from USACE arcgis website as CSV.

```bash
python surveys.py > surveys.csv
```

To get a subset of it, run it like

```bash
python surveys.py --query "(usacedistrictcode='CENAN') AND (channelareaidfk='CENAN_JI_01_INL')" \
        > surveys.JI_01.csv
```

The script accepts arbitrary parameters [ArcGIS query parameters][arcgisq]. For example,
use the following to get the survey download url for the most recent 10 uploads.

```bash
python surveys.py -n 10 \
                  --orderByFields 'dateuploaded DESC' \
                  --outFields sourcedatalocation
```

[arcgisq]: https://developers.arcgis.com/documentation/portal-and-data-services/data-services/feature-services/query-features/

### Query relevant survey information

```bash
duckdb << EOF
   select channelareaidfk,
          surveyjobidpk,
          sourcedatalocation,
          sourceprojection,
          dateuploaded
   from read_csv('surveys.csv')
   where channelareaidfk LIKE '%JI_01%'
   order by dateuploaded
EOF
```

```
┌─────────────────┬─────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┬───────────────┐
│ channelareaidfk │              surveyjobidpk              │                                               sourcedatalocation                                                │                    sourceprojection                     │ dateuploaded  │
│     varchar     │                 varchar                 │                                                     varchar                                                     │                         varchar                         │     int64     │
├─────────────────┼─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────┼───────────────┤
│ CENAN_JI_01_INL │ JI_01_INL_20190418_OT_4823_45           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20190418_OT_4823_45.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1577786790000 │
│ CENAN_JI_01_INL │ JI_01_INL_20190429_CS_4820_45           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20190429_CS_4820_45.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1577787038000 │
│ CENAN_JI_01_INL │ JI_01_INL_20170326_CS_4678_25           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20170326_CS_4678_25.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1577787274000 │
│ CENAN_JI_01_INL │ JI_01_INL_20160316_CS_4449_25           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20160316_CS_4449_25.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1577799892000 │
│ CENAN_JI_01_INL │ JI_01_INL_20150313_CS_4287_25           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20150313_CS_4287_25.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1577800130000 │
│ CENAN_JI_01_INL │ JI_01_INL_20140609_CS_4120_25           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20140609_CS_4120_25.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1577961696000 │
│ CENAN_JI_01_INL │ JI_01_INL_20170330_CS_4588_25           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20170330_CS_4588_25.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1577961980000 │
│ CENAN_JI_01_INL │ JI_01_INL_20200303_OT_4918_45           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20200303_OT_4918_45.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1585233130000 │
│ CENAN_JI_01_INL │ JI_01_INL_20210113_OT_5008_30           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20210113_OT_5008_30.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1612770912000 │
│ CENAN_JI_01_INL │ JI_01_INL_20210601_CS_5046_45           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20210601_CS_5046_45.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1623141264000 │
│ CENAN_JI_01_INL │ JI_01_INL_20220322_OT_5155_45           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20220322_OT_5155_45.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1649342170000 │
│ CENAN_JI_01_INL │ JI_01_INL_20220510_OT_5173_45           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20220510_OT_5173_45.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1652695282000 │
│ CENAN_JI_01_INL │ JI_01_INL_20221006_BD_5226_45           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20221006_BD_5226_45.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1666182102000 │
│ CENAN_JI_01_INL │ JI_01_INL_20221117_AD_5239_45           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/JI_01_INL_20221117_AD_5239_45.ZIP           │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1669118610000 │
│ CENAN_JI_01_INL │ CENAN_DIS_JI_01_INL_20230503_CS_5283_45 │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/CENAN_DIS_JI_01_INL_20230503_CS_5283_45.ZIP │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1683705566000 │
│ CENAN_JI_01_INL │ JI_01_INL_20240425_CS_5429_60           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/CENAN_DIS_JI_01_INL_20240425_CS_5429_60.ZIP │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1714992038000 │
│ CENAN_JI_01_INL │ JI_01_INL_20250501_CS_5560_60           │ https://ehydroprod.blob.core.usgovcloudapi.net/ehydro-surveys/CENAN/CENAN_DIS_JI_01_INL_20250501_CS_5560_60.ZIP │ NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet │ 1746627940000 │
├─────────────────┴─────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────┴───────────────┤
│ 17 rows                                                                                                                                                                                                                                     5 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Download surveys

Get a list of URLs from the survey data csv.

```bash
duckdb -noheader -list \
       -c "select sourcedatalocation from read_csv('surveys.csv') where channelareaidfk LIKE '%JI_01%'" \
        > urls.txt
```

Download all zips

```bash
cat urls.txt | parallel --bar -j 10 'curl -s -L --create-dirs -o surveys/{/} {}'
```

**Bonus** no need to create a txt

```bash
duckdb -noheader -list \
       -c "select sourcedatalocation from read_csv('surveys.csv') where channelareaidfk LIKE '%JI_01%'" \
        | parallel --bar -j 10 'curl -s -L --create-dirs -o surveys/{/} {}'
```

**Extra Bonus** no need to create a csv. The following downloads the 10 most
recently uploaded USACE surveys

```bash
python surveys.py -n 10 \
                  --orderByFields 'dateuploaded DESC' \
                  --outFields sourcedatalocation --no-header \
        | parallel --progress -d "\r\n" -j 10 'curl -s -L --create-dirs -o surveys/{/} {}'
```

### Visualize XYZ USACE survey

This part is useful to inspect the data and make some sense out of it using
pandas and matplotlib


```bash
python totiff.py JI_01_INL_20250501_CS_5560_60.XYZ --preview
```

<img width="531" alt="image" src="https://github.com/user-attachments/assets/7ff42af1-883b-474e-baba-c7e14f0cdca2" />

#### Masking

`totiff.py` supports two methods for masking the interpolated grid data,
filtering by distance using [k-d trees] (default) and using a hull.

[k-d trees]: https://en.wikipedia.org/wiki/K-d_tree

Distance filtering is fast and preferred for large datasets, while a concave
hull is the most precise method for creating a mask, it will be very slow on
large inputs.

##### Example using distance filtering

```bash
eskerda@trouble orca % time python totiff.py sample/data/*.XYZ
21:07:46.789 | INFO | Reading CSV
21:07:46.820 | WARNING | sample/data/JI_01_INL_20230503_CS_5283_45_A.XYZ is comma separated
21:07:46.998 | WARNING | Found 52663 dupes in dataset, averaging
21:07:47.198 | INFO | x min/max: 1092164.65 1108222.98
21:07:47.199 | INFO | y min/max: 145660.02 160284.13
21:07:47.200 | INFO | z min/max: -11.8872 9.2202
21:07:47.200 | INFO | Size 2753313
21:07:47.200 | INFO | Interpolating: 25 x 25
21:07:48.197 | INFO | Generating mask
21:07:48.197 | INFO | Distance mask: True, 50.000000
21:07:49.187 | INFO | Smoothing mask: sigma 1.500000, cutoff 0.300000
21:07:49.190 | INFO | Applying mask
21:07:49.191 | INFO | generating output.tif
python totiff.py sample/data/*.XYZ  2.93s user 0.17s system 99% cpu 3.108 total
```

<img width="698" alt="image" src="https://github.com/user-attachments/assets/599a98c2-14cd-4536-9dd4-6cb8096addd2" />

##### Example using a convex hull

```bash
eskerda@trouble orca % time python totiff.py sample/data/*.XYZ --concave-mask
21:14:37.872 | INFO | Reading CSV
21:14:37.902 | WARNING | sample/data/JI_01_INL_20230503_CS_5283_45_A.XYZ is comma separated
21:14:38.080 | WARNING | Found 52663 dupes in dataset, averaging
21:14:38.281 | INFO | x min/max: 1092164.65 1108222.98
21:14:38.282 | INFO | y min/max: 145660.02 160284.13
21:14:38.283 | INFO | z min/max: -11.8872 9.2202
21:14:38.283 | INFO | Size 2753313
21:14:38.283 | INFO | Interpolating: 25 x 25
21:14:39.289 | INFO | Generating mask
21:14:39.289 | WARNING | concave mask filtering is slow, please wait
21:14:39.289 | INFO | Concave mask: True, 0.010000, 25.000000
21:16:02.386 | INFO | Smoothing mask: sigma 1.500000, cutoff 0.300000
21:16:02.390 | INFO | Applying mask
21:16:02.390 | INFO | generating output.tif
python totiff.py sample/data/*.XYZ --concave-mask  83.92s user 1.33s system 99% cpu 1:25.32 total
```

<img width="698" alt="image" src="https://github.com/user-attachments/assets/dbf98db1-050e-434f-910f-e8679c1e0032" />

Note this method didn't filter out data on parts of the bathymetry that were
very sparse. But it comes at a 20x cost.

On sparse data, it's important to tweak parameters to properly get a mask,
either by increasing the distance filter or by using a hull. On these cases
generally a convex hull works better since a concave hull will result in
overfitting into a weird shape.

For full usage, see `python totiff.py --help`

### Generate a tiff out of a XYZ USACE survey


```bash
python totiff.py JI_01_INL_20250501_CS_5560_60.XYZ
```

Multiple XYZ files can be processed by

```bash
python totiff.py *.XYZ
```

### Generate contours using gdal

```bash
gdal_contour -a depth \
             -fl -10 -5 -4 -3 -2 -1 -0.5 0 \
             output.tif out_lines.shp

gdal_contour -amin depth_min -amax depth_max \
             -p \
             -fl -10 -5 -4 -3 -2 -1 -0.5 0 \
             output.tif out_poly.shp
```

### Visualize tiff and contours

```bash
python tiffpl.py output.tif out_lines.shp
```

<img width="698" alt="image" src="https://github.com/user-attachments/assets/a21d5c7a-ceb6-4dda-beac-df959dcc41a2" />

### Contours in PostGIS

#### Run a postgis instance

##### docker compose

```bash
docker compose up -d postgis
```

##### docker

```bash
docker run --rm -it \
           -e POSTGRES_HOST_AUTH_METHOD=trust \
           -e PGDATA=/var/lib/postgresql/data/pgdata \
           -v pgdata:/var/lib/postgresql/data \
           --name postgis -p 5432:5432 -d postgis/postgis
```

> **_NOTE:_**  postgis still has no arm64 image available so on apple silicon
> you will need to [build the image][postgis-docker-repo] locally. Make sure to increase the docker
> memory limit when building.

```bash
git clone git@github.com:postgis/docker-postgis.git
cd docker-postgis/17-master
docker build -t postgis/postgis .
```

[postgis-docker-repo]: https://github.com/postgis/docker-postgis

#### Store contours in postgis

Note that before pushing the shapefiles to postgis they need to be reprojected
from the original CRS to EPSG:3857 (web mercator).

```bash
ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=orca user=postgres" \
        -nln bathy -nlt MULTILINESTRING \
        -s_srs EPSG:2263 -t_srs EPSG:3857 \
        out_lines.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=orca user=postgres" \
        -nln bathy_pol -nlt MULTIPOLYGON \
        -s_srs EPSG:2263 -t_srs EPSG:3857 \
        out_poly.shp
```

USAGE survey data contain the original projection as `sourceprojection`.

Use the utility script to get it in EPSG form

```bash
$ ./process.sh crs --survey-id JI_01_INL_20250501_CS_5560_60
EPSG:2263
$ ./process.sh crs --survey-id SF_24_HBX_20210424_CS
EPSG:2225
```

### Run www map visualization

#### Using docker compose

```bash
docker compose up -d wwww
```

The website should be available at http://localhost:1337

#### Locally

##### Start martin for tile serving

```bash
docker run -p 3000:3000 -e RUST_LOG=debug \
           -e DATABASE_URL=postgresql://postgres@host.docker.internal/orca \
           -v ./martin:/tmp/shared/ \
           --name martin --rm \
           ghcr.io/maplibre/martin
```

##### Build website and serve

```bash
cd www
npm i
npm run build
npm run preview
open http://localhost:4173/
```

Start a development server with

```bash
npm run dev
```

### process.sh

This script ties together the whole pipeline in a single place. It can be
used to download and extract USACE surveys, preview the information, query
CRS and generate the shapefiles.

```bash
           process.sh: USACE to WWW

Usage: process.sh action [options...]

Options:
  -V, --verbose     echo every command that gets executed
  --channel-id      filter by channel id (ex: CENAN_JI_01_INL)
  --survey-id       filter by survey id (ex: JI_01_INL_20250501_CS_5560_60)
  --                stop reading arguments
  -h, --help        display this help

Commands:
  help                            Show usage
  download                        Download surveys (based on filters)
  extract                         Extract survey data
  preview                         Generate a preview of survey data
  crs                             Get CRS used in survey as EPSG

  Example:
    $ ./process.sh download --survey-id JI_01_INL_20250501_CS_5560_60
    $ ./process.sh download --channel-id CENAN_JI_01_INL

    $ ./process.sh extract

    $ ./process.sh preview --survey-id JI_01_INL_20250501_CS_5560_60
    $ ./process.sh do --survey-id JI_01_INL_20250501_CS_5560_60

    $ ./process.sh crs --survey-id JI_01_INL_20250501_CS_5560_60

    $ ./process.sh preview --survey-id JI_01_INL_20250501_CS_5560_60 -- --help
    $ ./process.sh preview --survey-id JI_01_INL_20250501_CS_5560_60 -- \
            --grid-res 50 --distance-filter 100
    $ ./process.sh do --survey-id JI_01_INL_20250501_CS_5560_60 -- \
            --grid-res 50 --distance-filter 100 \
            -o foo.tif
```

## NOTES

The scripts on this repo are meant to be used and tweaked on selected surveys.
For most of the parts, there's a --preview counterpart that helps exploring the
dataset and tweaking parameters to get appropriate contour lines, depending on
the density of the survey and the quality of the data.

Ideally there would be **less work** done in `pandas` and `gdal_` locally, and
instead **leverage native postgis functions** and the `gdal` extension. Still I
think it's very useful to graph and visualize the information to get a feel of
it.

In general, the pipe looks like:

* Collect metadata (surveys.csv)
* Query surveys.csv and download a survey or any survey in a channel area from
USACE.
* Preview the information and tweak parameters
* Generate a tiff file and generate contours using gdal
* Push contours to postgis

### Useful links
* https://abelvm.github.io/sql/contour/
* https://epsg4253.wordpress.com/2013/02/08/building-contour-elevation-lines-with-gdal-and-postgis/
* https://postgis.net/docs/RT_reference.html
* https://gist.github.com/philippkraft/2da0ab4314dd334463fe0e04985bba32

## References

```
@software{tange_2024_14207479,
      author       = {Tange, Ole},
      title        = {GNU Parallel 20241122 ('Ahoo Daryaei')},
      month        = Nov,
      year         = 2024,
      note         = {{GNU Parallel is a general parallelizer to run
                       multiple serial command line programs in parallel
                       without changing them.}},
      publisher    = {Zenodo},
      doi          = {10.5281/zenodo.14207479},
      url          = {https://doi.org/10.5281/zenodo.14207479}
}
```
