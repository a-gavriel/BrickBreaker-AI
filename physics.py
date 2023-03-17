from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from game_objects import GameObject, Ball, Brick
from constants import *

sign = lambda x: (1, -1)[x < 0]




def Collide(GameObjectA_sides, GameObjectB_sides):
  """
  Collide(GameObjectA, GameObjectB)

  Determines if GameObjectA collides with GameObjectB.


  Parameters
  ----------
  GameObjectA : GameObject
      First rectangle
  GameObjectB : GameObject
      Second rectangle

  Returns
  -------
  Bool
      If both rectangles collide.

  """
  if (GameObjectA_sides[0] < GameObjectB_sides[2]) and (GameObjectA_sides[2] > GameObjectB_sides[0]) and \
      (GameObjectA_sides[1] < GameObjectB_sides[3]) and (GameObjectA_sides[3] > GameObjectB_sides[1]):
    return True
  else:
    return False


def ball_player_collision(ball, player):
  """
  Determines if the ball collides with the player and updates the speed_x of the ball accordingly depending on the collision offset
  """
  ball.speed_y = - abs(ball.speed_y)
  temp_rect = ( player.left - ball.width, player.top, \
      player.width + 2* ball.width, player.height )
  offset = ball.get_center()[0] - (temp_rect[0] + temp_rect[2]/2)
  offset_normalized = offset / (temp_rect[2]/2.5)
  ball.speed_x = (offset_normalized * ball.MAX_SPEED)


def get_collided_brick(GameObjectA : GameObject, brick_list : list[Brick]) -> int:
  current_brick : 'Brick'
  for i, current_brick in enumerate(brick_list):
    if current_brick.active and Collide(GameObjectA.sides, current_brick.sides):
      return i
  return -1


def ball_brick_collision(ball : Ball, brick : Brick):
  if ball.speed_x == 0:
    ball.speed_y = -ball.speed_y
  else:
    if abs(ball.bottom - brick.top) < COLLISION_TOL or \
      abs(ball.top - (brick.bottom)) < COLLISION_TOL:
      ball.speed_y = -ball.speed_y
    elif abs(ball.left - (brick.right)) < COLLISION_TOL or \
      abs(ball.right - brick.left) < COLLISION_TOL:
      ball.speed_x = -ball.speed_x
    
  