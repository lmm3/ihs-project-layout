#!/usr/bin/python3

import math
import random
import pygame
import tk
#from tk import messagebox
import os, sys
from fcntl import ioctl
import threading
from ioctl_cmds import *
import time

class Cube(object):
    rows = 20
    width = 500
    def __init__(self,start,dirnx=1,dirny=0,color=(255,0,0)):
        self.pos = start
        self.dirnx =1
        self.dirny =0
        self.color = color

    def move(self,dirnx,dirny):
        self.dirnx = dirnx
        self.dirny = dirny

        self.pos=(self.pos[0]+self.dirnx,self.pos[1]+self.dirny)

    def draw(self,surface,eyes=False):
        dis = self.width // self.rows
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface,self.color,(i*dis+1,j*dis+1,dis-2,dis-2))
        
        if eyes:
            center = dis//2
            radius = 3
            circle_middle = (i*dis + center-radius,j*dis+8)
            circle_middle2 =(i*dis + dis-radius*2,j*dis+8)
            pygame.draw.circle(surface,(0,0,0),circle_middle,radius)
            pygame.draw.circle(surface,(0,0,0),circle_middle2,radius)


class Snake(object):
    body = []
    turns = {}
    def __init__(self,color,pos):
        self.color=color
        self.head = Cube(pos)
        self.body.append(self.head)
        #directions of the movement
        self.dirnx=0
        self.dirny=1

    def move(self, fd):
        ioctl(fd, RD_PBUTTONS)
        red = os.read(fd, 4); # read 4 bytes and store in red var
        #print("red 0x%X"%int.from_bytes(red, 'little'))

    
        flagMove =0
        #moveFPGAL = #receber click esquerda do fpga Aqui
        #moveFPGAR = #receber click direita do fpga Aqui
        #moveFPGAU = #receber click cima do fpga Aqui
        #moveFPGAD = #receber click baixo do fpga Aqui
        #Move Left
        #print(int.from_bytes(red,'little'))
        button = int.from_bytes(red,'little')
        #print(button)
         
        if (button == 14 and flagMove==0):
            flagMove = 1
            if((self.dirnx !=-1 and self.dirny !=0) or len(self.body)<3):
                self.dirnx = 1
                self.dirny = 0
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        elif(button == 15 and flagMove==1):
            flagMove = 0
        #Move Right
        if (button == 7 and flagMove==0):
            flagMove = 1
            if((self.dirnx !=1 and self.dirny !=0) or len(self.body)<3):
                self.dirnx = -1
                self.dirny = 0
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        elif((button == 15 and flagMove==1)):
            flagMove = 0
        #Move Up
        if (button ==13 and flagMove==0):
            flagMove = 1
            if((self.dirnx !=0 and self.dirny !=1) or len(self.body)<3):
                self.dirnx = 0
                self.dirny = -1
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        elif(button == 15 and flagMove==1):
            flagMove = 0
        #Move Down
        if (button == 11 and flagMove==0):
            flagMove = 1
            if((self.dirnx !=0 and self.dirny !=-1) or len(self.body)<3):
                self.dirnx = 0
                self.dirny = 1
                self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
        elif(button == 15 and flagMove==1):
            flagMove = 0
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            keys = pygame.key.get_pressed()

            for key in keys:

                if keys[pygame.K_LEFT]:
                    self.dirnx = -1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
                elif keys[pygame.K_RIGHT]:
                    self.dirnx = 1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
                elif keys[pygame.K_UP]:
                    self.dirnx = 0
                    self.dirny = -1
                    self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]
                elif keys[pygame.K_DOWN]:
                    self.dirnx = 0
                    self.dirny = 1
                    self.turns[self.head.pos[:]] = [self.dirnx,self.dirny]

            # [:] this operator makes a copy  

        for i,c in enumerate(self.body):
            p = c.pos[:]
            #       print(self.turns)
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0],turn[1])
                if i == len(self.body)-1:
                    self.turns.pop(p)
            else:
                if c.dirnx == -1 and c.pos[0] <=0:
                    c.pos = (c.rows-1,c.pos[1])  
                elif c.dirnx == 1 and c.pos[0] >=c.rows-1:
                    c.pos = (0,c.pos[1]) 
                elif c.dirny == 1 and c.pos[1] >=c.rows-1:
                    c.pos = (c.pos[0],0) 
                elif c.dirny == -1 and c.pos[1] <=0:
                    c.pos = (c.pos[0],c.rows-1) 
                else:
                    c.move(c.dirnx,c.dirny)
                
    def reset(self,pos):
        self.head = Cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def add_cube(self):
        tail = self.body[-1]
        dx,dy = tail.dirnx,tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0]-1,tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0]+1,tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0],tail.pos[1]-1)))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0],tail.pos[1]+1)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self,surface):
        for i,c in enumerate(self.body):
            if i==0:
                c.draw(surface,True)
            else:
                c.draw(surface)

def draw_grid(width,rows,surface):
    size_btwn = width//rows

    x = 0
    y = 0
    for l in range(rows):
        x = x + size_btwn
        y = y + size_btwn 

        pygame.draw.line(surface,(255,255,255),(x,0),(x,width))
        pygame.draw.line(surface,(255,255,255),(0,y),(width,y))

def redraw_window(surface):
    global width, rows,s,snack
    surface.fill((0,0,0))
    s.draw(surface)
    snack.draw(surface)
    draw_grid(width,rows,surface)
    pygame.display.update()

def charme(fd):
    while(True):
        data = 0xFEFEFEFE
        ioctl(fd, WR_L_DISPLAY)
        retval = os.write(fd, data.to_bytes(4, 'little'))
        time.sleep(0.2)
        data = 0xFDFDFDFD
        ioctl(fd, WR_L_DISPLAY)
        retval = os.write(fd, data.to_bytes(4, 'little'))
        time.sleep(0.2)
        data = 0xFBFBFBFB
        ioctl(fd, WR_L_DISPLAY)
        retval = os.write(fd, data.to_bytes(4, 'little'))
        time.sleep(0.2)
        data = 0xF7F7F7F7
        ioctl(fd, WR_L_DISPLAY)
        retval = os.write(fd, data.to_bytes(4, 'little'))
        time.sleep(0.2)
        data = 0xEFEFEFEF
        ioctl(fd, WR_L_DISPLAY)
        retval = os.write(fd, data.to_bytes(4, 'little'))
        time.sleep(0.2)
        data = 0xDFDFDFDF
        ioctl(fd, WR_L_DISPLAY)
        retval = os.write(fd, data.to_bytes(4, 'little'))
        time.sleep(0.2)

        
def blinking(fd):
    for i in range(3):
        data = 0x00000000
        ioctl(fd, WR_GREEN_LEDS)
        retval = os.write(fd, data.to_bytes(4, 'little'))
        time.sleep(0.02)
        data = 0x0000007f
        ioctl(fd, WR_GREEN_LEDS)
        retval = os.write(fd, data.to_bytes(4, 'little'))
        time.sleep(0.02)
        
    data = 0x00000000
    ioctl(fd, WR_GREEN_LEDS)
    retval = os.write(fd, data.to_bytes(4, 'little'))
        

def random_Snack(rows,item, fd):

    blink = threading.Thread(target=blinking, args=(fd,))
    blink.start()
    positions = item.body

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z: z.pos ==(x,y),positions)))>0:
            continue
        else:
            break

    return (x,y)

def message_box(subject,content):
    root = tk.Tk()
    root.attributes("-topmost",True)
    root.withdraw()
    tk.messagebox.showinfo(subject,content)
    try:
        root.destroy()
    except:
        pass

def startGame(fd):
    ioctl(fd,RD_SWITCHES)
    switch_status =os.read(fd,4)
    aux = int.from_bytes(switch_status, 'little')
    #print(aux)
    if (aux %2== 1):
        return True
    else:
        return False

def quitGame(fd):
    ioctl(fd,RD_SWITCHES)
    switch_status =os.read(fd,4)
    aux = int.from_bytes(switch_status, 'little')
   # print(aux)
    if (aux == 131073 or aux == 131072 or aux == 131074 or aux == 131075 ):
        exit(1)
    else:
        return False
    
def numMap(score):
    if (score ==0):
        return 0xC0
    if (score == 1):
        return 0xF9
    if (score == 2):#00010010
        return 0xA4
    if (score == 3):#00000110
        return 0xB0
    if (score == 4):#01001100
        return 0X99
    if (score == 5):#00100100
        return 0X92
    if (score == 6):#00100000
        return 0X82
    if (score == 7):#00001111
        return 0XF8
    if (score == 8):#00000000
        return 0X80
    if (score == 9):#00000100
        return 0X90

def drawScore(fd, score):
    if(score%10 == score):
        data = 0X40404000 + numMap(score)
        ioctl(fd,WR_R_DISPLAY)
        retval= os.write(fd, data.to_bytes(4,'little'))
    else:
        dataMinus = numMap(score%10)
        dataUpper = numMap(score//10) * 0x100
        data = 0x40400000 + dataUpper + dataMinus
        ioctl(fd,WR_R_DISPLAY)
        retval= os.write(fd, data.to_bytes(4,'little'))
        
    

def slowGame(fd):
    ioctl(fd,RD_SWITCHES)
    switch_status =os.read(fd,4)
    aux = int.from_bytes(switch_status, 'little')
   # print(aux)
    if (aux == 3):
        return 5
    else:
        return 10

def ledRed(fd, score):
    data = pow(0x2,score % 0x12) -0x1
    ioctl(fd, WR_RED_LEDS)
    retval = os.write(fd, data.to_bytes(4, 'little'))

def main():
    if len(sys.argv) < 2:
        print("Error: expected more command line arguments")
        print("Syntax: %s </dev/device_file>"%sys.argv[0])
        exit(1)
    #print("wrote %d bytes"%retval)
    fd = os.open(sys.argv[1], os.O_RDWR)
    #ioctl(fd, RD_PBUTTONS)
    #red = os.read(fd, 4); # read 4 bytes and store in red var
    #print("red 0x%X"%int.from_bytes(red, 'little'))
    #WR_RED_LEDS
    #WR_GREEN_LEDS
    charminho = threading.Thread(target=charme, args=(fd,))
    charminho.start()

    data = 0x0000007f
    ioctl(fd, WR_GREEN_LEDS)
    retval = os.write(fd, data.to_bytes(4, 'little'))
    
    global width,rows,s,snack
    width = 500
    rows = 20

    win = pygame.display.set_mode((width,width))
    s = Snake((255,0,0),(10,10))
    snack = Cube(random_Snack(rows,s, fd),color=(0,255,0))
    flagInit =  True
    flagStart =  False
    clock = pygame.time.Clock()

    while (flagInit):
        flagStart = startGame(fd)
        quitGame(fd)
        while flagStart:
            drawScore(fd,len(s.body))
            ledRed(fd, len(s.body))
            quitGame(fd)
            flagStart = startGame(fd)
            pygame.time.delay(50) # xms delay
            clock.tick(slowGame(fd)) # x frames per second
            s.move(fd) 
            if s.body[0].pos==snack.pos:
                s.add_cube()
                snack = Cube(random_Snack(rows,s, fd),color=(0,255,0))
                

            
            for x in range(len(s.body)):
                if s.body[x].pos in list(map(lambda z:z.pos,s.body[x+1:])):
                    print("Score",len(s.body))
                    #tk.message_box("You lost!","Play again?")
                    s.reset((10,10))
                    break
            
            redraw_window(win)


if __name__=="__main__":
    main()