web: gunicorn -w 2 -b 0.0.0.0:$PORT app:app
worker: sh -c "thumbor -p $THUMBOR_PORT"