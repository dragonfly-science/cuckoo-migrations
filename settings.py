DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cuckoo_test',
    }
}

INSTALLED_APPS = ['cuckoo', 'species']

SECRET_KEY = 'dummy'
