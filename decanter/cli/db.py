import os
import sys
from getpass import getpass

from cement.core import controller
from decanter.database import db

import decanter


class InstallDBController(controller.CementBaseController):

    class Meta:
        label = 'installdb'
        description = "Install the decanter database."
        arguments = [
            (['-c', '--connection'], {
                'action': 'store',
                'help': 'Connection string to use for the database connection',
                'default': 'postgresql://localhost/decanter',
            }),
            (['-s', '--schema'], {
                'action': 'store',
                'help': 'Schema to install into',
                'default': 'public',
            }),
        ]

    @controller.expose(hide=True, help='Install the database')
    def default(self):
        connection = self.pargs.connection

        db.init_connection({
            'SQLALCHEMY_DATABASE_URI': connection,
            'SQLALCHEMY_ECHO': True
        })

        try:
            schema = self.pargs.schema

            drop = 'DROP SCHEMA IF EXISTS "%s" CASCADE;'
            drop %= schema

            db.session.execute(drop)
            db.session.execute('CREATE SCHEMA "%s";' % schema)
            db.session.execute('SET search_path TO "%s";' % schema)
            db.session.execute(self.sql())
            db.session.commit()
        finally:
            db.session.remove()

    def sql(self):
        sql = self.load_sql('all.sql')
        sql += self.load_sql('extensions.sql')
        return sql

    def load_sql(self, *path):
        with open(os.path.join(decanter.DIR, 'sql', *path), 'r') as fd:
            return ''.join(fd.readlines())


class CreateRoleController(controller.CementBaseController):

    class Meta:
        label = 'create_role'
        description = "Install the decanter database."
        arguments = [
            (['-c', '--connection'], {
                'action': 'store',
                'help': 'Connection string to use for the database connection',
                'default': 'postgresql://localhost/decanter',
            }),
            (['-s', '--schema'], {
                'action': 'store',
                'help': 'Schema to install into',
                'default': 'public',
            }),
        ]

    @controller.expose(hide=True, help='Add a role to the database.')
    def default(self):
        from decanter.api.interface import role
        connection = self.pargs.connection

        db.init_connection({
            'SQLALCHEMY_DATABASE_URI': connection,
            'SQLALCHEMY_ECHO': True
        })

        sys.stdout.write('Role Name: ')
        name = raw_input().strip()

        sys.stdout.write('Role Description: ')
        description = raw_input().strip()

        role.create(name, description)


class CreateUserController(controller.CementBaseController):

    class Meta:
        label = 'create_user'
        description = "Install the decanter database."
        arguments = [
            (['-c', '--connection'], {
                'action': 'store',
                'help': 'Connection string to use for the database connection',
                'default': 'postgresql://localhost/decanter',
            }),
            (['-s', '--schema'], {
                'action': 'store',
                'help': 'Schema to install into',
                'default': 'public',
            }),
        ]

    @controller.expose(hide=True, help='Add a user to the database.')
    def default(self):
        from decanter.api.interface import user, role
        connection = self.pargs.connection

        db.init_connection({
            'SQLALCHEMY_DATABASE_URI': connection,
            'SQLALCHEMY_ECHO': True
        })

        sys.stdout.write('Username: ')
        username = raw_input().strip()

        sys.stdout.write('Email: ')
        email = raw_input().strip()

        while True:
            password = getpass('Enter password: ')
            password_2 = getpass('Reenter password: ')

            if password != password_2:
                sys.stdout.write('Passwords must match!\n\n')
                continue
            break

        while True:
            sys.stdout.write('Comma Separated List of User Roles: ')
            rs = raw_input().strip()
            roles = list()
            success = True
            for r in rs.split(','):
                r = r.strip()
                ro = role.get_by_name(r)
                if not ro:
                    success = False
                    sys.stdout.write('Unknown role: %s\n\n' % r)
                    continue
                roles.append(ro)
            if success:
                break

        usr = user.create(username, email, password, roles=roles)
        print "User %s created" % usr
