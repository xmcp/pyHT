#coding=utf-8
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

import time
import queue

import libtreasure as lib
import threading

tk=Tk()
tk.title('挖宝藏')
tk.resizable(False,False)

DESCRIPTION='您的使命是搜寻地下宝藏。\n按 ← 向左移，按 → 向右移，按 ↑ 向前挖，按 ↓ 向下挖。\n'\
    '当心触火，用心自疗，并在健康降至零点之前到达目标。'
ABOUT='名称：挖宝藏\n开发者：@xmcp'
game=lib.Game()
cmds=queue.Queue()
SZ=32
BORDER=10
TICKTIME=.4
INIT_LEVEL=11
paused=False
moneymsg=StringVar()
hudvar=StringVar()

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
}
player={
    'LeftNormal':PhotoImage(file='img/playerL.gif'),
    'RightNormal':PhotoImage(file='img/playerR.gif'),
    'LeftHurt':PhotoImage(file='img/playerHurtL.gif'),
    'RightHurt':PhotoImage(file='img/playerHurtR.gif'),
}

def pause():
    global paused
    paused=not paused
    pausebtn.state(['pressed' if paused else '!pressed'])
    pausebtn['text']='已暂停' if paused else '暂停'

def cmd(value):
    cmds.put(value)

def show_hud(msg):
    hudvar.set(' %s '%msg)
    hud.grid(row=1,column=0)
    time.sleep(2)
    hud.grid_forget()

def game_controller():
    init_level(INIT_LEVEL)
    show_hud('等级 %d：$ %d'%(game.level,game.goal))
    while True:
        if paused:
            time.sleep(.1)
            continue
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
            show_hud('您输了')
            show_hud('您的成绩：等级 %d'%game.level)
            init_level(INIT_LEVEL)
            show_hud('等级 %d：$ %d'%(game.level,game.goal))
        except lib.YouWin:
            show_hud('您赢了')
            init_level(game.level+1)
            show_hud('等级 %d：$ %d'%(game.level,game.goal))


def tick_routine(redraw=False):
    def get_player_img():
        return player[('Left' if game.player.left else 'Right')+('Hurt' if game.player.life_restore else 'Normal')]
    #update canvas
    for y in range(lib.GY):
        for x in range(lib.GX):
            if redraw or game.g[y][x] is not onscreen[y][x] or game.g[y][x]==lib.Elem.player:
                onscreen[y][x]=game.g[y][x]
                if dg[y][x]:
                    canvas.delete(dg[y][x])
                if game.g[y][x]==lib.Elem.player:
                    dg[y][x]=canvas.create_image(x*SZ,y*SZ,anchor='nw',image=get_player_img())
                else:
                    dg[y][x]=canvas.create_image(x*SZ,y*SZ,anchor='nw',image=material[game.g[y][x]])
    #update data
    tk.title('挖宝藏 [ 等级 %d ]'%game.level)
    moneymsg.set('$ %d / %d'%(game.cur,game.goal))
    moneybar['value']=game.cur
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
    moneybar['value']=0
    moneybar['maximum']=game.goal
    tick_routine(redraw=True)

f=Frame(tk)
f.grid(row=0,column=0,sticky='we')
f.columnconfigure(2,weight=1)

lifebar=Progressbar(f,orient=HORIZONTAL,length=100,value=100,maximum=100,mode='determinate')
lifebar.grid(row=0,column=0)
Label(f,text='生命').grid(row=0,column=1)
Label(f).grid(row=0,column=2,sticky='we')
Label(f,textvariable=moneymsg).grid(row=0,column=3)
moneybar=Progressbar(f,orient=HORIZONTAL,length=80,value=0,maximum=1,mode='determinate')
moneybar.grid(row=0,column=4)

canvas=Canvas(tk,width=10*SZ,height=10*SZ,bg='#770055')
canvas.grid(row=1,column=0,sticky='nswe')
hud=Label(tk,textvariable=hudvar,background='#000055',foreground='#ffffff',font='黑体 -30')

infof=Frame(tk)
infof.grid(row=2,column=0,sticky='we')
infof.columnconfigure(1,weight=1)

pausebtn=Button(infof,text='暂停',width=8,command=pause)
pausebtn.grid(row=0,column=0)
Label(infof).grid(row=0,column=1,sticky='we')
Button(infof,text='操作说明',width=8,command=lambda:messagebox.showinfo('操作说明',DESCRIPTION)).grid(row=0,column=2)
Button(infof,text='关于',width=8,command=lambda:messagebox.showinfo('关于',ABOUT)).grid(row=0,column=3)


tk.bind_all('<Left>',lambda *_:cmd(lib.Command.left))
tk.bind_all('<Right>',lambda *_:cmd(lib.Command.right))
tk.bind_all('<Up>',lambda *_:cmd(lib.Command.next))
tk.bind_all('<Down>',lambda *_:cmd(lib.Command.down))
tk.after(0,lambda *_:threading.Thread(target=game_controller).start())
mainloop()