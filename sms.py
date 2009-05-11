import datetime

import web
from pymongo.connection import Connection

urls = ("/image/(.*)", "Image",
        "/", "Main",
        "/page/(.*)", "Main")
app = web.application(urls, globals())
render = web.template.render("templates/")
db = Connection().sms

class Main:
    def GET(self, page=None):
        return render.index(db.messages.find())

    def POST(self):
        post_data = web.input()
        db.messages.insert({"nick": post_data.nickname,
                            "text": post_data.text,
                            "date": datetime.datetime.utcnow()})
        raise web.seeother("/")

class Image:
    def GET(self, id):
        pass

if __name__ == "__main__":
    app.run()
