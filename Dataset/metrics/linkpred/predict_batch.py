import os
import copy
import sys
import random
import subprocess
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


def genearate_tmp_filename(s):
    return ('tmp-' + str(hash(s)) + str(datetime.datetime.now()) + '.txt').replace(' ', '_').replace(':', '_')


def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        while True:
            try:
                os.makedirs(path)
                break
            except:
                if os.path.exists(path):
                    break


def load_edges(data_dir, predictor):
    edges = set()
    for line in open(os.path.join(data_dir, 'network.txt')):
        line = [i for i in line.split() if i in predictor.uname2uid]
        # print(line)
        doc_id = predictor.uname2uid[line[0]]
        for uname in line[1:]:
            ref_id = predictor.uname2uid[uname]
            edges.add((ref_id, doc_id))
    print(str(len(edges)) + " = len(edges)")
    return edges


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


def get_neg_edges(edges, predictor, max_uid, num):
    neg_edges = []
    for i in range(num):
        while True:
            from_user = random.randint(0, max_uid)
            to_user = random.randint(0, max_uid)
            if isinstance(predictor, MAGICPredictor):
                if predictor.label[from_user][1] == predictor.label[to_user][1]:
                    continue
                elif predictor.label[from_user][1] > predictor.label[to_user][1]:
                    from_user, to_user = to_user, from_user
            if (from_user, to_user) not in edges and (to_user, from_user) not in edges:
                break
        neg_edges.append((from_user, to_user))
    return neg_edges


def load_data(args):
    model2predictor = {
        'MAGIC': MAGICPredictor,
        'BIGCLAM': BIGCLAMPredictor,
        'CODA': CODAPredictor,
    }
    predictor = model2predictor[args['model']]()
    data_dir = '{root:s}/Datasets/{dataset:s}/'.format(**args)
    predictor.load_data(data_dir)
    ujson.dump(predictor.uname2uid, open('uname2uid.json', 'w'))
    global edges
    edges = load_edges(data_dir, predictor)
    # ujson.dump(edges, open('edges.json', 'w'))
    pos_edges = random.sample(edges, int(len(edges) * 0.1))
    neg_edges = get_neg_edges(edges, predictor, len(predictor.uname2uid) - 1, int(len(edges) * 0.1))
    print(datetime.datetime.now(), 'load edges done')
    sys.stdout.flush()
    return pos_edges, neg_edges


def predict(args):
    print(datetime.datetime.now(), args)
    sys.stdout.flush()
    args['data_dir'] = '{root:s}/Datasets/{dataset:s}/'.format(**args)
    model2result_prefix = {
        'MAGIC': '{root:s}/Results/{dataset:s}/{model:s}/cc{cc:d}_{n:s}',
        'BIGCLAM': '{root:s}/Results/{dataset:s}/{model:s}/cc{cc:d}_',
        'CODA': '{root:s}/Results/{dataset:s}/{model:s}/cc{cc:d}_',
    }
    args['result_prefix'] = model2result_prefix[args['model']].format(**args)
    model2score_prefix = {
        'MAGIC': '{root:s}/Scores/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_{n:s}',
        'BIGCLAM': '{root:s}/Scores/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_',
        'CODA': '{root:s}/Scores/{exp:s}/{dataset:s}/{model:s}/cc{cc:d}_',
    }
    args['score_prefix'] = model2score_prefix[args['model']].format(**args)
    mkdir_if_not_exists(os.path.dirname(args['score_prefix']))
    print (args)
    if not (os.path.exists(args['score_prefix'] + '.pos.txt') and os.path.exists(args['score_prefix'] + '.neg.txt')):
        tmp_filename = genearate_tmp_filename(ujson.dumps(args))
        ujson.dump(args, open(tmp_filename, 'w'))
        # print (tmp_filename)
        subprocess.run('python predict_one.py %s' % tmp_filename, shell=True)
        os.remove(tmp_filename)
    pos_score = [float(line) for line in open(args['score_prefix'] + '.pos.txt')]
    neg_score = [float(line) for line in open(args['score_prefix'] + '.neg.txt')]
    auc = roc_auc_score([1] * len(pos_score) + [0] * len(neg_score), pos_score + neg_score)
    print(datetime.datetime.now(), 'auc: ', auc)
    sys.stdout.flush()

    args['score'] = auc
    return args


if __name__ == '__main__':
    dataset = sys.argv[1]
    model = sys.argv[2]
    community_count = [
        100,
    ]

    exp = 'link_pred'
    root = os.path.abspath('../..')
    pos_edges, neg_edges = load_data({'exp': exp, 'root': root, 'model': model, 'dataset': dataset})
    ujson.dump(pos_edges, open('pos_edges.json', 'w'))
    del pos_edges
    ujson.dump(neg_edges, open('neg_edges.json', 'w'))
    del neg_edges
    result = []
    to_pred = []
    for cc in community_count:
        to_pred.append({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'n': 'final'})
        # predict({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': 'final'})
        gc.collect()
        if 'MAGIC' in model:
            for n in range(0, 100, 10):
                to_pred.append({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'n': '%05d' % n})
                # predict({'exp': exp, 'root': root, 'model': model, 'dataset': dataset, 'cc': cc, 'lw': lw, 'n': '%04d' % n})
    result += Pool(6).map(predict, to_pred, chunksize=1)
    pickle.dump(result, open('result_batch.pkl', 'wb'))
