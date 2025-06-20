"""openid.py: an openid library for webapp.py

Notes:

 - This will create a file called .openid_secret_key in the 
   current directory with your secret key in it. If someone 
   has access to this file they can log in as any user. And 
   if the app can't find this file for any reason (e.g. you 
   moved the app somewhere else) then each currently logged 
   in user will get logged out.

 - State must be maintained through the entire auth process 
   -- this means that if you have multiple webapp.py processes 
   serving one set of URLs or if you restart your app often 
   then log ins will fail. You have to replace sessions and 
   store for things to work.

 - We set cookies starting with "openid_".

"""

import os
import random
import hmac
from . import __init__ as webapp
import openid.consumer.consumer
import openid.store.memstore

sessions = {}
store = openid.store.memstore.MemoryStore()

def _secret():
    try:
        secret = file('.openid_secret_key').read()
    except IOError:
        # file doesn't exist
        secret = os.urandom(20)
        file('.openid_secret_key', 'w').write(secret)
    return secret

def _hmac(identity_url):
    return hmac.new(_secret(), identity_url).hexdigest()

def _random_session():
    n = random.random()
    while n in sessions:
        n = random.random()
    n = str(n)
    return n

def status():
    oid_hash = webapp.cookies().get('openid_identity_hash', '').split(',', 1)
    if len(oid_hash) > 1:
        oid_hash, identity_url = oid_hash
        if oid_hash == _hmac(identity_url):
            return identity_url
    return None

def form(openid_loc):
    oid = status()
    if oid:
        return '''
        <form method="post" action="%s">
          <img src="http://openid.net/login-bg.gif" alt="OpenID" />
          <strong>%s</strong>
          <input type="hidden" name="action" value="logout" />
          <input type="hidden" name="return_to" value="%s" />
          <button type="submit">log out</button>
        </form>''' % (openid_loc, oid, webapp.ctx.fullpath)
    else:
        return '''
        <form method="post" action="%s">
          <input type="text" name="openid" value="" 
            style="background: url(http://openid.net/login-bg.gif) no-repeat; padding-left: 18px; background-position: 0 50%%;" />
          <input type="hidden" name="return_to" value="%s" />
          <button type="submit">log in</button>
        </form>''' % (openid_loc, webapp.ctx.fullpath)

def logout():
    webapp.setcookie('openid_identity_hash', '', expires=-1)

class host:
    def POST(self):
        # unlike the usual scheme of things, the POST is actually called
        # first here
        i = webapp.input(return_to='/')
        if i.get('action') == 'logout':
            logout()
            return webapp.redirect(i.return_to)

        i = webapp.input('openid', return_to='/')

        n = _random_session()
        sessions[n] = {'webpy_return_to': i.return_to}
        
        c = openid.consumer.consumer.Consumer(sessions[n], store)
        a = c.begin(i.openid)
        f = a.redirectURL(webapp.ctx.home, webapp.ctx.home + webapp.ctx.fullpath)

        webapp.setcookie('openid_session_id', n)
        return webapp.redirect(f)

    def GET(self):
        n = webapp.cookies('openid_session_id').openid_session_id
        webapp.setcookie('openid_session_id', '', expires=-1)
        return_to = sessions[n]['webpy_return_to']

        c = openid.consumer.consumer.Consumer(sessions[n], store)
        a = c.complete(webapp.input(), webapp.ctx.home + webapp.ctx.fullpath)

        if a.status.lower() == 'success':
            webapp.setcookie('openid_identity_hash', _hmac(a.identity_url) + ',' + a.identity_url)

        del sessions[n]
        return webapp.redirect(return_to)
