# Cuckoo

Cuckoo is a simple django app for assisting with database migration.


There is no clever trickiness, magic, or other intelligence to automatically
generate your sql. For that you should be using
[South](http://south.aeracode.org). With cuckoo, you write sql patches, and the
application is only used to keep track of which have already been applied.  We
use cuckoo because we have messed with the django permissions system, in a way
that has somehow broken south. You might use it because you like to hand-roll
your sql.

Cuckoo works as follows:
 
 1. You write some sql patches
 2. Put them in a directory
 3. Run `./manage.py cuckoo` to execute any patches that haven't yet been run

## Installation

### Get the code

The easiest way is to use the `pip` installer:

    pip install git+ssh://git@github.com/dragonfly-science/cuckoo.git


### Modify your django settings file
 1. Add `cuckoo` to your `INSTALLED_APPS`
 2. Make a directory, by default `sql-patches`, to hold your patches
 3. Optionally, add a string `CUCKOO_DIRECTORY` to settings that holds the full path to the patches 
        directory, e.g., `CUCKOO_DIRECTORY = '/home/edward/django/www/patches'`
 4. Run ./manage.py syncdb, or pipe the output from `./manage.py sql cuckoo` at your database 

## Usage
    
When you install cuckoo, it creates a table 'cuckoo_patch' in your database. This table
holds a record of the patches that have been run. A Patch object has the fields
    - patch: The filename of the patch (must be unique)
    - 


**


## The shining cuckoo

The [shining cuckoo](http://en.wikipedia.org/wiki/Shining_Bronze_Cuckoo) 
migrates from  the Solomon Islands, Papua Guinea region to New Zealand in the spring. It breeds in New Zealand in the summer. It has a distinctive call, and is often heard, but rarely seen. So, cuckoo is for small beautiful migrations that you only notice if you pay attention.

![Shining cuckoo](http://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Chrysococcyx_lucidus_-_Meehan_Range.jpg/220px-Chrysococcyx_lucidus_-_Meehan_Range.jpg "Shining cuckoo, cc photograph by JJ Harrison)
