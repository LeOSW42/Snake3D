#!/usr/bin/env python # -*- coding: utf8 -*-

# Bibliothèques pour ftdi, calculs et gestion du temps
import sys
from math import *
from pylibftdi import Device
from collections import deque
from random import randint
from time import sleep

# Bibliothèque pour interface graphique
try:
	# for Python2
	from Tkinter import *
except ImportError:
	# for Python3
	from tkinter import *

# Dimension du cube XxXxX (maximum 9)
dimension = 8
# Quitter le programme
perdu = 0
# On place notre snake au bon endroit
snake = deque([[3,3,3],[3,4,3],[3,5,3]])
champi = deque([2,1,1])
#         x y z
# Avec y vers le haut, x vers la droite et z vers l'arrière
# Direction de départ
direction = 'left'
# Matrice des leds a allumer
matrice_leds = []
for i in range(dimension*dimension):
	matrice_leds.append([0] * dimension)

##############################################################
# Fonction de Robin pour envoyer la matrice au ftdi

def Envoyer():
	global dimension
	global matrice_leds
	
	octets_rouges=[]				
	octets_bleus=[]
	for k in range(dimension):
		octets_rouges.append([0] * dimension)
		octets_bleus.append([0] * dimension)		

	for k in range(dimension):	
		# Indice pour chaque PIC
		for i in range(dimension) :
			# Indice pour chaque diode d'une ligne (= d'un PIC)
			for j in range(dimension) :
				
				if i%2==0 and (j//4)%2==1:
					l=1
					c=-4
				elif i%2==1 and (j//4)%2==0:
					l=-1
					c=4
				else:
					l=0
					c=0
				
				if  matrice_leds[i+l+8*k][j+c] == 1:
					octets_rouges[k][i] = octets_rouges[k][i]+2**j

				elif matrice_leds[i+l+8*k][j+c] == 2:                
					octets_bleus[k][i] = octets_bleus[k][i]+2**j

				elif matrice_leds[i+l+8*k][j+c] == 3:
					octets_rouges[k][i] = octets_rouges[k][i]+2**j
					octets_bleus[k][i] = octets_bleus[k][i]+2**j

	try:
		# On envoie la sauce !
		with Device (mode = 't') as dev:
			dev.baudrate = 115200

			# 8 étages
			for k in range(dimension) :
				# 8 PICs = 8 lignes bicolores
				for i in range (dimension) :
					dev.write(chr(octets_bleus[k][i]))
					dev.write(chr(octets_rouges[k][i]))
	except Exception:	
		#if envoiState:
		#	Envoyer_Trame()
		print('FTDI non détecté')

##############################################################
# Fonction pour actualiser le cube

def ActualiserCube():
	global snake
	global matrice_leds
	global dimension
	global champi
	global perdu
	
	# Si on a perdu on quitte
	if (perdu==1):
		Mafenetre.destroy()
	
	queue = [0,0,0]
	# On met en cache la queue du snake (pour pouvoir l'agrandir)
	queue[0] = snake[len(snake)-1][0]
	queue[1] = snake[len(snake)-1][1]
	queue[2] = snake[len(snake)-1][2]
	
	if(perdu != 1):
		# On raccourcit le corps du snake
		snake.rotate(1)
		
		# On bouge la tête dans le bon sens
		if direction == 'up':
			snake[0][0] = snake[1][0]
			snake[0][1] = snake[1][1] + 1
			snake[0][2] = snake[1][2]
		elif direction == 'down':
			snake[0][0] = snake[1][0]
			snake[0][1] = snake[1][1] - 1
			snake[0][2] = snake[1][2]
		elif direction == 'left':
			snake[0][0] = snake[1][0] - 1
			snake[0][1] = snake[1][1]
			snake[0][2] = snake[1][2]
		elif direction == 'right':
			snake[0][0] = snake[1][0] + 1
			snake[0][1] = snake[1][1]
			snake[0][2] = snake[1][2]
		elif direction == 'back':
			snake[0][0] = snake[1][0]
			snake[0][1] = snake[1][1]
			snake[0][2] = snake[1][2] + 1
		elif direction == 'front':
			snake[0][0] = snake[1][0]
			snake[0][1] = snake[1][1]
			snake[0][2] = snake[1][2] - 1



	# Gestion des erreurs
	if(perdu != 1 and (snake[0][0] < 0 or snake[0][1] < 0 or snake[0][2] < 0 or snake[0][0] > dimension-1 or snake[0][1] > dimension-1 or snake[0][2] > dimension-1)):
		perdu = 1
		snake.rotate(-1)
		snake[len(snake)-1] = [queue[0],queue[1],queue[2]]

	for i in range(1,len(snake)):
		if(snake[0][0] == snake[i][0] and snake[0][1] == snake[i][1] and snake[0][2] == snake[i][2]):
			perdu = 1

	# Si on a bouffé le champignon
	if(snake[0][0] == champi[0] and snake[0][1] == champi[1] and snake[0][2] == champi[2]):
		champi[0] = randint(0, dimension-1)
		champi[1] = randint(0, dimension-1)
		champi[2] = randint(0, dimension-1)
		snake.append([queue[0],queue[1],queue[2]])
		Entete.config(text="Niveau : %s" %(len(snake)-3))
		

	# On efface la matrice	
	matrice_leds = []

	# On génère la matrice
	# Uniquement des zéros dans un premier temps
	for i in range(dimension*dimension):
		matrice_leds.append([0] * dimension)
	# On met des 1 pour le snake
	for i in range(len(snake)):
		ligne = "%s%s" %(dimension-1-snake[i][1],dimension-1-snake[i][2]) # On concatene nos deux valeurs
		result = 0
		place = 1
		# On passe la valeur dans la bonne dimension
		for j in range (len (ligne)):
			result += int (ligne[j]) * place
			place *= dimension
		ligne = result
		if (i==0):
			matrice_leds[ligne][snake[i][0]] = 3 # La tête en violet
		elif perdu!=1:
			matrice_leds[ligne][snake[i][0]] = 2 # le corps en bleu
		else:
			matrice_leds[ligne][snake[i][0]] = 1 # le corps en rouge
			
	ligne = "%s%s" %(dimension-1-champi[1],dimension-1-champi[2]) # On concatene nos deux valeurs
	result = 0
	place = 1
	# On passe la valeur dans la bonne dimension
	for j in range (len (ligne)):
		result += int (ligne[j]) * place
		place *= dimension
	ligne = result
	matrice_leds[ligne][champi[0]] = 1
	
	# On balance la sauce
	Envoyer()
	
	Mafenetre.after(100,ActualiserCube)

##############################################################
# Gestion des touches utilisées

def Touche(event):
	global direction
	
	# On récupère la touche pressée
	touche = event.keysym
	if (touche=='x'): # On quitte la boucle si on presse x
		Mafenetre.destroy()
	# On update la direction
	elif (touche=='Up' and direction != 'down'):
		direction = 'up'
	elif (touche=='Down' and direction != 'up'):
		direction = 'down'
	elif (touche=='Left' and direction != 'right'):
		direction = 'left'
	elif (touche=='Right' and direction != 'left'):
		direction = 'right'
	elif (touche=='a' and direction != 'front'):
		direction = 'back'
	elif (touche=='q' and direction != 'back'):
		direction = 'front'

#####################################################################################################
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
#####################################################################################################
# Création de la fenêtre principale
Mafenetre = Tk()
Mafenetre.title('Snake 3D')

# Image centrale
ImgDirections = Canvas(Mafenetre, width=216, height=216)
ImgDirections.grid(row=1, column=1)
jpgImgDirections = PhotoImage(file="directions.png")
ImgDirections.create_image(0, 0, image=jpgImgDirections, anchor=NW)

Entete = Label(Mafenetre, text="Niveau : %s" %(len(snake)-3))
Entete.grid(row=0, column=1)

# La méthode bind() permet de lier un événement avec une fonction :
# un appui sur une touche du clavier provoquera l'appel de la fonction utilisateur Touche()
Mafenetre.bind('<Key>', Touche)
# La c'est pour appeler l'actualisation du cube
Mafenetre.after(0,ActualiserCube)
Mafenetre.mainloop()
