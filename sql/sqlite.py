
import os
import sqlite3

#connection keys for sqlite
connect_keys = ["database", "timeout", "detect_types", "isolation_level",
        "check_same_thread", "factory", "cached_statements", "uri"]

class sqlite:
    def __init__(self, **kwargs):
        """    Constructor for managing a connection to the database.
    parameters are:
            database -  database file
        """
        self.name = None
        self.filename = kwargs["database"]
        if kwargs.get("detect_types", None) != None:
            kwargs["detect_types"] = int(kwargs["detect_types"])
        self.connection = self.conn = sqlite3.connect(**kwargs)
        self.cursor = self.connection.cursor()        

    def close(self):
        self.cursor.close()
        self.connection.close()

    def server_name(self):
        return self.filename
        if not self.name:
            self.cursor.execute("SELECT @@HOSTNAME")
            self.name = self.cursor.fetchall()[0][0]
        return self.name

    def databases(self, filters = None):
        dbs = []
        self.cursor.execute('PRAGMA database_list;')
        for item in self.cursor.fetchall():
            dbs.append(item[1])#[0])
        return dbs

    def create_database(self, database):
        self.cursor.execute('ATTACH "%s" as %s' % (self.filename, database))

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
        self.cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"')
        for item in self.cursor.fetchall():
            tbs.append(item[0])
        return tbs

    def create_table(self, database, table, fields):
        fieldsl = []
        for key in fields.keys():
            fieldsl.append("%s %s" % (key, fields[key]))
        code =  ",\n  ".join(fieldsl)
        self.cursor.execute("create table %s (%s);" % (table, code))

    def columns(self, database, table, types = None):
        cls = []
        self.cursor.execute('PRAGMA table_info("%s");' % table)
        _types = []
        for item in self.cursor.fetchall():
            #field, type, null, key, default, extra = item
            _types.append(item[2])
            cls.append(item[1])
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
        code = "insert into %s " % table
        items = []
        code += "(%s) VALUES " % ",".join(data.keys())
        code += str(tuple(data.values())).replace(",)", ")")
        #print(code)
        self.cursor.execute(code)
        self.conn.commit()

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
        code = "select %s from %s" % (fields, table)
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
            if len(returned) == 1:
                if len(returned[0]) == 1:
                    return returned[0][0]
                return returned[0]
            if len(returned[0]) == 1:
                ret = []
                for i in range(len(returned)):
                    ret.append(returned[i][0])
                return tuple(ret)
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

def py_types(types):
    pytypes = []
    for typ in types:
        t = typ.lower()
        if t.find("int") > -1:
            pytypes.append(int)
        elif t.find("char") > -1:
            pytypes.append(str)
        elif t.find("text") > -1:
            pytypes.append(str)
        elif t.find("real") > -1:
            pytypes.append(float)
        elif t.find("double") > -1:
            pytypes.append(float)

        else:
            pytypes.append(None)
        
    
    
def create_test_table(s, db = "sqltest", tbl = "testtable"):
    #s.create_database(db)
    fields = {}
    fields["integer"] = "INTEGER"
    fields["real"] = "REAL"
    fields["text"] = "TEXT"
    fields["blob"] = "BLOB"
    fields["wtf"] = "WTFTYPE"
    """
    fields["int"] = "INT"
    fields["tinyint"] = "TINYINT"
    fields["smallint"] = "SMALLINT"
    fields["mediumint"] = "MEDIUMINT"
    fields["bigint"] = "BIGINT"
    fields["bigint_unsigned"] = "BIGINT UNSIGNED"
    """
    s.create_table(db, tbl, fields)
    for i in range(10):
        s.insert(db, tbl, {"integer": i, "real" :float(i) * 1.1, "text" : "blah %i" % i, "blob" : "\x00\xff"})
    s.insert(db, tbl, {"integer": "blah", "real" :"blah", "text" : i, "blob" : i})
    

sql = sqlite
if __name__ == "__main__":
    s = sql(database = "sqlitetest.db", detect_types = 1)
    
