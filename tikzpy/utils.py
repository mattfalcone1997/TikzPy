

from abc import ABC, abstractmethod, abstractproperty
import numpy as np
from numpy import linalg
import operator
class rectCoord:
    def __init__(self,x,y):
        self._coord = np.array([x,y])

    def to_array(self):
        return self._coord

    def _arith_binary(self,coord,op):
        new_coords = op(self._coord,coord._coord)
        return self.__class__(*new_coords)

    def __add__(self,coord):
        return self._arith_binary(coord,operator.add)

    def __sub__(self,coord):
        return self._arith_binary(coord,operator.sub)
    
    def __getitem__(self,key):
        return self._coord[key]

    def __str__(self):
        return "%s(%s, %s)"%(self.__class__.__name__,self[0],self[1])

    def __repr__(self):
        return self.__str__()

class boundObject(ABC):
    @abstractmethod
    def __contains__(self):
        pass

class rectBound(boundObject):
    def __init__(self,corners):
        
        self._corners = corners

    def __contains__(self,coord):
        if isinstance(coord,tuple):
            coord = rectCoord(*coord)

        basis = self.get_basis()

        b = (coord - self._corners[0]).to_array()
        A = np.stack(basis).T
        x = linalg.solve(A,b)

        if x[0] > 1 or x[0] < 0:
            return False
        if x[1] > 1 or x[1] < 0:
            return False
        return True

    def get_basis(self):
        basisVector1 = (self._corners[1] - self._corners[0]).to_array()
        basisVector2 = (self._corners[-1] - self._corners[0]).to_array()

        return [basisVector1,basisVector2]

    def get_local(self,coord):
        basis = self.get_basis()
        A = np.stack(basis).T
        coord = np.array(coord)
        local = np.matmul(A,coord)
        return rectCoord(*local)

    def __iter__(self):
        for bound in self._corners:
            yield bound

    def __str__(self):
        coords = ["%.3g, %.3g"%(x._coord[0],x._coord[1]) for x in self._corners]

        return "%s([(%s),(%s),(%s),(%s)])"%(self.__class__.__name__,*coords)
    def __repr__(self):
        return self.__str__()