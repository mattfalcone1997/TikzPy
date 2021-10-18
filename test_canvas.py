import tikzpy

canvas = tikzpy.MasterCanvas([10,5])
centre = canvas.get_local([0.5,0.5])
subcanvas = tikzpy.rectCanvas([4,4],centre)

canvas.add_canvas(subcanvas)

canvas.save('test.pdf')
