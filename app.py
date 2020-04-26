
import os
from notion.client import NotionClient
from flask import Flask
from flask import request


app = Flask(__name__)


def createNotionTask(token, collectionURL, content):
    # notion
    client = NotionClient(token)
    cv = client.get_collection_view(collectionURL)
    row = cv.collection.add_row()
    row.title = content


@app.route('/create_task', methods=['GET'])
def create_task():

    task = request.args.get('task')
    token_v2 = os.environ.get("TOKEN")
    url = os.environ.get("TASKS_URL")
    createNotionTask(token_v2, url, task)
    return f'added {task} to Notion'

@app.route('/create_task', methods=['GET'])
def create_note():

    task = request.args.get('task')
    token_v2 = os.environ.get("TOKEN")
    url = os.environ.get("ARTICLES_URL")
    createNotionTask(token_v2, url, task)
    return f'added {task} to Notion'

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
