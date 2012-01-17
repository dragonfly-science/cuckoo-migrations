import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cuckoo.sqlite'
    }
}

# cuckoo is the main app, and species is a simple app used for testing
INSTALLED_APPS = ['cuckoo', 'species']

