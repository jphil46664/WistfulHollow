import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer


class Level:
    def __init__(self):

        #get the display surface
        self.display_surface = pygame.display.get_surface()

        #sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group() 
        self.tree_Sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

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
                            soil_layer = self.soil_layer)
                    if obj.name == 'Bed':
                        Interaction((obj.x,obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
                        
                        
        
                                        
        Generic(
        pos = (0,0),
        surf = pygame.image.load('C:/Users/phili/OneDrive/Desktop/HorrorValley/graphics/world/ground.png').convert_alpha(),
        groups = self.all_sprites,
        z = LAYERS['ground']
        )
        
    def player_add(self, item):
        self.player.item_inventory[item] += 1


    def reset(self):

        #apples on trees
        for tree in self.tree_Sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()


    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()
        #print(self.player.item_inventory)

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



