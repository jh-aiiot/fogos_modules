# -*- coding: utf-8 -*-
import os
from os.path import expanduser

def get_pubkey():
    home_dir = expanduser('~')
    ssh_pubkey_path = '{}/.ssh/id_rsa.pub'.format(home_dir)

    #my_env = os.environ.copy()
    #username = subprocess.check_output(['echo', my_env['USER']])
    #ssh_pubkey_path = '/home/{}/.ssh/id_rsa.pub'.format(username.decode('utf-8').strip())

    print(ssh_pubkey_path)
    pubkey = 'null'
    if os.path.exists(ssh_pubkey_path):
        with open(ssh_pubkey_path, 'r') as f:
            pubkey = f.readline().strip()
    else:
        print('no such file!!')
        pubkey = 'null'

    return pubkey

#
# Debug: test code
#
if __name__ == '__main__':
    res = get_pubkey().strip()
    print(res)
