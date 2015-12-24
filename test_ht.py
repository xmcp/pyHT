import libtreasure as lib
from tkinter import *

tk=Tk()
msg=StringVar()

Label(tk,textvariable=msg).grid(row=0,column=0)
t=Text(tk,font='monospace -14',height=lib.GY+1,width=lib.GX*2)
t.grid(row=1,column=0)

game=lib.Game()

def redraw(*_):
    t.delete(1.0,END)
    for row in game.g:
        t.insert(END,''.join([pretty_table[x] for x in row])+'\n')
    tk.title('cur = %d / goal = %d'%(game.cur,game.goal))
    msg.set('face = %s / life = %d / restore time = %d'%('left' if game.player.left else 'right',game.player.life,game.player.life_restore))

def cmd(value):
    game.player.command=value
    game.tick()
    redraw()

pretty_table={
    lib.Elem.chunk[0]:'①',
    lib.Elem.chunk[1]:'②',
    lib.Elem.chunk[2]:'③',
    lib.Elem.dirt:'■',
    lib.Elem.evildirt:'▒',
    lib.Elem.empty:'　',
    lib.Elem.heart:'☆',
    lib.Elem.fire:'卐',
    lib.Elem.player:'Ｐ',
}
tk.bind('<Left>',lambda *_:cmd(lib.Command.left))
tk.bind('<Right>',lambda *_:cmd(lib.Command.right))
tk.bind('<Up>',lambda *_:cmd(lib.Command.next))
tk.bind('<Down>',lambda *_:cmd(lib.Command.down))
tk.bind('<Return>',lambda *_:game.tick() or redraw())

game.init_level(10)
redraw()
mainloop()