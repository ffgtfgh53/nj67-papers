# def task1_1(c:str, n:int):
#     if c == ' ': return '!'
#     if not c.isalpha(): return -1
#     res = ((ord(c) & 0b11111 )+ n) % 26 or 26
#     return chr(res + 64) if c.isupper() else chr(res + 96)

# task1_1('z', 26)

# import string

# def task1_1(c,n):
#     if c == " ":
#         return "!"
#     if not c.isalpha():
#         return -1
#     if upc := c in string.ascii_uppercase:
#         posn = ord(c) - 65
#     else:
#         posn = ord(c) - 97
#     encrypted_ascii = posn+n
#     while encrypted_ascii > 25:
#         encrypted_ascii = encrypted_ascii -26
#     if upc:
#         return string.ascii_uppercase[encrypted_ascii]
#     else:
#         return string.ascii_lowercase[encrypted_ascii]

def task1_1(c,n): 
    if c == " ": 
        return "!" 
    elif c.isalpha(): 
        limit = 90 
        if c.islower(): 
            limit = 122 
        ASCII_Value = ord(c) 
        new_ASCII_Value = ASCII_Value + n 
        if new_ASCII_Value > limit: 
            new_ASCII_Value -= 26

        return chr(new_ASCII_Value)
    else: 
        return -1

def task1_2():
    with open("./Resources/TASK1/TASK1DATA.txt") as file:
        message =file.read()

    key = "Njc"
    times = len(message)/len(key)
    key_pattern = key.upper() * (int(times) + (times%1>0))
    encrypted_message = ""
    for idx in range(len(message)):
        c = message[idx]
        n = int(ord(key_pattern[idx]) - 64)
        if (encrypt := task1_1(c,n)) == -1:
            encrypt = message[idx]
        encrypted_message += encrypt
    with open("./Resources/TASK1/ENCRYPTEDMESSAGE.txt","w") as file:
        file.write(encrypted_message)