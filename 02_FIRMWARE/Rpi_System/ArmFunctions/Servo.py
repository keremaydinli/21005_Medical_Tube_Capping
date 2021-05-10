def run(mb=None, servo=None, angle=None):
    if mb is None or servo is None or angle is None:
        return None
    mb.send_now('M280 P' + str(servo) + ' S' + str(angle))
