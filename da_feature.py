'''
# da_feature.py
# author: Li Zhong
# last modify: 2015-06-15

# this file is used to generate DA feauture matrix, x is the prosody feature matrix, y is the DA tag .
# use simple SVM as classifier

# as noted:
# "in ES2002a to ES2016d (4 * 15 = 60 meetings). 99% of these relevant DAs fall under the following 7 classes:
# Inform, Suggest, Assessment, Offer, Elicit-Inform, Elicit-Offer-Or-Suggestion, Elicit-Assessment
# We can group the rest of the DAs under a single class and focus on building a 8-class DA classifier. 
# If needed, we can further combine the three Elicit classes into a single one, and simplify into a six class problem."





'''


import pandas as pd 
import numpy as np 
import os
import matplotlib.pyplot as plt
import re
import wave
import scipy.io.wavfile as siw
from sklearn.svm import SVC
import cPickle



path = "C:\Users\IBM_ADMIN\Desktop\data\\nxt\Data\signals\ES2002c\\audio\\"


def getDATime(name):
	DAlist = []
	#for name,c in zip(["a", "b", "d"], ['r','b','g']):
	with open(path+"DA."+name+".txt","rb") as f:
		for line in f.readlines():
			s = line.split(" ")
			DAtype, starttime, endtime = s[0], float(s[1]), float(s[2])
			# if endtime > 300:
			# 	break
			DAlist.append((starttime, endtime, DAtype))

	return DAlist

def splitWav():
	#rate, data = siw.read(path+"t1.wav")
	rate, data = siw.read(path+"ES2002c.Mix-Headset.wav")
	#print rate, type(data), len(data)
	for c in ["a","b","c","d"]:
		splitTimes = getDATime(c)
		for i, inter in enumerate(splitTimes):
			starttime = int(inter[0]*rate)
			endtime = int(inter[1]*rate)
			slicedata = data[starttime:endtime+1]
			name = path+"classificationDA_%s\\"%c+inter[2]+str(i)+".wav"
			siw.write(name,rate,slicedata)

def genRTTM():
	for name in ["a","b","c","d"]:
		splitTimes = getDATime(name)
		with open(path+name+".rttm","wb") as f:
			for i, inter in enumerate(splitTimes):
				starttime = inter[0]
				endtime = inter[1]
				duration = endtime - starttime
				DAtype = inter[2]
				outline = " ".join(["ES2002c",DAtype,"1",str(starttime),str(duration),"<NA>","<NA>",name,"<NA>","\n"])
				#print outline
				f.write(outline)

def featureEngDA(name = "ES2002a"):
	#print currPath
	print name
	try:
		x=pd.read_csv(name+".rttm.txt")
		rttm = pd.read_csv(name+'.rttm',sep=' ',header=None)
	except IOError:
		print '%s not exist!' %name
		return pd.DataFrame()
	del x['Unnamed: 25']
	print x.shape, rttm.shape
	DAtype = rttm.iloc[:,1]
	print "DAtype :", set(DAtype)
	x['DA'] = pd.Series(DAtype)
	xx = x.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
	print 'remove inf and na:', xx.shape
	return xx

def collectData():
	data = pd.DataFrame()
	for filename in os.listdir("../Data/signals"):
		if filename[-1] in ['a','b','c','d'] and filename[:2]=='ES':
			print filename
			currPath = "../Data/signals/%s/audio/"%filename
			newData = featureEngDA(currPath+filename)
			data = data.append(newData, ignore_index=True)
			print 'data shape:', data.shape, '\n'
			
	#print data
	print 'final shape', data.shape
	return data


if __name__ == '__main__':
	#splitWav()
	#genRTTM()
	#featureEngDA()
	#train, test = featureEngDA()
	data = collectData()
	data.to_csv("DAdata.csv",index=False)
