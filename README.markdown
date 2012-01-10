**Cuckoo**

Cuckoo is a simple django app for assisting with database migration.

There is no clever trickiness, for that you should be using [South](http://south.aeracode.org).
It works as follows:
    - You write some sql patches
    - Put them in a directory
    - Run ./manage.py cuckoo to execute any patches that haven't yet been run

** Installation

** Get the code
Try running
pip install cuckoo

** Modify your django settings file
    - Add 'cuckoo' to your INSTALLED_APPS
    - Make a directory, say 'patches', to hold your patches
    - Add the a string 'PATCHES_PATH to settings that holds the full path to the patches 
        directory, e.g., PATCHES_PATH = '/home/edward/django/www/patches'
    - Run ./manage.py syncdb, or pipe the output from './manage.py sql cuckoo' at your database 

** What it does
    
When you install cuckoo, it creates a table 'cuckoo_patch' in your database. This table
holds a record of the patches that have been run. A Patch object has the fields
    - patch: The filename of the patch (must be unique)
    - 


**



