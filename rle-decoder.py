# This module was created to provide support for the RLE format,
# as it is used to describe patterns in Conway's Game of Life.
#
# The RLE format is described in the following document:
# http://www.conwaylife.com/wiki/Run_Length_Encoded


from life import Pattern

class Decoder:
    '''Reads a Run Length Encoded (RLE) file and returns a Pattern object'''

    def __init__(self, filename):
        self._open_file(filename)
        self.pattern_name = None

    def _open_file(self, filename):
        # TODO: check validity
        self.filename = filename
    
    def decode(self):
        '''Reads the file and returns a Pattern object'''
        # TODO: read file and return a Pattern object
        file = open(self.filename, 'r')
        cells = [[]]

        while True:
            line = file.readline()
            if line.startswith('#'):
                self.pattern_name = line[2:] if line.startswith('N') else None
                continue

            # TODO: regex :D (good luck)

            if line.endswith('!'):
                break

        return Pattern(self.pattern_name, cells)

