from enum import Enum
from os import system
import platform

"""
Login Daten für Pyghthouse
"""
USERNAME      = 'stu235271'
API_TOKEN     = 'API-TOK_5v4X-eSbe-rDER-F5o9-w6x3'

"""
Framerate Begrenzung
    Die Framerate sollte dringend limitert werden, 
    da eine sehr hohe Framerate sehr kleine Delta Zeiten 
    bedeutet und kleinere Delta Zeiten ungenauer sind.

    Ist LIMIT_FRAMERATE True, wird die Framerate auf
    FRAMERATE begrenzt.
"""
FRAMERATE       = 60
LIMIT_FRAMERATE = True

"""
Auflösung und andere Rendereinstellungen

SUPERSAMPLING(int): Die Rendermaße werden mit diesem Faktor multipliziert
                    und das Bild zur Ausgabe wieder auf die ursprüngliche
                    Auflösung runtergerechnet. 
                    Sehr rechenaufwändig, da SUPERSAMPING^2 mal so viele Pixel
                    gerendert werden.

ASPECT(float): Das Bild wird auf der X-Achse um diesen Faktor gestaucht, 
               um die Verzerrung durch die nicht-quadratischen Fenster und
               und nicht-gleichen Abstände übereinander und nebeneinander
               liegender Fenster auszugleichen.
               Wird durch vertikales Supersampling umgesetzt.
"""
RESOLUTION_X  = 28
RESOLUTION_Y  = 14
SUPERSAMPLING = 1   # Render resolution factor
ASPECT        = 2.4

"""
Licht und Shader

BLOOM_OFFRAME_RENDER_TRESHOLD(float): Gibt an, ab welcher Entfernung zwischen
                                      Bildrand und Lightsource-Rand kein Bloom
                                      mehr gerendert werden soll
                                      (0.0 = schnellste)
"""
BLOOM_OFFRAME_RENDER_TRESHOLD: float = 0.2

"""
Caching
"""
CACHE_CANVAS = True

"""
Diagnose Einstellungen
"""
SHOW_FRAMERATE = True

"""
Systeminformationen
"""
PLATFORM         = platform.system()
PLATFORM_VERSION = platform.release()