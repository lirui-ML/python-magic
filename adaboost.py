# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 09:39:22 2019

@author: lirui_vendor
"""

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection  import train_test_split
from tqdm import tqdm

def create_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['label'] = iris.target
    df.columns = ['sepal length', 'sepal width', 'petal length', 'petal width', 'label']
    data = np.array(df.iloc[:100, [0,1,-1]])
    for i in range(len(data)):
        if data[i,-1] == 0:
            data[i,-1] = -1
    # print(data)
    return data[:,:2], data[:,-1]

class AdaBoostClassifier(object):
    
    def __init__(self,max_depth=None,
                 n_iteration=100,
                 learning_rate = 0.01,
                 error=1e-5):
        self.max_depth = max_depth
        self.iteration = n_iteration
        self.learning_rate = learning_rate
        self.error = error
    
    def init_args(self,X,y,init_weights):
        self.X = X
        self.y = y
        self.samples, self.features = X.shape
        # 弱分类器数目
        self.clf_sets = []
        
        # 初始化权重
        if init_weights == None:
            self.weights = np.full(self.samples,(1 / self.samples))
        
        # G(x)系数
        self.alpha = []
        
    def _G(self,features,labels,weights):
        m = len(features)
        error = 100000.0  # 无穷大
        best_v = 0.0
        # 单维feature
        features_min = min(features)
        features_max = max(features)
        n_step = (features_max - features_min +
                  self.learning_rate) // self.learning_rate
        direct, compare_array = None, None
        for i in range(1, int(n_step)):
            v = features_min + self.learning_rate * i
            if v not in features:
                # 误分类计算
                compare_array_positive = np.array(
                    [1 if features[k] > v else -1 for k in range(m)])
                weight_error_positive = sum([
                    weights[k] for k in range(m)
                    if compare_array_positive[k] != labels[k]
                ])
    
                compare_array_nagetive = np.array(
                    [-1 if features[k] > v else 1 for k in range(m)])
                weight_error_nagetive = sum([
                    weights[k] for k in range(m)
                    if compare_array_nagetive[k] != labels[k]
                ])
    
                if weight_error_positive < weight_error_nagetive:
                    weight_error = weight_error_positive
                    _compare_array = compare_array_positive
                    direct = 'positive'
                else:
                    weight_error = weight_error_nagetive
                    _compare_array = compare_array_nagetive
                    direct = 'nagetive'
                
                if weight_error < error:
                    error = weight_error
                    compare_array = _compare_array
                    best_v = v
        return best_v, direct, error, compare_array

    def G(self,x,v,direct):
        if direct == 'positive':
            return 1 if x > v else -1
        else:
            return -1 if x > v else 1
        
    def _alpha(self,error):
        # 计算分类器权重
        return 0.5 * np.log((1 - error) / error)
    
    def _Z(self,weights,alpha,clf):
        #规范化因子
        return np.sum([
                weights[i] * np.exp(-1 * self.y[i] * clf[i]) 
                for i in range(self.samples)
                ])
    
    def _compute_sample_weights(self,alpha,clf,Z):
        # 样本权重更新
        for i in range(self.samples):
            self.weights[i] = self.weights[i] * np.exp(
                    -1 * alpha * self.y[i] * clf[i]) / Z
                    
    def fit(self,X,y,initial_weight=None):
        print('start training.....')
        self.init_args(X=X,y=y,init_weights=initial_weight)
        for estimiter in tqdm(range(self.iteration)):
            best_clf_error, best_v, clf_result = 100000, None, None
            for j in range(self.features):
                features = self.X[:,j]
                v, direct, error, compare_array = self._G(
                    features, self.y, self.weights)
                
                if error < best_clf_error:
                    best_clf_error = error
                    best_v = v
                    final_direct = direct
                    clf_result = compare_array
                    axis = j
                    
                if best_clf_error == 0:
                    break
            # 计算G(X)系数alpha
            a = self._alpha(best_clf_error)
            self.alpha.append(a)
            # 记录分类器
            self.clf_sets.append((axis,best_v,final_direct))
            # 规范化因子
            Z = self._Z(self.weights,a,clf_result)
            # 权值更新
            self._compute_sample_weights(a,clf_result,Z)
    def predict(self,X):
        result = 0.0
        for i in range(len(self.clf_sets)):
            axis, clf_v, direct = self.clf_sets[i]
            f_input = X[axis]
            result += self.alpha[i] * self.G(f_input, clf_v, direct)
        return 1 if result > 0 else -1
    
    def score(self, X_test, y_test):
        right_count = 0
        for i in range(len(X_test)):
            feature = X_test[i]
            if self.predict(feature) == y_test[i]:
                right_count += 1

        return right_count / len(X_test)
    
if __name__ == "__main__":
    ## 测试通过
    X, y = create_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    clf = AdaBoostClassifier(n_iteration=100, learning_rate=0.05)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    print("score：{}".format(score))