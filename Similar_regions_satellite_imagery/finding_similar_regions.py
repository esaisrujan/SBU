import os
import io,zipfile
from PIL import Image
from pyspark import SparkContext,SparkConf
from pprint import pprint
import numpy as np
from tifffile import TiffFile
import hashlib
from scipy import linalg
import operator
#path="C:/Users/esais/Desktop/big_data/assignment_2/"
#path= 'hdfs:/data/small_sample/'
path= 'hdfs:/data/large_sample/'
conf = SparkConf().setAppName("A2")
sc=SparkContext(conf=conf)
#sc.addPyFile("scipy-1.0.0.zip")

def getOrthoTif(zfBytes):
 #given a zipfile as bytes (i.e. from reading from a binary file),
# return a np array of rgbx values for each pixel
     bytesio = io.BytesIO(zfBytes)
     zfiles = zipfile.ZipFile(bytesio, "r")
     #find tif:
     for fn in zfiles.namelist():
            if fn[-4:] == '.tif':#found it, turn into array:
                    #pprint("found")
                    tif = TiffFile(io.BytesIO(zfiles.open(fn).read()))
                    #pprint(tif.asarray().shape)

                    return tif.asarray()
     return None
def map1(kv):
    l = []
    #pprint(kv[1].shape)
    div = int(kv[1].shape[0] / 500)
    #pprint(div)
    temp = np.split(kv[1], div)
    for x in temp:
        l.append(np.split(x, div, axis=1))
    result = []
    [result.extend(el) for el in l]
    li=[]
    for i,x in enumerate(result):
        #pprint(x.shape)
        li.append([kv[0]+"-"+str(i),x])
    #return sorted(list(d.items()),key=operator.itemgetter(0))

    return li
def map2(kv):
    l=[]
    #pprint(kv[0])
    #with open('out_before_intensity.txt', 'w') as f:

    #    print(kv,file=f)
    #pprint(kv[1].shape)
    for y in kv[1].tolist():
        r=[]
        for x in y:
            rgb_mean=(x[0]+x[1]+x[2])/3
            r.append(int(rgb_mean*(x[3]/100)))
        #pprint(len(r))
        l.append(r)
    #pprint(np.array(l).shape)
    return (kv[0],np.array(l))
def map3(kv,factor):
    l = []
    result=[]
    value= kv[1]
    div = int(value.shape[0]/factor)
    temp = np.split(value, div)
    for x in temp:
        l.append(np.split(x, div, axis=1))
    [result.extend(el) for el in l]
    for i, x in enumerate(result):
        result[i] = result[i].flatten()
    result=np.array(result)
    pprint(result.shape)
    l= np.mean(result,axis=1)
    l=l.reshape(div,div)
    return [kv[0],l]
def map4(kv):
    #pprint(kv)
    #value=kv[1].tolist()
    #pprint(kv[1].shape)
    value=np.diff(kv[1],axis=1)
    #pprint(value.shape)
    #for j,v in enumerate(value):
     #   for i in range(len(v)-1):
      #      temp = value[j][i+1]-value[j][i]
      #      if temp<-1:
      #          value[j][i] = -1
      #      elif temp > 1:
      #          value[j][i] = 1
      #      else:
      #           value[j][i] = 0
      #   value[j] = value[j][:-1]
    #pprint([kv[0],value])
    value = value.flatten().tolist()

    for i in range(len(value)):
        if value[i] < -1:
            value[i] = -1
        elif value[i] > 1:
            value[i] = 1
        else:
            value[i] = 0
    return [kv[0], np.array(value)]

def map5(kv):
    #pprint(kv)
    value = np.diff(kv[1],axis=0)
    # for j,v in enumerate(value):
    #   for i in range(len(v)-1):
    #      temp = value[j][i+1]-value[j][i]
    #      if temp<-1:
    #          value[j][i] = -1
    #      elif temp > 1:
    #          value[j][i] = 1
    #      else:
    #           value[j][i] = 0
    #   value[j] = value[j][:-1]
    # pprint([kv[0],value])
    value = value.flatten().tolist()

    for i in range(len(value)):
        if value[i] < -1:
            value[i] = -1
        elif value[i] > 1:
            value[i] = 1
        else:
            value[i] = 0
    return [kv[0], np.array(value)]
def map6(kv):
    l=[]
    #with open('out_before_band.txt', 'w') as f:
    #    print(kv,file = f)
    bands = np.split(np.array(kv[1]),4) #large sample
    bands = list(zip(range(4),bands))   #large sample
   # bands = np.split(np.array(kv[1]),8) #small sample
   # bands = list(zip(range(8),bands))   #samll sample
    for x in bands:
        l.append([x[0],(kv[0],x[1])])
    return l
def map7(kv):
    l=[]
    for x in kv[1]:
     #   hashed = sum(list(hashlib.md5(x[1]).digest()))% 40 #small sample
        hashed = sum(list(hashlib.md5(x[1]).digest()))% 1000 #large sample
        l.append([str(kv[0])+","+str(hashed),x[0]])
    return l
def create_chunks(l, n):
    avg = len(l) / float(n)
    chunks = []
    last = 0.0

    while last < len(l):
        chunks.append(l[int(last):int(last + avg)])
        last += avg

    return chunks
def signmap(kv):
    #pprint("reached here")
    chunks = create_chunks(kv[1],128)
    #pprint(chunks)
    signature = []
    for x in chunks:
        hash_chunk = hashlib.md5(np.array(x)).digest()
        s=""
        for i in hash_chunk:
            s = s+ bin(int(i)).lstrip('0b')
        signature.append(s[-1])
    return [kv[0],signature]
def svd_cal(kv):
    img_diffs=[]
    names = []
    result=[]
    kv=kv[1]
  #  a=kv
  #  a=list(a)
   # with open('out_before_svd.txt', 'w') as f:

    #    print(kv[0], file=f)
    for x in kv:
        names.append(x[0])
        img_diffs.append(x[1])
    mu, std = np.mean(img_diffs, axis=0), np.std(img_diffs, axis=0)
    img_diffs_zs = (img_diffs - mu) / std
    img_diffs_zs= np.nan_to_num(img_diffs_zs)
    U, s, Vh = linalg.svd(img_diffs_zs, full_matrices=1)
    low_dim_p = 10
    img_diffs_zs_lowdim = U[:, 0:low_dim_p]
    for i,x in enumerate(img_diffs_zs_lowdim):
        result.append([names[i],x])
    return result
def distance(kv,factor):
    result=[]
    resultv=[]
    if factor == 10:
        ky = [kv[0],b_svd.value[kv[0]]]
    elif factor == 5:
        ky = [kv[0],b_svd_5.value[kv[0]]]
    val=[]
    for i,v in enumerate(kv[1]):
        if factor == 10:
            val.append([kv[1][i], b_svd.value[kv[1][i]]])
        elif factor == 5:
            val.append([kv[1][i], b_svd_5.value[kv[1][i]]])
    for i,v in enumerate(val):
        e = np.linalg.norm(val[i][1]-ky[1])
        #try:
        resultv.append([val[i][0],e])
        #except KeyError:
        #d[ky[0]] = [[val[i][0],e]]
    return [ky[0],resultv]
def sort(v):
    v=sorted(v, key=lambda x: x[1])
    return v
def fmap(kv):
    result=[]
    l=[]
    c=0
    i=0
    for x in kv:
        c=c+1
        if c<=25:
            l.append(x)
        else:
            i=i+1
            result.append([i,l])
            l=[]
            c=0
            c=c+1
            l.append(x)
    for x in l:
        result[-1][1].append(x)
    return result
def fmap_5(kv):
    result=[]
    l=[]
    c=0
    i=0
    for x in kv:
        c=c+1
        if c<=20:
            l.append(x)
        else:
            i=i+1
            result.append([i,l])
            l=[]
            c=0
            c=c+1
            l.append(x)
    for x in l:
        result[-1][1].append(x)
    return result



zip_rdd = sc.binaryFiles(path+"*")
img_count = int(zip_rdd.count())
zip_rdd = zip_rdd.map(lambda x : (x[0].split("/")[-1],x[1]) )
tiff_rdd=zip_rdd.mapValues(getOrthoTif)
divided_rdd=tiff_rdd.flatMap(map1)

filtered_rdd=divided_rdd.filter(lambda x : x if x[0] in ["3677454_2025195.zip-0","3677454_2025195.zip-1","3677454_2025195.zip-18","3677454_2025195.zip-19"] else None).map(lambda x: [x[0],x[1][0][0].tolist()])
with open('output_final.txt', 'w') as f:
    print("output of 1 ",file=f)
    print(filtered_rdd.collect(),file = f)

intensity_rdd = divided_rdd.map(map2)

resolution_factoring_rdd = intensity_rdd.map(lambda kv : map3(kv,10))
row_diff_rdd = resolution_factoring_rdd.map(map4)
col_diff_rdd = resolution_factoring_rdd.map(map5)
feature_vector_rdd = row_diff_rdd.union(col_diff_rdd).reduceByKey(lambda x,y :np.concatenate([x,y]))
filtered_feature_vector_rdd= feature_vector_rdd.filter(lambda x : x if x[0] in ['3677454_2025195.zip-1', '3677454_2025195.zip-18'] else None)
with open('output_final.txt', 'a') as f:
    print("output of 2",file=f)
    print(filtered_feature_vector_rdd.collect(),file = f)
signature_rdd1 = feature_vector_rdd.map(signmap)
band_rdd = signature_rdd1.flatMap(map6).groupByKey().map(lambda x : (x[0], list(x[1])))
hashed_bucketes_rdd =band_rdd.flatMap(map7).groupByKey().map(lambda x : (x[0], list(x[1])))
hashed_bucketes_rdd0=hashed_bucketes_rdd.filter(lambda x : x if "3677454_2025195.zip-0" in x[1] else None).map(lambda x : ("3677454_2025195.zip-0",x[1])).reduceByKey(lambda x,y : x+y).map(lambda x : (x[0],list(set(x[1]))))
hashed_bucketes_rdd1 = hashed_bucketes_rdd.filter(lambda x : x if "3677454_2025195.zip-1" in x[1] else None).map(lambda x : ("3677454_2025195.zip-1",x[1])).reduceByKey(lambda x,y : x+y).map(lambda x : (x[0],list(set(x[1]))))
hashed_bucketes_rdd18 = hashed_bucketes_rdd.filter(lambda x : x if "3677454_2025195.zip-18" in x[1] else None).map(lambda x : ("3677454_2025195.zip-18",x[1])).reduceByKey(lambda x,y : x+y).map(lambda x : (x[0],list(set(x[1]))))
hashed_bucketes_rdd19 = hashed_bucketes_rdd.filter(lambda x : x if "3677454_2025195.zip-19" in x[1] else None).map(lambda x : ("3677454_2025195.zip-19",x[1])).reduceByKey(lambda x,y : x+y).map(lambda x : (x[0],list(set(x[1]))))
#hashed_bucketes_rdd_4_images= hashed_bucketes_rdd0.union(hashed_bucketes_rdd1).union(hashed_bucketes_rdd18).union(hashed_bucketes_rdd19)

hashed_bucketes_rdd_1_18_images = hashed_bucketes_rdd1.union(hashed_bucketes_rdd18)
with open('output_final.txt', 'a') as f:
    print("output of 3b",file=f)
    print(hashed_bucketes_rdd_1_18_images.collect(),file = f)
svd_rdd = feature_vector_rdd.coalesce(1).mapPartitions(fmap).flatMap(svd_cal)

b_svd = sc.broadcast(dict(svd_rdd.collect()))
final_rdd=hashed_bucketes_rdd_1_18_images.map(lambda kv : distance(kv,10))

final_sorted_rdd = final_rdd.mapValues(sort)
with open('output_final.txt', 'a') as f:
    print("output of 3c",file=f)
    print(final_sorted_rdd.collect(),file = f)

############################# expected runtime up to here 20min ################################
####################################### extra credit ###########################################
resolution_factoring_rdd_5 = intensity_rdd.map(lambda kv : map3(kv,5))
row_diff_rdd_5 = resolution_factoring_rdd_5.map(map4)
col_diff_rdd_5 = resolution_factoring_rdd_5.map(map5)
feature_vector_rdd_5 = row_diff_rdd_5.union(col_diff_rdd_5).reduceByKey(lambda x,y : np.concatenate([x,y]))
filtered_feature_vector_rdd_5= feature_vector_rdd_5.filter(lambda x : x if x[0] in ['3677454_2025195.zip-1', '3677454_2025195.zip-18'] else None)
#pprint(filtered_feature_vector_rdd.take(1))
with open('output_final.txt', 'a') as f:
   print("factor 5 : solution for 2f",file=f)
   print(filtered_feature_vector_rdd_5.collect(),file = f)
signature_rdd1_5 = feature_vector_rdd_5.map(signmap)
band_rdd_5 = signature_rdd1_5.flatMap(map6).groupByKey().map(lambda x : (x[0], list(x[1])))
hashed_bucketes_rdd_5 =band_rdd_5.flatMap(map7).groupByKey().map(lambda x : (x[0], list(x[1])))
hashed_bucketes_rdd0_5=hashed_bucketes_rdd_5.filter(lambda x : x if "3677454_2025195.zip-0" in x[1] else None).map(lambda x : ("3677454_2025195.zip-0",x[1])).reduceByKey(lambda x,y : x+y).map(lambda x : (x[0],list(set(x[1]))))
hashed_bucketes_rdd1_5 = hashed_bucketes_rdd_5.filter(lambda x : x if "3677454_2025195.zip-1" in x[1] else None).map(lambda x : ("3677454_2025195.zip-1",x[1])).reduceByKey(lambda x,y : x+y).map(lambda x : (x[0],list(set(x[1]))))
hashed_bucketes_rdd18_5 = hashed_bucketes_rdd_5.filter(lambda x : x if "3677454_2025195.zip-18" in x[1] else None).map(lambda x : ("3677454_2025195.zip-18",x[1])).reduceByKey(lambda x,y : x+y).map(lambda x : (x[0],list(set(x[1]))))
hashed_bucketes_rdd19_5 = hashed_bucketes_rdd_5.filter(lambda x : x if "3677454_2025195.zip-19" in x[1] else None).map(lambda x : ("3677454_2025195.zip-19",x[1])).reduceByKey(lambda x,y : x+y).map(lambda x : (x[0],list(set(x[1]))))
#hashed_bucketes_rdd_4_images_5= hashed_bucketes_rdd0_5.union(hashed_bucketes_rdd1_5).union(hashed_bucketes_rdd18_5).union(hashed_bucketes_rdd19_5)

hashed_bucketes_rdd_1_18_images_5 = hashed_bucketes_rdd1_5.union(hashed_bucketes_rdd18_5)
with open('output_final.txt', 'a') as f:
    print("factor : 5: 3b",file=f)
    print(hashed_bucketes_rdd_1_18_images_5.collect(),file = f)
svd_rdd_5 = feature_vector_rdd_5.coalesce(1).mapPartitions(fmap_5).flatMap(svd_cal)

b_svd_5 = sc.broadcast(dict(svd_rdd_5.collect()))
final_rdd_5=hashed_bucketes_rdd_1_18_images_5.map(lambda kv : distance(kv,5))
#
final_sorted_rdd_5 = final_rdd_5.mapValues(sort)
with open('output_final.txt', 'a') as f:
    print("factor : 5 : 3c",file=f)
    print(final_sorted_rdd_5.collect(),file = f)

