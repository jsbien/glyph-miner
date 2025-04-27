# coding: utf-8
from server.webapp import webapp

class server:
    def GET(self):
        return "Main page loaded."

    def __call__(self):
        return self.GET()

class loader:
    def POST(self):
        return "Loader not implemented yet."

    def __call__(self):
        return self.POST()

class saver:
    def POST(self):
        return "Saver not implemented yet."

    def __call__(self):
        return self.POST()

class uploader:
    def POST(self):
        return "Uploader not implemented yet."

    def __call__(self):
        return self.POST()

class adder:
    def POST(self):
        return "Adder not implemented yet."

    def __call__(self):
        return self.POST()

class remover:
    def POST(self):
        return "Remover not implemented yet."

    def __call__(self):
        return self.POST()

# URL mapping
urls = [
    ('/', server()),
    ('/load', loader()),
    ('/save', saver()),
    ('/upload', uploader()),
    ('/add', adder()),
    ('/remove', remover()),
]

# Create WSGI app
app = webapp.application(urls, globals())
