'''
# da_parse.py
# author: Li Zhong
# last modify: 2015-05-29

# this file is used to parse the xml files of dialogue acts and words.
# it can be used to generate rttm file for praatlib, for prosody computing

'''

import xml.etree.ElementTree as ET 
import numpy as np 
import os,sys
import matplotlib.pyplot as plt
import pandas as pd 



da_types = {}

dt = ET.parse("ontologies/da-types.xml")
for c in dt.getroot():
	for child in c: 
		key = child.attrib['{http://nite.sourceforge.net/}id']
		val = child.attrib['name']
		da_types[key] = val

# print da_types, '\n'


			
		
def parseExtsummxml(filename='ES2002a'):
	DAIdList = []
	extsumm = ET.parse("extractive/%s.extsumm.xml"%filename)
	for line in extsumm.getroot():
		for child in line:
			DAId = child.attrib['href']
			# there are two cases: single DA and continous DA (startDA..endDA)
			if len(DAId) < 70: # single DA case
				DAId = DAId.split('(')[1][:-1]
				DAIdList.append(DAId)
			else: # continous DA
				DAId = DAId.split('..')
				startDAId = DAId[0].split('(')[1][:-1]
				endDAId = DAId[1].split('(')[1][:-1]
				DAIdList.append(startDAId)
				DAIdList.append(endDAId)
	return DAIdList


def parseDAxml(filename='ES2002a.A'):
	# parse a single dialogue act xml
	# return a list, each element is a tuple (startWordId, endWordId, DAtype)
	# modify: add DA id, like "ES2002a.B.dialog-act.dharshi.3" to match with extsumm.xml 

	DASegList = []
	dialog = ET.parse("dialogueActs/%s.dialog-act.xml"%filename)
	for line in dialog.getroot():
		if len(line) > 1:
			key = line[1].attrib['href'].split("#")[1].split("..")
			val = line[0].attrib['href'].split("(")[1].split(")")[0] 
			DAtype = da_types[val]
			# new added: DA id
			DAId = line.attrib['{http://nite.sourceforge.net/}id']
		

			startWordId = key[0][18:-1]
			try:
				endWordId = key[1][18:-1]
			except:
				endWordId = key[0][18:-1]

			# new added: DA id
			DASegList.append((int(startWordId), int(endWordId), DAtype, DAId))
	return sorted(DASegList) 


def parseWordxml(filename='ES2002a.A'):
	# parse a single word xml
	# return a ndarray, columns: wordId(row index), startTime, endTime, text
	wordSegList = []
	checkWordId = 0
	words = ET.parse("words/%s.words.xml"%filename)
	for line in words.getroot():
		try:
			wordId = line.attrib['{http://nite.sourceforge.net/}id']
			startTime = line.attrib['starttime']
			endTime = line.attrib['endtime']
		except KeyError:
			print 'in parseWordxml', filename, line.attrib
			continue
		text = line.text
		try:
			if checkWordId!=int(wordId[15:]):
				print 'wordId wrong:', filename, line, line.attrib, checkWordId
				break
		except ValueError:
			print 'in parseWordxml', filename, wordId, checkWordId
			continue
		wordSegList.append((startTime, endTime, text))
		checkWordId+=1
	return wordSegList



def genDATimeSeg(filename='ES2002a.A'):
	# combine DA xml and word xml
	# return a list of DATimeSeg, startTime, endTime, DAtype
	# modify: add new DA id
	# (modify: return a map, key: DA id, value: (startWordId, endWordId, DAtype)

	#DATimeSeg = []
	DATimeSeg = {}
	DA = parseDAxml(filename)
	word = parseWordxml(filename)
	for da in DA:
		startTime = word[da[0]][0]
		endTime = word[da[1]][1]
		DAtype = da[2]
		DAId =  da[3]
		if float(startTime) < 0:
			print 'in genDATimeSeg:', filename, da, word[da[0]], word[da[1]]
			continue

		# modify: from list into map
		#DATimeSeg.append((startTime, endTime, DAtype, DAId))
		if DAId in DATimeSeg:
			print 'error: repeated DA id', DAId, DATimeSeg[DAId], startTime, endTime, DAtype
			break
		DATimeSeg[DAId] = (startTime, endTime, DAtype)

	return DATimeSeg

def genExtsummSeg(filename='ES2002a'):
	DATimeSeg = {}
	for char in ["A","B","C","D"]:
		#print len(DATimeSeg)
		name = filename+"."+char
		tmpDict = DATimeSeg.copy()
		tmpDict.update(genDATimeSeg(name))
		DATimeSeg = tmpDict
		#print len(DATimeSeg)
	return DATimeSeg

def genRlSeg(filename='ES2002a'):
	DAMap = genExtsummSeg(filename)
	Extsumm = set(parseExtsummxml(filename))
	rlDA = []
	allDA = []
	for key in DAMap.keys():
		value = (float(DAMap[key][0]), float(DAMap[key][1]), DAMap[key][2])
		if key in Extsumm:
			#rlDA.append((key, DAMap[key]))
			rlDA.append(value) 
		allDA.append(value)

	print 'num of all DAs:\t', len(allDA)
	print 'num of relevant DAs:\t', len(rlDA)

	rlDA = pd.DataFrame(sorted(rlDA),columns=['startTime','endTime','DAtype'])
	allDA = pd.DataFrame(sorted(allDA),columns=['startTime','endTime','DAtype'])
	rlDA.to_csv("signals/%s/audio/%s.rl.seg"%(filename,filename),index=None)
	allDA.to_csv("signals/%s/audio/%s.all.seg"%(filename,filename),index=None)


	#print allDA
	# draw the distribution
	#draw(allDA, rlDA)
	#return sorted(rlDA)

def draw(a,b):
	plt.figure()
	y,c = 0.1,'g'
	for e in a:
		startTime = e[0]
		endTime = e[1]
		plt.plot((startTime,endTime),(y,y),color=c,linewidth=4)

	y, c = 0.2, 'r'
	for e in b:
		startTime = e[0]
		endTime = e[1]
		plt.plot((startTime,endTime),(y,y),color=c,linewidth=4)

	plt.ylim(0,0.3)
	#plt.show()

def genRTTM(filename):
	# generate rttm files for prosody computing
	# rttm: file chnl tbeg tdur ortho stype name conf  
	# see http://www.itl.nist.gov/iad/mig/tests/rt/2003-fall/docs/RTTM-format-v13.pdf for more details
	DATimeSeg = []
	for char in ["A","B","C","D"]:
		name = filename+"."+char
		DATimeSeg += genDATimeSeg(name)
	#print DATimeSeg
	try:
		with open("signals/%s/audio/%s.rttm"%(filename,filename),"wb") as f:
			for i, inter in enumerate(DATimeSeg):
				startTime = inter[0]
				endTime = inter[1]
				duration = float(endTime) - float(startTime)
				if duration <= 0:
					print 'non-positive duration, skip:', i, inter
					continue
				DAtype = inter[2]
				try:
					outline = " ".join([filename,DAtype,"1",startTime,str(duration),"<NA>","<NA>","NA","<NA>","\n"])
				except TypeError:
					print filename, i, inter, duration
					continue
				f.write(outline)
	except IOError:
		print filename, "no such file in signals!"

def genDASeg():
	print "loading..."
	print "generate DA time segments for each signals\n"
	for filename in os.listdir("../Data/signals"):
		# currently only apply for ES audio files
		if filename[-1] in ['a','b','c','d'] and filename[:2]=='ES':
			print filename
			#print genDATimeSeg(filename+'.A')
			#genRTTM(filename)
			print '\n'
			genRlSeg(filename)
			
	#plt.show()



if __name__ == '__main__':
	genDASeg()
	#genRTTM('ES2002a')
	#print parseDAxml()
	#print parseExtsummxml()
	#print genDATimeSeg()
	#genExtsummSeg()
	#genRlSeg()
