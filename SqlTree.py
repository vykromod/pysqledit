
from idlelib.TreeWidget import *

class SqlTreeItem(TreeItem):
    sublist = None
    def __init__(self, sql):
        self.sql = sql

    def GetText(self):
        return self.sql.server_name()

    def SetText(self, text):
        return self.sql.server_name()

    def GetIconName(self):
        if not self.IsExpandable():
            return "python" # XXX wish there was a "file" icon

    def IsExpandable(self):
        return 1

    def GetSubList(self):
        sublist = []
        for db in self.sql.databases():
            sublist.append(SqlDbItem(self, db))
        return sublist
                

class SqlDbItem(TreeItem):
    def __init__(self, master, name):
        self.name = name
        self.master = master
        
    def GetText(self):
        return self.name
    
    def IsExpandable(self):
        return 1

    def GetSubList(self):
        sublist = []
        for tbl in self.master.sql.tables(self.name):
            sublist.append(SqlTableItem(self, tbl))
        return sublist


class SqlTableItem(TreeItem):
    def __init__(self, master, name):
        self.master = master
        self.name = name

    def GetText(self):
        return self.name

    def IsExpandable(self):
        return 0

    def GetIconName(self):
        return "python"

    def OnDoubleClick(self):
        print("doubleclick")
        open_table(None, self)


def open_table(master, table_item):
    top = Toplevel(master)
    tbl = table_item.name
    db = table_item.master.name
    dbname = table_item.master.master.sql.server_name()
    top.wm_title("%s - %s.%s" % (dbname, db, tbl))
    sql = table_item.master.master.sql

    columns, types = sql.columns(db, tbl, True)
    import FilterTable
    top.bind("<MouseWheel>", FilterTable.on_mouse_wheel)
    top.bind_wheel = FilterTable.bind_wheel
    table = FilterTable.FilterTable(top, columns)
    array = sql.select(db, tbl, "*")
    table.pack(expand = 1, fill = "both")
    table.create_grid(30)
    table.set_array(array, sql.py_types(types))
    table.update_grid()


def _tree_widget(master, sql, **kwargs):
    global s, sc, item, node
    s = sql
    if not master:
        root = Tk()
    else:
        root = Toplevel(master)
        
    root.title(repr(sql))
    #width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    #root.geometry("+%d+%d"%(x, y + 150))
    sc = ScrolledCanvas(root, bg="white", highlightthickness=0, takefocus=1)
    sc.frame.pack(expand=1, fill="both", side=LEFT)
    #sql = sqlmodule.sql(**kwargs)
    item = SqlTreeItem(sql)
    node = TreeNode(sc.canvas, None, item)
    node.expand()
    #root.mainloop()


if __name__ == "__main__":
    from sql import mssql
    #from sql import mysql
    
    _tree_widget(None, mssql.sql(server=r"WS2008DEV2\SQLEXPRESS"))
