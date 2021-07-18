import tkinter as tk
from info.info import *

class trimClip(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master=master)
        self.configure(bg=background)
