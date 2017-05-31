
#!/usr/bin/env python
## -*- coding: utf-8 -*-
import os
import tornado.ioloop
import tornado.options
import tornado.httpserver
import sys
from NSFlogger import NSFlogger
from NSFsettings import *
from NSFviews import *


# Assign handler to the server root  (127.0.0.1:PORT/)
application = tornado.web.Application([
    (r"/", Index)
], static_path=STATIC_PATH,cookie_secret=TORNADO_SECRET,xsrf_cookies=XSRF_COOKIES,)


REDIRECT_APP = tornado.web.Application([
    (r"/", REDIRECT)], static_path=os.path.join(root, 'static'),cookie_secret=TORNADO_SECRET)


if __name__ == "__main__":
    # Setup the server
    args = sys.argv
    args.append("--log_file_prefix=/var/log/tornado.log")
    tornado.options.parse_command_line(args)
    if not check_db() or '--setup' in sys.argv:
        print ('It appears the database is not setup, entering first time setup...')
        setup_db()
        print ('Setup complete, now starting server.')
    if (HTTPS):
        http_server = tornado.httpserver.HTTPServer(application, ssl_options={
            "certfile": CERTFILE,
            "keyfile": KEYFILE,
        })
        http_server.listen(HTTPS_PORT)
        # application.listen(HTTP_PORT)
        # REDIRECT_APP.listen(HTTP_PORT)
    else:
        application.listen(HTTP_PORT)
    can0 = NSFlogger(blocksize=1000, interface='can0')
    can1 = NSFlogger(blocksize=1000, interface='can1')
    can0.start()
    can1.start()
    tornado.ioloop.IOLoop.instance().start()

