#!/usr/bin/env python3
import random

class MazeGenerator:
    def __init__(self, width=15, height=15, cell_size=2.0):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        # 初始化网格：False表示有墙，True表示通路 (或者反过来，这里用简单的墙壁记录法)
        # 这里为了生成 Pedsim 墙壁，我们记录墙的存在性
        # hor_walls[y][x] 表示格子(x,y)下方的墙
        self.hor_walls = [[True for _ in range(width)] for _ in range(height)]
        # ver_walls[y][x] 表示格子(x,y)右侧的墙
        self.ver_walls = [[True for _ in range(width)] for _ in range(height)]
        self.visited = [[False for _ in range(width)] for _ in range(height)]

    def generate(self, seed=None):
        """使用递归回溯算法生成迷宫"""
        if seed is not None:
            random.seed(seed)
            
        # 重置状态
        self.hor_walls = [[True for _ in range(self.width)] for _ in range(self.height)]
        self.ver_walls = [[True for _ in range(self.width)] for _ in range(self.height)]
        self.visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        self._visit(0, 0)
        return self

    def _visit(self, x, y):
        self.visited[y][x] = True
        # 定义四个方向：(dx, dy, wall_type)
        # wall_type='h' 表示操作水平墙，'v' 表示操作垂直墙
        directions = [
            (0, -1, 'h', 'up'),    # 上
            (0, 1,  'h', 'down'),  # 下
            (-1, 0, 'v', 'left'),  # 左
            (1, 0,  'v', 'right')  # 右
        ]
        random.shuffle(directions)

        for dx, dy, w_type, direction in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < self.width and 0 <= ny < self.height and not self.visited[ny][nx]:
                # 打通墙壁
                if w_type == 'h':
                    if direction == 'down': self.hor_walls[y][x] = False
                    else:                   self.hor_walls[ny][nx] = False # 打通上方，即上方格子的下墙
                else:
                    if direction == 'right': self.ver_walls[y][x] = False
                    else:                    self.ver_walls[ny][nx] = False # 打通左方，即左方格子的右墙
                
                self._visit(nx, ny)

    def save_xml(self, filename):
        """将生成的迷宫保存为 Pedsim XML 格式，并返回起终点坐标"""
        # 计算偏移量，使迷宫中心在 (0,0)
        offset_x = (self.width * self.cell_size) / 2.0
        offset_y = (self.height * self.cell_size) / 2.0
        
        def get_pos(ix, iy):
            return ix * self.cell_size - offset_x, iy * self.cell_size - offset_y

        # 设定起点 (0,0格子中心) 和 终点 (右下角格子中心)
        start_x, start_y = get_pos(0.5, 0.5)
        goal_x, goal_y = get_pos(self.width - 0.5, self.height - 0.5)

        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append('<scenario>')
        lines.append('    ')
        
        # 1. 绘制固定的上边界和左边界
        # 上边 (y=0 的上方)
        x1, y1 = get_pos(0, 0)
        x2, y2 = get_pos(self.width, 0)
        lines.append(f'    <obstacle x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" type="line"/>')
        # 左边 (x=0 的左方)
        x1, y1 = get_pos(0, 0)
        x2, y2 = get_pos(0, self.height)
        lines.append(f'    <obstacle x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" type="line"/>')

        lines.append('    ')
        # 2. 遍历网格绘制墙壁
        for y in range(self.height):
            for x in range(self.width):
                # 如果下方有墙
                if self.hor_walls[y][x]:
                    px1, py1 = get_pos(x, y + 1)
                    px2, py2 = get_pos(x + 1, y + 1)
                    lines.append(f'    <obstacle x1="{px1:.2f}" y1="{py1:.2f}" x2="{px2:.2f}" y2="{py2:.2f}" type="line"/>')
                
                # 如果右方有墙
                if self.ver_walls[y][x]:
                    px1, py1 = get_pos(x + 1, y)
                    px2, py2 = get_pos(x + 1, y + 1)
                    lines.append(f'    <obstacle x1="{px1:.2f}" y1="{py1:.2f}" x2="{px2:.2f}" y2="{py2:.2f}" type="line"/>')

        lines.append('')
        lines.append('    ')
        lines.append(f'    <waypoint id="goal" x="{goal_x:.2f}" y="{goal_y:.2f}" r="1.5"/>')

        lines.append('')
        lines.append('    ')
        lines.append(f'    <agent x="{start_x:.2f}" y="{start_y:.2f}" n="1" dx="0" dy="0" type="2">')
        lines.append('        <addwaypoint id="goal"/>')
        lines.append('    </agent>')

        lines.append('</scenario>')

        with open(filename, 'w') as f:
            f.write("\n".join(lines))
        
        return (start_x, start_y), (goal_x, goal_y)