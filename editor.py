
import os
import tkinter as Tkinter
import traceback
import sys
import imp



def reload_gui(*event):
    print("reload")
    global editor_gui
    for child in list(root.children.values()):
        child.destroy()
    editor_gui = imp.reload(editor_gui)
    editor_gui.root = root
    editor_gui.build_gui()

def on_mouse_wheel(event):
    """* if event is bound to child and parent widgets, only last child widget event will be triggered
    """
    widgets = wheel_bindings.keys()
    ewidget = root.winfo_containing(event.x_root, event.y_root)
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


def reload_gui():
    print ("reload function here")
    pass


def main():
    global root
    root = Tkinter.Tk()
    root.wm_title("sql editor by vYk")

    root.bind("<Control-Key-R>", reload_gui)
    root.bind("<Control-Key-r>", reload_gui)
    root.bind("<MouseWheel>", on_mouse_wheel)
    root.bind_wheel = bind_wheel

if __name__ == "__main__":
    #root.mainloop()
    pass
