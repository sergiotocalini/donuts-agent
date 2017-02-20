#!/usr/bin/env python
import os
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from donuts_agent import app, config

def simple(env, resp):
    resp(b'200 OK', [(b'Content-Type', b'text/plain')])
    return [b"Hello WSGI World"]

donuts_agent = DispatcherMiddleware(simple, {app.config.get('APPLICATION_ROOT', '/'): app})

if __name__ == "__main__":
    run_simple(app.config.get('BIND', '0.0.0.0'), app.config.get('PORT', 5000), donuts_agent)
