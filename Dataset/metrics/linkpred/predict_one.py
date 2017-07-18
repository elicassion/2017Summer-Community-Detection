import os
import copy
import sys
import random
import gc
import datetime
import ujson
from multiprocessing.pool import Pool
from multiprocessing import current_process
import pickle
from sklearn.metrics import roc_auc_score
sys.path.append(os.path.abspath('..'))
from BIGCLAM.predictor import predictor as BIGCLAMPredictor
from MAGIC.predictor import predictor as MAGICPredictor
from CODA.predictor import predictor as CODAPredictor


def prdict_edges(predictor, edges, tag):
    scores = []
    count = 0
    # for edge in random.sample(edges, num):
    for edge in edges:
        scores.append(predictor.link_predict(*edge))
        if count % 100000 == 0:
            print(datetime.datetime.now(), tag, count, scores[-1])
            sys.stdout.flush()
        count += 1
    return scores


if __name__ == '__main__':
    model2predictor = {
        'BIGCLAM': BIGCLAMPredictor,
        'MAGIC': MAGICPredictor,
        'CODA': CODAPredictor,
    }
    args = ujson.load(open(sys.argv[1]))
    pos_edges = ujson.load(open('pos_edges.json'))
    neg_edges = ujson.load(open('neg_edges.json'))
    uname2uid = ujson.load(open('uname2uid.json'))
    print(datetime.datetime.now(), 'get edges done')
    sys.stdout.flush()

    predictor = model2predictor[args['model']]()
    predictor.load_result(args['result_prefix'], uname2uid)
    print(datetime.datetime.now(), 'predictor init done')
    sys.stdout.flush()

    pos_score = prdict_edges(predictor, pos_edges, 'pos: ')
    print(datetime.datetime.now(), 'predict pos done')
    sys.stdout.flush()

    neg_score = prdict_edges(predictor, neg_edges, 'neg: ')
    print(datetime.datetime.now(), 'predict neg done')
    sys.stdout.flush()

    fp = open(args['score_prefix'] + '.pos.txt', 'w')
    for score in pos_score:
        fp.write('%f\n' % score)
    fp.close()
    print(datetime.datetime.now(), 'save pos done')
    sys.stdout.flush()

    fp = open(args['score_prefix'] + '.neg.txt', 'w')
    for score in neg_score:
        fp.write('%f\n' % score)
    fp.close()
    print(datetime.datetime.now(), 'save neg done')
    sys.stdout.flush()
