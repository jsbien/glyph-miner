import web

# Dummy implementations for now — replace with real logic later
def server(): return lambda: "Main server root"
def loader(): return lambda: "Loading..."
def saver(): return lambda: "Saving..."
def uploader(): return lambda: "Uploading..."
def adder(): return lambda: "Adding..."
def remover(): return lambda: "Removing..."

urls = [
    ('/api/', server()),
    ('/api/load', loader()),
    ('/api/save', saver()),
    ('/api/upload', uploader()),
    ('/api/add', adder()),
    ('/api/remove', remover()),
]

app = web.application(urls, globals())
application = app.wsgifunc()
