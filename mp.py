import multiprocessing

scientists = [
    { "name": 'Ada Lovelace', "born": 1815 },
    { "name": 'Emmy Noether', "born": 1882 },
    { "name": 'Marie Curie',  "born": 1867 },
    { "name": 'Tu Youyou',    "born": 1930 },
    { "name": 'Ada Yonath',   "born": 1939 },
    { "name": 'Vera Rubin',   "born": 1928 },
    { "name": 'Sally Ride',   "born": 1951 },
]

def process_item(item):
    return {
        'name': item["name"],
        'age': 2020 - item["born"]
    }

pool = multiprocessing.Pool()
result = pool.map(process_item, scientists)

print(tuple(result))
