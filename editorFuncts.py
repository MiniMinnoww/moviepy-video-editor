from moviepy.editor import *
from tkinter import *
import tkinter.ttk as ttk
from numba import jit
from threading import Thread
from tqdm import tqdm

@jit(nopython=True)
def getUnderAudio(a, minAudioLevel):
    x = 0
    returnList = []
    for index, lst in enumerate(a):
        if abs(lst[0]) < minAudioLevel:
            returnList.append(index + 1)
        x += 1
    return returnList

class ProgressBar(ttk.Progressbar):
    def __init__(self, root, mode, time=None, increment=10, **kwargs):
        self.increment = increment
        super(ProgressBar, self).__init__(root, **kwargs)
        if mode == "timed":
            if time is None:
                raise ValueError("Time needs to be set")
            else:
                pBarThr = Thread(target=self.time, args=(time,))
                pBarThr.start()

    def time(self, time):
        while True:
            self['value'] += self.increment

class ToolTip(object):

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
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self, _pass):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


class Loading_Bar:
    def __init__(self):
        pass

    def startLoad(self, text, dotShown=True, alpha=0.7,
                  updateDelay=500):  # Show the loading screen (should usually be thread)
        """
        Shows the loading bar on screen. Uses tkinter to show a black transparent screen.\n
        :param text: The text to be displayed
        :param alpha: The transparency of the window
        :param dotShown: If dots should be shown after the text - i.e. Loading. -> Loading.. -> Loading...
        :param updateDelay: Delay when calling update() function. This also includes the '.' loading.
        :return:
        """
        self.dots = 0
        self.load = True
        self.text = text
        self.iter = 0
        self.dotShown = dotShown
        self.updateDelay = updateDelay

        self.loading = Tk()
        self.loading.attributes("-alpha", alpha)
        self.loading.attributes("-fullscreen", True)
        self.loading.configure(bg="black")
        self.loading.overrideredirect(True)

        self.loading_text = Label(self.loading, text=self.text, bg="black", fg="green", font=("Courier", 44))
        self.loading_text.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.loading.after(self.updateDelay, self.update)
        self.loading.mainloop()

    def stopLoad(self):  # Stop showing the loading screen (this is usually called when its finished)
        """
        Stops the loading screen from showing.
        :return:
        """
        self.load = False

    def update(self):  # Update the onscreen text with '.', '..', '...' or '' after the text to show loading
        """
        Update function to update the text and check if window needs to close.
        :return:
        """
        if self.dotShown:
            self.loading_text.config(text=(self.text + ("." * self.dots)))
            if self.dots < 3:
                self.dots += 1
            else:
                self.dots = 0
        if self.load:
            self.loading.after(self.updateDelay, self.update)
        else:
            self.loading.destroy()


class Editor:

    def sub_clip(self, clip, startTime, endTime):
        return clip.subclip(startTime, endTime)

    def cut_out_no_audio(self, videoObj, audioGap=1, minAudioLevel=0.005,
                         speechGap=0.01):  # This works and I am NOT EDITING IT
        """
        Cuts out parts of the video that have no audio.\n
        :param videoObj: The video that needs to be cut
        :param audioGap: The minimum gap in audio for cut
        :param minAudioLevel: The level at which the audio has to be below to be cut
        :param speechGap: The size of the small pause between cuts so it doesn't cut instantly
        :return: VideoClip with necessary cuts
        """
        vid = videoObj
        vid = vid.set_duration(vid.duration)
        b = vid.audio
        a = b.to_soundarray()
        frames_to_remove = getUnderAudio(a, minAudioLevel)
        frames_to_remove_2d = []
        c_frames = []
        x = 0
        for item in frames_to_remove:
            if x != 0:
                if (c_frames[-1]) + 1 == item:
                    c_frames.append(item)
                    x += 1
                else:
                    frames_to_remove_2d.append(c_frames)
                    c_frames = []
                    x = 0
            else:
                c_frames.append(item)
                x += 1
        frames_to_remove_2d.append(c_frames)
        frame_ranges = []

        try:
            fps = vid.audio.fps
        except:
            fps = 11400
        x = 0
        for lst in frames_to_remove_2d:
            try:
                frame_ranges.append([lst[0] / fps, lst[-1] / fps])
                x += 1
            except Exception as e:
                pass

        indx = 0
        for x in range(0, len(frame_ranges)):
            if (frame_ranges[indx][1] - frame_ranges[indx][0]) < audioGap:
                frame_ranges.pop(indx)
            else:
                indx += 1

        vidAud = vid.audio
        vid = vid.without_audio()

        for lst in frame_ranges:
            vid = vid.cutout(lst[0], lst[1])
            vidAud = vidAud.cutout(lst[0], lst[1])
        vid = vid.set_audio(vidAud)
        if vid.audio.duration != vid.duration:
            print(f"BAD DURATION: {str(vid.duration)}, {str(vid.audio.duration)}")
        print("FINISHED CLIP")
        return vid

    def cut_out_start(self, videoObj, minAudioLevel=0.005, speechGap=0.01):
        """
        Cuts out parts of the video that have no audio.\n
        :param videoObj: The video that needs to be cut
        :param minAudioLevel: The level at which the audio has to be below to be cut
        :param speechGap: The size of the small pause between cuts so it doesn't cut instantly
        :return: VideoClip with necessary cuts
        """
        # try:
        frames_to_remove = []
        vid = videoObj
        vid = vid.set_duration(vid.duration)
        b = vid.audio
        a = b.to_soundarray()
        print(a.shape)

        for index, lst in enumerate(a):
            if abs(lst[0]) < minAudioLevel:
                frames_to_remove.append(index + 1)
            else:
                break

        frames_to_remove = [frames_to_remove[0] / vid.audio.fps, frames_to_remove[-1] / vid.audio.fps]
        print(frames_to_remove)
        vid = vid.cutout(frames_to_remove[0], frames_to_remove[1])
        return vid

        # except Exception as e:
        #     print(e)

    def addText(self, x, y, text, videoObj, fontsize, color):
        clip = videoObj
        text = TextClip(text, fontsize=fontsize, color=color)
        txt_clip = text.set_position((x, y))
        txt_clip.set_duration(videoObj.duration)
        video = CompositeVideoClip([clip, txt_clip]).set_duration(videoObj.duration)
        return video

    def getTextPreview(self, x, y, text, videoObj, fontsize, color):
        clip = videoObj.subclip(0, 0.001)
        text = TextClip(text, fontsize=fontsize, color=color)
        txt_clip = text.set_position((x, y))
        txt_clip.set_duration(videoObj.duration)
        video = CompositeVideoClip([clip, txt_clip]).set_duration(videoObj.duration)
        return video