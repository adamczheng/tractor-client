import socket


class Network:

    def __init__(self,test=False):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.host = "136.152.143.112" # For this to work on your machine this must be equal to the ipv4 address of the
        # machine running the server You can find this address by typing ipconfig in CMD and copying the ipv4
        # address. Again this must be the servers ipv4 address. This field will be the same for all your clients.
        port_in = 0
        if not test:
            port_in = input("Port number? ")
            try:
                port_in = int(port_in)
            except:
                port_in = 0
        if port_in == 0:
            self.host = socket.gethostbyname('localhost')
            self.port = 5555
        else:
            self.port = port_in
            self.host = socket.gethostbyname('0.tcp.ngrok.io')
        self.addr = (self.host, self.port)
        print(self.addr)
        self.id = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        print('connected')
        return self.client.recv(2048).decode()

    def send(self, data):
        """
        :param data: str
        :return: str
        """
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)

    def getID(self):
        return self.id
