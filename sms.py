import datetime
import string
import random
import cStringIO as StringIO

import web
from PIL import Image
from pymongo.connection import Connection
from pymongo import DESCENDING
import gridfs

# Workaround an incompatible between web.py templates and the datetime module in Python 2.5
def strftime(date, format):
    return date.strftime(format)

urls = ("/image/(\w+)/(.*)", "File",
        "/image/(.*)", "File",
        "/", "Main",
        "/page/(\d+)", "Main")
app = web.application(urls, globals())
render = web.template.render("templates/", globals={"strftime": strftime})
db = Connection().sms
fs = gridfs.GridFS(db)
page_size = 10


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

    def generate_filename(self, name):
        """Generate a unique filename to use for GridFS, using a given name.

        Just appends some random characters before the file extension and
        checks for uniqueness.
        """
        filename = name.rsplit(".", 1)
        filename[0] = "%s-%s" % (filename[0],
                                 "".join(random.sample(string.letters + string.digits, 10)))
        filename = ".".join(filename)

        # Try again if this filename already exists
        try:
            fs.open(filename, "r")
            return generate_filename(name)
        except IOError:
            return filename

    def POST(self):
        post_data = web.input(image = {})

        if not post_data.nickname or not post_data.text:
            raise web.seeother("/")

        message = {"nickname": post_data.nickname,
                   "text": post_data.text,
                   "date": datetime.datetime.utcnow()}

        if post_data.image.filename:
            filename = self.generate_filename(post_data.image.filename)

            # Only accept appropriate file extensions
            if not filename.endswith((".jpg", ".png", ".bmp", ".gif")):
                raise web.seeother("/")

            message["image"] = filename

            # Save fullsize image
            image = post_data.image.file.read()
            full = fs.open(filename, "w")
            full.write(image)
            full.close()

            # Save thumbnail
            thumb = fs.open(filename, "w", "thumb")
            image = Image.open(StringIO.StringIO(image))
            image.thumbnail((80, 60), Image.ANTIALIAS)
            data = StringIO.StringIO()
            image.save(data, image.format)
            thumb.write(data.getvalue())
            thumb.close()
            data.close()

        db.messages.insert(message)

        raise web.seeother("/")


class File:
    def GET(self, collection_or_filename, filename=None):
        if filename is not None:
            f = fs.open(filename, "r", collection_or_filename)
        else:
            f = fs.open(collection_or_filename, "r")
        data = f.read()
        f.close()
        return data


if __name__ == "__main__":
    app.run()
