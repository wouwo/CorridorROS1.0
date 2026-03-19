#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
import rospy
from geometry_msgs.msg import Twist

TOPIC_NAME = '/cmd_vel' 

# 速度参数
LIN_STEP = 0.02  # 每次累加的线速度 (前后)
ANG_STEP = 0.02  # 每次累加的角速度 (左右)
MAX_SPEED = 2.0  # 最大速度限制
RATE_HZ = 10     # 发送频率 (10Hz = 0.1秒一次)
# ===========================================

class RobotController:
    def __init__(self):
        # 初始化 ROS 发布者
        self.pub = rospy.Publisher(TOPIC_NAME, Twist, queue_size=10)
        
        # 速度状态变量
        self.linear_x = 0.0
        self.angular_z = 0.0
        
        # 按键状态标志 (True 表示按键被按住)
        self.keys = {
            'w': False,
            'x': False,
            'a': False,
            'd': False
        }

    def handle_event(self, event):
        """处理键盘按下和松开事件"""
        key_name = pygame.key.name(event.key)
        
        if event.type == pygame.KEYDOWN:
            if key_name in self.keys:
                self.keys[key_name] = True
            elif key_name == 's': # S 键特殊处理：急刹车
                self.stop()

        elif event.type == pygame.KEYUP:
            if key_name in self.keys:
                self.keys[key_name] = False

    def update_speed(self):
        """根据按键状态更新速度 (核心累加逻辑)"""
        # 线速度控制
        if self.keys['w']:
            self.linear_x += LIN_STEP
        if self.keys['x']:
            self.linear_x -= LIN_STEP
            
        # 角速度控制
        if self.keys['a']:
            self.angular_z += ANG_STEP
        if self.keys['d']:
            self.angular_z -= ANG_STEP

        # 限制最大速度
        self.linear_x = max(min(self.linear_x, MAX_SPEED), -MAX_SPEED)
        self.angular_z = max(min(self.angular_z, MAX_SPEED), -MAX_SPEED)

    def stop(self):
        """急刹车"""
        self.linear_x = 0.0
        self.angular_z = 0.0
        print(">> 急刹车触发！速度归零。")

    def publish(self):
        """发布速度指令"""
        twist = Twist()
        twist.linear.x = self.linear_x
        twist.angular.z = self.angular_z
        self.pub.publish(twist)
        return twist

def draw_ui(screen, font, twist_msg):
    """绘制简单的白色界面"""
    screen.fill((255, 255, 255)) # 白底
    
    # 绘制提示文字
    texts = [
        "ROS Keyboard Teleop",
        "-------------------",
        "W: Forward (+)",
        "X: Backward (-)",
        "A: Turn Left (+)",
        "D: Turn Right (-)",
        "S: Emergency Stop",
        "-------------------",
        "Linear X : {:.2f}".format(twist_msg.linear.x),
        "Angular Z: {:.2f}".format(twist_msg.angular.z)
    ]
    
    y = 20
    for text in texts:
        color = (0, 0, 0) # 黑色文字
        # 如果是速度显示，换个颜色
        if "Linear" in text or "Angular" in text:
            color = (255, 0, 0) # 红色
            
        surface = font.render(text, True, color)
        screen.blit(surface, (20, y))
        y += 30
        
    pygame.display.flip()

def main():
    rospy.init_node('simple_pygame_teleop', anonymous=True)
    
    # 初始化 Pygame
    pygame.init()
    screen = pygame.display.set_mode((300, 350))
    pygame.display.set_caption("ROS Controller")
    font = pygame.font.SysFont('Arial', 20)
    
    controller = RobotController()
    clock = pygame.time.Clock()

    while not rospy.is_shutdown():
        # 1. 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                controller.handle_event(event)
        
        # 2. 更新速度
        controller.update_speed()
        
        # 3. 发布 ROS 消息
        current_twist = controller.publish()
        
        # 4. 刷新界面
        draw_ui(screen, font, current_twist)
        
        # 5. 控制循环频率
        clock.tick(RATE_HZ)

if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
    finally:
        pygame.quit()