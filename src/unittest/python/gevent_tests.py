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

from gevent.monkey import patch_all

patch_all(aggressive=True, Event=True)

from karellen.sqlite3 import gevent_patch

gevent_patch()

from unittest import TestCase

from pysqlite2 import connect

class UpdateHookTests(TestCase):
    def connect(self):
        conn = connect("db.sqlite3", check_same_thread=False, isolation_level=None)
        conn.execute("PRAGMA journal_mode=wal")
        return conn

    def test_concurrent_read(self):
        with self.connect() as conn:
            conn.execute("CREATE TABLE a (int x)")
            conn.execute("CREATE TABLE b (int y)")



