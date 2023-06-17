from abc import ABC, abstractmethod

import os

class source(ABC):
    def __init__(self, captures, results):
        name = self.__class__.__name__.split('_')[0]
        if captures is None or captures == '':
            captures = os.path.join('audio', name, 'sources')

        if results is None or captures == '':
            results = os.path.join('out', name, 'sources')

        self.captures = captures
        self.results = results

    @abstractmethod
    def acquire(self, duration, plot):
        pass
