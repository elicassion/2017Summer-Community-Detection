import os
import copy
import sys
import random
import gc
import time
import datetime
import ujson
from multiprocessing.pool import Pool
from multiprocessing import current_process
import pickle
from sklearn.metrics import roc_auc_score
# sys.path.append(os.path.abspath('..'))
from bigclam.predictor import predictor as BIGCLAMPredictor
from cdot.predictor import predictor as CDOTPredictor
import numpy as np

class ProgressBar:
    def __init__(self, name = '', total = 0, width = 20):
        self.total = total
        self.width = width
        self.count = 0
        self.name = name
        self.start_time = 0

    def start(self):
        self.start_time = time.time()

    def move(self):
        self.count += 1
        self.showProgress()

    def showProgress(self):
        progress = self.width * self.count / self.total
        elapsed = time.time() - self.start_time
        eta = elapsed * (self.total / self.count - 1)
        sys.stdout.write('%s: [%d/%d] ' % (self.name, self.count, self.total))
        sys.stdout.write('[' + '=' * round(progress) + '>' + '-' * round(self.width - progress) + '] ')
        sys.stdout.write('Elapsed: %ds/ETA: %ds\r' % (round(elapsed), round(eta)))
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()

def prdict_edges(predictor, edges, tag, predict_mode, toleration):
    scores = []
    count = 0
    # for edge in random.sample(edges, num):
    predict_bar = ProgressBar(name="Predicting", total=len(edges))
    predict_bar.start()
    for edge in edges:
        scores.append(predictor.time_predict(*edge, predict_mode, toleration))
        if count % 100000 == 0:
            print(datetime.datetime.now(), tag, count, np.sum(scores)/len(scores))
            sys.stdout.flush()
        count += 1
        predict_bar.move()
        # if count < 10:
        #     print (edge)
    return scores


if __name__ == '__main__':
    model2predictor = {
        'bigclam': BIGCLAMPredictor,
        'cdot': CDOTPredictor,
    }
    args = ujson.load(open(sys.argv[1]))
    pos_edges = ujson.load(open('pos_edges.json'))
    neg_edges = ujson.load(open('neg_edges.json'))
    uname2uid = ujson.load(open('uname2uid.json'))
    print(datetime.datetime.now(), 'Get Edges Done.')
    print("Pos Edges Num: ", len(pos_edges))
    sys.stdout.flush()

    predictor = model2predictor[args['model']]()
    # load data
    data_dir = os.path.join(args['root'], args['dataset_path'], args['mode'], args['conference'])
    predictor.load_data(data_dir)
    predictor.load_result(args['result_prefix'], args['n'], uname2uid, int(args['cc']))
    print(datetime.datetime.now(), 'Predictor Init Done.')
    sys.stdout.flush()
    if args['predict_mode'] == 'topk':
        pos_score = prdict_edges(predictor, pos_edges, 'pos: ', args['predict_mode'], float(args['toleration']))
        print(datetime.datetime.now(), 'Predict Pos Done.')
        sys.stdout.flush()

        # neg_score = prdict_edges(predictor, neg_edges, 'neg: ')
        # print(datetime.datetime.now(), 'predict neg done')
        # sys.stdout.flush()

        fp = open(os.path.join(args['score_prefix'], args['n'] + '.pos.conf_%s.txt' % args['toleration']), 'w')
        for score in pos_score:
            fp.write('%f\n' % score)
    elif args['predict_mode'] == 'nlog':
        pos_score = prdict_edges(predictor, pos_edges, 'pos: ', args['predict_mode'], float(args['toleration']))
        print(datetime.datetime.now(), 'Predict Pos Done.')
        sys.stdout.flush()
        fp = open(os.path.join(args['score_prefix'], args['n'] + '.pos.nlog.txt'), 'w')
        for score in pos_score:
            fp.write('%f\n' % score)
    fp.close()
    print(datetime.datetime.now(), 'Save Pos Done')
    sys.stdout.flush()

    # fp = open(os.path.join(args['score_prefix'], args['n'] + '.neg.txt'), 'w')
    # for score in neg_score:
    #     fp.write('%f\n' % score)
    # fp.close()
    # print(datetime.datetime.now(), 'save neg done')
    # sys.stdout.flush()
