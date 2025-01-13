import sys
import math
import numpy as np
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

g_WindowWidth = 512  # ウィンドウの横幅
g_WindowHeight = 512  # ウィンドウの高さ

g_ControlPoints = []  # クリック点を格納する
g_RobotPosition = None  # ロボットの位置の座標を格納する
g_RobotT = 0.0  # ロボットを動かすアニメーションを実行するために必要なパラメータ
g_Animating = False  # アニメーションを動かすかどうかを判断する変数

theta = 0  # ロボットの向き

ID_ROBOT_LIST = 1  # ロボットを描画するためのディスプレイリストのID
ID_LINE_LIST = 2  # 点と直線を描画するためのディスプレイリストのID

def draw_robot_list():  # ロボットを描画するディスプレイリストを作成する
    glNewList(ID_ROBOT_LIST, GL_COMPILE)

    # 車体
    glColor3d(0.0, 1.0, 1.0)
    glBegin(GL_POLYGON)
    glVertex2d(0, -40)
    glVertex2d(-20, -20)
    glVertex2d(-20, 20)
    glVertex2d(20, 20)
    glVertex2d(20, -20)
    glEnd()

    # タイヤ
    glColor3d(0.0, 0.0, 0.0)
    for i,j in [(0, 0), (0, 30), (-45, 0), (-45, 30)]:
        glBegin(GL_POLYGON)
        glVertex2d(20+i, -20+j)
        glVertex2d(25+i, -20+j)
        glVertex2d(25+i, -10+j)
        glVertex2d(20+i, -10+j)
        glEnd()

    glEndList()

def draw_line_list():  # 点と直線を描画するディスプレイリストを作成する
    glNewList(ID_LINE_LIST, GL_COMPILE)

    # 点
    glPointSize(5)
    glColor3d(0., 0., 0.)
    glBegin(GL_POINTS)
    for point in g_ControlPoints:
        glVertex2dv(point)
    glEnd()

    # 直線
    glColor3d(1., 0., 0.)
    glLineWidth(1)
    glBegin(GL_LINE_STRIP)
    for point in g_ControlPoints:
        glVertex2dv(point)
    glEnd()

    glEndList()

def display():  # 描画を実行する関数
    glClearColor(1., 1., 1., 1.)  # 消去色を指定する
    glClear(GL_COLOR_BUFFER_BIT)

    # 点と直線を描画
    glCallList(ID_LINE_LIST)
    # 変換行列の初期化
    glLoadIdentity()
    # ロボットを描画
    if g_RobotPosition is not None and g_ControlPoints != []:
        glPushMatrix()  # スタックに現在の変換行列を格納する
        glTranslated(*g_RobotPosition, 0)  # ライン上の点に沿ってロボットを平行移動させる
        glRotated(theta, 0, 0, 1)  # ロボットが進行方向を向くように回転移動させる
        glCallList(ID_ROBOT_LIST)  # ディスプレイリストを呼び出す
        glPopMatrix()  # スタックの最上部の変換行列を取り出す

    glutSwapBuffers()  # 画面に表示させる

def resize(w, h):  # ウィンドウのサイズが変更されたときの処理
    global g_WindowWidth, g_WindowHeight
    if h > 0:
        glViewport(0, 0, w, h)
        g_WindowWidth = w
        g_WindowHeight = h
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -10, 10)
        glMatrixMode(GL_MODELVIEW)

def mouse(button, state, x, y):  # マウス操作に関する関数
    global g_ControlPoints, g_RobotPosition, g_Animating, g_RobotT, theta

    if state == GLUT_DOWN:  # マウス操作が行われたとき
        if button == GLUT_LEFT_BUTTON:  # 左クリックのとき
            g_ControlPoints.append(np.array([x, y]))  # クリック点を格納する
            if g_RobotPosition is None:
                g_RobotPosition = np.array([x, y])
            if len(g_ControlPoints) > 1:  # クリック点が2個以上のとき、ロボットを動かす
                # ロボットの回転角度を計算
                dx = g_ControlPoints[-1][0] - g_ControlPoints[-2][0]
                dy = g_ControlPoints[-1][1] - g_ControlPoints[-2][1]
                theta = math.degrees(math.atan2(dy, dx)) + 90
                g_Animating = True
                glutIdleFunc(animate)  # 左クリックによりロボットが進む動き表現する関数を呼び出す

        elif button == GLUT_RIGHT_BUTTON:  # 右クリックのとき
            if len(g_ControlPoints) > 1:  # クリック点が2個以上のとき、ロボットを動かす
                g_Animating = True
                g_RobotPosition = g_ControlPoints[-1]  # ロボットの位置を保存しておく
                g_ControlPoints.pop()  # 現在の座標をポップする
                glutIdleFunc(animate_back)  # 右クリックによりロボットが戻る動きを表現する関数を呼び出す

    # デバッグ用にプリントしていた
    # print(g_ControlPoints)
    # print(f"Theta: {theta}")

    draw_line_list()  # クリックによって点と直線も描画するので、ディスプレイリストを作成する
    glutPostRedisplay()  # 最新の状態になるように再描画する

def animate():  # 左クリックによるアニメーション
    global g_RobotPosition, g_RobotT, g_Animating

    # g_AnimatingがFalseの場合は終了する
    if not g_Animating:
        glutIdleFunc(None)
        return

    # 直線の端点を設定する
    p0 = g_ControlPoints[-2]
    p1 = g_ControlPoints[-1]

    g_RobotT += 0.001  # ロボットの直線状での座標を変えるためのパラメータ
    if g_RobotT > 1.0:  # パラメータが1までなので、1を超えたら、パラメータをリセットし、アニメーションを終了させる
        g_RobotT = 0.0
        g_Animating = False
        glutIdleFunc(None)
        return

    g_RobotPosition = (1 - g_RobotT) * p0 + g_RobotT * p1  # ロボットの位置を更新する
    glutPostRedisplay()  # 最新の状態になるように再描画する

def animate_back():  # 右クリックによるアニメーション
    global g_RobotPosition, g_RobotT, g_Animating

    # g_AnimatingがFalseの場合は終了する
    if not g_Animating:
        glutIdleFunc(None)
        return

    # 直線の端点を設定する
    p0 = g_RobotPosition
    p1 = g_ControlPoints[-1]

    g_RobotT += 0.001  # ロボットの直線状での座標を変えるためのパラメータ
    if g_RobotT > 1.0:  # パラメータが1までなので、1を超えたら、パラメータをリセットし、アニメーションを終了させる
        g_RobotT = 0.0
        g_Animating = False
        g_RobotPosition = g_ControlPoints[-1]
        glutIdleFunc(None)
        return

    g_RobotPosition = (1 - g_RobotT) * p0 + g_RobotT * p1  # ロボットの位置を更新する
    glutPostRedisplay()  # 最新の状態になるように再描画する

def init():  # OpenGLの初期化設定を行う
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

if __name__ == "__main__":
    glutInit(sys.argv)  # ライブラリの初期化
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)  # OpenGLでのダブルバッファリングにおいてmain関数で行う初期化
    glutInitWindowSize(g_WindowWidth, g_WindowHeight)  # ウィンドウサイズを指定
    glutCreateWindow(sys.argv[0])  # ウィンドウを作成
    glutDisplayFunc(display)  # 表示関数を指定
    draw_robot_list()  # ロボットを描画するディスプレイリストを作成
    glutReshapeFunc(resize)  # ウィンドウサイズが変更されたときの関数を指定
    glutMouseFunc(mouse)  # マウス関数を指定
    init()  # 初期設定を行う
    glutMainLoop()  # イベント待ち
