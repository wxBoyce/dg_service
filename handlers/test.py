#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import mimetypes

import pymongo
import bson.binary
import bson.objectid
from cStringIO import StringIO
from PIL import Image

from basic import BasicHandler

db = pymongo.MongoClient('localhost', 27017).test


class TestHandler(BasicHandler):
    def get(self):
        return self.write('''
            <!doctype html>
            <html>
                <body>
                    <form action='/' method='post' enctype='multipart/form-data'>
                        <input type='file' name='keyword-file'>
                        <input type='submit' value='Upload'>
                    </form>
                </body>
            </html>
            ''')

    def post(self):
        print "IN"
        if 'keyword-file' in self.request.files and len(self.request.files['keyword-file']) > 0:
            res = self.request.files['keyword-file'][0]

            if 'content_type' not in res or res['content_type'].find('/') < 1 or len(res['content_type']) > 128:
                return self.write("上传图片类型错误!!")

            if 'filename' not in res or res['filename'] == '':
                    return self.write("上传图片名称错误!!")

            ets = mimetypes.guess_all_extensions(res['content_type'])
            ext = os.path.splitext(res['filename'])[1].lower()
            if ets and ext not in ets:
                ext = ets[0]

            if ext not in ['.jpg']:
                return self.write("上传的图片格式不支持!!")

            print self.save_file(res['body'])

    def save_file(self, f):
        content = StringIO(f)
        try:
            mime = Image.open(content).format.lower()
        except IOError:
            return
        c = dict(content=bson.binary.Binary(content.getvalue()), mime=mime)
        db.files.save(c)
        return c['_id']
