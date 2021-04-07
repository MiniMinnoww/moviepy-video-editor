import tkinter as tk
from functools import partial
from threading import Thread

import numpy as np
import pygame as pg
from PIL import Image, ImageTk
import sys
import config


class DragManager:
    def add_draggable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_start, add="+")
        widget.bind("<B1-Motion>", self.on_drag, add="+")
        widget.bind("<ButtonRelease-1>", self.on_drop, add="+")
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
        try:
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
            config.clipFrames = new

            # except Exception as e:
            #     print(e)
        except:
            pass

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
    def __init__(self, master, image=None, command=None):
        super().__init__(master, borderwidth=3, highlightcolor="green", relief=tk.FLAT, image=image)

        # mgr = DragManager()
        self.configure(command=command)
        # mgr.add_draggable(self)
        self.photo = image


class VideoClipFilePlayer:
    def __init__(self, master, **kwargs):
        bg = kwargs.get("bg", "#000000")
        fg = kwargs.get("fg", "#FFFFFF")
        default_image = np.zeros([720, 1280, 3], dtype=np.uint8)

        self.display = tk.Label(master, bg=bg, fg=fg)
        self.display.pack()
        img = Image.fromarray(default_image, 'RGB')
        img = img.resize((round(img.width / 1.5), round(img.height / 1.5)), Image.ANTIALIAS)
        self.default_image = ImageTk.PhotoImage(img)

        self.display.configure(image=self.default_image)
        self.display.photo = self.default_image
        self.toggle_button = tk.Button(master, bg=bg, fg=fg, text="Play/Pause", command=self.toggle_play)
        self.toggle_button.pack()
        self.audio = None
        self.video = None
        self.paused = True
        self.stop = False

    def load(self, video):
        self.stop = True
        try:
            self.unload()
        except Exception as e:
            print(e)
        self.video = video
        for f in self.video.iter_frames():
            print(f.shape)
            img = Image.fromarray(f, 'RGB')
            img = img.resize((round(img.width / 1.5), round(img.height / 1.5)), Image.ANTIALIAS)
            tkImage = ImageTk.PhotoImage(img)
            self.display.configure(image=tkImage)
            self.display.photo = tkImage
            break
        pg.mixer.pre_init(frequency=44100, size=-16, channels=1)
        pg.mixer.init()
        pg.mixer.set_num_channels(1)
        prev_audio = self.video.audio.set_fps(44100)
        prev_audio = prev_audio.to_soundarray()
        prev_audio = np.reshape(prev_audio, (-1, 2))
        prev_audio = np.int16(prev_audio * (2 ** 15))

        self.audio = pg.sndarray.make_sound(prev_audio)
        self.audio.play()
        pg.mixer.pause()
        self.paused = True
        self.stop = False
        videoThread = Thread(target=self._video_play)
        videoThread.start()

    def toggle_play(self):
        if self.paused:
            self.play()
        else:
            self.pause()

    def play(self):
        self.paused = False
        self._audio_play()

    def pause(self):
        self.paused = True
        self._audio_pause()

    def _audio_pause(self):
        pg.mixer.pause()

    def _audio_play(self):
        pg.mixer.unpause()

    def _video_play(self):
        print("Video play")
        for frame in self.video.iter_frames():
            if self.stop:
                sys.exit()
            while self.paused: pass
            img = Image.fromarray(frame, 'RGB')

            img = img.resize((round(img.width / 1.5), round(img.height / 1.5)), Image.ANTIALIAS)
            tkImage = ImageTk.PhotoImage(img)

            self.display.configure(image=tkImage)
            self.display.photo = tkImage
            
    def unload(self):
        self.display.configure(image=self.default_image)
        self.display.photo = self.default_image
        self.audio.stop()
        self.audio = None
        self.video = None
        self.paused = True
        self.stop = False
        pg.mixer.stop()

