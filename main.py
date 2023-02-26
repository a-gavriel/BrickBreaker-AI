import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils import seeding

import sys, pygame, random
from random import *
from game_objects import *
from constants import *
from physics import *


pygame.init()

class Game(gym.Env):
  def __init__(self, human=False, env_info={'state_space':None}):
    super().__init__()

    self.done = False
    self.seed()
    self.reward = 0
    self.action_space = 4
    self.state_space = 12

    self.total, self.maximum = 0, 0
    self.human = human
    self.env_info = env_info

    self.clock = pygame.time.Clock()
    self.clock_counter = GAME_FPS-1
    self.gameDisplay = pygame.display.set_mode(DISPLAY_SIZE)
    self.game_paused : bool = False
    pygame.mouse.set_visible(self.game_paused)       # turn off mouse pointer
    self.crash : bool = False
    self.player = Player()
    self.ball = Ball()
    self.score : int = 0
    self.wall = Wall()
    self.lives : int = STARTING_LIVES
    
    # distance between ball and player
    self.prev_dist : int
    self.dist : int = self.player.get_center()[0] - self.ball.get_center()[0]

  def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

  def measure_distance(self):
    self.prev_dist = self.dist
    self.dist = self.player.get_center[0] - self.ball.get_center[0]

  def update(self):

    if Collide(self.ball.sides, self.player.sides):
      ball_player_collision(self.ball, self.player)

    collided_brick_i = get_collided_brick(self.ball, self.wall.brick_list)
    if collided_brick_i != -1:
      ball_brick_collision(self.ball, self.wall.brick_list[collided_brick_i])
      self.wall.brick_list[collided_brick_i].active = False
      self.score += 10
    
    if self.ball.update():
      self.lives -= 1
      if self.lives >= 0:
        self.ball.spawn()
      elif self.lives == -1:
        self.game_paused = True

  def reset_game(self):  
    self.ball.spawn() #Spawn ball before assigning lives 
    self.lives = STARTING_LIVES  
    self.player = Player()
    self.wall = Wall()
    self.score = 0
    self.reward = 0
    self.done = False
    state = self.get_state()

    return state


  def get_state(self):
    wall_state = []
    

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
                print("Score:", self.score)
                self.reset_game()
      
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
    


if __name__ == "__main__":
  seed(1)
  g = Game()
  g.main()