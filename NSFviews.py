import tornado.web
from tornado import httpclient

from jinja2 import Environment, FileSystemLoader
import tornado.web
import os, os.path
import wtforms
from wtforms_tornado import Form
import urllib
import random
import string
import re
import sys, inspect
import requests
import arrow
import time
import csv

from NSFsettings import *
from NSFutilities import *

# Handler for main page
class MainHandler(tornado.web.RequestHandler):

    def getContext(self, **kwargs):
        context = {}
        context.update(kwargs)
        context.update(JINJA2_SETTINGS)
        pages = []
        # import ipdb;ipdb.set_trace()
        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj):
                try:
                    new_page = {'name': obj.PAGE_NAME, 'desc': obj.PAGE_DESCRIPTION, 'url': obj.PAGE_URL, 'pos': obj.PAGE_POS}
                    if self.PAGE_NAME == obj.PAGE_NAME:
                        new_page.update({'navclass':'active'})
                    else:
                        new_page.update({'navclass':''})
                    pages.append(new_page)
                except AttributeError:
                    pass
        context.update({'pages': pages})
        return context

    def get(self, **kwargs):
        context = {}
        context.update(self.getContext(**kwargs))
        context.update({'log_data' : get_log_segment(self.get_arguments('offset')[0], self.get_arguments('delay')[0])})
        templateLoader = FileSystemLoader( searchpath=BASEDIR + "templates/" )
        templateEnv = Environment( loader=templateLoader )
        template = templateEnv.get_template(self.TEMPLATE_FILE)
        html_output = template.render(title="Forensic Link Adapter", **context)
        # Returns rendered template string to the browser request
        self.write(str(context['log_data']))

#---- PAGES ----

class REDIRECT(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.protocol == "http":
            self.redirect("https://%s" % self.request.full_url()[len("http://"):], permanent=True)

    def get(self):
        self.write("Hello, world")

class Index(MainHandler):
    TEMPLATE_FILE = "index.jinja"
    PAGE_NAME = "Home"
    PAGE_DESCRIPTION = "This is the main page for the CCDC website."
    PAGE_URL = '/'
    PAGE_POS = 0

    def getContext(self, **kwargs):
        context = super(Index, self).getContext(**kwargs)
        return context

    def get(self, **kwargs):
        context = self.getContext()
        return super(Index, self).get(**kwargs)

    def post(self, **kwargs):
        user_name = self.get_argument('user_name', '')
        phone_number = self.get_argument('phone_number', '')
        number = get_new_number(unique_id, phone_number, user_name)

