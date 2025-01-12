import sys
import numpy as np
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

# 制御点を格納する配列
g_ControlPoints = []

# ウィンドウサイズを保持する
g_WindowWidth = 512
g_WindowHeight = 512

# ロボットの位置
g_RobotPosition = None
g_RobotIndex = 0
g_RobotT = 0.0  # 線分上の進行度 (0.0～1.0)

# アニメーション状態
g_Animating = False

# ロボットの描画
def draw_robot(x, y):
    glPushMatrix()
    glTranslated(x, y, 0)

    glColor3d(0.0, 1.0, 1.0)
    glBegin(GL_POLYGON)
    glVertex2d(0, -40)
    glVertex2d(-20, -20)
    glVertex2d(-20, 20)
    glVertex2d(20, 20)
    glVertex2d(20, -20)
    glEnd()

    glColor3d(0.0, 0.0, 0.0)  # 色指定(R,G,B)で0～1まで
    for i,j in [(0, 0), (0, 30), (-45, 0), (-45, 30)]:
        glBegin(GL_POLYGON)
        glVertex2d(20+i, -20+j)
        glVertex2d(25+i, -20+j)
        glVertex2d(25+i, -10+j)
        glVertex2d(20+i, -10+j)
        glEnd()

    glPopMatrix()

#表示部分をこの関数で記入
def display():
    glClearColor(1., 1., 1., 1.) # 消去色指定
    glClear(GL_COLOR_BUFFER_BIT)

    # 制御点の描画
    glPointSize(5)
    glColor3d(0., 0., 0.)
    glBegin(GL_POINTS)
    for point in g_ControlPoints:
        glVertex2dv(point)    
    glEnd()

    # 制御点を結ぶ線分の描画
    glColor3d(1., 0., 0.)   
    glLineWidth(1)
    glBegin(GL_LINE_STRIP)
    for point in g_ControlPoints:
        glVertex2dv(point)    
    glEnd()

    glLoadIdentity()

    # ロボットの描画
    if g_RobotPosition is not None:
        draw_robot(*g_RobotPosition)

    glutSwapBuffers()

# ウィンドウのサイズが変更されたときの処理
def resize(w, h):
    global g_WindowWidth, g_WindowHeight
    if h > 0:
        glViewport(0, 0, w, h)
        g_WindowWidth = w
        g_WindowHeight = h
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # ウィンドウ内の座標系設定
        glOrtho(0, w, h, 0, -10, 10)
        glMatrixMode(GL_MODELVIEW)

# マウスクリックのイベント処理
def mouse(button, state, x, y):
    global g_ControlPoints, g_RobotPosition, g_Animating, g_RobotIndex, g_RobotT

    if state == GLUT_DOWN: 
        # 左ボタン: ロボットの初期位置を設定
        if button == GLUT_LEFT_BUTTON:
            if g_RobotPosition is None:  # 修正: 明示的に None と比較
                g_RobotPosition = np.array([x, y])
            g_ControlPoints.append(np.array([x, y]))

        # 右ボタン: アニメーションを開始
        if button == GLUT_RIGHT_BUTTON:
            if g_ControlPoints and len(g_ControlPoints) > 1:
                g_Animating = True
                g_RobotIndex = 0
                g_RobotT = 0.0
                glutIdleFunc(animate)

    glutPostRedisplay()

# ロボットを線分に沿って移動させるアニメーション
def animate():
    global g_RobotPosition, g_RobotIndex, g_RobotT, g_Animating

    if not g_Animating or g_RobotIndex >= len(g_ControlPoints) - 1:
        glutIdleFunc(None)  # アニメーションを停止
        return

    # 現在の線分の始点と終点を取得
    p0 = g_ControlPoints[g_RobotIndex]
    p1 = g_ControlPoints[g_RobotIndex + 1]

    # 線分上を移動 (tを増加)
    g_RobotT += 0.001
    if g_RobotT > 1.0:
        g_RobotT = 0.0
        g_RobotIndex += 1
        if g_RobotIndex >= len(g_ControlPoints) - 1:
            g_Animating = False
            glutIdleFunc(None)  # アニメーションを停止
            return

    # 線分上のロボットの位置を更新
    g_RobotPosition = (1 - g_RobotT) * p0 + g_RobotT * p1
    glutPostRedisplay()

# キーが押されたときのイベント処理
def keyboard(key, x, y): 
    if key == b'\x1b':  # ESCキー
        exit()

    glutPostRedisplay()

def init():
    # アンチエイリアスを有効にする
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

if __name__ == "__main__":
    glutInit(sys.argv) #ライブラリの初期化
    glutInitWindowSize(g_WindowWidth, g_WindowHeight) #ウィンドウサイズを指定
    glutCreateWindow(sys.argv[0]) #ウィンドウを作成
    glutDisplayFunc(display) #表示関数を指定
    glutReshapeFunc(resize) # ウィンドウサイズが変更されたときの関数を指定
    glutMouseFunc(mouse) # マウス関数を指定
    glutKeyboardFunc(keyboard) # キーボード関数を指定
    init() # 初期設定を行う
    glutMainLoop() #イベント待ち
