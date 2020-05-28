#! /usr/bin/python
from bs4 import BeautifulSoup
import re
import ast
import math
import collections

from collections import OrderedDict

q1n = {}						#Query TFIDF for Normalisation
documentVectors = {}			#Global document vectors dictionary


def fileReturn(file):
	"Method to open file from folder"
	returnB = 0
	with open(file) as data:
		returnB = ast.literal_eval(data.read())
	return returnB

vocab = fileReturn("vocab.txt")
docTFIDF = fileReturn("tfidf.txt")

def cosine(docID,query):
	sumxx, sumxy, sumyy = 0, 0, 0
											#Creates Document Vectors
	for word in vocab:
		if (word in docTFIDF[docID]):
			dtfidf = docTFIDF[docID][word]
			#print(dtfidf)	
		else:
			dtfidf = 0						#If not found, 0 for dot product
		if (word in query):
			qtfidf = q1n[word]
			#print(qtfidf)
		else:
			qtfidf = 0						#If not found, 0 for dot product
    
		x = dtfidf 							#Calculations for cosine similarity
		y = qtfidf
		sumxx += x*x
		sumyy += y*y
		sumxy += x*y
	sumxx = math.sqrt(sumxx)
	sumyy = math.sqrt(sumyy)
	if(sumxx == 0):
		return 0
	if(sumyy == 0):
		return 0
	return sumxy/(sumxx*sumyy)

def main():
	"Main method for searching"
	# Dictionary Declarations: 
	# ============================================================================== #
	postings = fileReturn("postings.txt")
	vocab = fileReturn("vocab.txt")
	idf = dict.fromkeys(postings) 				#Dictionary for idf
	tf = dict.fromkeys(postings) 				#Dictionary for tf
	collectionFrequency = dict.fromkeys(vocab) 	#Dictionary for collection frequency
	docIDdictionary = {} 						#Dictionary for docIDS
	url = fileReturn("docids.txt") 				#Creates url array from docids.txt
	# ============================================================================== #

	for i in postings:
		temp = postings[i][len(postings[i])-1]	#takes 'docFreq: 3' from postings
		temp = temp.split(':')					#splits on the : 
		idf[i] = temp[1] 						#takes the document frequency 

		tf[i] = postings[i]						#tf = everything in postings
		tf[i].pop(len(postings[i])-1) 			#removes the last element of the postings array, and assigns the rest to tf
		collectionFrequency[i] = vocab[i] 		#gets the collection frequency from vocab.txt

	for word in tf:
		tempDict = dict()										#creates temp dictionary
		for value in tf[word]:									#For each value in the tf dictionary
			docID = re.findall(r"(\d*):", str(value))[0]		#Get the docID which is before the :
			termFreq = re.findall(r":(\d*)", str(value))[0]		#Get the term frequency which is after the :
			tempDict[docID] = termFreq 							#Key for dictionary is docID, term frequency is added to tempDict
		tf[word] = tempDict										#tf[word] is then equal to what tempDict is

	for word in postings:
		docID = re.findall(r"(\d*):", str(postings[word]))
		docIDdictionary[word] = docID

	print('')
	term = input('Enter query: ')		#User Input
	term = term.lower()					#Converts all text to lowercase
	term = re.sub(r'[^\w]', ' ', term)	#Removes all punctuation and replaces with a ' '

	from UEAlite import stem_doc
	term = stem_doc(term)				#Stemming of the query

	query = []							#Array for length of query (needed for TF)
	query = term.split()				#Splits query into separate terms for array

	stopwords = ['i','a','about','an','are','as','at','be','by','com','for','from','how','in','is','it','of','or','that','the','this','to','was','what','when','where','who','will','with','www']
	for word in query:
		flag = False				
		if(word in stopwords):			#If word found, set flag to true and 
			flag = True 				#remove word from query
			query.remove(word)
		else:
			flag = False


	relevantDocs = []					#relevant docs array
	cosines = {}						#cosines dictionary
	for word in query:
		print('')
		print('===========================================')
		print('           QUERYING FOR: ', word)
		print('===========================================')
		
		if (word not in tf):
			print('Term not found')
		else:
			print('Postings: ', tf[word])							#can retrieve word from postings
			print('DocIDS: ', docIDdictionary[word]) 				#can retrieve all docIDS assoc.
			print('Document Frequency: ', idf[word]) 				#can retrieve the docFreq
			print('Collection Frequency: ', str(vocab[word])) 		#can retrieve collFreq
			print('')

			tfWord = (1 / len(query))						
			idfWord = (math.log10(len(url) / int(idf[word]))) 
			tfidfQuery = tfWord * idfWord
			q1n[word] = tfidfQuery

			#print('TF*IDF for', word, '= ', q1n[word])
			print('')

			relevantDocs = list(set(relevantDocs + docIDdictionary[word]))
	for docid in relevantDocs:
		cosines[docid] = cosine(docid,query)		#Calculates the cosine similarity

	orderedCosines = OrderedDict(sorted(cosines.items(), key = lambda t:t[1], reverse = True))
	
	#Orders Cosine Similarities
	j = 0
	for docid in orderedCosines:
		print(url[int(docid)])				#prints url
		#print(orderedCosines[docid])
		j += 1
		if(j == 10):
			break

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()

