
#!/usr/bin/env python
import sys
import server.webapp as web
import os
import time
from server import database as db
from server.webapp.webapi import debug
import traceback


print(">>> LOADED: /home/jsbien/git/glyph-miner/server/server.py ver. 0.05 <<<", flush=True)

print("[DEBUG] web.application:", hasattr(web, "application"))


from server.database.connection import MySQLDB

db = MySQLDB(
    db="glyphminer",
    user="glyphminer",
    pw="glyphminer",
    host="localhost",  # or "127.0.0.1"
#    autocommit=True
#    port=3306          # or adjust to match your config
)


timestamp = time.strftime("%Y%m%d-%H%M%S")
# debug_path = os.path.join(os.getcwd(), f"debug-web-{timestamp}.log")

# try:
#     with open(debug_path, "w") as f:
#         f.write(f"web.__file__ = {web.__file__}\n")
#         f.write(f"dir(web) = {dir(web)}\n")
#         f.flush()  # ensure it writes immediately
#     print(f"✅ Debug log written to {debug_path}")
# except Exception as e:
#     print(f"❌ Failed to write debug log: {e}")

import os
import json
import io
import math
import random
import numpy as np
import subprocess

from . import pagecreator

from ctypes import *
from PIL import Image, ImageDraw, ImageOps
from datetime import datetime

import datetime

class DebugClearHandler:
    def POST(self):
        try:
            print(">>> FULL RESET: collections, images, templates, etc. <<<", flush=True)
            cursor = db.connection.cursor()

            # Disable FK checks to avoid constraint violations
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # Clear all relevant tables
            cursor.execute("DELETE FROM collections_images")
            cursor.execute("DELETE FROM labels")
            cursor.execute("DELETE FROM matches")
            cursor.execute("DELETE FROM templates")
            cursor.execute("DELETE FROM images")
            cursor.execute("DELETE FROM collections")

            # Reset auto-increment counters
            for table in [
                "collections", "collections_images", "images",
                "labels", "matches", "templates"
            ]:
                cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")

            # Re-enable FK checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            db.connection.commit()
            return "✅ All tables cleared and counters reset.\n"

        except Exception as e:
            print(f"[ERROR] Failed to reset database: {e}", flush=True)
            raise web.internalerror()
# class DebugClearHandler:
#     def POST(self):
#         try:
#             print(">>> CLEARING collections table <<<", flush=True)
#             cursor = db.connection.cursor()
#             cursor.execute("DELETE FROM collections")
#             db.connection.commit()
#             return "Collections table cleared.\n"
#         except Exception as e:
#             print(f"[ERROR] Failed to clear collections: {e}", flush=True)
#             raise web.internalerror()


class PingHandler:
    def GET(self):
        web.header("Content-Type", "text/plain")
        return "PONG"


# class PingHandler:
#     def GET(self):
#         import datetime
#         ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#         with open(f"./debug-pinghandler-{ts}.log", "w") as debug_file:
#             debug_file.write("PingHandler.GET() was called\n")
#         return ["200 OK", [("Content-Type", "text/plain")], [b"PONG"]]

imageList = {}

# with open("/tmp/debug-web.txt", "w") as f:
#     f.write(f"web.__file__ = {web.__file__}\n")
#     f.write(f"dir(web) = {dir(web)}\n")


# web.config.debug = False

timestamp = time.strftime("%Y%m%d-%H%M%S")
# with open(f"debug-web-{timestamp}.log", "w") as f:
#     f.write(f"web.__file__ = {web.__file__}\n")
#     f.write(f"sys.path = {sys.path}\n")
#     f.write(f"os.listdir(web.__path__[0]) = {os.listdir(web.__path__[0])}\n")


# connect to database - seems redundant
# db = web.database(dbn='mysql', user='glyphminer', pw='glyphminer', db='glyphminer')

class index:

    def GET(self):
        return 'Glyph Miner API'


# import json
# import datetime

class collections_handler:
    def GET(self):
        print(">>> ENTERED collection_handler GET <<<", flush=True)
        try:
            collections = list(db.select('collections'))
            print(">>> FETCHED:", collections, flush=True)

            def serialize(obj):
                if isinstance(obj, datetime.datetime):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")

            web.ctx.status = '200 OK'
            web.header('Content-Type', 'application/json')
            return json.dumps(collections, default=serialize)

        except Exception as e:
            print(f"[ERROR] GET failed: {e}", flush=True)
            raise web.internalerror()

    def POST(self):
        print(">>> ENTERED POST <<<", flush=True)
        try:
            # ✅ SAFELY read raw POST body without relying on web.data()
            content_length = int(web.ctx.env.get('CONTENT_LENGTH', 0) or 0)
            raw = web.ctx.env.get('wsgi.input').read(content_length)
            print(f"[DEBUG] raw input = {repr(raw)}", flush=True)

            decoded = raw.decode("utf-8", errors="replace")
            print(f"[DEBUG] decoded input = {decoded}", flush=True)

            data = json.loads(decoded)
            print(f"[DEBUG] POST /collections - Payload: {data}", flush=True)

            title = data.get("title")
            if not title:
                raise web.badrequest()

            db.insert('collections', title=title)
            db.connection.commit()

            db_result = db.select('collections', where='title=$title', vars={'title': title})
            collection_list = list(db_result)
            if not collection_list:
                raise RuntimeError("Collection insert succeeded but lookup failed")
            collection = collection_list[-1]

            web.ctx.status = '200 OK'
            web.header('Content-Type', 'application/json')
            return json.dumps({'status': 'ok', 'id': collection['id']})

        except Exception as e:
            print(f"[ERROR] POST failed: {e}", flush=True)
            raise web.internalerror()
          
class collection_handler:

    def GET(self, collectionId):
        web.header('Access-Control-Allow-Origin', '*')
        collections = db.query('SELECT * FROM collections')
#        collections = db.select('collections')
        output = [collection for collection in collections]
        return json.dumps(output, cls=DateTimeEncoder)



class synthetic_pages:

    def POST(self, imageId):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())
        args = web.input()

        # get relevant templates and their matches
        matches = {}
        line_height = -1
        for template in db.query("SELECT t.* FROM templates t, images i " +
                                 "WHERE t.image_id = i.id AND i.id = " + imageId + " AND t.visible = 1"):
            # determine height of highest template
            if template.h > line_height:
                line_height = template.h

            # get all matches for this template
            matches[template.glyph] = pagecreator.getMatches(template, db, imageList)

        # check if we have to create pages or only lines
        if (hasattr(args, "lines_only") and args.lines_only == "true"):
            # create synthetic lines and pack them into a zip archive
            pagecreator.createLines(matches, line_height, data["text"], data["dimensions"],
                                    data["margin"], data["letter_spacing"], data["word_spacing"],
                                    data["baseline_skip"], db, imageList)
        else:
            # create synthetic lines and pages and pack them into a zip archive
            pagecreator.createPages(matches, line_height, data["text"], data["dimensions"],
                                    data["margin"], data["letter_spacing"], data["word_spacing"],
                                    data["baseline_skip"], db, imageList)

        web.header('Location', './synthetic_pages/page.zip')
        return "Successfully created synthetic page"

    def OPTIONS(self, imageId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return

class collection_synthetic_pages:

    def POST(self, collectionId):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())
        args = web.input()

        text = data["text"]
        dimensions = data["dimensions"]
        margin = data["margin"]
        letter_spacing = data["letter_spacing"]
        word_spacing = data["word_spacing"]
        baseline_skip = data["baseline_skip"]

        # get relevant templates and their matches
        matches = {}
        line_height = -1
        for template in db.query("SELECT t.* FROM templates t, collections_images ci " +
                                 "WHERE t.image_id = ci.image_id AND ci.collection_id = " + collectionId + " AND t.visible = 1"):
            # determine height of highest template
            if template.h > line_height:
                line_height = template.h

            # get all matches for this template
            matches[template.glyph] = pagecreator.getMatches(template, db, imageList)

        # check if we have to create pages or only lines
        if (hasattr(args, "lines_only") and args.lines_only == "true"):
            # create synthetic lines and pack them into a zip archive
            pagecreator.createLines(matches, line_height, data["text"], data["dimensions"],
                                    data["margin"], data["letter_spacing"], data["word_spacing"],
                                    data["baseline_skip"], db, imageList)
        else:
            # create synthetic lines and pages and pack them into a zip archive
            pagecreator.createPages(matches, line_height, data["text"], data["dimensions"],
                                    data["margin"], data["letter_spacing"], data["word_spacing"],
                                    data["baseline_skip"], db, imageList)

        web.header('Location', './synthetic_pages/page.zip')
        return "Successfully created synthetic page"

    def OPTIONS(self, imageId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return


class collection_images:

    def GET(self, collectionId):
        web.header('Access-Control-Allow-Origin', '*')
        images = [image for image in db.query(
                  "SELECT i.* FROM images i, collections_images ci WHERE i.id = ci.image_id AND ci.collection_id = $cid",
                  vars=dict(cid=collectionId))]
        return json.dumps(images, cls=DateTimeEncoder)


class collection_templates:

    def GET(self, collectionId):
        web.header('Access-Control-Allow-Origin', '*')
        templates = [template for template in db.query(
                     "SELECT t.* FROM templates t, collections_images ci WHERE t.image_id = ci.image_id AND ci.collection_id = $cid AND t.visible = 1",
                     vars=dict(cid=collectionId))]
        return json.dumps(templates, cls=DateTimeEncoder)


class collection_template:

    def GET(self, collectionId, templateId):
        web.header('Access-Control-Allow-Origin', '*')
        # TODO: do something sensible with collectionId?
        return json.dumps(db.select('templates', dict(tid=templateId), where="id = $tid AND visible = 1")[0], cls=DateTimeEncoder)


class memberships:

    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        args = web.input()

        where = ""
        if len(args) > 0 and hasattr(args, 'image_id'):
            iid = int(args.image_id)
            where += "image_id = $iid"
        if len(args) > 0 and hasattr(args, 'collection_id'):
            cid = int(args.collection_id)
            where += " AND " if (len(where) > 0) else ""
            where += "collection_id = $cid"
        if len(where) > 0:
            memberships = db.select('collections_images', vars=locals(), where=where)
        else:
            memberships = db.select('collections_images')

        output = [membership for membership in memberships]
        return json.dumps(output, cls=DateTimeEncoder)

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
#        data = json.loads(web.data())
        content_length = int(web.ctx.env.get("CONTENT_LENGTH", 0) or 0)
        raw = web.ctx.env.get("wsgi.input").read(content_length)
        data = json.loads(raw.decode("utf-8"))
        if not "image_id" in data:
            return web.badrequest("No image given.")
        if not "collection_id" in data:
            return web.badrequest("No collection given.")

        db.insert('collections_images', image_id=data["image_id"], collection_id=data["collection_id"])
        return json.dumps(
            db.select("collections", vars={"cid": data["collection_id"]}, where="id = $cid")[0],
            cls=DateTimeEncoder
        )

#        dbId = db.insert('collections_images', image_id=data["image_id"], collection_id=data["collection_id"])
#        return json.dumps(db.select('collections_images', vars=locals(), where="id = $dbId")[0], cls=DateTimeEncoder)
#        return json.dumps(db.select("collections", vars={"dbId": dbId}, where="id = $dbId")[0], cls=DateTimeEncoder)


    def OPTIONS(self, imageId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return


class image:

    def GET(self, imageId):
        web.header('Access-Control-Allow-Origin', '*')
        return json.dumps(db.select('images', dict(iid=imageId), where="id = $iid")[0], cls=DateTimeEncoder)


class images:

    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        try:
            print(">>> ENTERED images.GET()")  # 🔍 Simple runtime trace
            debug("🔍 Attempting to fetch images with collection count")
            images = db.query(
                'SELECT i.*, COUNT(ci.collection_id) AS collection_count '
                'FROM images i LEFT OUTER JOIN collections_images ci '
                'ON i.id = ci.image_id GROUP BY i.id'
            )
            image_list = list(images)  # ✅ Force result consumption to avoid DB sync issues
            debug("✅ Images fetched successfully")
            return json.dumps(image_list, cls=DateTimeEncoder)

        except Exception as e:
            debug("❌ Error in images GET:", str(e))
            debug.write(traceback.format_exc())
            raise web.internalerror()

    # def GET(self):
    #     web.header('Access-Control-Allow-Origin', '*')
    #     images = db.query('SELECT i.*, COUNT(ci.collection_id) AS collection_count FROM images i LEFT OUTER JOIN collections_images ci ON i.id = ci.image_id GROUP BY i.id')
    #     output = [image for image in images]
    #     return json.dumps(output, cls=DateTimeEncoder)

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        print("🔍 [POST /api/images] Handler entered", flush=True)
        print("📡 DEBUG: ctx.env exists?", hasattr(web.ctx, "env"))
        print("📡 DEBUG: ctx keys:", dir(web.ctx))

        try:
            print(">>> POST /api/images <<<", flush=True)
            web.header("Access-Control-Allow-Origin", "*")
            content_length = int(web.ctx.env.get("CONTENT_LENGTH", 0) or 0)
            raw = web.ctx.env.get("wsgi.input").read(content_length)
            data = json.loads(raw.decode("utf-8"))
            print(f"[DEBUG] JSON input: {data}", flush=True)

            # Insert into DB
            doc_id = db.insert(
                "images",
                title=data.get("title"),
                subtitle=data.get("subtitle"),
                author=data.get("author"),
                year=data.get("year"),
                signature=data.get("signature")
            )
            print(f"[DEBUG] db.insert(...) returned doc_id={doc_id}", flush=True)

            if not doc_id:
                print("❌ db.insert() returned None — insert failed", flush=True)
                raise web.internalerror("Could not insert document into 'images'")

            db.connection.commit()

            doc_list = list(db.select("images", where="id=$doc_id", vars={"doc_id": doc_id}))
            if not doc_list:
                print(f"❌ No document found after insert for id={doc_id}", flush=True)
                raise web.internalerror("Document inserted but not found")

            doc = doc_list[0]

            # # Insert into DB
            # doc_id = db.insert(
            #     "images",
            #     title=data.get("title"),
            #     subtitle=data.get("subtitle"),
            #     author=data.get("author"),
            #     year=data.get("year"),
            #     signature=data.get("signature")
            # )
            # db.connection.commit()

            # doc = list(db.select("images", where="id=$doc_id", vars=locals()))[0]

            web.ctx.status = "200 OK"
            web.header("Content-Type", "application/json")
            return json.dumps(doc, cls=DateTimeEncoder)

        except Exception as e:
            print(f"[ERROR] POST /api/images failed: {e}", flush=True)
            raise web.internalerror()

        def OPTIONS(self, imageId):
            web.header('Content-Type', 'application/json')
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Credentials', 'true')
            web.header('Access-Control-Allow-Headers', 'Content-Type')
            return

class image_file:

        
    def POST(self, imageId, imageType):
        import cgi
        from PIL import Image, ImageOps
        import subprocess

        web.header("Access-Control-Allow-Origin", "*")
        print(f"[DEBUG] 🔁 Upload requested for imageId={imageId} type={imageType}", flush=True)

        # Get WSGI environment
        try:
            env = getattr(web.ctx, "environ", None)
            if not env:
                env = web.ctx.env  # fallback for older web.py
        except Exception as e:
            print(f"[ERROR] Missing WSGI environment: {e}", flush=True)
            raise web.internalerror("Missing WSGI environment")

        # Parse multipart form data manually
        try:
            fs = cgi.FieldStorage(
                fp=env["wsgi.input"],
                environ=env,
                keep_blank_values=True
            )

            if "file" not in fs:
                raise web.badrequest("Missing uploaded file")

            field = fs["file"]
            filename = field.filename
            filedata = field.file.read()
            print(f"[DEBUG] Uploaded: {filename}, size={len(filedata)}", flush=True)

            # Save a copy to disk
            tmp_path = f"debug-upload-{imageId}-{imageType}.dat"
            with open(tmp_path, "wb") as f:
                f.write(filedata)
            print(f"[DEBUG] Saved to {tmp_path}", flush=True)

            # Load image and update DB
            im = Image.open(io.BytesIO(filedata))
            width, height = im.size
            #db.query("UPDATE images SET w = %s, h = %s WHERE id = %s", (width, height, imageId))
#            db.update('images', where="id = %s", params=(imageId,), w=width, h=height)
            db.update('images', vars=dict(iid=imageId), where="id = $iid", w=width, h=height)

            if imageType == "color":
##                db.query("UPDATE images SET web_path_color = %s WHERE id = %s", 
#                         (f"{imageId}-color.png", imageId))
                 db.update('images', vars=dict(iid=imageId), where="id = $iid",
#                           web_path_color=f"tiles_{imageId}-color.png")
                          web_path_color=(imageId + "-color.png"))

                 path = f'./images/{imageId}-color.png'
                 with open(path, 'wb') as f:
                     im.convert('RGB').save(f)

                 subprocess.Popen([
                    "./img2tiles.py",
                     path,
                     f"../web/tiles/tiles_{imageId}-color.png",
#                    f"../web/tiles/{imageId}-color.png",
                     "0",
                     "--verbose"
                ], close_fds=True)

#                 thumb = ImageOps.fit(im, (500, 300), Image.ANTIALIAS, 0.0, (0.0, 0.0))
                 thumb = ImageOps.fit(im, (500, 300), Image.LANCZOS)
                 with open(f"../web/thumbnails/thumb-{imageId}-color.png", 'wb') as f:
                     thumb.convert('RGB').save(f)

            else:  # binarized

#                db.query("UPDATE images SET web_path_color = %s WHERE id = %s", 
                db.update('images', vars=dict(iid=imageId), where="id = $iid",
#                          web_path=(imageId + ".png"))
                          web_path=f"tiles_{imageId}")

                path = f'images/{imageId}.png'
                print(f"[DEBUG] Saving binarized image to {path}", flush=True)
                with open(path, 'wb') as f:
                    im.save(f)

                subprocess.Popen([
                    "./img2tiles.py",
                    path,
                    f"../web/tiles/tiles_{imageId}",
                    "0",
                     "--verbose"
                ], close_fds=True)

#                db.query("UPDATE images SET web_path_color = %s WHERE id = %s", 
                db.update('images', vars=dict(iid=imageId), where="id = $iid",
                          path=(imageId + ".png"))

            result = db.select('images', dict(iid=imageId), where="id = $iid")[0]
            return json.dumps(result, cls=DateTimeEncoder)

        except Exception as e:
            print(f"[ERROR] Upload failed: {e}", flush=True)
            raise web.internalerror()

        


class templates:

    def GET(self, imageId):
        web.header('Access-Control-Allow-Origin', '*')
        templates = db.select('templates', dict(imageId=imageId), where="image_id = $imageId and visible = 1")
        output = [template for template in templates]
        return json.dumps(output, cls=DateTimeEncoder)

    def POST(self, imageId):
        web.header('Access-Control-Allow-Origin', '*')
        try:
            env = getattr(web.ctx, "env", None)
            if not env or "wsgi.input" not in env:
                raise KeyError("Missing wsgi.input in ctx.env")

            length = int(env.get("CONTENT_LENGTH", 0))
            body = env["wsgi.input"].read(length) if length > 0 else b"{}"
            data = json.loads(body.decode("utf-8"))

        except Exception as e:
            print(f"[ERROR] Failed to parse POST body: {e}", flush=True)
            return "400 Bad Request"
#        data = json.loads(web.data())
        if (int(data["w"]) == 0 or int(data["h"]) == 0):
            return web.badrequest("Template has no width or height.")
        imageId = imageId
        dbId = db.insert('templates', image_id=imageId, x=data["x"], y=data["y"], w=data["w"], h=data["h"], glyph=data["glyph"], visible=1)
        return json.dumps(db.select('templates', vars=locals(), where="id = $dbId")[0], cls=DateTimeEncoder)

    def OPTIONS(self, imageId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return


class template:

    def GET(self, imageId, templateId):
        web.header('Access-Control-Allow-Origin', '*')
        return json.dumps(db.select('templates', dict(iid=imageId, tid=templateId), where="id = $tid AND image_id = $iid AND visible = 1")[0], cls=DateTimeEncoder)

    def OPTIONS(self, imageId, templateId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', 'GET, DELETE')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return

    def DELETE(self, imageId, templateId):
        web.header('Access-Control-Allow-Origin', '*')
        db.update('templates', where="id = $tid AND image_id = $iid",
                  vars=dict(tid=templateId, iid=imageId), visible=0)
        return


class model:

    def PUT(self, imageId, templateId):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())
        iid = imageId
        tid = templateId
        if "thresh_score" in data:
            db.update('templates', where="id = $tid AND image_id = $iid", vars=locals(), beta_zero=data["beta_zero"],
                                   beta_one=data["beta_one"], thresh_score=data["thresh_score"])
        else:
            db.update('templates', where="id = $tid AND image_id = $iid", vars=locals(), beta_zero=data["beta_zero"],
                                   beta_one=data["beta_one"])
        return

    def OPTIONS(self, imageId, templateId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', 'PUT')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return


class typography:

    def PUT(self, imageId, templateId):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())
        iid = imageId
        tid = templateId
        db.update('templates', where="id = $tid AND image_id = $iid", vars=locals(),
                               baseline=data["baseline"], leftcrop=data["leftcrop"], rightcrop=data["rightcrop"])
        return

    def OPTIONS(self, imageId, templateId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', 'PUT')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return


class matches:

    def GET(self, imageId, templateId):
        web.header('Access-Control-Allow-Origin', '*')
        maxResults = 1000  # TODO: make this a request parameter
        args = web.input()
        # check for existing matches and return them
        matchesData = db.select('matches', dict(iid=imageId, tid=templateId),
                                where="image_id = $iid AND template_id = $tid")
        matches = [match for match in matchesData]
        if (len(matches) > 0):
            # check if we have to predict labels
            if (hasattr(args, "predict") and args.predict == "true"):
                templ = db.select('templates', dict(tid=templateId), where="id = $tid")[0]
                theta = (templ.beta_zero, templ.beta_one)
                tid = templateId
                matchesAndLabels = db.query("SELECT m.*, t.glyph, l.label_value FROM templates t, matches m LEFT OUTER JOIN labels l ON l.match_id = m.id " +
                                            "WHERE m.template_id = t.id AND t.id = $tid AND m.image_id = $imageId",
                                            vars=locals())
                matches = [match for match in matchesAndLabels]
                for match in matches:
                    if (match.label_value == None and templ.thresh_score != None):
                        match.label_value = (0 if templ.thresh_score <= match.score else 1)
                    elif (match.label_value == None and theta[0] != None and theta[1] != None):
                        match.label_value = self.predictLabel(theta, match)
            return json.dumps(matches, cls=DateTimeEncoder)

        # else, do template matching
        image = db.select('images', dict(iid=imageId), where="id = $iid")[0]
        templ = db.select('templates', dict(iid=imageId, tid=templateId), where="id = $tid AND image_id = $iid")[0]

        # save template to disk, if not external
        if templ.x != None and templ.y != None:
            if (image.id not in imageList):
                im = Image.open('./images/' + image.path)
                im.load()
                imageList[image.id] = im
                print(("adding " + str(image.id) + " to dict"))
            im = imageList[image.id]
            im.crop((templ.x, templ.y, templ.x + templ.w, templ.y + templ.h)).save("templates/" + str(templ.id) + ".png", "PNG")

        # run template matching in separate thread
        process = subprocess.Popen(
            ["./match", './images/' + image.path, './templates/' + str(templ.id) + ".png", str(maxResults)],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        # wait for the process to terminate
        out, err = process.communicate()
        errcode = process.returncode
        if errcode != 0:
            return web.internalerror("Error during template matching")
        matchesJson = out

        # store matches in database
        matches = json.loads(matchesJson)
        t = db.transaction()
        for match in matches:
            db.insert('matches', image_id=imageId, template_id=templateId, x=match["x"], y=match["y"],
                                w=match["w"], h=match["h"], score=match["score"], rank=match["rank"])
        t.commit()

        # get matches from DB so we return all the ids
        templateData = db.select('matches', dict(iid=imageId, tid=templateId),
                                 where="image_id = $iid AND template_id = $tid")
        templates = [template for template in templateData]
        return json.dumps(templates, cls=DateTimeEncoder)

    def predictLabel(self, theta, match):
        a = match.rank / 1000.0
        return self.sigmoid(np.dot(np.transpose(theta), (1, a)))

    def sigmoid(self, x):
        return 1.0 / (1.0 + math.exp(x))


class collection_matches:

    def GET(self, collectionId, templateId):
        web.header('Access-Control-Allow-Origin', '*')
        maxResults = 300  # TODO: make this a request parameter

        # Safely parse query string (instead of web.input())
        try:
            env = getattr(web.ctx, "env", {})
            qs = env.get("QUERY_STRING", "")
            params = dict(q.split("=") for q in qs.split("&") if "=" in q)
            print(f"[DEBUG] Parsed query string: {params}", flush=True)
        except Exception as e:
            print(f"[ERROR] Failed to parse query string: {e}", flush=True)
            params = {}

        # Predict mode
        if params.get("predict") == "true":
            templ = db.select('templates', dict(tid=templateId), where="id = $tid")[0]
            matchesAndLabels = db.query(
                "SELECT m.*, t.glyph, l.label_value FROM templates t, matches m "
                "LEFT OUTER JOIN labels l ON l.match_id = m.id "
                "WHERE m.template_id = t.id AND t.id = $tid",
                vars=dict(tid=templateId)
            )
            matches = list(matchesAndLabels)
            for match in matches:
                if templ["thresh_score"] is None:
                    match["label_value"] = None
                elif match["label_value"] not in ["user_positive", "user_negative"]:
                    match["label_value"] = 0 if templ["thresh_score"] <= match["score"] else 1
            return json.dumps(matches, cls=DateTimeEncoder)

        # Else: perform template matching
        images = list(db.query(
            "SELECT i.* FROM images i, collections_images ci WHERE i.id = ci.image_id AND ci.collection_id = $cid",
            vars=dict(cid=collectionId)
        ))

        templ = db.select('templates', dict(tid=templateId), where="id = $tid")[0]

        # Save template image to disk (if not external)
        if templ["x"] is not None and templ["y"] is not None:
            template_image = db.select('images', dict(iid=templ["image_id"]), where="id = $iid")[0]
            if template_image["id"] not in imageList:
                im = Image.open('./images/' + template_image["path"])
                im.load()
                imageList[template_image["id"]] = im
                print("adding " + str(template_image["id"]) + " to dict", flush=True)
            im = imageList[template_image["id"]]
            im.crop((
                templ["x"], templ["y"],
                templ["x"] + templ["w"],
                templ["y"] + templ["h"]
            )).save("templates/" + str(templ["id"]) + ".png", "PNG")

        # Perform matching (only if not already matched)
        for image in images:
            count = db.query(
                "SELECT COUNT(*) FROM matches WHERE image_id = $iid AND template_id = $tid",
                vars=dict(iid=image["id"], tid=templateId)
            )[0]["COUNT(*)"]
            if count > 0:
                continue

            process = subprocess.Popen(
                ["./match", f'./images/{image["path"]}', f'./templates/{templ["id"]}.png', str(maxResults)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, err = process.communicate()
            if process.returncode != 0:
                print(f"[ERROR] match failed on image {image['id']}: {err.decode()}", flush=True)
                continue

            matches = json.loads(out)

            for match in matches:
                db.insert('matches',
                          image_id=image["id"], template_id=templateId,
                          x=match["x"], y=match["y"], w=match["w"], h=match["h"],
                          score=match["score"], rank=match["rank"]
                )
            # t = db.transaction()
            # for match in matches:
            #     db.insert('matches',
            #         image_id=image["id"], template_id=templateId,
            #         x=match["x"], y=match["y"], w=match["w"], h=match["h"],
            #         score=match["score"], rank=match["rank"]
            #     )
            # t.commit()

        # Return all matches
        finalMatches = list(db.query(
            "SELECT DISTINCT m.* FROM matches m, images i, collections_images ci "
            "WHERE i.id = ci.image_id AND ci.collection_id = $cid AND m.template_id = $tid",
            vars=dict(cid=collectionId, tid=templateId)
        ))
        return json.dumps(finalMatches, cls=DateTimeEncoder)

    
#     def GET(self, collectionId, templateId):
#         web.header('Access-Control-Allow-Origin', '*')
#         maxResults = 300  # TODO: make this a request parameter
# #        args = web.input()
#         try:
#             env = getattr(web.ctx, "env", {})
#             qs = env.get("QUERY_STRING", "")
#             params = dict(q.split("=") for q in qs.split("&") if "=" in q)
#             print(f"[DEBUG] Parsed query string: {params}", flush=True)
#         except Exception as e:
#             print(f"[ERROR] Failed to parse query string: {e}", flush=True)
#             params = {}


#         # check if we have to predict labels
# #        if (hasattr(args, "predict") and args.predict == "true"):
#         if params.get("predict") == "true":
#             templ = db.select('templates', dict(tid=templateId), where="id = $tid")[0]
#             tid = templateId
#             # TODO: check for correct collection?
#             matchesAndLabels = db.query("SELECT m.*, t.glyph, l.label_value FROM templates t, matches m LEFT OUTER JOIN labels l ON l.match_id = m.id " +
#                                         "WHERE m.template_id = t.id AND t.id = $tid",
#                                         vars=locals())
#             matches = [match for match in matchesAndLabels]
#             for match in matches:
#                 if templ.thresh_score == None:
#                     match.label_value = None
#                 elif match.label_value != "user_positive" and match.label_value != "user_negative":
#                     match.label_value = (0 if templ.thresh_score <= match.score else 1)
#             return json.dumps(matches, cls=DateTimeEncoder)

#         # else, do template matching
#         images = [image for image in db.query(
#             "SELECT i.* FROM images i, collections_images ci WHERE i.id = ci.image_id AND ci.collection_id = $cid", vars=dict(cid=collectionId))]
#         templ = db.select('templates', dict(tid=templateId), where="id = $tid")[0]

#         # save template to disk, if not external
#         if templ["x"] is not None and templ["y"] is not None:
#             template_image = db.select('images', dict(iid=templ["image_id"]), where="id = $iid")[0]
#             # saving image to global dict to speed things up. BEWARE: race conditions?
#             if template_image["id"] not in imageList:
#                 im = Image.open('./images/' + template_image["path"])
#                 im.load()
#                 imageList[template_image["id"]] = im
#                 print("adding " + str(template_image["id"]) + " to dict")
#             im = imageList[template_image["id"]]
#             im.crop((templ["x"], templ["y"], templ["x"] + templ["w"], templ["y"] + templ["h"])).save("templates/" + str(templ["id"]) + ".png", "PNG")

#         # if templ.x != None and templ.y != None:
#         #     template_image = db.select('images', dict(iid=templ.image_id), where="id = $iid")[0]
#         #     # saving image to global dict to speed things up. BEWARE: race conditions?
#         #     if (template_image.id not in imageList):
#         #         im = Image.open('./images/' + template_image.path)
#         #         im.load()
#         #         imageList[template_image.id] = im
#         #         print(("adding " + str(template_image.id) + " to dict"))
#         #     im = imageList[template_image.id]
#         #     # im.crop((templ.x, templ.y, templ.x + templ.w, templ.y + templ.h)).save("templates/" + str(templ.id) + ".png", "PNG")

#         # run template matching processes in separate thread
#         processes = {}
#         for image in images:
#                 # check whether we have matches for this template and this image already
#             if (db.query("SELECT COUNT(*) FROM matches WHERE image_id = $iid AND template_id = $tid", vars=dict(iid=image.id, tid=templateId))[0]['COUNT(*)'] > 0):
#                 continue

#             # otherwise, do the actual template matching by calling the external library
#             process = subprocess.Popen(
#                 ["./match", './images/' + image.path, './templates/' +
#                     str(templ.id) + ".png", str(maxResults)],
#                 shell=False,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE)
#             out, err = process.communicate()
#             errcode = process.returncode
#             if errcode != 0:
#                 print("Error during template matching")
#                 continue
#             matches = json.loads(out)
#             t = db.transaction()
#             for match in matches:
#                 db.insert('matches', image_id=image.id, template_id=templateId, x=match["x"], y=match["y"],
#                           w=match["w"], h=match["h"], score=match["score"], rank=match["rank"])
#             t.commit()

#         # get matches again from DB so we return all the ids (and all matches that have been there before)
#         finalMatches = [finalMatch for finalMatch in db.query(
#             "SELECT DISTINCT m.* FROM matches m, images i, collections_images ci WHERE i.id = ci.image_id AND ci.collection_id = $cid AND m.template_id = $tid",
#             vars=dict(cid=collectionId, tid=templateId))]
#         return json.dumps(finalMatches, cls=DateTimeEncoder)

    def predictLabel(self, theta, match):
        a = match.rank / 1000.0
        return self.sigmoid(np.dot(np.transpose(theta), (1, a)))

    def sigmoid(self, x):
        return 1.0 / (1.0 + math.exp(x))


class match:

    def GET(self, imageId, templateId, matchId):
        web.header('Access-Control-Allow-Origin', '*')
        return json.dumps(db.select('matches',dict(iid=imageId, tid=templateId, mid=matchId),
                                    where="id = matchId AND template_id = $tid AND image_id = $iid")[0], cls=DateTimeEncoder)


class matchlabel:

    def POST(self, imageId, templateId, matchId):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())
        tid = templateId
        mid = matchId
        dbId = db.insert('labels', match_id=matchId,
                                   template_id=tid,
                                   label_value=data["label"],
                                   time=data["label_time"],
                                   iteration=data["label_iteration"])
        return json.dumps(db.select('labels', vars=locals(), where="id = $dbId")[0], cls=DateTimeEncoder)

    def OPTIONS(self, imageId, templateId, matchId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', 'POST')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return


class matchselect:

    def PUT(self, imageId, templateId, matchId):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())
        disable = 1 if data["disable"] == True else 0

        db.update('matches', vars=dict(id=matchId), where="id = $id", disabled=disable)
        return json.dumps(db.select('matches', vars=dict(id=matchId), where="id = $id")[0], cls=DateTimeEncoder)

    def OPTIONS(self, imageId, templateId, matchId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', 'PUT')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return

class crop:
    def GET(self, imageId):
        import os
        import io
        from PIL import Image
#        from server import database as db
        import server.webapp as web

        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'image/png')

        # Parse query string safely
        try:
            env = getattr(web.ctx, "env", {})
            qs = env.get("QUERY_STRING", "")
            params = dict(q.split("=") for q in qs.split("&"))
            x1, y1, x2, y2 = int(params["x1"]), int(params["y1"]), int(params["x2"]), int(params["y2"])
        except Exception as e:
            print(f"[ERROR] Failed to parse query string: {e}", flush=True)
            return "400 Bad Request"

        # Validate crop area
        if (x2 - x1 <= 0 or y2 - y1 <= 0):
            return "400 Bad Request — zero area crop"

        try:
            # Get image metadata from DB (Row object)
            # image = db.select('images', dict(iid=imageId), where="id = $iid")[0]
            # print(f"[DEBUG] DB returned image: {image} (type: {type(image)})", flush=True)

            # path = image.path  # ✅ Access path directly from Row object

            image = db.select('images', dict(iid=imageId), where="id = $iid")[0]
            print(f"[DEBUG] DB returned image: {image} (type: {type(image)})", flush=True)

            # Handle both str and object with .path attribute
            if isinstance(image, str):
                path = image
            elif hasattr(image, "path"):
                path = image.path
            elif isinstance(image, dict) and "path" in image:
                path = image["path"]
            else:
                raise Exception(f"Unexpected image record: {image}")

            # Cache image if not loaded
            if imageId not in imageList:
                im = Image.open('./images/' + path)
                im.load()
                imageList[imageId] = im
                print(f"[DEBUG] Loaded and cached image {imageId}", flush=True)

            im = imageList[imageId]
            buf = io.BytesIO()
            im.crop((x1, y1, x2, y2)).save(buf, format="PNG")
            return buf.getvalue()

        except Exception as e:
            print(f"[ERROR] Failed to serve crop: {e}", flush=True)
            return "500 Internal Server Error"

        # class crop:
#     def GET(self, imageId):
#         import os
#         import io
#         from PIL import Image
#         from server import database as db
#         import server.webapp as web

#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Content-Type', 'image/png')

#         try:
#             env = getattr(web.ctx, "env", {})
#             qs = env.get("QUERY_STRING", "")
#             params = dict(q.split("=") for q in qs.split("&"))
#             x1, y1, x2, y2 = int(params["x1"]), int(params["y1"]), int(params["x2"]), int(params["y2"])
#         except Exception as e:
#             print(f"[ERROR] Failed to parse query string: {e}", flush=True)
#             return "400 Bad Request"

#         if (x2 - x1 <= 0 or y2 - y1 <= 0):
#             return "400 Bad Request — zero area crop"

#         try:
#             image = db.select('images', dict(iid=imageId), where="id = $iid")[0]
#             print(f"[DEBUG] DB returned image: {image} (type: {type(image)})", flush=True)

#             if isinstance(image, str):
#                 path = image
#             elif isinstance(image, dict) and "path" in image:
#                 path = image["path"]
#             else:
#                 raise Exception(f"Unexpected DB row format: {image}")

#             if imageId not in imageList:
#                 im = Image.open('./images/' + path)
#                 im.load()
#                 imageList[imageId] = im
#                 print(f"[DEBUG] Loaded and cached image {imageId}", flush=True)

#             im = imageList[imageId]
#             buf = io.BytesIO()
#             im.crop((x1, y1, x2, y2)).save(buf, format="PNG")
#             return buf.getvalue()

#         except Exception as e:
#             print(f"[ERROR] Failed to serve crop: {e}", flush=True)
#             return "500 Internal Server Error"
 
#             # image = db.select('images', dict(iid=imageId), where="id = $iid")[0]
#             # if imageId not in imageList:
#             #     im = Image.open('./images/' + image.path)
#             #     im.load()
#             #     imageList[imageId] = im
#             #     print(f"[DEBUG] Loaded and cached image {imageId}", flush=True)

#             # im = imageList[imageId]
#             # buf = io.BytesIO()
#             # im.crop((x1, y1, x2, y2)).save(buf, format="PNG")
#             # return buf.getvalue()

#         except Exception as e:
#             print(f"[ERROR] Failed to serve crop: {e}", flush=True)
#             return "500 Internal Server Error"


class matchcrop:
    def GET(self, image_id, template_id, match_id):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-type', 'image/png')

        # --- Parse query string manually ---
        try:
            env = getattr(web.ctx, "env", {})
            qs = env.get("QUERY_STRING", "")
            args = dict(q.split("=") for q in qs.split("&") if "=" in q)
            print(f"[DEBUG] Parsed query string: {args}", flush=True)
        except Exception as e:
            print(f"[ERROR] Failed to parse query string: {e}", flush=True)
            args = {}

        # --- Parse margin + box parameters safely ---
        try:
            margin_top = int(args.get("margin_top", 0))
            margin_left = int(args.get("margin_left", 0))
            margin_right = int(args.get("margin_right", 0))
            margin_bottom = int(args.get("margin_bottom", 0))
            box = args.get("box", "false").lower() == "true"
        except Exception as e:
            print(f"[ERROR] Failed to parse margins: {e}", flush=True)
            return web.badrequest()

        # --- Get image from DB and cache ---
        image = db.select('images', dict(iid=image_id), where="id = $iid")[0]
        if image["id"] not in imageList:
            im = Image.open('./images/' + image["path"])
            im.load()
            imageList[image["id"]] = im
            print(f"adding {image['id']} to dict", flush=True)
        im = imageList[image["id"]]

        # --- Get match box from DB ---
        match = db.select('matches', dict(iid=image_id, tid=template_id, mid=match_id),
                          where="id = $mid AND template_id = $tid AND image_id = $iid")[0]

        # --- Crop the matched glyph with margins ---
        x1 = match["x"] - margin_left
        y1 = match["y"] - margin_top
        x2 = match["x"] + match["w"] + margin_right
        y2 = match["y"] + match["h"] + margin_bottom
        im_cropped = im.crop((x1, y1, x2, y2))

        # --- Draw red box if requested ---
        if box:
            im_cropped = im_cropped.convert("RGBA")
            draw = ImageDraw.Draw(im_cropped)
            draw.rectangle(
                [(margin_left, margin_top), (margin_left + match["w"], margin_top + match["h"])],
                outline=(255, 0, 0, 200)
            )

        # --- Return as PNG ---
        buf = io.BytesIO()
        im_cropped.save(buf, format="PNG")
        return buf.getvalue()

#     def GET(self, imageId, templateId, matchId):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Content-type', 'image/png')
# #        args = web.input()
#         try:
#             env = getattr(web.ctx, "env", {})
#             qs = env.get("QUERY_STRING", "")
#             args = dict(q.split("=") for q in qs.split("&") if "=" in q)
#             print(f"[DEBUG] Parsed query string: {args}", flush=True)
#         except Exception as e:
#             print(f"[ERROR] Failed to parse query string: {e}", flush=True)
#             args = {}


#         # get image from database
#         image = db.select('images', dict(iid=imageId), where="id = $iid")[0]

#         # saving image to global dict to speed things up
#         if (imageId not in imageList):
#             im = Image.open('./images/' + image.path)
#             im.load()
#             imageList[imageId] = im
#             print(("adding " + imageId + " to dict"))
#         im = imageList[imageId]

#         # get match from database
#         match = db.select('matches', dict(iid=imageId, tid=templateId, mid=matchId),
#                           where="id = $mid AND template_id = $tid AND image_id = $iid")[0]

#         # crop image of desired size
#         margin_top = int(args.margin_top)
#         margin_left = int(args.margin_left)
#         margin_right = int(args.margin_right)
#         margin_bottom = int(args.margin_bottom)
#         im_cropped = im.crop((match.x - margin_left,
#                               match.y - margin_top,
#                               match.x + match.w + margin_right,
#                               match.y + match.h + margin_bottom))

#         # draw rectangle around template if desired
#         if (hasattr(args, "box") and args.box == "true"):
#             im_cropped = im_cropped.convert("RGBA")
#             draw = ImageDraw.Draw(im_cropped)
#             draw.rectangle([(margin_left, margin_top),
#                             (margin_left + match.w, margin_top + match.h)],
#                            outline=(255, 0, 0, 200))

#         # save image to buffer and return
#         buf = io.BytesIO()
#         im_cropped.save(buf, format="PNG")
#         return buf.getvalue()
# #        buf = io.StringIO()
#         # im_cropped.save(buf, "PNG")
#         # contents = buf.getvalue()
#         # return contents

    

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super().default(o)

    
# define resource paths
urls = (
    # Match labels, crops, matches
    '/api/images/(.*)/templates/(.*)/matches/(.*)/label', 'matchlabel',
    '/api/images/(.*)/templates/(.*)/matches/(.*)/crops', 'matchcrop',
    '/api/images/(.*)/templates/(.*)/matches/(.*)', 'match',
    '/api/images/(.*)/templates/(.*)/matches', 'matches',

    # Templates and synthetic pages
    '/api/images/(.*)/templates/(.*)', 'template',
    '/api/images/(.*)/templates', 'templates',
    '/api/images/(.*)/synthetic_pages', 'synthetic_pages',
    '/api/images/(.*)/crops', 'crop',

    # Image uploads (color/binarized)
    '/api/images/(.*)/(color|binarized)', 'image_file',

    # Individual image
    '/api/images/(.*)', 'image',

    # Image list (must come after all /images/<id> routes)
    '/api/images', 'images',

    # Collections
    '/api/collections/(.*)/templates/(.*)/matches', 'collection_matches',
    '/api/collections/(.*)/templates/(.*)', 'collection_template',
    '/api/collections/(.*)/templates', 'collection_templates',
    '/api/collections/(.*)/images', 'collection_images',
    '/api/collections/(.*)/synthetic_pages', 'collection_synthetic_pages',
    '/api/collections/(.*)', 'collection',
    '/api/collections', 'collections',

    '/api/memberships', 'memberships',

    # Utility
    '/api/debug/clear', 'DebugClearHandler',
    '/api/ping', 'PingHandler',
)

# DEBUG: inspect the structure of urls
with open("/tmp/debug-urls.txt", "w") as f:
    f.write(f"Type of urls: {type(urls)}\n")
    for i, item in enumerate(urls):
        f.write(f"urls[{i}] = {repr(item)} (type: {type(item)})\n")


# import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
# with open(f"./debug-handler-scope-{timestamp}.log", "w") as f:
#     f.write(f"'PingHandler' in globals(): {'PingHandler' in globals()}\n")
    
print(f">>> collections_handler has methods: {dir(collections_handler)}", flush=True)

handler_map = {
    'DebugClearHandler': DebugClearHandler,
    'PingHandler': PingHandler,
    'index': index,
    'collections': collections_handler,
    'collection': collection_handler,
    'collection_images': collection_images,
    'collection_templates': collection_templates,
    'collection_template': collection_template,
    'collection_synthetic_pages': collection_synthetic_pages,
    'images': images,
    'image': image,
    'templates': templates,
    'template': template,
    'synthetic_pages': synthetic_pages,
    'crop': crop,
    'image_file': image_file,
    'memberships': memberships,
    'matches': matches,
    'match': match,
    'matchlabel': matchlabel,
    'matchselect': matchselect,
    'matchcrop': matchcrop,
    'model': model,
    'typography': typography,
    'collection_matches': collection_matches
}

print(f"[DEBUG] collections = {handler_map['collections']} (type: {type(handler_map['collections'])})", flush=True)

import datetime
ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
# with open(f"./handler-map-debug-{ts}.log", "w") as debug_file:
#     handler = handler_map.get("PingHandler", None)
#     debug_file.write(f"PingHandler in handler_map: {'PingHandler' in handler_map}\n")
#     debug_file.write(f"handler_map['PingHandler']: {repr(handler)}\n")
#     debug_file.write(f"type: {type(handler)}\n")

print(f">>> collections_handler has POST: {'POST' in dir(collections_handler)}", flush=True)

#app = web.application(urls, globals())
app = web.application(urls, handler_map)


application = app.wsgifunc()
import datetime
ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
# with open(f"./debug-application-object-{ts}.log", "w") as debug_file:
#     debug_file.write(f"type(application): {type(application)}\n")
#     debug_file.write(f"dir(application): {dir(application)}\n")

if hasattr(collections_handler, "POST"):
    print(">>> YES: collections_handler.POST exists", flush=True)
else:
    print(">>> NO: collections_handler.POST is missing", flush=True)

print(f"[DEBUG] application = {application}")
print(f"[DEBUG] application.__module__ = {application.__module__}")

if __name__ == "__main__":
    app.run()
    
