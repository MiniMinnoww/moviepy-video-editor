import tkinter as tk
from functools import partial
import window
import config

class DragManager:
    def add_dragable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)
        widget.configure(cursor="hand1")

    def on_start(self, event):
        # you could use this method to create a floating window
        # that represents what is being dragged.
        pass

    def on_drag(self, event):
        # you could use this method to move a floating window that
        # represents what you're dragging
        pass

    def on_drop(self, event):
        # find the widget under the cursor
        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x, y)
        # try:
        # targetImg = target.cget("image")
        # eventImg = event.widget.cget("image")
        # target.configure(image=eventImg)
        # event.widget.configure(image=targetImg)
        key1 = ""
        key2 = ""
        for x in list(config.clipFrames.keys()):
            if config.clipFrames[x][0] == event.widget:
                key1 = x
            elif config.clipFrames[x][0] == target:
                key2 = x
        new = {}
        for x in list(config.clipFrames.keys()):
            if x == key1:
                new[key2] = config.clipFrames[key2]
            elif x == key2:
                new[key1] = config.clipFrames[key1]
            else:
                new[x] = config.clipFrames[x]
        print(config.clipFrames)
        print(new)
        config.clipFrames = new

        # except Exception as e:
        #     print(e)

def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


def changeButtonBG(t, btn, _):
    if t == 1:
        btn.configure(bg="#1C1C1C")
    else:
        btn.configure(bg="#000000")


# def messagebox(title: str, text: str, options: tuple):
#     msg_root = tk.Tk()
#     msg_root.title(title)
#     msg_root.geometry("250x100")
#     msg_root.resizable(0, 0)
#     msg_root.configure(bg="#000000")
#     msg_root.overrideredirect(True)
#     center(msg_root)
#
#     label = tk.Label(msg_root, text=text, bg="#000000", fg="#FFFFFF")
#     label.pack(pady=10)
#     for indx, option in enumerate(options):
#         tk.Button(msg_root, text=option, command=partial()).grid(row=2, column=indx + 1)
#     msg_root.mainloop()

class Button(tk.Button):
    def __init__(self, master, text=None, image=None, command=None):
        if text is not None:
            super().__init__(master, text=text, command=command, bg="#000000", relief=tk.FLAT, fg="#FFFFFF")
        elif image is not None:
            super().__init__(master, image=image, command=command, bg="#000000", relief=tk.FLAT, fg="#FFFFFF")
            self.photo = image
        else:
            raise ValueError("'text' or 'image' parameter needs to be set!")
        self.bind('<Enter>', func=partial(changeButtonBG, 1, self), add="+")
        self.bind('<Leave>', func=partial(changeButtonBG, 0, self), add="+")


class ClipButton(tk.Button):
    def __init__(self, master, image=None, command=None, ):
        super().__init__(master, borderwidth=3, highlightcolor="green", relief=tk.FLAT, image=image)

        mgr = DragManager()
        self.configure(command=command)
        mgr.add_dragable(self)
        self.photo = image
