import board
import displayio
from board import DISPLAY
import adafruit_imageload
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from digitalio import DigitalInOut, Direction, Pull

class Btn:
    def __init__(self,pin,time,short_cb,long_cb):
        btn = DigitalInOut(board.BTNB)
        btn.direction = Direction.INPUT
        btn.pull = Pull.UP
        self.btn = btn
        self.status = 'ready'
        self.keydowntime=0
        self.t = time
        self.short_cb=short_cb
        self.long_cb=long_cb
        
    def on_short_click(self):
        print('on_short_click')
        self.short_cb()
    def on_long_click(self):
        print('on_long_click')
        self.long_cb()
        
    def loop(self):
        if self.status=='ready' and self.btn.value == 0:
            self.status='keydown'
        if self.status=='keydown':
            if self.btn.value == 0:
                print('keydowntime++')
                self.keydowntime+=1
            if self.btn.value == 1:
                self.status='keyup'
        if self.status=='keyup':
            print(self.keydowntime)
            if self.keydowntime > self.t :
                self.on_long_click()
            else:
                self.on_short_click()
            self.keydowntime = 0
            self.status='ready'

group = displayio.Group(scale=2, x=0, y=0)

DISPLAY.show(group)

color_bitmap = displayio.Bitmap(80, 64, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000

bg = displayio.TileGrid(color_bitmap,pixel_shader=color_palette,x=0, y=0)
group.append(bg)

font = bitmap_font.load_font("fonts/Arialbd_small.bdf")
text = label.Label(font, text=str(""), color=0xFFFFFF)
text.anchor_point = (0, 0)
text.anchored_position = (10, 10)

group.append(text)

text_alert = label.Label(font, text=str("Skateboard\n      Kid"), color=0xFFFFFF)
text_alert.anchor_point = (0, 0)
text_alert.anchored_position = (4, 20)

group.append(text_alert)

def checkCollision(a, b):
    a_left = a.x
    a_right = a.x + a.w
    a_top = a.y
    a_bottom = a.y + a.h
    b_left = b.x
    b_right = b.x + b.w
    b_top = b.y
    b_bottom = b.y + b.h
    return a_right > b_left and a_left < b_right and a_bottom > b_top and a_top < b_bottom

def gameover():
    if hero.gamestatus=='playing':
        text_alert.text="     Game\n     OVER"
        hero.gamestatus='gameover'

class Sprite:
    def __init__(self,w,h,x,y,speed,img,transparent=False,transparentColor=0):
        sprite_sheet, palette = adafruit_imageload.load(img,bitmap=displayio.Bitmap,palette=displayio.Palette)
        if transparent:
            palette.make_transparent(transparentColor)
        sheet = displayio.TileGrid(sprite_sheet, pixel_shader=palette,width = 1,height = 1,tile_width = w,tile_height = h)
        sheet[0] = 0
        sheet.x = x
        sheet.y = y
        self.sheet=sheet
        self.w=w
        self.h=h
        self.x=x
        self.y=y
        self.speed=speed
        group.append(self.sheet)
    def draw(self):       
        self.sheet.x=self.x
        self.sheet.y=self.y

class Hero(Sprite):
    def __init__(self):
        Sprite.__init__(self,22,30,2,64-30,2,'images/hero.bmp',True,0)
        self.current=0
        self.toy=self.y
        self.status='walk'
        
    def pause(self):
        pass
        
    def walk(self,time):
        if self.status=='walk':
            if time % 200 ==0:
                self.current+=1
                if self.current == 2:
                    self.current = 0
            self.sheet[0]=self.current
    def jump(self):
        if self.status=='walk':
           self.toy=-15
           self.status='jump'
        
    def update_loenemyion(self,time):
        if time % 12 ==0:
            if self.status=='jump':
                self.y-=self.speed
                if self.y<=self.toy:
                    self.y=self.toy
                    self.status='down'
            if self.status=='down':
                self.y+=self.speed
                if self.y>=64-self.h:
                    self.y=64-self.h
                    self.status='walk'
        
    def update(self,time):
        self.walk(time)
        self.update_loenemyion(time)

class Enemy(Sprite):
    def __init__(self):
        Sprite.__init__(self,4,13,150,64-13,1,'images/bo.bmp',True,0)
        self.current=0
        self.time=0
        self.score=0
    def update(self,time):
        if time % 10 ==0:
            self.x-=self.speed
        if self.x<=-1*self.w:
            self.x=150
            self.score+=1
            text.text = str(self.score)


time = 0
hero=Hero()
hero.gamestatus='ready'

enemy=Enemy()

def onclick():
    print('\n\n')
    print(hero.gamestatus)
    if hero.gamestatus=='ready':
        hero.gamestatus='playing'
        text_alert.text=""
    elif hero.gamestatus=='playing':
        hero.jump()
    elif hero.gamestatus=='gameover':
        enemy.x=300
        enemy.score=0
        text.text = str(0)
        enemy.draw()
        hero.status='down'
        hero.gamestatus='playing'
        text_alert.text=""
        
btn = Btn(board.BTNB,1000,onclick,hero.pause)

while True:
    btn.loop()
    if hero.gamestatus=='gameover':
        btn.keydowntime=0
    elif hero.gamestatus=='playing':
        time+=1
        hero.update(time)
        enemy.update(time)
        hero.draw()
        enemy.draw()
        if(checkCollision(hero, enemy)):
            gameover()