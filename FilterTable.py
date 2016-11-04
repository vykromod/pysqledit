try:
    import tkinter as Tkinter ##python 3.x.x
except ImportError:
    import Tkinter ##python 2.x.x


class Entry(Tkinter.Entry):
    def __init__(self, is_column, info_grid, master, **cnf):
        self.is_column = is_column
        self.info_grid = info_grid
        cnf["state"] = "readonly"
        cnf["cursor"] = "arrow"
        cnf["borderwidth"] = 0
        Tkinter.Entry.__init__(self, master, **cnf)
        if not is_column:
            self.bind('<Button-1>', self.on_click)
            self.bind('<Double-1>', self.on_doubleclick)
            self.bind("<KeyPress>", self.on_key_press)
        else:
            self._sort_reverse = False
            self.bind('<Button-1>', self.sort)

    def sort(self, event):
        self.info_grid.sort_by_index(int(self.master.grid_info()["column"]), self._sort_reverse)
        self._sort_reverse = not self._sort_reverse

    def set(self, value):
        self["state"] = "normal"
        self.delete(0, "end")
        if type(value) == str:
            value = value.encode("UTF-8")
        elif type(value) == type(None):
            value = ""
        else:
            value = str(value)
        self.insert(0, value)
        self["state"] = "readonly"

    def clear(self):
        self["state"] = "normal"
        self.delete(0, "end")
        self["state"] = "readonly"

    def on_key_press(self, event):
        key = event.keysym
        #print "press %s" % key
        units = None
        ammount = None
        if key == "Down":
            ammount = 1
            units = "units"
        elif key == "Up":
            ammount = -1
            units = "units"
        elif key == "Prior":
            ammount = -1
            units = "pages"
        elif key == "Next":
            ammount = 1
            units = "pages"
        else:
            return
        """
        if key in ("Up", "Down"):
            sel = self.info_grid.selected + ammount
            total = len(self.info_grid.cards_array.array)
            if sel > total:
                sel = total
            if sel < 0:
                sel = 0
            self.info_grid.selected = sel
        """
        self.info_grid.yview("scroll", ammount, units)
        if units == "units":
            if self.info_grid.selected > 0:
                self.info_grid.select_set(ammount)

    def on_click(self, event):
        if self.info_grid: #hasattr(self.master.master.master, "select_row"):
            row = int(self.grid_info()["row"])
            self.master.master.master.select_row(row)

    def on_doubleclick(self, event):
        if self.info_grid: #hasattr(self.master.master.master, "activate_row"):
            self.master.master.master.activate_row()

class Resizer(Tkinter.Frame):
    def __init__(self, info_grid, master, **cnf):
        self.info_grid = info_grid
        Tkinter.Frame.__init__(self, master, **cnf)
        self.bind('<Button1-Motion>', self.resize_row)
        self.bind('<ButtonPress-1>', self.resize_start)
        self._resizing = False

    def resize_row(self, event):
        if self._resizing:
            top = self.info_grid.top
            grid = self.info_grid._grid
            col = self.master.grid_info()["column"]
            width = self._width + event.x_root - self._x_root
            top.columnconfigure(col, minsize = width)
            grid.columnconfigure(col, minsize = width)

    def resize_start(self, event):
        top = self.info_grid.top
        self._resizing = True
        self._x_root = event.x_root
        col = self.master.grid_info()["column"]
        self._width = top.grid_bbox(row = 0, column = col)[2]
        #print event.__dict__
        
        col = self.master.grid_info()["column"]
        #print top.grid_bbox(row = 0, column = col)

class Filter(Tkinter.Frame):
    _active = False
    filter_type = str
    def __init__(self, info_grid, name, column, master, **cnf):
        global fil
        fil = self
        cnf["bd"] = 2
        cnf["relief"] = "solid"
        Tkinter.Frame.__init__(self, master, **cnf)
        self.key_name = name
        self.info_grid = info_grid
        self.column = column
        self.op_values = ["and", "or", "not"]
        self._filter_busy = False
        self._filter_break = False
        info_grid.filters.append(self)
        self._build_final()

    def next_op_value(self, event):
        current = self.label["text"]
        i = self.op_values.index(current)
        try:
            text = self.op_values[i + 1]
        except:
            text = self.op_values[0]
        self.label["text"] = text

    def prev_op_value(self, event):
        current = self.label["text"]
        i = self.op_values.index(current) - 1
        text = self.op_values[i]
        self.label["text"] = text

    def filter_value(self):
        value = self.entry.get()
        if value:
            value = "%s: %s" % (self.label["text"], value)
        return value

    def all_filter_values(self):
        all = []
        for i in range(len(self.info_grid.filters)):
            if not self.info_grid.filters[i]:
                filter_value = ""
            else:
                filter_value = self.info_grid.filters[i].filter_value()
            all.append((self.info_grid.filters[i].label["text"], filter_value))
        return tuple(all)

    def filter_by_all(self, event):
        #print "\nnew filter by all"
        self.filter(event)
        for i in range(len(self.info_grid.filters)):
            if not self.info_grid.filters[i]:
                continue
            if self.info_grid.filters[i] == self:
                continue
            self.info_grid.filters[i].filter()
        self.info_grid.update_grid()
        

    def filter(self, event = None):
        class dummy_event:
            keysym = "filter_event"
        if not event: event = dummy_event
        self._pre_filter(event)
        self._active = True
        self._filter_break = False
        getattr(self, "_filter_by_%s" % self.filter_type.__name__)(event)

    def _split_int_op(self, items):
        d = {}
        for item in items:
            item = item.strip()
            for op in self._int_ops:
                if item.find(op) == 0:
                    value = item.replace(op, "")
                    if not op in d.keys():
                        d[op] = []
                    d[op].append(int(value))
                    break
        return d
                    

    _int_ops = [">=", "<=", "==", ">", "<"]
    def _filter_by_int(self, event):
        print("filter int %s" % self.entry.get())
        index = self.index
        filters = self.entry.get().strip()
        if not filters:
            return
        sfilters = filters.split(" ")
        ifilters = self._split_int_op(sfilters)
        operator = self.label["text"]
        new = []
        print(ifilters)
        for i in range(len(self.info_grid.array)):
            item = self.info_grid.array[i]##[index]
            match = []
            if self._filter_break:
                    break
            value = item[index]
            if value == None:
                continue
            ops = ifilters.keys()
            for op in ops:
                if op == "<":
                    val = min(ifilters[op])
                    if value < val:
                        match.append(value)
                if op == "<=":
                    val = min(ifilters[op])
                    if value <= val:
                        match.append(value)
                if op == ">":
                    val = max(ifilters[op])
                    if value > val:
                        match.append(value)
                if op == ">=":
                    val = max(ifilters[op])
                    if value >= val:
                        match.append(value)
                if op == "==":
                    eq_match = []
                    for val in ifilters[op]:
                        if value == val:
                            eq_match.append(value)
                    if len(eq_match):
                        match.append(value)
            if operator == "or":
                if len(match) > 0:
                    new.append(item)
            elif operator == "and":
                if len(match) == len(sfilters):
                    new.append(item)
            elif operator == "not":
                if not len(match):
                    new.append(item)
            else:
                raise Exception("Invalid operator %s in %s" % (operator, self))
        if not self._filter_break:
            
            self.info_grid.filter_cache[self.key_name][operator][self.all_filter_values()] = list(new)
            self.info_grid.array = new
            

        self._filter_busy = False
        self._active = False
        if self._filter_break:
            print("broken")

    def _filter_by_str(self, event):
        print("filter string %s" % self.entry.get())
        index = self.index
        filters = self.entry.get().strip()
        if not filters:
            return
        sfilters = filters.split(" ")
        operator = self.label["text"]
        new = []
        for i in range(len(self.info_grid.array)):
            item = self.info_grid.array[i]##[index]
            value = item[index]
            if value == None:
                continue
            match = []
            if self._filter_break:
                    break
            for word in sfilters:
                if value.lower().find(word.lower()) > -1:
                    match.append(value)
                    
            if operator == "or":
                if len(match) > 0:
                    new.append(item)
            elif operator == "and":
                if len(match) == len(sfilters):
                    new.append(item)
            elif operator == "not":
                if not len(match):
                    new.append(item)
            else:
                raise Exception("Invalid operator %s in %s" % (operator, self))
        if not self._filter_break:
            
            self.info_grid.filter_cache[self.key_name][operator][self.all_filter_values()] = list(new)
            self.info_grid.array = new
            

        self._filter_busy = False
        self._active = False
        if self._filter_break:
            print("broken")
        
    
    def _build_final(self):
        self.label = label = Tkinter.Label(self, text = self.op_values[0])
        label.bind("<ButtonPress-1>", self.next_op_value)
        label.bind("<ButtonPress-3>", self.prev_op_value)
        self.entry = Tkinter.Entry(self, width = 1)
        self.entry.bind("<KeyRelease-Return>", self.filter_by_all)
        self.entry.bind("<KeyPress>", self._break_filter)
        self.label.pack(side = "left")
        self.entry.pack(side = "left", fill = "x", expand = 1)

    def _break_filter(self, event):
        if self._active:
            self._filter_break = True
            self._active = False
            self._filter_busy = False

    def _pre_filter(self, event):
        #if self._filter_busy:
        #   self._filter_break = True
        #   self._filter_busy = False
        #else:
        #    self._filter_busy = True
        #self._filter_break = False
            
        #print "filter by name", event.__dict__
        self._active = True
        operator = self.label["text"]
        if not self.key_name in self.info_grid.filter_cache.keys():
                self.info_grid.filter_cache[self.key_name] = {}
        if self.info_grid.filter_cache[self.key_name].get(operator, None) == None:
            self.info_grid.filter_cache[self.key_name][operator] = {}
        last_filter = self.info_grid.filter_cache[self.key_name][operator].get(self.all_filter_values(), None)
        _return = False
        if last_filter:
            self.info_grid.array = list(last_filter)
            if event.keysym in ("BackSpace", "Delete"):
                return
            #else:
            #return "refresh"
        else:
            #if self.info_grid.start_filter == self:
            if event.keysym != "filter_event":
                self.info_grid.array = list(self.info_grid.default_array)
                return
            return
            #self.info_grid.update_grid()

    

    

    


    
class FilterTable(Tkinter.Frame):
    default_column_width = 100
    def __init__(self, master, columns, **cnf):
        self.filter_cache = {}
        self.filters = []
        self.__columns = []
        self.columns = columns
        Tkinter.Frame.__init__(self, master, **cnf)
        self.selected = None
        self.create_frames()

    def create_frames(self):
        self.create_top()
        self.create_main()

    def create_top(self):
        self.top = top = Tkinter.Frame(self, bg = "#BBBBBB")
        columns = self.columns
        for i in range(len(columns)):
            name = columns[i]
            self.add_column(name, top)
        top.pack(fill = "both")

    def add_column(self, name, top):
        col = Tkinter.Frame(top)
        i = len(self.__columns)
        filter = Filter(self, name, i, top)
        entry = Entry(True, self, col, width = 1) #readonlybackground
        entry.set(name)
        resizer = Resizer(self, col, bg = "#000000", width = 5, height = 21, cursor = 'sb_h_double_arrow')
        #entry.grid(row = 0, column = 0, sticky = "we")
        #resizer.grid(row = 0, column = 1, sticky = "e")
        entry.pack(side = "left", fill = "both", expand = 1)
        resizer.pack(side = "right")
        top.columnconfigure(i, minsize = self.default_column_width)
        filter.grid(row = 0, column = i, sticky = "we")
        col.grid(row = 1, column = i, sticky = "we")
        col.entry = entry
        col.filter = filter
        col.index = filter.index = i
        self.__columns.append(col)
    

    def create_main(self):
        self.main = main = Tkinter.Frame(self)
        try:
            self.winfo_toplevel().bind_wheel(main, self.on_wheel)
        except:
            print("couldn't bind wheel")
        main.pack(fill = "both")
        self.vscroll = vscroll = Tkinter.Scrollbar(main)
        self.hscroll = hscroll = Tkinter.Scrollbar(main, orient = "h")
        self._grid = grid = Tkinter.Frame(main, bg = "#BBBBBB")
        grid.grid(row = 0, column = 0, sticky = "nsew")
        vscroll.grid(row = 0, column = 1, sticky = "nse")
        hscroll.grid(row = 1, column = 0, sticky = "ews")

        main.grid_columnconfigure(0, weight = 1)
        main.grid_rowconfigure(0, weight = 1)

        self.vscroll["command"] = self.yview
        self.hscroll["command"] = self.xview
        #self.canvas["yscrollcommand"] = self.vscroll.set
        #self.canvas["xscrollcommand"] = self.hscroll.set
        grid.bind('<Button-1>', self.on_grid_click)
        grid.bind('<Double-1>', self.on_grid_doubleclick)


    def on_grid_click(self, event):
        row = self.grid.grid_location(event.x, event.y)[1]
        self.select_row(row)
        return "break"

    def on_grid_doubleclick(self, event):
        ##click always preceedes doubleclick
        #row = self.grid.grid_location(event.x, event.y)[1]
        self.activate_row()
        return "break"

    def select_row(self, row):
        self.selected = row + self.yscroll_offset
        self.update_grid(True)
        print("select row: %i" % row) ###self.set(self.array[int(self.selected)])

    def select_set(self, offset):
        self.selected += offset
        
        ##self.set(self.array[int(self.selected)])

    def activate_row(self):
        #cf.set(self.CardsArray.array(self.selected))
        pass#print "activated %s %s" % (self.selected, self.array[self.selected][0])
        

    def on_wheel(self, event):
        #print event.__dict__
        if event.delta > 0:
            self.yscroll_offset -= event.delta / 120 * 3
            if self.yscroll_offset < 0:
                self.yscroll_offset = 0
        if event.delta < 0:
            self.yscroll_offset -= event.delta /120 * 3
            total = len(self.array)
            if self.yscroll_offset > total:
                self.yscroll_offset = total
        self.update_grid()
        self.yscrollcommand()
    yscroll_offset = 0
    def yscrollcommand(self):
        total = len(self.array) or 1
        visible = len(self.grid_array)
        offset = self.yscroll_offset
        if not offset:
            upper = 0.0
        else:
            upper = offset / float(total)
        lower = upper + visible / float(total)
        #print upper, lower
        self.vscroll.set(upper, lower)

    def yview(self, *args):
        total = len(self.array)
        pagesize = len(self.grid_array)
        if args[0] == "moveto":
            self.yscroll_offset = int(total * float(args[1]))
        if args[0] == "scroll":
            what = args[2]
            ammount = int(args[1])
            if what == "pages":
                
                self.yscroll_offset += ammount * pagesize
            elif what == "units":
                self.yscroll_offset += ammount
        if self.yscroll_offset < 0:
            self.yscroll_offset = 0
        if self.yscroll_offset > total - pagesize:
            self.yscroll_offset = total - pagesize
        self.update_grid()
        self.yscrollcommand()

    def xview(self, args):
        pass#print args
        
    bgcolor0 = "#FFFFFF"
    bgcolor1 = "#DDDDDD"
    selbgcolor = "#9999FF"
    def create_grid(self, height):
        columnsw = self.columnsw = self.top.grid_slaves(row = 1)
        self.grid_array = []
        for i in range(height):
            row = []
            for j in range(len(columnsw)):
                bg = self.bgcolor0
                if i % 2 == 1:
                    bg = self.bgcolor1
                entry = Entry(False, self, self._grid, bg = bg, width = 1)
                entry.grid(row = i, column = j, sticky = "we", padx = 5)
                row.append(entry)
            self.grid_array.append(row)
            

    def sort_by_index(self, column, reverse = False):
        global sort
        #print "sort_by %s" % column
        items = {}
        array = self.array
        for i in range(len(array)):
            key = array[i][column]
            #if not items.has_key(key):
            if items.get(key, "n0kEy") == "n0kEy":
                items[key] = [i]
            else:
                items[key].append(i)
        sort = sorted(items.keys())
        new = []
        for key in sort:
            for i in items[key]:
                new.append(array[i])
        if reverse:
            new = list(reversed(new))
        self.array = new
        self.update_grid()

    def update_grid(self, color_only = False):
        rowsnum = len(self.top.grid_slaves(row = 1))
        for i in range(len(self.grid_array)):
            row = self.grid_array[i]
            for j in range(rowsnum):
                entry = row[j]
                if not color_only:
                    try:
                        entry.set(str(self.array[i + int(self.yscroll_offset)][j]))
                    except IndexError:
                        entry.clear()
                if i + self.yscroll_offset == self.selected:
                    entry["bg"] = self.selbgcolor
                    entry["readonlybackground"] = self.selbgcolor
                elif (i + self.yscroll_offset) % 2 == 0:
                    entry["bg"] = self.bgcolor0
                    entry["readonlybackground"] = self.bgcolor0
                else:
                    entry["bg"] = self.bgcolor1
                    entry["readonlybackground"] = self.bgcolor1
        self._grid.update_idletasks()
        for i in range(len(self.columnsw)):
            gwidth = self._grid.grid_bbox(column = i, row = 0)[2]
            cwidth = self.top.grid_bbox(column = i, row = 0)[2]
            #if cwidth <= gwidth:
            #    self.top.columnconfigure(i, minsize = gwidth)
            if cwidth > gwidth:
                self._grid.columnconfigure(i, minsize = cwidth)
        self.yscrollcommand()

    def set_array(self, array, types = None):
        self.array = array
        self.default_array = list(array)
        self.filter_cache = {}
        self.filter_cache[self.filters[0].all_filter_values()] = array
        if types:
            self.set_filter_types(types)

    def set_filter_types(self, types):
        for i in range(len(self.filters)):
            self.filters[i].filter_type = types[i]


def on_mouse_wheel(event):
    """* if event is bound to child and parent widgets, only last child widget event will be triggered
    """
    ##print(event.__dict__)
    widgets = wheel_bindings.keys()
    top = event.widget.winfo_toplevel()
    ewidget = top.winfo_containing(event.x_root, event.y_root)
    call = False
    if ewidget in widgets:
        call = wheel_bindings[widget]
    else:
        while ewidget.master:
            ewidget = ewidget.master
            if ewidget in widgets:
                call = wheel_bindings[ewidget]
                break
    if call:
        try:
            call(event)
        except:
            sys.stderr.write("\n%s" % traceback.format_exc())

wheel_bindings = {}

def bind_wheel(widget, function):
    """binds widget to mouse wheel event
    """
    wheel_bindings[widget] = function

    
if __name__ == "__main__":
    root = Tkinter.Tk()
    root.wm_title("FlterTable test")
    root.bind_wheel = bind_wheel
    root.bind("<MouseWheel>", on_mouse_wheel)
    t = FilterTable(root, [])
    for i in range(10):
        t.add_column("column %i" % i, t.top)
    t.pack(expand=1, fill = "both")

    a = []
    for i in range(100000):
        a.append([])
        for j in range(10):
            if j == 0:
                a[i].append(i)
            else:
                a[i].append("%i %i" % (i, j))
    t.set_array(a)
    t.create_grid(25)
    t.update_grid()


    ##Tkinter.mainloop()  #Enable this if not running on idle on python 3
