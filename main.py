
import sys, pygame, random
from random import *
from game_objects import *
from constants import *
from physics import *
from numpy import random as random_numpy

pygame.init()

class Game:
  def __init__(self):
    self.clock = pygame.time.Clock()
    self.clock_counter = GAME_FPS-1
    self.gameDisplay = pygame.display.set_mode(DISPLAY_SIZE)
    self.game_paused = False
    pygame.mouse.set_visible(self.game_paused)       # turn off mouse pointer
    self.crash = False
    self.player = Player()
    self.ball = Ball()
    self.score =  0
    self.wall = Wall()
    self.lives = STARTING_LIVES
    

  def update(self):

    if Collide(self.ball.sides, self.player.sides):
      ball_player_collision(self.ball, self.player)

    collided_brick_i = collide_list(self.ball, self.wall.brick_list, self.wall.brick_width, self.wall.brick_height)
    if collided_brick_i != -1:
      ball_brick_collision(self.ball, self.wall.brick_list[collided_brick_i], self.wall.brick_width, self.wall.brick_height)
      self.wall.brick_list.pop(collided_brick_i)
    
    if self.ball.update():
      self.lives -= 1
      if self.lives >= 0:
        self.ball.spawn()
      elif self.lives == -1:
        self.game_paused = True



  def main(self):
    update_render_ratio = 3 #How many times the values are updated before rendering
    while(not self.crash):
      self.clock.tick(GAME_FPS*update_render_ratio) #How many times to update the game in a second
      self.clock_counter += 1
      self.clock_counter %= update_render_ratio
      # process key presses
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              sys.exit()
          if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
              self.game_paused = not (self.game_paused)
              pygame.mouse.set_visible(self.game_paused) 
              if self.lives < 0: #If lost, press ESC to restart
                self.ball.spawn() #Spawn ball before assigning lives 
                self.lives = STARTING_LIVES  
      
      if not self.game_paused:
        keys = pygame.key.get_pressed()  #checking pressed keys
        if keys[pygame.K_LEFT]:                        
            self.player.update(-1)  
        if keys[pygame.K_RIGHT]:                  
            self.player.update(1)
        if keys[pygame.K_SPACE]:
            self.ball.start_ball()
            
        self.update()  # Update the game if not paused
      
      if (self.clock_counter == 0):
        self.render(self.game_paused)

  def render(self, game_paused):
    bg_color = ( 0x2F, 0x2F, 0x2F )
    self.gameDisplay.fill(bg_color) #clean display
    self.player.render(self.gameDisplay)
    self.ball.render(self.gameDisplay)
    self.wall.render(self.gameDisplay)

    if game_paused: # If the game is paused, place a grey semi-transparent surface on top
      grey_image = pygame.Surface((GAME_WIDTH,GAME_HEIGHT))
      grey_image.set_alpha(100)
      self.gameDisplay.blit(grey_image, (0,0))
      if self.lives < 0: #If lost, write "Game Over" instead of "Game Paused"
        msg = pygame.font.Font(None,17*DISPLAY_SCALE).render(" Game Over ", True, (0,255,255), (155,155,155))
      else:
        msg = pygame.font.Font(None,17*DISPLAY_SCALE).render(" Game Paused ", True, (0,255,255), (155,155,155))
      msgrect = msg.get_rect()
      msgrect = msgrect.move(GAME_WIDTH / 2 - (msgrect.center[0]), GAME_HEIGHT / 3)
      self.gameDisplay.blit(msg, msgrect)

    pygame.display.flip()
    

class Wall:
  bricks_per_row = 16
  brick_width = GAME_WIDTH // bricks_per_row
  brick_height = brick_width // 2
  color_palette = {
    0: (200,200,200),
    1: (255,0,0),
    2: (0,255,0),
    3: (0,0,255),
    4: (255,255,0),
    5: (0,255,255),
    6: (255,0,255)
  }
  def __init__(self):
    self.brick_list = []
    if  (GAME_WIDTH % Wall.bricks_per_row) > 0:
      print("The amount of bricks don't fit in the screen width")
      exit()
    if ( Wall.brick_width % 2) > 0:
      print("The amount of bricks don't fit in the screen height")
      exit()
    
    self.create_bricks()

  def create_bricks(self):
    temp_matrix =  random_numpy.randint(0,4,(5,Wall.bricks_per_row))

    for i,row in enumerate(temp_matrix):
      for j,e in enumerate(row):
        if e != 0:
          temp_rect = (Wall.brick_width * j, Wall.brick_height * i, e)          
          self.brick_list.append(temp_rect)

  def render(self, gameDisplay):
    for temp_rect in self.brick_list:
      #Draws the squares for each block filled with the given color's value
      pygame.draw.rect(gameDisplay, Wall.color_palette[temp_rect[2]],pygame.Rect(temp_rect[0] , temp_rect[1], Wall.brick_width, Wall.brick_height ) )
      #Draws the square's outline with the value 0 of the palette
      pygame.draw.rect(gameDisplay, Wall.color_palette[0],pygame.Rect(temp_rect[0] , temp_rect[1], Wall.brick_width, Wall.brick_height ) , 1)



if __name__ == "__main__":
  seed(1)
  g = Game()
  g.main()