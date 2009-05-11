import datetime

import web
from pymongo.connection import Connection
from pymongo import DESCENDING

urls = ("/image/(.*)", "Image",
        "/", "Main",
        "/page/(\d+)", "Main")
app = web.application(urls, globals())
render = web.template.render("templates/")
db = Connection().sms
page_size = 5

class Main:
    def GET(self, page=None):
        if page is None:
            page = 0
        page = int(page)

        previous = None
        if page > 0:
            previous = page - 1

        next = None
        if db.messages.count() > (page + 1) * page_size:
            next = page + 1

        return render.index(db.messages.find().sort("date", DESCENDING).limit(page_size).skip(page * page_size),
                            previous, next)

    def POST(self):
        post_data = web.input()
        if post_data.nickname and post_data.text:
            db.messages.insert({"nickname": post_data.nickname,
                                "text": post_data.text,
                                "date": datetime.datetime.utcnow()})
        raise web.seeother("/")

class Image:
    def GET(self, id):
        pass

if __name__ == "__main__":
    app.run()
