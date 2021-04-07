clipFrames = {}  # {[btn, vid, pos]}
oldClipFrames = []
redo_ = []


def undo():
    global oldClipFrames
    global redo_
    """
    A function to undo last move
    :return last: 
    """
    try:
        last = oldClipFrames[-1]
        oldClipFrames.pop(-1)
        redo_.append(last)
        return last
    except:
        return False


def redo():
    global oldClipFrames
    global redo_
    try:
        last = redo_[-1]
        redo_.pop(-1)
        oldClipFrames.append(last)
        return last
    except:
        return False


def saveOld():
    global oldClipFrames
    oldClipFrames.append(clipFrames)
    print(oldClipFrames)
