from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import math
import numpy
import pyrr
from enum import Enum
from Texture import Texture
import random
from ObjLoader import ObjLoader


class ObjectType(Enum):
    NOTHING = 0,
    WALL = 1,
    CACTUS = 2,
    ROCK = 3,
    FINISH_LINE = 5,
    LOG = 6


class Map:
    def __init__(self, width, height):
        self.width = 2*width + 3
        self.height = 2*height + 3
        self.obsticles = 0
        difficulty = input("select which difficulty you want to play, the options are easy, normal and hard  ")
        if difficulty == "easy":
            self.obsticles = 5
        if difficulty == "normal":
            self.obsticles = 8
        if difficulty == "hard":
            self.obsticles = 10

        self.table = [[ObjectType.NOTHING for _ in range(
            self.width)] for _ in range(self.height)]

        for i in range(0, self.height):
            self.table[i][0] = ObjectType.WALL
            self.table[i][self.width - 1] = ObjectType.WALL

        for i in range(0, self.width):
            self.table[0][i] = ObjectType.FINISH_LINE
            self.table[self.height - 1][i] = ObjectType.WALL

        for i in range(self.obsticles + 10):
            randomheightvalue = random.randint(2, self.height-25)
            randomwidthvalue = random.randint(2, self.width-2)
            self.table[randomheightvalue][randomwidthvalue] = ObjectType.CACTUS
        for i in range(self.obsticles):
            randomheightvalue = random.randint(2, self.height-25)
            randomwidthvalue = random.randint(2, self.width-2)
            self.table[randomheightvalue][randomwidthvalue] = ObjectType.ROCK
        
        for i in range(self.obsticles):
            randomheightvalue = random.randint(2, self.height-25)
            randomwidthvalue = random.randint(2, self.width-2)
            self.table[randomheightvalue][randomwidthvalue] = ObjectType.LOG
        

        vertices = [0.0, 1.0, 1.0,  0, 1, 0, 0, 0,
                    1.0, 1.0, 1.0,  0, 1, 0, 0, 1,
                    1.0, 1.0, 0.0,  0, 1, 0, 1, 1,
                    0.0, 1.0, 0.0,  0, 1, 0, 1, 0,

                    0.0, 0.0, 1.0,  0, -1, 0, 0, 0,
                    1.0, 0.0, 1.0,  0, -1, 0, 0, 1,
                    1.0, 0.0, 0.0,  0, -1, 0, 1, 1,
                    0.0, 0.0, 0.0,  0, -1, 0, 1, 0,

                    1.0, 0.0, 1.0,  1, 0, 0, 0, 0,
                    1.0, 0.0, 0.0,  1, 0, 0, 0, 1,
                    1.0,  1.0, 0.0,  1, 0, 0, 1, 1,
                    1.0,  1.0, 1.0,  1, 0, 0, 1, 0,

                    0.0, 0.0, 1.0,  -1, 0, 0, 0, 0,
                    0.0, 0.0, 0.0,  -1, 0, 0, 0, 1,
                    0.0,  1.0, 0.0,  -1, 0, 0, 1, 1,
                    0.0,  1.0, 1.0,  -1, 0, 0, 1, 0,

                    0.0,  0.0,  1.0, 0, 0, 1, 0, 0,
                    1.0,  0.0,  1.0, 0, 0, 1, 0, 1,
                    1.0,   1.0,  1.0, 0, 0, 1, 1, 1,
                    0.0,   1.0,  1.0, 0, 0, 1, 1, 0,

                    0.0,  0.0,  0.0, 0, 0, -1, 0, 0,
                    1.0,  0.0,  0.0, 0, 0, -1, 0, 1,
                    1.0,   1.0,  0.0, 0, 0, -1, 1, 1,
                    0.0,   1.0,  0.0, 0, 0, -1, 1, 0]

        vertices = numpy.array(vertices, dtype=numpy.float32)
        self.buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # cactus

        self.cactusindices, self.cactusvertices = ObjLoader.load_model(
            "goodlowpolycactus.obj")
        self.cactusvertices = numpy.array(
            self.cactusvertices, dtype=numpy.float32)
        self.cactusvertCount = len(self.cactusindices)
        self.cactusshapeType = GL_TRIANGLES
        self.cactustexture = Texture("cactustexture.png")
        self.cactusangle = 0

        # rock

        self.rockindices, self.rockvertices = ObjLoader.load_model(
            "goodlowpolyrock.obj")
        self.rockvertices = numpy.array(self.rockvertices, dtype=numpy.float32)
        self.rockvertCount = len(self.rockindices)
        self.rockshapeType = GL_TRIANGLES
        self.rocktexture = Texture("desertrocktexture.jpg")
        self.rockangle = 0

        #log
        self.logindices, self.logvertices = ObjLoader.load_model(
            "logs.obj")
        self.logvertices = numpy.array(self.logvertices, dtype=numpy.float32)
        self.logvertCount = len(self.logindices)
        self.logshapeType = GL_TRIANGLES
        self.logtexture = Texture("log.jpg")
        self.logangle = 0


        

        with open("cube.vert") as f:
            vertex_shader = f.read()

        with open("cube.frag") as f:
            fragment_shader = f.read()

        # A fajlbol beolvasott stringeket leforditjuk, es a ket shaderbol egy shader programot gyartunk.
        self.shader = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(
                fragment_shader, GL_FRAGMENT_SHADER)
        )
        self.wallTexture = Texture("desertrocktexture.jpg")
        self.finish_line_texture = Texture("ckeckboard.jpg")
        self.cellSize = 20

    def createModel(self, indices, vertices):
        # keszitunk egy uj buffert, ez itt meg akarmi is lehet
        vao = glGenBuffers(1)
        # megadjuk, hogy ez egy ARRAY_BUFFER legyen (kesobb lesz mas fajta is)
        glBindBuffer(GL_ARRAY_BUFFER, vao)
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     indices.nbytes, indices, GL_STATIC_DRAW)

        # Feltoltjuk a buffert a szamokkal.
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

        # Ideiglenesen inaktivaljuk a buffert, hatha masik objektumot is akarunk csinalni.
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        return vao, ebo

    def setLightPos(self, x, y, z):
        self.lightX = x
        self.lightY = y
        self.lightZ = z

    def renderModel(self, vao, ebo, vertices, vertCount, shapeType):

        # Mindig 1 GL_ARRAY_BUFFER lehet aktiv, most megmondjuk, hogy melyik legyen az
        glBindBuffer(GL_ARRAY_BUFFER, vao)
    #	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)

        # Az OpenGL nem tudja, hogy a bufferben levo szamokat hogy kell ertelmezni
        # A kovetkezo 3 sor ezert megmondja, hogy majd 3-asaval kell kiszednia bufferbpl
        # a szamokat, és azokat a vertex shaderben levo 'position' 3-as vektorba kell mindig
        # betolteni.
        position_loc = glGetAttribLocation(self.shader, 'in_position')
        glEnableVertexAttribArray(position_loc)
        glVertexAttribPointer(position_loc, 3, GL_FLOAT,
                              False, vertices.itemsize * 8, ctypes.c_void_p(0))

        normal_loc = glGetAttribLocation(self.shader, 'in_normal')
        glEnableVertexAttribArray(normal_loc)
        glVertexAttribPointer(normal_loc, 3, GL_FLOAT, False,
                              vertices.itemsize * 8, ctypes.c_void_p(20))

        texture_loc = glGetAttribLocation(self.shader, 'in_texture')
        glEnableVertexAttribArray(texture_loc)
        glVertexAttribPointer(texture_loc, 2, GL_FLOAT,
                              False, vertices.itemsize * 8, ctypes.c_void_p(24))

        # Kirajzoljuk a buffert, a 0. vertextol kezdve, 24-et ( a kockanak 6 oldala van, minden oldalhoz 4 csucs).
        glDrawArrays(shapeType, 0, vertCount)
        #glDrawElements(GL_TRIANGLES, vertCount, GL_UNSIGNED_INT, None)

    def render(self, camera, projectionMatrix):

        glUseProgram(self.shader)

        materialAmbientColor_loc = glGetUniformLocation(
            self.shader, "materialAmbientColor")
        materialDiffuseColor_loc = glGetUniformLocation(
            self.shader, "materialDiffuseColor")
        materialSpecularColor_loc = glGetUniformLocation(
            self.shader, "materialSpecularColor")
        materialEmissionColor_loc = glGetUniformLocation(
            self.shader, "materialEmissionColor")
        materialShine_loc = glGetUniformLocation(self.shader, "materialShine")
        glUniform3f(materialAmbientColor_loc, 0.25, 0.25, 0.25)
        glUniform3f(materialDiffuseColor_loc, 0.4, 0.4, 0.4)
        glUniform3f(materialSpecularColor_loc, 0.774597, 0.774597, 0.774597)
        glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
        glUniform1f(materialShine_loc, 76.8)

        lightAmbientColor_loc = glGetUniformLocation(
            self.shader, "lightAmbientColor")
        lightDiffuseColor_loc = glGetUniformLocation(
            self.shader, "lightDiffuseColor")
        lightSpecularColor_loc = glGetUniformLocation(
            self.shader, "lightSpecularColor")

        glUniform3f(lightAmbientColor_loc, 1.0, 1.0, 1.0)
        glUniform3f(lightDiffuseColor_loc, 1.0, 1.0, 1.0)
        glUniform3f(lightSpecularColor_loc, 1.0, 1.0, 1.0)

        lightPos_loc = glGetUniformLocation(self.shader, 'lightPos')
        viewPos_loc = glGetUniformLocation(self.shader, 'viewPos')
        glUniform3f(lightPos_loc, self.lightX, self.lightY, self.lightZ)
        glUniform3f(viewPos_loc, camera.x, camera.y, camera.z)

        proj_loc = glGetUniformLocation(self.shader, 'projection')
        view_loc = glGetUniformLocation(self.shader, 'view')
        world_loc = glGetUniformLocation(self.shader, 'world')
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projectionMatrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, camera.getMatrix())

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)

        position_loc = glGetAttribLocation(self.shader, 'in_position')
        glEnableVertexAttribArray(position_loc)
        glVertexAttribPointer(position_loc, 3, GL_FLOAT,
                              False, 4 * 8, ctypes.c_void_p(0))

        normal_loc = glGetAttribLocation(self.shader, 'in_normal')
        glEnableVertexAttribArray(normal_loc)
        glVertexAttribPointer(normal_loc, 3, GL_FLOAT,
                              False, 4 * 8, ctypes.c_void_p(12))

        texture_loc = glGetAttribLocation(self.shader, 'in_texture')
        glEnableVertexAttribArray(texture_loc)
        glVertexAttribPointer(texture_loc, 2, GL_FLOAT,
                              False, 4 * 8, ctypes.c_void_p(24))

        Texture.enableTexturing()
        self.wallTexture.activate()
        # wall
        for row in range(0, self.height):
            for col in range(0, self.width):
                if self.table[row][col] == ObjectType.WALL:
                    transMat = pyrr.matrix44.create_from_translation(
                        pyrr.Vector3([col*self.cellSize, -10, row*self.cellSize]))
                    scaleMat = pyrr.matrix44.create_from_scale(
                        [self.cellSize, self.cellSize, self.cellSize])
                    worldMat = pyrr.matrix44.multiply(scaleMat, transMat)
                    glUniformMatrix4fv(world_loc, 1, GL_FALSE, worldMat)
                    glDrawArrays(GL_QUADS, 0, 24)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        # finish_line
        self.finish_line_texture.activate()
        for row in range(0, self.height):
            for col in range(0, self.width):
                if self.table[row][col] == ObjectType.FINISH_LINE:
                    transMat = pyrr.matrix44.create_from_translation(
                        pyrr.Vector3([col*self.cellSize, -10, row*self.cellSize]))
                    scaleMat = pyrr.matrix44.create_from_scale(
                        [self.cellSize, self.cellSize, self.cellSize])
                    worldMat = pyrr.matrix44.multiply(scaleMat, transMat)
                    glUniformMatrix4fv(world_loc, 1, GL_FALSE, worldMat)
                    glDrawArrays(GL_QUADS, 0, 24)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        # cactus
        self.cactustexture.activate()
        for row in range(0, self.height):
            for col in range(0, self.width):
                if self.table[row][col] == ObjectType.CACTUS:
                    transMat = pyrr.matrix44.create_from_translation(
                        pyrr.Vector3([col*self.cellSize, -10, row*self.cellSize]))
                    rotMat = pyrr.matrix44.create_from_axis_rotation(
                        pyrr.Vector3([1., 0., 0.0]), math.radians(self.cactusangle))
                    modelMat = pyrr.matrix44.multiply(rotMat, transMat)
                    glUniformMatrix4fv(world_loc, 1, GL_FALSE, modelMat)
                    modelV, modelI = self.createModel(
                        self.cactusindices, self.cactusvertices)
                    self.renderModel(
                        modelV, modelI, self.cactusvertices, self.cactusvertCount, self.cactusshapeType)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        # bush
        self.rocktexture.activate()
        for row in range(0, self.height):
            for col in range(0, self.width):
                if self.table[row][col] == ObjectType.ROCK:
                    transMat = pyrr.matrix44.create_from_translation(
                        pyrr.Vector3([col*self.cellSize, -10, row*self.cellSize]))
                    scaleMat = pyrr.matrix44.create_from_scale(
                        [self.cellSize/3, self.cellSize/3, self.cellSize/3])
                    worldMat = pyrr.matrix44.multiply(scaleMat, transMat)
                    glUniformMatrix4fv(world_loc, 1, GL_FALSE, worldMat)

                    modelV, modelI = self.createModel(
                        self.rockindices, self.rockvertices)
                    self.renderModel(
                        modelV, modelI, self.rockvertices, self.rockvertCount, self.rockshapeType)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        #log
        self.logtexture.activate()
        for row in range(0, self.height):
            for col in range(0, self.width):
                if self.table[row][col] == ObjectType.LOG:
                    transMat = pyrr.matrix44.create_from_translation(
                        pyrr.Vector3([col*self.cellSize, -5, row*self.cellSize]))
                    scaleMat = pyrr.matrix44.create_from_scale(
                        [self.cellSize/3, self.cellSize/3, self.cellSize/3])
                    worldMat = pyrr.matrix44.multiply(scaleMat, transMat)
                    glUniformMatrix4fv(world_loc, 1, GL_FALSE, worldMat)

                    modelV, modelI = self.createModel(
                        self.logindices, self.logvertices)
                    self.renderModel(
                        modelV, modelI, self.logvertices, self.logvertCount, self.logshapeType)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        
        glUseProgram(0)

    def getCellType(self, row, col):
        if row <= -1 or col <= -1 or row >= self.height or col >= self.width:
            return ObjectType.NOTHING
        return self.table[row][col]

    def isSomething(self, row, col):
        if self.table[row][col] == ObjectType.NOTHING:
            return False
        return True

    def isFinishLine(self, row, col):
        if self.table[row][col] == ObjectType.FINISH_LINE:
            return True
        return False
