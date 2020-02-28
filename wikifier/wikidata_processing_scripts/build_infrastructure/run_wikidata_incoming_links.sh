spark-submit --master local[24] \
--driver-memory 32g \
--executor-memory  32g \
 --py-files /data02/amandeep_wikidata/github/wikidata-wikifier/wikifier/wikidata_processing_scripts/build_infrastructure/wikidata_incoming_links.py \
wikidata_incoming_links.py \
/data02/amandeep_wikidata/data/wikidata_infrastructure_files_2/raw/latest-all.json.bz2 \
/data02/amandeep_wikidata/data/wikidata_infrastructure_files_2/wikidata_incoming_links