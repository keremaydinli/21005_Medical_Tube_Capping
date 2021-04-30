def get_file_lines(file):
    f = open(file, "r")
    return f.readlines()


def s_protocol(received):
    # TODO: bazi caseler tamamlanmadı gcodelar kontrol edilecek

    generated_g_codes = []
    feedrate = ' F8000'

    received = str(received).lower()

    if 'start' in received:
        # start:21-13
        command = received.split(':')[1]
        int_olcut = command.split('-')[0]

        # float_miktar = value + decimal value
        float_olcut = float(str(int_olcut)[0:-1]) + float(int(int_olcut[-1]) / 10)

        int_miktar = int(command.split('-')[1])
        print('DEBUG: olcut:{} - miktar:{}'.format(float_olcut, int_miktar))

        one_shoot_g_codes = get_file_lines('one_shoot_g_codes.txt')

        for index in range(0, int_miktar):
            for line in one_shoot_g_codes:
                line = line.strip()
                line = special_cases(line, float_olcut)
                generated_g_codes.append(line)

        f = open('temp_send_g_code_file.txt', "w")
        for line in generated_g_codes:
            f.write(line + '\n')
        f.close()

    elif 'ileri' in received:
        # ileri:10
        dist = float(received.split(':')[1])
        generated_g_codes.append('G91')
        generated_g_codes.append('G0 X' + str(dist) + feedrate)
        generated_g_codes.append('G90')
    elif 'sag' in received:
        # sag:1
        dist = float(received.split(':')[1])
        generated_g_codes.append('G91')
        generated_g_codes.append('G0 Y' + str(dist) + feedrate)
        generated_g_codes.append('G90')
    elif 'sol' in received:
        # sol:0.1
        dist = float(received.split(':')[1])
        generated_g_codes.append('G91')
        generated_g_codes.append('G0 Y-' + str(dist) + feedrate)
        generated_g_codes.append('G90')
    elif 'geri' in received:
        # geri:10
        dist = float(received.split(':')[1])
        generated_g_codes.append('G91')
        generated_g_codes.append('G0 X-' + str(dist) + feedrate)
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


def special_cases(line, olcut):
    # line: G1 E135 F8000;pump
    # 2 ml icin peristaltik pompanın ne kadar donmesi gerektigi sayıyı bulacagız
    # elde ettigimiz sayi hep asagıdaki sayıya esit olmak zorunda
    # mesela 2 mL icin donduruyorsak asagıdaki sayı 2 olmalı, 0.5 mL icin donduruyorsak asagıdaki sayı 0.5 olmalı
    standard_olcut_quantity = 2.0
    extrude_pump_quantity = 135.0
    if 'pump' in line.lower():
        raw_line = line.split(';')[0].strip()  # line: G1 E135 F8000
        raw_line_params = raw_line.split(' ')
        for raw_line_param in raw_line_params:
            if 'e' in raw_line_param.lower():  # line: E135
                extrude_pump_quantity = float(raw_line_param[1:])  # extrude_pump_quantity: 135
                break
        print('DEBUG: extrude_pump_for_2_mL: {}'.format(extrude_pump_quantity))

        # compare to what do user want extrude quantity and standart extrude quantity
        coefficient = olcut / standard_olcut_quantity
        print('DEBUG: coefficient: {}'.format(coefficient))
        new_extrude_pump_quantity = extrude_pump_quantity * coefficient
        print('DEBUG: new extrude pump quantity: {}'.format(new_extrude_pump_quantity))
        new_line = ''
        for raw_line_param in raw_line_params:
            if 'e' in raw_line_param.lower():
                new_line += 'E' + str(new_extrude_pump_quantity)
            else:
                new_line += raw_line_param
            new_line += ' '
        return new_line
    else:
        return line
