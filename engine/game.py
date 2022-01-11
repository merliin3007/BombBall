import sys
from os import system
from keyboard import is_pressed
from pyghthouse import Pyghthouse  # Paket "pyghthouse" muss installiert sein, das erfordert Python 3.9
from pyghthouse.ph import VerbosityLevel
from time import sleep, time
from enum import Enum
from queue import Queue

from engine.canvas import Canvas
from engine.lightsource import LightSource
from engine.overlay import OverlayLayer
from engine.render_layer import GameLayer, RenderLayer
from engine.render_object import Circle, Pawn, RenderObject, Terrain
from engine.shader import GlobalShaderSettings, SkyShader
from engine.text_rendering import CharRenderObject, ShrinkTextLayer, HorizontalScrollTextLayer
from engine.camera import Camera
from engine.utility import TerminalColors, pure_virtual
from engine.texture import Texture
from engine.sprite import Sprite

from engine.settings import USERNAME
from engine.settings import API_TOKEN
from engine.settings import FRAMERATE
from engine.settings import RESOLUTION_X
from engine.settings import RESOLUTION_Y
from engine.settings import SUPERSAMPLING
from engine.settings import ASPECT
from engine.settings import LIMIT_FRAMERATE
from engine.settings import SHOW_FRAMERATE
from engine.settings import CACHE_CANVAS
from engine.settings import PLATFORM
from engine.settings import PLATFORM_VERSION

class Event(Enum):
    Exit = 0
    Jump = 1
    MoveLeft = 2
    MoveRight = 3

"""
Game Class
    Enthält das gesamte Spiel.
"""
class Game:
    def __init__(self):
        self._background_color = [0, 128, 255]
        self._player: Pawn = None
        self._events = Queue()
        self.scaling_factor: float = 1.0 / (RESOLUTION_Y * SUPERSAMPLING)
        
        # Render Layers
        self.render_layers = []
        self._overlay_layer: OverlayLayer = OverlayLayer()
        
        # Pyghthouse
        self.p = Pyghthouse(USERNAME, API_TOKEN)
        Pyghthouse.start(self.p)

        self._camera = Camera()
        self.t = time()

        self._playback_speed: float = 1.0
        self._render_brightness: float = 1.0

        self._on_update = []

        # Time
        self._enable_day_night_cycle: bool = False
        self._time: float = 0.0
        self._day: int = 0
        self._day_night_cycle_speed: float = 1000.0

        # Sky
        self._sun: LightSource = None
        self._moon: LightSource = None
        self._sky_shader = SkyShader()
        self._day_sky_texture_sprite: Sprite = Sprite()
        self._night_sky_texture_sprite: Sprite = Sprite()
        self._day_sky_texture_sprite.set_position(0.5, 0.5)
        self._night_sky_texture_sprite.set_position(0.5, 0.5)


        # diagnose
        self.render_time: float = 0.0
        self.send_time: float = 0.0
        self.current_frame_rate: float = FRAMERATE

        self.render_time_avg: float = 0.0
        self.send_time_avg: float = 0.0
        self.current_frame_rate_avg: float = FRAMERATE

        self.render_time_max: float = 0.0
        self.send_time_max: float = 0.0
        self.current_frame_rate_min: float = FRAMERATE

        self.possible_framerate_avg: float = FRAMERATE

        self.t = time()

        self._canvas = Canvas(RESOLUTION_X, RESOLUTION_Y, SUPERSAMPLING, ASPECT, [0, 128, 255])

        self.show_title: bool = False
        self._title_layer: RenderLayer = ShrinkTextLayer('SAMPLE GAME')
        self._title_layer.repeat = False

        self._text_layer: RenderLayer = ShrinkTextLayer('')
        self._text_layer.repeat = False
        self._text_layer_pause_game: bool = False

        self.info_text: str = '' # Wird nur angezegt, wenn SHOW_FRAMERATE == True
        

    """
    start
        startet das Spiel
    """
    def start(self):
        # Eigener Loop scheint besonders bei schlechter Internetverbindung zuverlässiger als die Callback Funktion
        i = 0.0
        while(True):
            begin = time()
            frame: list = self.gameloop_callback()
            self.render_time =  time() - begin
            begin2 = time()
            self.p.set_image(frame)
            self.send_time = time() - begin2

            # Mit Escape das Spiel beenden
            if is_pressed('Esc'): break

            self.render_time_avg = (self.render_time_avg + self.render_time) / 2.0
            self.send_time_avg = (self.send_time_avg + self.send_time) / 2.0
            self.current_frame_rate_avg = (self.current_frame_rate_avg + self.current_frame_rate) / 2.0

            self.render_time_max = max(self.render_time_max, self.render_time)
            self.send_time_max = max(self.send_time_max, self.send_time)
            self.current_frame_rate_avg = min(self.current_frame_rate_min, self.current_frame_rate)

            i += self.render_time + self.send_time
            if i >= 1.0 and SHOW_FRAMERATE:
                i = 0.0
                system('cls')
                print(f'{PLATFORM} {PLATFORM_VERSION}')
                print('----------------------------------------------')
                print(f'{TerminalColors.ENDC}render_time_avg: {self.render_time_avg}')
                print(f'send_time_avg: {self.send_time_avg}')
                print(f'frame_rate_avg: {self.current_frame_rate_avg}')
                print('----------------------------------------------')
                print(f'render_time_max: {self.render_time_max}')
                print(f'send_time_max: {self.send_time_max}')
                print(f'frame_rate_min: {self.current_frame_rate_min}')
                print('----------------------------------------------')
                print_color = TerminalColors.CYAN
                if self.possible_framerate_avg < 25:
                    print_color = TerminalColors.FAIL
                elif self.possible_framerate_avg < 30:
                    print_color = TerminalColors.WARNING
                elif self.possible_framerate_avg >= 59:
                    print_color = TerminalColors.GREEN
                print(f'{print_color}possible_frame_rate_avg: {self.possible_framerate_avg}')
                print(f'{TerminalColors.ENDC}----------------------------------------------')

                self.render_time_avg = self.render_time
                self.send_time_avg = self.send_time
                self.current_frame_rate_avg = self.current_frame_rate

                self.render_time_max = self.render_time
                self.send_time_max = self.send_time
                self.current_frame_rate_min = self.current_frame_rate

            if LIMIT_FRAMERATE:
                complete_render_time = time() - begin
                if complete_render_time < 1.0 / FRAMERATE:
                    self.possible_framerate_avg = (self.possible_framerate_avg + (1.0 / complete_render_time)) / 2.0
                    sleep((1.0 / FRAMERATE) - complete_render_time)
                else:
                    self.possible_framerate_avg = self.current_frame_rate_avg

            self.current_frame_rate = 1.0 / (time() - begin)
        sys.exit(0)

    """
    display_text
        Zeigt während des Spiels Text an.
    
    Args:
        text(str): Der anzuzeigende Text
    """
    def display_text(self, text: str, pause_game: bool = False):
        self._text_layer.set_text(text)
        self._text_layer.is_playing = True
        self._text_layer_pause_game = pause_game

    """
    get_empty_canvas
        
    Returns:
        Ein leeres Canvas mit den aktuellen Einstellungen
    """
    def get_empty_canvas(self):
        return Canvas(RESOLUTION_X, RESOLUTION_Y, SUPERSAMPLING, ASPECT, self._background_color)

    """
    add_render_layer
        Fügt einen RenderLayer hinzu

        Args:
            render_layer(RenderLayer): der hinzuzufügende RenderLayer
    """
    def add_render_layer(self, render_layer: RenderLayer):
        self.render_layers.append(render_layer)

    """
    call_event
        Löst ein Event aus, das durch den gameloop verarbeitet wird
        -> MUSS THREADSAVE SEIN.

        Args:
            event(Event): das auszulösender Event
            params(list): die Parameter des Events (Noch nicht implementiert)
    """
    def call_event(self, event: Event, params = None):
        self._events.put(event)

    """
    gameloop_callback
        wird FRAMERATE mal pro Sekunde aufgerufen.

        Returns
            canvas.to_array(): Der nächste gerenderte Frame als Array in passendem Format fürs lighthouse
    """
    def gameloop_callback(self):
        delta_time: float = time() - self.t
        self.t = time()

        # Events
        while not self._events.empty():
            event = self._events.get()
            if event == Event.Exit:
                self.p.close()
        
        # Input
        self._player.is_moving_left = is_pressed('a')
        self._player.is_moving_right = is_pressed('d')
        self._player.is_jumping = is_pressed('w')
        
        # Update
        self._update(delta_time)

        # Render
        canvas = self._render()

        end_time = time()
        
        # output
        return canvas.to_array()

    """
    _update
        Ruft die Update-Prozeduren jeder Componenten auf.

        Args
            delta_time(float): die vergangene Zeit, seit dem die Prozedur das letzte mal aufgerufen wurde
    """
    def _update(self, delta_time: float):
        # title screen
        if self.show_title == True:
            if self._title_layer.is_playing == True:
                self._title_layer.update(delta_time)
                return

        # text layer
        if self._text_layer.is_playing == True:
            self._text_layer.update(delta_time)
            if self._text_layer_pause_game: return
    
        # time
        self._time += delta_time * self._day_night_cycle_speed
        if self._time >= 24 * 60 * 60:
            self._time -= 24 * 60 * 60
            self._day += 1
        
        # day night cylce
        if self._enable_day_night_cycle:
            brightness: float = 0.0
            if self._time < (24 * 60 * 60) / 2.0:
                brightness = self._time / ((24 * 60 * 60) / 2.0)
            else:
                brightness = -self._time / ((24 * 60 * 60) / 2.0) + 2.0
                #print(GlobalShaderSettings.light_brightness)
            GlobalShaderSettings.light_brightness = min(1.0, brightness)
            sun_position: float = -(self._time) / ((24 * 60 * 60) / 4.0) + 4.0
            moon_position: float = -(self._time + 12 * 60 * 60) / ((24 * 60 * 60) / 4.0) + 4.0
            # sun
            if self._sun != None:
                self._sun.set_position(0.5, sun_position) 
            # moon
            if self._moon != None:
                self._moon.set_position(0.5, moon_position)
            # sky textures
            self._day_sky_texture_sprite.opacity = GlobalShaderSettings.light_brightness
            self._night_sky_texture_sprite.opacity = 1.0 - GlobalShaderSettings.light_brightness
                

        # update game components
        self._camera.update(delta_time)
        for render_layer in self.render_layers:
            if type(render_layer) == GameLayer:
                self._camera.transform_game_layer(render_layer)
            render_layer.update(delta_time)

        # Call OnUpdate Event (kann weg)
        for f in self._on_update:
            f(self, delta_time)

        self.on_update(delta_time)

        self._overlay_layer.update(delta_time)

    """
    on_update
        Eine Funktion, die beim Update aufgerufen wird.
    """
    @pure_virtual
    def on_update(self, delta_time: float):
        pass

    """
    _render
        Rendert die momentante Szene

    Returns:
        canvas(Canvas): Das Canvas, auf dem die Szene gerendert wurde
    """
    def _render(self) -> Canvas:
        if CACHE_CANVAS:
            canvas = self._canvas
            self._canvas.reset()
        else:
            canvas = Canvas(RESOLUTION_X, RESOLUTION_Y, SUPERSAMPLING, ASPECT, [0, 128, 255])

        # title Screen
        if self.show_title == True:
            if self._title_layer.is_playing == True:
                self._title_layer.render(canvas)
                return canvas
        
        canvas.brightness = self._render_brightness
        # render sky texture
        canvas.reset_view_translation()
        canvas.zoom = self._camera.zoom
        if self._day_sky_texture_sprite.opacity != 0.0:
            self._day_sky_texture_sprite.draw(canvas)
        if self._night_sky_texture_sprite.opacity != 0.0:
            self._night_sky_texture_sprite.draw(canvas)
        # render normal renderlayers
        for render_layer in self.render_layers:
            render_layer.render(canvas)
        canvas.reset_view_translation()
        canvas.zoom = 1.0
        # render sfx
        for lightsource in canvas.lightsources:
            lightsource: LightSource = lightsource
            if lightsource.brightness != 0:
                lightsource.draw_bloom(canvas)
        # render overlay
        self._overlay_layer.render(canvas)
        # render text
        if self._text_layer.is_playing:
            self._text_layer.render(canvas)
        return canvas

    # GETTERS / SETTERS

    """
    on_update_subscribe
        Übergibt eine Funktion, die beim Event 'OnUpdate'
        aufgerufen wird.

    Args:
        f(function): Die Funktion muss die Paramter sender(Game) und delta_time(float) aktzeptieren
    """
    def on_update_subscribe(self, f):
        self._on_update.append(f)

    # Properties

    """
    player:
        Ruft den Pawn, der aktuell als Spieler festgelegt ist ab, oder legt diesen Fest
    """
    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player: Pawn):
        self._player = player

    """
    camera:
        Ruft die aktuelle Kamera ab, oder legt diese fest.
    """
    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, camera: Camera):
        self._camera = camera

    """
    overlay_layer
    """
    @property
    def overlay_layer(self) -> OverlayLayer:
        return self._overlay_layer

    """
    playback_speed
    """
    @property
    def playback_speed(self) -> float:
        return self._playback_speed

    @playback_speed.setter
    def playback_speed(self, value: float):
        self._playback_speed = max(0.0, value)

    """
    render_brightness
    """
    @property
    def render_brightness(self) -> float:
        return self._render_brightness

    @render_brightness.setter
    def render_brightness(self, value: float):
        self._render_brightness = max(0.0, value)
    
    """
    enable_day_night_cycle (bool)
    """
    @property
    def enable_day_night_cycle(self) -> bool:
        return self._enable_day_night_cycle

    @enable_day_night_cycle.setter
    def enable_day_night_cycle(self, value: bool):
        self._enable_day_night_cycle = value

    """
    time
        Gibt die virtuelle Tageszeit in Sekunden an, oder legt diese fest
    """
    @property
    def time(self) -> float:
        return self._time

    @time.setter
    def time(self, value: float):
        self._time = min(24 * 60 * 60, value)

    """
    sun
        Legt eine LightSource als Sonne fest, oder ruft diese ab
    """
    @property
    def sun(self) -> LightSource:
        return self._sun

    @sun.setter
    def sun(self, lightsource: LightSource):
        self._sun = lightsource

    """
    moon
        Legt eine LightSource als Mond fest, oder ruft dies ab
    """
    @property
    def moon(self) -> LightSource:
        return self._moon

    @moon.setter
    def moon(self, lightsource: LightSource):
        self._moon = lightsource

    """
    day_sky_texture
        Legt eine Textur für den Tageshimmel fest oder ruft diese ab.
    """
    @property
    def day_sky_texture(self) -> Texture:
        return self._day_sky_texture_sprite.texture
    
    @day_sky_texture.setter
    def day_sky_texture(self, tex: Texture):
        self._day_sky_texture_sprite.texture = tex

    """
    night_sky_texture
        Legt eine Textur für den Nachthimmel fest oder ruft diese ab.
    """
    @property
    def night_sky_texture(self) -> Texture:
        return self._night_sky_texture_sprite.texture
    
    @night_sky_texture.setter
    def night_sky_texture(self, tex: Texture):
        self._night_sky_texture_sprite.texture = tex

    """
    title
        Legt den Titel des Spiels fest, oder ruft diesen ab
    """
    @property
    def title(self) -> str:
        self._title_layer: ShrinkTextLayer = self._title_layer
        return self._title_layer.text

    @title.setter
    def title(self, value: str):
        self._title_layer: ShrinkTextLayer = self._title_layer
        self._title_layer.set_text(value)
