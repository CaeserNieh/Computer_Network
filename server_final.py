import socket,select
import threading
import time
import sys

HOST=""
PORT = 5000
RECV_BUFFER = 4096
TIME = 5


class chatroom(threading.Thread):
    
    def __init__(self,con,addr):
        threading.Thread.__init__(self)
        self.conn = con
        self.addr = addr
        self.ip = self.addr[0]
        self.name=""

    def send_to_connection(self,prompt):
        self.conn.send(("%s\n"%prompt))


    def login(self):
        global clients
        global messages
        global accounts
        global onlines


        clients.add((self.conn,self.addr))
        msg = "Welcome to Simple Chat Room \nEnter '!q' to quit\n"

        print(accounts)
        if self.ip not in accounts:
            msg += 'Please enter your name:'
            self.send_to_connection(msg)
            accounts[self.ip] = {
                'name': '',
                'pass': '',
                'lastlogin': time.ctime()
            }    
            while 1:
                name = self.conn.recv(RECV_BUFFER).strip()
                if name in messages :
                    self.send_to_connection("This nams is already exist,try again")
                else:
                    break
            accounts[self.ip]['name'] = name
            self.name = name
            messages[name] = []
            self.send_to_connection('please enter your password:')
            password = self.conn.recv(RECV_BUFFER)
            accounts[self.ip]['pass'] = password.strip()
            self.send_to_connection('enjoy your chat')

        else:
            self.name = accounts[self.ip]["name"]
            msg+="please enter you password"
            self.send_to_connection(msg)

            while 1:
                password = self.conn.recv(RECV_BUFFER).strip()
                if password != accounts[self.ip]["pass"]:
                    self.send_to_connection("incorrect password")
                else:
                    self.send_to_connection("welcome back last time %s"%(accounts[self.ip]["lastlogin"]))
                    accounts[self.ip]["lastlogin"] = time.ctime()
                    break

            self.conn.send(self.show_message_to(self.name))

        self.conn.send("<Input> :")
        self.broadcast("%s is online now"%(self.name),clients,False)
        print("%s is on line"%(self.name))
        print("login done!!")
        onlines[self.name] = self.conn

        
        
    def logoff(self):
        global clients
        global onlines
        self.conn.send("Bye Bye\n")
        del onlines[self.name]
        clients.remove((self.conn,self.addr))
        if onlines :
            self.broadcast("%s is offline now" % (self.name),clients,True)

        self.conn.close()
        sys.exit()
        
        
    def check_keyword(self,buf):
        global onlines
        global clients
        if buf.find("!q") == 0:
            clients.remove((self.conn,self.addr))
            self.conn.close()
            sys.exit()
        if buf.find("@") == 0:
            to_user = buf.split(" ")[0][1:]
            from_user = self.name
            msg = buf.split(" ",1)[1]   
            if to_user in onlines:
                onlines[to_user].send("@ %s : %s\n"%(from_user.msg))
                self.message_to(from_user,to_user,msg,1)
            else:
                self.message_to(from_user,to_user,msg)     
        return False
        
    def message_to(self,from_user,to_user,msg,read=0):
        global messages
        if to_user in messages:
            messages[to_user].append([from_user, msg, read])
            self.send_to_connection('Message has sent to %s' % (to_user))
        else:
            self.send_to_connection('No such user named %s' % (to_user))
        
    def show_message_to(self,name):
        global messages
        res="here are your message :\n"
        if not messages[name]:
            res = res + "NO message available\n"
            return res    
        for msg in messages[name]:
            if msg[2] == 0:
                res = res + "(NEW) %s : %s \n "%(msg[0],msg[1])
                msg[2] = 1
            else:
                res = res + "%s : %s\n"%(msg[0],msg[1])

        return res
        
    def broadcast(self,msg,receivers,to_self=True):
        for conn,addr in receivers:
            if addr[0] != self.ip:
                conn.send(msg+"\n")
            else :
                if to_self :
                    self.conn.send("Broadcast : "+msg+"\n")
                else :
                    self.conn.send('')
         
    def run(self):
        global messages
        global accounts
        global clients
        self.login()
        while 1:
            try:
                buf = self.conn.recv(RECV_BUFFER).strip()
                print("%s : %s\n"%(self.name,buf))
                if not self.check_keyword(buf):
                    self.broadcast("%s :%s"%(self.name,buf),clients,False)
            except Exception as e :
                print(e)
                pass


def main():
    global clients
    global messages
    global accounts
    global onlines
    clients = set()
    messages = {}
    accounts = {}
    onlines = {}
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(10)

    print("Chat Room Server start on PORT "+str(PORT))
    print("Welcome!!")
    while 1:
        try:
            connection,addr = sock.accept()
            print("client (%s,%s)connected"%addr)
            server = chatroom(connection,addr)
            server.start()
        except Exception as e:
            print(e)



################  main ##################
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Quit")