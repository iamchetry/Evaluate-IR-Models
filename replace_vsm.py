import os
import pysolr
import requests
import json

CORE_NAME = "project3_VSM"
AWS_IP = "localhost"


def delete_core(core=CORE_NAME):
    print(os.system('sudo su - solr -c "/opt/solr/bin/solr delete -c {core}"'.format(core=core)))


def create_core(core=CORE_NAME):
    print(os.system(
        'sudo su - solr -c "/opt/solr/bin/solr create -c {core} -n data_driven_schema_configs"'.format(
            core=core)))


class Indexer:
    def __init__(self):
        self.solr_url = f'http://{AWS_IP}:8983/solr/'
        self.connection = pysolr.Solr(self.solr_url + CORE_NAME, always_commit=True, timeout=5000000)

    def do_initial_setup(self):
        delete_core()
        create_core()

    def create_documents(self, docs):
        self.connection.add(docs)

    def retrieve(self):
        return self.connection.search(q='Assad und ISIS auf dem Vormarsch',
                                      **{'defType': 'dismax',
                                         'qf': 'text_en text_de text_ru',
                                         'indent': 'true',
                                         'fl': 'id,score',
                                         'rows': '20',
                                         'wt': 'json'})

    def add_fields(self):
        data = {
            "add-field": [
                {
                    "name": "lang",
                    "type": "string",
                    "multiValued": False
                },
                {
                    "name": "text_de",
                    "type": "text_general",
                    "multiValued": False
                }, {
                    "name": "text_en",
                    "type": "text_general",
                    "multiValued": False
                },
                {
                    "name": "text_ru",
                    "type": "text_general",
                    "multiValued": False
                },
                {
                    "name": "tweet_urls",
                    "type": "strings",
                    "multiValued": True
                },
                {
                    "name": "tweet_hashtags",
                    "type": "strings",
                    "multiValued": True
                }
            ]
        }

        requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json()

    def replace_fields(self):
        data = {
            "replace-field": [
                {
                    "name": "age",
                    "type": "string",
                    "multiValued": False
                }
            ]
        }

        requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json()

    def replace_VSM(self):
        data = {
            "replace-field-type": [
                {
                    'name': 'text_en',
                    'class': 'solr.TextField',
                    'positionIncrementGap': '100',
                    'indexAnalyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.StopFilterFactory',
                            'words': 'lang/stopwords_en.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.EnglishPossessiveFilterFactory'
                        }, {
                            'class': 'solr.KeywordMarkerFilterFactory',
                            'protected': 'protwords.txt'
                        }, {
                            'class': 'solr.PorterStemFilterFactory'
                        }]
                    },
                    'similarity': {
                        'class': 'solr.ClassicSimilarityFactory'
                    },
                    'queryAnalyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.SynonymGraphFilterFactory',
                            'expand': 'true',
                            'ignoreCase': 'true',
                            'synonyms': 'synonyms.txt'
                        }, {
                            'class': 'solr.StopFilterFactory',
                            'words': 'lang/stopwords_en.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.EnglishPossessiveFilterFactory'
                        }, {
                            'class': 'solr.KeywordMarkerFilterFactory',
                            'protected': 'protwords.txt'
                        }, {
                            'class': 'solr.PorterStemFilterFactory'
                        }]
                    }
                }, {
                    'name': 'text_ru',
                    'class': 'solr.TextField',
                    'positionIncrementGap': '100',
                    'analyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.StopFilterFactory',
                            'format': 'snowball',
                            'words': 'lang/stopwords_ru.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.SnowballPorterFilterFactory',
                            'language': 'Russian'
                        }]
                    },
                    'similarity': {
                        'class': 'solr.ClassicSimilarityFactory'
                    },
                }, {
                    'name': 'text_de',
                    'class': 'solr.TextField',
                    'positionIncrementGap': '100',
                    'analyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.StopFilterFactory',
                            'format': 'snowball',
                            'words': 'lang/stopwords_de.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.GermanNormalizationFilterFactory'
                        }, {
                            'class': 'solr.GermanLightStemFilterFactory'
                        }]
                    },
                    'similarity': {
                        'class': 'solr.ClassicSimilarityFactory'
                    },
                }
            ]
        }

        requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json()


if __name__ == "__main__":
    with open('train.json', encoding='utf-8') as f:
        collection = json.load(f)

    i = Indexer()
    i.do_initial_setup()
    i.replace_VSM()
    i.add_fields()
    i.create_documents(collection)
