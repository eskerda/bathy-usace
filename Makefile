IN_CRS=EPSG:2263
OUT_CRS=EPSG:3857

sample:
	# XXX Make it so incomplete downloads can be resumed
	cat surveys.sample.txt | parallel --bar -j 10 'curl -s -L --create-dirs -o sample/{/} {}'
	cd sample; unzip -j '*.ZIP' "*.XYZ" -x "*FULL.XYZ" -d data

output.tif: sample
	python totiff.py \
		$$(find ./sample/data -type f -name '*.XYZ' ! -name '*_FULL.XYZ')

out_lines.shp: output.tif
	gdal_contour -a depth -fl -10 -5 -4 -3 -2 -1 -0.5 0 output.tif out_lines.shp

out_poly.shp: output.tif
	gdal_contour -amin depth_min -amax depth_max -p -fl -10 -5 -4 -3 -2 -1 -0.5 0 output.tif out_poly.shp

.PHONY: install
install:
	pip install -r requirements.txt
	@echo "warming up env. This might take a long time ..."
	python totiff.py --help

.PHONY: contours
contours: out_lines.shp out_poly.shp

.PHONY: preview
preview: output.tif out_lines.shp
	python tiffpl.py output.tif out_lines.shp

.PHONY: preview-poly
preview-poly: output.tif out_poly.shp
	python tiffpl.py output.tif out_poly.shp

.PHONY: push-contours
push-contours: contours
	ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=orca user=postgres" \
        -nln bathy -nlt MULTILINESTRING \
	-s_srs $(IN_CRS) -t_srs $(OUT_CRS) \
        out_lines.shp
	ogr2ogr -f "PostgreSQL" PG:"host=localhost dbname=orca user=postgres" \
        -nln bathy_pol -nlt MULTIPOLYGON \
	-s_srs $(IN_CRS) -t_srs $(OUT_CRS) \
        out_poly.shp

.PHONY: clean
clean:
	rm -rf *.shp *.shx *.dbf *.prj *.tif
	psql -h localhost -U postgres orca -c "DROP TABLE bathy; DROP TABLE bathy_pol;" || true
