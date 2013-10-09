from distutils.core import setup

setup(name = "cuckoo",
    version = "1.2",
    description = "Simple migrations for Django",
    author = "Edward Abraham",
    author_email = "edward@dragonfly.co.nz",
    url = "https://github.com/dragonfly-science/cuckoo",
    packages = ['cuckoo', 'cuckoo.management', 'cuckoo.management.commands'],
    scripts = ['scripts/cuckoo'],
) 
