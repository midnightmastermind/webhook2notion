from notion.client import *

token_v2 = "ab276d01115dd3f4ab499eb5ac4055057ddf28380755c8b77d83924cb2965f7928f1127c0e8bbc390e4f4b9b48535e897c428d9569538efb89ae22a615883a45746c819509bc6a285c48a4ddcc42"

client = NotionClient(token_v2=token_v2, monitor=True, start_monitoring=True)

def postBlog(record):
    return record.title

def watch_blog():

	cv = client.get_collection_view(
		"https://www.notion.so/7c0cb2186c1b454cb838adf35d5d4dc2?v=29a73ce95f57452d80c88f5f03d902ce"
	)

	def my_callback(record):
        try:
            job = q.enqueue_call(func=postBlog, args=(record), result_ttl=5000)
            return f'added {record.title} to Queue'
            print(job.get_id())


	for block_row in cv.collection.get_rows() :
		block_row.add_callback(my_callback(block_row))

watch_blog()

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
