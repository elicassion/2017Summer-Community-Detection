import numpy as np
import os
from io import StringIO


class predictor(object):

    def __init__(self):
        super(predictor, self).__init__()
        # self.data_dir = data_dir
        # result_prefix = result_prefix
        # self.load()

    def load_data(self, data_dir):
        self.max_time = 0
        self.min_time = 0x7fffffff
        self.word2wid = {}
        self.uname2uid = {}
        for line in open(os.path.join(data_dir, 'docs.txt')):
            line = line.rstrip().split('\t')
            if line[0] not in self.uname2uid:
                self.uname2uid[line[0]] = len(self.uname2uid)
            self.update_time(int(line[1]))
            if len(line) < 3:
                continue
            for word in line[2].split():
                if word not in self.word2wid:
                    self.word2wid[word] = len(self.word2wid)
        for line in open(os.path.join(data_dir, 'links.txt')):
            line = line.split()
            if line[0] not in self.uname2uid:
                self.uname2uid[line[0]] = len(self.uname2uid)
            if line[1] not in self.uname2uid:
                self.uname2uid[line[1]] = len(self.uname2uid)
            for time in line[2:]:
                self.update_time(int(time))
        self.max_time += 1
        self.min_time -= 1

    def load_result(self, result_prefix):
        self.pi = np.loadtxt(result_prefix + '.pi.txt')  # U*C
        self.theta = np.loadtxt(result_prefix + '.theta.txt')  # C*K
        self.phi = np.loadtxt(result_prefix + '.phi.txt')  # K*W
        self.U = self.pi.shape[0]
        self.C = self.pi.shape[1]
        self.K = self.theta.shape[1]
        self.W = self.phi.shape[1]
        self.eta = np.loadtxt(result_prefix + '.eta.txt')  # C*C
        ptkcstring = open(result_prefix + '.psi.txt').read().replace(',', '\t')
        self.ptkc = np.loadtxt(StringIO(ptkcstring)).reshape(self.C, self.K, -1).T  # T*K*C
        self.u2t = np.dot(self.pi, self.theta)

    def update_time(self, time):
        if time > self.max_time:
            self.max_time = time
        if time < self.min_time:
            self.min_time = time

    def norm_time(self, time):
        return (time - self.min_time) / (self.max_time - self.min_time)

    def unnorm_time(self, time):
        return time * (self.max_time - self.min_time) + self.min_time

    def link_predict(self, from_user, to_user, from_time, to_time):
        result = self.pi[from_user].reshape(-1, 1) * self.pi[to_user]
        result *= self.eta
        return result.sum()

    def doc_predict(self, doc, user):
        pw = np.ones(self.K, dtype=float)
        doc = doc.split()
        for word in doc:
            if word in self.word2wid:
                pw *= self.phi[:, self.word2wid[word]]
        pw = np.sum(pw * self.u2t[user])
        return pw, len(doc)

    def time_predict(self, doc, user):
        pw = np.ones(self.K, dtype=float)
        doc = doc.split()
        for word in doc:
            if word in self.word2wid:
                pw *= self.phi[:, self.word2wid[word]]
        pt = np.dot(np.dot(self.ptkc, self.pi[user]), pw)
        pt[~np.isfinite(pt)] = 0
        return np.argmax(pt) / len(pt)
