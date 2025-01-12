import sys
import numpy as np
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# グローバル変数
g_ControlPoints = []
g_RobotPosition = None
g_RobotAngle = 0.0  # ロボットの回転角度
g_Animating = False
g_WindowWidth = 512
g_WindowHeight = 512
ID_ROBOT_LIST = 1  # ロボットのディスプレイリストID

def draw_robot_list():
    """ロボットのディスプレイリストを作成"""
    glNewList(ID_ROBOT_LIST, GL_COMPILE)

    # 本体部分
    glColor3d(0.0, 1.0, 1.0)
    glBegin(GL_POLYGON)
    glVertex2d(0.0, 0.2)
    glVertex2d(-0.1, 0.1)
    glVertex2d(-0.1, -0.1)
    glVertex2d(0.1, -0.1)
    glVertex2d(0.1, 0.1)
    glEnd()

    # 車輪部分
    glColor3d(0.0, 0.0, 0.0)
    for i, j in [(0.0, 0.0), (0.22, 0.0), (0.0, -0.14), (0.22, -0.14)]:
        glBegin(GL_POLYGON)
        glVertex2d(-0.12 + i, 0.1 + j)
        glVertex2d(-0.12 + i, 0.04 + j)
        glVertex2d(-0.1 + i, 0.04 + j)
        glVertex2d(-0.1 + i, 0.1 + j)
        glEnd()

    glEndList()

def display():
    """描画処理"""
    glClearColor(1., 1., 1., 1.)
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

    # ロボットの描画
    if g_RobotPosition is not None:
        glPushMatrix()

        # 位置の平行移動
        glTranslated(g_RobotPosition[0], g_RobotPosition[1], 0)

        # 進行方向の回転
        glRotated(g_RobotAngle, 0, 0, 1)

        # ロボットの描画
        glCallList(ID_ROBOT_LIST)

        glPopMatrix()

    glFlush()

def resize(w, h):
    """ウィンドウサイズ変更時の処理"""
    global g_WindowWidth, g_WindowHeight
    if h > 0:
        g_WindowWidth = w
        g_WindowHeight = h
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -10, 10)
        glMatrixMode(GL_MODELVIEW)

def mouse(button, state, x, y):
    """マウス操作の処理"""
    global g_ControlPoints, g_RobotPosition, g_RobotAngle, g_Animating
    if state == GLUT_DOWN:
        if button == GLUT_LEFT_BUTTON:
            g_ControlPoints.append(np.array([x, y]))
        elif button == GLUT_RIGHT_BUTTON and len(g_ControlPoints) > 1:
            g_RobotPosition = g_ControlPoints[0].astype(float)  # 修正箇所
            g_RobotAngle = 0.0
            g_Animating = True
            glutIdleFunc(animate)
    glutPostRedisplay()

def animate():
    """アニメーションの処理"""
    global g_ControlPoints, g_RobotPosition, g_RobotAngle, g_Animating

    if not g_Animating or len(g_ControlPoints) < 2:
        glutIdleFunc(None)
        return

    # 現在位置と次の制御点を取得
    p0 = g_RobotPosition
    p1 = g_ControlPoints[1]

    # 進行方向ベクトルを計算
    direction = p1 - p0
    distance = np.linalg.norm(direction)

    # 移動速度
    speed = 1.0

    # ロボットが次の制御点に近づいたか判定
    if distance < speed:
        g_ControlPoints.pop(0)  # 次の制御点に到達したら制御点を削除
        if len(g_ControlPoints) < 2:
            g_Animating = False
            glutIdleFunc(None)
            return

        p0 = g_RobotPosition
        p1 = g_ControlPoints[1]
        direction = p1 - p0
        distance = np.linalg.norm(direction)

    # 進行方向に移動
    g_RobotPosition += (direction / distance) * speed

    # 回転角度を更新
    g_RobotAngle = math.degrees(math.atan2(direction[1], direction[0]))

    glutPostRedisplay()

def init():
    """初期化処理"""
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

    # ロボットのディスプレイリスト作成
    draw_robot_list()

if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitWindowSize(g_WindowWidth, g_WindowHeight)
    glutCreateWindow(b"Robot Animation")
    glutDisplayFunc(display)
    glutReshapeFunc(resize)
    glutMouseFunc(mouse)
    init()
    glutMainLoop()
