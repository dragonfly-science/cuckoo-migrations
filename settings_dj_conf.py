from configurations import Configuration, values


class Local(Configuration):
    DATABASES = values.DatabaseURLValue('postgresql://localhost/cuckoo_test_2')
    INSTALLED_APPS = ('cuckoo', 'species')
    SECRET_KEY = 'NOT THIS!!!'
