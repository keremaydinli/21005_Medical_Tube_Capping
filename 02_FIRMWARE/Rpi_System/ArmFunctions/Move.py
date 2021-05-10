def forward(mb=None, distance=None, feedrate=6000):
    if mb is None or distance is None:
        return
    move(mb, 'Y', distance, feedrate)


def backward(mb=None, distance=None, feedrate=6000):
    if mb is None or distance is None:
        return
    move(mb, 'Y-', distance, feedrate)


def right(mb=None, distance=None, feedrate=6000):
    if mb is None or distance is None:
        return
    move(mb, 'X', distance, feedrate)


def left(mb=None, distance=None, feedrate=6000):
    if mb is None or distance is None:
        return
    move(mb, 'X-', distance, feedrate)


def up(mb=None, distance=None, feedrate=6000):
    if mb is None or distance is None:
        return
    move(mb, 'Z', distance, feedrate)


def down(mb=None, distance=None, feedrate=6000):
    if mb is None or distance is None:
        return
    move(mb, 'Z-', distance, feedrate)


def home(mb=None, go_park_position=True, feedrate=6000):
    mb.send_now('G28')
    if go_park_position:
        mb.send_now('G0 X200 Y0 F' + str(feedrate))


def move(mb=None, axis=None, distance=None, feedrate=None):
    if axis is None or feedrate is None:
        return
    mb.send_now('G91')
    mb.send_now('G0 ' + axis + str(distance) + ' F' + str(feedrate))
    mb.send_now('G90')
