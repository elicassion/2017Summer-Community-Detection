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
        for line in open(os.path.join(data_dir, 'network_snap.txt')):
            line = line.split()
            if line[0] not in self.uname2uid:
                self.uname2uid[line[0]] = len(self.uname2uid)
            if line[1] not in self.uname2uid:
                self.uname2uid[line[1]] = len(self.uname2uid)

    def load_result(self, result_prefix, uname2uid):
        self.f = np.loadtxt(result_prefix + '.F.txt')  # U*C
        self.U = self.f.shape[0]
        self.C = self.f.shape[1]

    def link_predict(self, from_user, to_user):
        result = np.dot(self.f[from_user], self.f[to_user])
        result = 1 - exp(-result)
        return result
