#
#  -*- coding: utf-8 -*-
#
# (C) Copyright 2016 Karellen, Inc. (http://karellen.co/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from functools import wraps, partial
from greenlet import greenlet as RawGreenlet

import gevent
from gevent.hub import get_hub
from gevent.monkey import patch_item

from karellen.sqlite3 import _sqlite
from karellen.sqlite3 import dbapi2
from karellen.sqlite3.dbapi2 import Cursor, Connection, connect


def _wrap_async(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return get_hub().threadpool.apply(func, args, kwargs)

    return wrapped


def _connect(database, **kwargs):
    kwargs["check_same_thread"] = False
    return connect(database, **kwargs)


def gevent_update_hook_adapter(hub, hook, conn, _, op, db_name, table_name, rowid):
    watcher = hub.loop.async(lambda: None)
    g = RawGreenlet(_sqlite.update_hook_adapter, hub)
    hub.loop.run_callback(g.switch, hook, conn, None, op, db_name, table_name, rowid)
    watcher.send()


def gevent_commit_hook_adapter(hub, hook, conn, _):
    watcher = hub.loop.async(lambda: None)
    g = RawGreenlet(_sqlite.commit_hook_adapter, hub)
    hub.loop.run_callback(g.switch, hook, conn, None)
    watcher.send()
    return 0


def gevent_rollback_hook_adapter(hub, hook, conn, _):
    watcher = hub.loop.async(lambda: None)
    g = RawGreenlet(_sqlite.rollback_hook_adapter, hub)
    hub.loop.run_callback(g.switch, hook, conn, None)
    watcher.send()


class GeventConnection(Connection):
    cursor = _wrap_async(Connection.cursor)
    close = _wrap_async(Connection.close)
    commit = _wrap_async(Connection.commit)
    rollback = _wrap_async(Connection.rollback)
    create_function = _wrap_async(Connection.create_function)
    create_aggregate = _wrap_async(Connection.create_aggregate)

    if hasattr(Connection, "enable_load_extension"):
        load_extension = _wrap_async(Connection.load_extension)

    execute = _wrap_async(Connection.execute)
    executemany = _wrap_async(Connection.executemany)
    executescript = _wrap_async(Connection.executescript)

    def _make_update_hook_adapter(self, hook):
        hub = gevent.get_hub()
        return partial(gevent_update_hook_adapter, hub, hook, self)

    def _make_commit_hook_adapter(self, hook):
        hub = gevent.get_hub()
        return partial(gevent_commit_hook_adapter, hub, hook, self)

    def _make_rollback_hook_adapter(self, hook):
        hub = gevent.get_hub()
        return partial(gevent_rollback_hook_adapter, hub, hook, self)


class GeventCursor(Cursor):
    execute = _wrap_async(Cursor.execute)
    executemany = _wrap_async(Cursor.executemany)
    executescript = _wrap_async(Cursor.executescript)
    fetchone = _wrap_async(Cursor.fetchone)
    fetchmany = _wrap_async(Cursor.fetchmany)
    fetchall = _wrap_async(Cursor.fetchall)
    close = _wrap_async(Cursor.close)


def gevent_patch():
    patch_item(_sqlite, "Connection", GeventConnection)
    patch_item(dbapi2, "Cursor", GeventCursor)
    patch_item(dbapi2, "connect", _wrap_async(connect))
