def get_file_lines(file):
    f = open(file, "r")
    return f.readlines()


def s_protocol(received):
    generated_g_codes = []
    FEEDRATE = ' F8000'

    if 'start' in received:
        # start:21-13
        command = received.split(':')[1]
        int_olcut = command.split('-')[0]

        # float_miktar = value + decimal value
        float_olcut = float(str(int_olcut)[0:-1]) + float(int(int_olcut[-1]) / 10)

        int_miktar = int(command.split('-')[1])
        print('DEBUG: miktar:{} - olcut:{}'.format(float_olcut, int_miktar))

        one_shoot_g_codes = get_file_lines('one_shoot_g_codes.txt')

        for index in range(0, int_miktar):
            for line in one_shoot_g_codes:
                generated_g_codes.append(special_cases(line.strip()))

        f = open('temp_send_g_code_file.txt', "w")
        for line in generated_g_codes:
            f.write(line + '\n')
        f.close()

    elif 'ileri' in received:
        # ileri:10
        dist = float(received.split(':')[1])
        generated_g_codes.append('G91')
        generated_g_codes.append('G0 X' + dist + FEEDRATE)
        generated_g_codes.append('G90')
    elif 'sag' in received:
        # sag:1
        dist = float(received.split(':')[1])
        generated_g_codes.append('G91')
        generated_g_codes.append('G0 Y' + dist + FEEDRATE)
        generated_g_codes.append('G90')
    elif 'sol' in received:
        # sol:0.1
        dist = float(received.split(':')[1])
        generated_g_codes.append('G91')
        generated_g_codes.append('G0 Y-' + dist + FEEDRATE)
        generated_g_codes.append('G90')
    elif 'geri' in received:
        # geri:10
        dist = float(received.split(':')[1])
        generated_g_codes.append('G91')
        generated_g_codes.append('G0 X-' + dist + FEEDRATE)
        generated_g_codes.append('G90')
    elif 'home' in received:
        # home
        generated_g_codes.append('G28')
    elif 'kapagi' in received:
        if 'bosalt' in received:
            # kapagi-bosalt
            generated_g_codes.append('M280 P2 S')
            generated_g_codes.append('G4 P1000')
            generated_g_codes.append('M280 P2 S')
    elif 'tupu' in received:
        if 'tut' in received:
            # kapagi-tut
            generated_g_codes.append('M280 P2 S')
        elif 'birak' in received:
            # kapagi-birak
            generated_g_codes.append('M280 P2 S')

    return generated_g_codes


def special_cases(line):
    return line
