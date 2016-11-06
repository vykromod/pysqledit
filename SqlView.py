
import SqlTree
import FilterTable
try:
    from tkinter import *
except ImportError:
    from Tkinter import *

class EntryObj(Entry):
    def __init__(self, master, key):
        self.key = key
        self.var = StringVar()
        Entry.__init__(self, master, textvariable = self.var)
        if key == "password":
            self.config(show = "*")

class SqlConnect(Frame):
    support = ["mysql", "mssql", "sqlite", "pgsql"]
    def __init__(self, master, **kwargs):
        self.input = {}
        self.master = master
        self.kwargs = kwargs
        Frame.__init__(self, master)
        self.build()

    def build(self):
        self.buttons = []
        for txt in self.support:
            b = Button(self, text = txt)
            b.bind("<Button-1>", self.get_sqlmod)
            b.pack()#side = "left")
            self.buttons.append(b)

    def get_sqlmod(self, evt):
        ##print(evt.__dict__)
        name = evt.widget["text"]
        evt = {}
        code = "from sql import %s as sql" % name
        exec(code, evt)
        print(evt["sql"])
        self.sqlmod = evt["sql"]
        self.build_entries(name)
        

    entries = None
    label = None
    def build_entries(self, name):
        
        entries = self.input.get(name, None)
        if not entries:
            entries = Frame(self)
            entries.label = Label(entries, text = name)
            entries.label.grid(row=0,column=0)
            
            self.input[name] = entries
            for i in range(len(self.sqlmod.connect_keys)):
                txt = self.sqlmod.connect_keys[i]
                label = Label(entries, text=txt)
                entry = EntryObj(entries, txt) 
                label.grid(row = i + 1, column = 0)
                entry.grid(row = i + 1, column = 1)
            self.button = Button(entries, text="Connect", command=self.connect)
            self.button.grid(row = i+2, column = 0)
            entries.pack()
        for entryframe in self.input.values():
            if entryframe != entries:
                entryframe.pack_forget()
        entries.pack()
        self.entries = entries

    def collect(self):
        dic = {}
        for entry in self.entries.grid_slaves(column = 1):
            value = entry.var.get()
            if value:
                dic[entry.key] = value
        return dic

    def connect_callback(self, sql):
        global s
        s = sql
        self.sql = sql
        print("sql connected %s" % str(sql))
        opendb(self, sql)
        

    def connect(self):
        sql = self.sqlmod.sql(**self.collect())
        self.connect_callback(sql)

def opendb(master, sql):
    SqlTree._tree_widget(master, sql)

def main():
    global root, sc
    root = Tk()
    root.wm_title("SQL connect mk1")
    sc = SqlConnect(root)
    sc.pack(fill = "both", expand = 1)
    #root.mainloop()


if __name__ == "__main__":
    main()
