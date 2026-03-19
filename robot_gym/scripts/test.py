#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import numpy as np
from scipy.spatial.transform import Rotation as R
from tf2_msgs.msg import TFMessage
from pedsim_msgs.msg import TrackedPersons

class PosePrinter:
    def __init__(self):
        # 订阅 TF 和 行人话题
        self.tf_sub = rospy.Subscriber("/tf", TFMessage, self.tf_callback)
        self.ped_sub = rospy.Subscriber("/persons", TrackedPersons, self.persons_callback)
        
        # 内部状态存储
        self.robot_data = None
        self.ped_data = None
        self.printed = False

    def tf_callback(self, msg):
        if self.printed: return
        for transform in msg.transforms:
            # 严格匹配目标为 base_link
            # 根据您的 fake_odom 脚本逻辑，这里监听 map -> base_link 的变换
            child = transform.child_frame_id.strip('/')
            if child == "base_link":
                x = transform.transform.translation.x
                y = transform.transform.translation.y
                
                # 四元数转 Yaw
                q = transform.transform.rotation
                rot = R.from_quat([q.x, q.y, q.z, q.w])
                yaw = rot.as_euler('zyx')[0]
                
                self.robot_data = [x, y, yaw]
                self.check_and_print()

    def persons_callback(self, msg):
        if self.printed: return
        peds = []
        for person in msg.tracks:
            # 获取每个行人的 x, y
            peds.append([person.pose.pose.position.x, person.pose.pose.position.y])
        
        if peds:
            self.ped_data = peds
            self.check_and_print()

    def check_and_print(self):
        # 只有当机器人位姿和行人数据都获取到时才打印一次
        if self.robot_data is not None and self.ped_data is not None and not self.printed:
            # 严格按照 [] 格式输出
            print(f"[{self.robot_data}, {self.ped_data}]")
            self.printed = True
            rospy.signal_shutdown("Done printing once.")

if __name__ == '__main__':
    try:
        rospy.init_node('pose_one_shot_printer', anonymous=True)
        pp = PosePrinter()
        rospy.spin()
    except Exception:
        pass