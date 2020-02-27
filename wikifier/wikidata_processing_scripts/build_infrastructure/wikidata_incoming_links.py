import json
from pyspark import SparkContext, SparkConf, StorageLevel
from optparse import OptionParser


def wikidata_incoming_map(wiki_json):
    """
    Create a dictionary with keys as properties whose objects are wikidata QNodes
    :param wiki_json: one wikidata record in json format
    :return: a dictionary
    """
    incoming_dict = dict()
    claims = wiki_json.get('claims', dict())
    for prop, snaks in claims.items():
        if not isinstance(snaks, list):
            snaks = [snaks]
        for snak in snaks:
            mainsnak = snak.get('mainsnak')
            mainsnak_datavalue = mainsnak.get('datavalue', None)
            if mainsnak_datavalue:
                if mainsnak_datavalue.get('type', "") == "wikibase-entityid":
                    object = mainsnak_datavalue['value']['id']
                    if object not in incoming_dict:
                        incoming_dict[object] = 0
                    incoming_dict[object] += 1

    tup_list = list()
    for k, v in incoming_dict.items():
        tup_list.append((k, v))
    return tup_list if len(tup_list) > 0 else [(None, None)]


if __name__ == '__main__':
    sc = SparkContext(appName="WIKIData Incoming Links")
    parser = OptionParser()

    (c_options, args) = parser.parse_args()
    input_path = args[0]
    output_path = args[1]

    input_rdd = sc.textFile(input_path).mapValues(lambda x: json.loads(x))

    wiki_map_rdd = input_rdd.flatMap(lambda x: wikidata_incoming_map(x[1])).filter(
        lambda x: x[1] is not None).reduceByKey(lambda x, y: x + y)
    wiki_map_rdd.persist(StorageLevel.MEMORY_AND_DISK)
    output_rdd = wiki_map_rdd.map(lambda x: {'qnode': x[0], 'incoming_links': x[1]}).map(lambda x: json.dumps(x))
    output_rdd.saveAsTextFile(output_path)
