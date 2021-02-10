import collections
import json


def braces_match(json_str):
    return json_str.count(b"{") == json_str.count(b"}")


class SocketWrapper:
    def __init__(self, socket):
        self.socket = socket
        self.received_data = collections.deque()
        self.unparsed_data = b""

    def recv(self, buffer_size):
        while not self.received_data:
            new_data = self.socket.recv(buffer_size)
            self.unparsed_data = self.unparsed_data + new_data
            start_idx = 0
            newbreak = self.unparsed_data.find(b"}{", start_idx)
            while newbreak != -1:
                end_idx = newbreak + 1
                data_chunk = self.unparsed_data[start_idx:end_idx]
                self.received_data.append(data_chunk)

                start_idx = end_idx
                newbreak = self.unparsed_data.find(b"}{", start_idx)

            final_chunk = self.unparsed_data[start_idx:]
            if braces_match(final_chunk):
                self.unparsed_data = b""
                self.received_data.append(final_chunk)
            else:
                self.unparsed_data = final_chunk

        retbytes = self.received_data.popleft()
        retdata = json.loads(retbytes.decode("utf-8"))
        return retdata

    def __getattr__(self, val):
        return getattr(self.socket, val)
