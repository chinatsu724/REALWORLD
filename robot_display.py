import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

def display():
    glClearColor(1., 1., 1., 1.) 
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3d(0.0, 1.0, 1.0)
    glBegin(GL_POLYGON)
    glVertex2d(0.0, 0.2)
    glVertex2d(-0.1, 0.1)
    glVertex2d(-0.1, -0.1)
    glVertex2d(0.1, -0.1)
    glVertex2d(0.1, 0.1)
    glEnd()

    glColor3d(0.0, 0.0, 0.0)  # 色指定(R,G,B)で0～1まで
    for i,j in [(0.0, 0.0), (0.22, 0.0), (0.0, -0.14), (0.22, -0.14)]:
        glBegin(GL_POLYGON)
        glVertex2d(-0.12+i, 0.1+j)
        glVertex2d(-0.12+i, 0.04+j)
        glVertex2d(-0.1+i, 0.04+j)
        glVertex2d(-0.1+i, 0.1+j)
        glEnd()

    glFlush()

if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitWindowSize(600, 600)
    glutCreateWindow(sys.argv[0])
    glutDisplayFunc(display)
    glutMainLoop()