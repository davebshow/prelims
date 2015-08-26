# BASED ON: https://gist.github.com/peterlozano/3a4578f64ec9630cfefe
all: peru.json

peru.json: subunits.json places.json provinces.json
	topojson \
		-o peru.json \
		--id-property SU_A3 \
		--properties \
		-- \
		subunits.json \
		provinces.json \
		places.json

subunits.json: ne_10m_admin_0_map_subunits.shp
	ogr2ogr \
		-f GeoJSON \
		-where "ADM0_A3 IN ('PER')" \
		subunits.json \
		ne_10m_admin_0_map_subunits.shp

ne_10m_admin_0_map_subunits.shp: ne_10m_admin_0_map_subunits.zip
	unzip ne_10m_admin_0_map_subunits.zip

ne_10m_admin_0_map_subunits.zip:
	wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_map_subunits.zip

provinces.json: ne_10m_admin_1_states_provinces.shp
	ogr2ogr \
		-f GeoJSON \
		-where "ADM0_A3 IN ('PER')" \
		provinces.json \
		ne_10m_admin_1_states_provinces.shp

ne_10m_admin_1_states_provinces.shp: ne_10m_admin_1_states_provinces.zip
	unzip ne_10m_admin_1_states_provinces.zip

ne_10m_admin_1_states_provinces.zip:
	wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_1_states_provinces.zip

places.json: ne_10m_populated_places.shp
	ogr2ogr \
		-f GeoJSON \
		-where "ISO_A2 IN ('PE') AND SCALERANK < 6" \
		places.json \
		ne_10m_populated_places.shp

ne_10m_populated_places.shp: ne_10m_populated_places.zip
	unzip ne_10m_populated_places.zip

ne_10m_populated_places.zip:
	wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_populated_places.zip

clean:
	rm -rf peru.json subunits.json places.json provinces.json

distclean: clean
	rm -rf ne_*
