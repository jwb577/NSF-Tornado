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

class AdminLogin(MainHandler):
    TEMPLATE_FILE = "admin_login.jinja"
    def getContext(self, **kwargs):
        context = super(AdminLogin, self).getContext(**kwargs)
        context.update({'auth_fail':self.get_argument('auth_fail',False)})
        return context

    def get(self, **kwargs):
        if self.get_secure_cookie("auth_token")==ADMIN_KEY:
            return self.redirect('/admin')
        return super(AdminLogin, self).get(**kwargs)


class Admin(MainHandler):
    TEMPLATE_FILE = 'admin.jinja'

    def getContext(self, **kwargs):
        context = super(Admin, self).getContext(**kwargs)
        context.update({'api_key':API_KEY})
        num = get_current_number()
        if(HUMANIZE):
            date = arrow.get(num[1]).humanize()
        else:
            date = arrow.get(num[1]).to(TIMEZONE).format(DATE_FORMAT)
        context.update({'number':num[0], 'date':date})
        context.update({'users': get_all_users()})
        state = seeing_people()
        if(HUMANIZE):
            state_date = arrow.get(state[1]).humanize()
        else:
            state_date = arrow.get(state[1]).to(TIMEZONE).format(DATE_FORMAT)
        context.update({'seeing_people':state[0], 'seeing_people_date':state_date})
        return context

    def get(self, **kwargs):
        if self.get_secure_cookie("auth_token")!=ADMIN_KEY:
            return self.redirect('/admin_login')
        return super(Admin, self).get(**kwargs)

    def post(self, **kwargs):
        user_name = self.get_argument('user_name', '')
        password = self.get_argument('password', '')
        if authenticate_user(user_name, password):
            self.set_secure_cookie("auth_token", ADMIN_KEY)
            return super(Admin, self).get(**kwargs)
        else:
            time.sleep(5)
            return self.redirect('/admin_login?auth_fail=1')


#APIs
class GetCurrentNumber(tornado.web.RequestHandler):
    def get(self):
        num = get_current_number()
        if(HUMANIZE):
            date = arrow.get(num[1]).humanize()
        else:
            date = arrow.get(num[1]).to(TIMEZONE).format(DATE_FORMAT)
        response ={'number':num[0], 'date':date}
        self.write(response)


class IncrementNumber(tornado.web.RequestHandler):
    def post(self):
        post_api_key = self.get_argument('api_key', '')
        if post_api_key != API_KEY:
            self.set_status(403)
            self.write({'error':"You're not authorized"})
            return
        num = inc_current_number()
        if(HUMANIZE):
            date = arrow.get(num[1]).humanize()
        else:
            date = arrow.get(num[1]).to(TIMEZONE).format(DATE_FORMAT)
        response ={'number':num[0], 'date':date}
        self.write(response)


class SetNumber(tornado.web.RequestHandler):
    def post(self):
        post_api_key = self.get_argument('api_key', '')
        if post_api_key != API_KEY:
            self.set_status(403)
            self.write({'error':"You're not authorized"})
            return
        new_num = self.get_argument('number', 0)
        num = set_current_number(int(new_num))
        if(HUMANIZE):
            date = arrow.get(num[1]).humanize()
        else:
            date = arrow.get(num[1]).to(TIMEZONE).format(DATE_FORMAT)
        response ={'number':num[0], 'date':date}
        self.write(response)


class GetState(tornado.web.RequestHandler):
    def get(self):
        num = seeing_people()
        if(HUMANIZE):
            date = arrow.get(num[1]).humanize()
        else:
            date = arrow.get(num[1]).to(TIMEZONE).format(DATE_FORMAT)
        response ={'state':num[0], 'date':date}
        self.write(response)


class SetState(tornado.web.RequestHandler):
    def post(self):
        post_api_key = self.get_argument('api_key', '')
        if post_api_key != API_KEY:
            self.set_status(403)
            self.write({'error':"You're not authorized"})
            return
        new_state = self.get_argument('state', 0)
        try:
            new_state = int(new_state)
        except ValueError:
            new_state = 1 if new_state=='true' else 0
        num = set_seeing_people(new_state)
        if(HUMANIZE):
            date = arrow.get(num[1]).humanize()
        else:
            date = arrow.get(num[1]).to(TIMEZONE).format(DATE_FORMAT)
        response ={'state':num[0], 'date':date}
        if new_state: # If needed, send text to first in queue
            start_receiving()
        self.write(response)


class ClearSchedule(tornado.web.RequestHandler):
    def post(self):
        post_api_key = self.get_argument('api_key', '')
        if post_api_key != API_KEY:
            self.set_status(403)
            self.write({'error':"You're not authorized"})
            return
        clear_schedule()
        response ={}
        self.write(response)


class GetTable(tornado.web.RequestHandler):
    def post(self):
        post_api_key = self.get_argument('api_key', '')
        if post_api_key != API_KEY:
            self.set_status(403)
            self.write({'error':"You're not authorized"})
            return
        users= get_all_users()
        response =[]
        if users:
            for user in users:
                response.append({'name': user[0], 'phone': user[1]})
        else:
            response.append({'name': 'No users now', 'phone': ''})
        self.write({'table':response})
