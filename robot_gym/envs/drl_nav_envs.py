import numpy as np
import numpy.matlib
import random
import math
from scipy.optimize import linprog, minimize
import threading

#import itertools 
import rospy
import gym # https://github.com/openai/gym/blob/master/gym/core.py
from gym.utils import seeding
from gym import spaces
from std_msgs.msg import Float64, Empty, Bool
from gazebo_msgs.msg import ModelStates, ModelState
from gazebo_msgs.srv import GetModelState, SetModelState
from nav_msgs.msg import Odometry, OccupancyGrid, Path
from geometry_msgs.msg import Pose, Twist, Point, PoseStamped, PoseWithCovarianceStamped
import time
from actionlib_msgs.msg import GoalStatusArray
from pedsim_msgs.msg  import TrackedPersons, TrackedPerson

# 基于pedsim仿真环境编写强化学习的gym函数接口
class PedsimRLEnv(gym.Env):
    def __init__(self):

        rospy.logdebug

        # 机器人相关参数
        self.ROBOT_RADIUS = 0.3     # 机器人半径


        # 定义动作空间



    def step(self, action):
        """
        Gives env an action to enter the next state,
        obs, reward, done, info = env.step(action)
        """
        pass

    def reset(self):
        pass


    # 获取pedsim仿真环境中的相关信息，比如机器人位置信息、行人位置信息、障碍物信息、目标点信息、激光信息等
    def _get_observation(self):
        pass

    def _take_action(self, action):
        """
        Set linear and angular speed for robot and execute.
        Args:
        action: 2-d numpy array.
        """
