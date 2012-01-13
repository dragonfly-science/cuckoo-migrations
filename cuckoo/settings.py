import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cuckoo.sqlite'
    }
}

INSTALLED_APPS = ['cuckoo',]

CUCKOO_DIRECTORY = 'test_patches'

