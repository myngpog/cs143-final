# Flask-On-Docker Tutorial Assignment (CSCI143)
## By: My Nguyen

[![](https://github.com/myngpog/cs143-final/actions/workflows/tests.yml/badge.svg)](https://github.com/myngpog/cs143-final/actions/workflows/tests.yml)

[Tutorial Link](https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/)

### Overview
This repo is me following a tutorial on "how to containerize a Flask application with Postgres". I also used Gunicorn and Nginx to "handle static and media files". I learned how to set up a development environment for a Flask web application, including configuring Docker containers for Flask, PostgreSQL, Gunicorn, and Nginx. The finished product includes being able to file upload onto a local port and viewing that image.The goal of this assignment is to build a working web service from scratch, based off of instagram's tech stack.

Demo\
![alt text](/big-data.gif)

### Build Instructions
To build:
```
# Build
docker-compose build
docker-compose up

# If you want to build specific file, where -d runs it in the background:
docker-compose -f <file-name> up -d --build

# Take down, where -v takes down volumes as well
docker-compose down -v
```

