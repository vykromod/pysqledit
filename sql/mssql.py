

import pymssql

connect_keys = ["server", "user", "password", "database", "timeout",
                "login_timeout", "charset", "appname", "port", "conn_properties",
                "autocommit", "tds_version"]

class mssql:
    def __init__(self, **kwargs):
        self.name = None
        if kwargs.get("port", ""):
            kwargs["port"] = int(kwargs["port"])
        self.connection = self.conn = pymssql.connect(**kwargs)
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def server_name(self):
        if not self.name:
            self.cursor.execute("SELECT @@SERVERNAME;")
            self.name = self.cursor.fetchall()[0]
        return self.name

    def databases(self, filters = None):
        dbs = []
        self.cursor.execute("select * from sys.databases;")
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
        self.cursor.execute("""SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG='%s'""" % database)
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
        self.cursor.execute("""use %s;
select COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, 
       NUMERIC_PRECISION, DATETIME_PRECISION, 
       IS_NULLABLE 
from INFORMATION_SCHEMA.COLUMNS
where TABLE_NAME='%s'""" % (database, table))
        _types = []
        for item in self.cursor.fetchall():
            cls.append(item[0])
            _types.append(item[1])
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
        code = "use %s; select %s from %s" % (database, fields, table)
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
    
    

def get_data_from_table(table, field, **where):
    code = "select %s from %s" % (field, table)
    wheres = []
    for key in where.keys():
        wheres.append("%s%s%s" % (key, where[key][0], where[key][1]))
    if len(wheres):
        code += " WHERE " +  " AND ".join(wheres)
        code += ";"
    #return code
    cursor.execute(code)
    return mysql_return(cursor.fetchall())
    
    
def py_types(types):
    pass

sql = mssql


if __name__ == "__main__":
    "mysql > grant all on *.* to vertex@192.168.1.12"  #local network - no password
    #s  = sql()
    server = r"WS2008DEV2\SQLEXPRESS"
    s = sql(server=server)
