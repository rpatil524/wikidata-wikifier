import json
import glob
import gzip

input_path = '/data02/amandeep_wikidata/data/wikidata_infrastructure_files_2/wikidata_incoming_links'

d = dict()
c = 0
for f in glob.glob('{}/part-*'.format(input_path)):
    print('processing file: {}'.format(f))
    lines = open(f)
    for line in lines:
        if c % 10000 == 0:
            print('done with {} lines'.format(c))
        c += 1
        x = json.loads(line)
        d[x['qnode']] = x['incoming_links']

gzip.open('/data02/amandeep_wikidata/data/wikidata_infrastructure_files_2/incoming_links_dictionary.json.gz',
          'w').write(json.dumps(d))
print('Done')
