import mysql.connector

class dbConnecting:
    def __init__(self, configuration):
        """ Set the database parameters to use (assumes passed in as a dictionary).
            """
        self.host = configuration['DB_HOST']
        self.user = configuration['DB_USER']
        self.password = configuration['DB_PASSWD']
        self.database = configuration['DB_NAME']

    def __enter__(self):
        """ Connect to database, and create a cursor, which is returned.
            """
        self.conn = mysql.connector.connect(host=self.host,
                                            user=self.user,
                                            password=self.password,
                                            database=self.database,)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """ Destroy the cursor as well as the connection (as we're done), ignoring
            any exceptions generated while the "with" executes.
            """
        self.cursor.close()
        self.conn.commit()
        self.conn.close()
