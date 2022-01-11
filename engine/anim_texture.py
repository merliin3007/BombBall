from typing import Text
from engine.texture import Texture
from engine.canvas import Canvas
from engine.utility import overrides

import os
import math

"""
AnimTexture (Texture)
    Stellt eine animierte Textur dar.
"""
class AnimTexture(Texture):
    def __init__(self, framerate: int = 5, size: float = 1.0):
        #super().__init__()
        self._framerate: int = framerate
        self._frames: list = []
        self._size = 1.0
        self._is_playing: bool = True
        self._repeat: bool = False

        self._current_frame_index: int = -1
        self._time_since_last_frame_switch: float = 0.0

        self._load_next_frame()

    """
    add_frame
        Fügt der Animation ein Frame hinzu

    Args:
        frame(Texture): Der hinzuzufügende Frame
    """
    def add_frame(self, frame: Texture):
        self._frames.append(frame)

    """
    add_frame_from_file
        Lädt eine Textur aus einer Datei und fügt der Animation
        diese als Frame hinzu.

    Args:
        filepath(str): Der Dateipfad
    """
    def add_frame_from_file(self, filepath: str):
        texture = Texture()
        texture.load_from_file(filepath, self._size)
        self.add_frame(texture)

    """
    load_multiple_frames_from_files
        Lädt mehrere Frames aus Datein

    Args:
        filepaths(list): Liste mit den entsprechenden Dateipfaden
    """
    def load_multiple_frames_from_files(self, filepaths: list):
        for filepath in filepaths:
            assert(type(filepath == str))
            self.add_frame_from_file(filepath)

    def load_multiple_frames_from_directory(self, dirpath: str):
        # TODO: implement
        pass

    """
    play
        Spielt die Animation ab.
    """
    def play(self):
        self._is_playing = True
        self._load_next_frame()

    """
    stop
        Beendet die Animation.
    """
    def stop(self):
        self._is_playing = False

    """
    clone
        Cloned NUR den aktuellen Frame der Animation.
    """
    def clone(self):
        return self._frames[self._current_frame_index].clone()

    """
    clone_rescaled
        Cloned NUR den aktuellen Frame der Animation und skalliert die Pixeldaten dabei neu

    Args:
        new_pixel_width(int): Die neue Breite der Textur in Pixeln
    """
    def clone_rescaled(self, new_pixel_width: int) -> 'Texture':
        return self._frames[self._current_frame_index].clone_rescaled(new_pixel_width)

    """
    _load_next_frame
        Lädt den nächsten Frame

    Args:
        frames_diff(int): 0 = aktueller Frame nochmal, 1 = nächster Frame, sonst x frames weiter
    """
    def _load_next_frame(self, frames_diff: int = 1):
        if (len(self._frames) == 0):
            return
        if self._repeat:
            self._current_frame_index = (self._current_frame_index + frames_diff) % len(self._frames)
        else:
            self._current_frame_index += frames_diff
            if self._current_frame_index >= len(self._frames):
                self._current_frame_index: int = -1
                self._is_playing = False
        current_frame_texture: Texture = self._frames[self._current_frame_index]
        current_frame_texture.size = self._size
        

    """
    __getitem__
        Gibt die Farbwerte eines bestimmten Pixels des aktuellen Frames zurück
    """
    @overrides(Texture)
    def __getitem__(self, index):
        current_frame_texture: Texture = self._frames[self._current_frame_index]
        return current_frame_texture.__getitem__(index)

    """
    calc_render_dimensions
        Berechnet die Rendermaße des Aktuellen Frames relativ zu einem Canvas

    Args:
        canvas(Canvas): Das Canvas, zu dem die Maße relativ sein sollen.
    """
    @overrides(Texture)
    def calc_render_dimensions(self, canvas: Canvas):
        current_frame_texture: Texture = self._frames[self._current_frame_index]
        current_frame_texture.calc_render_dimensions(canvas)

    """
    update
        Wird 1/FRAMERATE mal pro Sekunde aufgerufen

    Args:
        delta_time(float): Die vergangene Zeit seit dem letzten Aufruf der Prozedur
    """
    @overrides(Texture)
    def update(self, delta_time: float):
        if not self._is_playing:
            return
        self._time_since_last_frame_switch += delta_time
        frame_time: float = 1.0 / self._framerate
        frames_diff: int = math.floor(self._time_since_last_frame_switch / frame_time)
        #self._time_since_last_frame_switch -= frames_diff * frame_time
        if frames_diff > 0.0:
            self._time_since_last_frame_switch = 0.0
            #print(self._time_since_last_frame_switch)
            self._load_next_frame(frames_diff)

    """
    load_from_file
        Lädt einen weiteren Frame von einer Datei und fügt diesen zur Animation hinzu

    Args:
        filename(str): Der Dateiname der Textur
    """
    @overrides(Texture)
    def load_from_file(self, filename: str, relative_size_x: float):
        self.add_frame_from_file(filename)

    """
    load_from_json
        Lädt einen weiteren Frame aus einem JSON string und fügt diesen zur Animation hinzu

    Args:
        filename(str): Der Dateiname der Textur
    """
    @overrides(Texture)
    def load_from_json(self, json_text: str, relative_size_x: float):
        texture = Texture()
        texture.load_from_json(json_text, relative_size_x)
        self.add_frame(texture)

    # properties (Texture)

    """
    [OVERRIDE] pixel_width
        Gibt die Breite der Textur in Pixeln zurück
    """
    @property
    def pixel_width(self):
        current_frame_texture: Texture = self._frames[self._current_frame_index]
        if current_frame_texture == None:
            return 0
        return current_frame_texture.pixel_width

    """
    [OVERRIDE] pixel_height
        Gibt die Höhe der Textur in Pixeln zurück
    """
    @property
    def pixel_height(self):
        current_frame_texture: Texture = self._frames[self._current_frame_index]
        if current_frame_texture == None:
            return 0
        return current_frame_texture.pixel_height

    """
    [OVERRIDE] relative_size
        Gibt die aktuellen relativen Maße der Textur zurück.
    TODO: sollte in 'relative_dimensions' umbenannt werden, um Verwechslung mit 'size' zu vermeiden
    """
    @property
    def relative_size(self):
        current_frame_texture: Texture = self._frames[self._current_frame_index]
        if current_frame_texture == None:
            return 0, 0
        return current_frame_texture.relative_size

    """
    [OVERRIDE] size
        Gibt die relative Größe der Textur an oder legt diese fest.
    """
    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size_x: float):
        self._size = size_x
        current_frame_texture: Texture = self._frames[self._current_frame_index]
        if current_frame_texture == None:
            return
        current_frame_texture.size = size_x

    # Properties (Animation)

    """
    framerate
        Gibt die Framerate der Animation zurück oder legt diese fest.
    """
    @property
    def framerate(self) -> int:
        return self._framerate

    @framerate.setter
    def framerate(self, value: int):
        self._framerate = value

    """
    repeat
        Gibt an, ob sich die Animation wiederholt, oder nur einmal abgespielt wird.
    """
    @property
    def repeat(self) -> bool:
        return self._repeat

    @repeat.setter
    def repeat(self, value: bool):
        self._repeat = value
