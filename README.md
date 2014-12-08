Snake3D
=======

Un script python pour un snake en 3D dans un cube LED (jusqu'à 9x9x9)
Le code génère une matrice comprennant des valeurs suivantes 0 (éteint), 1 (rouge), 2 (bleu) ou 3 (violet)

Installation
=======

Il faut pour cela installer `pylibftdi` comme suivant :

#### Sous Debian et dérivés :

    sudo apt-get install python-pip libftdi-dev python-tk
    sudo pip install pylibftdi
    sudo nano /etc/udev/rules.d/99-libftdi.rules
    
Et y coller :

    SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", GROUP="dialout", MODE="0660"
    SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", GROUP="dialout", MODE="0660"

#### Sous Archlinux :

    sudo pacman -S libftdi python-pip tk
    sudo pip install pylibftdi
    sudo nano /etc/udev/rules.d/99-libftdi.rules
    
Et y coller :

    SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", GROUP="dialout", MODE="0660"
    SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", GROUP="dialout", MODE="0660"
