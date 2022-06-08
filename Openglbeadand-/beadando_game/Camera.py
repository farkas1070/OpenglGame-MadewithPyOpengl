from OpenGL.GL import *
from OpenGL.GLU import *
import math
import pyrr

class Camera:
	"""!
		Kamera osztaly. A kamera mozgatasaert, beallitasaert felel.
	"""
	def __init__(self, x, y, z):
		"""!
			@param x: A kamera kezdo x koordinataja.
			@param y: A kamera kezdo y koordinataja.
			@param z: A kamera kezdo z koordinataja.
		"""
		self.x = x
		self.y = y
		self.z = z
		self.dirX = 0
		self.dirY = 0
		self.dirZ = -1
		
	
	def move(self, dist):
		"""!
			Az kamera aktualis iranyanak megfelelo iranyba mozditja el a kamerat.
			@param dist: Azt adja meg, hogy az iranyvektor hanyszorosaval mozduljunk el.
		"""

		self.prevX = self.x
		self.prevY = self.y
		self.prevZ = self.z
		self.x += self.dirX * dist
		#self.y += self.dirY * dist
		self.z += self.dirZ * dist
		


	def undo(self):
		self.x = self.prevX
		self.y = self.prevY
		self.z = self.prevZ

	def getCellPosition(self, cellSize):
		return int(self.x / cellSize), int(self.z / cellSize)


	
	def moveonx(self,value):
		self.x += value

	def getMatrixForCubemap(self):
		return pyrr.matrix44.create_look_at([0.0, 0.0, 0.0], 
											[self.dirX, self.dirY, self.dirZ], 
											[0.0, 1.0, 0.0])
	def getMatrix(self):
		return pyrr.matrix44.create_look_at([self.x, self.y, self.z], 
											[self.x + self.dirX, self.y + self.dirY, self.z + self.dirZ], 
											[0.0, 1.0, 0.0])

	def apply(self):
		"""!
			Atadja az OpenGL-nek a kamera beallitasait.
		"""
		glLoadIdentity()
		gluLookAt(self.x, self.y, self.z, 
					self.x + self.dirX, 
					self.y + self.dirY, 
					self.z + self.dirZ, 0, 1, 0)
