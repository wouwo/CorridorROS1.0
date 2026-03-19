#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import actionlib
import math
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from nav_msgs.msg import Odometry

class NavigationEvaluator:
    def __init__(self):
        rospy.init_node('navigation_evaluator', anonymous=True)
        
        # 按照论文，每次试验(trial)需要测试25个目标点 
        # 这里仅作示例，请根据你的 Gazebo 地图 (如 lobby_45ped.world) 替换这 25 个实际坐标
        self.goals = [
            (2.0, 2.0), (5.0, 1.0), (8.0, 3.0), (10.0, 2.0), (12.0, 5.0),
            (10.0, 8.0), (5.0, 6.0), (0.0, 8.0), (3.0, 5.0), (5.0, 0.0),
            (3.0, 5.0), (5.0, 8.0), (8.0, 5.0), (12.0, 2.0),
            (15.0, 2.0), (12.0, 6.0), (8.0, 8.0), (3.0, 10.0), (2.0, 10.0),
            (8.0, 8.0), (10.0, 3.0), (8.0, 2.0), (4.0, 8.0)
        ]
        
        # 统计指标 (对应论文中的四大指标) 
        self.total_goals = len(self.goals)
        self.success_count = 0
        self.total_time = 0.0
        self.total_distance = 0.0
        
        # 内部状态
        self.is_navigating = False
        self.current_distance = 0.0
        self.last_pose = None
        
        # 订阅里程计以计算实际行驶的路径长度 (Average length) [cite: 505]
        rospy.Subscriber('/odom', Odometry, self.odom_callback)
        
        # 连接 move_base 动作服务器
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        rospy.loginfo("正在等待 move_base 服务器...")
        self.client.wait_for_server()
        rospy.loginfo("成功连接到 move_base!")

    def odom_callback(self, msg):
        """实时累加机器人行驶的欧式距离"""
        if not self.is_navigating:
            self.last_pose = msg.pose.pose
            return
            
        current_pose = msg.pose.pose
        if self.last_pose is not None:
            dx = current_pose.position.x - self.last_pose.position.x
            dy = current_pose.position.y - self.last_pose.position.y
            self.current_distance += math.sqrt(dx**2 + dy**2)
            
        self.last_pose = current_pose

    def send_goal(self, x, y, goal_index):
        """发送目标点并记录时间和距离"""
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.orientation.w = 1.0 
        
        rospy.loginfo("----------------------------------------")
        rospy.loginfo("正在前往目标点 %d/%d: [X: %.2f, Y: %.2f]", goal_index, self.total_goals, x, y)
        
        # 初始化测量
        self.current_distance = 0.0
        self.is_navigating = True
        start_time = rospy.Time.now().to_sec()
        
        self.client.send_goal(goal)
        
        # 等待结果，设置超时时间防止彻底卡死
        wait_result = self.client.wait_for_result(rospy.Duration(120.0))
        end_time = rospy.Time.now().to_sec()
        self.is_navigating = False
        
        duration = end_time - start_time
        
        if not wait_result:
            rospy.logwarn("目标点超时！机器人可能陷入死锁或发生碰撞。")
            self.client.cancel_goal()
            return False
            
        state = self.client.get_state()
        if state == actionlib.GoalStatus.SUCCEEDED:
            rospy.loginfo("成功到达目标点！耗时: %.2f 秒, 路径长度: %.2f 米", duration, self.current_distance)
            self.success_count += 1
            self.total_time += duration
            self.total_distance += self.current_distance
            return True
        else:
            rospy.logwarn("到达目标点失败，状态码: %d", state)
            return False

    def run_trial(self):
        """运行一次完整的试验 (包含 25 个目标点)"""
        rospy.sleep(2.0) # 等待仿真环境稳定
        for i, target in enumerate(self.goals):
            self.send_goal(target[0], target[1], i + 1)
            rospy.sleep(1.0) # 到达后短暂休眠，等待动态行人移动
            
        self.print_report()

    def print_report(self):
        """输出论文格式的评估报告"""
        rospy.loginfo("============= 最终测试报告 =============")
        rospy.loginfo("算法评估完成，共测试 %d 个目标点", self.total_goals)
        
        success_rate = (float(self.success_count) / self.total_goals)
        rospy.loginfo("1. Success rate (成功率): %.2f (%d/%d)", success_rate, self.success_count, self.total_goals)
        
        if self.success_count > 0:
            avg_time = self.total_time / self.success_count
            avg_length = self.total_distance / self.success_count
            avg_speed = self.total_distance / self.total_time
            rospy.loginfo("2. Average time (平均时间): %.2f s", avg_time)
            rospy.loginfo("3. Average length (平均路径长度): %.2f m", avg_length)
            rospy.loginfo("4. Average speed (平均速度): %.2f m/s", avg_speed)
        else:
            rospy.logwarn("所有目标点均失败，无法计算平均时间、长度和速度。")
        rospy.loginfo("========================================")

if __name__ == '__main__':
    try:
        evaluator = NavigationEvaluator()
        evaluator.run_trial()
    except rospy.ROSInterruptException:
        pass