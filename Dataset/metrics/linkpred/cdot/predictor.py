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

    def load_result(self, result_prefix, n, uname2uid):
        resf = open(os.path.join(result_prefix, n + '.f_mu_sigma.txt'), 'r')
        res = resf.read()
        lines = res.split('\n')
        au_num = len(uname2uid)
        self.f = np.zeros([au_num, 100])
        self.mu = np.zeros([au_num, 100])
        self.sigma = np.zeros([au_num, 100])
        for au_id, line in enumerate(lines[1:-1]):
            items = line.split('\t')
            au = items[0]
            edges = items[1]
            if edges is not '[]':
                edges = edges.replace('[', '').replace(']', '').split(' ')
            else:
                continue
            for edge in edges[-1]:
                edge = edge.replace('(', '').replace(')', '')
                tpl = edge.split(',')
                comm_id = int(tpl[0])
                self.f[au_id][comm_id] = float(tpl[1])
                self.mu[au_id][comm_id] = float(tpl[2])
                self.sigma[au_id][comm_id] = float(tpl[3])
        self.U = au_num
        self.C = 100
        print ("load result done.")
        # print (np.dot(self.f[0], self.f[1]))

    def link_predict(self, from_user, to_user, from_time, to_time):
        # TODO: revise formula
        # print ()
        result = np.dot(self.f[from_user], self.f[to_user])
        result = 1 - exp(-result)
        return result
