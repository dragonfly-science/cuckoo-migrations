DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cuckoo.sqlite',
        # We need to specify a TEST_NAME because an in-memory
        # sqlite3 db for migrations won't work
        'TEST_NAME': 'cuckoo_test.sqlite',
    }
}

INSTALLED_APPS = ['cuckoo', 'species']
