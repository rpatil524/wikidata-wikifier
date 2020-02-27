import gzip
import json

"""
This file is downloaded from 
sitaware.isi.edu:/data02/amandeep_wikidata/data/wikidata_properties_map/spark_wikidata_dbpedia_joined_improved/wikidata_dbpedia_joined.jl.gz

It contains wikidata entities joined with their corresponding DBPedia entries.
Each document contains labels, aliases, descriptions, properties, property-values etc
"""

file_path = '/Users/amandeep/Documents/wikidata_dbpedia_joined.jl.gz'

f = gzip.open(file_path)
hierarchy_dict = {}
count = 1
for line in f:
    if count % 10000 == 0:
        print('processed {} rows'.format(count))
    count += 1
    j_x = json.loads(line)
    prop_vals = j_x.get('wd_prop_vals', [])
    if not isinstance(prop_vals, list):
        prop_vals = [prop_vals]
    qnode = j_x['id']
    for prop_val in prop_vals:
        if prop_val.startswith('P279'):
            # P279 is subclass of
            _ = prop_val.split('#')
            if _[1] not in hierarchy_dict:
                hierarchy_dict[_[1]] = list( )
            hierarchy_dict[_[1]].append(qnode)

open('/Users/amandeep/Github/wikidata-wikifier/wikifier/caches/wikidata_direct_children.json', 'w').write(
    json.dumps(hierarchy_dict))
