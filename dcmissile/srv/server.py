import os
import sys

from twisted.application import internet, service
from twisted.web import server, wsgi, static
from twisted.python import threadpool
from twisted.internet import reactor

current_dir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.abspath(os.path.join(current_dir, "..", ".."))

sys.path.append(basedir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'dcmissile.settings'

from django.conf import settings

PORT = settings.WWWPORT

from django.core.handlers.wsgi import WSGIHandler

from dcmissile.srv import twresource


def wsgi_resource():
    pool = threadpool.ThreadPool()
    pool.start()
    # Allow Ctrl-C to get you out cleanly:
    reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
    wsgi_resource = wsgi.WSGIResource(reactor, pool, WSGIHandler())
    return wsgi_resource


application = service.Application('twisted-django')

wsgi_root = wsgi_resource()
root = twresource.Root(wsgi_root)

media_dir = os.path.abspath(os.path.join(current_dir, "../media"))
mediarsrc = static.File(media_dir)
root.putChild("media", mediarsrc)

static_dir = os.path.abspath(os.path.join(current_dir, "../static"))
staticrsrc = static.File(static_dir)
root.putChild("static", staticrsrc)

# Serve it up:
main_site = server.Site(root)
if __name__ == '__main__':
    reactor.listenTCP(PORT, main_site)
    reactor.run()
else:
    internet.TCPServer(PORT, main_site).setServiceParent(application)
