#!/usr/bin/env python
# coding: utf-8

import sys, os, time, thread
import random, math
import pygame
from pygame.locals import *

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
os.environ['SDL_VIDEO_WINDOW_POS'] = "40,35"


def load_png(name):
	fullname=os.path.join('./Image/',name)
	try:
		image=pygame.image.load(fullname)
		if image.get_alpha is None:
			image=image.convert()
		else:
			image=image.convert_alpha()
	except pygame.error, message:
		print 'Probleme lors de la lecture de l\'image :', fullname
		raise SystemExit, message
	return image,image.get_rect()


# Creation de chaines de caractere affichables
def createFont(policeEcriture, taille, texte, couleur, position): 
	newFont = pygame.font.Font(policeEcriture, taille)
	newLabel = newFont.render(texte,1,couleur)
	return newLabel, position


def calculDirection(xA, yA, xB, yB):
	vx = xB-xA
	vy = yB-yA
	longueur = math.sqrt(math.pow(vx,2) + math.pow(vy,2))
	direction = [vx/longueur, vy/longueur]
	return direction


def rotater(image, angle):
	orig_rect = image.get_rect()
	rot_image = pygame.transform.rotate(image, angle)
	rot_rect = orig_rect.copy()
	rot_rect.center = rot_image.get_rect().center
	rot_image = rot_image.subsurface(rot_rect).copy()
	return rot_image


def checkColisionTirSol(sol_rect, tir_sprite):
	for sprite in tir_sprite.sprites():
		if sol_rect.colliderect(sprite.rect):
			sprite.kill()


def essaiSpawn(chance):
	rand = random.randint(1, chance)
	if rand == chance:
		cote = random.randint(1, 2)
		if cote == 1:
			return True, SCREEN_WIDTH + 180
		else:
			return True, -180
	else:
		return False, 0

def dommagesEffectues(touche):
	for tir in touche.keys():
		for mob in touche[tir]:
			mob.degatsPris(tir.element.degats)

def dessinerBarreDeVie(screen ,ennemi):
	x, y = ennemi.rect.bottomleft
	w = ennemi.rect.width
	vieB = ennemi.vieBase
	vieC = ennemi.vieRestante
	barre = pygame.draw.rect(screen, (0,0,0),(x, y, w, 5), 2)
	remplisage = pygame.draw.rect(screen, (124,124,124),(x+1, y+1, w-1, 4))
	vie = pygame.draw.rect(screen, (204,22,22),(x+1, y+1, (w-1) * ((vieB-(vieB-vieC))/vieB), 4))


# Jade (joueur)
class Jade(pygame.sprite.Sprite):    
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('Sprite/jade.png')
		self.rect.center = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]
		self.liste_elements = []

	def ajouterElement(self, element):
		self.liste_elements.append(element)


class Element():
	def __init__(self, nom, vitesse, poids, rotation, degats, intervalle):
		self.nom = nom
		self.vitesse = vitesse
		self.poids = poids
		self.rotation = rotation
		self.degats = degats
		self.intervalle = intervalle
		self.cpt_intervalle = 0

class Ennemi(pygame.sprite.Sprite):    
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('Sprite/sprite_demon1.png')
		self.cote = self.toFlipOrNotToFLip(x)
		self.rect.center = [x, y]
		# Attributs
		self.vieBase = 10
		self.vieRestante = 10
		self.vitesseBase = 1
		self.vitesseCourante = 1

	def toFlipOrNotToFLip(self, x):
		if x > SCREEN_WIDTH/2:
			self.image = pygame.transform.flip(self.image, True, False)
			return -1
		return 1

	def update(self, jade_rect, sol_rect):
		self.checkHorsLimite()
		if self.rect.right >= jade_rect.left and self.cote == 1:
			pass
		elif self.rect.left <= jade_rect.right and self.cote == -1:
			pass
		else:
			self.rect = self.rect.move(self.vitesseCourante * self.cote, 0)

		if self.rect.bottom >= sol_rect.top:
			pass
		else:
			self.rect = self.rect.move(0, self.vitesseCourante * 10)

	def checkHorsLimite(self):
		if(self.rect.top < -100 or self.rect.bottom > 720 or self.rect.left < -300 or self.rect.right > 1580):
			self.kill()

	def degatsPris(self, degats):
		self.vieRestante -= degats
		if self.vieRestante <= 0:
			self.vieRestante = 0
			self.kill()

class Tir(pygame.sprite.Sprite):
	def __init__(self, element, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('Sprite/'+element.nom+'.png')
		self.element = element
		self.rect.center = [x, y]
		self.direction = direction

	def update(self):
		self.checkHorsLimite()
		direction = [v * self.element.vitesse for v in self.direction]
		self.rect = self.rect.move(direction)
		self.image = rotater(self.image, self.element.rotation)
		self.direction[1] += (self.element.poids/20)

	def checkHorsLimite(self):
		if(self.rect.top < -1000 or self.rect.bottom > 720 or self.rect.left < -300 or self.rect.right > 1580):
			self.kill()


def main_function():
	
	# Initialisation
	pygame.init()
	pygame.display.set_caption("UN NOM PUTAIN")
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	clock = pygame.time.Clock()
	pygame.key.set_repeat(1,1)

	# Objets de classe
	jade = Jade()
	jade_sprite = pygame.sprite.RenderClear(jade)
	tir_sprite = pygame.sprite.RenderClear()
	ennemi_sprite = pygame.sprite.RenderClear()

	# Images
	background_image, background_rect = load_png('Background/bg1.png')
	sol_image, sol_rect = load_png('Decor/sol.png')

	# Move_ip
	sol_rect.move_ip(0, 540)

	# Zone de test
	jade.ajouterElement(Element('feu', 6.0, 0.2, 15.0, 4.0, 20.0))
	jade.ajouterElement(Element('foudre', 8.0, 0.0, 13.0, 2.0, 30.0))
	jade.ajouterElement(Element('glace', 4.0, 1.0, 11.0, 5.0, 90.0))
	jade.ajouterElement(Element('roche', 3.0, 0.5, 9.0, 6.0, 60.0))

	while True:
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				raise SystemExit
			if event.type == pygame.MOUSEBUTTONUP:
				x, y = event.pos
				for element in jade.liste_elements:
					if element.cpt_intervalle >= element.intervalle:
						element.cpt_intervalle = 0.0
						direction = calculDirection(jade.rect.centerx, jade.rect.centery, x, y)
						tir = Tir(element, jade.rect.centerx, jade.rect.centery, direction)
						tir_sprite.add(tir)

		# Check colisions
		checkColisionTirSol(sol_rect, tir_sprite)
		tirs_ennemis_touche = pygame.sprite.groupcollide(tir_sprite, ennemi_sprite, True, False, pygame.sprite.collide_circle_ratio(0.5))
		dommagesEffectues(tirs_ennemis_touche)

		# Spawn ennemis
		spawn, xPos = essaiSpawn(100)
		if spawn == True:
			ennemi = Ennemi(xPos, SCREEN_HEIGHT/2)
			ennemi_sprite.add(ennemi)

		# Updatage
		tir_sprite.update()
		ennemi_sprite.update(jade.rect, sol_rect)
		for element in jade.liste_elements:
					element.cpt_intervalle += 1.0

		# Blitage
		screen.blit(background_image, background_rect)
		screen.blit(sol_image, [sol_rect[0], sol_rect[1] - 20])

		# Drawage
		jade_sprite.draw(screen)
		tir_sprite.draw(screen)
		ennemi_sprite.draw(screen)
		for ennemi in ennemi_sprite:
			dessinerBarreDeVie(screen ,ennemi)

		# Infos
		#newFont, posFont = createFont(None,40,"Nombre d'elements : "+str(len(tir_sprite)),(0,0,0),(0,0))
		#screen.blit(newFont, posFont)


		pygame.display.flip()


if __name__ == '__main__':
	main_function()
	sys.exit(0)
