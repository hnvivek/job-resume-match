#!/bin/sh

# Default port to 5000 if $PORT is not set
PORT=${PORT:-5000}

# Start the Gunicorn server
gunicorn -b 0.0.0.0:$PORT app:app
