import pysearch

#Задание 1 и 2
pysearch.insertFile("sample.txt")
pysearch.insertFile("sample2.txt")

#Задание 3
pysearch.findDocuments("Борис Пастернак")
pysearch.findDocuments("Пастернак")
pysearch.findDocuments("Пастернак Разлука")
pysearch.findDocuments("Пастернак Разлука Гамлет")

#Задание 4 (Работает только вывод строк без контекстного окна и выделения искомых слов)
pysearch.searchByPhrase("люблю")