# Cuckoo

## Cuckoo is a simple django app for assisting with database migration.


There is no clever trickiness, magic, or other intelligence to automatically
generate your sql. For that you should be using
[South](http://south.aeracode.org). With cuckoo, you write sql patches, and the
application keeps track of which have already been applied. You might use it because you like to hand-roll
your sql, or because you have messed with your django and intelligent migrations fail.

Cuckoo works as follows:
 
 1. You write some sql patches
 2. Put them in a directory
 3. Run `./manage.py cuckoo` to execute any patches that haven't yet been run

## Installation

### Get the code

The easiest way is to use the `pip` installer:

    pip install git+ssh://git@github.com/dragonfly-science/cuckoo.git


### Setup
 1. Add `cuckoo` to `INSTALLED_APPS` in your settings file
 2. Make a directory, by default `sql-patches`, to hold your patches
 3. Optionally, add a string `CUCKOO_DIRECTORY` to your settings file that holds the full path to the 
        directory where you store your patches, e.g., `CUCKOO_DIRECTORY = '/home/edward/django/www/patches'`
 4. Run ./manage.py syncdb, or pipe the output from `./manage.py sql cuckoo` at your database 

## Usage
    
When you install cuckoo, it creates a table `cuckoo_patch` in your database. This table
holds a record of the patches that have been run. A Patch object has the fields 

 - patch: The filename of the patch (must be unique)
 - sql: The content of the patch file (not really necessary)
 - output: The output from running the patch
 - last\_updated: When the patch was actually run.

Cuckoo needs to know how to find the database. There are two ways of doing this.  

 1. The standard django way, see https://docs.djangoproject.com/en/dev/ref/settings/#databases
 2. By setting a `CUCKOO_DATABASE_STRING` string, with `%s` indicating where the patch filename should be substituted. 
This is useful if your sql patches contain commands that are not parsed by the python database connection layer. For a
postgres database you might have `database_string = 'psql %(NAME)s -U %(USER)s -h %(HOST)s -f '%DATABASES['default']` in your 
settings file, with `CUCKOO_DATABASE_STRING = database_string + '%s'`.



## The shining cuckoo

The [shining cuckoo](http://en.wikipedia.org/wiki/Shining_Bronze_Cuckoo) 
migrates from  the Solomon Islands, Papua Guinea region to New Zealand in the spring. It breeds in New Zealand in the summer. It has a distinctive call, and is often heard, but rarely seen. Cuckoos lay
their eggs in the nest of other birds (the shining cuckoo parasitises the gray warbler). The cuckoo migrations systems lets
you put your own eggs into the django nest.

![Shining cuckoo](http://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Chrysococcyx_lucidus_-_Meehan_Range.jpg/220px-Chrysococcyx_lucidus_-_Meehan_Range.jpg "Shining cuckoo, cc photograph by JJ Harrison)
