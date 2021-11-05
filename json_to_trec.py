# -*- coding: utf-8 -*-

import os
import requests
from nltk.stem import PorterStemmer
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download(['stopwords', 'punkt', 'averaged_perceptron_tagger', 'wordnet'])

outfn = 'test_trec_input.txt'
words_ = ['russia', 'syria', 'us', 'europ', 'umfragen', 'isis', 'iran', 'greek', 'airbnb', 'instacart', 'kickstarter',
          'dresden', 'assad', 'russische', 'syrien']

if os.path.exists(outfn):
    os.remove(outfn)
    print('deleting file')
else:
    print("The file does not exist")

f = open('test-queries.txt', mode='r', encoding='utf-8').read().split('\n')

q_ids = list()
queries = list()

for line_ in f:
    q_ids.append(line_.split(' ', 1)[0])
    q = line_.split(' ', 1)[1].replace(':', '').replace("'", " ").replace('-', ' ').replace('.', '').replace(
        ',', ' ').replace('’', ' ').strip()
    ps = PorterStemmer()
    q = q.lower()
    q = [_ for _ in q.split() if _ not in ['', ' '] and len(_) > 1]

    t = ''
    for _ in q:
        if _.startswith('#'):
            t = t + _[1:] + '^2 '
        else:
            t = t + _ + ' '
    q = t.strip()
    q = q + ' ~10'

    queries.append(q)

# BM25
for _, q in enumerate(queries):
    inurl = 'http://localhost:8983/solr/project3_BM25/select?q={}&fl=id%2Cscore&defType=edismax&qf=text_en+text_de+text_ru&wt=json&indent=true&rows=20'.format('%20'.join(q.split()))
    qid = q_ids[_]
    IRModel = 'bm25'
    outf = open(outfn, 'a+')
    data = eval(requests.get(inurl).text.replace('true', 'True').replace('false', 'False'))
    docs = data['response']['docs']

    rank = 1
    for doc in docs:
        outf.write(
            qid + ' ' + 'Q0' + ' ' + str(doc['id']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
        rank += 1
    outf.close()

#VSM
for _, q in enumerate(queries):
    inurl = 'http://localhost:8983/solr/project3_VSM/select?q={}&fl=id%2Cscore&defType=edismax&qf=text_en+text_de+text_ru&wt=json&indent=true&rows=20'.format('%20'.join(q.split()))
    qid = q_ids[_]
    IRModel = 'vsm'
    outf = open(outfn, 'a+')
    data = eval(requests.get(inurl).text.replace('true', 'True').replace('false', 'False'))
    docs = data['response']['docs']

    rank = 1
    for doc in docs:
        outf.write(
            qid + ' ' + 'Q0' + ' ' + str(doc['id']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
        rank += 1
    outf.close()
