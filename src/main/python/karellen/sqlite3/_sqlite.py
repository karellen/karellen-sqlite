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

import _sqlite3
import ctypes
import enum
import sqlite3
import sys
from functools import partial

sqlite3_lib = ctypes.PyDLL(_sqlite3.__file__)

SQLITE3_UPDATE_HOOK_CB = ctypes.PYFUNCTYPE(None, ctypes.c_void_p,
                                           ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
                                           ctypes.c_int64)

SQLITE3_COMMIT_HOOK_CB = ctypes.PYFUNCTYPE(ctypes.c_int, ctypes.c_void_p)
SQLITE3_ROLLBACK_HOOK_CB = ctypes.PYFUNCTYPE(None, ctypes.c_void_p)

sqlite3_lib.sqlite3_update_hook.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
sqlite3_lib.sqlite3_update_hook.restype = ctypes.c_void_p

sqlite3_lib.sqlite3_commit_hook.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
sqlite3_lib.sqlite3_commit_hook.restype = ctypes.c_void_p

sqlite3_lib.sqlite3_rollback_hook.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
sqlite3_lib.sqlite3_rollback_hook.restype = ctypes.c_void_p

sqlite3_conn_db_field_offset = ctypes.sizeof(ctypes.c_size_t) + ctypes.sizeof(ctypes.c_void_p)
is_debug_python = "d" in sys.abiflags
if is_debug_python:  # pragma: no cover
    sqlite3_conn_db_field_offset += (ctypes.sizeof(ctypes.c_void_p) * 2)


class UpdateHookOps(enum.Enum):
    SQLITE_DELETE = 9
    SQLITE_INSERT = 18
    SQLITE_UPDATE = 23


def update_hook_adapter(hook, conn, _, op, db_name, table_name, rowid):
    op = UpdateHookOps(op)
    db_name = str(db_name, "utf-8")
    table_name = str(table_name, "utf-8")

    conn._last_error = None
    try:
        hook(conn, op, db_name, table_name, rowid)
    except Exception as e:
        conn._last_error = e


def commit_hook_adapter(hook, conn, _):
    conn._last_error = None
    try:
        hook(conn)
    except Exception as e:
        conn._last_error = e
    finally:
        return 0


def rollback_hook_adapter(hook, conn, _):
    conn._last_error = None
    try:
        hook(conn)
    except Exception as e:
        conn._last_error = e


class Connection(sqlite3.Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        conn_addr = id(self)
        sqlite_db_addr = conn_addr + sqlite3_conn_db_field_offset
        self.sqlite_db = ctypes.c_void_p.from_address(sqlite_db_addr)

        self._update_hook = None
        self._update_hook_cb = None
        self._commit_hook = None
        self._commit_hook_cb = None
        self._rollback_hook = None
        self._rollback_hook_cb = None

        self._last_error = None

    def last_hook_error(self):
        """Returns the last error raised inside an update hook or `None`"""
        return self._last_error

    def _make_update_hook_adapter(self, hook):
        return partial(update_hook_adapter, hook, self)

    def _make_commit_hook_adapter(self, hook):
        return partial(commit_hook_adapter, hook, self)

    def _make_rollback_hook_adapter(self, hook):
        return partial(rollback_hook_adapter, hook, self)

    def set_update_hook(self, hook=None):
        """Sets an update hook overwriting a previous one

        The hook must be a callable able to accept the following positional arguments:
            conn: Connection
            op: operation performed, one of the :obj:`UpdateHookOps` enum values
            db_name (str): name of the database
            table_name (str): name of the table
            rowid (int): ROWID of the affected record

        Note:
            The hook MUST NOT perform any database operations whatsoever.
            Please see additional restrictions in
            `SQLite documentation <https://www.sqlite.org/c3ref/update_hook.html>`_

        Args:
            hook: a callable or `None` to remove the hook

        Returns:
            The last update hook set or `None`

        Note:
            If a hook raises an exception, it can be checked in `last_hook_error`
        """
        last_hook = self._update_hook
        if hook is None:
            self._update_hook = None
            self._update_hook_cb = hook_proper = None
            self._last_error = None
        else:
            self._update_hook = hook
            self._update_hook_cb = hook_proper = SQLITE3_UPDATE_HOOK_CB(self._make_update_hook_adapter(hook))

        sqlite3_lib.sqlite3_update_hook(self.sqlite_db, hook_proper, None)
        return last_hook

    def set_commit_hook(self, hook=None):
        """Sets an commit hook overwriting a previous one

        The hook must be a callable able to accept the following positional arguments:
            conn: Connection

        Note:
            The hook MUST NOT perform any database operations whatsoever.
            Please see additional restrictions in
            `SQLite documentation <https://www.sqlite.org/c3ref/update_hook.html>`_

        Args:
            hook: a callable or `None` to remove the hook

        Returns:
            The last update hook set or `None`

        Note:
            If a hook raises an exception, it can be checked in `last_hook_error`
        """
        last_hook = self._commit_hook
        if hook is None:
            self._commit_hook = None
            self._commit_hook_cb = hook_proper = None
            self._last_error = None
        else:
            self._commit_hook = hook
            self._commit_hook_cb = hook_proper = SQLITE3_COMMIT_HOOK_CB(self._make_commit_hook_adapter(hook))

        sqlite3_lib.sqlite3_commit_hook(self.sqlite_db, hook_proper, None)
        return last_hook

    def set_rollback_hook(self, hook=None):
        """Sets an rollback hook overwriting a previous one

        The hook must be a callable able to accept the following positional arguments:
            conn: Connection


        Note:
            The hook MUST NOT perform any database operations whatsoever.
            Please see additional restrictions in
            `SQLite documentation <https://www.sqlite.org/c3ref/update_hook.html>`_

        Args:
            hook: a callable or `None` to remove the hook

        Returns:
            The last update hook set or `None`

        Note:
            If a hook raises an exception, it can be checked in `last_hook_error`
        """
        last_hook = self._rollback_hook
        if hook is None:
            self._rollback_hook = None
            self._rollback_hook_cb = hook_proper = None
            self._last_error = None
        else:
            self._rollback_hook = hook
            self._rollback_hook_cb = hook_proper = SQLITE3_ROLLBACK_HOOK_CB(self._make_rollback_hook_adapter(hook))

        sqlite3_lib.sqlite3_rollback_hook(self.sqlite_db, hook_proper, None)
        return last_hook


def connect(database, **kwargs):
    if 'factory' not in kwargs:
        kwargs['factory'] = Connection
    return sqlite3.connect(database, **kwargs)
