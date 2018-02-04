import os
import io, tarfile
from pyspark import SparkContext
from pprint import pprint
import numpy as np
from numpy import genfromtxt

import tensorflow as tf
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import pearsonr, zscore
import matplotlib.pyplot as plt



sc = SparkContext("local[*]", "aa")

path = "C:/Users/esais/Desktop/big_data/project/output/"




############################  Read the pre processed data from a pickle file ######################################
tmy_data = sc.pickleFile(path + "tmy_total_data")
tmy_data_numpy = tmy_data.collect()
tmy_data_list = []
for i, x in enumerate(tmy_data_numpy):
    tmy_data_list.append([tmy_data_numpy[i][0], tmy_data_numpy[i][1].tolist()])
# pprint(kv1)
superdata = []
# Appending the electricity consumption data from 936 locations to a single superdata list
for j, y in enumerate(tmy_data_list):
    data = tmy_data_list[j][1]
    data = np.asarray(data)
    superdata.append(data[0:, 1])
superdata = np.asarray(superdata).flatten()
#Normalising the data



count = 0
featuresZ_pBias_test = []
electricity_test = []
featuresZ_pBias = []
electricity = []
sdataz = []
################################################## Building features for AR3 model ##########################################################3
while count < len(superdata):

    dataz = zscore(superdata[count:count + 52])
    sdataz.append(dataz)
    electricity_tmy = dataz[5:]
    xt1 = dataz[4:-1]
    xt2 = dataz[3:-2]
    xt3 = dataz[2:-3]
    xt4=dataz[1:-4]
    xt5 = dataz[0:-5]
    featuresZ = np.vstack((xt1, xt2, xt3,xt4,xt5)).transpose()
    tfeaturesZ_pBias = np.c_[np.ones((featuresZ.shape[0], 1)), featuresZ]
    ## 60% data is for training and 40% is for testing ##
    offset = int(tfeaturesZ_pBias.shape[0] * 0.6)

    for eft in tfeaturesZ_pBias[offset:]:
        featuresZ_pBias_test.append(eft)
    for ept in electricity_tmy[offset:]:
        electricity_test.append(ept)
    for ef in tfeaturesZ_pBias[:offset]:
        featuresZ_pBias.append(ef)
    for ep in electricity_tmy[:offset]:
        electricity.append(ep)
    count += 52


featuresZ_pBias = np.asarray(featuresZ_pBias)
featuresZ_pBias_test = np.asarray(featuresZ_pBias_test)
electricity = np.asarray(electricity)
electricity_test = np.asarray(electricity_test)
sdataz = np.asarray(sdataz).flatten()

def evaluateTestData(betas, X_test, y_test, i):
    y_pred = np.matmul(X_test, betas)[:, 0]
    ######### Uncomment the below code for plotting the graph ###################
    #plt.plot(range(32, 52), y_pred.tolist())

    #plt.savefig("C:/Users/esais/Desktop/big_data/project/outputs/tmy_ar3_60-40/"+str(kv[i][0])+"_"+str(mean_absolute_error(y_test,y_pred))+"_"+str(mean_squared_error(y_test,y_pred))+"_"+str(pearsonr(y_test,y_pred)[0])+".tiff")
    #plt.close('all')
    return [mean_absolute_error(y_test, y_pred), mean_squared_error(y_test, y_pred), pearsonr(y_test, y_pred)[0]]

def ARmodel(learning_rate=0.000001, n_epochs=2000):
    mae_list = [] # Mean Absolute Error
    mse_list = [] # Mean Squared Error
    pr_list = []  # Pearson Correlation
    X = tf.constant(featuresZ_pBias, dtype=tf.float32, name="X")
    y = tf.constant(electricity.reshape(-1, 1), dtype=tf.float32, name="y")
    beta = tf.Variable(tf.random_uniform([featuresZ_pBias.shape[1], 1], -1., 1.), name="beta")
    y_pred = tf.matmul(X, beta, name="predictions")
    error = tf.reduce_sum(tf.square(y - y_pred))
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
    training_op = optimizer.minimize(error)
    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init)
        for epoch in range(n_epochs):
            if epoch % 100 == 0:  # print debugging output
                print("Epoch", epoch, "; error =", error.eval())
            sess.run(training_op)
        # done training, get final beta:
        best_beta = beta.eval()
        pred = y_pred.eval()
        y_eval = y.eval()

    print(best_beta)
    # Evaluating The results location wise

    for i in range(936):
        ######### Uncomment the below code for plotting the graph ###################
        #plt.figure(i+1)
        #plt.plot(range(52), sdataz[52 * i:52 * (i + 1)])
        rv = evaluateTestData(best_beta, featuresZ_pBias_test[i * 19:(i + 1) * 19],electricity_test[i * 19:(i + 1) * 19], i)
        mae_list.append(rv[0])
        mse_list.append(rv[1])
        pr_list.append(rv[2])
    parameters = []
    # Taking the average of MeanSquaredError, MeanAbsoluteError , PearsonCorrelation among 936 locations
    parameters.append(sum(mse_list) / float(len(mse_list)))
    parameters.append(sum(mae_list) / float(len(mae_list)))
    parameters.append(sum(pr_list) / float(len(pr_list)))

    return parameters


parameters = ARmodel()
pprint(parameters)
