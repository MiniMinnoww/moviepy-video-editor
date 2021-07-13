# Import Modules
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox as box
from functools import partial

from PIL import Image as Img
from PIL import ImageTk as ImgTK

import config
import vidTk as vtk
from editorFuncts import *

tooltips = []


def getImages(sprite_sheet,
              x):  # Get all individual images from the sprite sheet ('x' is the number of items on the sheet)
    im = Img.open(sprite_sheet)
    w, h = im.size
    ww = w // x
    images = []
    for n in range(0, x):
        images.append(im.crop((ww * n, 0, ww * (n + 1), h)))
    del images[6]
    return images


# Function to know when user slides the slider
def sliderUpdate(val):
    return val


# Adds a tooltip to the button
def addToolTip(widget, tip):
    tooltips.append(vtk.ToolTip(tip, widget))
    widget.bind('<Enter>', tooltips[len(tooltips) - 1].showtip, add="+")
    widget.bind('<Leave>', tooltips[len(tooltips) - 1].hidetip, add="+")


# Main for video window
class main:
    def __init__(self, prints=True):
        self.prints = prints
        self.oldConfig = config.clipFrames
        self._bgcolor = '#000000'
        self._framebg = "#2E2E2E"
        _fgcolor = '#000000'

        config.clipFrames = {}
        self.sliderPos = 1
        self.displaying = False
        self.paused = False
        self.selectedClip = ""
        self.selectedColor = "#000000"
        self.editor = Editor()

        self.root = tk.Tk()

        self.root.geometry("1537x877+271+154")
        self.root.minsize(120, 1)
        self.root.maxsize(1604, 881)
        self.root.resizable(1, 1)
        self.root.title("Video Editor")
        self.root.configure(background=self._bgcolor)
        self.root.state("zoomed")

        self.selectionInfo = tk.Label(self.root, text="", font=('Helvetica', 9), bg=self._bgcolor, fg="#FFFFFF")
        self.root.update()
        self.selectionInfo.place(x=0, y=835)

        imageLst = getImages("spritesheet.png", 8)

        _addImage = ImgTK.PhotoImage(imageLst[1])
        _switchImage = ImgTK.PhotoImage(imageLst[5])
        _trimImage = ImgTK.PhotoImage(imageLst[6])
        _autoTrimImage = ImgTK.PhotoImage(imageLst[3])
        _autoStartImage = ImgTK.PhotoImage(imageLst[0])
        _exportImage = ImgTK.PhotoImage(imageLst[4])
        _addTextImage = ImgTK.PhotoImage(imageLst[2])

        self.videoPlayer = tk.Frame(self.root)
        self.videoPlayer.place(relx=0.371, rely=0.011, relheight=0.593, relwidth=0.618)
        self.videoPlayer.configure(relief='flat')
        self.videoPlayer.configure(borderwidth="2")
        self.videoPlayer.configure(relief="flat")
        self.videoPlayer.configure(background=self._framebg)

        self.clipTimeline = tk.Frame(self.root)
        self.clipTimeline.place(relx=0.007, rely=0.627, relheight=0.35, relwidth=0.986)

        self.clipTimeline.configure(relief='flat')
        self.clipTimeline.configure(borderwidth="2")
        self.clipTimeline.configure(relief="flat")
        self.clipTimeline.configure(background=self._framebg)

        self.menubar = tk.Menu(self.root, font="TkMenuFont", bg=self._bgcolor, fg=_fgcolor,
                               activebackground=self._bgcolor, activeforeground=_fgcolor)

        self.editMenu = tk.Menu(self.menubar, tearoff=0)

        self.editMenu.add_command(label="Undo", command=None)
        self.editMenu.add_command(label="Redo", command=None)
        self.editMenu.add_separator()
        self.editMenu.add_command(label="Add Clip", command=self.getClipPath)
        self.editMenu.add_command(label="Export video", command=self.finishVideo)

        self.menubar.add_cascade(label="Edit", menu=self.editMenu)
        self.root.configure(menu=self.menubar)

        self.menuFrame = tk.Frame(self.root)
        self.menuFrame.place(relx=0.007, rely=0.011, relheight=0.542, relwidth=0.354)
        self.menuFrame.configure(relief='flat')
        self.menuFrame.configure(borderwidth="2")
        self.menuFrame.configure(relief="flat")
        self.menuFrame.configure(background=self._framebg)

        self.scrollbar = tk.Scale(self.clipTimeline, orient=tk.HORIZONTAL, length=1400, showvalue=False,
                                  highlightbackground=self._framebg, bg=self._framebg, activebackground="black",
                                  relief=tk.FLAT,
                                  troughcolor=self._framebg, from_=0, to=30, command=self.sliderUpdate)
        self.scrollbar.place(relx=0.5, y=290, anchor=tk.CENTER)

        self.buttons = []
        self.buttonTips = ["Select and Add a clip to the project", "Render/Export your video"]
        self.commands = [self.getClipPath, self.finishVideo]
        self.images = [_addImage, _exportImage]

        for index, tip in enumerate(self.buttonTips):
            self.buttons.append(
                vtk.Button(self.root, image=self.images[index], command=self.commands[index]))
            self.buttons[index].place(x=index * 30, y=490)

            addToolTip(self.buttons[index], tip)
        if self.prints: print("Main initialised")

    def addClip(self, path):
        """
        Adds a clip object to the clip dictionary (config.clipFrames) along with an image on the clip timeline.
        :param path: Path to the video file
        :return:
        """
        clipNum = len(config.clipFrames)
        clipName = "clip" + str(clipNum)

        vid = VideoFileClip(path)
        image = vid.get_frame(1)
        img = Img.fromarray(image, 'RGB')
        img = img.resize((300, 200), Img.ANTIALIAS)
        tkImage = ImgTK.PhotoImage(img)
        pos = 20 + (tkImage.width() * clipNum) + (20 * clipNum)

        btn = vtk.ClipButton(self.clipTimeline, image=tkImage, position=pos, video=vid)

        config.clipFrames[clipName] = btn
        config.clipFrames[clipName].configure(command=lambda: self.buttonSelect(config.clipFrames[clipName]))
        config.clipFrames[clipName].bind("<Double-Button-1>", self.doubleClick)
        config.clipFrames[clipName].place(x=btn.position, y=50)

    def finishVideo(self, export=False):
        """
        Exports/Renders the video
        :return:
        """
        if not export:
            self.finishRoot = tk.Tk()
            self.finishRoot.title("Export Video")
            self.finishRoot.configure(bg=self._bgcolor)

            presetOptions = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower",
                             "veryslow", "placebo"]

            tkinter.Label(self.finishRoot, text="Video Name", bg=self._bgcolor, relief=tk.FLAT, fg="#FFFFFF").grid(
                row=1, column=1)
            tkinter.Label(self.finishRoot, text="Video fps", bg=self._bgcolor, relief=tk.FLAT, fg="#FFFFFF").grid(row=2,
                                                                                                                  column=1)
            tkinter.Label(self.finishRoot, text="Speed", bg=self._bgcolor, relief=tk.FLAT, fg="#FFFFFF").grid(row=3,
                                                                                                              column=1)

            self.nameEntry = tk.Entry(self.finishRoot, bg=self._framebg, relief=tk.FLAT, fg="#FFFFFF")
            self.nameEntry.grid(row=1, column=2)

            self.fpsEntry = tk.Entry(self.finishRoot, bg=self._framebg, relief=tk.FLAT, fg="#FFFFFF")
            self.fpsEntry.grid(row=2, column=2)

            self.speedList = tk.Spinbox(self.finishRoot, values=presetOptions, background=self._framebg,
                                        foreground="#FFFFFF", relief=tk.FLAT)
            self.speedList.grid(row=3, column=2)

            finishButton = vtk.Button(self.finishRoot, text="Export Video", command=partial(self.finishVideo, True))
            finishButton.grid(row=4, column=1, columnspan=2)

        else:
            try:
                videoName = self.nameEntry.get()
                clips = []
                for key in list(config.clipFrames.keys()):
                    clips.append(config.clipFrames[key][1])  # VideoFile object

                for index, clip in enumerate(clips):
                    clips[index] = clip.without_audio().set_audio(clip.audio)
                final_clip = concatenate_videoclips(clips)
                if self.fpsEntry.get() != "":
                    final_clip = final_clip.set_fps(int(self.fpsEntry.get()))
                final_clip.write_videofile(videoName + ".mp4", preset=str(self.speedList.get()), threads=6)
                if self.prints: print("Video exported")
                box.showinfo("Success", "Your video has been successfully created!")
            except Exception as e:
                if self.prints: print(f"Video export failed: {e}")

    def getClipPath(self):
        clips = tkinter.filedialog.askopenfilenames(title="Choose Clip File")

        clips = [clip.replace("/", "\\") for clip in clips]  # For consistency
        for clip in clips:
            self.addClip(clip)

    def sliderUpdate(self, val):
        self.sliderPos = int(val)
        for key in list(config.clipFrames.keys()):
            config.clipFrames[key][0].place_forget()
            config.clipFrames[key][0].place(x=(config.clipFrames[key][2]) - (self.sliderPos * 100), y=50)

    def buttonSelect(self, button):
        for key, value in config.clipFrames.items():
            if button == value[0]:
                self.selectedClip = key
                self.selectedClipInfo = value[1]

        for key in list(config.clipFrames.keys()):
            config.clipFrames[key][0].configure(bg="gray")
        button.configure(bg="green")
        self.updateInfoOnSelection()

    def updateInfoOnSelection(self):
        try:
            selectedObject = self.selectedClipInfo  # MoviePy VideoClip object
            clipName = self.selectedClip
            clipDur = selectedObject.duration
            clipFps = selectedObject.fps
            audDur = selectedObject.audio.duration
            text = f" Clip: {clipName},    Duration: {clipDur},    FPS: {clipFps},     Audio: {audDur}"
            self.selectionInfo.configure(text=text)
        except:
            self.selectionInfo.configure(text="Nothing selected")

    def doubleClick(self, event):
        print("Double clicked")



if __name__ == '__main__':
    a = main(prints=False)
    a.root.mainloop()
