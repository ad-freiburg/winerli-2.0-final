import os
import sqlite3


class Database:
    def __init__(self, path, read_only=False, same_thread=True, create_anew=True):
        if read_only:
            mode = 'ro'
        else:
            mode = 'rwc'
            if create_anew:
                # Delete the file if it exists already before trying to create it anew
                try:
                    os.remove(path)
                except:
                    pass
        self._database = sqlite3.connect(
            'file:' + path + '?mode=' + mode, uri=True, check_same_thread=same_thread)

    def start_transaction(self):
        self._database.execute("BEGIN TRANSACTION;")

    # Data is a tuple of values to be inserted into the query
    def query(self, query, data=()):
        result = self._database.execute(query, data).fetchall()
        if result is None:
            return None
        return result

    def query_and_commit(self, query, data=()):
        self._database.execute(query, data)
        self._database.commit()

    def commit(self):
        self._database.commit()

    def commit_and_close(self):
        self._database.commit()
        self._database.close()
    
    def close(self):
        self._database.close()
