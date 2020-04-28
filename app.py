
import os
from notion.client import NotionClient
from flask import Flask
from flask import request
from notion.block import BookmarkBlock, TextBlock, PageBlock
import markdown
from md2notion.upload import convert, uploadBlock
import urllib3
import urllib.parse
from lxml import etree
import prettierfier
from imgurpython import ImgurClient
import shutil
import pathlib
from pathlib import Path
from markdownify import markdownify as md

from readability.readability import Document
from io import StringIO, BytesIO
from pypandoc.pandoc_download import download_pandoc
import pypandoc
import urlexpander

from rq import Queue
from rq.job import Job
from worker import conn

# see the documentation how to customize the installation path
# but be aware that you then need to include it in the `PATH`
download_pandoc()

app = Flask(__name__)
q = Queue(connection=conn)
client_id = '3e53eed3d26e0da'
client_secret = 'd607afe07fef247d39078a678163f26eede5bc98'


def createNotionTask(token, collectionURL, content, url):
    def convertImagePath(imagePath, mdFilePath):
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.scheme + '://' + parsed_url.netloc
        print("wtf4")
        print(parse_url)
        print(domain)
        print(imagePath)
        relative_url = os.path.abspath(str(pathlib.Path().absolute()) + '/images/' + imagePath)
        new_url = urllib.parse.urljoin(domain, imagePath)
        r = http.request('GET', new_url)
        img = r.data

        os.makedirs(os.path.dirname(relative_url), exist_ok=True)
        with open(relative_url, 'wb') as f:
            f.write(img)

        return Path(os.path.abspath(str(pathlib.Path().absolute()) + imagePath))

    if (content):
        client = NotionClient(token)
        cv = client.get_collection_view(collectionURL)
        print(cv.collection.parent.views)
        row = cv.collection.add_row()

        if('task:' in content):
            content = content.replace('task:', '')

        if('Task:' in content):
            content = content.replace('Task:', '')

        row.title = content

        if (url and "http://ifttt.com/missing_link" not in url):
            expanded_url = urlexpander.expand(url)
            if('imgur' in expanded_url):
                if 'gallery/' in expanded_url:
                    gallery = expanded_url.split('gallery/')[1]

                    client = ImgurClient(client_id, client_secret)
                    items = client.get_album_images(gallery)

                    imgur_object = ""
                    for item in items:
                        img = "<img src='" + item.link + "' /><br>"
                        imgur_object += img

                    text = prettierfier.prettify_html(imgur_object)
                    doc = Document(text)
                    text = doc.summary()

                    output = pypandoc.convert_text(text, 'gfm-raw_html', format='html')
                    print(output)
                    if (output != ""):
                        page = row.children.add_new(BookmarkBlock)
                        page.link = url
                        page.title = content
                    else:
                        rendered = convert(output)
                        for blockDescriptor in rendered:
                            print(blockDescriptor)
                            print("wtf7")
                            uploadBlock(blockDescriptor, row, content, imagePathFunc=convertImagePath)
            else:
                try:
                    row.url = url

                    http = urllib3.PoolManager()
                    r = http.request('GET', url)

                    text = prettierfier.prettify_html(str(r.data))
                    doc = Document(text)
                    text = doc.summary()

                    output = pypandoc.convert_text(text, 'gfm-raw_html', format='html')
                    output = output.replace('\\\\n', '')
                    output = output.replace("\\\\'", "\'")
                    print(output)
                    if (output == ""):
                        print("wtf1")
                        raise ValueError('No website data')

                    rendered = convert(output)

                    # Upload all the blocks
                    for blockDescriptor in rendered:
                        uploadBlock(blockDescriptor, row, doc.title(),imagePathFunc=convertImagePath)
                except:
                    page = row.children.add_new(BookmarkBlock)
                    page.link = url
                    page.title = content
        else:
            row.children.add_new(TextBlock, title=content)

        # shutil.rmtree(Path(str(pathlib.Path().absolute()) + '/images/'), ignore_error=True)
        return content

@app.route('/create_note', methods=['GET'])
def create_note():
    note = request.args.get('note')
    url = request.args.get('url')
    token_v2 = os.environ.get("NOTES_TOKEN")
    notes_url = os.environ.get("NOTES_URL")

    try:
        job = q.enqueue_call(func=createNotionTask, args=(token_v2, notes_url, note, url), result_ttl=5000)
        return f'added {note} to Queue'
        print(job.get_id())
    except:
        return f'added {note} to Queue'

@app.route('/create_task', methods=['GET'])
def create_task():
    url = request.args.get('url')
    task = request.args.get('task')
    token_v2 = os.environ.get("TASKS_TOKEN")
    tasks_url = os.environ.get("TASKS_URL")

    try:
        job = q.enqueue_call(func=createNotionTask, args=(token_v2, tasks_url, task, url), result_ttl=5000)
        print(job.get_id())
        return f'added {note} to Notion'
    except:
        return f'added {task} to Queue'


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(
            result.result_no_stop_words.items(),
            key=operator.itemgetter(1),
            reverse=True
        )[:10]
        return jsonify(results)
    else:
        return "Nay!", 202

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
