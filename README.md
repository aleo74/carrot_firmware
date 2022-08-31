# Carrot firmware
### Only french for now


Carrot firmware est un Ordinateur De Bord, pensé et développé pour facilement évoluer, se basant sur le microcontroller RP2040.

L'idée du programme, c'est de rendre accessible à moindre coût la construction d'un ODB, qu'il soit évolutif, et facile à programmer.

## Tech

[CircuitPython](https://circuitpython.org/)

## Plugins

Carrot Firmware s'agrémente avec des modules:

| Plugin      | README                                                                                     |
|-------------|--------------------------------------------------------------------------------------------|
| MPU 6050    | [Lire](https://github.com/aleo74/carrot_firmware/blob/main/modules/MPU_6050/README.md)     |
| GY-GPS6MV2  | [Lire](https://github.com/aleo74/carrot_firmware/blob/main/modules/GPS/README.md)          |
| NRF401      | en cours                                                                                   |
| SerilWriter | [Lire](https://github.com/aleo74/carrot_firmware/blob/main/modules/SerialWriter/README.md) |

## Extensions

Non pris en charge pour le moment.

## Installation

Suivre la procédure d'installation de circuitPython sur votre carte depuis le site adafruit.
Copier sur votre carte tout le contenu du dossier [carrot_firmware].
Dans le dossier [modules], récupérer ceux que vous mettrez dans votre montage.
Coller le fichier .py dans le dossier [modules] de votre carte.
Ajoutez dans le dossier [lib] la libraire du module installé.

Sur votre carte, dans le fichier code.py :
Ajoutez l'import du/des modules que vous utilisez.

Par exemple, pour ajouter le capteur MPU6050:
Dans les imports
```python
from odb.modules.mpu_6050 import Mpu6050
```

Initialisation du module
```python
mpu = Mpu6050(scl, sda)
```
Les paramètres scl et sda doivent être les pins de votre montage  :
```python
board.GPXX
```

Ajout du module dans l'odb
```python
Odb.modules = [mpu]
```

Pour ajouter plusieurs modules :
```python
Odb.modules = [mpu, module2, module3]
```

## Dévelopement

Vous voulez contribuer, ajouter un nouveau module, ou une nouvelle extension ?
Faite un pull request, en oubliant pas d'ajouter un README
