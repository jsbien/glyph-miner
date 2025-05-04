#!/usr/bin/env python
import sys
import server.webapp as web
import os
import time
# import web

print(">>> LOADED: /home/jsbien/git/glyph-miner/server/server.py ver. 0.02 <<<", flush=True)

timestamp = time.strftime("%Y%m%d-%H%M%S")
debug_path = os.path.join(os.getcwd(), f"debug-web-{timestamp}.log")

try:
    with open(debug_path, "w") as f:
        f.write(f"web.__file__ = {web.__file__}\n")
        f.write(f"dir(web) = {dir(web)}\n")
        f.flush()  # ensure it writes immediately
    print(f"✅ Debug log written to {debug_path}")
except Exception as e:
    print(f"❌ Failed to write debug log: {e}")

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

with open("/tmp/debug-web.txt", "w") as f:
    f.write(f"web.__file__ = {web.__file__}\n")
    f.write(f"dir(web) = {dir(web)}\n")


# web.config.debug = False

timestamp = time.strftime("%Y%m%d-%H%M%S")
with open(f"debug-web-{timestamp}.log", "w") as f:
    f.write(f"web.__file__ = {web.__file__}\n")
    f.write(f"sys.path = {sys.path}\n")
    f.write(f"os.listdir(web.__path__[0]) = {os.listdir(web.__path__[0])}\n")


# connect to database
db = web.database(dbn='mysql', user='glyphminer', pw='glyphminer', db='glyphminer')

class index:

    def GET(self):
        return 'Glyph Miner API'


class collection_handler:

    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        collections = db.query('SELECT * FROM collections')
#        collections = db.select('collections')
        output = [collection for collection in collections]
        return json.dumps(output, cls=DateTimeEncoder)

import json
from server.webapp import webapi
from server.server import db  # Ensure your db instance is available at this path

class collections_handler:
    def POST(self):
        print(">>> Entering collections_handler.POST", flush=True)
        data = webapi.data()
        print(f"[DEBUG] raw data = {repr(data)}", flush=True)
        # decode bytes to string first
        if isinstance(data, bytes):
            data = data.decode("utf-8", errors="replace")  # safe decoding
            print(f"[DEBUG] decoded data = {repr(data)}", flush=True)
        # if isinstance(data, bytes):
        #     data = data.decode("utf-8")
        payload = json.loads(data)
        print(f"[DEBUG] POST /collections - Payload: {payload}", flush=True)

        if "title" not in payload:
            raise webapi.badrequest()

        db.insert('collections', title=payload["title"])
        return json.dumps({'status': 'ok'})

    def GET(self):
        print(">>> ENTERED GET <<<", flush=True)
        collections = list(db.select('collections'))
        return json.dumps(collections)
    
# class collections_handler:

#     def __init__(self):
#         print(">>> INIT: collections_handler <<<", flush=True)

#     def GET(self):
#         print(">>> ENTERED GET <<<", flush=True)
#         web.header('Access-Control-Allow-Origin', '*')
#         collections = db.query('SELECT * FROM collections')
#         output = [collection for collection in collections]
#         return json.dumps(output, cls=DateTimeEncoder)

#     def POST(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         print(">>> POST /collections entered <<<", flush=True)

#         try:
#             data_raw = web.data()
#             print(f"[DEBUG] Raw request data: {data_raw}")
#             data = json.loads(data_raw)
#             print(f"[DEBUG] Parsed data: {data}")
#         except Exception as e:
#             print(f"[ERROR] Failed to parse request body: {e}")
#             return web.badrequest("Invalid JSON payload.")

#         if not "title" in data or data["title"] == "":
#             print("[ERROR] Title missing in payload.")
#             return web.badrequest("No title given.")

#         for key in ["subtitle", "author", "year", "signature"]:
#             if key not in data:
#                 data[key] = None
                
#         try:
#             dbId = db.insert('collections',
#                              title=data["title"],
#                              subtitle=data["subtitle"],
#                              author=data["author"],
#                              year=data["year"],
#                              signature=data["signature"])
#             print(f"[DEBUG] dbId after insert: {dbId} ({type(dbId)})")

#             result = list(db.select('collections', vars={'dbId': dbId}, where="id = $dbId"))
#             print(f"[DEBUG] Select result: {result}")

#             if not result:
#                 print("[ERROR] No collection found after insert.")
#                 return web.internalerror("Collection inserted but not found.")

#             web.header("Content-Type", "application/json")
#             print(">>> COLLECTION CREATED AND RETURNED <<<")
#             return json.dumps(result[0], cls=DateTimeEncoder)

#         except Exception as e:
#             print(f"[FATAL] Exception during insert/select: {e}")
#             return web.internalerror("Failed to create collection.")


#    def OPTIONS(self, imageId):
    # def OPTIONS(self):
    #     web.header('Content-Type', 'application/json')
    #     web.header('Access-Control-Allow-Origin', '*')
    #     web.header('Access-Control-Allow-Credentials', 'true')
    #     web.header('Access-Control-Allow-Headers', 'Content-Type')
    #     return


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
        data = json.loads(web.data())
        if not "image_id" in data:
            return web.badrequest("No image given.")
        if not "collection_id" in data:
            return web.badrequest("No collection given.")

        dbId = db.insert('collections_images', image_id=data["image_id"], collection_id=data["collection_id"])
#        return json.dumps(db.select('collections_images', vars=locals(), where="id = $dbId")[0], cls=DateTimeEncoder)
        return json.dumps(db.select("collections", vars={"dbId": dbId}, where="id = $dbId")[0], cls=DateTimeEncoder)


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
        images = db.query('SELECT i.*, COUNT(ci.collection_id) AS collection_count FROM images i LEFT OUTER JOIN collections_images ci ON i.id = ci.image_id GROUP BY i.id')
        output = [image for image in images]
        return json.dumps(output, cls=DateTimeEncoder)

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())
        if not "title" in data:
            data["title"] = None
        if not "subtitle" in data:
            data["subtitle"] = None
        if not "author" in data:
            data["author"] = None
        if not "year" in data:
            data["year"] = None
        if not "signature" in data:
            data["signature"] = None

        dbId = db.insert('images', title=data["title"],
                                   subtitle=data["subtitle"],
                                   author=data["author"],
                                   year=data["year"],
                                   signature=data["signature"])
        return json.dumps(db.select('images', vars=locals(), where="id = $dbId")[0], cls=DateTimeEncoder)

    def OPTIONS(self, imageId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return


class image_file:

    def POST(self, imageId, imageType):
        web.header('Access-Control-Allow-Origin', '*')
        form = web.input()

        # save files at correct locations for the web tools and the server
        im = Image.open(io.StringIO(form.file))
        (width, height) = im.size
        db.update('images', vars=dict(iid=imageId), where="id = $iid", w=width, h=height)

        if imageType == "color":
            db.update('images', vars=dict(iid=imageId), where="id = $iid", web_path_color=(imageId + "-color.png"))

            # save full image
            with open('./images/' + imageId + "-color.png", 'wb') as f:
                im.convert('RGB').save(f)

            # dispatch tile creation
            subprocess.Popen(["./img2tiles.py", "./images/" + imageId + "-color.png", "../web/tiles/" +
                              imageId + "-color.png", "0"], shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)

            # create thumbnail
            thumb = ImageOps.fit(im, (500, 300), Image.ANTIALIAS, 0.0, (0.0, 0.0))
            with open("../web/thumbnails/thumb-" + imageId + "-color.png", 'wb') as f:
                thumb.convert('RGB').save(f)
        else:
            db.update('images', vars=dict(iid=imageId), where="id = $iid", web_path=(imageId + ".png"))

            # save full image
            with open('./images/' + imageId + ".png", 'wb') as f:
                im.save(f)

            # dispatch tile creation
            subprocess.Popen(["./img2tiles.py", "./images/" + imageId + ".png", "../web/tiles/" +
                              imageId + ".png", "0"], shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)

            db.update('images', vars=dict(iid=imageId), where="id = $iid", path=(imageId + ".png"))
        return json.dumps(db.select('images', dict(iid=imageId), where="id = $iid")[0], cls=DateTimeEncoder)

    def OPTIONS(self, imageId):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return


class templates:

    def GET(self, imageId):
        web.header('Access-Control-Allow-Origin', '*')
        templates = db.select('templates', dict(imageId=imageId), where="image_id = $imageId and visible = 1")
        output = [template for template in templates]
        return json.dumps(output, cls=DateTimeEncoder)

    def POST(self, imageId):
        web.header('Access-Control-Allow-Origin', '*')
        data = json.loads(web.data())
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
        args = web.input()

        # check if we have to predict labels
        if (hasattr(args, "predict") and args.predict == "true"):
            templ = db.select('templates', dict(tid=templateId), where="id = $tid")[0]
            tid = templateId
            # TODO: check for correct collection?
            matchesAndLabels = db.query("SELECT m.*, t.glyph, l.label_value FROM templates t, matches m LEFT OUTER JOIN labels l ON l.match_id = m.id " +
                                        "WHERE m.template_id = t.id AND t.id = $tid",
                                        vars=locals())
            matches = [match for match in matchesAndLabels]
            for match in matches:
                if templ.thresh_score == None:
                    match.label_value = None
                elif match.label_value != "user_positive" and match.label_value != "user_negative":
                    match.label_value = (0 if templ.thresh_score <= match.score else 1)
            return json.dumps(matches, cls=DateTimeEncoder)

        # else, do template matching
        images = [image for image in db.query(
            "SELECT i.* FROM images i, collections_images ci WHERE i.id = ci.image_id AND ci.collection_id = $cid", vars=dict(cid=collectionId))]
        templ = db.select('templates', dict(tid=templateId), where="id = $tid")[0]

        # save template to disk, if not external
        if templ.x != None and templ.y != None:
            template_image = db.select('images', dict(iid=templ.image_id), where="id = $iid")[0]
            # saving image to global dict to speed things up. BEWARE: race conditions?
            if (template_image.id not in imageList):
                im = Image.open('./images/' + template_image.path)
                im.load()
                imageList[template_image.id] = im
                print(("adding " + str(template_image.id) + " to dict"))
            im = imageList[template_image.id]
            im.crop((templ.x, templ.y, templ.x + templ.w, templ.y + templ.h)).save("templates/" + str(templ.id) + ".png", "PNG")

        # run template matching processes in separate thread
        processes = {}
        for image in images:
                # check whether we have matches for this template and this image already
            if (db.query("SELECT COUNT(*) FROM matches WHERE image_id = $iid AND template_id = $tid", vars=dict(iid=image.id, tid=templateId))[0]['COUNT(*)'] > 0):
                continue

            # otherwise, do the actual template matching by calling the external library
            process = subprocess.Popen(
                ["./match", './images/' + image.path, './templates/' +
                    str(templ.id) + ".png", str(maxResults)],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            out, err = process.communicate()
            errcode = process.returncode
            if errcode != 0:
                print("Error during template matching")
                continue
            matches = json.loads(out)
            t = db.transaction()
            for match in matches:
                db.insert('matches', image_id=image.id, template_id=templateId, x=match["x"], y=match["y"],
                          w=match["w"], h=match["h"], score=match["score"], rank=match["rank"])
            t.commit()

        # get matches again from DB so we return all the ids (and all matches that have been there before)
        finalMatches = [finalMatch for finalMatch in db.query(
            "SELECT DISTINCT m.* FROM matches m, images i, collections_images ci WHERE i.id = ci.image_id AND ci.collection_id = $cid AND m.template_id = $tid",
            vars=dict(cid=collectionId, tid=templateId))]
        return json.dumps(finalMatches, cls=DateTimeEncoder)

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
        args = web.input()
        web.header('Access-Control-Allow-Origin', '*')
        if (int(args.x2) - int(args.x1) <= 0 or int(args.y2) - int(args.y1) <= 0):
            return web.badrequest("Requested crop has no width or height.")

        web.header('Content-type', 'image/png')

        # get image from database
        image = db.select('images', dict(iid=imageId), where="id = $iid")[0]

        # saving image to global dict to speed things up
        if (imageId not in imageList):
            im = Image.open('./images/' + image.path)
            im.load()
            imageList[imageId] = im
            print(("adding " + imageId + " to dict"))
        im = imageList[imageId]
        buf = io.StringIO()
        im.crop((int(args.x1), int(args.y1), int(
            args.x2), int(args.y2))).save(buf, "PNG")
        contents = buf.getvalue()
        return contents


class matchcrop:

    def GET(self, imageId, templateId, matchId):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-type', 'image/png')
        args = web.input()

        # get image from database
        image = db.select('images', dict(iid=imageId), where="id = $iid")[0]

        # saving image to global dict to speed things up
        if (imageId not in imageList):
            im = Image.open('./images/' + image.path)
            im.load()
            imageList[imageId] = im
            print(("adding " + imageId + " to dict"))
        im = imageList[imageId]

        # get match from database
        match = db.select('matches', dict(iid=imageId, tid=templateId, mid=matchId),
                          where="id = $mid AND template_id = $tid AND image_id = $iid")[0]

        # crop image of desired size
        margin_top = int(args.margin_top)
        margin_left = int(args.margin_left)
        margin_right = int(args.margin_right)
        margin_bottom = int(args.margin_bottom)
        im_cropped = im.crop((match.x - margin_left,
                              match.y - margin_top,
                              match.x + match.w + margin_right,
                              match.y + match.h + margin_bottom))

        # draw rectangle around template if desired
        if (hasattr(args, "box") and args.box == "true"):
            im_cropped = im_cropped.convert("RGBA")
            draw = ImageDraw.Draw(im_cropped)
            draw.rectangle([(margin_left, margin_top),
                            (margin_left + match.w, margin_top + match.h)],
                           outline=(255, 0, 0, 200))

        # save image to buffer and return
        buf = io.StringIO()
        im_cropped.save(buf, "PNG")
        contents = buf.getvalue()
        return contents

    

class DateTimeEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
    
# define ressource paths
urls = (
#     '/api/', 'index',
#     '/api/images/(.*)/templates/(.*)/matches/(.*)/label', 'matchlabel',
#     '/api/images/(.*)/templates/(.*)/matches/(.*)/crops', 'matchcrop',
#     '/api/images/(.*)/templates/(.*)/matches/(.*)/select', 'matchselect',
#     '/api/images/(.*)/templates/(.*)/matches/(.*)', 'match',
#     '/api/images/(.*)/templates/(.*)/matches', 'matches',
#     '/api/images/(.*)/templates/(.*)/model', 'model',
#     '/api/images/(.*)/templates/(.*)/typography', 'typography',
#     '/api/images/(.*)/templates/(.*)', 'template',
#     '/api/images/(.*)/templates', 'templates',
#     '/api/images/(.*)/crops', 'crop',
#     '/api/images/(.*)/(color|binarized)', 'image_file',
#     '/api/images/(.*)/synthetic_pages', 'synthetic_pages',
#     '/api/images/(.*)', 'image',
#     '/api/images', 'images',
#     '/api/collections/(.*)/templates/(.*)/matches', 'collection_matches',
#     '/api/collections/(.*)/templates/(.*)', 'collection_template',
#     '/api/collections/(.*)/templates', 'collection_templates',
#     '/api/collections/(.*)/images', 'collection_images',
#     '/api/collections/(.*)/synthetic_pages', 'collection_synthetic_pages',
     '/api/collections/(.*)', 'collection',
    '/api/collections', 'collections',
#     '/api/memberships', 'memberships',
     '/api/ping', 'PingHandler'
)

# DEBUG: inspect the structure of urls
with open("/tmp/debug-urls.txt", "w") as f:
    f.write(f"Type of urls: {type(urls)}\n")
    for i, item in enumerate(urls):
        f.write(f"urls[{i}] = {repr(item)} (type: {type(item)})\n")


# import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
with open(f"./debug-handler-scope-{timestamp}.log", "w") as f:
    f.write(f"'PingHandler' in globals(): {'PingHandler' in globals()}\n")
    
print(f">>> collections_handler has methods: {dir(collections_handler)}", flush=True)

handler_map = {
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


import datetime
ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
with open(f"./handler-map-debug-{ts}.log", "w") as debug_file:
    handler = handler_map.get("PingHandler", None)
    debug_file.write(f"PingHandler in handler_map: {'PingHandler' in handler_map}\n")
    debug_file.write(f"handler_map['PingHandler']: {repr(handler)}\n")
    debug_file.write(f"type: {type(handler)}\n")

print(f">>> collections_handler has POST: {'POST' in dir(collections_handler)}", flush=True)

#app = web.application(urls, globals())
app = web.application(urls, handler_map)

# 🐒 Monkey-patch the web.application class
original_delegate = web.application._delegate

def patched_delegate(self, f, fvars, args=[]):
    print(">>> 🐒 Monkey-patched _delegate called <<<", flush=True)
    print(f"[DEBUG] f = {f} (type: {type(f)})", flush=True)
    print(f"[DEBUG] fvars keys = {list(fvars.keys())}", flush=True)
    return original_delegate(self, f, fvars, args)

web.application._delegate = patched_delegate

# ✅ Now assign the WSGI callable

application = app.wsgifunc()


import datetime
ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
with open(f"./debug-application-object-{ts}.log", "w") as debug_file:
    debug_file.write(f"type(application): {type(application)}\n")
    debug_file.write(f"dir(application): {dir(application)}\n")

if hasattr(collections_handler, "POST"):
    print(">>> YES: collections_handler.POST exists", flush=True)
else:
    print(">>> NO: collections_handler.POST is missing", flush=True)


if __name__ == "__main__":
    app.run()
    
