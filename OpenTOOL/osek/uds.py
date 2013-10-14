"""/* Copyright(C) 2013, OpenOSEK by Fan Wang(parai). All rights reserved.
 *
 * This file is part of OpenOSEK.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 *
 * Email: parai@foxmail.com
 * Sourrce Open At: https://github.com/parai/OpenOSEK/
 */
"""
import socket
import UserString
import time

uds_tx_id = 0x731
uds_rx_id = 0x732
def UdsOnCanUsage():
    print "Usage:"
    print "\t python uds.py --port port"
    print "Example: python uds.py --port 8999"

def CanTransmit(port,canid,data,length):
    if(port < 9000):
        p = 8000
    else:
        p = 9000
    msg = UserString.MutableString("c" * 17)
    msg[0] = '%c'%((canid>>24)&0xFF)
    msg[1] = '%c'%((canid>>16)&0xFF)
    msg[2] = '%c'%((canid>>8)&0xFF)
    msg[3] = '%c'%(canid&0xFF)
    msg[4] = '%c'%(length) #DLC
    for i in range(0,length):
        msg[5+i] = '%c'%((data[i])&0xFF)
    for i in range(length,8):
        msg[5+i] = '%c'%(0x55)
    msg[13] = '%c'%((port>>24)&0xFF)
    msg[14] = '%c'%((port>>16)&0xFF)
    msg[15] = '%c'%((port>>8)&0xFF)
    msg[16] = '%c'%((port)&0xFF)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', p))  
        sock.send(msg.data)
        sock.close()
    except:
        print 'ERROR: CanBusServer isn\'t started.'
def CanTpSendSF(port,canid,data,length):
    data = [0x00+length] + data
    CanTransmit(port,canid,data,length+1)
    msg = CanTpRxIndication(port)
    if msg == None:
        return
    length = ord(msg[5])
    response = []
    for i in range(0,length):
        response.append(msg[6+i])
    UdsClientTrace(response)
def CanTpTransmit(port,canid,data,length):
    if(length <= 7): # Send SF
        CanTpSendSF(port,canid,data,length)

def UdsClientTrace(msg):
    cstr = '\tResponse: \n\t['
    for i in range(0,len(msg)):
        cstr += '0x%-2x, '%(ord(msg[i]))
        if(i != 0 and i%8 == 0):
            cstr += '\n\t'
    cstr += ']'
    print cstr

def CanTpRxIndication(port = 8999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.bind(('127.0.0.1', port))  
    sock.listen(32) 
    startT = time.time()
    msg = None
    while True:  
        if((time.time()-startT)*1000 > 1000): # Timeout
            break 
        try:  
            sock.settimeout(1)
            connection,address = sock.accept() 
            connection.settimeout(1)
            msg = connection.recv(1024)  
            connection.close()
            if(len(msg) == 17):
                canid =  (ord(msg[0])<<24)+(ord(msg[1])<<16)+(ord(msg[2])<<8)+(ord(msg[3]))
                if(canid == uds_rx_id):
                    break
        except socket.timeout:  
            continue  
        connection.close()
    sock.close()
    return msg

def UdsConfig():
    global uds_tx_id, uds_rx_id
    print 'Welcome to OpenOSEK UDS client cnter!'
    value = raw_input('Please Input the UDS client Tx CAN ID(default = 0x731):')
    if('' != value):
        uds_tx_id = int(value,16)
    value = raw_input('Please Input the UDS client Rx CAN ID(default = 0x732):')
    if('' != value):
        uds_rx_id = int(value,16)
    print 'Tx = %s, Rx = %s.'%(hex(uds_tx_id),hex(uds_rx_id))
    
def UdsOnCanClient(port = 8999):
    global uds_tx_id, uds_rx_id
    #UdsConfig()
    while True:
        data = []
        value = raw_input("uds send [ 3E 00 ]:")
        if(value != ''):
            for chr in value.split(' '):
                try:
                    data.append(int(chr,16))
                except:
                    print 'Error input!'
                    data = [0x3e,00]
                    break
        else:
            data = [0x3e,00]
        CanTpTransmit(port,uds_tx_id,data,len(data))
   
def main(argc,argv):
    if(argc != 3):
        UdsOnCanUsage()
        return
    if(argv[1] == '--port'):
        UdsOnCanClient(int(argv[2]))
        
if __name__ == '__main__': 
    import sys 
    main(len(sys.argv),sys.argv);