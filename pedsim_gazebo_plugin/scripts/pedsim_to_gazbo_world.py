#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pedsim XML to Gazebo World Converter (Python 3 Version)
支持: Line, Circle, Rectangle 障碍物
"""

import math
import os
import xml.etree.ElementTree as ET 
from rospkg import RosPack

# 全局文件句柄
gzb_world = None

def generate_pose_line(x1, y1, x2, y2):
    """计算线性障碍物的位姿 (中心点 + 旋转角)"""
    if x2 - x1 == 0:
        yaw = 1.570796 # 90 degrees
    else:
        yaw = math.atan((y2-y1)/(x2-x1))
    
    # z=1.4 代表墙高2.8的一半
    print("\t  <pose frame=''>{} {} 1.4 0 0 {}</pose>".format(
        (x2+x1)/2, (y2+y1)/2, yaw), file=gzb_world)

def generate_size_line(x1, y1, x2, y2):
    """计算线性障碍物的长度"""
    l = math.sqrt(pow(y2-y1, 2) + pow(x2-x1, 2))
    print("\t     <size> {} 0.2 2.8 </size>".format(l), file=gzb_world)

# ---------------------------------------------------------
# 1. 生成线性障碍物 (Line -> Box)
# ---------------------------------------------------------
def generate_line_obstacle(x1, y1, x2, y2, idx):
    print(f'''
    <model name='wall_line_{idx}'>
      <static>1</static>
      <link name='link'>
    ''', file=gzb_world)
    
    generate_pose_line(x1, y1, x2, y2)
    
    # Collision
    print('''
        <collision name='collision'>
          <geometry>
            <box>''', file=gzb_world)
    generate_size_line(x1, y1, x2, y2)
    print('''
            </box>
          </geometry>
        </collision>
    ''', file=gzb_world)
    
    # Visual
    print('''
        <visual name='visual'>
          <cast_shadows>0</cast_shadows>
          <geometry>
            <box>''', file=gzb_world)
    generate_size_line(x1, y1, x2, y2)
    print('''
            </box>
          </geometry>
          <material>
            <script>
              <uri>model://grey_wall/materials/scripts</uri>
              <uri>model://grey_wall/materials/textures</uri>
              <name>vrc/grey_wall</name>
            </script>
          </material>
        </visual>
      </link>
    </model>
    ''', file=gzb_world)

# ---------------------------------------------------------
# 2. 生成圆形障碍物 (Circle -> Cylinder)
# ---------------------------------------------------------
def generate_circle_obstacle(x, y, radius, idx):
    # Gazebo Cylinder 需要 radius 和 length
    # 我们假设高度统一为 2.8
    print(f'''
    <model name='wall_circle_{idx}'>
      <static>1</static>
      <link name='link'>
        <pose frame=''>{x} {y} 1.4 0 0 0</pose>
        
        <collision name='collision'>
          <geometry>
            <cylinder>
              <radius>{radius}</radius>
              <length>2.8</length>
            </cylinder>
          </geometry>
        </collision>

        <visual name='visual'>
          <cast_shadows>0</cast_shadows>
          <geometry>
            <cylinder>
              <radius>{radius}</radius>
              <length>2.8</length>
            </cylinder>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Grey</name>
            </script>
          </material>
        </visual>
      </link>
    </model>
    ''', file=gzb_world)

# ---------------------------------------------------------
# 3. 生成矩形障碍物 (Rectangle -> Box)
# ---------------------------------------------------------
def generate_rectangle_obstacle(x, y, hx, hy, theta, idx):
    # Pedsim 给出的是 xHalfLength (半长)，Gazebo 需要全长 (Size)
    # 所以需要乘以 2
    size_x = hx * 2
    size_y = hy * 2
    
    print(f'''
    <model name='wall_rect_{idx}'>
      <static>1</static>
      <link name='link'>
        <pose frame=''>{x} {y} 1.4 0 0 {theta}</pose>
        
        <collision name='collision'>
          <geometry>
            <box>
              <size>{size_x} {size_y} 2.8</size>
            </box>
          </geometry>
        </collision>

        <visual name='visual'>
          <cast_shadows>0</cast_shadows>
          <geometry>
            <box>
              <size>{size_x} {size_y} 2.8</size>
            </box>
          </geometry>
          <material>
            <script>
              <uri>model://grey_wall/materials/scripts</uri>
              <uri>model://grey_wall/materials/textures</uri>
              <name>vrc/grey_wall</name>
            </script>
          </material>
        </visual>
      </link>
    </model>
    ''', file=gzb_world)

# ---------------------------------------------------------
# XML 解析逻辑
# ---------------------------------------------------------
def parseXML(xmlfile): 
    try:
        tree = ET.parse(xmlfile) 
        root = tree.getroot() 
        idx = 0
        print(f"正在解析: {xmlfile}")

        for item in root:
            if item.tag == 'obstacle':
                idx += 1
                obs_type = item.attrib.get('type', 'line') # 默认为 line
                
                # --- 情况 1: 直线 (Line) ---
                if obs_type == 'line':
                    if 'x1' in item.attrib and 'x2' in item.attrib:
                        x1 = float(item.attrib['x1'])
                        y1 = float(item.attrib['y1'])
                        x2 = float(item.attrib['x2'])
                        y2 = float(item.attrib['y2'])
                        generate_line_obstacle(x1, y1, x2, y2, idx)
                
                # --- 情况 2: 圆形 (Circle) ---
                elif obs_type == 'circle':
                    if 'x' in item.attrib and 'radius' in item.attrib:
                        x = float(item.attrib['x'])
                        y = float(item.attrib['y'])
                        r = float(item.attrib['radius'])
                        generate_circle_obstacle(x, y, r, idx)

                # --- 情况 3: 矩形 (Rectangle) ---
                elif obs_type == 'rectangle':
                    if 'x' in item.attrib and 'xHalfLength' in item.attrib:
                        x = float(item.attrib['x'])
                        y = float(item.attrib['y'])
                        hx = float(item.attrib['xHalfLength'])
                        hy = float(item.attrib['yHalfLength'])
                        theta = float(item.attrib.get('theta', 0.0)) # 矩形可能有旋转
                        generate_rectangle_obstacle(x, y, hx, hy, theta, idx)

    except FileNotFoundError:
        print(f"错误: 找不到文件 {xmlfile}")
    except Exception as e:
        print(f"解析出错: {e}")

# ---------------------------------------------------------
# 主生成逻辑
# ---------------------------------------------------------
def generate_gzb_world(pedsim_file_name): 
    rospack1 = RosPack()
    pkg_path = rospack1.get_path('pedsim_simulator')
    
    # 路径指向 scenes
    xml_scenario = os.path.join(pkg_path, "scenes", pedsim_file_name)
    
    rospack2 = RosPack()
    pkg_path_gazebo = rospack2.get_path('pedsim_gazebo_plugin')
    
    file_basename = os.path.splitext(pedsim_file_name)[0]
    gazebo_world_path = os.path.join(pkg_path_gazebo, "worlds", file_basename + ".world")
    
    global gzb_world    
    with open(gazebo_world_path, 'w') as f:
        gzb_world = f 
        
        print("<?xml version=\"1.0\" ?>", file=gzb_world)    
        print('''<sdf version="1.5">
      <world name="default">
      <include><uri>model://ground_plane</uri></include>
      <include><uri>model://sun</uri></include>
        ''', file=gzb_world)
        
        if os.path.exists(xml_scenario):
            parseXML(xml_scenario)
        else:
            print(f"致命错误: 找不到源文件 {xml_scenario}")
            return

        print('''
            <plugin name="ActorPosesPlugin" filename="libActorPosesPlugin.so"></plugin>
      </world>
    </sdf>''', file=gzb_world)
        
    print(f"Gazebo World 已生成: {gazebo_world_path}")

def generate_launch_file(pedsim_file_name): 
    rospack2 = RosPack()
    pkg_path = rospack2.get_path('pedsim_gazebo_plugin')
    
    file_basename = os.path.splitext(pedsim_file_name)[0]
    launch_file_path = os.path.join(pkg_path, "launch", file_basename + ".launch")
    
    with open(launch_file_path, 'w') as launch:
        print(f'''<launch>
        <include file="$(find gazebo_ros)/launch/empty_world.launch">
             <arg name="world_name" value="$(find pedsim_gazebo_plugin)/worlds/{file_basename}.world"/>
         </include>
         <node pkg="pedsim_gazebo_plugin" type="spawn_pedsim_agents.py" name="spawn_pedsim_agents" output="screen">
         </node>
</launch>
''', file=launch)

    print(f"Launch File 已生成: {launch_file_path}")

if __name__ == "__main__": 
    print(">> 请输入 pedsim_simulator/scenes/ 下的文件名 (例如: lobby_45ped.xml)")
    pedsim_file_name = input(">> Filename: ").strip()

    if pedsim_file_name:
        generate_gzb_world(pedsim_file_name)     
        generate_launch_file(pedsim_file_name) 
        
        file_basename = os.path.splitext(pedsim_file_name)[0]
        print("\n>> 完成！运行以下命令启动:")
        print(f"   roslaunch pedsim_gazebo_plugin {file_basename}.launch")
    else:
        print("未输入文件名，程序退出。")