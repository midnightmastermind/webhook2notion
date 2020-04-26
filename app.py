
import os
from notion.client import NotionClient
from flask import Flask
from flask import request
from notion.block import BookmarkBlock, TextBlock, PageBlock
import markdown
from bs4 import BeautifulSoup
import urllib3

app = Flask(__name__)


def createNotionTask(token, collectionURL, content, url):
    if (content):
        client = NotionClient(token)
        cv = client.get_collection_view(collectionURL)
        print(cv.collection.parent.views)
        row = cv.collection.add_row()
        row.title = content
        row.url = url
        if (url):
            html = markdown.markdown(url)
            md = "".join(BeautifulSoup(html, features="html.parser").findAll(text=True))
            with open(md, "r", encoding="utf-8") as mdFile:
                newPage = page.children.add_new(PageBlock, title="TestMarkdown Upload")
                upload(mdFile, newPage)

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
    createNotionTask(token_v2, notes_url, note, url)
    return f'added {note} to Notion'


@app.route('/create_task', methods=['GET'])
def create_task():
    url = request.args.get('url')
    task = request.args.get('task')
    token_v2 = os.environ.get("TASKS_TOKEN")
    tasks_url = os.environ.get("TASKS_URL")
    createNotionTask(token_v2, tasks_url, task, url)
    return f'added {task} to Notion'

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
