import json
from pyspark import SparkContext, SparkConf, StorageLevel
from optparse import OptionParser

compression = "org.apache.hadoop.io.compress.GzipCodec"


def json_loads(wiki_line):
    try:
        wj = json.loads(wiki_line[:-1])
        return wj
    except:
        print(wiki_line)
    return None


if __name__ == '__main__':
    sc = SparkContext(appName="WIKIData Preprocess Raw Files")
    parser = OptionParser()

    (c_options, args) = parser.parse_args()
    input_path = args[0]
    output_path = args[1]

    input_rdd = sc.textFile(input_path).map(lambda x: json_loads(x)).filter(lambda x: x is not None).map(
        lambda x: (x['id'], x))
    input_rdd.mapValues(lambda x: json.dumps(x)).saveAsSequenceFile(output_path, compressionCodecClass=compression)
