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


def get_postgresql_command(settings_dict, cmd='psql'):
    args = [cmd]  # executable
    if cmd == 'psql':
        args.append('--set ON_ERROR_STOP=1')
    if settings_dict['USER']:
        args += ["-U", settings_dict['USER']]
    if settings_dict['HOST']:
        args.extend(["-h", settings_dict['HOST']])
    if settings_dict['PORT']:
        args.extend(["-p", str(settings_dict['PORT'])])
    if 'pg_restore' not in cmd:
        args += [settings_dict['NAME']]
    else:
        args.extend(['-d', settings_dict['NAME']])
    return ' '.join(args)


def get_db_shell_cmd(db_name, exists, dba, cmd='psql'):
    # If defined explicitly in settings, use that
    env = settings.DATABASES[db_name].copy()
    if not exists and cmd == 'psql':
        env['NAME'] = 'postgres'
    if dba or not exists:
        env['USER'] = 'dba'

    db_cmd_func = _get_db_command_function(env)
    if db_cmd_func is None:
        raise NotImplementedError(
            "Cuckoo doesn't know about db engine %s" % env['ENGINE'])
    return db_cmd_func(env, cmd)


def _get_db_command_function(env):
    db_type_functions = {
        'postgresql_psycopg2': get_postgresql_command,
        'postgis': get_postgresql_command,
    }
    engine = env['ENGINE'].split('.')[-1]
    return db_type_functions.get(engine, None)
