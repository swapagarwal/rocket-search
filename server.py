from bottle import route, run, request
import json, time, os, math
from whoosh import scoring
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from bs4 import BeautifulSoup

@route('/')
def usage():
    return ''

@route('/about')
def about():
    return 'Rocket Search'

@route('/query/:query_string', method='POST')
@route('/query/:query_string')
def query(query_string):
    page_number = request.query.page_number or request.forms.get('page_number') or '1'
    page_length = request.query.page_length or request.forms.get('page_length') or '10'
    weighting = request.query.weighting or request.forms.get('weighting') or 'bm25'
    return_object = {
        'query_string': query_string,
        'page_number': page_number,
        'page_length': page_length
    }

    ix = open_dir(os.getcwd() + "/indexdir")
    if weighting == 'tf':       weighting = scoring.Frequency();  return_object['weighting'] = 'tf'
    elif weighting == 'tfidf':  weighting = scoring.TF_IDF();     return_object['weighting'] = 'tfidf'
    else:                       weighting = scoring.BM25F();      return_object['weighting'] = 'bm25'
    with ix.searcher(weighting=weighting) as searcher:
        query = QueryParser('content', ix.schema).parse(query_string)
        start = time.time()
        results = searcher.search_page(query, int(page_number), pagelen=int(page_length))
        #results.fragmenter = highlight.WholeFragmenter()
        end = time.time()
        return_object['query_time'] = end - start
        return_object['number_of_results'] = len(results)
        return_object['results'] = []
        for hit in results:
            with open(hit['path']) as fileobj:
                content = fileobj.read()
            soup = BeautifulSoup(content, 'html.parser')
            body = soup.get_text()
            snippet = hit.highlights('content', text=body)
            return_object['results'] += [{
                'title': hit['title'],
                'path': hit['path'],
                'snippet': snippet
            }]
    with open('log-query-'+return_object['weighting'],'a+') as fileobj:
        fileobj.write(','.join([str(return_object['query_time']), str(return_object['query_string'])]))
        fileobj.write('\n')
    print json.dumps(return_object, indent=4)
    return json.dumps(return_object)

@route('/log', method='POST')
@route('/log')
def log():
    time = request.query.time or request.forms.get('time') or 'a'
    ip = request.query.ip or request.forms.get('ip') or 'b'
    query = request.query.query or request.forms.get('query') or 'c'
    clicked = request.query.clicked or request.forms.get('clicked') or 'd'
    position = request.query.position or request.forms.get('position') or 'e'
    weighting = request.query.weighting or request.forms.get('weighting') or 'f'

    with open('log','a+') as fileobj:
        fileobj.write(','.join([time, ip, query, clicked, position, weighting]))
        fileobj.write('\n')

@route('/precision', method='POST')
@route('/precision')
def precision():
    relevance = request.query.relevance or request.forms.get('relevance') or 'a'
    relevance = map(int, relevance.split(','))
    weighting = request.query.weighting or request.forms.get('weighting')
    if weighting != 'tf' and weighting != 'tfidf': weighting = 'bm25'

    current_sum = 0.0
    current_number = 0.0
    for i in xrange(len(relevance)):
        if relevance[i]:
            current_number += 1
            current_sum += current_number / (i + 1)
    average_precision = current_sum / current_number

    with open('precision-' + weighting,'a+') as fileobj:
        fileobj.write(str(average_precision))
        fileobj.write('\n')
    with open('precision-' + weighting) as fileobj:
        values = map(float, fileobj)

    mean_average_precision = sum(values) / len(values)
    return_object = {
        'ap': average_precision,
        'map': mean_average_precision,
        'weighting': weighting
    }

    with open('log-precision','a+') as fileobj:
        fileobj.write(json.dumps(return_object, indent=4))
        fileobj.write('\n')

    print json.dumps(return_object, indent=4)
    return json.dumps(return_object)

@route('/ndcg', method='POST')
@route('/ndcg')
def ndcg():
    relevance = request.query.relevance or request.forms.get('relevance') or 'a'
    relevance = map(int, relevance.split(','))
    weighting = request.query.weighting or request.forms.get('weighting')
    if weighting != 'tf' and weighting != 'tfidf': weighting = 'bm25'

    current_sum = 0.0
    current_number = 0.0
    for i in xrange(len(relevance)):
        if i == 0:
            current_sum += relevance[i]
        else:
            current_sum += relevance[i] / (math.log(i + 1) / math.log(2))
    discounted_cumulative_gain = current_sum

    relevance.sort(reverse=True)
    current_sum = 0.0
    current_number = 0.0
    for i in xrange(len(relevance)):
        if i == 0:
            current_sum += relevance[i]
        else:
            current_sum += relevance[i] / (math.log(i + 1) / math.log(2))
    normalized_discounted_cumulative_gain = discounted_cumulative_gain / current_sum

    return_object = {
        'dcg': discounted_cumulative_gain,
        'ndcg': normalized_discounted_cumulative_gain,
        'weighting': weighting
    }

    with open('log-ndcg','a+') as fileobj:
        fileobj.write(json.dumps(return_object, indent=4))
        fileobj.write('\n')

    print json.dumps(return_object, indent=4)
    return json.dumps(return_object)

run(host='0.0.0.0', port=5555, debug=True)
