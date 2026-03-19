#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
import sys, select, termios, tty # 用于处理非阻塞键盘输入

# 键盘操作提示
msg = """
控制你的机器人!
---------------------------
移动方向:
    w : 增加线速度 (前进)
    s : 减少线速度 (后退)
    a : 增加角速度 (左转)
    d : 减少角速度 (右转)

    space : 紧急刹车 (速度清零)
    q     : 退出
---------------------------
"""

# 获取键盘按键的函数（非阻塞）
def getKey():
    tty.setraw(sys.stdin.fileno())
    # 等待 0.1 秒看有没有按键输入
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def simple_publisher():
    rospy.init_node('my_teleop_node', anonymous=True)
    
    # 注意：海龟用 /turtle1/cmd_vel，通用机器人用 /cmd_vel
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)

    rate = rospy.Rate(10) # 10Hz 连续发布

    # 初始化速度
    target_linear_vel = 0.0
    target_angular_vel = 0.0
    
    # 每次按键增加的步长
    LIN_VEL_STEP = 0.1
    ANG_VEL_STEP = 0.2

    print(msg)

    while not rospy.is_shutdown():
        key = getKey() # 获取当前按下的键

        if key == 'w':
            target_linear_vel += LIN_VEL_STEP
            print(f">> 线速度累计: {target_linear_vel:.2f}")
        elif key == 's':
            target_linear_vel -= LIN_VEL_STEP
            print(f">> 线速度累计: {target_linear_vel:.2f}")
        elif key == 'a':
            target_angular_vel += ANG_VEL_STEP
            print(f">> 角速度累计: {target_angular_vel:.2f}")
        elif key == 'd':
            target_angular_vel -= ANG_VEL_STEP
            print(f">> 角速度累计: {target_angular_vel:.2f}")
        elif key == ' ':
            target_linear_vel = 0.0
            target_angular_vel = 0.0
            print(">> 刹车！")
        elif key == 'q':
            print("退出中...")
            break
        
        # 构造消息
        vel_msg = Twist()
        vel_msg.linear.x = target_linear_vel
        vel_msg.angular.z = target_angular_vel

        # 连续发布（无论有没有按键，都会发布当前的速度状态）
        pub.publish(vel_msg)
        
        rate.sleep()

if __name__ == '__main__':
    # 保存终端设置，防止程序结束后终端乱码
    settings = termios.tcgetattr(sys.stdin)
    try:
        simple_publisher()
    except rospy.ROSInterruptException:
        pass
    finally:
        # 退出前发一个停止指令，并恢复终端状态
        stop_msg = Twist()
        # pub.publish(stop_msg) # 如果想退出时停下可以取消注释
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)