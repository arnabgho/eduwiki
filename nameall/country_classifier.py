#!/usr/bin/env python
# Country classifier
###############################################################################
import sys, os, subprocess, time, codecs, re, shutil, glob
import utils
from nltk.util import ngrams
import nltk
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn import tree
from sklearn.externals import joblib
from sklearn import cross_validation
from sklearn.metrics import accuracy_score
from scipy.sparse import csr_matrix
import cPickle as pickle
import numpy as np
import random,math
from string import ascii_lowercase

def main(params_file):
    params = {}
    params_file = os.path.realpath(params_file)
    # Figure out the paths
    script_path = os.path.realpath(__file__)
    script_dir = os.path.dirname(script_path)
    app_dir = os.path.dirname(script_dir)
    params['app_dir'] = app_dir

    # Current timestamp
    curr_timestamp = time.strftime("%d_%b_%Y_%H_%M_%S_GMT", time.gmtime())

    # read configuration file and check
    utils.read_config(params_file, params)
    gen_class = CountryClassifier()
    #gen_class.loadData(params['process_country_gender_output_file_country'], params['process_country_gender_output_country_id'], params['country_classifier_model_file'])
    gen_class.loadModel(params['country_classifier_model_file'], params['process_country_gender_output_country_id'])
    t1 = time.time()
    print gen_class.predict('Diyi Yang')
    t2 = time.time()
    print("Predict Time: %f ms"%((t2-t1)*1000))
    print gen_class.predict('Yuntian Deng')
    print gen_class.predict('Hanyue Liang')
    print gen_class.predict('Lidan Mu')
    print gen_class.predict('Lanxiao Xu')
    print gen_class.predict('Zhiruo Zhou')
    print gen_class.predict('Charlotte Riley')
    print gen_class.predict('Qi Guo')
    print gen_class.predict('Eric Xing')
    print gen_class.predict('Yiming Yang')
    print gen_class.predict('Xiaoping Deng')
    print gen_class.predict('Yidi Zhao')
    print gen_class.predict('Yuanchi Ning')
    print gen_class.predict('Jinping Xi')
    print gen_class.predict('Liyuan Peng')
    print gen_class.predict('Wei-chiu Ma')
    print gen_class.predict('Zhiting Hu')
    print gen_class.predict('Hao Zhang')
    print gen_class.predict('Li Zhou')
    print gen_class.predict('Shayan Doroudi')
    print gen_class.predict('Daniel Guo')
    print gen_class.predict('Christoph Dann')
class CountryClassifier:
    def __init__(self):
        self.non_letters = r'[^a-zA-Z ]'
        self.feature_global = set()
        self.feature_id = {}
        self.cv = 5
        self.country_id = {}
        random.seed(910820)

    def loadModel(self, modelfile_prefix, country_id_file):
        self.clf = joblib.load(modelfile_prefix+'.pkl')
        self.feature_id = pickle.load(file(modelfile_prefix, 'r'))
        self.num_fea = len(self.feature_id)
        with open(country_id_file, 'r') as fin:
            for line in fin:
                country,id = line.strip().split('\t')
                self.country_id[int(id)] = country

    def predict(self, name):
        features = self._nameFeatures(name)
        print name
        row = []
        col = []
        data = []
        idx = 0
        for feature in features:
            if feature in self.feature_id:
                row.append(idx)
                col.append(self.feature_id[feature])
                data.append(features[feature])
        row = np.array(row)
        col = np.array(col)
        data = np.array(data)
        X = csr_matrix((data, (row, col)), shape=(1, self.num_fea))
        return self.country_id[self.clf.predict(X)[0]]


    def loadData(self, filename, country_id_file, modelfile_prefix):
        with open(country_id_file, 'r') as fin:
            for line in fin:
                country,id = line.strip().split('\t')
                self.country_id[int(id)] = country
        row = []
        col = []
        data = []
        genders = []
        feature_idx = 0
        with open(filename, 'r') as fin:
            line_idx = 0
            idx = 0
            for line in fin:
                line_idx += 1
                if line_idx % 1000 == 0:
                    print '%d lines read' %line_idx
                    #if line_idx > 10000:
                    #    break
                name, gender = line.strip().split('\t')
                features = self._nameFeatures(name, False)
        	for feature in features:
        	    row.append(idx)
                    if not feature in self.feature_id:
                        self.feature_id[feature] = feature_idx
                        feature_idx += 1
        	    col.append(self.feature_id[feature])
        	    data.append(features[feature])
        	genders.append(int(gender))
        	idx += 1
        idx = 0
        self.num_fea = feature_idx
        print '%d features' %self.num_fea
        
        self.Y = np.array(genders)
        inds = range(len(genders))
        random.shuffle(inds)
        #inds = inds[10000:]
        row = np.array(row)
        col = np.array(col)
        data = np.array(data)
        self.Y = self.Y
        print row
        print col
        print data
        self.X = csr_matrix((data, (row, col)), shape=(len(genders), self.num_fea))
        self.X = self.X[inds,:]
        self.Y = self.Y[inds]
        print self.Y

        self.clf = tree.DecisionTreeClassifier(min_samples_leaf=10)
        #self.clf = RandomForestClassifier(n_estimators=100, min_samples_leaf=10)
        #self.clf = svm.SVC()
	t1 = time.time()
        self.clf = self.clf.fit(self.X, self.Y)
	t2 = time.time()
	print("Training Time: %f ms"%((t2-t1)*1000))
        joblib.dump(self.clf, modelfile_prefix+'.pkl') 
	pickle.dump(self.feature_id, file(modelfile_prefix, 'w'))
        print 'Model saved to %s' %modelfile_prefix
        predicted = self.clf.predict(self.X)
        print 'Training Accuracy: %0.2f' %(accuracy_score(self.Y, predicted))

	t1 = time.time()
        scores = cross_validation.cross_val_score(self.clf, self.X, self.Y, cv=self.cv)
	t2 = time.time()
	print("CV Time: %f ms"%((t2-t1)*1000))
        print("CV Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


    
    def _nameFeatures(self, name, flag=False):
        features = {}
        name = re.sub(r' +', ' ', name)
        self._addNgramFeatures(name, features, '7', flag)
        self._addVowelFeatures(name, features, '8', flag)
        self._addTrailingFeatures(name, features, '9', flag)
        name=name.upper()
        self._addNgramFeatures(name, features, '1', flag)
        self._addVowelFeatures(name, features, '2', flag)
        self._addTrailingFeatures(name, features, '3', flag)

        name_pure = re.sub(self.non_letters, " ", name)
        self._addNgramFeatures(name_pure, features, '4', flag)
        self._addVowelFeatures(name_pure, features, '5', flag)
        self._addTrailingFeatures(name_pure, features, '6', flag)
        return features

    def _addNgramFeatures(self, name, features, prefix, flag):
        for n in range(1,5):
            ngrams_dict = nltk.FreqDist(ngrams([ch for ch in name], n))
            for item in ngrams_dict:
                feature_name = '%s-%d-%s' %(prefix, n, item)
                if flag:
                    self.feature_global.add(feature_name)
                features[feature_name] = ngrams_dict[item]
    def _addVowelFeatures(self, name, features, prefix, flag):
        cnt = 0
        for n in range(len(name)):
            if name[n] in 'AEIOUY':
                cnt += 1
        feature_name = prefix
        if flag:
            self.feature_global.add(feature_name)
        features[feature_name] = cnt
    def _addTrailingFeatures(self, name, features, prefix, flag):
        self._addWholeTrailingFeatures(name, features, prefix+'-1', flag)
        self._addFirstTrailingFeatures(name, features, prefix+'-2', flag)
        self._addLastTrailingFeatures(name, features, prefix+'-3', flag)
    def _addWholeTrailingFeatures(self, name, features, prefix, flag):
        for n in range(min([3, len(name)])):
            letters = name[-1-n:]
            feature_name = '%s-%d-%s' %(prefix, n, letters)
            if flag:
                self.feature_global.add(feature_name)
            features[feature_name] = 1
        for n in range(min([3, len(name)])):
            letter = name[-1-n]
            feature_name = '%s-%d-%s' %(prefix, n+3, letter)
            if flag:
                self.feature_global.add(feature_name)
            features[feature_name] = 1
        if name[-1] in 'AEIOUY':
            feature_name = '%s-6-vowel' %prefix
            if flag:
                self.feature_global.add(feature_name)
            features[feature_name] = 1
    def _addFirstTrailingFeatures(self, name, features, prefix, flag):
        names = name.split()
        if len(names) >= 2:
            first_name = names[0]
            self._addNgramFeatures(first_name, features, prefix, flag)
            self._addVowelFeatures(first_name, features, prefix, flag)
            self._addTrailingFeatures(first_name, features, prefix, flag)
            self._addWholeTrailingFeatures(first_name, features, prefix, flag)
    def _addLastTrailingFeatures(self, name, features, prefix, flag):
        names = name.split()
        if len(names) >= 2:
            first_name = names[1]
            self._addNgramFeatures(first_name, features, prefix, flag)
            self._addVowelFeatures(first_name, features, prefix, flag)
            self._addTrailingFeatures(first_name, features, prefix, flag)
            self._addWholeTrailingFeatures(first_name, features, prefix, flag)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print >> sys.stderr, 'Usage: python %s <params-file>' %sys.argv[0]
        sys.exit(1)
    params_file = sys.argv[1]
    assert os.path.isfile(params_file), 'params-file %s is not a valid file!' %params_file
    main(params_file)
