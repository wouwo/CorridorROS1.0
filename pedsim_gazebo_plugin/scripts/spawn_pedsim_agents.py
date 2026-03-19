#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 17:03:34 2019

@author: mahmoud
"""

"""
这部分代码根据pedsim中行人的初始状态,在gazebo中生成对应的行人模型
"""

import rospy
from gazebo_msgs.srv import SpawnModel
from geometry_msgs.msg import *
from rospkg import RosPack
from pedsim_msgs.msg  import AgentStates

# xml file containing a gazebo model to represent agent, currently is represented by a cubic but can be changed
global xml_file

# 遍历pedsim仿真环境中的所有行人，每一个actor即一个行人
def actor_poses_callback(actors):
    for actor in actors.agent_states:
        # 每一个行人向量包含了行人的id、位置以及朝向信息
        actor_id = str( actor.id )
        actor_pose = actor.pose
        rospy.loginfo("Spawning model: actor_id = %s", actor_id)

        model_pose = Pose(Point(x= actor_pose.position.x,
                               y= actor_pose.position.y,
                               z= actor_pose.position.z),
                         Quaternion(actor_pose.orientation.x,
                                    actor_pose.orientation.y,
                                    actor_pose.orientation.z,
                                    actor_pose.orientation.w) )
        
        # 按照上面的id、位置和朝向生成行人模型
        spawn_model(actor_id, xml_string, "", model_pose, "world")
    
    # 生成完毕后退出
    rospy.signal_shutdown("all agents have been spawned !")




if __name__ == '__main__':

    # 在ROS中注册一个节点
    rospy.init_node("spawn_pedsim_agents")

    # 利用RosPack找到pedsim_gazebo_plugin这个包的路径
    rospack1 = RosPack()
    pkg_path = rospack1.get_path('pedsim_gazebo_plugin')
    # 读取路径下的默认行人文件
    default_actor_model_file = pkg_path + "/models/actor_model.sdf"

    actor_model_file = rospy.get_param('~actor_model_file', default_actor_model_file)
    file_xml = open(actor_model_file)
    xml_string = file_xml.read()

    # 等待gazebo中在仿真环境中动态添加模型这个服务上线
    print("Waiting for gazebo services...")
    rospy.wait_for_service("gazebo/spawn_sdf_model")
    spawn_model = rospy.ServiceProxy("gazebo/spawn_sdf_model", SpawnModel)
    print("service: spawn_sdf_model is available ....")

    # 订阅pedsim中的行人信息
    rospy.Subscriber("/pedsim_simulator/simulated_agents", AgentStates, actor_poses_callback)

    rospy.spin()
