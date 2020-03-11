#!/usr/bin/python3
# -*- coding: utf-8 -*-
# data_access.py

import settings
import sqlite3
import time

TABLE_SENSORS = 'SENSORS'

class DataAccessLayer:

    def getOnlyConnection(self):
        connection = sqlite3.connect(settings.DATABASE_FILE)
        return connection

    def getConnection(self):
        connection = sqlite3.connect(settings.DATABASE_FILE)
        cursor = connection.cursor()
        return connection, cursor

    def initDb(self):
        connection, cursor = self.getConnection()
        sql = "CREATE TABLE IF NOT EXISTS " + TABLE_SENSORS \
            + " (sensor TEXT, qty INTEGER, log_date TEXT, sync TEXT)"
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close()

    """
        used by wiidem-api
    """

    def getPendingRecords(self):
        connection, cursor = self.getConnection()
        try:
            sql = "SELECT rowid, * From " + TABLE_SENSORS \
                + " WHERE sync = 'n' ORDER BY rowid ASC LIMIT 10"
            cursor.execute(sql)
            connection.commit()
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except sqlite3.DatabaseError as e:
            cursor.close()
            connection.close()
            return []

    def markRecordAsSynched(self, rowid):
        assert rowid is not None, 'rowid no puede ser None'
        connection, cursor = self.getConnection()
        try:
            sql = "UPDATE " + TABLE_SENSORS + " SET sync = 'y' WHERE rowid = " + str(rowid)
            cursor.execute(sql)
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except sqlite3.DatabaseError as e:
            cursor.close()
            connection.close()
            return False


    """
        used by wiidem-io
    """

    def saveSensorData(self, connection, sensor, qty):
        assert sensor is not None, 'cntCode no puede ser None'
        assert qty is not None, 'qty no puede ser None'
        cursor = connection.cursor()
        try:
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sync = 'n'
            sql = "INSERT INTO " + TABLE_SENSORS \
                + " (sensor, qty, log_date, sync) VALUES (?, ?, ?, ?)"
            params = (sensor, qty, date, sync)
            cursor.execute(sql, params)
            connection.commit()
            cursor.close()
            return True
        except sqlite3.DatabaseError as e:
            cursor.close()
            return False

    def countSynchedRecords(self, connection):
        cursor = connection.cursor()
        try:
            sql = "SELECT count(*) FROM "  + TABLE_SENSORS + " WHERE sync = 'y'"
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()
            return int(row[0])
        except sqlite3.DatabaseError as e:
            cursor.close()
            return 0

    def deleteSynchedRecords(self, connection):
        cursor = connection.cursor()
        try:
            sql = "DELETE FROM "  + TABLE_SENSORS + " WHERE sync = 'y'"
            cursor.execute(sql)
            connection.commit()
            cursor.close()
            return True
        except sqlite3.DatabaseError as e:
            cursor.close()
            return False
