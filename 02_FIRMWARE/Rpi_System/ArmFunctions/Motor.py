def run(mb=None, extruder=None, distance=540, feedrate=6000):
    if mb is None or extruder is None:
        return None
    mb.send_now('T' + extruder)
    mb.send_now('G91')
    mb.send_now('G1 E' + str(distance) + ' F' + str(feedrate))
    mb.send_now('G90')
