from colosseum.utils.compress import compress, decompress
import numpy as np

input_array = np.random.uniform(low=-9, high=9, size=(4, 4))
print(input_array)
compressed_array = compress(input_array)
print(compressed_array)
decompressed_array = decompress(compressed_array)
print(decompressed_array)
assert np.array_equal(input_array, decompressed_array)
print("Test Passed")
