import sys

from gevent.pywsgi import WSGIServer
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config

from windmills.core import Crate, Shaft

__author__ = 'Raul Gonzalez'


class WebEmitter(Shaft):
    def __init__(self, **kwargs):
        Shaft.__init__(self, **kwargs)
        self.cargo = self.declare_cargo()

        # wsgi server
        self._wsgi_server = None

    def appctx(self):
        return self

    def configuration_options(self, arg_parser=None):
        assert arg_parser

    def configure(self, args=list()):
        assert args
        config = Configurator()
        config.include('pyramid_jinja2')
        config.add_jinja2_search_path('windmills.web_service:templates')
        config.add_static_view('static', 'static', cache_max_age=3600)
        config.add_request_method(self.appctx)
        config.add_route('hello', '/hello')
        config.add_view(self.hello_world, route_name='hello')
        config.add_route('root_url', '/')
        config.add_view(self.root_url, route_name='root_url', renderer='web_emitter.jinja2')
        app = config.make_wsgi_app()
        self._wsgi_server = WSGIServer(('', 8000), app)
        self._wsgi_server.serve_forever()

    def run_loop(self):
        self.log.info('... Entering run loop ...')

    def root_url(self, request):
        return {'key': 'value'}

    def hello_world(self, request):
        request.appctx().log.debug('request: %s', request)
        return Response('Hello World')


if __name__ == '__main__':
    argv = sys.argv
    ui_emitter = WebEmitter(argv=argv)
    ui_emitter.run()