# nginx -g 'daemon on;'
# gunicorn -w 4 --threads 4 -b 0.0.0.0:9000 flask_api:application
gunicorn -w 1 --threads 4 -b unix:/tmp/gunicorn.sock main:app &
nginx -g 'daemon off;'
