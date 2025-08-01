# odb/modules/orientation.py
"""
orientation.py –Madgwick 6‑DOF quaternion à partir des mesures du module «mpu».

•Ne lit **pas** directement l’I2C: on récupère les valeurs gyro/acc
  déjà fournies par le module Mpu6050 pour respecter votre découplage.
•Renvoie un dictionnaire:  { 'quat_x', 'quat_y', 'quat_z', 'quat_w' }
  qui sera immédiatement sérialisé par telemetry.py (JSON/CBOR/MAVLink).

Dépendances à déposer dans odb/lib:
    fusion.py   (https://github.com/tuupola/micropython-fusion)
    deltat.py   (fichier compagnon de fusion.py)
"""

import time
import math
from odb.modules import Module
from odb.lib.fusion import Fusion     # copie locale du filtre Madgwick

_GRAVITY = 9.80665                   # pour normaliser l'accéléro

class Orientation(Module):
    name = 'quat'                    # clé visible dans la télémétrie

    # --- paramètres «publics» du module --------------------------------
    def __init__(self, waiting_time=0):
        """
        waiting_time en ms: délai minimum avant un nouveau calcul.
        0 = calcule à chaque tour de boucle (recommandé; c’est léger).
        """
        self.waiting_time = waiting_time / 1000   # stocké en secondes
        self._next_due   = 0                      # timestamp du prochain update
        self._fusion     = Fusion()               # Madgwick 6‑DOF
        self._fusion.sample_rate = 100            # Hz (valeur par défaut)
        self.ready       = False
        self._q_ref      = None

    # ---------------------------------------------------------------------
    # Les trois méthodes que votre scheduler connaît déjà
    # ---------------------------------------------------------------------
    def during_bootup(self):
        """Aucun matériel à initialiser directement, juste OK‑flag."""
        self.ready = True

    def before_handle(self, data=None):
        """On ne fait que marquer l'instant – identique aux autres modules."""
        self._now = time.time()
        return self._now

    def handle(self, data=None):
        """
        data provient du scheduler et contient déjà les clés 'gyro_x' etc.
        On calcule le quaternion et on le remet dans le flux.
        """
        # cadence contrôlée?
        if self._now < self._next_due:
            return None                 # trop tôt, on laisse tomber

        try:
            gx = data['gyro_x']; gy = data['gyro_y']; gz = data['gyro_z']
            ax = data['acc_x'];  ay = data['acc_y'];  az = data['acc_z']
        except (TypeError, KeyError):
            # Si le module «mpu» n’a pas encore alimenté le dict,
            # on ne renvoie rien pour cette itération.
            return None

        # normaliser l'accéléro (le filtre attend 1 g)
        ax_n, ay_n, az_n = ax / _GRAVITY, ay / _GRAVITY, az / _GRAVITY
        gx, gy, gz = map(math.degrees, (gx, gy, gz))
        # Madgwick 6-DOF  (accel d’abord, gyro ensuite)
        self._fusion.update_nomag((ax_n, ay_n, az_n), (gx, gy, gz))
        self._next_due = self._now + self.waiting_time

        # ─── quaternion relatif ──────────────────────────────────────
        w, x, y, z = self._fusion.q  # (w,x,y,z) absolu

        # initialisation ou reset
        if self._q_ref is None:
            self._q_ref = (w, x, y, z)

        w0, x0, y0, z0 = self._q_ref  # conjugué(q_ref)
        # Hamilton product  q_rel = q_ref* ⊗ q
        qw = w0 * w - x0 * x - y0 * y - z0 * z
        qx = w0 * x + x0 * w + y0 * z - z0 * y
        qy = w0 * y - x0 * z + y0 * w + z0 * x
        qz = w0 * z + x0 * y - y0 * x + z0 * w

        # normalisation de sûreté
        norm = (qw * qw + qx * qx + qy * qy + qz * qz) ** 0.5
        qw, qx, qy, qz = (qw / norm, qx / norm, qy / norm, qz / norm)

        return {
            "quat_x": qx,
            "quat_y": qy,
            "quat_z": qz,
            "quat_w": qw
        }

    # ───────────────────────── API publique ──────────────────────────
    def reset_orientation(self):
        """À appeler depuis nrf24, CLI, etc. pour recaler le ‘0’."""
        self._q_ref = None
"""
        # Normalisation de l'accéléro (le filtre attend ~1g)
        ax_n = ax / _GRAVITY
        ay_n = ay / _GRAVITY
        az_n = az / _GRAVITY

        # Mise à jour Madgwick – gyro en °/s, acc en g
        self._fusion.update_nomag((gx, gy, gz), (ax_n, ay_n, az_n))

        # Stocke l’instant du prochain calcul
        self._next_due = self._now + self.waiting_time

        # Renvoie le dictionnaire à fusionner dans la télémétrie
        qw, qx, qy, qz = self._fusion.q           # (w,x,y,z)
        return {
            'quat_x': qx,
            'quat_y': qy,
            'quat_z': qz,
            'quat_w': qw
        }
"""