#-*- coding: utf-8 -*-

import sys
import json
import csv
from sets import Set

def printResult(start, end, suggest, search, company, industry):
	print 
	print 'Results : ' + start + " ~ " + end
	print 'number of suggest request : ' + str(suggest)
	print 'number of search : ' + str(search)
	print 'number of junp to company : ' + str(company)
	print 'number of junp to industry : ' + str(industry)

def parse(line):
	logData = json.loads(line)
	time = logData['timestamp']
	data = logData['actionData']['com_uzabase_speeda_web_component_field_IndustrySearchTextPanel']['global_suggest']
	return (formatTime(time), data['action_type'], int(data['count']))

def formatTime(time):
	# 10秒ごと
	#return time[0:18].replace('T',' ')

	# 1分ごと
	#return time[0:16].replace('T',' ')

	# 10分ごと
	#return time[0:15].replace('T',' ')

	# 1時間ごと
	return "\"" + time[0:13] + ":00\""

def load():
	path = sys.argv[1]
	print u"start parsing...  " + path
	f = open(path)
	lines = f.readlines()
	f.close()

	record = []
	for l in lines:
		record.append(parse(l))
	return record

def getTimeRange(records):
	if len(records) == 0:
		return ('-','-')

	return (records[0][0], records[len(records) - 1][0])

def writeRecord(results):
	writer = csv.writer(open('results.csv', 'wb'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	#writer.writerow(['time', 'action_type', 'suggest_request'])
	writer.writerow(['time', 'suggest_request', 'search', 'company', 'industry'])
	for r in results:
		writer.writerow(r)


def summary(records):
	count_search = 0
	count_company = 0
	count_industry = 0
	count_suggest = 0

	for (time, actionType, suggest) in records:
		count_suggest += suggest
	
		if actionType == 'search':
			count_search += 1
		elif actionType == 'company':
			count_company += 1
		elif actionType == 'industry':
			count_industry += 1

	(start_time, end_time) = getTimeRange(records)
	printResult(start_time, end_time, count_suggest, count_search, count_company, count_industry)

def timeKeys(records):
	timeset = Set([])
	#2016-08-24T08:53:47Z
	for r in records:
		timeset.add(r[0])

	timelist = list(timeset)
	timelist.sort()
	return timelist

def writeRecordForPlot(records):
	writer = csv.writer(open('results2.csv', 'wb'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	writer.writerow(['time', 'action_type', 'suggest_request'])
	for r in records:
		writer.writerow(r)

def draw(): 
	import numpy as np
	import seaborn as sns
	import pandas as pd

	logdataset = pd.read_csv('results2.csv')

	drawPointPlot(logdataset)

def drawPointPlot(logdataset):
	import seaborn as sns

	sns.pointplot(x="time", y="suggest_request", hue="action_type", data=logdataset);
	sns.plt.show()	

def grouping(records):
	results = {}

	for (time, actionType, suggest) in records:
		results[time] = (time, 0, 0, 0, 0)
		
	for (time, actionType, suggest) in records:
		search = 0
		company = 0
		indutsry = 0
		if actionType == 'search':
			search = 1
		elif actionType == 'company':
			company = 1
		elif actionType == 'industry':
			indutsry = 1


		value = results[time]
		if value is None:
			value = (time, 0, 0, 0, 0)
		
		results[time] = (time, value[1] + suggest, value[2] + search, value[3] + company, value[4] + indutsry)

			
	resultList = []
	for time in timeKeys(records):
		resultList.append(results[time])
	return resultList;


if __name__ == "__main__":

	records = load()
	writeRecordForPlot(records)

	#results = grouping(records)
	#writeRecord(results)

	#timeKeys(records)

	#summary(records)

	draw()

