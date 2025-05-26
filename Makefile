# For advanced usage, look at the process.sh script

IN_CRS=EPSG:2263
OUT_CRS=EPSG:3857
LEVELS="-10 -5 -4 -3 -2 -1 -0.5 0"
OUTNAME ?= output
OUTFILE := $(OUTNAME).tif
OUTFILE_LINES := $(OUTNAME)_lines.shp
OUTFILE_POLY := $(OUTNAME)_poly.shp

all: preview

sample:
	# XXX Make it so incomplete downloads can be resumed
	cat surveys.sample.txt | parallel --bar -j 10 'curl -s -L --create-dirs -o sample/{/} {}'
	cd sample; unzip -j '*.ZIP' "*.XYZ" -x "*FULL.XYZ" -x "*_A.XYZ" -d data

$(OUTFILE): sample
	python totiff.py -o $(OUTFILE) \
		$$(find ./sample/data -type f -name '*.XYZ' ! -name '*_FULL.XYZ')

$(OUTFILE_LINES): $(OUTFILE)
	gdal_contour -a depth -fl $(LEVELS) $(OUTFILE) $(OUTFILE_LINES)

$(OUTFILE_POLY): $(OUTFILE)
	gdal_contour -amin depth_min -amax depth_max -p -fl $(LEVELS) $(OUTFILE) $(OUTFILE_POLY)

.PHONY: install
install:
	pip install -r requirements.txt
	@echo "warming up env. This might take a long time ..."
	python totiff.py --help

.PHONY: contours
contours: $(OUTFILE_LINES) $(OUTFILE_POLY)

.PHONY: preview
preview: $(OUTFILE) $(OUTFILE_LINES)
	python tiffpl.py $(OUTFILE) $(OUTFILE_LINES)

.PHONY: preview-poly
preview-poly: $(OUTFILE) out_poly.shp
	python tiffpl.py $(OUTFILE) $(OUTFILE_POLY)

.PHONY: push-contours
push-contours: contours
	ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=orca user=postgres" \
        -nln bathy -nlt MULTILINESTRING \
	-s_srs $(IN_CRS) -t_srs $(OUT_CRS) \
	$(OUTFILE_LINES)
	ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=orca user=postgres" \
        -nln bathy_pol -nlt MULTIPOLYGON \
	-s_srs $(IN_CRS) -t_srs $(OUT_CRS) \
	$(OUTFILE_POLY)

.PHONY: clean
clean:
	rm -rf *.shp *.shx *.dbf *.prj *.tif
