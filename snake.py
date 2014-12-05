#!/usr/bin/env python # -*- coding: utf8 -*-

#######################################
#                                     # 
#    ###                              #
#   #   #   ###       #         #     #
#    ###    #  #      #         ##    #
#   #   #   ###   ##  ###   ##  #     #
#   #   #   # #  #  # #  # #  # #     #
#    ###    #  #  ##  ###   ##   ##   #
#                                     #
#######################################
#
# UN SNAKE POUR UN CUBE LED
#
# Dimensions maximales du cube : 9x9x9
# 
# Requis : python, python-tk, pylibftdi
#
# Fonctionnalités :
#    * Déplacement du snake
#    * Champignons aléatoires
#    * Détection erreurs (croquage queue et murs)
#    * Grandissement lors des miam champis
#    * Couleurs (champi rouge, tête violet, corps bleu (ou rouge si mort))
#    * Un mode pause (actif au lancement)
#
# Auteurs : Robin, Léo (et autres)


# ~~~~~~~~~~~~~~~~~~~ Bibliothèques ~~~~~~~~~~~~~~~~~~~

# Bibliothèques pour ftdi, calculs et gestion du temps
import sys
from math import *
from pylibftdi import Device
from collections import deque # Permet de faires des opérations avancés sur les listes (rotate)
from random import randint    # Permet de créer des chiffres aléatoires
from time import sleep

# Bibliothèque pour interface graphique
try:
	# for Python2
	from Tkinter import *
except ImportError:
	# for Python3
	from tkinter import *

# ~~~~~~~~~~~~~~~~~~~ Variables globales ~~~~~~~~~~~~~~~~~~~

# Taille du cube
dimension = 8
# Drapeau mis à un si perdu
perdu = 0
# Drapeau de pause du jeu
pause = 1
# Snake (avec initialisation sur un bord)
# 3 de long par défaut
snake = deque([[5,3,3],[6,3,3],[7,3,3]])
# Champignon du niveau 1 (FIXME : Pourrait être aléatoire)
champi = deque([2,1,1])
# Direction de départ
direction = 'left'
# Matrice des leds a allumer
matrice_leds = []
# Initialisation de la matrice de bonne taille avec des zéros (FIXME : Inutile)
for i in range(dimension*dimension):
	matrice_leds.append([0] * dimension)



##############################################################
# Fonction d'envoi la matrice au ftdi (Auteur : Robin)
# Nécessite la matrice_leds
##############################################################

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
# Fonction pour actualiser l'affichage du cube (Auteur : Léo)
# Renvoi matrice_leds en prennant en compte les positions du snake et des champis
##############################################################

def ActualiserCube():
	global snake
	global matrice_leds
	global dimension
	global champi
	global perdu
	global pause
	
	# Dans un premier temps, si le jeu est fini, quitter
	if (perdu==1):
		Mafenetre.destroy()
	
	# On met en cache la queue du snake (dernière case) pour pouvoir agrandir le snake si besoin est
	queue = [0,0,0]
	queue[0] = snake[len(snake)-1][0]
	queue[1] = snake[len(snake)-1][1]
	queue[2] = snake[len(snake)-1][2]
	
	# Si on a pas perdu, le snake doit avancer
	if(perdu != 1):
		# On raccourci le snake (la queue passe à la tête)
		# C'est une décalage à droite de la liste
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

	# Gestion des erreurs pouvant entrainer une défaite
	# Dans un premier temps, si on est encore en vie et que l'on rentre dans un mur
	if(perdu != 1 and (snake[0][0] < 0 or snake[0][1] < 0 or snake[0][2] < 0 or snake[0][0] > dimension-1 or snake[0][1] > dimension-1 or snake[0][2] > dimension-1)):
		# On passe le drapeu à 1
		perdu = 1
		# On fait reculer le snake pour anuler l'avancement qui n'as pas lieu d'être
		snake.rotate(-1)
		# On restitue la queue au snake (car elle a été effacée précédement)
		snake[len(snake)-1] = [queue[0],queue[1],queue[2]]
	# On teste ici si le snake mange sa queue
	# Pour chaque morceau de snake (tête exclue) on regarde si il n'est pas à la même position que la tête
	# FIXME : Est-ce que le snake peut vraiment manger la deuxième et troisième case
	for i in range(1,len(snake)):
		if(snake[0][0] == snake[i][0] and snake[0][1] == snake[i][1] and snake[0][2] == snake[i][2]):
			perdu = 1

	# Si le snake mange un champignon (si sa tête a la position d'un champignon)
	if(snake[0][0] == champi[0] and snake[0][1] == champi[1] and snake[0][2] == champi[2]):
		# On génère un champignon à une position aléatoire
		champi[0] = randint(0, dimension-1)
		champi[1] = randint(0, dimension-1)
		champi[2] = randint(0, dimension-1)
		# On rajoute une case à la liste du snake (l'ajout de fait à droite, donc à la queue)
		snake.append([queue[0],queue[1],queue[2]])
		# On actualise le niveau dans la fenêtre graphique
		Entete.config(text="Niveau : %s" %(len(snake)-3))
		
	# On efface la matrice	
	matrice_leds = []
	# On remplit la matrice avec le bon nombre de zéros
	for i in range(dimension*dimension):
		matrice_leds.append([0] * dimension)

	# On remplace les zéros si il y a des éléments à afficher
	# On s'occupe du snake dans un premier temps
	# Pour chaque case du snake
	for i in range(0,len(snake)):
		# Là c'est un calcul complexe, transformation de nos coordonnées x, y et z au x, plan zOy de Robin
		# Dans un premier temps, on inverse nos y et z, et on concatène nos deux valeurs
		ligne = "%s%s" %(dimension-1-snake[i][1],dimension-1-snake[i][2])
		# Ensuite, On passe d'une base 8 (si dimension = 8) à une base 10 (c'est une sorte de modulo)
		result = 0
		place = 1
		for j in range (len (ligne)):
			result += int (ligne[j]) * place
			place *= dimension
		# On a alors la ligne de la matrice_leds
		ligne = result
		# Si on est au premier point (la tête), on l'affiche en violet
		if (i==0):
			matrice_leds[ligne][snake[i][0]] = 3 # La tête en violet
		# Sinon, et si on est vivant, le corps en bleu
		elif perdu!=1:
			matrice_leds[ligne][snake[i][0]] = 2 # le corps en bleu
		# Enfin, si on est mort, le corps en rouge
		else:
			matrice_leds[ligne][snake[i][0]] = 1 # le corps en rouge
	
	# Même magouille de conversion pour les coordonnées du champignon
	# Concaténation de nos deux valeurs y et z
	ligne = "%s%s" %(dimension-1-champi[1],dimension-1-champi[2])
	# On passe dans la bonne base (notre espèce de modulo)
	result = 0
	place = 1
	for j in range (len (ligne)):
		result += int (ligne[j]) * place
		place *= dimension
	ligne = result
	# On affiche le champignon en rouge
	matrice_leds[ligne][champi[0]] = 1 # le champi en rouge
	
	# On balance la sauce !!!
	Envoyer()
	
	# On rapelle cette fonction dans 100 ms (raffraichissement du cube)
	# !!! Ne pas mettre zéro sinon les interruption du clavier ne pourront plus se lancer !!!
	# Seulement si on est pas en pause
	# FIXME : Un variable pour gérer la vitesse serait sympa
	if (pause != 1):
		Mafenetre.after(100,ActualiserCube)



##############################################################
# Fonction pour actualiser la direction en fonction de la touche pressée (Auteur : Léo)
# Empêche entre autre les demi tours sur place
##############################################################

def Touche(event):
	global direction
	global pause
	
	# On récupère la touche pressée
	touche = event.keysym
	# Si on presse x on quitte la fenêtre
	if (touche=='Escape'):
		Mafenetre.destroy()
	# Si on presse espace on se met en pause ou on en sort
	if (touche=='space'):
		if (pause == 1):
			pause = 0
			Mafenetre.after(250,ActualiserCube)
		else:
			pause = 1
	# Dans un cas autre, on actualise la direction
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

# ~~~~~~~~~~~~~~~~~~~ Fenêtre principale ~~~~~~~~~~~~~~~~~~~

Mafenetre = Tk()
Mafenetre.title('Snake 3D')

# On affiche l'image avec les contrôles
ImgDirections = Canvas(Mafenetre, width=216, height=216)
ImgDirections.grid(row=1, column=1)
jpgImgDirections = PhotoImage(file="directions.png")
ImgDirections.create_image(0, 0, image=jpgImgDirections, anchor=NW)

# On met une ligne au dessus avec le niveau indiqué
# FIXME : C'est toujours zéro au lancement, calcul inutile
Entete = Label(Mafenetre, text="Niveau : %s" %(len(snake)-3))
Entete.grid(row=0, column=1)
Commandes = Label(Mafenetre, text="Echap : Quitter le jeu\r\nSpace : Mode pause", justify=LEFT)
Commandes.grid(row=2, column=1)

# Un appui sur le clavier appelle la fonction Touche() qui actualisera la direction
Mafenetre.bind('<Key>', Touche)
# On appelle directement l'actualisation du cube, ce sera encuite bouclé dans la fonction
# Seulement si on est pas en pause
if (pause != 1):
	Mafenetre.after(250,ActualiserCube)
# On rentre dans le while 1 qui permet de tout faire tourner
Mafenetre.mainloop()
