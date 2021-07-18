import tkinter as tk
from functools import partial


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
    def __init__(self, master, position, video, image, command=None):
        super().__init__(master, borderwidth=3, highlightcolor="green", relief=tk.FLAT, image=image)
        self.position = position
        self.image = image
        self.video = video

        self.configure(command=command)
        self.photo = image


class ToolTip:

    def __init__(self, tip, widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.text = tip

    def showtip(self, _pass):
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self, _pass):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

