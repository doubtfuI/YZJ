import hashlib


def check(user_name, psw):
    user_name = str(user_name)
    psw = str(psw)
    string = (user_name + psw)
    bytes_str = string.encode('utf-8')
    md5 = hashlib.md5(bytes_str).hexdigest()
    return md5

