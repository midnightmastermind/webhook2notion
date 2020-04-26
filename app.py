
import os
from notion.client import NotionClient
from flask import Flask
from flask import request
from notion.block import BookmarkBlock, TextBlock, PageBlock
import markdown
from md2notion.upload import upload

from bs4 import BeautifulSoup
import urllib3
from mdutils.mdutils import MdUtils

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
            http = urllib3.PoolManager()
            r = http.request('GET', url)
            html = markdown.markdown(r.data)
            soup = BeautifulSoup(html)

            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()    # rip it out

            # get text
            text = soup.get_text()

            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            md = "".join(BeautifulSoup(text, features="html.parser").findAll(text=True))
            mdFile = MdUtils(file_name='Example_Markdown',title='Markdown File Example')

            mdFile.write(md)
            mdFile.create_md_file()
            print(mdFile)
            newPage = row.children.add_new(PageBlock, title="TestMarkdown Upload")
            upload("", newPage)

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
