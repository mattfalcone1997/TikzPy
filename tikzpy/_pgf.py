from . import _tex

class tikzMaster:
    def __init__(self,ext,**image_params):
        self._texgen = _tex.texGenerator()
        
        if ext != '.pdf':
            options = self.set_image_options(ext,**image_params)
        else:
            options = None

        self._texgen.set_document_class('standalone',options=options)

        self._packages = _tex.texBlock()
        self._libraries = pgfLibraries()
        self._preamble_commands = _tex.texBlock()

    def add_packages(self,packages):
        self._packages.add_items(packages)

    def add_tikz_libraries(self,libraries):
        self._libraries.add_libraries(libraries)

    def add_preamble_commands(self,*commands):
        if not all([isinstance(x,(_tex.texCommand,_tex.texBlock)) for x in commands]):
            msg = "Problem"
            raise TypeError(msg)

        self._preamble_commands.add_items(commands)
        
    def add_tikzpicture(self,tikzpicture):
        self._tikzpicture = tikzpicture

    def write(self,filename,temp):
        texsys = _tex.texSystem()
        
        self._texgen.add_to_preamble(self._packages)

        self._texgen.add_to_preamble(self._libraries)

        for command in self._preamble_commands:
            self._texgen.add_command(command)

        self._texgen.start_document()

        self._texgen.add_environment(self._tikzpicture)

        texsys.set_filename(filename,temp=temp)

        texsys.run_latex(self._texgen)

    def set_image_options(self,ext,dpi):
        return ("convert=\{outext=%s, density=%d\}"%(ext,int(dpi)))


class pgfLayer(_tex.texEnvironment):
    def __init__(self,name):
        super().__init__('pgfonlayer')
        self.add_compulsory_args(name)

class pgfLibraries(_tex.texBase):
    def __init__(self,*names):
        self._names = list(names)

    def add_libraries(self,*names):
        for name in names:
            if isinstance(name,str):
                self._names.append(name)
            elif isinstance(name,pgfLibraries):
                self._names.extend(name._names)


    def write(self):
        library = ",".join(self._names)
        return ["\\usetikzelibrary{%s}\n"%library]

class tikzpicture(_tex.texEnvironment):
    def __init__(self,*options):
        super().__init__('tikzpicture')
        if options:
            self.add_optional_args(*options)


    def writefile(self,filename):
        with open(filename,'w') as file:
                file.writelines(self.write())

class node:

    @classmethod
    def from_coords(cls,x,y,name=None):
        pass

    @classmethod
    def from_reference(cls,name,offset):
        pass

    def add_options(self,*options):
        pass

    def __init__(self,*options):
        pass

    def add_text(self,text):
        pass

class draw:
    @classmethod
    def from_nodes(cls,*nodes):
        pass

    def add_options(self,*options):
        pass



