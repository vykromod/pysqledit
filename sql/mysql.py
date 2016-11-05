

try:
    import MySQLdb #python 2.x
except ImportError:
    import pymysql
    pymysql.install_as_MySQLdb()
    import MySQLdb

#connection keys for mysql
connect_keys = ["host", "user", "password", "db", "port", "unix_socket",
                      "conv", "compress", "connect_timeout", "named_pipe", "init_command",
                      "read_default_file", "read_default_group", "cursorclass", "use_unicode",
                      "charset", "sql_mode", "ssl"]

class mysql:
    def __init__(self, **kwargs):
        """    Constructor for creating a connection to the database. Returns a Connection Object. Parameters are the same as for the MySQL C API. In addition, there are a few additional keywords that correspond to what you would pass mysql_options() before connecting. Note that some parameters must be specified as keyword arguments! The default value for each parameter is NULL or zero, as appropriate. Consult the MySQL documentation for more details. The important parameters are:

        host
            name of host to connect to. Default: use the local host via a UNIX socket (where applicable)
        user
            user to authenticate as. Default: current effective user.
        passwd
            password to authenticate with. Default: no password.
        db
            database to use. Default: no default database.
        port
            TCP port of MySQL server. Default: standard port (3306).
        unix_socket
            location of UNIX socket. Default: use default location or TCP for remote hosts.
        conv
            type conversion dictionary. Default: a copy of MySQLdb.converters.conversions
        compress
            Enable protocol compression. Default: no compression.
        connect_timeout
            Abort if connect is not completed within given number of seconds. Default: no timeout (?)
        named_pipe
            Use a named pipe (Windows). Default: don't.
        init_command
            Initial command to issue to server upon connection. Default: Nothing.
        read_default_file
            MySQL configuration file to read; see the MySQL documentation for mysql_options().
        read_default_group
            Default group to read; see the MySQL documentation for mysql_options().
        cursorclass
            cursor class that cursor() uses, unless overridden. Default: MySQLdb.cursors.Cursor. This must be a keyword parameter.
        use_unicode

            If True, CHAR and VARCHAR and TEXT columns are returned as Unicode strings, using the configured character set. It is best to set the default encoding in the server configuration, or client configuration (read with read_default_file). If you change the character set after connecting (MySQL-4.1 and later), you'll need to put the correct character set name in connection.charset.

            If False, text-like columns are returned as normal strings, but you can always write Unicode strings.

            This must be a keyword parameter.
        charset

            If present, the connection character set will be changed to this character set, if they are not equal. Support for changing the character set requires MySQL-4.1 and later server; if the server is too old, UnsupportedError will be raised. This option implies use_unicode=True, but you can override this with use_unicode=False, though you probably shouldn't.

            If not present, the default character set is used.

            This must be a keyword parameter.
        sql_mode

            If present, the session SQL mode will be set to the given string. For more information on sql_mode, see the MySQL documentation. Only available for 4.1 and newer servers.

            If not present, the session SQL mode will be unchanged.

            This must be a keyword parameter.
        ssl
            This parameter takes a dictionary or mapping, where the keys are parameter names used by the mysql_ssl_set MySQL C API call. If this is set, it initiates an SSL connection to the server; if there is no SSL support in the client, an exception is raised. This must be a keyword parameter.

        """
        self.name = None
        if kwargs.get("port", ""):
            kwargs["port"] = int(kwargs["port"])
        self.connection = self.conn = MySQLdb.connect(**kwargs)
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def server_name(self):
        if not self.name:
            self.cursor.execute("SELECT @@HOSTNAME")
            self.name = self.cursor.fetchall()[0][0]
        return self.name

    def databases(self, filters = None):
        dbs = []
        self.cursor.execute("show databases;")
        for item in self.cursor.fetchall():
            dbs.append(item[0])
        return dbs

    def create_database(self, database):
        self.cursor.execute("create database %s;" % database)

    def database_exists(self, database):
        self.cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%s'" % database)
        return len(self.cursor.fetchall())

    def selected_database(self, database = None):
        """selects database if given, returns last selected database
        """
        self.cursor.execute("SELECT DATABASE()")
        db = self.cursor.fetchall()[0][0]
        if database:
            self.cursor.execute("USE %s" % database)
        return db
        

    def tables(self, database, filters = None):
        tbs = []
        self.cursor.execute("show tables from %s;" % database)
        for item in self.cursor.fetchall():
            tbs.append(item[0])
        return tbs

    def create_table(self, database, table, fields):
        fieldsl = []
        for key in fields.keys():
            fieldsl.append("%s %s" % (key, fields[key]))
        code =  ",\n  ".join(fieldsl)
        self.cursor.execute("create table %s.%s (%s);" % (database, table, code))

    def columns(self, database, table, types = None):
        cls = []
        _types = []
        self.cursor.execute("show columns from %s.%s" % (database, table))
        for item in self.cursor.fetchall():
            field, type, null, key, default, extra = item
            _types.append(type)
            cls.append(field)
        if types:
            return cls, _types
        return cls

    def py_types(self, types):
        pytypes = []
        for typ in types:
            if typ.lower().find("int") > -1:
                pytypes.append(int)
            else:
                pytypes.append(str)
        return pytypes

    def add_column(self, database, table, fields):
        code = "alter table %s.%s ADD " % (database, table)
        fieldsl = []
        for key in fields.keys():
            fieldsl.append("%s %s" % (key, fields[key]))
        code += ", ".join(fieldsl)
        self.cursor.execute(code)

    def delete_coulmn():
        pass

    def columns_data(self, database, table, filters = None):
        cls = []
        self.cursor.execute("show columns from %s.%s" % (database, table))
        for item in self.cursor.fetchall():
            #field, type, null, key, default, extra = item
            cls.append(item)
        return cls

    def insert(self, database, table, data):
        code = "insert into %s.%s SET " % (database, table)
        items = []
        for key in data.keys():
            value = data[key]
            if str(value).strip():
                items.append('%s="%s"' % (key, value))
                #code += '\n%s="%s"' % (key, data[key])
        code +=  ", ".join(items) + ";"
        #print [code]
        self.cursor.execute(code)

    def update(self, database, table, data, where):
        code = "update %s.%s SET " % (database, table)
        items = []
        for key in data.keys():
            value = data[key]
            if str(value).strip():
                items.append('%s="%s"' % (key, value))
                #code += '\n%s="%s"' % (key, data[key])
        code +=  ", ".join(items)
        wheres = []
        for key in where.keys():
            try:
                operator, value = where[key]
            except:
                operator = "="
                value = where[key]
            wheres.append('%s%s"%s"' % (key, operator, value))
        if len(wheres):
            code += " WHERE " +  " AND ".join(wheres)
        code += ";"
        self.cursor.execute(code)

    def delete(self, database, table, where):
        code = "delete from %s.%s " % (database, table)
        wheres = []
        for key in where.keys():
            try:
                operator, value = where[key]
            except:
                operator = "="
                value = where[key]
            wheres.append('%s%s"%s"'% (key, operator, value))
        if len(wheres):
            code += " WHERE " +  " AND ".join(wheres)
        code += ";"

    def select(self, database, table, fields, where = {}, order_by = None):
        code = "select %s from %s.%s" % (fields, database, table)
        wheres = []
        for key in where.keys():
            try:
                operator, value = where[key]
            except:
                operator = "="
                value = where[key]
            wheres.append('%s%s"%s"' % (key, operator, value))
        if len(wheres):
            code += " WHERE " +  " AND ".join(wheres)
        if order_by:
            code += " ORDER BY %s" % order_by
        code += ";"
        #return code
        self.cursor.execute(code)
        returned = self.cursor.fetchall()
        """
        if len(returned):
            if len(returned) == 1:
                if len(returned[0]) == 1:
                    return returned[0][0]
                return returned[0]
            if len(returned[0]) == 1:
                ret = []
                for i in range(len(returned)):
                    ret.append(returned[i][0])
                return tuple(ret)
        """
        return returned

    def distinct(self, database, table, field, where = {}, order_by = None):
        code = "select distinct(%s) from %s.%s" % (field, database, table)
        wheres = []
        for key in where.keys():
            try:
                operator, value = where[key]
            except:
                operator = "="
                value = where[key]
            wheres.append('%s%s"%s"' % (key, operator, value))
        if len(wheres):
            code += " WHERE " +  " AND ".join(wheres)
        if order_by:
            code += " ORDER BY %s" % order_by
        code += ";"
        #return code
        self.cursor.execute(code)
        returned = self.cursor.fetchall()
        if len(returned):
            if len(returned[0]) == 1:
                ret = []
                for i in range(len(returned)):
                    ret.append(returned[i][0])
                return tuple(ret)
        return returned

    def count(self, database, table, fields, where = {}):
        code = "select count(%s) from %s.%s" % (fields, database, table)
        wheres = []
        for key in where.keys():
            try:
                operator, value = where[key]
            except:
                operator = "="
                value = where[key]
            wheres.append('%s%s"%s"' % (key, operator, value))
        if len(wheres):
            code += " WHERE " +  " AND ".join(wheres)
        code += ";"
        #return code
        self.cursor.execute(code)
        return self.cursor.fetchall()[0][0]
    
    
def create_test_db(s, db = "sqltest", tbl = "testtable"):
    #s.create_database(db)
    fields = {}
    fields["bit"] = "BIT(64)"
    fields["tiny_unsigned"] = "TINYINT UNSIGNED"
    fields["tiny_signed"] = "TINYINT"
    s.create_table(db, tbl, fields)

sql = mysql
if __name__ == "__main__":
    "mysql > grant all on *.* to vertex@192.168.1.12"  #local network - no password
    s = mysql(host = "192.168.1.12", user="vertex")
