import gzip
import pickle
from base64 import b64decode, b64encode


def compress(original_data):
    pickled_data = pickle.dumps(original_data)
    gzipped_data = gzip.compress(pickled_data, compresslevel=1)
    b64_data = b64encode(gzipped_data)
    return b64_data.decode()


def decompress(compressed_data):
    b64_data = bytes(compressed_data, "utf-8")
    gzipped_data = b64decode(b64_data)
    pickled_data = gzip.decompress(gzipped_data)
    original_data = pickle.loads(pickled_data)
    return original_data
