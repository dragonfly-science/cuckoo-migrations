"""
This module provides a way to get db shell commands, similar to
what `./manage.py dbshell` will provide. This functionality is provided in the
core django library in modules such as
`django.db.backends.sqlite3.client.DatabaseClient`. Unfortunately these do not
encapsulate the creation of the command string, and terminate the process with 
`os.execvp`. Thus there is no way to get the command or a pipe to it using the
existing code. Instead, we duplicate the command string building here.

NOTE: Unlike psql, mysql and sqlite3 do not allow you to specify a file
to load statements from, instead it expects to have stdin
redirected using '< statements.sql'
"""
from django.conf import settings

def get_postgresql_command(settings_dict):
    args = ['psql'] # executable
    # TODO: What does this do?
    args.append('--set ON_ERROR_STOP=1')
    if settings_dict['USER']:
        args += ["-U", settings_dict['USER']]
    if settings_dict['HOST']:
        args.extend(["-h", settings_dict['HOST']])
    if settings_dict['PORT']:
        args.extend(["-p", str(settings_dict['PORT'])])
    args += [settings_dict['NAME'], '-f', '%s']
    return ' '.join(args)

def get_sqlite3_command(settings_dict):
    return 'sqlite3 ' + settings_dict['NAME'] + ' < %s'

def get_mysql_command(settings_dict):
    """
    This is taken directly from
    `django.db.backends.mysql.client.DatabaseClient`.
    No idea if it works!
    """
    args = [self.executable_name]
    db = settings_dict['OPTIONS'].get('db', settings_dict['NAME'])
    user = settings_dict['OPTIONS'].get('user', settings_dict['USER'])
    passwd = settings_dict['OPTIONS'].get('passwd', settings_dict['PASSWORD'])
    host = settings_dict['OPTIONS'].get('host', settings_dict['HOST'])
    port = settings_dict['OPTIONS'].get('port', settings_dict['PORT'])
    defaults_file = settings_dict['OPTIONS'].get('read_default_file')
    # Seems to be no good way to set sql_mode with CLI.

    if defaults_file:
        args += ["--defaults-file=%s" % defaults_file]
    if user:
        args += ["--user=%s" % user]
    if passwd:
        args += ["--password=%s" % passwd]
    if host:
        if '/' in host:
            args += ["--socket=%s" % host]
        else:
            args += ["--host=%s" % host]
    if port:
        args += ["--port=%s" % port]
    if db:
        args += [db]

    args += ['< %s']

    return ' '.join(args)

def get_db_shell_cmd(db_name, exists, dba):
    # If defined explicitly in settings, use that
    env = settings.DATABASES[db_name]

    if not exists:
        env['NAME'] = 'postgres'
    if dba or not exists:
        env['USER'] = 'dba'

    db_cmd_func = _get_db_command_function(env)
    if db_cmd_func is None:
        raise NotImplementedError(
                "Cuckoo doesn't know about db engine %s" % env['ENGINE'])
    return db_cmd_func(env)

def _get_db_command_function(env):
    db_type_functions = {
            'postgresql_psycopg2': get_postgresql_command,
            'sqlite3': get_sqlite3_command,
            'mysql': get_mysql_command,
            }
    engine = env['ENGINE'].split('.')[-1]
    return db_type_functions.get(engine, None)
