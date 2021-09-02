import paramiko
import os
from binascii import hexlify
import sys
from getpass import getpass
def key_trust(t,host):
    key = t.get_remote_server_key()
    trusted_hosts = paramiko.HostKeys(os.path.expanduser("~/.ssh/known_hosts"))
    if not trusted_hosts.check(host,key):
        print("The authenticity of host {}:{} can't be established.".format(t.getpeername()[0],t.getpeername()[1]))
        print("Key fingerprint is : {}".format(hexlify(key.get_fingerprint()).decode()))
        
        trust = input('Are you sure you want to continue connecting (yes/no): ')
        while not trust in ('yes','no'):
            trust = input("Please enter (yes/no): ")
        if trust == 'yes':
            trusted_hosts.add(host,key.get_name(),key)
            trusted_hosts.save(os.path.expanduser("~/.ssh/known_hosts"))
            return
        else:
            print("Host key verification failed.")
            sys.exit(1)
    return
def manual_auth(transport,username):
    print("Which key type do you want to use for authenticating.Default is password")
    key_type = 'p'
    uin = input("Connect using: [p] password, [r] rsa key, [d] dsa key, [e] ecdsa key: ")
    if len(uin):
        key_type=uin
    if key_type == 'r':
        default_path = os.path.expanduser('~/.ssh/id_rsa')
        key_path = input("What is the path to the key file[default '~/.ssh/id_rsa': ")
        if not len(key_path):
            key_path = default_path
        try:
            key = paramiko.RSAKey.from_private_key_file(key_path)
        except paramiko.PasswordRequiredException:
            passwd = getpass("Passphrase for the RSA private  Key file :  ")
            try:
                key = paramiko.RSAKey.from_private_key_file(key_path,passwd)
            except paramiko.SSHException:
                print("Passphrase does not match!!!")
                sys.exit(1)
        try:
            transport.auth_publickey(username,key)
        except paramiko.BadAuthenticationType:
            print("Sorry, but the server does not support authentication by public key")
            sys.exit(1)
        except paramiko.AuthenticationException:
            print("Invalid key")
            sys.exit(1)
        except paramiko.SSHException:
            print("Something went wrong")
            sys.exit(1)

    elif key_type == 'd':
        default_path = os.path.expanduser('~/.ssh/id_dsa')
        key_path = input("What is the path to the key file [default '~/.ssh/id_dsa']:  ")
        if not len(key_path):
            key_path = default_path
        try:
            key = paramiko.DSSKey.from_private_key_file(key_path)
        except paramiko.PasswordRequiredException:
            passwd = getpass("Passphrase for the DSA private Key file: ")
            try:
                key = paramiko.DSSKey.from_private_key_file(key_path,passwd)
            except paramiko.SSHException:
                print("Passphrase does not match!!!")
                sys.exit(1)
        try:
            transport.auth_publickey(username,key)
        except paramiko.BadAuthenticationType:
            print("Sorry, but the server does not support authentication by public key")
            sys.exit(1)
        except paramiko.AuthenticationException:
            print("Invalid key")
            sys.exit(1)
        except paramiko.SSHException:
            print("Something went wrong")
            sys.exit(1)
    
    elif key_type == 'e':
        default_path = os.path.expanduser('~/.ssh/id_ecdsa')
        key_path = input("What is the path to the key file[default '~/.ssh/id_ecdsa']: ")
        if not len(key_path):
            key_path = default_path
        try:
            key = paramiko.ECDSAKey.from_private_key_file(key_path)
        except paramiko.PasswordRequiredException:
            passwd = getpass("Password to the RSA Key file: ")
            try:
                key = paramiko.ECDSAKey.from_private_key_file(key_path,passwd)
            except paramiko.SSHException:
                print("Passphrase does not match!!!")
                sys.exit(1)
        try:
            transport.auth_publickey(username,key)
        except paramiko.BadAuthenticationType:
            print("Sorry, but the server does not support authentication by public key")
            sys.exit(1)
        except paramiko.AuthenticationException:
            print("Invalid key")
            sys.exit(1)
        except paramiko.SSHException:
            print("Something went wrong")
            sys.exit(1)
    
    elif key_type == 'p':
        try:
            passwd = getpass("Enter the password: ")
            transport.auth_password(username,passwd)
        except paramiko.BadAuthenticationType:
            print("Sorry, the server doesn't support password authentication")
            sys.exit(1)
        except paramiko.AuthenticationException:
            print("Wrong username/password combination")
            sys.exit(1)
        except paramiko.SSHException as e:
            print("Something went wrong, please try again later") 
            print('[DEBUGGING]: %s' % str(e)) 
            sys.exit(1)
    else:
        print("provide valid authentication option")
        sys.exit(1)
        
def auto_auth(t,u):
    agent = paramiko.Agent()
    keys = agent.get_keys()
    if len(keys) == 0:
        print("No keys loaded!!! : ")
        return
    for key in keys:
        try:
            print("[+] Trying the key %s" % key.get_fingerprint())
            t.auth_publickey(u,key)
            print("[+] Success")
            return True
        except paramiko.BadAuthenticationType:
            print("Sorry the server does not allow public key authentication")
        except paramiko.AuthenticationException:
            print("[-] Failed")
        except paramiko.SSHException as e:
            print("Agent auth Failed : %s" % str(e))
        except Exception as e:
            print('Caught exception {}'.format(str(e)))
    return False
