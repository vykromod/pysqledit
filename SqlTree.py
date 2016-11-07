
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
        count = 0
        for tbl in self.master.sql.tables(self.name):
            count += 1
        return count

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
    table.create_grid(30)
    table.pack(expand = 1, fill = "both")
    table.set_array(array, sql.py_types(types))
    table.update_grid()

_delta_mod = 20.0
def _on_canvas_wheel(evt):
    global canv
    canv = evt.widget
    top, bottom = canv.sc.vbar.get()
    size = bottom - top
    if size == 1.0:
        return
    canv.yview("scroll", - int(evt.delta/_delta_mod), "units")

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
    root.wm_title("%s - %s" % (sql.__class__.__name__, item.GetText()))
    #root.mainloop()
    #this wheel binding doesn't work if widget in canvas is focused
    sc.canvas.bind("<MouseWheel>", _on_canvas_wheel)
    sc.canvas.sc = sc

if __name__ == "__main__":
    from sql import mssql
    #from sql import mysql
    from sql import pgsql
    _tree_widget(None, pgsql.sql(host = "192.168.1.13", user = "postgres"))
    #_tree_widget(None, mssql.sql(server=r"WS2008DEV2\SQLEXPRESS"))
