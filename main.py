import pygame
import random
import os
#from pygame.surfarray import array_alpha

#initialize
pygame.init()
clock = pygame.time.Clock()

#game variables
FPS = 60
GRAVITY = 0.5
MAX_PLATFORMS = 10
SCROLL_THRESH = 200
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0
difficulty = 0

if (os.path.exists('scoreboard.txt')):
	with open ('scoreboard.txt', 'r') as file:
		high_score = int(file.read())
else:
	high_score = 0

#window
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Jumper')

#load images
background_image = pygame.image.load('Assets/Background/1.png').convert_alpha()
player_image = pygame.image.load('Assets/Player/player.png').convert_alpha()
platform_image = pygame.image.load('Assets/Platform/brick.png').convert_alpha()

#colors
WHITE = (255, 255, 255)
BG = (52, 154, 254)
BLACK = (0, 0, 0, 100)
RED = (255, 0, 0)
GOLD = (255, 188, 0)
HOT_PINK = (255, 0, 230)

#fonts
small_font = pygame.font.SysFont("Calibri", 25)
big_font = pygame.font.SysFont("Calibri", 35)
panel_font = pygame.font.SysFont('Bahnschrift', 40)
small_panel_font = pygame.font.SysFont('Bahnschrift', 30)

def draw_text(text, font, color, x, y):
	image = font.render(text, True, color)
	screen.blit(image, (x, y))

def draw_panel():
	draw_shade(SCREEN_WIDTH, 60, 20, 0, 0)
	x = SCREEN_WIDTH // 2
	y = 0
	score_length = len(str(int(score))) * 8
	if (player.multiplier >= 4.9):
		x = random.randint(199, 201)
		y = random.randint(1, 3)
		if (player.multiplier >= 9.9):
			x = random.randint(198, 202)
			y = random.randint(0, 4)	
	#' x' + str(round(player.multiplier, 1)
	draw_text(str(int(score)), panel_font, BLACK, SCREEN_WIDTH // 2 - score_length, 3)
	draw_text(str(int(score)), panel_font, BLACK, SCREEN_WIDTH // 2 - score_length, 5)
	draw_text(str(int(score)), panel_font, WHITE, SCREEN_WIDTH // 2 - score_length, 0)
	if (player.multiplier >= 1.1):
		draw_text('x' + str(round(player.multiplier, 1)), small_panel_font, BLACK, x, y + 40)
		draw_text('x' + str(round(player.multiplier, 1)), small_panel_font, GOLD, x, y + 37)

def draw_shade(width, height, alpha, x, y):
	shade = pygame.Surface((width, height))			# the size of your rect
	shade.set_alpha(alpha)							# alpha level
	shade.fill((0, 0, 0))							# this fills the entire surface
	screen.blit(shade, (x, y))						# (0,0) are the top-left coordinates

def draw_bg(bg_scroll):
	screen.blit(background_image, (0, SCREEN_HEIGHT - background_image.get_height() + bg_scroll // 8))

#player class
class Player():
	def __init__(self, x, y):
		self.image = player_image
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.center = (x, y)
		self.movement_speed = 1
		self.vertical_velocity = 0
		self.momentum = 0
		self.direction = 1
		self.flip = False
		self.multiplier = 0.9

	def movement(self):
		scroll = 0
		dx = 0
		dy = 0

		#keyboard inputs
		key = pygame.key.get_pressed()
		if (key[pygame.K_LEFT]):
			self.direction = -1
			self.flip = False
			dx -= self.movement_speed + self.momentum
			if (self.momentum <= 4):
				self.momentum += 0.5

		elif (key[pygame.K_RIGHT]):
			self.direction = 1
			self.flip = True
			dx += self.movement_speed + self.momentum
			if (self.momentum <= 4):
				self.momentum += 0.5
		else:
			#if no keys are pressed, gradually lower the momentum
			if (self.momentum > 0):
				dx += (self.movement_speed * self.direction) + (self.momentum * self.direction)
				self.momentum -= 0.2

		#gravity
		self.vertical_velocity += GRAVITY
		dy += self.vertical_velocity

		#check for screen boundaries
		if (self.rect.right - 15 < 0):					#left
			self.rect.x = SCREEN_WIDTH - 15
		if (self.rect.left + 15 > SCREEN_WIDTH):		#right 
			self.rect.x = -15

		distance = dy #get distance traveled
		#check for platform collision
		for platform in platform_group:
			if (platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height)):
				if (self.rect.bottom < platform.rect.centery):
					if (self.vertical_velocity > 0):
						self.rect.bottom = platform.rect.top
						dy = 0
						self.vertical_velocity = int(-distance // 1.3)
						if (distance <= 15.5):
							self.vertical_velocity = -12
						self.image = pygame.transform.rotate(player_image, random.randint(0, 360)) #rotate the player every time he hits the platform
						self.multiplier += 0.1
						if (distance > 9):
							self.multiplier = 0.9
		#check for screen scrolling
		if (self.rect.top <= SCROLL_THRESH):
			if (self.vertical_velocity < 0):
				scroll = -dy
		self.rect.x += dx
		self.rect.y += dy + scroll
		return scroll

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, width, move):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(platform_image, (width, 10))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.momentum = 0
		self.width = width
		self.move = move
		self.move_counter = random.randint(0, 50)
		self.move_direction = random.choice([-1, 1])
		self.move_speed = random.randint(1, 2)

	def update(self, scroll):
		self.rect.y += scroll
		if (self.rect.top > SCREEN_HEIGHT):
			self.kill() #delete unseen platforms

		#platform shade
		draw_shade(self.width, 15, 50, self.rect.x, self.rect.y)

		#moving platforms
		if (self.move == True):
			self.move_counter += 1
			self.rect.x += self.move_direction * self.move_speed

		if (self.move_counter >= 200) or (self.rect.right > SCREEN_WIDTH) or (self.rect.left < 0):
			self.move_direction *= -1
			self.move_counter = 0

#groups		
platform_group = pygame.sprite.Group()

#instances
player = Player(250, 400)
platform = Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, False) #starting platform
platform_group.add(platform)

running = True
while (running):
	clock.tick(FPS)
	if (game_over == False):
		bg_scroll += scroll
		screen.fill(BG) #background color
		draw_bg(bg_scroll) #background
		
		scroll = player.movement()
		player.draw()

		#score
		if (scroll > 0):
			score += (int(scroll) // 5) * player.multiplier

		#difficulty
		difficulty += int(scroll) #difficulty increases as player goes higher
		if (len(platform_group) < MAX_PLATFORMS):
			platform_width = random.randint(80, 90)	- (difficulty // 900)	#platform width
			if (platform_width < 25):	
				platform_width = 25
			platform_x = random.randint(0, SCREEN_WIDTH - platform_width)	#platform x location
			platform_y = platform.rect.y - random.randint(80, 120)			#platform y location
			moving_platforms_cap = 10 - (difficulty - 10000) // 3000
			if (moving_platforms_cap < 3):
				moving_platforms_cap = 2
			platform_type = random.randint(1, moving_platforms_cap)
			if (platform_type == 1) and (difficulty >= 10000):
				platform_moving = True
			else:
				platform_moving = False
			platform = Platform(platform_x, platform_y, platform_width, platform_moving)
			platform_group.add(platform)
			
		platform_group.update(scroll)
		platform_group.draw(screen)
	
		draw_panel() #score and highscore panels

		#game over
		kill = pygame.key.get_pressed()
		if (player.rect.top > SCREEN_HEIGHT or kill[pygame.K_x]):
			game_over = True

	else:
		if (fade_counter < SCREEN_WIDTH):
			fade_counter += 5
			for y in range(0, 8, 2):
				pygame.draw.rect(screen, BLACK, (0, y * (SCREEN_HEIGHT / 8), fade_counter, SCREEN_HEIGHT / 8))
				pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * (SCREEN_HEIGHT / 8), SCREEN_WIDTH, SCREEN_HEIGHT / 6))
			#update highscore in file
			if (score > high_score):
				high_score = int(score)
				with open('scoreboard.txt', 'w') as file:
					file.write(str(high_score))
		else:
			draw_text('GAME OVER', big_font, WHITE, SCREEN_WIDTH // 2 - 70, 200)
			draw_text('SCORE: ' + str(int(score)), small_font, WHITE, SCREEN_WIDTH // 2 - 45, 250)
			draw_text('HIGHSCORE: ' + str(int(high_score)), small_font, WHITE, SCREEN_WIDTH // 2 - 90, 300)
			draw_text('PRESS SPACE TO PLAY AGAIN', small_font, WHITE, SCREEN_WIDTH // 2 - 130, 350)

			key = pygame.key.get_pressed()
			if (key[pygame.K_SPACE]):
				#reset everything
				difficulty = 0
				player.multiplier = 1
				fade_counter = 0
				game_over = False
				score = 0
				scroll = 0
				bg_scroll = 0
				player.vertical_velocity = -12
				player.rect.center = (250, 650)
				platform_group.empty()
				platform = Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, False) #starting platform
				platform_group.add(platform)

	#event handler
	for event in pygame.event.get():
		if (event.type == pygame.QUIT):
			running = False
	#update
	pygame.display.update()

pygame.quit()