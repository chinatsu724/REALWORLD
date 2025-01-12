# 修正版コード
import sys
import math
import numpy as np
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

g_ControlPoints = []  # 制御点
g_WindowWidth = 512
g_WindowHeight = 512
g_RobotPosition = None
g_RobotT = 0.0
g_Animating = False
theta = 0
ID_ROBOT_LIST = 1
ID_LINE_LIST = 2

def draw_robot_list():
    glNewList(ID_ROBOT_LIST, GL_COMPILE)
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
    glEndList()

def draw_line_list():
    glNewList(ID_LINE_LIST, GL_COMPILE)
    glPointSize(5)
    glColor3d(0., 0., 0.)
    glBegin(GL_POINTS)
    for point in g_ControlPoints:
        glVertex2dv(point)
    glEnd()
    glColor3d(1., 0., 0.)
    glLineWidth(1)
    glBegin(GL_LINE_STRIP)
    for point in g_ControlPoints:
        glVertex2dv(point)
    glEnd()
    glEndList()

def display():
    glClearColor(1., 1., 1., 1.)
    glClear(GL_COLOR_BUFFER_BIT)

    glCallList(ID_LINE_LIST)

    glLoadIdentity()

    if g_RobotPosition is not None and g_ControlPoints != []:
        glPushMatrix()
        glTranslated(*g_RobotPosition, 0)
        glCallList(ID_ROBOT_LIST)
        glPopMatrix()

    glutSwapBuffers()

def resize(w, h):
    global g_WindowWidth, g_WindowHeight
    if h > 0:
        glViewport(0, 0, w, h)
        g_WindowWidth = w
        g_WindowHeight = h
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -10, 10)
        glMatrixMode(GL_MODELVIEW)

def mouse(button, state, x, y):
    global g_ControlPoints, g_RobotPosition, g_Animating, g_RobotT, theta

    if state == GLUT_DOWN:
        if button == GLUT_LEFT_BUTTON:
            g_ControlPoints.append(np.array([x, y]))
            if g_RobotPosition is None:
                g_RobotPosition = np.array([x, y])
            if len(g_ControlPoints) > 1:
                g_Animating = True
                glutIdleFunc(animate)

        elif button == GLUT_RIGHT_BUTTON:
            if g_ControlPoints and len(g_ControlPoints) > 1:
                g_Animating = True
                g_RobotPosition = g_ControlPoints[-1]
                g_ControlPoints.pop()
                glutIdleFunc(animate_back)

    print(g_ControlPoints)

    draw_line_list()
    glutPostRedisplay()

def animate():
    global g_RobotPosition, g_RobotT, g_Animating

    if not g_Animating:
        glutIdleFunc(None)
        return

    p0 = g_ControlPoints[-2]
    p1 = g_ControlPoints[-1]

    g_RobotT += 0.001
    if g_RobotT > 1.0:
        g_RobotT = 0.0
        g_Animating = False
        glutIdleFunc(None)
        return

    g_RobotPosition = (1 - g_RobotT) * p0 + g_RobotT * p1
    glutPostRedisplay()

def animate_back():
    global g_RobotPosition, g_RobotT, g_Animating

    if not g_Animating:
        glutIdleFunc(None)
        return

    p0 = g_RobotPosition
    p1 = g_ControlPoints[-1]

    g_RobotT += 0.001
    if g_RobotT > 1.0:
        g_RobotT = 0.0
        g_Animating = False
        g_RobotPosition = g_ControlPoints[-1]
        glutIdleFunc(None)
        return

    g_RobotPosition = (1 - g_RobotT) * p0 + g_RobotT * p1
    glutPostRedisplay()

def keyboard(key, x, y):
    if key == b'\x1b':
        exit()
    glutPostRedisplay()

def init():
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(g_WindowWidth, g_WindowHeight)
    glutCreateWindow(sys.argv[0])
    glutDisplayFunc(display)
    draw_robot_list()
    glutReshapeFunc(resize)
    glutMouseFunc(mouse)
    glutKeyboardFunc(keyboard)
    init()
    glutMainLoop()
