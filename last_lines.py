import io
import os

def last_lines(filename):
    read_size = io.DEFAULT_BUFFER_SIZE
    file_iterator = []
    with open(filename, 'r') as file:
        file_size = os.fstat(file.fileno()).st_size 
        seek_position = max(file_size - read_size, 0)

        while seek_position >= 0:
            file.seek(seek_position)
            file_iterator.append(repr(file.read(read_size)))
            seek_position -= read_size
    return iter(file_iterator)


lines = last_lines('text_file.txt') 
