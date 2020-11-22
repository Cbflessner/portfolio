from client import app, db, r_ngram, r_words

key = "long lines were"
predictions = r_ngram.zrange("long lines were", 0, 2)
print(predictions)