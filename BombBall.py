from time import sleep, time
from engine.anim_texture import AnimTexture
from engine.camera import Camera
from engine.drawing import draw_circle
from engine.game import FRAMERATE, Game, Event
from engine.lightsource import LightSource
from engine.overlay import HealthBar
from engine.render_layer import GameLayer
from engine.render_object import Circle, RenderObject, Pawn, Terrain
from engine.canvas import Canvas
from engine.shader import NoShader, GlobalShaderSettings
from engine.sprite import Sprite
from engine.text_rendering import CharRenderObject
from engine.texture import Texture
from engine.utility import calculate_points_distance, overrides

import os
import keyboard
from random import randint, random

"""
Bomb
    Eine Bombe, die der Player werfen kann.
"""
class Bomb(Pawn):
    def __init__(self):
        super().__init__()
        self.init_textures()
        self.on_explode = None # Funktion
        self.is_currently_exploding: bool = False
        self.is_visible = False

        self.time_since_last_damage_cast: float = 0.0
        self.damage_cooldown: float = 0.1

        self.shader = NoShader()

    def init_textures(self):
        self.render_object: Sprite = Sprite()
        self.bomb_texture = Texture()
        self.bomb_texture.load_from_file(os.path.join('textures', 'bomb.mtex'), 0.2)
        self.render_object.texture = self.bomb_texture

        self.explosion_texture = AnimTexture()
        self.explosion_texture.framerate = 5
        self.explosion_texture.repeat = False
        self.explosion_texture.add_frame_from_file(os.path.join('textures', 'explosion', 'frame_1.mtex'))
        self.explosion_texture.add_frame_from_file(os.path.join('textures', 'explosion', 'frame_2.mtex'))
        self.explosion_texture.add_frame_from_file(os.path.join('textures', 'explosion', 'frame_3.mtex'))
        self.explosion_texture.add_frame_from_file(os.path.join('textures', 'explosion', 'frame_4.mtex'))
        self.explosion_texture.add_frame_from_file(os.path.join('textures', 'explosion', 'frame_5.mtex'))
        self.explosion_texture.size = 0.4

    def reset(self):
        self.is_currently_exploding = False
        self.init_textures()

    @overrides(Pawn)
    def on_update(self, delta_time: float):
        if not self.is_visible:
            return
        if self.is_in_air and not self.render_object.texture == self.bomb_texture:
            self.render_object.texture = self.bomb_texture
        elif not self.is_in_air and not self.render_object.texture == self.explosion_texture:
            self.render_object.texture = self.explosion_texture
            self.explosion_texture.play()
            self.is_currently_exploding = True
            self.on_explode()
            self.time_since_last_damage_cast = 0.0
        elif not self.is_in_air and not self.explosion_texture._is_playing:
            self.is_currently_exploding = False
            self.is_visible = False

        self.time_since_last_damage_cast += delta_time

    @overrides(Pawn)
    def on_pawn_collision(self, pawn: 'Pawn'):
        if not self.is_currently_exploding:
            return
        if not self.is_visible:
            return
        if self.time_since_last_damage_cast >= self.damage_cooldown:
            pawn.receive_damage(10.0)
            self.time_since_last_damage_cast = 0.0

"""
Enemy
    Ein Pawn, der den Player angreift
"""
class Enemy(Pawn):
    def __init__(self, bomb: Bomb):
        super().__init__()
        self.follow_pawn: Pawn = None
        self.fear_pawn: Pawn = None
        self.view_distance = 1.0

        self.bomb: Bomb = bomb

        sprite = Sprite()
        texture = Texture()
        texture.load_from_file(os.path.join('textures', 'enemy.mtex'), 0.25) # 0.2
        sprite.texture = texture
        self.render_object = sprite
        self.velocity_max = 0.1
        self.health = self.max_health

        self.time_since_last_damage_cast: float = 0.0
        self.time_since_last_bomb_thrown: float = 0.0
        self.attack_cooldown: float = 1.0
        self.bomb_throw_cooldown: float = 10.0

        self.on_died_event = None # Funktion

        self.can_throw_bomb: bool = False

    def follow(self, pawn: Pawn):
        self.follow_pawn = pawn

    def fear(self, pawn: Pawn):
        self.fear_pawn = pawn

    def respawn(self, pos_x: float, pos_y: float):
        self.is_visible = True
        self.health = self.max_health
        self.position_x = pos_x
        self.position_y = pos_y

    @overrides(Pawn)
    def on_update(self, delta_time: float):
        self.time_since_last_damage_cast += delta_time
        self.time_since_last_bomb_thrown += delta_time

        if self.can_throw_bomb and not self.bomb.is_visible and self.time_since_last_bomb_thrown >= self.bomb_throw_cooldown:
            x_dist: float = self.position_x - self.follow_pawn.position_x
            if abs(x_dist) < 0.6 and abs(x_dist) > 0.3:
                self.time_since_last_bomb_thrown = 0.0
                self.bomb.is_visible = True
                self.bomb.is_in_air = True
                self.bomb.reset()
                self.throw(self.bomb, -0.1 if x_dist > 0 else 0.1, 0.05 * abs(x_dist))

        # vor gefürchtetem Pawn fliehen
        if self.fear_pawn != None and self.fear_pawn.is_visible:
            fear_x: float = self.fear_pawn.position_x
            fear_y: float = self.fear_pawn.position_y
            if calculate_points_distance(self.position_x, self.position_y, fear_x, fear_y) <= self.view_distance:
                if fear_x < self.position_x:
                    self.is_moving_left = False
                    self.is_moving_right = True
                if fear_x > self.position_x:
                    self.is_moving_left = True
                    self.is_moving_right = False
                return

        # ... sonst follow_pawn verfolgen
        if self.follow_pawn == None:
            return
        if self.follow_pawn.position_x < self.position_x:
            self.is_moving_left = True
            self.is_moving_right = False
        elif self.follow_pawn.position_x > self.position_x:
            self.is_moving_left = False
            self.is_moving_right = True


    @overrides(Pawn)
    def on_damage_received(self, damage: float):
        pass

    @overrides(Pawn)
    def on_died(self):
        self.is_visible = False
        if self.on_died_event != None: self.on_died_event()
        # TODO: play die animation

    @overrides(Pawn)
    def on_pawn_collision(self, pawn: 'Pawn'):
        if self.time_since_last_damage_cast >= self.attack_cooldown:
            pawn.receive_damage(5.0)
            self.time_since_last_damage_cast = 0.0

"""
BombBall
"""
class BombBall(Game):
    def __init__(self):
        super().__init__()

        self.highscore = 0
        self.score = 0

        # Background
        bg0_layer = GameLayer(100000.0)
        self.add_render_layer(bg0_layer)

        # Sonne
        sun = LightSource()
        sun_texture = Texture()
        sun_texture.load_from_file(os.path.join('textures', 'sun.mtex'), 0.4)
        sun.texture = sun_texture
        sun.set_position(0.5, 0.8)
        bg0_layer.add_object(sun)

        # Mond
        moon = LightSource()
        moon_texture = Texture()
        moon_texture.load_from_file(os.path.join('textures', 'moon.mtex'), 0.4)
        moon.texture = moon_texture
        moon.brightness = 0.2
        moon.set_position(0.5, 0.8)
        bg0_layer.add_object(moon)

        # Backround 1
        bg1_layer = GameLayer(16.0)
        bg1_terrain = Terrain([200, 200, 200], [1.2, 34, 0.5], 1.0)
        bg1_layer.add_object(bg1_terrain)
        self.add_render_layer(bg1_layer)

        self.game_layer = GameLayer(1.0)
        pawn = Pawn()
        #pawn.render_object = Circle([255, 0, 0], 0.1, 0.0, 0.0)
        self.player = pawn
        self.camera.follow(self.player)
        terrain = Terrain([0, 255, 0], [1.0, 1.5], 0.2)
        self.game_layer.add_object(terrain)
        self.game_layer.add_object(pawn)
        self.add_render_layer(self.game_layer)

        sprite = Sprite()
        tex = Texture()
        tex.load_from_file(os.path.join("textures", "player.mtex"), 0.25) #0.2
        sprite.texture = tex
        pawn.render_object = sprite

        baum = Sprite()
        baumtex = Texture()
        baumtex.load_from_file(os.path.join("textures", "behindibaum.mtex"), 1.0)
        baum.texture = baumtex
        terrain.add_foliage(baum, 0.5)

        grass = Sprite()
        grasstex = Texture()
        grasstex.load_from_file(os.path.join("textures", "grass.mtex"), 0.2)
        grass.texture = grasstex
        terrain.add_foliage(grass, 3)

        spruce = Sprite()
        sprucetex = Texture()
        sprucetex.load_from_file(os.path.join("textures", "spruce"), 0.3)
        spruce.texture = sprucetex
        bg1_terrain.add_foliage(spruce, 1.0)

        health_bar = HealthBar()
        health_bar.pawn = self.player
        self.overlay_layer.add_object(health_bar)

        self.init_bomb()

        self.enemies: list = []
        self.time_since_last_enemy_respawn: float = 0.0
        self.enemy_respawn_intervall: float = 1.0

        self.init_enemies()

        self.night_sky_texture = Texture()
        self.night_sky_texture.load_from_file(os.path.join('textures', 'night_sky.mtex'))
        self.night_sky_texture.size = 1.0

        self.enable_day_night_cycle = True
        self.time = 12 * 60 * 60 # Mittags
        self.sun = sun
        self.moon = moon

        self.camera.zoom = 1.0
        #self.camera.zoom_smooth(1.0, 0.01)

        self.show_title = False

        self.title = 'BOMB BALL'
        self.start()

    """
    init_bomb
        Initialisiert die vom Player werfbare Bombe
    """
    def init_bomb(self): 
        self.bomb = Bomb()
        self.enemy_bomb = Bomb()
        self.bomb.on_explode = self.on_bomb_explode
        self.enemy_bomb.on_explode = self.on_bomb_explode
        self.game_layer.add_object(self.bomb)
        self.game_layer.add_object(self.enemy_bomb)

    """
    init enemies
        Initalisert die Enemies (momentan nur eins).
        Wird auch genutzt, um die Enemies zu resetten
    """
    def init_enemies(self):
        # Alle enemeis aus dem GameLayer entfernen
        for x in self.enemies:
            self.game_layer.remove_object(x)
        self.enemies.clear()
        # Neue Enemies
        enemy = Enemy(self.enemy_bomb)
        enemy.position_x = 1.0
        enemy.follow(self.player)
        enemy.fear(self.bomb)
        enemy.on_died_event = self.on_enemy_died
        self.game_layer.add_object(enemy)
        self.enemies.append(enemy)

    """
    reset_game
        Setzt das Spiel zurück
    """
    def reset_game(self):
        self.score = 0
        # bomb
        self.bomb.is_visible = False
        # camera
        self.camera.position_x = -0.5
        # player
        self.player.position_x = 0.0
        self.player.health = self.player.max_health
        for enemy in self.enemies:
            enemy: Enemy = enemy
            enemy.health = 0.0

    """
    on_update
    """
    @overrides(Game)
    def on_update(self, delta_time: float):
        if keyboard.is_pressed('q'):
            self.player_throw_bomb(-0.1, 0.05)
        if keyboard.is_pressed('e'):
            self.player_throw_bomb(0.1, 0.05)

        # Bomb Camera
        if self.bomb.is_visible:
            self.camera.follow(self.bomb)
            #self.camera.zoom_smooth(0.9, 0.1)
        else:
            self.camera.follow(self.player)
            #self.camera.zoom_smooth(1.0, 0.1)

        # respawn enemies
        self.time_since_last_enemy_respawn += delta_time
        if self.time_since_last_enemy_respawn >= self.enemy_respawn_intervall:
            self.time_since_last_enemy_respawn = 0.0
            self.respawn_dead_enemies()

        # Player dead
        if self.player.is_dead:
            fade_step: float = 1.0 / FRAMERATE
            self.playback_speed -= fade_step
            self.render_brightness -= fade_step
            if self.playback_speed == 0.0:
                if self.score > self.highscore:
                    self.display_text('HIGH SCORE!', True)
                self.reset_game()
                self.playback_speed = 1.0
                self.render_brightness = 1.0

        #print(self.player.velocity_x, self.enemies[0].velocity_x)
        #GlobalShaderSettings.light_brightness = 0.0


    def player_throw_bomb(self, dir_x, dir_y):
        if self.bomb.is_visible:
            return
        self.bomb.is_visible = True
        self.bomb.is_in_air = True
        self.bomb.reset()
        self.player.throw(self.bomb, dir_x, dir_y)

    def on_bomb_explode(self):
        self.camera.earthquake(0.1, 20.0, 10.0)

    def respawn_dead_enemies(self):
        for enemy in self.enemies:
            enemy: Enemy
            if enemy.is_dead:
                respawn_location: float = random() + randint(2, 5)
                respawn_location = -respawn_location if randint(0, 1) == 0 else respawn_location
                enemy.velocity_max *= 1.2
                if self._day >= 4: enemy.can_throw_bomb = True
                enemy.respawn(self.player.position_x + respawn_location, self.player.position_y)

    def on_enemy_died(self):
        self.display_text('5')
        self.score += 5
