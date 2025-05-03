# server/server.py

# import web wrong!
import server.webapp as web
import json
from datetime import datetime
from web.db import SQLLiteral

print(">>> LOADED: server.py (Python 3, safe handler names) ver. 0.02 <<<")

urls = (
    '/api/collections', 'collections_handler',
    '/api/images', 'images_handler',
    '/api/images/(\d+)/color', 'color_handler',
    '/api/images/(\d+)/binarized', 'binarized_handler',
    '/api/memberships', 'memberships_handler',
    '/api/select', 'select_handler'
)

app = web.application(urls, globals())

db = web.database(dbn='mysql', user='root', pw='',
                  db='glyphminer', host='localhost', charset='utf8')


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class collections_handler:
    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        return json.dumps(list(db.select('collections')), cls=DateTimeEncoder)

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())

        if not "title" in data or data["title"] == "":
            return web.badrequest("No title given.")

        for key in ["subtitle", "author", "year", "signature"]:
            if key not in data:
                data[key] = None

        dbId = db.insert('collections',
                         title=data["title"],
                         subtitle=data["subtitle"],
                         author=data["author"],
                         year=data["year"],
                         signature=data["signature"])

        result = list(db.select('collections', vars={'dbId': dbId}, where="id = $dbId"))
        if not result:
            raise RuntimeError(f"No collection found after insert (id={dbId})")

        web.header("Content-Type", "application/json")
        print(">>> COLLECTION CREATED AND RETURNED <<<")
        return json.dumps(result[0], cls=DateTimeEncoder)


# Minimal placeholder classes for rest of API
class images_handler:
    def GET(self):
        return json.dumps([])

    def POST(self):
        return json.dumps({"id": -1})


class color_handler:
    def POST(self, image_id):
        return json.dumps({"status": "uploaded color"})


class binarized_handler:
    def POST(self, image_id):
        return json.dumps({"status": "uploaded binarized"})


class memberships_handler:
    def POST(self):
        return json.dumps({"status": "assigned"})


class select_handler:
    def GET(self):
        return json.dumps([])


if __name__ == "__main__":
    app.run()
