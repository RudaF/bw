import io
import os

def last_lines(filename, read_size=io.DEFAULT_BUFFER_SIZE):
    file_iterator = []
    with open(filename, 'r') as file:
        file_size = os.fstat(file.fileno()).st_size 
        seek_position = file_size
        while seek_position >= 0:
            file.seek(seek_position)
            try:
                current_line = repr(file.readline(read_size))
                file_iterator.append(current_line)
            except Exception:
                seek_position -= 1
            seek_position -= read_size
    return iter(file_iterator)

lines = last_lines('text_file.txt', 3)


