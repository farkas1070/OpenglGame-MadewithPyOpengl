import os
from enum import Enum
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import numpy
import pyrr
from SkyBox import SkyBox
from Texture import Texture
from Camera import Camera
from Ground import Ground
from Map import Map
from ObjLoader import ObjLoader

# minden alapérték beállítása
speed = 25
distance = 800
leftxpositionforobject = 300
rightxpositionforobject = -110
zpositionforobject = 7000
sensitivity = 0.05
lightX = -200.0
lightY = 200.0
lightZ = 100.0
firstCursorCallback = True
exitProgram = False
failed = False
win = False


class ObjectType(Enum):
    CUSTOM_MODEL = 1,
    WALL = 1,
    CACTUS = 2,
    ROCK = 3,
    FINISH_LINE = 4


selectObject = ObjectType.CUSTOM_MODEL


class Material(Enum):
    YELLOW_RUBBER = 1


materialType = Material.YELLOW_RUBBER
angle = 0

# a kurzor függvénye a kamerához

# Atallitjuk az eleresi utat az aktualis fajlhoz
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ha nem indul el a glfw, akkor hiba (exception)
if not glfw.init():
    raise Exception("glfw init hiba")

# window beállítása
window = glfw.create_window(1280, 720, "OpenGL window",
                            None, None)

# window pozíció beállítása, az input mód beállítása, behelyezzük a korábban megírt kurzor függvényt, az ablakot megtesszük a mostani "kontextknek, bekapcsoljuk a depth-tesztet, és beállítjuk a viewportot"
glfw.set_window_pos(window, 0, 0)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

glfw.make_context_current(window)
glEnable(GL_DEPTH_TEST)

glViewport(0, 0, 1280, 720)

# framebuffer előkészítése
frameBuffer = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, frameBuffer)
texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1280, 720, 0, GL_RGB, GL_UNSIGNED_BYTE, ctypes.c_void_p(0))
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glBindTexture(GL_TEXTURE_2D, 0)

glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

rbo = glGenRenderbuffers(1)
glBindRenderbuffer(GL_RENDERBUFFER, rbo)
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 1280, 720)
glBindRenderbuffer(GL_RENDERBUFFER, 0)

glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo)

if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
    print("Hiba a framebuffer elokeszitesekor!")
else:
    print("Framebuffer elokeszitve!")

rectanglevertices = [
    -1,  1, 0, 0,
    1,  1, 1, 0,
    1, -1, 1, 1,
    -1, -1, 0, 1
]
rectanglevertices = numpy.array(rectanglevertices, dtype=numpy.float32)
glBindFramebuffer(GL_FRAMEBUFFER, 0)
rectangle = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, rectangle)

# shaderek beolvasása, elnevezése
with open("screen_shader.vert") as f:
    vertex_shader = f.read()
    print(vertex_shader)

with open("screen_shader.frag") as f:
    fragment_shader = f.read()
    print(fragment_shader)
screen_shader = OpenGL.GL.shaders.compileProgram(
    OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
    OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
)

glUseProgram(0)


with open("vertex_shader_texture.vert") as f:
    vertex_shader = f.read()
    print(vertex_shader)

with open("fragment_shader_texture.frag") as f:
    fragment_shader = f.read()
    print(fragment_shader)

position_loc = glGetAttribLocation(screen_shader, 'in_position')
glEnableVertexAttribArray(position_loc)
glVertexAttribPointer(position_loc, 2, GL_FLOAT, False,
                      rectanglevertices.itemsize * 4, ctypes.c_void_p(0))

texture_loc = glGetAttribLocation(screen_shader, 'in_texCoord')
glEnableVertexAttribArray(texture_loc)
glVertexAttribPointer(texture_loc, 2, GL_FLOAT, False,
                      rectanglevertices.itemsize * 4, ctypes.c_void_p(8))

glBufferData(GL_ARRAY_BUFFER, rectanglevertices.nbytes,
             rectanglevertices, GL_STATIC_DRAW)

glBindBuffer(GL_ARRAY_BUFFER, 0)

# A fajlbol beolvasott stringeket leforditjuk, es a ket shaderbol egy shader programot gyartunk.
shader = OpenGL.GL.shaders.compileProgram(
    OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
    OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER),
    validate=False
)

# Megcsinájuk az osztály változókat
camera = Camera(100, 10, 4000)
skyBox = SkyBox("right.jpg", "left.jpg", "top.jpg",
                "bottom.jpg", "front.jpg", "back.jpg")
ground = Ground(0, -10, 0, 500, 8200)
world = Map(5, 100)

# beállítjuk a változókat a custom model változóhoz
if selectObject == ObjectType.CUSTOM_MODEL:
    indices, vertices = ObjLoader.load_model("goodlowpolytree.obj")
    vertCount = len(indices)
    shapeType = GL_TRIANGLES
    objecttexture = Texture("treetexture.jpg")
    wintexture = Texture("wintexture.jpg")


# elokeszitjuk az OpenGL-nek a memoriat:
vertices = numpy.array(vertices, dtype=numpy.float32)


def createModel(shader):
    # keszitunk egy uj buffert, ez itt meg akarmi is lehet
    vao = glGenBuffers(1)
    # megadjuk, hogy ez egy ARRAY_BUFFER legyen (kesobb lesz mas fajta is)
    glBindBuffer(GL_ARRAY_BUFFER, vao)
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                 indices.nbytes, indices, GL_STATIC_DRAW)

    # Feltoltjuk a buffert a szamokkal.
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Ideiglenesen inaktivaljuk a buffert, hatha masik objektumot is akarunk csinalni.
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    return vao, ebo


def renderModel(vao, ebo, vertCount, shapeType):
    Texture.enableTexturing()
    objecttexture.activate()
    # Mindig 1 GL_ARRAY_BUFFER lehet aktiv, most megmondjuk, hogy melyik legyen az
    glBindBuffer(GL_ARRAY_BUFFER, vao)
#	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)

    # Az OpenGL nem tudja, hogy a bufferben levo szamokat hogy kell ertelmezni
    # A kovetkezo 3 sor ezert megmondja, hogy majd 3-asaval kell kiszednia bufferbpl
    # a szamokat, és azokat a vertex shaderben levo 'position' 3-as vektorba kell mindig
    # betolteni.
    position_loc = glGetAttribLocation(shader, 'in_position')
    glEnableVertexAttribArray(position_loc)
    glVertexAttribPointer(position_loc, 3, GL_FLOAT, False,
                          vertices.itemsize * 8, ctypes.c_void_p(0))

    normal_loc = glGetAttribLocation(shader, 'in_normal')
    glEnableVertexAttribArray(normal_loc)
    glVertexAttribPointer(normal_loc, 3, GL_FLOAT, False,
                          vertices.itemsize * 8, ctypes.c_void_p(20))

    texture_loc = glGetAttribLocation(shader, 'in_texture')
    glEnableVertexAttribArray(texture_loc)
    glVertexAttribPointer(texture_loc, 2, GL_FLOAT, False,
                          vertices.itemsize * 8, ctypes.c_void_p(24))

    glDrawArrays(shapeType, 0, vertCount)
    


# beállítjuk hogy a program a shader változóból beolvasott shadereket használja
glUseProgram(shader)

# itt megadjuk hogy a nézet, és a fényértekek milyenek legyenek
lightPos_loc = glGetUniformLocation(shader, 'lightPos')
viewPos_loc = glGetUniformLocation(shader, 'viewPos')
glUniform3f(lightPos_loc, lightX, lightY, lightZ)
glUniform3f(viewPos_loc, camera.x, camera.y, camera.z)
materialAmbientColor_loc = glGetUniformLocation(shader, "materialAmbientColor")
materialDiffuseColor_loc = glGetUniformLocation(shader, "materialDiffuseColor")
materialSpecularColor_loc = glGetUniformLocation(
    shader, "materialSpecularColor")
materialEmissionColor_loc = glGetUniformLocation(
    shader, "materialEmissionColor")
materialShine_loc = glGetUniformLocation(shader, "materialShine")
lightAmbientColor_loc = glGetUniformLocation(shader, "lightAmbientColor")
lightDiffuseColor_loc = glGetUniformLocation(shader, "lightDiffuseColor")
lightSpecularColor_loc = glGetUniformLocation(shader, "lightSpecularColor")
glUniform3f(lightAmbientColor_loc, 1.0, 1.0, 1.0)
glUniform3f(lightDiffuseColor_loc, 1.0, 1.0, 1.0)
glUniform3f(lightSpecularColor_loc, 1.0, 1.0, 1.0)

# A materiál értékek beállítása
if materialType is Material.YELLOW_RUBBER:
    glUniform3f(materialAmbientColor_loc, 0.05, 0.05, 0.0)
    glUniform3f(materialDiffuseColor_loc, 0.5, 0.5, 0.4)
    glUniform3f(materialSpecularColor_loc, 0.7, 0.7, 0.04)
    glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
    glUniform1f(materialShine_loc, 10)

# beállítjuk a perpektív, a világ, a nézet, és a viewworldlocationt a shadernek
perspectiveLocation = glGetUniformLocation(shader, "projection")
worldLocation = glGetUniformLocation(shader, "world")
viewLocation = glGetUniformLocation(shader, "view")
viewWorldLocation = glGetUniformLocation(shader, "viewWorld")

# perspektívmátrix beállítása, paraméterezése
perspMat = pyrr.matrix44.create_perspective_projection_matrix(
    45.0, 1280.0 / 720.0, 0.1, distance)
glUniformMatrix4fv(perspectiveLocation, 1, GL_FALSE, perspMat)

# objektgenerálási függvéyn, ami a rendelést, és mindent csinál paraméterezve

modelV, modelI = createModel(shader)
def generateobject(modelV,modelI, translatex, translatez, translatey, scalex, scalez, scaley):

    
    transMat = pyrr.matrix44.create_from_translation(
        pyrr.Vector3([translatex, translatez, translatey]))
    scaleMat = pyrr.matrix44.create_from_scale([scalex, scalez, scaley])
    worldMat = pyrr.matrix44.multiply(scaleMat, transMat)
    glUniformMatrix4fv(worldLocation, 1, GL_FALSE, worldMat)
    viewWorldMatrix = pyrr.matrix44.multiply(worldMat, camera.getMatrix())
    glUniformMatrix4fv(viewWorldLocation, 1, GL_FALSE, viewWorldMatrix)
    glUniformMatrix4fv(viewLocation, 1, GL_FALSE, camera.getMatrix())
    
    renderModel(modelV, modelI, vertCount, shapeType)


def placebackgroundmodels():
    generateobject(modelV,modelI,leftxpositionforobject, -50, 5500, 30, 30, 30)
    generateobject(modelV,modelI,leftxpositionforobject, -50, 6500, 30, 30, 30)
    generateobject(modelV,modelI,leftxpositionforobject, -50, 4500, 30, 30, 30)
    generateobject(modelV,modelI,leftxpositionforobject, -50, 3500, 30, 30, 30)
    generateobject(modelV,modelI,leftxpositionforobject, -50, 2500, 30, 30, 30)
    generateobject(modelV,modelI,leftxpositionforobject, -50, 1500, 30, 30, 30)
    generateobject(modelV,modelI,leftxpositionforobject, -50, 500, 30, 30, 30)
    generateobject(modelV,modelI,leftxpositionforobject, -50, 2000, 30, 30, 30)
    generateobject(modelV,modelI,rightxpositionforobject, -50, 5500, 30, 30, 30)
    generateobject(modelV,modelI,rightxpositionforobject, -50, 6500, 30, 30, 30)
    generateobject(modelV,modelI,rightxpositionforobject, -50, 4500, 30, 30, 30)
    generateobject(modelV,modelI,rightxpositionforobject, -50, 3500, 30, 30, 30)
    generateobject(modelV,modelI,rightxpositionforobject, -50, 2500, 30, 30, 30)
    generateobject(modelV,modelI,rightxpositionforobject, -50, 1500, 30, 30, 30)
    generateobject(modelV,modelI,rightxpositionforobject, -50, 500, 30, 30, 30)
    generateobject(modelV,modelI,rightxpositionforobject, -50, 2000, 30, 30, 30)
    


world.setLightPos(lightX, lightY, lightZ)
viewMat = pyrr.matrix44.create_look_at(
    [0.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0])



while not glfw.window_should_close(window) and not exitProgram and not failed:
    startTime = glfw.get_time()
    glfw.poll_events()

    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        exitProgram = True

    directionTry = speed
    directionReal = speed
    camera.move(directionTry)

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:

        directionTry = -240*elapsedTime
        directionReal = -120*elapsedTime
        camera.moveonx(directionTry)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:

        directionTry = 240*elapsedTime
        directionReal = 120*elapsedTime
        camera.moveonx(directionTry)

    cellX, cellZ = camera.getCellPosition(20)
    collision = False
    if world.isFinishLine(cellZ, cellX):
        win = True

    if world.isSomething(cellZ, cellX) and not world.isFinishLine(cellZ, cellX):
        collision = True
        failed = True

    print(world.getCellType(cellZ, cellX))

    glClearDepth(1.0)
    glClearColor(0, 0.1, 0.1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    skyBox.render(perspMat, camera.getMatrixForCubemap())

    ground.render(camera.getMatrix(), perspMat)
    world.render(camera, perspMat)

    glUseProgram(shader)
    glUniform3f(viewPos_loc, camera.x, camera.y, camera.z)
    # ezek a külső mapon vannak, csak a látvány miatt vannak bennt
    placebackgroundmodels()
    wintexture.activate()

    skybox_loc = glGetUniformLocation(shader, "skybox")
    glUniform1i(skybox_loc, 0)
    skyBox.activateCubeMap(shader, 1)
    endTime = glfw.get_time()
    elapsedTime = endTime - startTime
    
    if win:
        speed=0
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClearDepth(1.0)
        glClearColor(0, 0.1, 0.1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        glUseProgram(screen_shader)

        glBindBuffer(GL_ARRAY_BUFFER, rectangle)
        position_loc = glGetAttribLocation(screen_shader, 'in_position')
        glEnableVertexAttribArray(position_loc)
        glVertexAttribPointer(position_loc, 2, GL_FLOAT, False, 4 * 4, ctypes.c_void_p(0))
        texture_loc = glGetAttribLocation(screen_shader, 'in_texCoord')
        glEnableVertexAttribArray(texture_loc)
        glVertexAttribPointer(texture_loc, 2, GL_FLOAT, False, 4 * 4, ctypes.c_void_p(8))

        glBindTexture(GL_TEXTURE_2D, texture)
        
        glDrawArrays(GL_QUADS, 0, 4)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glUseProgram(0)
    glfw.swap_buffers(window)

glfw.terminate()
