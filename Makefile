sample:
	duckdb -noheader -list \
	       -c "select sourcedatalocation from read_csv('surveys.sample.csv')" \
		| parallel --bar -j 10 'curl -s -L --create-dirs -o sample/{/} {}'

output.tif: sample
	python totiff.py $$(find ./sample -type f -name '*.XYZ' ! -name '*_FULL.XYZ')

out_lines.shp: output.tif
	gdal_contour -a depth -fl -10 -5 -4 -3 -2 -1 -0.5 0 output.tif out_lines.shp

out_poly.shp: output.tif
	gdal_contour -amin depth_min -amax depth_max -p -fl -10 -5 -4 -3 -2 -1 -0.5 0 output.tif out_poly.shp

.PHONY: preview
preview: sample output.tif out_lines.shp out_poly.shp
	python tiffpl.py output.tif out_lines.shp out_poly.shp

.PHONY: clean
clean:
	rm -rf *.shp *.shx *.dbf *.prj *.tif sample
