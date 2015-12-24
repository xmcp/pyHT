#coding=utf-8
import random
import math

GX=23
GY=35
ELEM_PROB=.05
EVIL_PROB=.05
GOAL_OF_LEVEL=lambda level:300+level*100

class GameOver(Exception):
    def __str__(self):
        return 'Game Over'

class YouWin(Exception):
    def __str__(self):
        return 'You Win'

class _FireStopped(Exception):
    pass

class Elem:
    dirt='Dirt'
    evildirt='Evil Dirt'
    empty='Empty'
    fire='Fire'
    heart='Heart'
    chunk=['Chunk1','Chunk2','Chunk3']
    player='player'
SALARY={Elem.chunk[0]:100, Elem.chunk[1]:200, Elem.chunk[2]:300}

class Command:
    left='Move Left'
    right='Move Right'
    next='Digg Next'
    down='Digg Down'

class Fire:
    def __init__(self,game,y,x):
        self.left=False
        self.y=y
        self.x=x
        self.game=game

    def step(self):
        if self.y<GY-1 and self.game.g[self.y+1][self.x]==Elem.empty: #go down
            self.y+=1
            self.game.g[self.y+1][self.x]=Elem.fire
            self.game.g[self.y][self.x]=Elem.empty
        elif self.game.g[self.y+1][self.x] in Elem.chunk+[Elem.heart]: #burn down
            self.game.new_fire(self.y+1,self.x)
        elif self.game.g[self.y][self.x+1]==self.game.g[self.y][self.x-1] in (Elem.dirt,Elem.evildirt,Elem.fire): #do nothing
            return
        else:
            if self.x==0: self.left=False
            if self.x==GX-1: self.left=True
            nextx=self.x-1 if self.left else self.x+1
            if self.game.g[self.y][nextx] in (Elem.dirt,Elem.evildirt): self.left=not self.left

            if self.game.g[self.y][nextx]==Elem.empty: #go next
                self.x=nextx
                self.game.g[self.y][nextx]=Elem.fire
                self.game.g[self.y][self.x]=Elem.empty
            elif self.game.g[self.y][nextx] in Elem.chunk+[Elem.heart]: #burn next
                self.game.new_fire(self.y,nextx)
            elif self.game.g[self.y][nextx]==Elem.fire: #ourselves, just keep calm
                pass
            elif self.game.g[self.y][nextx]==Elem.player: #beat it
                if self.game.player.hurt(20):
                    raise _FireStopped()
            else:
                raise RuntimeError('bad next elem: %s'%self.game.g[self.y][nextx])


class Player: #todo
    def __init__(self,game,y,x):
        self.life=100
        self.life_restore=0
        self.left=False
        self.command=None
        self.game=game
        self.y=y
        self.x=x

    def _move(self,x):
        def go():
            self.x=x
            self.game.g[self.y][self.x]=Elem.empty
            self.game.f[self.y][x]=Elem.player

        if self.game.g[self.y][x]==Elem.empty:
            go()
        elif self.game.g[self.y][x]==Elem.heart:
            self.life=min(self.life+25,100)
            go()
        elif self.game.g[self.y][x] in Elem.chunk:
            self.game.cur+=SALARY[self.game.g[self.y][x]]
            if self.game.cur>self.game.goal:
                raise YouWin()
            go()

    def tick(self):
        if self.life_restore:
            self.life_restore-=1
        self.life-=1
        if self.life<=0:
            raise GameOver()

        { #todo: start from here
            Command.down: lambda:
        }
        self.command=None

    def hurt(self,value):
        if self.life_restore:
            return False
        else:
            self.life-=value
            self.life_restore=10
            if self.life<=0:
                raise GameOver()
            return True

class Game:
    def __init__(self):
        self.g=None
        self.cur=0
        self.goal=0
        self.fires=set()
        self.player=Player(self,0,0)
        self.init_level(1)

    def init_level(self,level):
        #init grid
        self.g=[[Elem.dirt if random.random()>EVIL_PROB else Elem.evildirt for x in range(GX)] for y in range(GY)]
        self.g[0][math.floor(GX/2)]=Elem.player
        #put goods
        available=[(y,x) for y in range(GY) for x in range(GX) if self.g[y][x]==Elem.dirt]
        for y,x in random.sample(available,math.ceil(GX*GY*ELEM_PROB)):
            self.g[y][x]=random.choice(Elem.chunk+[Elem.heart])
        #init data
        self.cur=0
        self.goal=GOAL_OF_LEVEL(level)
        self.fires=[]
        self.player=Player(self,0,math.floor(GX/2))

    def move_fire(self):
        for fire in sorted(self.fires,key=lambda this:this.y*GX+this.x):
            try:
                fire.step()
            except _FireStopped:
                self.g[fire.y][fire.x]=Elem.empty

    def new_fire(self,y,x):
        self.g[y][x]=Elem.fire
        self.fires.add(Fire(self,y,x))
