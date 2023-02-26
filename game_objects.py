import pygame
from constants import *
from random import randint
from physics import *
from numpy import random as random_numpy

class GameObject():
  """
  Basic Game Object with a rectangle, render and move function
  
  """
  def __init__(self, x = 0, y = 0, width = 10, height = 10):
    self._x = x
    self._y = y
    self._width = width
    self._height = height
    self.left = x
    self.top = y
    self.right = self.left + self.width
    self.bottom = self.top + self.height 
    self.sides = (self.left, self.top, self.right, self.bottom)

  @property
  def width(self):
    return self._width
  @width.setter
  def width(self, val):
    self._width = val
    self.update_vars()

  @property
  def height(self):
    return self._height
  @height.setter
  def height(self, val):
    self._height = val
    self.update_vars()

  @property
  def x(self):
    return self._x
  @x.setter
  def x(self, val):
    self._x = val
    self.update_vars()

  @property
  def y(self):
    return self._y
  @y.setter
  def y(self, val):
    self._y = val
    self.update_vars()

  def update_vars(self):
    """
    Updates internal Game Object's attributes
    """
    self.left = self.x
    self.top = self.y
    self.right = self.x + self.width
    self.bottom = self.y + self.height
    self.sides = (self.left, self.top, self.right, self.bottom) 

  def get_center(self):
    """
    Returns a tuple with  (center_x , center_y)
    """
    return self.left + (self.width/2) , self.top + (self.height/2)
    
  def move(self,dx,dy):
    """
    Adds the given distance of x and y to the corresponding attributes
    """
    self.x += dx
    self.y += dy
  
  def replace(self, x, y):
    """
    Assigns the x and y values to the corresponding attributes
    """
    self.x = x
    self.y = y

  
  def load_rect(self, render_rect):
    """
    Loads the coords from a pygame rect
    """
    self.width = render_rect.width
    self.height = render_rect.height
    self.x = render_rect.left
    self.y = render_rect.top

  
  def get_render_rect(self):
    """
    Returns a pygame rect from the GameObject's coords
    """
    return pygame.rect.Rect((self.left,self.top,self.width,self.height))


  def render(self, gameDisplay):
    """
    Renders a black rectangle in the Game Object's position
    """
    pygame.draw.rect(gameDisplay,(0,0,0), self.get_render_rect() )



class Player(GameObject):
  """
  Player Game Object, it can move!
  
  """
  def __init__(self):
    super().__init__() 
    self.width = GAME_WIDTH//10
    self.height = self.width//5
    self.x = GAME_WIDTH//2 - self.width//2
    self.y = (7*GAME_HEIGHT)//8
    self.speedx = INITIAL_PLYR_SPEED
    self.speedy = 0   
  def update(self, action):    
    self.move(self.speedx * action,0)
    new_x_left, new_x_right = self.left, self.right
    if self.left < 0:
      self.move( 0 - new_x_left, 0 )
    if self.right > GAME_WIDTH:
      self.move( (GAME_WIDTH) - new_x_right, 0 )



class Ball(GameObject):
  """
  Ball Game Object, can bounce. Starts without moving.
  """
  def __init__(self):
    super().__init__()
    self.img = pygame.image.load("ball-3.png").convert_alpha()
    img_scale = DISPLAY_SCALE / 4 #The image fits when scale = 4
    temp_rect = self.img.get_rect() #Get the size of the image
    self.img = pygame.transform.scale(self.img, (int(temp_rect.width * img_scale), int(temp_rect.height * img_scale))) #Resize image to the given Display Scale
    self.load_rect( self.img.get_rect() ) # Load the rectangle from the image
    self.spawn()
    self.speed_x = 0
    self.speed_y = 0
    self.MAX_SPEED = 1 + DISPLAY_SCALE//2

  def start_ball(self):
    if (self.speed_x == 0) and (self.speed_y == 0):
      self.speed_x = 0
      self.speed_y = INITIAL_BALL_SPEED

  def spawn(self):
    self.speed_x = 0
    self.speed_y = 0
    spawn_range_x = (GAME_WIDTH//4,(GAME_WIDTH*3)//4)
    spawn_x = randint(*spawn_range_x)
    spawn_y = (GAME_HEIGHT)//3
    self.replace(spawn_x , spawn_y)

  def update(self):
    if self.left < 0 or self.right > GAME_WIDTH:
      self.speed_x = -self.speed_x
    if self.top < 0:
      self.speed_y = -self.speed_y
    self.move(self.speed_x, self.speed_y)
    
    #If the ball is below the screen, return True
    if self.top > GAME_HEIGHT:
      return True
    else:
      return False

  def render(self,gameDisplay):
    gameDisplay.blit(self.img, self.get_render_rect())



# Brick object, not currently in use
class Brick(GameObject):
  COLOR_PALETTE : dict [int, tuple[int, int, int]] = {
    0: (200,200,200),
    1: (255,0,0),
    2: (0,255,0),
    3: (0,0,255),
    4: (255,255,0),
    5: (0,255,255),
    6: (255,0,255)
  }
  BRICK_WIDTH = 40
  BRICK_HEIGHT = 20
  def __init__(self, x, y, width, height, resistance = 1, color_id = 0):
    super().__init__(x, y, width, height)  
    self.resistance = resistance
    self.color = Brick.COLOR_PALETTE[color_id]
    self.active = True
    if color_id == 0:
      self.active = False
  
  def render(self, gameDisplay) -> None:
    if self.active:
      #Draws the squares for each block filled with the given color's value
      pygame.draw.rect(gameDisplay, self.color, self.get_render_rect() )
      #Draws the square's outline with the value 0 of the palette
      pygame.draw.rect(gameDisplay, self.COLOR_PALETTE[0], self.get_render_rect(), 1)


class Wall:
  BRICKS_PER_ROW = 16
  WALL_ROWS = 5
  
  def __init__(self):
    self.brick_list : list[Brick] = []
    if  (GAME_WIDTH % Wall.BRICKS_PER_ROW) > 0:
      print("The amount of bricks don't fit in the screen width")
      exit()
    if ( Brick.BRICK_WIDTH % 2) > 0:
      print("The amount of bricks don't fit in the screen height")
      exit()
    
    self.create_bricks()

  def create_bricks(self) -> None:
    color_id : int
    temp_brick : Brick

    temp_matrix =  random_numpy.randint(0,4,(Wall.WALL_ROWS,Wall.BRICKS_PER_ROW))
    for i,row in enumerate(temp_matrix):
      for j,color_id in enumerate(row):
        temp_brick = Brick(Brick.BRICK_WIDTH * j, Brick.BRICK_HEIGHT * i, Brick.BRICK_WIDTH, Brick.BRICK_HEIGHT, 1, color_id)      
        self.brick_list.append(temp_brick)

  def render(self, gameDisplay) -> None:
    for temp_rect in self.brick_list:
      temp_rect.render(gameDisplay)
