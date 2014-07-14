'''Dump all non-null data from a listening memcached server instance'''
import socket
import argparse
import time
import re
import sys

def recv_basic(the_socket,terminator):
    total_data=[]
    while True:
        data = the_socket.recv(8192)
        if not data:
            break
        total_data.append(data)
        if terminator in data:
            break
    return ''.join(total_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t","--target",help='Memcached server host:port')
    args = parser.parse_args()

    if(len(sys.argv) < 2):
        parser.print_help()
        sys.exit(0)

    [host,port] = args.target.split(':')
    port = int(port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s.send('stats items\n')
    statItems = recv_basic(s,'END')
    
    itemNumbers = re.findall('STAT items:(\d+):number (\d+)',statItems)

    for itemNumber in itemNumbers:
        cmd = 'stats cachedump '+itemNumber[0]+' '+itemNumber[1]+'\n'
        s.send(cmd)
        keys = recv_basic(s,'END')
        keyNames = re.findall('ITEM ([^\s]+) \[(\d+) b',keys)

        for keyName in keyNames:
            if(int(keyName[1]) != 0):
                print keyName[0]
                s.send('get ' + keyName[0]+'\n')
                content = recv_basic(s,'END')
                print content