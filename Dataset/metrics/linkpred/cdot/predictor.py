import numpy as np
import os
from math import exp
from scipy.stats import norm

class predictor(object):

    def __init__(self):
        super(predictor, self).__init__()
        # self.data_dir = data_dir
        # self.result_prefix = result_prefix
        # self.load()

    def load_data(self, data_dir):
        self.uname2uid = {}
        for line in open(os.path.join(data_dir, 'links.txt')):
            line = line.split('\t')
            if line[0] not in self.uname2uid:
                self.uname2uid[line[0]] = len(self.uname2uid)
            if line[1] not in self.uname2uid:
                self.uname2uid[line[1]] = len(self.uname2uid)
        print ("Load Data Done.")

    def load_result(self, result_prefix, n, uname2uid, cc):
        # print (os.path.join(result_prefix, n + '.f_mu_sigma.txt'))
        resf = open(os.path.join(result_prefix, n + '.f_mu_sigma.txt'), 'r')
        res = resf.read()
        # print (res)
        lines = res.split('\n')
        au_num = len(uname2uid)
        # L0=19
        self.f = np.zeros([au_num, cc])
        # self.mu = np.zeros([au_num, cc])
        self.mu = np.linspace(2008, 2008, au_num*cc).reshape((au_num, cc))
        self.sigma = np.ones([au_num, cc])
        for au_id, line in enumerate(lines[1:-1]):
            items = line.split('\t')
            au = items[0]
            edges = items[1]
            if edges is not '[]':
                edges = edges.replace('[', '').replace(']', '').split(' ')
            else:
                continue
            for edge in edges[:-1]:
                edge = edge.replace('(', '').replace(')', '')
                tpl = edge.split(',')
                comm_id = int(tpl[0])
                self.f[au_id][comm_id] = float(tpl[1])
                self.mu[au_id][comm_id] = float(tpl[2])
                self.sigma[au_id][comm_id] = float(tpl[3])
                # print (tpl)
        self.U = au_num
        self.C = cc
        print ("load result done.")
        # print (np.dot(self.f[0], self.f[1]))
        print (np.dot(norm.pdf(1994, self.mu[0], self.sigma[0]), norm.pdf(1998, self.mu[1], self.sigma[1])))

    def link_predict(self, from_user, to_user, from_time, to_time):
        # TODO: revise formula
        # print ()
        # result = np.dot(self.f[from_user], norm.pdf(from_time, self.mu[from_user], self.sigma[from_user])) * \
        #             np.dot(self.f[to_user], norm.pdf(to_time, self.mu[to_user], self.sigma[to_user]))
        result = 0
        result = np.sum(self.f[from_user] * self.f[to_user] * \
                    norm.pdf(from_time, self.mu[from_user], self.sigma[from_user]) * \
                    norm.pdf(to_time, self.mu[to_user], self.sigma[to_user]))
        # for i in range(self.f.shape[1]):
        #     result += self.f[from_user][i] * self.f[to_user][i] * \
        #             norm.pdf(from_time, self.mu[from_user][i], self.sigma[from_user][i]) * \
        #             norm.pdf(to_time, self.mu[to_user][i], self.sigma[to_user][i])
        # print (result)
        result = 1 - exp(-result)
        return result
