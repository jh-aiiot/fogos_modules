import random, hashlib

def get_hash(str):
    rand_num = random.randrange(0,4294967295)
    temp_str = '{}{}'.format(str, rand_num)
    m = hashlib.md5()
    m.update(temp_str.encode('utf-8'))
    return m.hexdigest()
