import random
import pygame

pygame.init()

WIDTH  = 1024
HEIGHT = 1024

BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
BLUE    = (0, 0, 255)
L_RED   = (255, 128, 128)
L_GREEN = (128, 255, 128)
PINK    = (255, 128, 255)

def rect_intersection(la, ta, wa, ha, lb, tb, wb, hb):
	x = False
	y = False

	ra = la + wa
	ba = ta + ha

	rb = lb + wb
	bb = tb + hb

	if lb < ra and la < rb:
		x = True

	if tb < ba and ta < bb:
		y = True

	return x and y

class Point:
	def __init__(self, x, y, vx=None, vy=None):
		self.x = x
		self.y = y
		self.rx = self.x
		self.ry = self.y

		if vx:
			self.vx = vx
		else:
			self.vx = 10 * (random.random())

		if vy:
			self.vy = vy
		else:
			self.vy = 1 * (random.random())

	def __repr__(self):
		return f'Point(x={self.x}, y={self.y}, vx={self.vx:.2f}, vy={self.vy:.2f})'

	def step(self):
		self.rx += self.vx
		self.ry += self.vy
		self.x = int(self.rx)
		self.y = int(self.ry)

class QuadTree:
	def __init__(self, left, top, width, height, max_size=1):
		self.left     = left
		self.top      = top
		self.width    = width
		self.height   = height
		self.right    = self.left + self.width
		self.bottom   = self.top  + self.height
		self.h_width  = self.width//2
		self.h_height = self.width//2
		self.h_left   = self.left + self.h_width
		self.h_top    = self.top  + self.h_height

		self.points  = []
		self.divided = False
		self.target  = False

		self.upper_left  = None
		self.upper_right = None
		self.lower_left  = None
		self.lower_right = None

		self.max_size = max_size
		self.children_count = 0

		self.marker = False

	def draw(self, surface):
		if self.divided:
			self.upper_left.draw(surface)
			self.upper_right.draw(surface)
			self.lower_left.draw(surface)
			self.lower_right.draw(surface)
		else:
			color = L_RED

			if len(self.points) > 0:
				color = L_GREEN

				if self.target:
					color = GREEN

				if self.marker:
					color = PINK

			pygame.draw.rect(surface, color, (self.left, self.top, self.width, self.height))

			for p in self.points:
				pygame.draw.rect(surface, RED, (p.x, p.y, 2, 2))

	def insert(self, point):
		# print('Inserting...')

		self.children_count += 1

		if self.divided:
			self.sub_insert(point)
		else:
			self.points.append(point)

			if len(self.points) >= self.max_size:
				# print('Dividing')

				self.divided = True

				self.marker = False

				self.upper_left  = QuadTree(self.left,   self.top,   self.h_width,              self.h_height,               self.max_size * 2)
				self.upper_right = QuadTree(self.h_left, self.top,   self.width - self.h_width, self.h_height,               self.max_size * 2)
				self.lower_left  = QuadTree(self.left,   self.h_top, self.h_width,              self.height - self.h_height, self.max_size * 2)
				self.lower_right = QuadTree(self.h_left, self.h_top, self.width - self.h_width, self.height - self.h_height, self.max_size * 2)

				for p in self.points:
					self.sub_insert(p)

				self.points = None

		# print('Done')

	def sub_insert(self, point):
		# print('Sub Inserting...')

		x = point.x
		y = point.y

		if x >= self.h_left:
			if y >= self.h_top:
				# print('lower_right')
				self.lower_right.insert(point)
			else:
				# print('upper_right')
				self.upper_right.insert(point)
		else:
			if y >= self.h_top:
				# print('lower_left')
				self.lower_left.insert(point)
			else:
				# print('upper_left')
				self.upper_left.insert(point)

	def verify(self):
		throw_up = []

		if self.divided:
			points = []
			points += self.lower_right.verify()
			points += self.upper_right.verify()
			points += self.lower_left.verify()
			points += self.upper_left.verify()

			for p in points:
				if self.inbounds(p):
					self.sub_insert(p)
				else:
					throw_up.append(p)

		else:
			points = self.points
			self.points = []

			for p in points:
				if self.inbounds(p):
					self.points.append(p)
				else:
					throw_up.append(p)

		self.children_count -= len(throw_up)

		if self.children_count == 0:
			if self.divided:
				# print('Undivide')

				self.divided = False

				self.upper_left  = None
				self.upper_right = None
				self.lower_left  = None
				self.lower_right = None

				self.points = []

				self.marker = True

		return throw_up

	def inbounds(self, point):
		x = point.x
		y = point.y

		return (self.left <= x < self.right) and (self.top <= y < self.bottom)

	def collide(self, left, top, width, height):
		self.target = False

		if rect_intersection(self.left, self.top, self.width, self.height, left, top, width, height):
			if self.divided:
				self.upper_left.collide(left, top, width, height)
				self.upper_right.collide(left, top, width, height)
				self.lower_left.collide(left, top, width, height)
				self.lower_right.collide(left, top, width, height)
			else:
				if len(self.points) > 0:
					self.target = True

	def collect(self):
		qt = 0

		if self.divided:
			qt += self.upper_left.collect()
			qt += self.upper_right.collect()
			qt += self.lower_left.collect()
			qt += self.lower_right.collect()
		else:
			if self.target:
				qt += len(self.points)

		self.target = False

		return qt

quad = QuadTree(0, 0, WIDTH, HEIGHT)
points = []

for i in range(10):
	border = i * 50
	for _ in range(10):
		p = Point(random.randint(border, WIDTH - border), random.randint(border, HEIGHT - border))
		points.append(p)
		quad.insert(p)

screen  = pygame.display.set_mode((WIDTH, HEIGHT))
clock   = pygame.time.Clock()
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			p = Point(*pygame.mouse.get_pos())
			points.append(p)
			quad.insert(p)

	screen.fill(WHITE)

	mx, my = mpos = pygame.mouse.get_pos()
	radius = 50

	for p in points:
		p.step()

	thup = quad.verify()

	quad.collide(mx - radius, my - radius, 2*radius, 2*radius)

	quad.draw(screen)

	qt = quad.collect()

	print(qt)

	for p in thup:
		if p.x < 0 or WIDTH <= p.x:
			p.vx *= -1
			px = min(WIDTH - 1, max(p.x, 0))
		if p.y < 0 or HEIGHT <= p.y:
			p.vy *= -1
			py = min(HEIGHT - 1, max(p.y, 0))

		quad.insert(p)

	pygame.display.flip()

	clock.tick(60)