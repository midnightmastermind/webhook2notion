
import os
from notion.client import NotionClient
from flask import Flask
from flask import request
from notion.block import BookmarkBlock, TextBlock, PageBlock
import markdown
from md2notion.upload import convert, uploadBlock

import urllib3

from readability.readability import Document

from pypandoc.pandoc_download import download_pandoc
import pypandoc

from rq import Queue
from worker import conn

# see the documentation how to customize the installation path
# but be aware that you then need to include it in the `PATH`
download_pandoc()

app = Flask(__name__)
q = Queue(connection=conn)

def createNotionTask(token, collectionURL, content, url):
    if (content):
        client = NotionClient(token)
        cv = client.get_collection_view(collectionURL)
        print(cv.collection.parent.views)
        row = cv.collection.add_row()
        row.title = content
        row.url = url
        if (url):
            try:
                http = urllib3.PoolManager()
                r = http.request('GET', url)
                doc = Document(r.data)
                text = doc.summary()

                output = pypandoc.convert_text(text, 'markdown_github-raw_html', format='html')
                rendered = convert(output)

                # Process the rendered array of `notion-py` block descriptors here
                # (just dicts with some properties to pass to `notion-py`)

                # Upload all the blocks
                for blockDescriptor in rendered:
                    uploadBlock(blockDescriptor, row, doc.title())
            except:
                page = row.children.add_new(BookmarkBlock)
                page.link = url
                page.title = content
        else:
            page = row.children.add_new(TextBlock,title=content)


@app.route('/create_note', methods=['GET'])
def create_note():
    note = request.args.get('note')
    url = request.args.get('url')
    token_v2 = os.environ.get("NOTES_TOKEN")
    notes_url = os.environ.get("NOTES_URL")

    q.enqueue(createNotionTask(token_v2, notes_url, note, url))
    return f'added {note} to Notion'


@app.route('/create_task', methods=['GET'])
def create_task():
    url = request.args.get('url')
    task = request.args.get('task')
    token_v2 = os.environ.get("TASKS_TOKEN")
    tasks_url = os.environ.get("TASKS_URL")
    q.enqueue(createNotionTask(token_v2, tasks_url, task, url))
    return f'added {task} to Notion'

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
