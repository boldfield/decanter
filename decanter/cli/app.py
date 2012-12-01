from cement.core import foundation, handler
from decanter.cli.root import RootController


class App(foundation.CementApp):

    @classmethod
    def execute(cls, *args, **kw):
        meta = getattr(cls, 'Meta', None)
        base = getattr(meta, 'base_controller', RootController)
        kw.setdefault('base_controller', base)
        app = cls(*args, **kw)

        try:
            app.register()
            app.setup()
            app.run()
        finally:
            app.close()

        return app

    def register(self):
        meta = getattr(self, '_meta', None)
        handlers = getattr(meta, 'handlers', None) or []
        self.register_handler(*handlers)

    def register_handler(self, *handlers):
        for h in handlers:
            handler.register(h)
