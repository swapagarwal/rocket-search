# Rocket Search

Content Based Document Retrieval System

Given a query, it retrieves the set of documents relevant to the submitted query using TF, TFIDF and BM25 term weighting measures. Appropriate snippets from the documents are also displayed.

### Requirements

```
pip install -r requirements.txt
```
### Usage

Set the following values in `index.py`:

`schema` Indexing with or without stop-word removal, with or without term stemming

`INDEX_NAME` Name your index

`PATH_TO_DATASET` Path to dataset

Run `python index.py` to build the index.

Set index path in `server.py` and run `python server.py` to start the server.

### Endpoints

`/query/:query_string` Takes page number, page length and weighting (tf, tfidf or bm25) as parameters and returns a JSON containing various fields including query time, number of results and an array of results

`/log` Logs the query

`/precision` Calculates mean average precision

`/ndcg` Calculates normalized discounted cumulative gain
