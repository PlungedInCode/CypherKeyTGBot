# def xor_encrypt_decrypt(message, key):
#     if key:
#         encrypted = bytearray()
#         for i in range(len(message)):
#             encrypted.append(message[i] ^ key[i % len(key)])
#         return encrypted

#     return message.decode('utf-8')

def xor_encrypt_decrypt(message, key):
    if key:
        key = key * (len(message) // len(key)) + key[:len(message) % len(key)]
        encrypted = ''.join(chr(ord(m) ^ ord(k)) for m, k in zip(message, key))
        return encrypted
    return message