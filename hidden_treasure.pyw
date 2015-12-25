#coding=utf-8
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

import time
import queue

import libtreasure as lib
import threading

tk=Tk()
tk.title('Hidden Treasure')
tk.resizable(False,False)

game=lib.Game()
cmds=queue.Queue()
SZ=32
BORDER=10
TICKTIME=.4
moneymsg=StringVar()

dg=[[None for x in range(lib.GX)] for y in range(lib.GY)]
onscreen=[[None for x in range(lib.GX)] for y in range(lib.GY)]
material={
    lib.Elem.chunk[0]: PhotoImage(file='img/chunk1.gif'),
    lib.Elem.chunk[1]: PhotoImage(file='img/chunk2.gif'),
    lib.Elem.chunk[2]: PhotoImage(file='img/chunk3.gif'),
    lib.Elem.dirt: PhotoImage(file='img/dirt.gif'),
    lib.Elem.evildirt: PhotoImage(file='img/dirt.gif'),
    lib.Elem.empty: PhotoImage(file='img/empty.gif'),
    lib.Elem.fire: PhotoImage(file='img/fire.gif'),
    lib.Elem.heart: PhotoImage(file='img/heart.gif'),
    lib.Elem.player: PhotoImage(file='img/player.gif'),
}

def cmd(value):
    cmds.put(value)

def game_controller():
    init_level(1)
    while True:
        try:
            try:
                if not game.player.command:
                    x=cmds.get_nowait()
                    game.player.command=x
            except queue.Empty:
                game.player.command=''
            game.tick()
            tick_routine()
            time.sleep(TICKTIME)
        except lib.GameOver:
            messagebox.showerror('Hidden Trasure','您输了')
            init_level(1)
        except lib.YouWin:
            messagebox.showinfo('Hidden Trasure','您赢了')
            init_level(game.level+1)


def tick_routine(redraw=False): #todo: player position and life restore
    #update canvas
    for y in range(lib.GY):
        for x in range(lib.GX):
            if redraw or game.g[y][x] is not onscreen[y][x]:
                onscreen[y][x]=game.g[y][x]
                if dg[y][x]:
                    canvas.delete(dg[y][x])
                dg[y][x]=canvas.create_image(x*SZ,y*SZ,anchor='nw',image=material[game.g[y][x]])
    #update data
    tk.title('Hidden Treasure [ Level %d]'%game.level)
    moneymsg.set('Money: %d / %d'%(game.cur,game.goal))
    lifebar['value']=game.player.life
    #focus on player
    canvas.yview_moveto((BORDER+game.player.y-3.5)/(lib.GY+2*BORDER))
    canvas.xview_moveto((BORDER+game.player.x-4.5)/(lib.GX+2*BORDER))

def init_level(level):
    global dg
    global onscreen
    dg=[[None for x in range(lib.GX)] for y in range(lib.GY)]
    onscreen=[[None for x in range(lib.GX)] for y in range(lib.GY)]
    canvas.delete('all')
    game.init_level(level)
    canvas['scrollregion']=(-BORDER*SZ,-BORDER*SZ,(BORDER+lib.GX)*SZ,(BORDER+lib.GY)*SZ)
    tick_routine(redraw=True)

f=Frame(tk)
f.grid(row=0,column=0,sticky='we')
f.columnconfigure(1,weight=1)

lifebar=Progressbar(f,orient=HORIZONTAL,length=100,value=100,mode='determinate')
lifebar.grid(row=0,column=0)
Label(f).grid(row=0,column=1,sticky='we')
Label(f,textvariable=moneymsg).grid(row=0,column=2)

canvas=Canvas(tk,width=10*SZ,height=10*SZ,bg='#bb0077')
canvas.grid(row=1,column=0,sticky='nswe')

tk.bind('<Left>',lambda *_:cmd(lib.Command.left))
tk.bind('<Right>',lambda *_:cmd(lib.Command.right))
tk.bind('<Up>',lambda *_:cmd(lib.Command.next))
tk.bind('<Down>',lambda *_:cmd(lib.Command.down))
tk.after(1,lambda *_:threading.Thread(target=game_controller).start())
mainloop()