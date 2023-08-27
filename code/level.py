import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import *
from random import randint
from menu import Menu


class Level:
    def __init__(self):

        #get the display surface
        self.display_surface = pygame.display.get_surface()

        #sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group() 
        self.tree_Sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        #sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 5
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        #shop
        self.menu = Menu(self.player, self.toggle_shop)
        self.shop_active = False

        #sound
        self.succes = pygame.mixer.Sound('C:/Users/phili/OneDrive/Desktop/HorrorValley/audio/success.wav')
        self.succes.set_volume(0.3)

        self.music = pygame.mixer.Sound('C:/Users/phili/OneDrive/Desktop/HorrorValley/audio/bg.wav')
        self.music.play(loops=-1)
        self.music.set_volume(0.8)

    def setup(self):

        tmx_data = load_pygame('C:/Users/phili/OneDrive/Desktop/HorrorValley/data/map.tmx')

        #house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x,y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
                
        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x,y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

        #Fence
        for x,y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE,y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites] , LAYERS['main'])


        #water
        WATER_FRAMES = import_folder('C:/Users/phili/OneDrive/Desktop/HorrorValley/graphics/water')
        for x,y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE,y * TILE_SIZE), WATER_FRAMES, [self.all_sprites, self.collision_sprites])
        
        #WildFlower
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, self.all_sprites)

        #tree
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos = (obj.x, obj.y), 
                surf = obj.image, 
                groups = [self.all_sprites, self.collision_sprites, self.tree_Sprites], 
                name = obj.name,
                player_add = self.player_add)

        #collision tiles

        for x,y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE,y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites, LAYERS['main'])

        # Player 
        for obj in tmx_data.get_layer_by_name('Player'):
                    if obj.name == 'Start':
                        self.player = Player(
                            pos = (obj.x,obj.y), 
                            group = self.all_sprites, 
                            collision_sprites = self.collision_sprites,
                            tree_sprites = self.tree_Sprites,
                            interaction = self.interaction_sprites,
                            soil_layer = self.soil_layer,
                            toggle_shop = self.toggle_shop)
                    if obj.name == 'Bed':
                        Interaction((obj.x,obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
                        
                    if obj.name == 'Trader':
                        Interaction((obj.x,obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
                        
        
                                        
        Generic(
        pos = (0,0),
        surf = pygame.image.load('C:/Users/phili/OneDrive/Desktop/HorrorValley/graphics/world/ground.png').convert_alpha(),
        groups = self.all_sprites,
        z = LAYERS['ground']
        )
        
    def player_add(self, item):
        self.player.item_inventory[item] += 1
        self.succes.play()

    def toggle_shop(self):

        self.shop_active = not self.shop_active

    def reset(self):

        #plants
        self.soil_layer.update_plants()

        #soil
        self.soil_layer.remove_water()
        self.raining = randint(0,10) > 5
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        #apples on trees
        for tree in self.tree_Sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        #sky
        self.sky.start_color = [255,255,255]

    def plant_collisions(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvastable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, LAYERS['main'])
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

    def run(self, dt):

        #draw logic
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        #updates
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collisions()

        #waether and sky
        self.overlay.display()
        if self.raining and not self.shop_active:
            self.rain.update()
        self.sky.display(dt)

        #transition overlay
        if self.player.sleep:
            self.transition.play()
        
        

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = Vector2(0,0)

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH/2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT/2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)

                    
               # # anaytics
               # if sprite == player:
               #     pygame.draw.rect(self.display_surface,'red',offset_rect,5)
               #     hitbox_rect = player.hitbox.copy()
               #     hitbox_rect.center = offset_rect.center
               #     pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
               #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSETS[player.status.split('_')[0]]
               #     pygame.draw.circle(self.display_surface,'blue',target_pos,5)



