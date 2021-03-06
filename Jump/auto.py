# _*_ coding  ：  UTF-8 _*_
# 开发团队    ：  dream
# 开发人员    ：  刘育彬
# 开发时间    ：  2020/1/31  19:47
# 文件名称    ：  auto.py
# 开发工具    ：  PyCharm


import os                  # 系统模块
import subprocess          # 子进程模块
import random              # 随机数模块


# 是否循环游戏
loop = False


# 获取屏幕截图
def get_screen_shot():
    # 通过 adb 命令截取当前手机界面，然后将截图保存在手机的 sd 卡根目录下
    os.system('adb shell screencap -p /sdcard/autojump.png')
    # 将手机中的截图保存在当前项目夹当中
    os.system('adb pull /sdcard/autojump.png')


def find_piece_and_board():
    # 获取图片的宽高
    w, h = img.size
    # 棋子的底边界
    piece_y_max = 0
    scan_x_side = int(w / 8)        # 扫描棋子的左右边界减少开销
    scan_star_y = 0                # 扫描起始 y 坐标
    # 图片像素矩阵
    img_pixel = img.load
    if not loop:                   # 是否循环游戏
        if sum(img_pixel[5, 5][: -1]) < 150:             # 屏幕黑色，也就是手机锁屏后游戏结束
            stop()
    # 以 50px 步长，尝试探测 scan_start_y
    for i in range(int(h / 3), int(h * 2 / 3), 50):
        # 每一行第一个像素
        first_pixel = img_pixel[0, i]
        for j in range(1, w):
            # 每一个像素
            pixel = img_pixel[j, i]
            # 如果不是纯色，说明碰到了新的棋盘，跳出，找到了 y 轴最大值
            if pixel[0] != first_pixel[0] or pixel != first_pixel[1] or pixel[2] != first_pixel[2]:
                # 找到最高点
                scan_star_y = i - 50
                break
        if scan_star_y:
            break
    # 从上往下开始扫描棋子，棋子位于屏幕上半部分
    left = 0
    right = 0
    for i in range(scan_star_y, int(h * 2 /3)):
        flag = True
        # 切掉左右八分之一
        for j in range(scan_x_side, w - scan_x_side):
            pixel = img_pixel[j, i]
            # 根据棋子的最低行的颜色判断，找最后一行像素点的起始和末尾
            # 判断 RGB 颜色为棋子的颜色
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                if flag:
                    left = j                # 记录棋子底部第一个横坐标
                    flag = False
                    right = j               # 记录棋子底部最后的横坐标
                    # 棋子最后一行像素的 y 轴坐标点
                    piece_y_max = max(i, piece_y_max)
    if not all((left, right)):
        return 0, 0, 0, 0
    # 棋子底部中心
    piece_x = (left + right) // 2
    # 寻找落点
    board_x = 0
    # 限制棋盘扫描的横坐标，如果棋子位置小于图片宽度的一半时
    # 设置扫描期盼的范围
    if piece_x < w /2:
        board_x_start, board_x_end = w//2, w         # 起点和终点的中心是画面中心
    else:
        board_x_start, board_x_end = 0, w//2

    # 寻找落点顶点
    board_x_set = []
    for by in range((h - w) // 2, (h + w) // 2, 4):
        bg_pixel = img_pixel[0, by]
        for bx in range(board_x_start, board_x_end):
            pixel = img_pixel[bx, by]
            # 色差比较
            if (abs(pixel[0] - bg_pixel[0]) + abs(pixel[1] - bg_pixel[1]) + abs(pixel[2] - bg_pixel[2]) > 10):
                board_x_set.append(bx)
        if len(board_x_set) > 10:
            # 根据筛选出来的色差坐标，获取棋盘横向坐标的中心点
            board_x = sum(board_x_set) / len(board_x_set)
            break          # 找到了退出
    print('读取图片并获取棋子与棋盘位置横向中心坐标')
    return piece_x, board_x


def jump(piece_x, board_x, im, point):
    distanceX = abs(board_x - piece_x)                           # 起点到目标的水平距离
    shortEdge = min(im.size)                 # 屏幕宽度
    jumpPercent = distanceX / shortEdge      # 跳跃百分比
    jumpFullWidth = 1700                     # 跳过整个宽度，需要按压的好描述
    press_time = round(jumpFullWidth * jumpPercent)            # 按压时间
    press_time = 0 if not press_time else max(press_time, 200)                  # press_time 大于0 时限定最小值
    # 按压命令
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(x1=point[0],
                                                                        y1=point[1],
                                                                        x2=point[0] + random.randint(0, 3),
                                                                        y2=point[1] + random.randint(0, 3),
                                                                        duration=press_time)
    os.system(cmd)
    print('生成按压命令，执行跳！')
    # 停止自动跳


def stop():
    exit('停止自动跳！')
