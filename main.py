# Import Modules
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import tkinter.messagebox as box
import tkinter.colorchooser as chooser
from collections import OrderedDict
from functools import partial
from random import randint
from threading import Thread
from timeme import timeme
from PIL import Image as Img
from PIL import ImageTk as ImgTK
from editorFuncts import *
from moviepy.editor import *
from time import sleep

tooltips = []


def getImages(sprite_sheet, x):
    im = Img.open(sprite_sheet)
    w, h = im.size
    ww = w // x
    images = []
    for n in range(0, x):
        images.append(im.crop((ww * n, 0, ww * (n + 1), h)))
    return images

# Function to know when user slides the slider
def sliderUpdate(val):
    return val


# Function to highlight the button background when hover
def changeButtonBG(t, btn, _):
    if t == 1:
        btn.configure(bg="#1C1C1C")
    else:
        btn.configure(bg="#000000")


# Adds a tooltip to the button
def addToolTip(widget, tip):
    tooltips.append(ToolTip(tip, widget))
    widget.bind('<Enter>', tooltips[len(tooltips) - 1].showtip, add="+")
    widget.bind('<Leave>', tooltips[len(tooltips) - 1].hidetip, add="+")


# A listbox class to let user drag and drop elements
class Drag_and_Drop_Listbox(tkinter.Listbox):
    def __init__(self, master, **kw):
        kw['selectmode'] = tkinter
        kw['activestyle'] = 'none'
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.getState, add='+')
        self.bind('<Button-1>', self.setCurrent, add='+')
        self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None
        self.curState = None

    def setCurrent(self, event):
        self.curIndex = self.nearest(event.y)

    def getState(self, event):
        i = self.nearest(event.y)
        self.curState = self.selection_includes(i)

    def shiftSelection(self, event):
        i = self.nearest(event.y)
        if self.curState == 1:
            self.selection_set(self.curIndex)
        else:
            self.selection_clear(self.curIndex)
        if i < self.curIndex:
            # Moves up
            x = self.get(i)
            selected = self.selection_includes(i)
            self.delete(i)
            self.insert(i + 1, x)
            if selected:
                self.selection_set(i + 1)
            self.curIndex = i
        elif i > self.curIndex:
            # Moves down
            x = self.get(i)
            selected = self.selection_includes(i)
            self.delete(i)
            self.insert(i - 1, x)
            if selected:
                self.selection_set(i - 1)
            self.curIndex = i


# Main for video window
class main:
    def __init__(self):
        self._bgcolor = '#000000'
        self._framebg = "#2E2E2E"
        _fgcolor = '#000000'

        self.clipFrames = {}
        self.loader = Loading_Bar()
        self.sliderPos = 1
        self.displaying = False
        self.paused = False
        self.selectedClip = ""
        self.selectedColor = "#000000"  # This is because buttons don't return value
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
        _trimImage = ImgTK.PhotoImage(imageLst[7])
        _autoTrimImage = ImgTK.PhotoImage(imageLst[3])
        _autoStartImage = ImgTK.PhotoImage(imageLst[0])
        _previewImage = ImgTK.PhotoImage(imageLst[6])
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
        self.videoMenu = tk.Menu(self.menubar, tearoff=0)

        self.editMenu.add_command(label="Add Clip", command=self.getClipPath)
        self.editMenu.add_command(label="Order Clips", command=self.reorderClips)
        self.editMenu.add_command(label="Trim Clip", command=self.trimClip)
        self.editMenu.add_command(label="Auto-Cut clip", command=self.cutOutAudio)
        self.editMenu.add_command(label="Add margin", command=self.addMargin, state=tk.DISABLED)

        self.videoMenu.add_command(label="Preview video", command=self._preview)
        self.videoMenu.add_command(label="Export video", command=self.finishVideo)

        self.menubar.add_cascade(label="Edit", menu=self.editMenu)
        self.menubar.add_cascade(label="Video", menu=self.videoMenu)
        self.root.configure(menu=self.menubar)

        self.menuFrame = tk.Frame(self.root)
        self.menuFrame.place(relx=0.007, rely=0.011, relheight=0.542, relwidth=0.354)
        self.menuFrame.configure(relief='flat')
        self.menuFrame.configure(borderwidth="2")
        self.menuFrame.configure(relief="flat")
        self.menuFrame.configure(background=self._framebg)
        tk.Label(self.menuFrame, text="ADD TEMP_ROOT HERE").pack()

        self.scrollbar = tk.Scale(self.clipTimeline, orient=tk.HORIZONTAL, length=1400, showvalue=False,
                                  highlightbackground=self._framebg, bg=self._framebg, activebackground="black",
                                  relief=tk.FLAT,
                                  troughcolor=self._framebg, from_=0, to=30, command=self.sliderUpdate)
        self.scrollbar.place(relx=0.5, y=290, anchor=tk.CENTER)

        self.buttons = []
        self.buttonTips = ["Select and Add a clip to the project", "Order the clips in your project",
                           "Trim the selected clip", "Add text to a clip - (Disabled because of MoviePy error)",
                           "Cut out audio breaks in the selected clip",
                           "Cut out audio break at the start of the clip", "Preview clip (in new window)",
                           "Render/Export your video"]
        self.commands = [self.getClipPath, self.reorderClips, self.trimClip, self.addText, self.cutOutAudio,
                         self.cutOutStart, self._preview,
                         self.finishVideo]
        self.images = [_addImage, _switchImage, _trimImage, _addTextImage, _autoTrimImage, _autoStartImage,
                       _previewImage, _exportImage]

        for index, tip in enumerate(self.buttonTips):
            state = tk.NORMAL
            self.buttons.append(
                tk.Button(self.root, image=self.images[index], command=self.commands[index], bg=self._bgcolor,
                          relief=tk.FLAT, state=state))

            self.buttons[index].photo = self.images[index]
            self.buttons[index].place(x=index * 30, y=490)
            self.buttons[index].bind('<Enter>', func=partial(changeButtonBG, 1, self.buttons[index]), add="+")
            self.buttons[index].bind('<Leave>', func=partial(changeButtonBG, 0, self.buttons[index]), add="+")

            addToolTip(self.buttons[index], tip)

    def addClip(self, path):
        """
        Adds a clip object to the clip dictionary (self.clipFrames) along with an image on the clip timeline.
        :param path: Path to the video file
        :return:
        """
        clipNum = len(self.clipFrames)
        clipName = "clip" + str(clipNum)

        vid = VideoFileClip(path)
        image = vid.get_frame(1)
        img = Img.fromarray(image, 'RGB')
        clip = f"clip {str(len(self.clipFrames))}.png"
        img.save(clip)
        tkImage = tk.PhotoImage(file=clip)
        tkImage = tkImage.subsample(4, 4)

        btn = tk.Button(self.clipTimeline, image=tkImage, borderwidth=3, highlightcolor="green", relief=tk.FLAT)
        pos = 20 + (tkImage.width() * clipNum) + (20 * clipNum)

        self.clipFrames[clipName] = [btn, vid, pos]
        self.clipFrames[clipName][0].configure(command=partial(self.buttonSelect, self.clipFrames[clipName][0]))
        self.clipFrames[clipName][0].photo = tkImage
        self.clipFrames[clipName][0].place(x=self.clipFrames[clipName][2], y=50)

    def reloadOrder(self):
        """
        Reloads the order of clips on the timeline
        :return:
        """
        temp_loader = Loading_Bar()
        if __name__ == "__main__":
            loadThread = Thread(target=Loading_Bar.startLoad, args=(temp_loader, "Reordering Clips"))
            loadThread.start()
        xPos = 20
        for index, item in enumerate(list(self.clipFrames.keys())):
            try:
                self.clipFrames[item][0].destroy()
            except:
                pass
            image = self.clipFrames[item][1].get_frame(1)
            img = Img.fromarray(image, 'RGB')
            clip = f"clip {str(len(self.clipFrames))}.png"
            img.save(clip)
            tkImage = tk.PhotoImage(file=clip)
            tkImage = tkImage.subsample(4, 4)
            self.clipFrames[item][0] = tk.Button(self.clipTimeline, image=tkImage, borderwidth=3,
                                                 highlightcolor="green", relief=tk.FLAT)
            self.clipFrames[item][0].configure(command=partial(self.buttonSelect, self.clipFrames[item][0]))
            self.clipFrames[item][0].photo = tkImage
            self.clipFrames[item][0].place(x=xPos, y=50)
            xPos += 20 + tkImage.width()
            print(xPos)
        temp_loader.stopLoad()

    def finishVideo(self, export=False):
        """
        Exports/Renders the video
        :return:
        """
        if not export:
            self.finishRoot = tk.Tk()
            self.finishRoot.title("Export Video")
            self.finishRoot.configure(bg=self._bgcolor)

            presetOptions = ["ultra fast", "super fast", "very fast", "faster", "fast", "medium", "slow", "slower",
                             "very slow", "placebo"]

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

            finishButton = tkinter.Button(self.finishRoot, text="Export Video", command=partial(self.finishVideo, True),
                                          bg=self._bgcolor, relief=tk.FLAT, fg="#FFFFFF")
            finishButton.grid(row=4, column=1, columnspan=2)
            finishButton.bind('<Enter>', func=partial(changeButtonBG, 1, finishButton), add="+")
            finishButton.bind('<Leave>', func=partial(changeButtonBG, 0, finishButton), add="+")

        else:
            videoName = self.nameEntry.get()
            clips = []
            for key in list(self.clipFrames.keys()):
                clips.append(self.clipFrames[key][1])  # VideoFile object

            for index, clip in enumerate(clips):
                clips[index] = clip.without_audio().set_audio(clip.audio)
            final_clip = concatenate_videoclips(clips)
            if self.fpsEntry.get() != "":
                print("hello there")
                final_clip = final_clip.set_fps(int(self.fpsEntry.get()))
            print(f"Duration: {str(final_clip.duration)}, {str(final_clip.audio.duration)}")

            final_clip.write_videofile(videoName + ".mp4", threads=6)  # , preset=str(self.speedList.get())
            box.showinfo("Success", "Your video has been successfully created!")

    def cutOutAudio(self):
        if self.clipFrames[self.selectedClip][1] != '':
            vid = self.clipFrames[self.selectedClip][1]
            videoClipList = []
            x = 0
            if vid.duration > 300:
                for n in range(0, int(vid.duration / 300)):
                    videoClipList.append(vid.subclip(x, x + 300))
                    x += 300
                    if x > vid.duration: x = vid
            else:
                videoClipList.append(vid)
            print(f"There are {str(len(videoClipList))} clips to cut")
            cutVideos = []
            for vid in videoClipList:
                x = timeme(self.editor.cut_out_no_audio, 'both', vid)
                cutVideos.append(x[0])
            cutVideos = [clip.without_audio().set_audio(clip.audio) for clip in cutVideos]
            # cutVideos = [clip.set_duration(int(clip.duration)) for clip in cutVideos]
            concat = concatenate_videoclips(cutVideos)
            self.clipFrames[self.selectedClip][1] = concat
            print("FINISHED")

    def cutOutStart(self):
        if self.clipFrames[self.selectedClip][1] != '':
            # temp_loader = Loading_Bar()
            # if __name__ == "__main__":
            #     loadThread = Thread(target=Loading_Bar.startLoad, args=(temp_loader, "Auto-cutting your clips"))
            #     loadThread.start()
            self.clipFrames[self.selectedClip][1] = self.editor.cut_out_start(self.clipFrames[self.selectedClip][1])
            print("FINISHED")
            # temp_loader.stopLoad()

    def _preview(self):
        try:
            clips = []
            for lists in list(self.clipFrames.values()):
                clips.append(lists[1])

            to_play = concatenate_videoclips(clips)
            to_play = to_play.without_audio().set_audio(to_play.audio)
            to_play.set_fps(to_play.fps)
            to_play.preview()
        except ValueError as e:
            print(e)

        except Exception as e:
            print(e)

    def trimClip(self):
        self.reloadMenuFrame()
        if self.selectedClip != "":
            tkinter.Label(self.menuFrame, text="Start Trim: ").grid(row=0, column=0)
            self._entry1 = tk.Entry(self.menuFrame)
            self._entry1.grid(row=0, column=1)
            tkinter.Label(self.menuFrame, text="End Trim: ").grid(row=1, column=0)
            self._entry2 = tk.Entry(self.menuFrame)
            self._entry2.grid(row=1, column=1)
            trimButton = tk.Button(self.menuFrame, text="Trim", command=self._trim)
            trimButton.grid(row=2, column=0, columnspan=2)
        else:
            box.showwarning("You can't do this", "You need to select a clip to trim first!")

    def _trim(self):
        self.clipFrames[self.selectedClip][1] = self.editor.sub_clip(self.clipFrames[self.selectedClip][1],
                                                                     int(self._entry1.get()), int(self._entry2.get()))
        self.reloadMenuFrame()

    def getClipPath(self):
        clips = tkinter.filedialog.askopenfilenames(title="Choose Clip File")

        clips = [clip.replace("/", "\\") for clip in clips]  # For consistency
        temp_loader = Loading_Bar()
        if __name__ == "__main__":
            loadThread = Thread(target=Loading_Bar.startLoad, args=(temp_loader, "Adding Clips"))
            loadThread.start()
        for clip in clips:
            # try:
            self.addClip(clip)
            # except Exception as e:
            #     box.showerror("Error loading clip", "There was an error loading clip: " + os.path.basename(clip))
            #     print(e)
            #     print(e.args)
        temp_loader.stopLoad()

    def reorderClips(self):
        self.reloadMenuFrame()
        self.clipsList = Drag_and_Drop_Listbox(self.menuFrame)
        self.clipsList.pack()
        saveButton = tk.Button(self.menuFrame, text="Save New Order", command=self.saveOrder)
        saveButton.pack()
        for item in list(self.clipFrames.keys()):
            self.clipsList.insert(tk.END, item)

    def saveOrder(self):
        order = list(self.clipsList.get(0, tk.END))
        ordered = OrderedDict()
        for k in order:
            ordered[k] = self.clipFrames[k]
        self.clipFrames = dict(ordered)
        self.reloadMenuFrame()
        self.reloadOrder()
        self.updateInfoOnSelection()

    def sliderUpdate(self, val):
        self.sliderPos = int(val)
        for key in list(self.clipFrames.keys()):
            self.clipFrames[key][0].place_forget()
            self.clipFrames[key][0].place(x=(self.clipFrames[key][2]) - (self.sliderPos * 100), y=50)

    def buttonSelect(self, button):
        for key, value in self.clipFrames.items():
            if button == value[0]:
                self.selectedClip = key
                self.selectedClipInfo = value[1]

        for key in list(self.clipFrames.keys()):
            self.clipFrames[key][0].configure(bg="gray")
        if button["bg"] == "gray":
            button.configure(bg="green")
        self.updateInfoOnSelection()

    def addText(self, add=False):
        if self.selectedClip != "":
            if not add:
                self.temp_root = tk.Tk()
                self.temp_root.configure(bg=self._bgcolor)
                tk.Label(self.temp_root, text="Enter text here", background=self._bgcolor, foreground="#FFFFFF",
                         relief=tk.FLAT).grid(row=1, column=1)
                self.entry1 = tk.Entry(self.temp_root, background=self._framebg, foreground="#FFFFFF", relief=tk.FLAT)
                self.entry1.grid(row=1, column=2)

                tk.Label(self.temp_root, text="Select font size", background=self._bgcolor, foreground="#FFFFFF",
                         relief=tk.FLAT).grid(row=2, column=1)
                self.entry2 = tk.Entry(self.temp_root, background=self._framebg, foreground="#FFFFFF", relief=tk.FLAT)
                self.entry2.grid(row=2, column=2)

                tk.Label(self.temp_root, text="Enter x value (0 = left)", background=self._bgcolor,
                         foreground="#FFFFFF", relief=tk.FLAT).grid(row=4, column=1)
                self.entry3 = tk.Entry(self.temp_root, background=self._framebg, foreground="#FFFFFF", relief=tk.FLAT)
                self.entry3.grid(row=4, column=2)

                tk.Label(self.temp_root, text="Enter x value (0 = top)", background=self._bgcolor, foreground="#FFFFFF",
                         relief=tk.FLAT).grid(row=5, column=1)
                self.entry4 = tk.Entry(self.temp_root, background=self._framebg, foreground="#FFFFFF", relief=tk.FLAT)
                self.entry4.grid(row=5, column=2)

                colorBtn = tk.Button(self.temp_root, text="Select text colour", command=self.selectColour,
                                     background=self._bgcolor, foreground="#FFFFFF", relief=tk.FLAT)
                colorBtn.grid(row=6, column=1, columnspan=2)
                colorBtn.bind('<Enter>', func=partial(changeButtonBG, 1, colorBtn), add="+")
                colorBtn.bind('<Leave>', func=partial(changeButtonBG, 0, colorBtn), add="+")

                prevBtn = tk.Button(self.temp_root, text="Preview video", command=partial(self.addText, 2),
                                    background=self._bgcolor, foreground="#FFFFFF", relief=tk.FLAT)
                prevBtn.grid(row=7, column=1, columnspan=2)
                prevBtn.bind('<Enter>', func=partial(changeButtonBG, 1, prevBtn), add="+")
                prevBtn.bind('<Leave>', func=partial(changeButtonBG, 0, prevBtn), add="+")

                addBtn = tk.Button(self.temp_root, text="Add Text", command=partial(self.addText, 1),
                                   background=self._bgcolor, foreground="#FFFFFF", relief=tk.FLAT)
                addBtn.grid(row=8, column=1, columnspan=2)
                addBtn.bind('<Enter>', func=partial(changeButtonBG, 1, addBtn), add="+")
                addBtn.bind('<Leave>', func=partial(changeButtonBG, 0, addBtn), add="+")

            elif add == 1:
                # try:
                x = self.editor.addText(x=int(self.entry3.get()), y=int(self.entry4.get()), text=self.entry1.get(),
                                        videoObj=self.clipFrames[self.selectedClip][1], color=self.selectedColor,
                                        fontsize=int(self.entry2.get()))
                print(type(x))
                self.clipFrames[self.selectedClip][1] = x
                print(type(self.clipFrames[self.selectedClip][1]))
                # except:
                #     box.showwarning("Error", "There was an error adding text to the clip")
                self.temp_root.destroy()

            elif add == 2:
                x = self.editor.getTextPreview(x=int(self.entry3.get()), y=int(self.entry4.get()),
                                               text=self.entry1.get(),
                                               videoObj=self.clipFrames[self.selectedClip][1], color=self.selectedColor,
                                               fontsize=int(self.entry2.get()))
                for image in x.iter_frames():
                    img = Img.fromarray(image)
                    img = img.resize((400, 200), Img.ANTIALIAS)
                    TKImg = ImgTK.PhotoImage(img)
                    break
                self.reloadVideoFrame()
                self.img_label = tk.Label(self.videoPlayer, image=TKImg)
                self.img_label.pack()
                self.img_label.photo = TKImg
            else:
                box.showwarning("Error", "Please select a clip first")

    def updateInfoOnSelection(self):
        try:
            selectedObject = self.selectedClipInfo  # MoviePy VideoClip object
            clipName = self.selectedClip
            clipDur = selectedObject.duration
            clipFps = selectedObject.fps
            audDur = selectedObject.audio.duration
            clipPosition = list(self.clipFrames.keys()).index(self.selectedClip) + 1
            text = f" Clip: {clipName},    Duration: {clipDur},    FPS: {clipFps},    Position: {clipPosition},     Audio: {audDur}"
            self.selectionInfo.configure(text=text)
        except:
            self.selectionInfo.configure(text="Nothing selected")

    def reloadMenuFrame(self):
        try:
            self.menuFrame.destroy()
            self.menuFrame = tk.Frame(self.root)
            self.menuFrame.place(relx=0.007, rely=0.011, relheight=0.542, relwidth=0.354)
            self.menuFrame.configure(relief='flat')
            self.menuFrame.configure(borderwidth="2")
            self.menuFrame.configure(relief="flat")
            self.menuFrame.configure(background=self._framebg)
        except:
            pass

    def reloadVideoFrame(self):
        try:
            self.videoPlayer.destroy()
            self.videoPlayer = tk.Frame(self.root)
            self.videoPlayer.place(relx=0.371, rely=0.011, relheight=0.593, relwidth=0.618)
            self.videoPlayer.configure(relief='flat')
            self.videoPlayer.configure(borderwidth="2")
            self.videoPlayer.configure(relief="flat")
            self.videoPlayer.configure(background=self._framebg)
        except:
            pass

    def selectColour(self):
        colour = chooser.askcolor()
        self.selectedColor = str(colour[1]).upper()

    def addMargin(self, add=False):
        if self.selectedClip != "":
            if not add:
                self.temp_root = tk.Tk()
                self.temp_root.configure(bg=self._bgcolor)
                tk.Label(self.temp_root, text="Enter margin size: ", background=self._bgcolor, foreground="#FFFFFF",
                         relief=tk.FLAT).grid(row=1, column=1)
                self.entry01 = tk.Entry(self.temp_root, background=self._framebg, foreground="#FFFFFF", relief=tk.FLAT)
                self.entry01.grid(row=1, column=2)

                tk.Label(self.temp_root, text="Enter margin type (margin or border)", background=self._bgcolor,
                         foreground="#FFFFFF", relief=tk.FLAT).grid(row=2, column=1)
                self.entry03 = tk.Entry(self.temp_root, background=self._framebg, foreground="#FFFFFF", relief=tk.FLAT)
                self.entry03.grid(row=2, column=2)

                colorBtn = tk.Button(self.temp_root, text="Select margin color", command=self.selectColour,
                                     background=self._bgcolor, foreground="#FFFFFF", relief=tk.FLAT)
                colorBtn.grid(row=3, column=1, columnspan=2)
                colorBtn.bind('<Enter>', func=partial(changeButtonBG, 1, colorBtn), add="+")
                colorBtn.bind('<Leave>', func=partial(changeButtonBG, 0, colorBtn), add="+")

                prevBtn = tk.Button(self.temp_root, text="Preview video", command=partial(self.addMargin, 2),
                                    background=self._bgcolor, foreground="#FFFFFF", relief=tk.FLAT, state=tk.DISABLED)
                prevBtn.grid(row=4, column=1, columnspan=2)
                prevBtn.bind('<Enter>', func=partial(changeButtonBG, 1, prevBtn), add="+")
                prevBtn.bind('<Leave>', func=partial(changeButtonBG, 0, prevBtn), add="+")

                addBtn = tk.Button(self.temp_root, text="Add Margin", command=partial(self.addMargin, 1),
                                   background=self._bgcolor, foreground="#FFFFFF", relief=tk.FLAT)
                addBtn.grid(row=5, column=1, columnspan=2)
                addBtn.bind('<Enter>', func=partial(changeButtonBG, 1, addBtn), add="+")
                addBtn.bind('<Leave>', func=partial(changeButtonBG, 0, addBtn), add="+")

            elif add == 1:
                x = self.editor.addMargin(vid=self.clipFrames[self.selectedClip][1], size=int(self.entry01.get()),
                                          type=self.entry03.get(), color=self.selectedColor)
                self.clipFrames[self.selectedClip][1] = x
                self.temp_root.destroy()

            elif add == 2:
                x = self.editor.getMarginPreview(vid=self.clipFrames[self.selectedClip][1],
                                                 size=int(self.entry01.get()), type=self.entry03.get(),
                                                 color=self.selectedColor)
                for image in x.iter_frames():
                    img = Img.fromarray(image)
                    img = img.resize((400, 200), Img.ANTIALIAS)
                    TKImg = ImgTK.PhotoImage(img)
                    break
                self.reloadVideoFrame()
                self.img_label = tk.Label(self.videoPlayer, image=TKImg)
                self.img_label.pack()
                self.img_label.photo = TKImg
            else:
                box.showwarning("Error", "Please select a clip first")


if __name__ == "__main__":
    a = main()
    a.root.mainloop()
