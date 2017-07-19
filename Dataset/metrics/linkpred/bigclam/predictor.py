import numpy as np
import os
from math import exp


class predictor(object):

    def __init__(self):
        super(predictor, self).__init__()
        # self.data_dir = data_dir
        # self.result_prefix = result_prefix
        # self.load()

    def load_data(self, data_dir):
        self.uname2uid = {}
        for line in open(os.path.join(data_dir, 'link.txt')):
            line = line.split('\t')
            if line[0] not in self.uname2uid:
                self.uname2uid[line[0]] = len(self.uname2uid)
            if line[1] not in self.uname2uid:
                self.uname2uid[line[1]] = len(self.uname2uid)
        print ("load data done.")

    def load_result(self, result_prefix, uname2uid):
        resf = open(os.path.join(result_prefix, n + '.f.txt'), 'r')
        res = resf.read()
        # print (res)
        lines = res.split('\n')
        au_num = len(uname2uid)
        self.f = np.zeros([au_num, cc])
        for au_id, line in enumerate(lines[1:-1]):
            items = line.split('\t')
            au = uname2uid[items[0]]
            edges = items[1].strip(' ')
            if edges is '0':
                continue
            edges = edges.split(' ')
            for i in range(1, len(edges)-1, 2):
                comm_id = int(edges[i])
                self.f[au_id][comm_id] = float(edges[i+1])
        self.U = au_num
        self.C = cc
        print ("load result done.")
        # print (np.dot(self.f[0], self.f[1]))
        print (np.dot(norm.pdf(1994, self.mu[0], self.sigma[0]), norm.pdf(1998, self.mu[1], self.sigma[1])))

    def link_predict(self, from_user, to_user):
        result = np.dot(self.f[from_user], self.f[to_user])
        result = 1 - exp(-result)
        return result
