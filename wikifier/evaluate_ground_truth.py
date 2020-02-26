import os
import requests
import pandas as pd
from io import StringIO
from glob import glob
import json


def check_if_correct_uri(correct_uris, answer_uri):
    if not isinstance(answer_uri, str) or answer_uri.strip() == "":
        return '-1'
    uris = [x.strip() for x in correct_uris.split(' ')]
    return '1' if answer_uri in uris else '0'


def upload_files(file_path, url, column_name):
    file_name = os.path.basename(file_path)
    payload = {
        'columns': column_name,
        'case_sensitive': 'false'
    }
    files = {
        'file': (file_name, open(file_path, mode='rb'), 'application/octet-stream')
    }
    resp = requests.post(url, data=payload, files=files)

    s = str(resp.content, 'utf-8')

    data = StringIO(s)

    df = pd.read_csv(data)

    df['__dummy'] = list(zip(df.correct_uris, df.Value_answer_dburi))
    df['evaluation'] = df['__dummy'].map(lambda x: check_if_correct_uri(x[0], x[1]))
    df.drop(columns=['__dummy'], inplace=True)
    total = len(df)
    correct = len(df[df.evaluation == '1'])
    no_answer = len(df[df.evaluation == '-1'])
    precision = float(correct) / (float(total - no_answer))
    recall = float(correct) / float(total)
    f1 = 2 * precision * recall / (precision + recall)
    judgement_dict[file_name] = {'f1': f1, 'p': precision, 'r': recall}
    df.to_csv('{}/output/{}'.format(ground_truth_path, file_name), index=False, header=False)
    return resp.status_code


ground_truth_path = 'ground_truth'
judgement_dict = {}
url = "http://localhost:7805/wikify"

print(__file__)
for f_path in glob('{}/input/dataset_*.csv'.format(ground_truth_path)):
    print(f_path)
    print(upload_files(f_path, url, 'Value'))
print(json.dumps(judgement_dict, indent=2))
