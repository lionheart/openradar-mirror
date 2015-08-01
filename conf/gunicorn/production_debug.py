import os
pythonpath = os.path.abspath("..")

bind = "0.0.0.0:{}".format(os.environ['PORT'])

# http://gunicorn.org/design.html#how-many-workers
workers = 3

# Supervisor needs a non-daemonized process
daemon = False

loglevel = "debug"
proc_name = "openradarmirror-debug"
worker_class = "gevent"
debug = True

django_settings = "openradarmirror.settings"

