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
  def __init__(self, human=False):
    super().__init__()

    self.done = False
    self.seed()
    self.reward = 0
    self.action_space : int = 3  # Nothing / Left / Right
    self.state_space : int = 254   # 254

    self.total, self.maximum = 0, 0
    self.human = human
    

    self.clock = pygame.time.Clock()
    self.clock_counter = GAME_FPS-1
    self.gameDisplay = pygame.display.set_mode(DISPLAY_SIZE)
    self.game_paused : bool = False
    pygame.mouse.set_visible(self.game_paused)       # turn off mouse pointer
    self.crash : bool = False
    self.player = Player()
    self.ball = Ball(human)
    self.score : int = 0
    self.wall = Wall()
    self.lives : int = STARTING_LIVES
    self.update_render_ratio = 3 #How many times the values are updated before rendering
    
    # distance between ball and player
    
    self.dist : int = int(self.player.get_center()[0] -  self.ball.get_center()[0])
    self.prev_dist : int = self.dist
    self.collision_dist : int = 0

    if human:
      self.main()

  def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

  def measure_distance(self):
    self.prev_dist = self.dist
    px, _ = self.player.get_center()
    bx, _ = self.ball.get_center()
    return int(px-bx)

  def update(self):
    self.reward = 0
    reward_given = False
    self.dist = self.measure_distance()

    if Collide(self.ball.sides, self.player.sides):
      ball_player_collision(self.ball, self.player)
      #self.score += 10
      self.collision_dist = self.dist
      self.reward += 10
      reward_given = True

    collided_brick_i = get_collided_brick(self.ball, self.wall.brick_list)
    if collided_brick_i != -1:
      ball_brick_collision(self.ball, self.wall.brick_list[collided_brick_i])
      self.wall.brick_list[collided_brick_i].active = False
      self.score += 50
      self.reward += 50
      reward_given = True
    
    if self.ball.update():
      self.lives -= 1
      if self.lives >= 0:
        self.ball.spawn()
      elif self.lives <= -1:
        self.reward = -100
        self.done = True
        reward_given = True
        if self.human:
          self.game_paused = True
          self.reset()

          

    if not reward_given:
      ball_x = self.ball.get_center()[0]
      if self.player.left <= ball_x <= self.player.right:
        self.reward = 2
      elif abs(self.dist) <= abs(self.prev_dist):
        self.reward = 1
      else:
        self.reward = -1

  def reset(self):  
    self.ball.spawn() #Spawn ball before assigning lives 
    self.lives = STARTING_LIVES  
    self.player = Player()
    self.wall = Wall()
    self.score = 0
    self.reward = 0
    self.total = 0
    self.done = False
    state = self.get_state()

    return state


  def get_state(self) -> list[int]:
    state : list[int] = []
    temp_center : tuple[float, float]

    # getting active wall state
    for current_brick in self.wall.brick_list:
      state.append(int(current_brick.active))
      temp_center = current_brick.get_center()
      state.append(int(temp_center[0]))
      state.append(int(temp_center[1]))
    
    # getting ball
    temp_center = self.ball.get_center() 
    state.append(int(temp_center[0]*10))
    state.append(int(temp_center[1]*10))
    state.append(int(self.ball.speed_x*10))
    state.append(int(self.ball.speed_y*10))

    # getting player
    state.append(self.player.left)
    state.append(self.player.right)
    state.append(int(self.player.top*10))
    #state.append(self.player.bottom)
    temp_center = self.player.get_center() 
    state.append(int(temp_center[0]*10))
    state.append(int(temp_center[1]*10))

    self.measure_distance()
    state.append(int(self.dist*10))
    state.append(int(self.collision_dist*10))

    state.append(GAME_WIDTH*10)
    state.append(GAME_HEIGHT*10)
    state.append(self.score*10)

    return state

  def step(self, action):
    if action == 0:
      pass
    if action == 1:
      self.player.update(-1)
    if action == 2:
      self.player.update(1)
    self.game_step()
    state = self.get_state()
    return state, self.reward, self.done, {}


  def game_step(self):
    #self.clock.tick(GAME_FPS*self.update_render_ratio*3) #How many times to update the game in a second

    self.clock_counter += 1
    self.clock_counter %= self.update_render_ratio

    self.update()  # Update the game if not paused
    if (self.clock_counter == 0):
        self.render(self.game_paused)


  def main(self):
    print("Playing game as human!")
    while(not self.crash):
      self.clock.tick(GAME_FPS*self.update_render_ratio) #How many times to update the game in a second
      self.clock_counter += 1
      self.clock_counter %= self.update_render_ratio
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
                self.reset()
      
      if not self.game_paused:
        keys = pygame.key.get_pressed()  #checking pressed keys
        if keys[pygame.K_UP]:                        
            print(len(self.get_state()))
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
  g = Game(human=True)

  