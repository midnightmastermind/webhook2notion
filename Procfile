web: gunicorn --preload app:app --timeout=60 --keep-alive=5 --log-level=debug
worker: rq worker && python worker.py
