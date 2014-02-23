# telnet program example
import socket, select, string, sys

host = 'localhost'
port = 5001
 
# main function
if __name__ == "__main__":
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()
     
    print 'Connected to remote host. Start sending messages'
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:
            # incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print '\nDisconnected from server'
                    sys.exit()
                else :
                    # print data
                    try:
                        dict = eval(data)
                        print str(dict)
                    except:
                        print "ERROR: " + data
             
            # user entered a message
            else :
                msg = raw_input("What message do you want to send?\n")
                s.send(msg)
                if(msg=="quit"):
                    print '\033[1;31mShutting down client\033[1;m'
                    sock.close()
                    sys.exit(0)