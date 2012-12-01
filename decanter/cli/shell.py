from cement.core import controller


class ShellController(controller.CementBaseController):
    class Meta:
        label = 'shell'
        description = "Opens a bpython, ipython or python interactive shell."

        epilog = "By default, the first interpreter found is used. The " \
                 "order of look up is bpython, ipython, python. You can " \
                 "specify a specific interpreter as a subcommand or as a " \
                 "flag."

        arguments = [
            (['-b', '--bpython'], {
                'action': 'store_true',
                'help': 'Run bpython shell'
            }),
            (['-i', '--ipython'], {
                'action': 'store_true',
                'help': 'Run ipython shell'
            }),
            (['-p', '--python'], {
                'action': 'store_true',
                'help': 'Run python shell'
            })
        ]

    @controller.expose(hide=True, help='Run an interactive shell')
    def default(self):
        if self.pargs.bpython:
            return self.bpython()

        if self.pargs.ipython:
            return self.ipython()

        if self.pargs.python:
            return self.python()

        shell = self.shell()

        if shell:
            return shell()

        print 'Interactive shell not found.'

    def shell(self):
        for fn in [self.bpy, self.ipy, self.py]:
            shell = fn()
            if shell:
                return shell

    @controller.expose(help='Run bpython shell')
    def bpython(self):
        shell = self.bpy()
        if not shell:
            print 'bpython is not available.'
        else:
            shell()

    def bpy(self):
        try:
            from bpython.cli import main as bpython_main
            return lambda: bpython_main(args=[])
        except ImportError:
            pass

    @controller.expose(help='Run ipython shell')
    def ipython(self):
        shell = self.ipy()
        if not shell:
            print 'ipython is not available.'
        else:
            shell()

    def ipy(self):
        try:
            from IPython.frontend.terminal import ipapp
            app = ipapp.TerminalIPythonApp.instance()
            app.initialize([])
            return app.start
        except ImportError:
            pass

    @controller.expose(help='Run python shell')
    def python(self):
        shell = self.py()
        if not shell:
            print 'python is not available.'
        else:
            shell()

    def py(self):
        try:
            import code
            return code.InteractiveConsole(locals=globals()).interact
        except ImportError:
            pass
