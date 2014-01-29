import sys

from gevent.pywsgi import WSGIServer
from pyramid.config import Configurator
from pyramid.response import Response

from windmills.core import Crate, Shaft

__author__ = 'Raul Gonzalez'


def app_ctx_enabled(contexts=list()):
    def func_handler(func):
        def func_wrapper(request):
            appctx = request.appctx()
            log = appctx.log

            # Retrieve any additional contexts
            args = list()
            for context in contexts:
                args.append(getattr(appctx, context))

            return func(request, appctx, log, *args)

        return func_wrapper

    return func_handler


class WebEmitter(Shaft):
    def __init__(self, **kwargs):
        # wsgi server
        self._wsgi_server = None

        print 'pre configure shaft'
        Shaft.__init__(self, **kwargs)
        print 'post configure shaft'

        self.cargo = self.declare_cargo()


    def appctx(self):
        return self

    def configuration_options(self, arg_parser=None):
        assert arg_parser

    def configure(self, args=list()):
        assert args

        # Override the jinja2 template default comment and variable tags
        # so that is doesn't conflict with the Handlebar tags.
        config = Configurator(settings={
            'jinja2.comment_start_string': '(#',
            'jinja2.comment_end_string': '#)',
            'jinja2.variable_start_string': '((',
            'jinja2.variable_end_string': '))',
        })

        # Configure jinja
        config.include('pyramid_jinja2')
        config.add_jinja2_search_path('windmills.web_service:templates')

        # Configure static views.
        config.add_static_view('static', 'static', cache_max_age=3600)

        # Configure a request method to access application context
        config.add_request_method(self.appctx)

        # Configure Route and View combinations
        config.add_route('root_url', '/')
        config.add_view(self.root_url, route_name='root_url', renderer='web_emitter.jinja2')
        config.add_route('send_msg', '/send_message')
        config.add_view(self.send_msg, route_name='send_msg', request_method='POST',
                        renderer='json', accept='application/json')

        # Generate the app and start the server.
        app = config.make_wsgi_app()
        self._wsgi_server = WSGIServer(('', 8000), app)
        self._wsgi_server.start()  # todo: raul - need to make this non blocking

    def run_loop(self):
        self.log.info('... Entering run loop ...')

    @staticmethod
    def root_url(request):
        return {'key': '(Jinja2 Test String)'}

    @staticmethod
    @app_ctx_enabled(['cargo'])
    def send_msg(request, appctx, log, cargo):
        log.debug('request.body: %s', request.body)

        crate = Crate(msg_data=request.body)
        cargo.send(crate)

        return Response(status=200)


if __name__ == '__main__':
    argv = sys.argv
    ui_emitter = WebEmitter(argv=argv)
    ui_emitter.run()
