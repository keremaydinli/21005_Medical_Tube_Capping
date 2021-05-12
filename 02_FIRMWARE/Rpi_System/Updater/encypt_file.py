from Encryption import Encryptor

enc = Encryptor()
file_path = 'v1.0.1.zip'
enc_file_path = 'enc_' + file_path

if __name__ == "__main__":
    enc.encrypt_file(file_path, enc_file_path)
    print('FILE ENCRYPTION DONE.')