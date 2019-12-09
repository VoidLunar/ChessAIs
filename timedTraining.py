import time
import qLearnRandom
import qLearnStockfish

def timeRun(func, o):
	startTime = time.time()
	func()
	endTime = time.time()
	timeSpent = endTime - startTime
	outFile = open(o,'w')
	outFile.write("Time spent: " + str(timeSpent))

timeRun(qLearnStockfish.train, 'QStockfishTime.txt')
timeRun(qLearnRandom.train, 'QRandomTime.txt')
