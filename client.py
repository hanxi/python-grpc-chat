import threading
import os 
import time

import grpc

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc

address = 'localhost'
port = 11912


class Client:

    def __init__(self, u: str):
        # the frame to put ui components on
        self.username = u
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)
        # create new listening thread for when new message streams come in
        threading.Thread(target=self.__ListenForMessages, daemon=True).start()

    def __ListenForMessages(self):
        """
        This method will be ran in a separate thread as the main/ui thread, because the for-in call is blocking
        when waiting for new messages
        """
        for note in self.conn.ChatStream(chat.Empty()):
            print("R[{}] {}".format(note.name, note.message))

    def SendMessage(self, message):
        if message is not '':
            n = chat.Note()
            n.name = self.username
            n.message = message
            print("S[{}] {}".format(n.name, n.message))
            self.conn.SendNote(n)

if __name__ == '__main__':
    username = None
    while username is None:
        username = input("Enter your name: ") 
    c = Client(username)
    while True:
        line = input("> ")
        if line == "exit":
            os.exit()
        c.SendMessage(line)
        time.sleep(0.02)

