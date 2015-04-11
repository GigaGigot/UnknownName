#!/usr/bin/env python
# coding: utf-8

import sys, pygame
import os
import time
from pygame.locals import *
import random
import thread
import math

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


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
	def __init__(self, nom, vitesse, poids, rotation):
		self.nom = nom
		self.vitesse = vitesse
		self.poids = poids
		self.rotation = rotation


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
		self.image = rotater(self.image, self.element.rotation * self.element.vitesse)
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

	# Images
	background_image, background_rect = load_png('Background/bg1.png')
	sol_image, sol_rect = load_png('Decor/sol.png')

	# Move_ip
	sol_rect.move_ip(0, 540)

	# Zone de test
	jade.ajouterElement(Element('feu', 20.0, 1.0, 1.0))
	jade.ajouterElement(Element('glace', 10.0, 0.5, 1.0))
	jade.ajouterElement(Element('foudre', 15.0, 0.0, 2.0))
	jade.ajouterElement(Element('roche', 5.0, 1.0, 1.0))

	while True:
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				raise SystemExit
			if event.type == pygame.MOUSEBUTTONUP:
				x, y = event.pos
				for element in jade.liste_elements:
					direction = calculDirection(jade.rect.centerx, jade.rect.centery, x, y)
					tir = Tir(element, jade.rect.centerx, jade.rect.centery, direction)
					tir_sprite.add(tir)

		# Check colisions
		checkColisionTirSol(sol_rect, tir_sprite)

		# Updatage
		tir_sprite.update()

		# Blitage
		screen.blit(background_image, background_rect)
		screen.blit(sol_image, [sol_rect[0], sol_rect[1] - 20])

		# Drawage
		jade_sprite.draw(screen)
		tir_sprite.draw(screen)

		# Infos
		#newFont, posFont = createFont(None,40,"Nombre d'elements : "+str(len(tir_sprite)),(0,0,0),(0,0))
		#screen.blit(newFont, posFont)


		pygame.display.flip()


if __name__ == '__main__':
	main_function()
	sys.exit(0)
