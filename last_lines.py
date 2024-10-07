import io
import os
import mmap

def last_lines(filename: str, read_size: int = io.DEFAULT_BUFFER_SIZE):
    '''
    Read a file with filename in the same dir backwards based on read_size in bytes.

    Returns:
    Iterator with each line read with read_size
    '''
    # enquanto eu não encontro um \n eu vou diminuindo o seek position até encontrar e aí leio a linha da minha frente quando encontrar
    file_iterator = []
    with open(filename, 'rb', 0) as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as file_map:
        file_size = os.fstat(file.fileno()).st_size 
        file_line_breaks = _find_all_new_line_positions_in_bytestr(file_map)
        file_line_breaks.append(file_size)
        file_line_breaks.reverse()
        file_line_breaks.append(0)
        seek_position = file_size
        chunk_size = read_size
        i = 0
        while seek_position >= 0 and i < len(file_line_breaks):
            current_line_pos = file_line_breaks[i]
            if i >= len(file_line_breaks) - 1:
                break
            next_line = file_line_breaks[i + 1]
            
            seek_position = current_line_pos + 1
            while seek_position > next_line:
                seek_position, chunk_size = _get_what_to_read(seek_position, chunk_size, next_line)
                file.seek(seek_position)
                try:
                    current_line = file.read(chunk_size)                    
                    file_iterator.append(current_line.decode())
                except:
                    seek_position -= 1
                    continue
                chunk_size = read_size    
            i += 1

    return iter(file_iterator)


def _get_what_to_read(current_position, chunk_size, next_line):
    seek_position = current_position
    if seek_position - chunk_size < next_line:
        # the next chunk will surpass current line, so we read only until the next line
        chunk_size = seek_position - next_line
        seek_position = next_line
    else:
        # we are still reading the somewhere inside the line still
        seek_position -= chunk_size

    return seek_position, chunk_size


def _find_all_new_line_positions_in_bytestr(bytestr):
    new_line_positions = []
    current_index = 0
    while 0 <= current_index < len(bytestr) - 1:
        new_index = bytestr.find(b'\n', current_index + 1)
        if new_index > 0:
            new_line_positions.append(new_index)
        current_index = new_index
    return new_line_positions


