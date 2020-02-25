from similarity.normalized_levenshtein import NormalizedLevenshtein

label_fields = ['wd_labels', 'wd_aliases', 'person_abbr']


class AddLevenshteinSimilarity(object):
    def __init__(self):
        self.lev = NormalizedLevenshtein()

    def lev_mapper(self, label, wikidata_json, case_sensitive=True):
        qnode = wikidata_json['id']
        max_lev = -1
        max_label = None
        label_lower = label.lower()
        for label_field in label_fields:
            _labels = wikidata_json.get(label_field)
            for l in _labels:
                if case_sensitive:
                    lev_similarity = self.lev.similarity(label, l)
                else:
                    lev_similarity = self.lev.similarity(label_lower, l.lower())
                if lev_similarity > max_lev:
                    max_lev = lev_similarity
                    max_label = l
        if 'db_labels' in wikidata_json and 'en' in wikidata_json['db_labels']:
            en_labels = wikidata_json['db_labels']['en']
            if not isinstance(en_labels, list):
                en_labels = [en_labels]
            for l in en_labels:
                if case_sensitive:
                    lev_similarity = self.lev.similarity(label, l)
                else:
                    lev_similarity = self.lev.similarity(label_lower, l.lower())
                if lev_similarity > max_lev:
                    max_lev = lev_similarity
                    max_label = l

        if max_label is not None:
            return (qnode, max_lev, max_label)
        return (None, None, None)

    @staticmethod
    def candidates_from_candidate_string(candidate_string):
        qnode_set = set()
        db_group_set = set()
        if candidate_string is not None and isinstance(candidate_string, str):
            c_tuples = candidate_string.split('@')
            for c_tuple in c_tuples:
                if c_tuple is not None and isinstance(c_tuple, str) and c_tuple != 'nan':
                    try:
                        vals = c_tuple.split(':')
                        if vals[0] != '5':
                            qnode_set.add(vals[1])
                        else:
                            _ = vals[1].split('$')
                            db_group_set.add(_[0])
                            if len(_) > 1:
                                qnode_set.add(_[1])
                    except:
                        print(c_tuple)

        return list(qnode_set), list(db_group_set)

    def compute_lev(self, label_cand_str, wikidata_index_dict, case_sensitive):
        clean_label = label_cand_str[0]
        candidate_string = label_cand_str[1]
        qnodes, db_groups = self.candidates_from_candidate_string(candidate_string)
        wikidata_jsons = [wikidata_index_dict[qnode] for qnode in qnodes if qnode in wikidata_index_dict]

        results = []
        for wikidata_json in wikidata_jsons:
            r = self.lev_mapper(clean_label, wikidata_json, case_sensitive=case_sensitive)
            if r[0] is not None:
                results.append('{}:{}'.format(r[0], r[1]))

        return '@'.join(results)

    def add_lev_feature(self, df, wikidata_index_dict, case_sensitive):
        df['_dummy'] = list(zip(df._clean_label, df._candidates))
        df['lev_feature'] = df['_dummy'].map(
            lambda x: self.compute_lev(x, wikidata_index_dict, case_sensitive))
        return df
