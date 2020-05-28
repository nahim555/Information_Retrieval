To run the crawler on all the UEA computing pages:
	python PCcrawler.py uea.ac.uk/computing https://www.uea.ac.uk/computing/ 

Strongly recommended for development:
To run the crawler on the UEA computing pages, just finding the first 4:
	python PCcrawler.py uea.ac.uk/computing https://www.uea.ac.uk/computing/  4

If you are working on the indexer you can run:
	python indexer.py
which takes page1.txt as its input. 
This is good for initial development, but will need testing with input direct from the crawler as well.
