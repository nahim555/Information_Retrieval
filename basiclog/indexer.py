#! /usr/bin/python

from bs4 import BeautifulSoup
import re
import math

# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = {}
docfreq = {} # a document frequency dictionary
termFrequencies = {} #global dictionary for termFrequencies


def main():
	infile = 'page1.txt' # a static test file containing a single page's contents
	textin = open(infile, 'rU')
	page_contents = textin.read()
	make_index(infile, page_contents)
	textin.close()
	
	
def write_index():	# writes index contents to disk, called from the crawler
	# declare refs to global variables
	global docids
	global postings
	global vocab
	global tfidf
	
	for term in postings:  #attaches document frequency to postings
		postings[term].append('docFreq: ' + str(docfreq[term]))

	idf = dict.fromkeys(postings)	#idf dictionary is from the postings file

	for i in postings:
		temp = postings[i][len(postings[i])-1]
		temp = temp.split(':')		#splits on the colon '0:1'
		idf[i] = temp[1] 			#gets the document Frequency

	#Calculates TF*IDF	
	document = {}
	for docid in termFrequencies:
		termTFIDF = {}
		#Gets the word count for each word
		wordCount = 0
		for word in termFrequencies[docid]:
			wordCount += termFrequencies[docid][word]
			# print(word)		#prints word
			# print(wordCount)	#prints the total word count for that document
		for word in termFrequencies[docid]:
			#theTF = (float(termFrequencies[docid][word]) / float(wordCount))
			theTF = (1 + math.log(float(termFrequencies[docid][word]), 10))
			theIDF = (math.log10(len(docids) / int(idf[word]) ))
			termTFIDF[word] = theTF * theIDF
			#print(word, tfidf) #Prints the word and its TF*IDF
		document[docid] = termTFIDF

	# writes to index files: docids, vocab, postings
	outlist1 = open('docids.txt', 'w')
	outlist2 = open('vocab.txt', 'w')
	outlist3 = open('postings.txt', 'w')
	outlist4 = open('tfidf.txt', 'w')
	
	print (docids, file=outlist1)
	print (vocab, file=outlist2)
	print (postings, file=outlist3)
	print (document, file=outlist4)

	outlist1.close()
	outlist2.close()
	outlist3.close()
	outlist4.close()

	return
	
	
def make_index(url, page_contents):	# the main indexing function
	# declare refs to global variables
	global docids
	global postings
	global vocab
	
	#print ('===============================================')
	#print ('make_index0: url = ', url)
	#print ('make_index0: page_contents = ', page_contents)
	#print ('===============================================')
	
	##### extract the words from the page contents #####
	
	## the BeautifulSoup route
	#b = BeautifulSoup(page_contents, 'html.parser')
	#b = re.sub('<.*>', '', b.decode('utf-8'))
	#page_text = b.get_text()
	#print ('===============================================')
	#print ('make_index1: page_text = ', page_text)
	#print ('===============================================')

	if (isinstance(page_contents, bytes)): # convert bytes to string if necessary
		c = page_contents.decode('utf-8')
	else:
		c = page_contents
	if isinstance (c, bytes):
		print ('!!!ERROR!!! page not converted to string')

	## the raw regex route
	# can be refined to be more selective
	c = re.sub('\\\\n|\\\\r|\\\\t', ' ', c)							# get rid of newlines, tabs
	c = re.sub('\\\\\'', '\'', c)									# replace \' with '
	c = re.sub('<script.*?script>', ' ', c, flags=re.DOTALL) 		# get rid of scripts
	c = re.sub('<!\[CDATA\[.*?\]\]', ' ', c, flags=re.DOTALL)		# get rid of CDATA ?redundant
	c = re.sub('<link.*?link>|<link.*?>', ' ', c, flags=re.DOTALL) 	# get rid of links
	c = re.sub('<style.*?style>', ' ', c, flags=re.DOTALL) 			# get rid of links
	c = re.sub('<.*?>', ' ', c, flags=re.DOTALL)					# get rid of HTML tags
	c = re.sub('{.*?}', ' ', c)										# get rid of stray JS
	c = re.sub('\\\\x..', ' ', c)									# get rid of hex values
	c = re.sub('<--|-->', ' ', c, flags=re.DOTALL)					# get rid of comments
	c = re.sub('<|>', ' ', c)										# get rid of stray angle brackets
	c = re.sub('&.*?;|#.*?;', ' ', c)								# get rid of HTML entities
	c = re.sub(r'[^\w]', ' ', c)									# removes all punctuation and replaces with a ' '
	
	page_text = re.sub('\s+', ' ', c)								# replace multiple spaces with a single space
	page_text = page_text.lower()									# converts all text to lower case

	print ('===============================================')
	print ('make_index2: url = ', url)
	#print ('make_index2: page_text = ', page_text)
	print ('===============================================')
	
	##### add information to the index files #####
	
	### add the url to the doclist (DJS Nov 2015) ###
	# need to worry about duplicates that only differ in the protocol and www.
	# as these are not picked up by the crawler
	if (re.search('https:..', url)):	# match and remove https://
		domain_url = re.sub('https://', '', url)
	elif (re.search('http:..', url)):	# match and remove http://
		domain_url = re.sub('http://', '', url)
	else:
		print ("make_index no match for protocol url=", url)
		
	if (re.search('www.', domain_url)):	# match and remove www.
		domain_url = re.sub('www.', '', domain_url)
	
	#print ("\n make_index5 domain_url=", domain_url, '\n')

	### append the url to the list of documents
	if (domain_url in docids): # return if we've seen this before
		return
	else:
		docids.append(domain_url)				# add url to docids table
		docid = str(docids.index(domain_url))	# get a string version of the docid
	
	##### stemming and other processing goes here #####
	# from Stemmer import stem_doc
	# page_text = stem_doc(page_text)

	# page_text is the initial content, transformed to words
	words = page_text
	freq = {} #a local dictionary for term frequencies
	
	for word in words.split():
		if (word in freq):
			freq[word] += 1	#if word is already in vocab.txt + 1 to term frequency
		else:
			freq[word] = 1	
	
	termFrequencies[docid] = freq  #puts freq dictionary within global termFrequencies dictionary

	# add the vocab counts and postings
	for word in words.split():
		if (word in vocab):
			vocab[word] += 1	#if word is already in vocab.txt + 1 to term frequency
		else:
			vocab[word] = 1		#if word is not in vocab.txt, add word and + 1 to term frequency
		if (not word in postings):
			docfreq[word] = 1
			postings[word] = [docid + ':' + str(freq[word])]	#adds frequency 1 to posting
		elif (docid not in re.findall(r"(\d*):", str(postings[word]))):
			docfreq[word] += 1	#extract docid, check whether the docid matches the current docid
								#if == true, then extract freq, freq++
			postings[word].append(docid + ':' + str(freq[word]))

	
		#print ('make_index3: docid=', docid, ' word=', word, ' count=', vocab[word], ' postings=', postings[word])
	return
	
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()


	