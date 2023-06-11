def xor_encrypt_decrypt(message, key):
    if key == "":
        return message
    
    encrypted = bytearray()
    for i in range(len(message)):
        encrypted.append(message[i] ^ key[i % len(key)])
    return encrypted

# Пример использования
plaintext = b'Hello, XOR encryption!'
encryption_key = b'secret_key'

# Шифрование
encrypted_message = xor_encrypt_decrypt(plaintext, encryption_key)
print('Зашифрованное сообщение:', encrypted_message)

# Дешифрование
decrypted_message = xor_encrypt_decrypt(encrypted_message, encryption_key)
print('Расшифрованное сообщение:', decrypted_message.decode('utf-8'))
