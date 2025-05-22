sample:
	duckdb -noheader -list \
	       -c "select sourcedatalocation from read_csv('surveys.sample.csv')" \
		| parallel --bar -j 10 'curl -s -L --create-dirs -o sample/{/} {}'

.PHONY: clean
clean:
	rm -rf *.shp *.shx *.dbf *.prj *.tif sample
