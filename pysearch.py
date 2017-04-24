import codecs
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.edithor_db

def insertFile(path):
	""" Reads given file and puts all found words to DB"""
	i_line = 0
	file = codecs.open(path, 'r', encoding="utf-8")
	for line in file:
		readLine(line, i_line, path)
		i_line += 1
	file.close()
	return True

def readLine(line, line_index, path, offset=0):
	"""Helper function for insertFile()
	
	Reads given line and puts all found words to DB.
	"""
	i,word = 0, False
	if (not line):
		return
	for ch in line:
		if (ch.isalpha()):
			i+=1
			word=True
		elif(not ch.isalpha() and word):
			putWord(path, line[:i], line_index, offset, offset+i)
			return readLine(line[i:], line_index, path, offset+i)
		else:
			return readLine(line[i+1:], line_index, path, offset + 1)
	putWord(path, line[:i], line_index, offset, offset+i)

def putWord(path, word, line_index, start, end):
	"""Puts word into MongoDB"""
	post = {
		"word": word,
		"document": path,
		"line": line_index,
		"start": start,
		"end": end
	}
	return db.words.insert_one(post)

def cleanLine(line, offset=0, words=[]):
	"""Helper function for findDocuments and searchByPhrase

	Clears input query from non-string characters and returns list of words.
	"""
	i,word = 0, False
	if (not len(line)):
		return
	for ch in line:	
		if (ch.isalpha()):
			i+=1
			word=True
		elif(not ch.isalpha() and word):
			words.append(line[:i])
			return cleanLine(line[i:], offset+i, words)
		else:
			return cleanLine(line[i+1:], offset + 1, words)
	words.append(line[:i])
	return words

def findDocumentsByWord(word):
	"""Helper function for findDocuments

	Returns set of documents containing given word.
	"""
	documents = set()
	for entry in db.words.find({"word": word}):	
		documents.add(entry['document'])
	return documents

def allDocuments():
	"""Helper function for findDocuments

	Returns set of all processed documents in DB.
	"""
	documents = set()
	for entry in db.words.find():
		documents.add(entry['document'])
	return documents

def findDocuments(input):
	"""Function for printing set of documents only containing all given words.
	"""
	documents = allDocuments()
	for word in cleanLine(input):
		documents = documents & findDocumentsByWord(word)
	print(documents)

def findLines(word):
	"""Helper function for preparing lines containing words in query

	Returns a list of found lines.

	"""
	documents = []
	for entry in db.words.find({"word": word}):
		lineIndex = {
			"word": word,
			"document": entry["document"],
			"line": entry["line"],
			"start": entry["start"],
			"end": entry["end"]
		}	
		documents.append(lineIndex)
	return documents

def searchFile(word):
	"""Helper function for searching lines in file.

	Returns line containing giver word.
	"""
	file = codecs.open(word['document'], 'r', encoding="utf-8")
	lines = file.readlines()
	line = lines[word['line']]
	file.close()
	return line

def searchByPhrase(phrase):
	""" Function for printing lines containing query words"""
	words = []
	for word in cleanLine(phrase):
		words = words + findLines(word)
	for  word in words:
		print(searchFile(word))


def wordLookup(word):
	"""Returns id of word if found in DB
	
	If not found, returns false
	"""
	word_id = False or db.words.find_one()._id
	return word_id

def putUpdateWord(word, path, line_index, start, end):
	"""Puts or updates word in MongoDB"""
	word_id = wordLookup(word)
	if (word_id):
		position = {
			"document": path,
			"line": line_index,
			"start": start,
			"end": end
		}
		return db.words.update({"_id": word_id}, {"$push": {"positions": position}})
	else:
		post = {
			"word": word,
			"positions": [
				{
					"document": path,
					"line": line_index,
					"start": start,
					"end": end
				}
			]
		}
		return db.words.insert_one(post)