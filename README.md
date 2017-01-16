# Karellen Sqlite Extensions

[![Gitter chat](https://badges.gitter.im/karellen/gitter.svg)](https://gitter.im/karellen/lobby)

## About

This project contains [Karellen](https://www.karellen.co/karellen/) 
[Sqlite](https://docs.python.org/3/library/sqlite3.html) extensions to the standard Python SQLite3 module.

These extensions are verified to work with Python 3.x (x >= 3) on Linux x86_64 and have been verified 
to work with GA and Debug builds of CPython. Any CPython ABI-compliant Python should work as well (YMMV).


## SQLite3 Update Hook

The [SQLite3 update hook](https://www.sqlite.org/c3ref/update_hook.html) allows the hook to be notified if the database 
to which the connection is made was changed.

This a drop-in replacement that can be used as demonstrated in the example below. The name `pysqlite2` was chosen
to the driver to be discovered automatically by 
[Django SQLite backend](https://docs.djangoproject.com/en/1.10/ref/databases/#using-newer-versions-of-the-sqlite-db-api-2-0-driver).

```python

from pysqlite2 import connect

def hook(conn, op, db_name, table_name, rowid):
    """Handle notification here. Do not modify the connection!"""
    
with connect(":memory:") as conn:
    conn.set_update_hook(hook)
    conn.execute("CREATE TABLE a (int id);")
    conn.execute("INSERT INTO a VALUES (1);")

```

You can also use this library directly with your Python 3 without renaming:

```python
from sqlite3 import connect
from karellen.sqlite3 import Connection

with connect(":memory:", factory=Connection):
    # Do something useful here
    pass

```

