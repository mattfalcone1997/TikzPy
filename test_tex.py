import tikzpy
from tikzpy import _tex

tex = _tex.texSystem()

tex.set_filename("test.tex")

texgen = _tex.texGenerator()
texgen.set_document_class('article')
texgen.add_package('amsmath')

title = _tex.texCommand('title')
title.add_compulsory_args('Hello from tikzpy')

texgen.add_command(title)

texgen.start_document()

maketitle = _tex.texCommand('maketitle')

texgen.add_command(maketitle)


itemenv = _tex.texEnvironment('itemize')
itemenv.add_command(_tex.texCommand('item test'))

texgen.add_environment(itemenv)
print(texgen.write())
tex.run_latex(texgen)



