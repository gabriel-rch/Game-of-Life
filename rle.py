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

class Decoder:
    '''Reads a Run Length Encoded (RLE) file and returns a Pattern object'''

    def __init__(self, filename):
        self._open_file(filename)
        self.pattern_name = None
        self.pattern_w = None
        self.pattern_h = None

    def _open_file(self, filename):
        # TODO: check existence of file
        self.filename = filename
    
    def decode(self):
        '''Reads the file and returns a Pattern object'''
        # TODO: read file and return a Pattern object
        file = open(self.filename, 'r')

        while True:
            line = file.readline()

            # Information parsing
            if line.startswith('#'):
                self.pattern_name = line[2:] if line.startswith('N') else None
                continue

            # Header parsing
            if not self.pattern_w:
                # match the width and height of the pattern
                match_w = re.search(r"x\s*=\s*(\d+)", line)
                match_h = re.search(r"y\s*=\s*(\d+)", line)

                if match_w and match_h:
                    w = int(match_w.group(1))
                    h = int(match_h.group(1))

                    cells = [[] for i in range(h)]

                    # choose the largest dimension as the width and height
                    self.pattern_w = h if h > w else w
                    self.pattern_h = w if w > h else h

                    continue
                
                else:
                    # TODO: handle invalid file
                    pass
            
            # Data parsing

            # TODO: detect invalid file

            # split the data into a list of the lines in the pattern
            pattern_lines = line.split('$')

            offset = 0

            # iterate over the lines in the pattern
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

            # if the line ends with a '!', or is empty, stop reading the file
            if line.endswith('!') or not line:
                break
        
        # pad the pattern with dead cells
        for row in cells:
            for i in range(self.pattern_w - len(row)):
                row.append(0)

        # pad the pattern with dead rows
        for i in range(self.pattern_h - len(cells)):
            if i % 2 == 0:
                cells.append([0 for i in range(self.pattern_w)])
            else:
                cells.insert(0, [0 for i in range(self.pattern_w)])

        # if the pattern name was not found in the file, use the filename
        if not self.pattern_name:
            self.pattern_name = self.filename[:-4]
        
        # return the pattern
        return Pattern(self.pattern_name, cells)


class Encoder:
    '''Encodes a Pattern object into a Run Length Encoded (RLE) file'''

    def __init__(self, pattern):
        self.pattern = pattern

    def encode(self, filename):
        '''Encodes the Pattern object into a file'''
        # TODO: encode the pattern into a file