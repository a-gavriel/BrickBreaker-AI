
import sys, pygame, random
from random import *
gamespeed = 1

size = width, height = 640, 480

sign = lambda x: (1, -1)[x < 0]

class GameObject():
  def __init__(self,game):
    self.width = 10
    self.height = 10
    self.xpos = width // 2
    self.ypos = height // 10    
    self.rect = pygame.rect.Rect(( self.xpos - self.width//2 , self.ypos - self.height//2 , self.width, self.height))   
  def left(self):
    return self.xpos - self.width//2
  def right(self):
    return self.xpos + self.width//2
  def top(self):
    return self.ypos - self.height//2
  def bottom(self):
    return self.ypos + self.height//2
  def gxpos(self):
    return self.xpos
  def gypos(self):
    return self.ypos
  def grect(self):
    return pygame.rect.Rect(( self.xpos - self.width//2 , self.ypos - self.height//2 , self.width, self.height))   
  def update(self):
    None
  def render(self, game):
    newrect = pygame.rect.Rect(( self.xpos - self.width//2 , self.ypos - self.height//2 , self.width, self.height))   
    pygame.draw.rect(game.gameDisplay,(0,0,0),newrect )



# TODO: verify speed
class Player(GameObject):
  def __init__(self,game):
    super().__init__(game)   
    self.xspeed = 20 
    self.xpos = 200
    self.width = 100    
    self.ypos = 450
  def update(self,direction):
    if direction == 1:
      if self.left() > 0:
        self.xpos-= self.xspeed
    if direction == 2:
      if self.right() < width:
        self.xpos += self.xspeed
    self.rect = pygame.rect.Rect(( self.xpos - self.width//2 , self.ypos - self.height//2 , self.width, self.height))  

# TODO: verify speed
class Ball(GameObject):
  def __init__(self,game):
    super().__init__(game)
    self.basespeed = 6
    self.xspeed = 3
    self.yspeed = 3
    self.width = 7
    self.height = 7    
    self.xpos = randint(100,500)
    self.ypos = height//3
    self.pong = pygame.mixer.Sound('Blip_1-Surround-147.wav')
    self.pong.set_volume(10)    
  def update(self,game, player):
    self.rect = pygame.rect.Rect(( self.xpos - self.width//2 , self.ypos - self.height//2 , self.width, self.height))  
    self.xpos += (self.xspeed )
    self.ypos += (self.yspeed )
    if (self.xpos <= 0):
      self.xspeed *= -1
    if (self.xpos >= width):
      self.xspeed *= -1
    if (self.ypos <= 0):
      self.yspeed *= -1
    if (self.ypos > height):
      game.crash = True
    col_result = colission(self,player)
    #print(self.xpos, self.ypos)
    if col_result[0]:      
      self.yspeed *= -1
      print(col_result[1])

# TODO: verify offset
## shoueld call RecA = ball for correct offset
def colission(RectA, RectB):
  playerx = RectB.gxpos()    
  if (RectA.left() <= RectB.right() and RectA.right() >= RectB.left() and
     RectA.top() <= RectB.bottom() and RectA.bottom() >= RectB.top() ):
     RectA.pong.play(0)
     offset = RectA.xpos - playerx #unknown error if replaced with RectB.xpos or RectB.gxpos()
     offsetF = offset / RectB.width
     side = sign(offset)
     offsetF = abs(offsetF)     
     if offsetF > 0.7:
       offset = side * 7
     elif offsetF > 0.3:
       offset = side * 6
     else:
       offset = side * 5
     return (1,offset)
  else:
    return (0,0) 
  


class Game:
  def __init__(self,game_width,game_height):
    self.crash = False
    self.player = Player(self)
    self.ball = Ball(self)
    self.score =  0
    self.game_height = game_height
    self.game_width = game_width
    self.gameDisplay = pygame.display.set_mode((game_width,game_height+60))
    self.wall = Wall()
    self.wall.build_wall(width) #TODO: goes here?
  def update(self):
    self.ball.update(self, self.player)
    self.wall.update(self.ball,self)    
  def render(self):
    self.gameDisplay.fill((0,255,255))
    self.player.render(self)
    self.ball.render(self)
    self.wall.render(self)
    pygame.display.flip()
    



class Brick(GameObject):
  def __init__(self):
    super().__init__(self)  
    self.xpos = 0
    self.ypos = 0    
    self.width = 52
    self.height = 21
    


class Wall:
  def __init__(self):

    self.bricks = []
    self.colors = []
    self.brick = pygame.image.load("brick.png").convert()
    self.brickrect = self.brick.get_rect()
  def build_wall(self, width):        
    Wxpos = 0
    Wypos = 60
    adj = 0
    for i in range (0, 14):        
      newbrick = Brick()
      newcolor = (randint(0,255),randint(0,255),randint(0,255))
      if Wxpos > width:
        if adj == 0:
          adj = newbrick.width // 2
        else:
          adj = 0
        Wxpos = -adj
        Wypos += newbrick.height      
      self.bricks.append(newbrick.grect())
      self.colors.append(newcolor)
      self.bricks[i] = self.bricks[i].move(Wxpos, Wypos)
      Wxpos = Wxpos + newbrick.width
  def update(self,ball, game):
    index = ball.rect.collidelist(self.bricks)       
    if index != -1: 
      if ball.rect.center[0] > self.bricks[index].right or \
        ball.rect.center[0] < self.bricks[index].left:
        ball.xspeed = -ball.xspeed
      else:
        ball.yspeed = -(ball.yspeed)
      ball.pong.play(0)              
      self.bricks[index:index + 1] = []
      self.colors[index:index + 1] = []
      game.score += 10
  def render(self,game):
    for i in range(len(self.bricks)):
    	game.gameDisplay.blit(self.brick, self.bricks[i])    
    	#pygame.Surface.blit(self.image, game.gameDisplay, self.bricks[i])
      #pygame.draw.rect(game.gameDisplay,self.colors[i],self.bricks[i])
      


def run():
  pygame.init()            
  counter_games = 0
  #create agent
  max_iterations = 10 #TODO: move to top
  clock = pygame.time.Clock()
  while counter_games < max_iterations:
    game = Game(640,480)
    #initializegame
    #render game
    while(not game.crash):
      #agent stuff
      

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          sys.exit()

      final_move = 0
      pressed = pygame.key.get_pressed()
      if pressed[pygame.K_LEFT]:
        final_move = 1
      if pressed[pygame.K_RIGHT]:
        final_move = 2
      #final_move = randint(1,2) #TODO: replace with agent stuff
      game.player.update(final_move)     
      game.update()
      game.render()
      #print(game.ball.ypos)
      clock.tick(60)
      #render game
    print("game finished!")
    counter_games += 1

run()
