jongos
======

NoSQLite, simple JSON flat file based database engine. Insert, Update, Delete, Find, Group and Count any items with mongo queries taste. Featured with lock support, for concurrent / multithread usage.


Introduction
Init Module
>import jongos

>db = jongos.jongos()

Load JSON file
> db.load("file_name.json")

Show current loaded db stats
> db.stats()

Refresh current loaded JSON file
> db.refresh()

Save current in-memory db into current loaded JSON file
> db.save()

Insert new record
> db.insert(json_item)

Delete record
> db.remove(query)

Update record with partial information
> db.update(query, {'$set': json_item})

Update record with all new information
> db.update(query, json_item)

Find a rows
> db.find(query)

Count a rows that match query
> db.find(query).count()

Group a rows with a field key:
> db.find(query).group(field_key)

Sort a rows with a field key:
> db.find(query).sort(field_key,reverse=True)

Get all results from the queries:
> db.find(query).all()

Save the results as JSON file
> db.find(query).capture("save_to_file_name.json")

Query
JSON structure examples:

[ {"id":1, "name": "One", "title": "Mr", "email": "one@mailinator.com", "score": {"math": 80, "science": 80} }, {"id":2, "name": "Two", "title": "Mrs", "email": "two@mailinator.com", "score": {"math": 60, "science": 70}}, {"id":3, "name": "Three", "title": "Ms", "email": "three@mailinator.com", "score": {"math": 75, "science": 90}}, {"id":4, "name": "Four", "title": "Mrs", "email": "five@mailinator.com", "score": {"math": 60, "science": 30}}, {"id":5, "name": "Five", "title": "Mrs", "email": "fivefour@mailinator.com", "score": {"math": 70, "science": 60}} ]

Match Exact, Except, Like and LikeAnd?
Filter all item with Mrs title : query = {"title": "Mrs"}

Filter all item with title except Ms : query = {"title": {"$ne":"Ms"}}

Filter all item like 'five' in email : query = {"email": {"$like":"five"}}

Filter all item like 'five' or 'four' in email : query = {"email": {"$likes":["five","four]}}

Filter all item like 'five' and 'four' in email : query = {"email": {"$likesAnd":["five","four]}}

Greater and Lower than
Filter all math score greater than 60 : query = {"score.math": {"$gt":60}}

Filter all math score lower than 60 : query = {"score.math": {"$lt":60}}

Filter all math score greater than equal 60 : query = {"score.math": {"$gte":60}}

Filter all math score lower than equal 60 : query = {"score.math": {"$lte":60}}

Include and No Include
Filter all math score in 60 and 70: query = {"score.math": {"$in":[60,70]}}

Filter all math score not in 60 and 70 : query = {"score.math": {"$nin":[60,70]}}
