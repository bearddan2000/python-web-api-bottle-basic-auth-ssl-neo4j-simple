from bottle import (
    auth_basic,
    request,
    route,
    run,
    ServerAdapter,
    default_app,
)
from beaker.middleware import SessionMiddleware

import logging
from model import DbModel

logging.basicConfig(level=logging.INFO)

neo = DbModel()

def is_authenticated_user(user, password):
    # You write this function. It must return
    # True if user/password is authenticated, or False to deny access.
	if user == 'user' and password == 'pass':
		return True
	return False

@route('/')
def smoke_test():
    cipher = 'UNWIND range(1, 3) AS n RETURN n, n * n as n_sq'
    d = neo.connect().run(cipher).data()
    return {'results': d}

@route('/dog')
@auth_basic(is_authenticated_user)
def get_all():
    return neo.get_all()

@route('/dog/name/<name>')
@auth_basic(is_authenticated_user)
def filter_by_name(name: str):
    return neo.filter_by_name(name)

@route('/dog/breed/<breed>')
@auth_basic(is_authenticated_user)
def filter_by_breed(breed: str):
    return neo.filter_by_breed(breed)

@route('/dog/color/<color>')
@auth_basic(is_authenticated_user)
def filter_by_color(color: str):
    return neo.filter_by_color(color)

class SSLCherootAdapter(ServerAdapter):
    def run(self, handler):
        from cheroot import wsgi
        from cheroot.ssl.builtin import BuiltinSSLAdapter
        import ssl

        server = wsgi.Server((self.host, self.port), handler)
        server.ssl_adapter = BuiltinSSLAdapter("./server.crt", "./server.key")

        try:
            server.start()
        finally:
            server.stop()


# define beaker options
# -Each session data is stored inside a file located inside a
#  folder called data that is relative to the working directory
# -The cookie expires at the end of the browser session
# -The session will save itself when accessed during a request
#  so save() method doesn't need to be called
session_opts = {
    "session.type": "file",
    "session.cookie_expires": True,
    "session.data_dir": "./data",
    "session.auto": True,
}

# Create the default bottle app and then wrap it around
# a beaker middleware and send it back to bottle to run
app = SessionMiddleware(default_app(), session_opts)

if __name__ == "__main__":
    run(app=app, host="0.0.0.0", port=443, server=SSLCherootAdapter)
