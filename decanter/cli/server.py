import os
import signal
from cement.core import controller, exc
from flask import Flask


class ServerController(controller.CementBaseController):

    class Meta:
        label = 'runserver'
        description = "Run the flask development server"
        arguments = [
            (['-d', '--debugger'], {
                'action': 'store_true',
                'help': 'Run the server with the debugger enabled'
            }),
            (['-r', '--reload'], {
                'action': 'store_true',
                'help': 'Run the server with the reloader enabled'
            }),
        ]

    @controller.expose(hide=True, help='Run the flask development server')
    def default(self):
        self.run(getattr(self, 'flask_app'),
                 use_debugger=self.pargs.debugger,
                 use_reloader=self.pargs.reload)

    def run(self, app, **kw):
        kw.setdefault('host', os.environ.get('HOST', '0.0.0.0'))
        kw.setdefault('port', int(os.environ.get('PORT', 5000)))
        a = Flask(__name__)
        a.wsgi_app = app

        while True:
            try:
                a.run(**kw)
            except exc.CaughtSignal, e:
                if e.signum != signal.SIGHUP:
                    return
