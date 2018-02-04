import os
import io,tarfile
from pyspark import SparkContext
from pprint import pprint
import numpy as np
from numpy import genfromtxt
import tensorflow as tf

def get_np_csv(kv):
 #given a tar file of csv files containing hourly electricity consumption of a year,return a np array of electricity consumption on weekly basis

     bytes = kv[1]
     d =dict()
     bytesio = io.BytesIO(bytes)
     tfiles = tarfile.open(fileobj=bytesio,mode="r")

     for fn in tfiles.getnames():

            if fn[-4:] == '.csv':#found csv, turn into array:

                    obj=tfiles.extractfile(fn)

                    my_data = genfromtxt(obj, delimiter=',',skip_header=True)
                    my_data = my_data[:8736, :3]
                    # Converting 8736 hours into 52 weeks
                    my_data = np.split(my_data, 52)
                    for i, x in enumerate(my_data):
                         my_data[i] = np.sum(my_data[i], axis=0)
                    my_data = np.array(my_data)
                    #Extracting the name of the tmy3 location from the name of the csv file
                    fn = "".join(fn.split("/")[1].split(".")[:-2])
                    d[fn]=my_data

     return list(d.items())


sc=SparkContext("local[*]","aa")
input_path="C:/Users/esais/Desktop/big_data/project/input/"
output_path="C:/Users/esais/Desktop/big_data/project/output/"

tar_rdd = sc.binaryFiles(input_path+"*") # path contains the tar files of the data, If all tar files doesn't fit in the data, run multiple tar file in batches and perform reduce by key on them
np_rdd=tar_rdd.flatMap(get_np_csv)
#TMY3 location - weekly data

TMY3_rdd = np_rdd.reduceByKey(lambda x,y : np.add(x,y))
TMY3_rdd.saveAsPickleFile(output_path+"tmy_total_data")
