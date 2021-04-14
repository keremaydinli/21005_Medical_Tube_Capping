from cryptography.fernet import Fernet
import pyAesCrypt


class Encryptor:
    def __init__(self):
        self.key = 'BarIUMel-NLSS'
        self.bufferSize = 64 * 1024

    def generate_key(self):
        """
        Generates a key and save it into a file
        """
        self.key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(self.key)

    def load_key(self, key):
        """
        Load the previously generated key
        """
        self.key = key

    def encrypt_message(self, message):
        """
        Encrypts a message
        """
        encoded_message = message.encode()
        f = Fernet(bytes(self.key))
        encrypted_message = f.encrypt(encoded_message)
        return encrypted_message

    def decrypt_message(self, encrypted_message):
        """
        Decrypts an encrypted message
        """
        f = Fernet(bytes(self.key))
        decrypted_message = f.decrypt(encrypted_message)
        return decrypted_message

    def encrypt_file(self, file, crypted_file):
        """
        Encrypts a file
        """
        pyAesCrypt.encryptFile(file, crypted_file, self.key, self.bufferSize)

    def decrypt_file(self, file, crypted_file):
        """
        Decrypts an encrypted file
        """
        pyAesCrypt.decryptFile(file, crypted_file, self.key, self.bufferSize)