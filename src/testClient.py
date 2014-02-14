import socket
import sys
ANY = '0.0.0.0'
SENDERPORT=1501
MCAST_ADDR = '224.168.2.9'
MCAST_PORT = 1602
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#The sender is bound on (0.0.0.0:1501)
sock.bind((ANY,SENDERPORT))
#Tell the kernel that we want to multicast and that the data is sent
#to everyone (255 is the level of multicasting)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
while 1:
	#time.sleep(10)
	#send the data 'hello, world' to the multicast addr: port
	#Any subscribers to the multicast address will receive this data
	message = raw_input("What message do you want to send?\n")
	sock.sendto(message, (MCAST_ADDR,MCAST_PORT) )
	if(message=='quit'):
		print '\033[1;31mShutting down client\033[1;m'
		sock.close()
		sys.exit(0)