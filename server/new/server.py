urls = (
    '/api/', 'index',
    '/api/images/(.*)/templates/(.*)/matches/(.*)/label', 'matchlabel',
    '/api/images/(.*)/templates/(.*)/matches/(.*)/crops', 'matchcrop',
    '/api/images/(.*)/templates/(.*)/matches/(.*)/select', 'matchselect',
    '/api/images/(.*)/templates/(.*)/matches/(.*)', 'match',
    '/api/images/(.*)/templates/(.*)/matches', 'matches',
    '/api/images/(.*)/templates/(.*)/model', 'model',
    '/api/images/(.*)/templates/(.*)/typography', 'typography',
    '/api/images/(.*)/templates/(.*)', 'template',
    '/api/images/(.*)/templates', 'templates',
    '/api/images/(.*)/crops', 'crop',
    '/api/images/(.*)/(color|binarized)', 'image_file',
    '/api/images/(.*)/synthetic_pages', 'synthetic_pages',
    '/api/images/(.*)', 'image',
    '/api/images', 'images',
    '/api/collections/(.*)/templates/(.*)/matches', 'collection_matches',
    '/api/collections/(.*)/templates/(.*)', 'collection_template',
    '/api/collections/(.*)/templates', 'collection_templates',
    '/api/collections/(.*)/images', 'collection_images',
    '/api/collections/(.*)/synthetic_pages', 'collection_synthetic_pages',
    '/api/collections/(.*)', 'collection',
    '/api/collections', 'collections',
    '/api/memberships', 'memberships'
)



import server.webapp as web
import json
from datetime import datetime

print(">>> LOADED: server.py (Python 3 restored structure) <<<")

urls = (
    '/api/', 'index_handler',
    '/api/collections', 'collections_handler',
    '/api/collections/(\d+)', 'collections_handler',
    '/api/images', 'images_handler',
    '/api/images/(\d+)', 'images_handler',
    '/api/images/(\d+)/color', 'color_handler',
    '/api/images/(\d+)/binarized', 'binarized_handler',
    '/api/memberships', 'memberships_handler',
    '/api/select', 'select_handler'
)

app = web.application(urls, globals())
application = app  # for uwsgi

db = web.database(dbn='mysql', user='root', pw='',
                  db='glyphminer', host='localhost', charset='utf8')


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class collections_handler:
    def GET(self):
        print(">>> ENTERED collections_handler.GET <<<", flush=True)

        try:
            collections_query = db.select('collections')
            collections = list(collections_query)

            print(f"[DEBUG] Retrieved collections: {collections}", flush=True)
            web.header('Content-Type', 'application/json')
            return json.dumps(collections)

        except Exception as e:
            print(f"[ERROR] collections_handler.GET failed: {e}", flush=True)
            raise

        
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


class images_handler:
    def GET(self, image_id=None):
        web.header('Access-Control-Allow-Origin', '*')
        if image_id:
            result = list(db.select('images', where="id=$id", vars={'id': int(image_id)}))
            if result:
                return json.dumps(result[0], cls=DateTimeEncoder)
            else:
                return web.notfound()
        else:
            return json.dumps(list(db.select('images')), cls=DateTimeEncoder)

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())

        if not "title" in data or data["title"] == "":
            return web.badrequest("No title given.")

        dbId = db.insert('images', title=data["title"])
        result = list(db.select('images', vars={'dbId': dbId}, where="id = $dbId"))

        web.header("Content-Type", "application/json")
        return json.dumps(result[0], cls=DateTimeEncoder)


class color_handler:
    def POST(self, image_id):
        web.header('Access-Control-Allow-Origin', '*')
        x = web.input(file={})
        if not x.file.filename:
            return web.badrequest("No file uploaded.")

        db.update('images', where="id=$id", vars={'id': int(image_id)},
                  color=x.file.file.read())

        return json.dumps({"status": "ok"})


class binarized_handler:
    def POST(self, image_id):
        web.header('Access-Control-Allow-Origin', '*')
        x = web.input(file={})
        if not x.file.filename:
            return web.badrequest("No file uploaded.")

        db.update('images', where="id=$id", vars={'id': int(image_id)},
                  binarized=x.file.file.read())

        return json.dumps({"status": "ok"})


class memberships_handler:
    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())

        if not ("image_id" in data and "collection_id" in data):
            return web.badrequest("Missing image_id or collection_id")

        db.insert('memberships',
                  image_id=data["image_id"],
                  collection_id=data["collection_id"])

        return json.dumps({"status": "ok"})


class select_handler:
    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        return json.dumps(list(db.query("SELECT id, title FROM collections")), cls=DateTimeEncoder)


class index_handler:
    def GET(self):
        web.header("Content-Type", "text/plain")
        return "Glyph Miner API"


handler_map = {
    'collections': collections_handler,
    'images': images_handler
}

if __name__ == "__main__":
    app.run()
