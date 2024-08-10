# This module was created to provide support for the RLE format,
# as it is used to describe patterns in Conway's Game of Life.
#
# The RLE format is described in the following document:
# http://www.conwaylife.com/wiki/Run_Length_Encoded
#
# In short, the format is as follows:
#   The header contains the name of the pattern, the width and height of the pattern, and the author.
#   The data is a series of lines, each line representing a row of the pattern.
#   Each line is a series of runs of cells, where a run is a number followed by a cell.
#   If the number is omitted, it is assumed to be 1.
#   Each cell is either 'o' or 'b', where 'o' represents a live cell and 'b' represents a dead cell.
#   The end of the data is denoted by a '!' character.

from life import Pattern
import re
import os

def _open_file(file_path):
    if os.path.exists(file_path):
        return open(file_path, 'r')
    else:
        raise FileNotFoundError(f"File '{file_path}' not found")

def decode(file_path):
    '''Reads the file and returns a Pattern object'''
    file = _open_file(file_path)

    pattern_w = None
    pattern_h = None
    pattern_name = "Unknown Pattern"

    line = 'stub'
    while not (line.endswith('!') or not line):
        # read the next line
        line = file.readline()

        # information parsing
        if line.startswith('#'):
            info_type = line[1]
            match (info_type):
                case 'N':
                    pattern_name = line[2:].strip('\n   ') 
            continue
        
        # header parsing
        if not (pattern_w and pattern_h):
            match = re.search(r"x\s*=\s*(\d+),\s*y\s*=\s*(\d+)", line)
            if match:
                pattern_w = int(match.group(1))
                pattern_h = int(match.group(2))
                
                cells = [[] for _ in range(pattern_h)]
        
        # data parsing
        pattern_lines = line.split('$')
        offset = 0
        
        for index, body_line in enumerate(pattern_lines):
            
            # skip empty lines
            if not body_line:
                continue
            
            # find all the multiple or single runs of 'o' or 'b'
            for match in re.finditer(r"(\d+)([bo])|([bo])", body_line):
            
                # if there is a number, append that many cells
                if match.group(1):
                    for i in range(int(match.group(1))):
                        cells[index + offset].append(1 if match.group(2) == 'o' else 0)
                
                # if there is no number, append a single cell
                else:
                    cells[index + offset].append(1 if match.group(3) == 'o' else 0)
            
            # if the line ends with a number, add that many blank rows
            if body_line[-1].isnumeric():
                offset += int(body_line[-1]) - 1
        
    # pad the pattern with dead cells
    for row in cells:
        for i in range(pattern_w - len(row)):
            row.append(0)

    # pad the pattern with dead rows
    for i in range(pattern_h - len(cells)):
        if i % 2 == 0:
            cells.append([0 for _ in range(pattern_w)])
        else:
            cells.insert(0, [0 for _ in range(pattern_w)])

    # return the pattern
    return Pattern(pattern_name, cells)

def encode(self, file_path):
    '''Encodes the Pattern object into a file'''
    # TODO: encode the pattern into a file