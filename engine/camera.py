from engine.render_layer import GameLayer
from engine.render_object import Pawn
from engine.utility import floatcmp

from math import sin

class Camera:
    def __init__(self):
        self._position_x = 0.0
        self._position_y = 0.0
        
        self._follow = None
        self._is_parallax = True
        self._follow_speed = 2.5

        # Camera Shake
        self._enable_shake: bool = False
        self._shake_strength = 0.001
        self._shake_speed = 1.0
        self._shake_time = 0.0
        self._current_shake_offset_x = 0.0
        self._current_shake_offset_y = 0.0
        self._fade_out_shake: bool = False
        self._shake_fade_out_speed: float = 0.1

        # Scene Params
        self._scene_max_x = 10000#1.3
        self._scene_min_x = -10000#-1.3

        self._follow_y = False
        self._follow_speed_y = 0.5
        self._scene_max_y = 10000
        self._scene_min_y = -10000

        self.zoom: float = 1.0
        self._aimed_zoom: float = 1.0
        self._zoom_speed: float = 0.1

    """
    move
        Bewegt die Kamera
    
    Args:
        dir_x(float): Die Menge, um die die Kamera auf der X-Achse bewegt werden soll.
        dir_y(float): die Menge, um die die Kamera auf der Y-Achse bewegt werden soll.
    """
    def move(self, dir_x: float, dir_y: float):
        self._position_x += dir_x
        self._position_y += dir_y

    """
    follow
        Setzt einen Pawn, dem die Kamera fortan folgen soll.

    Args:
        pawn(Pawn): Der Pawn, dem die Kamera folgen soll
    """
    def follow(self, pawn: Pawn):
        self._follow = pawn

    """
    update
        updated die Kamera

    Args:
        delta_time(float): Die vergangenen Zeit seit dem letzten Aufruf der Prozedur
    """
    def update(self, delta_time: float):
        #update zoom
        if self.zoom != self._aimed_zoom:
            self.zoom += self._zoom_speed * (self._aimed_zoom - self.zoom)
            if floatcmp(self.zoom, self._aimed_zoom, 0.0001):
                self.zoom = self._aimed_zoom
                
        # update follow
        if self._follow != None:
            self._update_follow(delta_time)

        # update shake
        self._update_shake(delta_time)

    """ 
    transform_game_layer
        Verschiebt den zu rendernden Ausschnitt eines GameLayers entsprechen der momentanen Kameraeinstellung

    Args:
        layer(GameLayer): der GameLayer, dessen Renderausschnitt verschoben werden soll
    """
    def transform_game_layer(self, layer: GameLayer):
        position_x: float = self._position_x + self._current_shake_offset_x
        position_y: float = self._position_y + self._current_shake_offset_y
        if not self._is_parallax:
            layer.set_view_translation(position_x, position_y)
        else:
            factor: float = 1.0 / layer.get_z_index()
            layer.set_view_translation(position_x * factor, position_y * factor)

    """
    fade_out_shake
        Blendet den Camerashake aus

    Args:
        fade_speed(float): Die Übergangsgeschwindigkeit
    """
    def fade_out_shake(self, fade_speed: float):
        self._shake_fade_out_speed = fade_speed
        self._fade_out_shake = True

    """
    earthquake
        Erdbeben lol
    """
    def earthquake(self, strength: float, shake_speed: float, duration: float):
        self._enable_shake = True
        self._shake_strength = strength
        self._shake_speed = shake_speed
        self._shake_time = 0.0
        self.fade_out_shake(1.0 / duration)

    """
    zoom_smooth
        Zoomed mit ein beliebigen Geschwindigkeit auf einen bestimmten Faktor

    Args:
        zoom(float): Die gewünschte Zoomstufe
        zoom_speed(float): Die Zoom-Geschwindigkeit
    """
    def zoom_smooth(self, zoom: float, zoom_speed: float = 0.1):
        self._zoom_speed = zoom_speed
        self._aimed_zoom = zoom


    """
    _update_follow
        Updatet die Kameraposition, um einem Pawn zu folgen (sofern ein Pawn zum folgen eingestellt ist)

    Args:
        delta_time(float): die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist.
    """
    def _update_follow(self, delta_time: float):
        # x
        player_x: float = self._follow.position_x
        #view_center_x: float = self._position_x + 0.5
        center_offset = (1.0 / self.zoom) / 2.0
        view_center_x: float = self._position_x + center_offset
        if floatcmp(player_x, view_center_x, 0.00001):
            return
        dir: float = -1.0 if player_x < view_center_x else 1.0
        border_diff: float = abs(view_center_x - self._scene_min_x) if dir == -1.0 else abs(view_center_x - self._scene_max_x)
        self.move(dir * abs(player_x - view_center_x) * self._follow_speed * delta_time, 0.0)

        # y
        if self._follow_y:
            player_y: float = self._follow.position_y
            #view_center_y: float = self._position_y + 0.5
            view_center_y: float = self._position_y + center_offset
            if floatcmp(player_y, view_center_y, 0.00001):
                return
            dir: float = -1.0 if player_y < view_center_y else 1.0
            border_diff: float = abs(view_center_y - self._scene_min_y) if dir == -1.0 else abs(view_center_y - self._scene_max_y)
            self.move(0.0, dir * abs(player_y - view_center_y) * self._follow_speed_y * delta_time)

        # Hier fehlt noch was... (Kamera nicht über die größe des Levels hinausbewegen)

    """
    _update_shake
        Updated den Kamerashake, falls die Kamera wackeln soll.

    Args:
        delta_time(float): Die Zeit, die seit dem letzten Funktionsaufruf vergangen ist.
    """
    def _update_shake(self, delta_time: float):
        if not self._enable_shake:
            return
        self._shake_time += delta_time
        self._current_shake_offset_x = sin(self._shake_time * self._shake_speed) * self._shake_strength
        self._current_shake_offset_y = sin(self._shake_time * self._shake_speed) * self._shake_strength
        #self.move(sin(self._shake_time * self._shake_speed) * self._shake_strength, sin(self._shake_time * self._shake_speed) * self._shake_strength)

        if self._fade_out_shake:
            self._shake_strength -= self._shake_fade_out_speed * delta_time
            if self._shake_strength <= 0.0:
                self._shake_strength = 0.0
                self._fade_out_shake = False
                self.enable_shake = False


    # properties

    """
    enable_shake
        Gibt an, ob der Camerashake aktiviert ist, oder legt dies fest
    """
    @property
    def enable_shake(self) -> bool:
        return self._enable_shake

    @enable_shake.setter
    def enable_shake(self, value: bool):
        self._enable_shake = value
        if value == False:
            self._current_shake_offset_x = 0.0
            self._current_shake_offset_y = 0.0

    """
    shake_strength
        Gibt an, wie stark der Camerashake eingestellt ist, oder legt dies fest
    """
    @property
    def shake_strength(self) -> float:
        return self._shake_strength

    @shake_strength.setter
    def shake_strength(self, value: float):
        self._shake_strength = value

    """
    shake_speed
        Gibt an, wie schnell der Camerashake sein soll, oder legt dies fest
    """
    @property
    def shake_speed(self) -> float:
        return self._shake_speed

    @shake_speed.setter
    def shake_speed(self, value: float):
        self._shake_speed = value

    """
    position_x
        Gibt die X-Achsen Position der Kamera an, oder legt diese fest.
    """
    @property
    def position_x(self):
        return self._position_x

    @position_x.setter
    def position_x(self, value: float):
        self._position_x = value

    """
    position_y
        Gibt die Y-Achsen Position der Kamera an, oder legt diese fest.
    """
    @property
    def position_y(self):
        return self._position_y

    @position_y.setter
    def position_y(self, value: float):
        self._position_y = value