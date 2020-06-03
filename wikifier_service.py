import pathlib
import json
import pandas as pd
from uuid import uuid4
from flask import Flask
from flask import request
from flask import send_from_directory
from wikifier.wikifier import Wikifier

app = Flask(__name__)

wikifier = Wikifier()
config = json.load(open('wikifier/config.json'))


@app.route('/')
def wikidata_wikifier():
    return "ISI's Wikidata based wikifier"


@app.route('/wikify', methods=['POST'])
def wikify():
    columns = request.form.get('columns', None)
    case_sensitive = request.form.get('case_sensitive', 'true').lower() == 'true'
    skiprows = request.form.get('skiprows', None)
    if columns is not None:
        columns = columns.split(',')
        int_columns = check_if_columns_int(columns)
        if int_columns:
            if skiprows:
                df = pd.read_csv(request.files['file'], dtype=object, skiprows=int(skiprows), header=None)
            else:
                df = pd.read_csv(request.files['file'], dtype=object, lineterminator='\n', header=None)
        else:
            if skiprows:
                df = pd.read_csv(request.files['file'], dtype=object, skiprows=int(skiprows))
            else:
                df = pd.read_csv(request.files['file'], dtype=object, lineterminator='\n')
    else:
        if skiprows:
            df = pd.read_csv(request.files['file'], dtype=object, header=None, names=['value'], skiprows=int(skiprows))
        else:
            df = pd.read_csv(request.files['file'], dtype=object, header=None, names=['value'])
        columns = 'value'

    df.fillna('', inplace=True)
    _uuid_hex = uuid4().hex

    format = request.form.get('format')

    _path = 'user_files/{}_{}'.format(columns, _uuid_hex)
    pathlib.Path(_path).mkdir(parents=True, exist_ok=True)
    if format and (format.lower() == 'wikifier' or format.lower() == 'iswc'):
        df.to_csv('{}/input.csv'.format(_path), index=False, header=None)
    else:
        df.to_csv('{}/input.csv'.format(_path), index=False)

    r_df = wikifier.wikify(df, columns, format=format, case_sensitive=case_sensitive)
    if format and (format.lower() == 'wikifier' or format.lower() == 'iswc'):
        r_df.to_csv('{}/results.csv'.format(_path), index=False, header=False)
        lines = open('{}/results.csv'.format(_path)).readlines()
        lines = [line.replace('\n', '') for line in lines]
        return json.dumps({'data': lines})
    else:
        r_df.to_csv('{}/results.csv'.format(_path), index=False)
        return send_from_directory(_path, 'results.csv')


def check_if_columns_int(columns):
    if not isinstance(columns, list):
        columns = [columns]
    for column in columns:
        try:
            _ = int(column)
        except:
            return False
    return True


if __name__ == '__main__':
    app.run(threaded=True, host=config['host'], port=config['port'])
