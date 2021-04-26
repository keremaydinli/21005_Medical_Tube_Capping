def get_file_lines(file):
    f = open(file, "r")
    return f.readlines()


def s_protocol(received):
    if 'start' in received:
        # start:21-13
        command = received.split(':')[1]
        int_olcut = command.split('-')[0]

        # float_miktar = value + decimal value
        float_olcut = float(str(int_olcut)[0:-1]) + float(int(int_olcut[-1]) / 10)

        int_miktar = int(command.split('-')[1])
        print('DEBUG: miktar:{} - olcut:{}'.format(float_olcut, int_miktar))

        generated_g_codes = []
        one_shoot_g_codes = get_file_lines('one_shoot_g_codes.txt')

        for index in range(0, int_miktar):
            for line in one_shoot_g_codes:
                generated_g_codes.append(line.strip())

        f = open('temp_send_g_code_file.txt', "w")
        for line in generated_g_codes:
            f.write(line + '\n')
        f.close()

        return generated_g_codes
