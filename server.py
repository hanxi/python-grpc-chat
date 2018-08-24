from concurrent import futures

import grpc
import time

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc

gConn = {}

class ChatServer(rpc.ChatServerServicer):

    def __init__(self):
        # List with all the chat history
        self.chats = []

    # The stream which will be used to send new messages to clients
    def ChatStream(self, request_iterator, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n
            time.sleep(0.02)

    def SendNote(self, request: chat.Note, context):
        """
        This method is called when a clients sends a Note to the server.

        :param request:
        :param context:
        :return:
        """
        print("[{}] {}".format(request.name, request.message))
        # Add it to the chat history
        self.chats.append(request)
        gConn[request.name] = context
        return chat.Empty()


if __name__ == '__main__':
    port = 11912
    # create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ChatServer()
    rpc.add_ChatServerServicer_to_server(servicer, server)

    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    # Server starts in background (another thread) so keep waiting
    while True:
        for name,context in gConn.items():
            note = chat.Note()
            note.name = "system"
            note.message = "Hello every body."
            servicer.chats.append(note)
            servicer.ChatStream(None, context)
        time.sleep(10)

