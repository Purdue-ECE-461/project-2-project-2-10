import subprocess
import sys
from .score_npm import *
from .connectgithub import *
from .test_suite import *
from .readEnvironment import *

# logFile_ptr = open(LOG_FILE, "w")

#function to install dependencies
def installPackages():
	#use subprocess to invoke pip in commandline, create file of requirements given project location, install dependencies
	#subprocess.run(["pip", "freeze", ">", "requirements.txt"], shell=True)
	#subprocess.run(["pip", "install", "-r", "requirements.txt"], shell=True)
	
	#Count dependencies and print count
	req = open("requirements.txt")
	num_lines = sum(1 for line in req)
	print("\n" + str(num_lines) + " dependencies installed...")
	#close file s
	req.close()
	return

#function to get url list
def getInputs(inputfile):
	#Get urls from file and make list
	with open(inputfile) as urlFile:
		urlList = urlFile.read().splitlines()
	
	return urlList

#call git or npm function based on list
def gitOrNpm(urlList):
	githubString = "github.com"
	npmString = "npmjs.com"
	scoresList = []
	removeIndex = []
	count = 0

	#calls correct function for connection and creates list with returned scores list (2d list)
	for url in urlList:
		if githubString in url:
			urlScore = scoreGithub(url)
			urlScore = [round(i, 2) for i in urlScore]
			scoresList.append(urlScore)

		elif npmString in url:
			npmScore =  (npm_score(connect_npm(url)).ramp_score + npm_score(connect_npm(url)).cor_score + npm_score(connect_npm(url)).bus_score + npm_score(connect_npm(url)).resp_score + npm_score(connect_npm(url)).lic_score) / 15
			urlScore = [npmScore , npm_score(connect_npm(url)).ramp_score, npm_score(connect_npm(url)).cor_score, npm_score(connect_npm(url)).bus_score, npm_score(connect_npm(url)).resp_score, npm_score(connect_npm(url)).lic_score]
			urlScore = [round(i, 2) for i in urlScore] #Rounding scores to two decimal places
			scoresList.append(urlScore)
		else:
			print(url + " is not a valid github or npm url")
			removeIndex.append(count)

		count += 1
	#remove urls that didn't connect and move on after shifting down
	for index in removeIndex:
		urlList.pop(index)
	
	#create url : scores list dictionary
	#urlAndScoresDict = {}
	zip_it = zip(urlList, scoresList)
	urlAndScoresDict = dict(zip_it)
	return urlAndScoresDict

#function to print the urls with their scores
def printUrlWithScore(urlDict):
	print("\nURL NET_SCORE RAMP_UP_SCORE CORRECTNESS_SCORE BUS_FACTOR_SCORE RESPONSIVE_MAINTAINER_SCORE LICENSE_SCORE FRACTION_PINNED\n")

	for key, value in urlDict.items():
		print(key + " ", end="")
		print(" ".join(map(str,value)))
	return

def main(inputfile):
	installPackages()

	urlList = getInputs(inputfile)
	urlDict = gitOrNpm(urlList)
	printUrlWithScore(urlDict)
	
	return

if __name__ == "__main__":
	inputfile = str(sys.argv[1])
	#main(inputfile)

	if inputfile == "test":
		try:
			Tests()
		except Exception as e:
			raise ValueError("Error! Please install dependencies before running tests!\n Coverage: 0%")
		exit(0)
	elif ".txt" in inputfile:
		try:
			main(inputfile)
		except Exception as e:
			raise ValueError("Error! Please install dependencies before running on URLs!")
		exit(0)
