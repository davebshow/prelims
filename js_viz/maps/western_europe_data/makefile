# BASED ON: https://gist.github.com/peterlozano/3a4578f64ec9630cfefe
all: we.json

we.json: subunits.json places.json provinces.json
	topojson \
		-o we.json \
		--id-property SU_A3 \
		--properties \
		-- \
		subunits.json \
		provinces.json \
		places.json

subunits.json: ne_10m_admin_0_map_subunits.shp
	ogr2ogr \
		-f GeoJSON \
		-where "ADM0_A3 IN ('ESP', 'PRT', 'FRA', 'BEL', 'ITA')" \
		subunits.json \
		ne_10m_admin_0_map_subunits.shp

ne_10m_admin_0_map_subunits.shp: ne_10m_admin_0_map_subunits.zip
	unzip ne_10m_admin_0_map_subunits.zip

ne_10m_admin_0_map_subunits.zip:
	wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_map_subunits.zip

provinces.json: ne_10m_admin_1_states_provinces.shp
	ogr2ogr \
		-f GeoJSON \
		-where "ADM0_A3 IN ('ESP', 'PRT', 'FRA', 'BEL', 'ITA')" \
		provinces.json \
		ne_10m_admin_1_states_provinces.shp

ne_10m_admin_1_states_provinces.shp: ne_10m_admin_1_states_provinces.zip
	unzip ne_10m_admin_1_states_provinces.zip

ne_10m_admin_1_states_provinces.zip:
	wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_1_states_provinces.zip

places.json: ne_10m_populated_places.shp
	ogr2ogr \
		-f GeoJSON \
		-where "ISO_A2 IN ('ES', 'PT', 'FR', 'BE', 'IT') AND SCALERANK < 7" \
		places.json \
		ne_10m_populated_places.shp

ne_10m_populated_places.shp: ne_10m_populated_places.zip
	unzip ne_10m_populated_places.zip

ne_10m_populated_places.zip:
	wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_populated_places.zip

clean:
	rm -rf we.json subunits.json places.json provinces.json

distclean: clean
	rm -rf ne_*
