from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.analysis import StandardAnalyzer, StemmingAnalyzer
from whoosh.qparser import QueryParser
from bs4 import BeautifulSoup
import os.path

no_stop_analyzer = StandardAnalyzer(stoplist=None)
stem_analyzer = StemmingAnalyzer()
schema = Schema(path=ID(unique=True, stored=True), title=TEXT(stored=True), content=TEXT)
#schema = Schema(path=ID(unique=True, stored=True), title=TEXT(stored=True), content=TEXT(phrase=True, analyzer=no_stop_analyzer))
#schema = Schema(path=ID(unique=True, stored=True), title=TEXT(stored=True), content=TEXT(analyzer=stem_analyzer))

INDEX_NAME = "indexdir"
PATH_TO_DATASET = "dataset"

if not os.path.exists(INDEX_NAME):
    os.mkdir(INDEX_NAME)
ix = create_in(INDEX_NAME, schema)

def add(writer, path):
    fileobj = open(path, 'r')
    content = fileobj.read()
    fileobj.close()
    soup = BeautifulSoup(content, "html.parser")
    title = soup.title.string
    body = soup.get_text()
    writer.add_document(path=path, title=unicode(title), content=body)

writer = ix.writer()
for root, _, files in os.walk(PATH_TO_DATASET):
    for file in files:
        file_path = os.path.join(root, file)
        try:
            add(writer, u"" + file_path)
        except Exception, e:
            print file_path + ": " + str(e)
writer.commit()
