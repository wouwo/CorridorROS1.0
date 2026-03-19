#!/usr/bin/env python3
import os
import time
import random
import math
import subprocess
import signal
import rospy
from nav_msgs.msg import Odometry
# 引入刚才写的生成器
from maze_generator import MazeGenerator 

# ---------------------------------------------------------
# 监控类：负责检查机器人是否到达终点
# ---------------------------------------------------------
class ExperimentMonitor:
    def __init__(self, goal_pos, threshold=1.0):
        self.goal_pos = goal_pos
        self.threshold = threshold
        self.success = False
        self.min_dist = 9999.0
        # 订阅机器人位置，注意根据你的实际话题调整，可能是 /odom 或 /pedbot/control/odom
        self.sub = rospy.Subscriber("/odom", Odometry, self.callback)

    def callback(self, msg):
        rx = msg.pose.pose.position.x
        ry = msg.pose.pose.position.y
        dist = math.hypot(self.goal_pos[0] - rx, self.goal_pos[1] - ry)
        if dist < self.min_dist:
            self.min_dist = dist
        
        if dist < self.threshold:
            self.success = True

    def stop(self):
        self.sub.unregister()

# ---------------------------------------------------------
# 主流程
# ---------------------------------------------------------
def run_all_experiments(total_episodes=500):
    rospy.init_node('maze_batch_runner', anonymous=True)

    # 获取 pedsim_simulator 包的路径，用于存放临时文件
    try:
        pkg_path = subprocess.check_output("rospack find pedsim_simulator", shell=True).decode('utf-8').strip()
    except:
        print("Error: 找不到 pedsim_simulator 包，请确认已 source 工作空间")
        return

    xml_path = os.path.join(pkg_path, "scenes", "temp_maze_autogen.xml")
    csv_file = "experiment_results.csv"

    # 初始化结果文件
    with open(csv_file, "w") as f:
        f.write("Episode,Width,Height,Result,TimeUsed,MinDistance\n")

    print(f"=== 开始 {total_episodes} 组迷宫导航测试 ===")

    for i in range(total_episodes):
        episode_id = i + 1
        
        # --- 1. 生成新迷宫 ---
        # 随机设定迷宫复杂度
        w = 4
        h = 4
        
        generator = MazeGenerator(width=w, height=h, cell_size=2.0)
        generator.generate(seed=None) # seed=None 表示全随机
        (start_pos, goal_pos) = generator.save_xml(xml_path)
        
        print(f"\n[Episode {episode_id}] Map: {w}x{h}, Start: {start_pos}, Goal: {goal_pos}")

        # --- 2. 启动 ROS 仿真 ---
        # 动态传入 xml 路径和机器人初始位置
        cmd = [
            "roslaunch", 
            "pedsim_simulator", 
            "simulator.launch", 
            f"scene_file:={xml_path}",
            f"pose_initial_x:={start_pos[0]}",
            f"pose_initial_y:={start_pos[1]}",
            "with_robot:=true",
            "default_queue_size:=1"
        ]

        # 启动子进程，静音输出以免刷屏
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # --- 3. 监控运行 ---
        monitor = ExperimentMonitor(goal_pos, threshold=2.0)
        
        start_time = time.time()
        timeout = 90.0 # 90秒超时
        result_status = "TIMEOUT"
        
        while time.time() - start_time < timeout:
            if rospy.is_shutdown():
                proc.kill()
                return
            
            if monitor.success:
                result_status = "SUCCESS"
                break
            
            time.sleep(0.5)

        duration = time.time() - start_time
        monitor.stop()

        print(f"  -> {result_status} (Time: {duration:.2f}s, Min Dist: {monitor.min_dist:.2f}m)")

        # --- 4. 记录数据 ---
        with open(csv_file, "a") as f:
            f.write(f"{episode_id},{w},{h},{result_status},{duration:.2f},{monitor.min_dist:.2f}\n")

        # --- 5. 清理并准备下一轮 ---
        # 优雅退出 roslaunch
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        
        # 等待 ROS 节点完全清理，防止端口占用
        time.sleep(3)

    print(f"\n全部测试结束，结果已保存至 {csv_file}")

if __name__ == "__main__":
    try:
        run_all_experiments(500)
    except rospy.ROSInterruptException:
        pass