'''
# da_classification.py
# author: Li Zhong
# last modify: 2015-06-15

# this file is used to do dialogue act classification
# It's a 5-class classification problem: inform(+elicit), suggest(+elicit), assessment(+elicit), offer, other
# resample to handle imbanlanced problem
# 4-fold to split into train and test dataset 
'''


import pandas as pd 
import numpy as np 
from sklearn.preprocessing import scale
from sklearn.svm import SVC, LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import matplotlib.pyplot as plt



otherDA = set(['stl','fra','bck','be.pos','be.neg','oth','und','el.und'])


# data splitting: train & test
# 4-fold cross-validation
# random sampling

def KfoldSelect(df, k=4):
	numTotalRow = df.shape[0]
	numTestRow = numTotalRow/k

	rowTest = np.random.choice(df.index.values,numTestRow)
	dfTest = df.ix[rowTest]
	dfTrain = df.drop(rowTest)

	print 'train, test:', dfTrain.shape, dfTest.shape, df.shape
	return dfTrain, dfTest

def preparation():

	data = pd.read_csv('DAdata.csv')
	DAList = {}
	chaDA(data)
	# directly sampling
	# dataTrain, dataTest = KfoldSelect(data)

	# wrong code to get 90% percent
	# for da in data['DA'].unique():
	# 	if da not in otherDA:
	# 		if da[:3]=='el.':
	# 			newda = da[3:]
	# 			d = pd.DataFrame(data[data['DA']==da])
	# 			d['DA'] = pd.Series([newda]*d.shape[0],index=d.index)
	# 		else:
	# 			newda = da 
	# 			d = data[data['DA']==da]
	# 		if newda not in DAList:
	# 			DAList[newda] = pd.DataFrame()
	# 		DAList[newda] = DAList[newda].append(d,ignore_index=True)
	# 	else:
	# 		if 'other' not in DAList:
	# 			DAList['other'] = pd.DataFrame()
	# 			d = pd.DataFrame(data[data['DA']==da])
	# 			d['DA'] = pd.Series(['other']*d.shape[0],index=d.index)
	# 		DAList['other'] = DAList['other'].append(d,ignore_index=True)

	#print DAList
	#print DAList['other']

	# sampling from each class
	dataTrain = pd.DataFrame()
	dataTest = pd.DataFrame()

	for key in data['DA'].unique():
		DAdata = data[data['DA']==key]
		print key
		train, test = KfoldSelect(DAdata)
		dataTrain = dataTrain.append(train)
		dataTest = dataTest.append(test)
		print '\n'

	print dataTrain.shape
	print dataTest.shape

	dataTrain.to_csv('DATrain.csv',index=False)
	dataTest.to_csv('DATest.csv',index=False)


def genXY(df):
	y = df['DA'].values
	del df['DA']
	x = df.values
	return x, y

def chaDA(df):
	oldDA = df['DA'].values
	newDA = []
	#oldDA = [1 if e == 'other' else 0 for e in oldDA]
	for e in oldDA:
		if e in otherDA:
			ne = 'other'
		elif e[:3] == 'el.':
		 	ne = e[3:]
		else:
			ne = e
		newDA.append(ne)
	df['DA'] = pd.Series(newDA, index=df.index)
	

def quickClassification():
	# training
	dataTrain = pd.read_csv('DATrain.csv')
	dataTest = pd.read_csv('DATest.csv')

	dataTrain = chaDA(dataTrain)
	dataTest = chaDA(dataTest)
	clf = GaussianNB()
	#clf = SVC(class_weight='auto')
	#clf = RandomForestClassifier(n_estimators=50, n_jobs=-1)
	#clf = GradientBoostingClassifier()
	x,y = genXY(dataTrain)
	#print x, '\n'
	#print y
	clf.fit(x,y)

	# testing
	x, y = genXY(dataTest)
	yy = clf.predict(x)
	H = genFusionMat(y,yy)
	print H




def classification():
	# training
	dataTrain = pd.read_csv('DATrain.csv')
	dataTest = pd.read_csv('DATest.csv')

	#clf = GaussianNB()
	#clf = LinearSVC(C=1,class_weight='auto',dual=False)
	#clf = RandomForestClassifier(n_estimators=50, n_jobs=-1)
	#clf = GradientBoostingClassifier()
	clf = LogisticRegression(class_weight='auto')
	x,y = genXY(dataTrain)
	#print x, '\n'
	#print y
	x = scale(x)
	clf.fit(x,y)

	# testing
	x, y = genXY(dataTest)
	x = scale(x)
	yy = clf.predict(x)

	#print dataTrain.shape
	#print dataTest.shape
	
	H = genFusionMat(y,yy)
	print H
	fig = plt.figure()
	plt.imshow(H)
	plt.show()

def genFusionMat(y,yy):
	print set(y)
	print set(yy)
	rowIndex = {}
	colIndex = {}
	for i, e in enumerate(set(y)):
		rowIndex[e] = i
	for j, e in enumerate(set(yy)):
		colIndex[e] = j
	mat = np.zeros((i+1,j+1))
	for e, ee in zip(y,yy):
		#print e, ee
		mat[rowIndex[e],colIndex[ee]] += 1
	row_sums = mat.sum(axis=1)
	new_mat = mat / row_sums[:, np.newaxis]
	return new_mat



if __name__ == '__main__':
	#preparation()
	#quickClassification()
	classification()
