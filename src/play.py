import pygame
from src import config
import os
import time
import sys
from src.board.gobang import GoBang
from src.mcts.mcts_zero import MCTSZero
from src.mcts.mcts import MCTS
from src.models.mcts import Model

"""
使用棋盘开始玩
"""
pygame.init()
pygame.display.set_caption('五子棋')  # 改标题
screen = pygame.display.set_mode((640, 640))
# 给窗口填充颜色，颜色用三原色数字列表表示
screen.fill([125, 95, 24])

width = config.default_width
height = config.default_height
white = [255, 255, 255]
black = [0, 0, 0]


def draw(data=None):
    for h in range(width):
        pygame.draw.line(screen, black, [40, 40 + h * 70], [600, 40 + h * 70], 1)

        pygame.draw.line(screen, black, [40 + h * 70, 40], [40 + h * 70, 600], 1)
        # 在棋盘上标出，天元以及另外4个特殊点位
        pygame.draw.circle(screen, black, [320, 320], 5, 0)
        pygame.draw.circle(screen, black, [180, 180], 3, 0)
        pygame.draw.circle(screen, black, [180, 460], 3, 0)
        pygame.draw.circle(screen, black, [460, 180], 3, 0)
        pygame.draw.circle(screen, black, [460, 460], 3, 0)
    if data:
        for action, player in data.items():
            color = black if player == 0 else white
            h, w = action // width, action % width
            pos = [40 + 70 * w + 1, 40 + 70 * h]
            # 画出棋子
            pygame.draw.circle(screen, color, pos, 22, 0)
    pygame.display.flip()  # 刷新窗口显示


board = GoBang()
model = Model()
mcts = MCTS(model)
mcts_zero = MCTSZero(mcts)
draw()
while True:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            h = round((y - 40) / 70)
            w = round((x - 40) / 70)
            action = h * width + w
            mcts.reset_action(board, action)
            board.move(action)
            draw(board.actions)
            is_end, player = board.is_end
            if is_end:
                board.reset()
                screen.fill([125, 95, 24])
            action, probs = mcts_zero.get_action(board)
            board.move(action)
            draw(board.actions)
            is_end, player = board.is_end
            if is_end:
                board.reset()
                screen.fill([125, 95, 24])

        break
