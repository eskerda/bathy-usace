# USACE Bathymetry ingestion pipeline

## Generate a CSV of USACE surveys feature data from arcgis

Get survey information from USACE arcgis website as CSV.

```bash
python surveys.py > surveys.csv
```

To get a subset of it, run it like

```bash
python surveys.py --query "(usacedistrictcode='CENAN') AND (channelareaidfk='CENAN_JI_01_INL')" > surveys.JI_01.csv
```

Now you can query relevant information with any CSV tool

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


## Download surveys

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

** Bonus ** no need to create a txt

```bash
duckdb -noheader -list \
       -c "select sourcedatalocation from read_csv('surveys.csv') where channelareaidfk LIKE '%JI_01%'" \
        | parallel --bar -j 10 'curl -s -L --create-dirs -o surveys/{/} {}'
```

## Visualize XYZ USACE survey

This part is useful to inspect the data and make some sense out of it using
pandas and matplotlib


```bash
python process.py JI_01_INL_20250501_CS_5560_60.XYZ
```

<img width="531" alt="image" src="https://github.com/user-attachments/assets/7ff42af1-883b-474e-baba-c7e14f0cdca2" />


## Generate a tiff out of a XYZ USACE survey


```bash
python totiff.py JI_01_INL_20250501_CS_5560_60.XYZ
```

Multiple XYZ files can be processed by

```bash
python totiff.py *.XYZ
```

## Generate contours using gdal

```bash
gdal_contour -a depth \
             -fl -10 -5 -4 -3 -2 -1 -0.5 0 \
             output.tif out_lines.shp

gdal_contour -amin depth_min -amax depth_max \
             -p \
             -fl -10 -5 -4 -3 -2 -1 -0.5 0 \
             output.tif out_poly.shp
```

## Visualize tiff and contours

```bash
python tiffpl.py output.tif out_lines.shp
```

<img width="698" alt="image" src="https://github.com/user-attachments/assets/754ff612-9e29-4945-8091-a45585481407" />

## Contours in PostGIS

### Run a postgis instance

```bash
docker run --rm -it \
           -e POSTGRES_HOST_AUTH_METHOD=trust \
           -e PGDATA=/var/lib/postgresql/data/pgdata \
           -v pgdata:/var/lib/postgresql/data \
           --name postgis -p 5432:5432 -d postgis/postgis
```

> **_NOTE:_**  postgis still has no arm64 image available so on apple silicon
> you will need to build the image locally. Make sure to increase the docker
> memory limit when building.

```bash
git clone git@github.com:postgis/docker-postgis.git
cd docker-postgis/17-master
docker build -t local/postgis .
```

### Store contours in postgis

```bash
ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=orca user=postgres" \
        -nln bathy -nlt MULTILINESTRING \
        out_lines.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=orca user=postgres" \
        -nln bathy_pol -nlt MULTIPOLYGON \
        out_poly.shp
```


## Run www map visualization

### Start martin for tile serving

```bash
docker run -p 3000:3000 -e RUST_LOG=debug \
           -e DATABASE_URL=postgresql://postgres@host.docker.internal/orca \
           -v ./martin:/tmp/shared/ \
           --name martin --rm \
           ghcr.io/maplibre/martin
```

### Build website and serve

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

## NOTES

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
