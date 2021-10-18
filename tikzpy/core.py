
from abc import ABC, abstractmethod, abstractproperty
from . import _tex
from . import utils, _pgf
import os
class tikzObject(ABC):
    pass

class plottingObject(tikzObject):
    @abstractmethod
    def get_owner(self):
        pass

    


class canvasObject(plottingObject,ABC):
    _addable = True
    def plot_shape(self,shape,coord):
        pass

    def add_canvas(self,canvas):
        if not isinstance(canvas,canvasObject):
            msg = "Only canvasObjects can be added"
            raise TypeError(msg)
            
        if not canvas._addable:
            msg = "This canvas type cannot be owned"
            raise Exception(msg)

        if not all(bound in self.Bounds for bound in canvas.Bounds):
            msg = "The canvas bounding box must be within its owning canvas"
            raise ValueError(msg)
        
        canvas._owner = self
        self._objects_owned.append(canvas)

    @abstractproperty
    def Bounds(self):
        pass

    def get_local(self,coord):
        return self.Bounds.get_local(coord)

    def get_canvasses(self):
        canvases = []
        for object in self._objects_owned:
            if isinstance(object,canvasObject):
                canvases.append(object)
                canvases.extend(object.get_canvasses())
        return canvases


        

class rectCanvas(canvasObject):
   
    def __init__(self,canvas_size,centre, orientation=None, on_layer='main'):
        self._owner = None
        self._canvas_size = canvas_size
        self._coord = utils.rectCoord(*centre)
        self._layer = on_layer
        self._objects_owned = []

        self._set_bounds()

    def _set_bounds(self):
        half_size_x = 0.5*self._canvas_size[0]
        half_size_y = 0.5*self._canvas_size[1]
        x = self._coord[0]
        y = self._coord[1]
        self._bounds = utils.rectBound([utils.rectCoord(-half_size_x + x,-half_size_y + y),
                                    utils.rectCoord(-half_size_x + x,half_size_y + y),
                                    utils.rectCoord(half_size_x + x,half_size_y + y),
                                    utils.rectCoord(half_size_x + x,-half_size_y + y)])
    def get_owner(self):
        return self._owner

    def _generate_tex(self):
        block = _tex.texBlock()
        
        for object in self._objects_owned:
            block.add_items(object._generate_tex())

        return block

    @property
    def Coord(self):
        return self._coord

    @property
    def Bounds(self):
        return self._bounds

class MasterCanvas(rectCanvas):
    _addable = False
    def __init__(self,figsize,units='in'):
        centre = [0.5*figsize[0],
                    0.5*figsize[1]]

        super().__init__(figsize,centre)
        self._layers = ['main']
        
        self._units = units

    def check_objects(self):
        pass
    
    def define_layer(self,name,level=None):
        if level is None:
            self._layers.append(name)
        else:
            num_layers = len(self._layers)
            if level > num_layers:
                msg = ("The specified level cannot"
                        " be greater than the number of current layers")
                raise ValueError(msg)

            self._layers.insert(level,name)

    def _generate_tex(self):
        tikzpicture = _pgf.tikzpicture()
        pgf_layers = [_pgf.pgfLayer(x) for x in self._layers ]

        for canvas in self.get_canvasses():
            layer = canvas._layer
            for pgf in pgf_layers:
                if layer == pgf._name:
                    pgf.add_item(canvas._generate_tex())

        items = [item for item in self._objects_owned \
                        if not isinstance(item,canvasObject)]

        base_block = _tex.texBlock(*items)

        pgf_layers[0].add_item(base_block)

        for pgf in pgf_layers:
            
            tikzpicture.add_item(pgf)

        return tikzpicture

    def save(self,filename,keep_temps=False,**image_params):
        base, ext = os.path.splitext(filename)
        

        tikzpicture = self._generate_tex()
        packages = self._get_package_list()
        libraries = self._get_library_list()
        preamble_comms = self._get_preamble_commands()

        if ext == '.tex':
            tikzpicture.writefile(filename)

            self.output_preamble(base)

        elif ext in ('.png','.pdf'):
            master = _pgf.tikzMaster(ext,**image_params)

            master.add_packages(packages)
            master.add_tikz_libraries(libraries)
            master.add_preamble_commands(preamble_comms)

            master.add_tikzpicture(tikzpicture)

            master.write(filename,not keep_temps)

        else:
            msg = "Only png and pdf files can be handled"
            raise ValueError(msg)

    def _get_package_list(self):
        return [_tex.texPackage('tikz')]
    
    def _get_library_list(self):
        return _pgf.pgfLibraries()

    def _get_preamble_commands(self):
        commands = []
        for layer in self._layers:
            command = _tex.texCommand('pgfdeclarelayer')
            command.add_compulsory_args(layer)
            commands.append(command)
        setlayer = _tex.texCommand('pgfsetlayers')
        setlayer.add_compulsory_args(','.join(self._layers))
        commands.append(setlayer)

        return _tex.texBlock(*commands)

    def output_preamble(self,basename):
        packages = self._get_package_list()
        libraries = self._get_library_list()
        premable_comms = self._get_preamble_commands()

        filename = basename + "_preamble.tex"

        preamble_block = _tex.texBlock(*packages,libraries,*premable_comms)
        with open(filename,'w') as file:
            file.writelines(preamble_block.write())

    
