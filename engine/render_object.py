from re import X
from subprocess import PIPE

from keyboard import parse_hotkey_combinations
from engine.canvas import Canvas
#from engine.component import Component, PhysicsCompoment
from engine.drawing import draw_circle, draw_thick_line, draw_line
from engine.utility import Bounds, floatcmp, pure_virtual
from engine.shader import PixelShader

import math
from enum import Enum

M = 400.0
S = 0.0001

"""
RenderObject
    Alle renderbaren Objekte müssen hiervon erben.
"""
class RenderObject:
    def __init__(self):
        self._is_visible = True
        self._shader = None
        self._z_index: float = 1.0

    def update(self, delta_time: float):
        raise NotImplementedError()

    def draw(self, canvas: Canvas):
        raise NotImplementedError()

    # GETTERS / SETTERS

    def set_position(self, x: float, y: float):
        raise NotImplementedError()

    def get_bounds(self) -> Bounds:
        raise NotImplementedError()

    # properties

    """
    is_visible
        Gibt an, oder legt fest, ob das RenderObject sichtbar ist
    """
    @property
    def is_visible(self) -> bool:
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value: bool):
        self._is_visible = value

    """
    shader
        Gibt den Shader zurück, mit dem das RenderObject gerendert wird, oder legt diesen fest
    """
    @property
    def shader(self) -> PixelShader:
        return self._shader

    @shader.setter
    def shader(self, shader: PixelShader):
        self._shader = shader

    """
    z_index
        Gibt den Z-Index zurück
    """
    @property
    def z_index(self) -> float:
        return self._z_index


"""
Rectangle(RenderObject) Class
    Ein RenderObject, das als Rechteck gerendert wird
"""
class Rectangle(RenderObject):
    def __init__(self):
        super().__init__()
        pass

    def update(self, delta_time: float):
        pass

    def draw(self, canvas: Canvas):
        pass

"""
Circle(RenderObject) Class
    Ein RenderObject, das als Kreis gerendert wird
"""
class Circle(RenderObject):
    def __init__(self, color = [255, 0, 0], radius = 0.2, position_x = 0.0, position_y = 0.0):
        super().__init__()
        self._color = color
        self._radius = radius
        self.pos_x = position_x
        self.pos_y = position_y

    """
    [OVERRIDE] update
    
    Args:
        delta_time(float): Die vergangene Zeit seit dem letzten Aufruf der Prozedur.
    """
    def update(self, delta_time: float):
        pass

    """
    [OVERRIDE] draw
        Zeichnet das RenderObject auf ein Canvas

    Args:
        canvas(Canvas): Das Canvas, auf das der Kreis gezeichnet werden soll
    """
    def draw(self, canvas: Canvas):
        pixel_radius: int = canvas.relative_distance_to_pixel_distance(self._radius)
        #draw_circle(canvas, 10 * canvas.supersampling, self.pos_x, self.pos_y, self._color)
        x, y = canvas.get_pixel_position_undistorted(self.pos_x, self.pos_y)
        draw_circle(canvas, pixel_radius, x, y, self._color)
        pass

    # GETTERS / SETTERS

    """
    set_color
        Setzt die Farbe des Kreises

    Args:
        color(list): Die Farbe ([r,g,b])
    """
    def set_color(self, color: list):
        self._color = color

    """
    set_radius 
        Legt den Radius des Kreises fest

    Args:
        radius(float): Der Radius des Kreises
    """
    def set_radius(self, radius: float):
        self._radius = radius

    """
    [OVERRIDE] set_position
        Legt die Position des Kreises fest

    Args:
        x(float): Die X-Koordinate des Kreismittelpunktes (Relativ)
        y(float): Die Y-Koordinate des Kreismittelpunktes (Relativ)
    """
    def set_position(self, x: float, y: float):
        self.pos_x = x
        self.pos_y = y

    """
    [OVERRIDE] get_bounds
        Gibt die Maße des RenderObjects zurück

    Returns:
        (Bounds): Die Maße des RenderObjects
    """
    def get_height(self) -> float:
        return Bounds(self._radius * 2, self._radius * 2)

"""
Pawn(RenderObject) Class
    Ein RenderObject, das einen Player, eine KI oder ähnliches darstellt.
    Auch Objekte, mit denen der Player agieren kann, wie Projektile
    können über ein Pawn realisiert werden.
"""
class Pawn(RenderObject):
    def __init__(self, max_health: float = 100.0):
        super().__init__()

        self._components: list = []

        self._velocity_x: float = 0.0
        self._velocity_y: float = 0.0
        self._velocity_max: float = 10.0 * M * S
        self._velocity_min: float = 1.0 * S
        self._acceleration: float = 3.5 * M * S
        self._drag: float = 0.87
        self._gravity: float = 4.0 * M 
        self._max_falling_speed: float = 15.0 * M * S

        self._jump_power: float = 0.1

        self.is_moving_left = False
        self.is_moving_right = False
        self.is_jumping = False

        self._position_x: float = 0.5
        self._position_y: float = 1.0

        self._is_in_air: bool = True

        self._health: float = max_health
        self._max_health: float = max_health
        
        self.circle = Circle() # Kann weg, braucht keiner mehr

        self._render_object: RenderObject = None
        pass

    """
    [OVERRIDE] update
        Updated den Pawn

    Args:
        delta_time(float): Die vergangene Zeit seit dem letzten Aufruf der Prozedur
    """
    def update(self, delta_time: float):
        self._update_physics(delta_time)
        self._update_movement(delta_time)
        if self._render_object != None:
            self._render_object.update(delta_time)

        self.on_update(delta_time)

    """
    [OVERRIDE] draw
        Zeichnet den Pawn auf ein Canvas

    Args:
        canvas(Canvas): Das Canvas, auf das der Pawn gezeichnet werden soll
    """
    def draw(self, canvas: Canvas):
        if self._render_object == None:
            return
        #x, y = canvas.get_pixel_position_undistorted(self.position_x, self.position_y)
        #self.circle.pos_x = x
        #self.circle.pos_y = y
        #draw_circle(canvas, 2 * canvas.supersampling, x, y, [255, 0, 0])
        self._render_object.shader = self.shader
        self._render_object.set_position(self.position_x, self.position_y)
        self._render_object.draw(canvas)

    """
    [OVERRIDE] get_bounds
        Gibt die Maße des RenderObjects zurück

    Returns:
        (Bounds): Die Maße des RenderObjects
    """
    def get_bounds(self) -> Bounds:
        if self._render_object == None:
            return Bounds(0.0, 0.0)
        return self._render_object.get_bounds()

    """
    move
        Bewegt den Pawn
    
    Args:
        dir_x(float): Die Menge, um die der Pawn auf der X-Achse verschoben werden soll
        dir_y(float): Die Menge, um die der Pawn auf der Y-Achse verschoben werden soll
    """
    def move(self, dir_x: float, dir_y: float):
        self.position_x += dir_x
        self.position_y += dir_y

    """
    walk
        Beschleunigt (unter Berücksichtigung der Physics) den Pawn auf der X-Achse

    Args:
        dir_x(float): Die Menge, um die der Pawn beschleunigt werden soll
    """
    def walk(self, dir_x: float):
        # acceleration
        self._velocity_x += dir_x * self._acceleration
        # limit velocity
        if abs(self._velocity_x) > self._velocity_max:
            self._velocity_x = self._velocity_max * (-1.0 if self._velocity_x < 0.0 else 1.0)

    """
    jump
        Lässt den Pawn springen
    """
    def jump(self):
        #if self._velocity_y > 0.0:
        #    return
        if self._is_in_air:
            return
        self._velocity_y = self._jump_power

    """
    reset_velocity_y
        Setzt die Momentane Geschwindigkeit des Pawns entlang der Y-Achse auf 0.0 zurück
    """
    def reset_velocity_y(self):
        self._velocity_y = 0.0

    """
    throw
        Lasst den Pawn einen anderen Pawn 'werfen'.

    Args:
        object(Pawn): Der Pawn, der geworfen werden soll.
        dir_x(float): Die X-Achsen Richtung und Stärke, in die der Pawn geworfen werden soll
        dir_y(float): Die Y-Achsen Richtung und Stärke, in die der Pawn geworfen werden soll
    """
    def throw(self, object: 'Pawn', dir_x: float, dir_y: float = 1.0):
        object.position_x = self.position_x
        object.position_y = self.position_y
        object.velocity_x = dir_x
        object.velocity_y = dir_y

    """
    receive_damage
        Zieht dem Pawn Lebenspunkte ab.

    Args:
        damage(float): Der Schaden, den der Pawn nehmen soll.
    """
    def receive_damage(self, damage: float):
        if self._health == 0.0: return
        self._health -= damage
        self._health = max(0.0, self._health)
        self.on_damage_received(damage)
        if self._health == 0.0:
            self.on_died()

    """
    _update_movement
        Updateted die Bewegung des Pawns

    Args:
        delta_time(float): Die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist
    """
    def _update_movement(self, delta_time: float):
        if self.is_moving_left:
            self.walk(-delta_time)
        elif self.is_moving_right:
            self.walk(delta_time)
        if self.is_jumping:
            self.jump()

    """
    _update_physics
        Updated die Physics
    
    Args:
        delta_time(float): Die Zeit, die seit dem letzten Aufruf der Prozedur vergangen ist
    """
    def _update_physics(self, delta_time: float):
        # Gravity
        self._velocity_y -= S * self._gravity * delta_time
        # Limit falling Speed
        if self._velocity_y > self._max_falling_speed:
            self._gravity = self._max_falling_speed
        # Deceleration
        self._velocity_x *= self._drag
        self._velocity_y *= self._drag
        # Limit deceleration (Prevent endless deceleration)
        if abs(self._velocity_x) < self._velocity_min:
            self._velocity_x = 0.0
        if abs(self._velocity_y) < self._velocity_min:
            self._velocity_y = 0.0
        
        self.move(self._velocity_x, self._velocity_y)

    """
    on_update
        Eine Funktion, die beim Update aufgerufen wird.
    """
    @pure_virtual
    def on_update(self, delta_time: float):
        pass

    """
    on_pawn_collision
    """
    @pure_virtual
    def on_pawn_collision(self, pawn: 'Pawn'):
        pass

    """
    on_damage_received
    """
    @pure_virtual
    def on_damage_received(self, damage: float):
        pass

    """
    on_died
        Wir aufgerufen, wenn der Pawn gestorben ist
    """
    @pure_virtual
    def on_died(self):
        pass

    # Properties

    """
    render_object
        Gibt das Object zurück, als das der Pawn gerendert wird, oder legt dieses fest.
    """
    @property
    def render_object(self):
        return self._render_object

    @render_object.setter
    def render_object(self, object):
        self._render_object = object

    """
    is_in_air
        Gibt an oder legt fest, ob der Pawn gerade in der Luft schwebt.
    """
    @property
    def is_in_air(self):
        return self._is_in_air

    @is_in_air.setter
    def is_in_air(self, value: bool):
        self._is_in_air = value

    """
    position_x
        Gibt die X-Achsen Position des Pawns an oder legt diese fest
    """
    @property
    def position_x(self):
        return self._position_x

    @position_x.setter
    def position_x(self, value: float):
        self._position_x = value

    """
    position_y
        Gibt die Y-Achsen Position des Pawns an oder legt diese fest
    """
    @property
    def position_y(self):
        return self._position_y

    @position_y.setter
    def position_y(self, value: float):
        self._position_y = value

    """
    velocity_x
        Gibt die X-Achsen Geschwindigkeit, mit der sich der Pawn derzeit bewegt,
        an oder legt diese fest.
    """
    @property
    def velocity_x(self):
        return self._velocity_x

    @velocity_x.setter
    def velocity_x(self, value: float):
        self._velocity_x = value

    """
    velocity_y
        Gibt die Y-Achsen Geschwindigkeit, mit der sich der Pawn derzeit bewegt,
        an oder legt diese fest.
    """
    @property
    def velocity_y(self):
        return self._velocity_y

    @velocity_y.setter
    def velocity_y(self, value: float):
        self._velocity_y = value

    """
    max_velocity
        Gibt die Maximale X-Achsen Geschwindigkeit des Pawns an oder legt diese fest.
    """
    @property
    def velocity_max(self) -> float:
        return self._velocity_max / M / S

    @velocity_max.setter
    def velocity_max(self, value: float):
        self._velocity_max = value * M * S

    """
    health
    """
    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, value: float):
        self._health = value

    """
    max_health
    """
    @property
    def max_health(self) -> float:
        return self._max_health

    @max_health.setter
    def max_health(self, value: float):
        self._max_health = value
        self._health = min(self._health, self._max_health)

    """
    is_dead
    """
    @property
    def is_dead(self) -> bool:
        return self._health == 0.0

    """
    [OVERRIDE ]shader
    """
    @property
    def shader(self) -> PixelShader:
        return self._shader

    @shader.setter
    def shader(self, value: PixelShader):
        self._shader = value
        if self._render_object == None:
            return
        self._render_object.shader = value


"""
Foliage Object
"""
class FoliageObject():
    def __init__(self, render_object: RenderObject, frequency: float, offset: float):
        super().__init__()

        self.render_object: RenderObject = render_object
        self.frequency: float = frequency
        self.offset: float = offset

    def render(self, canvas: Canvas, range_begin: float, range_end: float, terrain_gen_func):
        for i in range(int(range_begin * self.frequency) - 1, int(range_end * self.frequency) + 1):
            self.render_object.set_position((i / self.frequency) + self.offset, terrain_gen_func(i / self.frequency) + (self.render_object.get_bounds().height / 2.0))
            self.render_object.draw(canvas)


"""
Terrain(RenderObject) Class
    Eine Landschaft.
"""
class Terrain(RenderObject):
    def __init__(self, color_grass: list = [0, 255, 0], seed: list = [1.0], max_terrain_height = 0.1):
        super().__init__()

        self.__seed = [1.23, 4.23, 57.4]
        self.__color_grass = [0, 255, 0]
        self.__color_dirt = [100, 60, 0]
        self._max_terrain_height = 0.1

        self.__color_grass = color_grass
        self.__seed = seed
        self._max_terrain_height = max_terrain_height

        self._single_foliage_render_objects = []
        self._single_foliage_render_distance = 1.0
        self._foliage_render_objects = []

    """
    [OVERRIDE] update
    
    Args:
        delta_time(float): Die vergangene Zeit seit dem letzten Aufruf der Prozedur.
    """
    def update(self, delta_time: float):
        for foliage_object in self._single_foliage_render_objects:
            foliage_object.update(delta_time)
        for foliage_object in self._foliage_render_objects:
            foliage_object: FoliageObject = foliage_object
            foliage_object.render_object.update(delta_time)

    """
    [OVERRIDE] draw
        Zeichnet die Landschaft auf ein Canvas

    Args:
        canvas(Canvas): Das Canvas, auf das gezeichnet werden soll
    """
    def draw(self, canvas: Canvas):
        # Draw Landscape
        for i in range(canvas.pixel_width):
            x,y = canvas.from_pixel_position_undistorted(i, 0)
            #y = math.sin(x) * self._max_terrain_height + 0.5
            y = self.terrain_gen_func(x)
            b,c = canvas.get_pixel_position_undistorted(0, y)
            for j in range(c, canvas.pixel_height):
                #canvas[i,j] = self.__color_grass
                canvas[i,j] = self._shader.process_pixel(i, j, self.__color_grass)
                
        # Draw Singular Foliage
        for foliage_object in self._single_foliage_render_objects:
            foliage_object: RenderObject = foliage_object
            # Only Draw if is in range
            position_x: float = foliage_object.get_bounds().position_x
            begin_x, y = canvas.from_pixel_position_undistorted(0, 0)
            end_x, y = canvas.from_pixel_position_undistorted(canvas.pixel_width, 0)
            if position_x < begin_x - self._single_foliage_render_distance or position_x > end_x + self._single_foliage_render_distance:
                continue
            # Draw
            foliage_object.draw(canvas)

        # Draw Foliage
        for foliage_object in self._foliage_render_objects:
            foliage_object: FoliageObject = foliage_object
            begin_x,begin_y = canvas.from_pixel_position_undistorted(0, 0)
            end_x,end_y = canvas.from_pixel_position_undistorted(canvas.pixel_width, 0)
            foliage_object.render(canvas, begin_x - self._single_foliage_render_distance, end_x + self._single_foliage_render_distance, self.get_surface_height)

    """
    get_surface_height
        Gibt die Höhe der Obefläche an einer bestimmten Stelle zurück

    Args:
        x(float): Die Stelle, deren Oberflächenhöhe zurückgegeben wird
    """
    def get_surface_height(self, x: float):
        return self.terrain_gen_func(x)

    """
    add_singe_foliage
        Fügt ein einzelnes RenderObject an einer einzelnen Stelle auf die Landschaft

    Args:
        foliage_object(RenderObject): Das hinzuzufügende RenderObject
        position_x(float): Die X-Achsen Position
    """
    def add_single_foliage(self, foliage_object: RenderObject, position_x: float):
        foliage_object.set_position(position_x, self.get_surface_height(position_x) + (foliage_object.get_bounds().height / 2.0))
        self._single_foliage_render_objects.append(foliage_object)

        # eigenen Shader festlegen, falls das RenderObject keinen eigenen Shader hat
        if foliage_object.shader == None:
            from engine.lightsource import LightSource
            if type(foliage_object) == LightSource:
                pass
            else:
                foliage_object.shader = self.shader

    """
    add_foliage
        Fügt ein RenderObject als Foliage hinzu, das auf der ganzen Landschaft
        verteilt immer wieder auftritt.

    Args:
        foliage_object(RenderObject): Das hinzuzufügende RenderObject
        frequency(float): Die Häufigkeit, mit der das RenderObject auftreten soll
    """
    def add_foliage(self, render_object: RenderObject, frequency: float, offset: float = 0.0):
        self._foliage_render_objects.append(FoliageObject(render_object, frequency, offset))

        # eigenen Shader festlegen, falls das RenderObject keinen eigenen Shader hat
        if render_object.shader == None:
            from engine.lightsource import LightSource
            if type(render_object) == LightSource:
                pass
            else:
                render_object.shader = self.shader

    """
    terrain_gen_func
        Die Funktion, die das Terrain generiert
        TODO: statt sinuskurven zu addieren, perlin noise verwenden

    Args:
        x(float): Die X-Koordinate, an der das Terrain abgetastet werden soll
    """
    def terrain_gen_func(self, x: float):
        y = 0.0
        for i in range(len(self.__seed)):
            y += (1.0 / (i + 1.0)) * math.sin(x * self.__seed[i])
        return (y / len(self.__seed)) * self._max_terrain_height + 0.3 # 0.5
