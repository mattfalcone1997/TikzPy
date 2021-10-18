import subprocess
from shutil import which, copy, rmtree
from abc import ABC, abstractmethod

import os

class texSystem:
    def __init__(self,latex_cmd=None):
        if latex_cmd is None:
            self._latex_cmd = 'pdflatex'
        else:
            self._latex_cmd = latex_cmd

        if which(self._latex_cmd) is None:
            msg = "Latex command '%s' not on path"%self._latex_cmd
            raise ValueError(msg)

    def set_filename(self,filename,temp=True):
        basename = os.path.splitext(filename)[0]
        self._filename = filename
        self._wdir_name = "." + basename + "_wdir"
        self._is_temp_dir = temp

    def run_latex(self,tex_generator):
        cwd = os.getcwd()
        if not os.path.isdir(self._wdir_name):
            os.mkdir(self._wdir_name)

        os.chdir(self._wdir_name)
        with open(self._filename,'w') as file:
            file.writelines(tex_generator.write())

        cmd = [self._latex_cmd,
                "-interaction=nonstopmode",
                self._filename]
        log_file = os.path.splitext(self._filename)[0] + ".log"
        out = subprocess.run(cmd,capture_output=True)
        
        output_file = os.path.splitext(self._filename)[0] + ".pdf"
        copy(output_file,"..")
        copy(log_file,"..")

        os.chdir(cwd)
        if self._is_temp_dir:
            rmtree(self._wdir_name)

    # def __del__(self):
        # if self._is_temp_dir and os.path.isdir(self._wdir_name):
        #     os.rmdir(self._wdir_name)

class TikzError(Exception):
    def __init__(self,latex_output):
        if not isinstance(latex_output,subprocess.CompletedProcess):
            msg = (f"Input to TikzError must be a {subprocess.CompletedProcess.__name__}"
                    f" not {type(latex_output)}")

        if latex_output.returncode == 0:
            msg = "This exception should not be invoked with a zero return code"
            return RuntimeError(msg)
        self._stderr = latex_output.stderr

    def __str__(self):
        msg = "The latex subprocess returned the errors. Look at the latex log file\n" 
        return msg

class texBase(ABC):

    @abstractmethod
    def write(self):
        pass

class texGenerator(texBase):
    def __init__(self):
        self._preamble = texBlock()
    
    @property
    def document(self):
        if not hasattr(self,'_document'):
            msg = ("This property cannot be accessed until"
                " the start_document method has been called")
            raise AttributeError(msg)
            
        return self._document

    def set_document_class(self,name,options=None):
        if options is None:
            options = []

        doc_class = texDocumentClass(name,*options)
        for item in  self._preamble:
            if isinstance(item,texDocumentClass):
                msg = "A document class already exists"
                raise ValueError(msg)

        if len(self._preamble) > 0:
            preamble = texBlock(doc_class)
            preamble.add_items(self._preamble)
            self._preamble = preamble
        else:
            self._preamble = texBlock(doc_class)


    def add_to_preamble(self,*preamble):
        self._preamble.add_items(preamble)

    def add_package(self,name_or_package,options=None):
        if isinstance(name_or_package,texPackage):
            self.add_to_preamble(name_or_package)
        else:
            package = texPackage(name_or_package,options)
            self.add_to_preamble(package)

    def start_document(self):
        self._document = texEnvironment('document')

    def add_environment(self,environment):
        self._document.add_environment(environment)

    def add_block(self,block):
        if not hasattr(self,'_document'):
            self._preamble.add_items(block)
        else:
            self._document.add_command(*block)

    def add_command(self,command):
        if not hasattr(self,'_document'):
            self._preamble.add_items(command)
        else:
            self._document.add_command(command)

    def write(self):
        write_list = []
        
        write_list.extend(self._preamble.write())
        write_list.extend(self._document.write())

        return write_list

class texDocumentClass(texBase):
    def __init__(self,name,*options):
        self._name = name
        self._options = list(options)

    def write(self):
        if self._options:
            options = ",".join(self._options)
            return ["\documentclass[%s]{%s}\n"%(options,self._name)]
        else:
            return ["\documentclass{%s}\n"%self._name]

class texPackage(texBase):
    def __init__(self,name,*options):
        self._name = name
        self._options= options

    def write(self):
        if self._options:
            options = ",".join(self._options)
            return ["\\usepackage[%s]{%s}\n"%(options,self._name)]
        else:
            return ["\\usepackage{%s}\n"%self._name]

class texEnvironment(texBase):
    def __init__(self,name):
        self._name = name
        self._compulsory_args = []
        self._optional_args = []
        self._internal = []


    def add_compulsory_args(self,*args):
        self._compulsory_args.extend(args)
    
    def add_optional_args(self,*args):
        self._optional_args.extend(args)

    def add_internal(self,input):
        self._internal.append(input + "\n")
    
    def add_environment(self,environment):
        self._internal.append(environment)

    def add_command(self,command):
        self._internal.append(command)

    def add_item(self,item):
        if isinstance(item ,texCommand):
            self.add_command(item)
        elif isinstance(item,texEnvironment):
            self.add_environment(item)
        elif isinstance(item,texBlock):
            for i in item.get_list():
                self.add_item(i)

    def write(self):
        write_list = []
        env_string = "\\begin{%s}"%self._name
        if self._optional_args:
            env_string += "[%s]"%",".join(self._optional_args)

        if self._compulsory_args:
            env_string += "{%s}"%",".join(self._compulsory_args)

        write_list.append(env_string+"\n")

        for arg in self._internal:
            if isinstance(arg,texBase):
                write_list.extend(arg.write())
            else:
                write_list.append(arg)

        write_list.append("\end{%s}\n"%self._name)

        return write_list



class texCommand(texBase):
    def __init__(self,name,pgf=False):
        self._name = name
        self._compulsory_args = []
        self._optional_args = []
        self._pgf = pgf
    def add_compulsory_args(self,*args):
        self._compulsory_args.extend(args)

    def add_optional_args(self,*args):
        self._optional_args.extend(args)

    def write(self):
        command_string = "\%s"%self._name 
        if self._optional_args:
            command_string += "[%s]"%",".join(self._optional_args)
        for arg in self._compulsory_args:
            command_string += "{%s}"%arg

        if self._pgf:
            command_string += ";"

        command_string += "\n"

        return [command_string]


class texBlock(texBase):
    def __init__(self,*Block):
        if not all([isinstance(x,texBase) for x in Block]):
            msg = "All items must be an instane of texBase"
            raise TypeError(msg)

        self._command_list = list(Block)

    def add_items(self,items):
        if not all([isinstance(x,texBase) for x in items]):
            msg = "All items must be an instane of texBase"
            raise TypeError(msg)

        self._command_list.extend(items)

    def get_list(self):
        return self._command_list

    def write(self):
        writer =[]
        for command in self._command_list:
            writer.extend(command.write())
        return writer

    def __iter__(self):
        for x in self._command_list:
            yield x

    def __len__(self):
        return len(self._command_list)

    def __iadd__(self,other_tex):
        if hasattr(other_tex,'__iter__'):
            if not all([isinstance(tex,texBlock) for tex in other_tex]):
                msg = ("To use this command all inputs must be "
                "dervied from texBase or iterables of them")
                raise TypeError(msg)

            self.add_items(other_tex)

        else:
            self._command_list.append(other_tex)