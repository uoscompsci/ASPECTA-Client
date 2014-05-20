# telnet program example
import socket, select, string, sys

host = 'localhost'
port = 5000
errors = {1 : "Invalid API call",
          2 : "Wrong number of arguments (% instead of %)",
          3 : "User name not yet set",
          4 : "User name already set",
          5 : "Application name already set",
          6 : "Application name not yet set",
          7 : "Must be owner to change admin setting"
          }
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
                    dict = eval(data)
                    try:
                        errno = dict["error"]
                        error = str(errors[errno])
                        spliterr = error.split("%")
                        errorStr = spliterr[0]
                        for x in range(1,len(spliterr)): #Constructs errors which have parameters
                            errorStr = errorStr + dict[str(x)] + spliterr[x]
                        print "\033[1;31mERROR: " + errorStr + "\033[1;m"
                    except:
                        print str(dict)
             
            # user entered a message
            else :
                msg = raw_input("What message do you want to send?\n")
                s.send(msg)
                if(msg=="quit"):
                    print '\033[1;31mShutting down client\033[1;m'
                    sock.close()
                    sys.exit(0)