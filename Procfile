web: gunicorn --preload app:app --timeout=140 --keep-alive=5 --log-level=debug
worker: python3.6 worker.py
worker: python3.6 watch.py
