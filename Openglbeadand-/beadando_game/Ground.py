from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import math
import numpy
import pyrr
from Texture import Texture
from enum import Enum


class ObjectType(Enum):
    WALL = 0


class Ground:
    def __init__(self, x, y, z, width, height):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.cellsize = 20
        vertices = [
            -width / 2 + x, y, -height / 2 + z, 0, 0,
            width / 2 + x, y, -height / 2 + z, 10, 0,
            width / 2 + x, y, height / 2 + z, 10, 10,
            -width / 2 + x, y, height / 2 + z, 0, 10
        ]
        vertices = numpy.array(vertices, dtype=numpy.float32)
        self.buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        with open("ground.vert") as f:
            vertex_shader = f.read()

        with open("ground.frag") as f:
            fragment_shader = f.read()

        # A fajlbol beolvasott stringeket leforditjuk, es a ket shaderbol egy shader programot gyartunk.
        self.shader = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(
                fragment_shader, GL_FRAGMENT_SHADER)
        )
        self.groundTexture = Texture("sand.jpg")

    def setLightPos(self, x, y, z):
        self.lightX = x
        self.lightY = y
        self.lightZ = z

    def render(self, viewMatrix, projectionMatrix):
        Texture.enableTexturing()
        self.groundTexture.activate()

        glUseProgram(self.shader)
        proj_loc = glGetUniformLocation(self.shader, 'projection')
        view_loc = glGetUniformLocation(self.shader, 'view')
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projectionMatrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, viewMatrix)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)

        position_loc = glGetAttribLocation(self.shader, 'in_position')
        glEnableVertexAttribArray(position_loc)
        glVertexAttribPointer(position_loc, 3, GL_FLOAT,
                              False, 4 * 5, ctypes.c_void_p(0))

        texture_loc = glGetAttribLocation(self.shader, 'in_texture')
        glEnableVertexAttribArray(texture_loc)
        glVertexAttribPointer(texture_loc, 2, GL_FLOAT,
                              False, 4 * 5, ctypes.c_void_p(3*4))


        glDrawArrays(GL_QUADS, 0, 4)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glUseProgram(0)



