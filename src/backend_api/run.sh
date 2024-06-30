
#!/bin/bash
./build.sh
gunicorn --bind "0.0.0.0:5002" wsgi:app