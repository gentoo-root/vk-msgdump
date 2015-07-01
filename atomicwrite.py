import os

class AtomicWrite(object):
    def __init__(self, filename, binary=False):
        self._filename = filename
        self._binary = binary

    def __enter__(self):
        self._file = open(self._filename + '.part', 'w' + 'b'*self._binary)
        return self._file

    def __exit__(self, exc_type, exc_value, traceback):
        self._file.close()
        os.rename(self._filename + '.part', self._filename)
