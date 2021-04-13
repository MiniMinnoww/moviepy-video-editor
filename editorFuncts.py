from moviepy.editor import *
from tkinter import *

from numba import jit
import moviepy.editor as mpy


@jit(nopython=True)
def getUnderAudio(a, minAudioLevel):
    x = 0
    returnList = []
    for index, lst in enumerate(a):
        if abs(lst[0]) < minAudioLevel:
            returnList.append(index + 1)
        x += 1
    return returnList


class Editor:

    def sub_clip(self, clip, startTime, endTime):
        return clip.subclip(startTime, endTime)

    def cut_out_no_audio(self, videoObj, audioGap=1, minAudioLevel=0.005,
                         safeMode=False):
        """
        Cuts out parts of the video that have no audio.\n
        :param videoObj: The video that needs to be cut
        :param audioGap: The minimum gap in audio for cut
        :param minAudioLevel: The level at which the audio has to be below to be cut
        :param safeMode: Whether to check audio is working after each iteration
        :return: VideoClip with necessary cuts
        """

        vid = videoObj
        vid = vid.set_duration(vid.duration)
        print(f"This clip is {str(vid.fps * vid.duration)} frames long")
        b = vid.audio
        frames_to_remove_2d = []
        c_frames = []
        frame_ranges = []
        x = 0
        indx = 0

        a = b.to_soundarray()

        frames_to_remove = getUnderAudio(a, minAudioLevel)

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
        if len(c_frames) > 0:
            frames_to_remove_2d.append(c_frames)

        try:
            fps = vid.audio.fps
        except:
            fps = 11400

        x = 0

        for lst in frames_to_remove_2d:
            try:
                frame_ranges.append([lst[0] / fps, lst[-1] / fps])
            except:
                frame_ranges.append([lst[0] / fps])
            x += 1

        for x in range(0, len(frame_ranges)):
            if (frame_ranges[indx][1] - frame_ranges[indx][0]) < audioGap:
                frame_ranges.pop(indx)
            else:
                indx += 1
        vidAud = vid.audio
        vid = vid.without_audio()
        if safeMode:
            for lst in reversed(frame_ranges):
                testaud = vidAud.cutout(lst[0], lst[1])

                try:
                    testaud.to_soundarray()
                    vid = vid.cutout(lst[0], lst[1])
                    vidAud = vidAud.cutout(lst[0], lst[1])
                except:
                    pass
        else:
            for lst in reversed(frame_ranges):
                vid = vid.cutout(lst[0], lst[1])
                vidAud = vidAud.cutout(lst[0], lst[1])
        vid = vid.set_audio(vidAud)

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

    def addMargin(self, vid, _type, size, color):
        if _type == "border":
            clip_with_margin = vid.margin(size, color=color)
        else:
            clip_with_margin = vid.margin(top=size, bottom=size, color=color)
        return clip_with_margin

    def getMarginPreview(self, vid, _type, size):
        clip = vid.subclip(0, 0.001)
        if _type == "border":
            clip_with_margin = clip.margin(size)
        else:
            clip_with_margin = clip.margin(top=size, bottom=size)
        return clip_with_margin
