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

from sqlite3 import Connection as Sqlite3Connection
from unittest import TestCase

from karellen.sqlite3._sqlite import Connection as KarellenConnection
from pysqlite2.dbapi2 import connect, UpdateHookOps


class UpdateHookTests(TestCase):
    def test_update_hook_set(self):
        hook_ex = Exception("hook goes boom")

        def hook(conn, op, db_name, table_name, rowid):
            self.assertTrue(isinstance(conn, KarellenConnection))
            self.assertEqual(op, UpdateHookOps.SQLITE_INSERT)
            self.assertEqual(db_name, "main")
            self.assertEqual(table_name, "a")
            self.assertEqual(rowid, 1)

        def error_hook(conn, op, db_name, table_name, rowid):
            raise hook_ex

        with connect(':memory:') as conn:
            self.assertIsNone(conn.set_update_hook(hook))
            conn.execute("CREATE TABLE a (int id);")
            conn.execute("INSERT INTO a VALUES (1);")
            if conn.last_update_hook_error():
                raise conn.last_update_hook_error()

            self.assertIs(conn.set_update_hook(error_hook), hook)
            conn.execute("INSERT INTO a VALUES (2);")
            self.assertIs(conn.last_update_hook_error(), hook_ex)
            self.assertIs(conn.set_update_hook(), error_hook)
            self.assertIsNone(conn.last_update_hook_error())

    def test_factory_can_be_overwritten(self):
        with connect(':memory:', factory=Sqlite3Connection) as conn:
            self.assertFalse(isinstance(conn, KarellenConnection))

    def test_imports(self):
        from karellen.sqlite3 import Connection as conn
        self.assertIs(conn, KarellenConnection)

        from karellen.sqlite3.dbapi2 import Connection as conn
        self.assertIs(conn, KarellenConnection)

        from pysqlite2 import Connection as conn
        self.assertIs(conn, KarellenConnection)

        from pysqlite2.dbapi2 import Connection as conn
        self.assertIs(conn, KarellenConnection)
