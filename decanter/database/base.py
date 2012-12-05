import psycopg2
import psycopg2.extras

from decanter import sqla as sqlalchemy


class Database(sqlalchemy.Database):

    def apply_driver_hacks(self, info, options):
        """This method adds option to support hstore on psycopg2"""

        creator = 'create_%s_connection' % info.drivername
        creator = getattr(self, creator, None)

        if hasattr(creator, '__call__'):
            def _connect():
                return creator(info, options)
            options['creator'] = _connect

        super(Database, self).apply_driver_hacks(info, options)

    def create_postgres_connection(self, info, options):
        conn = psycopg2.connect(user=info.username,
                                host=info.host,
                                port=info.port,
                                dbname=info.database,
                                password=info.password)
        psycopg2.extras.register_hstore(conn)
        return conn
