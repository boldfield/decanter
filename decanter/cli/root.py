from cement.core.controller import CementBaseController, expose


class RootController(CementBaseController):
    class Meta:
        label = 'base'

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()
