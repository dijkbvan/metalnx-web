#!/usr/bin/python
import sys
from os import path, stat
import platform
import psycopg2 as postgres
import MySQLdb as mysql


# MySQLdb lib
# Windows: exe
# yum install mysql-python
# apt-get install python-mysqldb

class MetalnxContext:
    def __init__(self):
        self.jar_path = '/usr/bin/jar'
        self.tomcat_home = '/usr/share/tomcat'
        self.db_type = ''
        self.db_host = ''
        self.db_name = ''
        self.db_user = ''
        self.db_pwd = ''
        pass

    def config_java_devel(self):
        '''It will make sure the java-devel package is correctly installed'''
        stat(self.jar_path)
        return True

    def config_tomcat_home(self):
        '''It will ask for your tomcat home directory and checks if it is a valid one'''
        self.tomcat_home = raw_input('Enter your Tomcat home directory [{}]: '.format(self.tomcat_home))

        # Getting bin/ and webapps/ dirs for current installation of Tomcat
        self.tomcat_bin_dir = path.join(self.tomcat_home, 'bin')
        self.tomcat_webapps_dir = path.join(self.tomcat_home, 'webapps')

        # If all paths are valid, then this is a valid tomcat directory
        if path.exists(self.tomcat_home) and path.isdir(self.tomcat_home) \
                and path.exists(self.tomcat_bin_dir) and path.isdir(self.tomcat_bin_dir) \
                and path.exists(self.tomcat_webapps_dir) and path.isdir(self.tomcat_webapps_dir):
            return True

        raise Exception('Tomcat directory is not valid. Please check the path and try again.')

    def config_database(self):
        """It will configure database access"""

        self._is_host_reachable(self.db_host)
        self._test_database_connection(self, self.db_type, self.db_host, self.db_user, self.db_pwd, self.db_name)

    def _is_host_reachable(self, host):
        ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
        return os.system("ping " + ping_str + " " + host) == 0

    def _test_database_connection(self, db_type, db_host, db_user, db_pwd, db_name):
        db_connect_dict = {
            'mysql': self._connect_mysql,
            'postgres': self._connect_postgres
        }

        db_connect_dict[db_type](db_host, db_user, db_pwd, db_name)
        return True

    def _connect_mysql(self, db_host, db_user, db_pwd, db_name):
        mysql.connect(db_host, db_user, db_pwd, db_name).close()

    def _connect_postgres(self, db_host, db_user, db_pwd, db_name):
        postgres.connect(host=db_host, user=db_user, password=db_pwd, database=db_name).close()


    def run(self):
        '''
        Runs Metalnx configuration
        '''
        print self._banner()

        # Filtering out method that does not start with 'config_'
        methods_to_run = [m for m in dir(self) if m.startswith('config_')]

        for step, method in enumerate(methods_to_run):
            invokable = getattr(self, method)
            print '[*] Executing {} ({}/{})\n   - {}'.format(method, step + 1, len(methods_to_run), invokable.__doc__)

            try:
                invokable()
            except Exception as e:
                print '[ERROR]: {}'.format(e)
                sys.exit(-1)

        sys.exit(0)

    def _banner(self):
        main_line = '#          Metalnx Installation Script        #'
        return '#' * len(main_line) + '\n' + main_line + '\n' + '#' * len(main_line)


def main():
    MetalnxContext().run()


if __name__ == '__main__':
    main()
