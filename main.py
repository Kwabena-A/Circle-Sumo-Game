import pygame
from sys import exit
import time
import random
import numpy as np
from math import atan, degrees, sin

pygame.init()
SCREEN = pygame.display.set_mode((1280, 720))
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

startup_sfx = pygame.mixer.Sound('Assets\Music\startup.mp3')
impact_sfx = {}
for x in range(0, 11):
    impact_sfx.update({f'{x}' : pygame.mixer.Sound(f'Assets\Music\Hit_sfx\hit {x}.mp3')})

woosh_sfx = pygame.mixer.Sound('Assets/Music/whoosh.mp3')
dash_sfx = pygame.mixer.Sound('Assets\Music\dash.mp3')
dash_sfx.set_volume(500)
whack_sfx = pygame.mixer.Sound('Assets\Music\whack.mp3')
dash_channel = pygame.mixer.Channel(2)

ATTACK_FRAMES = [pygame.transform.smoothscale(pygame.image.load(f'Assets\Attack Animation\ezgif-frame-{x}.jpg').convert_alpha(), (160, 90)) for x in range(1, 12)]

def distance_between_two_points(x1, y1, x2, y2, sqrt=False):
    if sqrt == False:
        distance = (((x2 - x1)**2) + ((y2 - y1)**2))
    else:
        distance = (((x2 - x1)**2) + ((y2 - y1)**2))**(1/2)
    return distance

def calculate_xy_velo(opp, adj, margin=10):
    divisor = 1
    while True:
        if opp / divisor < (margin) and adj / divisor < (margin) and opp / divisor > (margin * -1) and adj / divisor > (margin *-1):
            yvelo = opp / divisor
            xvelo = adj / divisor
            return xvelo, yvelo
        else:
            divisor += 1
    

enemy_spawnpoints_down = [(x, (700**2 - x**2)**0.5) for x in range(0, 700)]

enemy_spawnpoints_up = [(x, ((700**2 - x**2)**0.5)*-1) for x in range(0, 700)]

enemy_spawnpoints_downl = [(x*-1, (700**2 - x**2)**0.5) for x in range(0, 700)]

enemy_spawnpoints_upl = [(x*-1, ((700**2 - x**2)**0.5)*-1) for x in range(0, 700)]

enemy_spawnpoints = enemy_spawnpoints_down + enemy_spawnpoints_up + enemy_spawnpoints_downl + enemy_spawnpoints_upl

WAVE_ACTIVE = False
WAVE_NUMBER = 1

TIME_LIMIT = pygame.time.get_ticks() + 500
TIME_REMAINING = TIME_LIMIT - pygame.time.get_ticks()

ALIVE = True

class Island(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.speed_cap_timer = pygame.time.get_ticks() + 1000


        self.image = pygame.Surface((5000, 5000)).convert_alpha()
        self.image.fill((210, 210, 255))
        self.rect = self.image.get_rect(center = (1280/2, 720/2))
        self.mask = pygame.mask.from_surface(self.image)

        self.xvelo = 0
        self.yvelo = 0
        self.friction = 0.1
        self.speed_cap = 4
        self.offset = [0, 0]

    def movement(self):
        keys = pygame.key.get_pressed()
        #Key Presses
        if self.speed_cap == 4:
            if keys[pygame.K_w]:
                self.yvelo += 1
            if keys[pygame.K_s]:
                self.yvelo -= 1
            if keys[pygame.K_a]:
                self.xvelo += 1
            if keys[pygame.K_d]:
                self.xvelo -= 1
        
        #Speed Capper
        if self.xvelo > self.speed_cap:
            self.xvelo = self.speed_cap
        if self.xvelo < self.speed_cap * -1:
            self.xvelo = self.speed_cap * -1
        
        if self.yvelo > self.speed_cap:
            self.yvelo = self.speed_cap
        if self.yvelo < self.speed_cap * -1:
            self.yvelo = self.speed_cap * -1
        
        # Friction
        if self.xvelo > 0:
            self.xvelo -= self.friction
        elif self.xvelo < 0:
            self.xvelo += self.friction
        
        if self.yvelo > 0:
            self.yvelo -= self.friction
        elif self.yvelo < 0:
            self.yvelo += self.friction
        
        self.rect.x += self.xvelo
        self.offset[0] += self.xvelo
        self.rect.y += self.yvelo
        self.offset[1] += self.yvelo

    def reset_speed_cap(self):
        if pygame.time.get_ticks() > self.speed_cap_timer:
            if self.speed_cap > 5:
                self.speed_cap -= 0.2
            else:
                self.speed_cap = 4
                player.sprite.dashing = False
    
    def update(self):
        self.reset_speed_cap()
        self.movement()
        self.image.fill('#BBEDFF')

island = pygame.sprite.GroupSingle(Island())

class Land(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 750
        self.image = pygame.Surface((self.radius*2 + 50, self.radius*2 + 50)).convert_alpha()
        self.image.fill((0,0,0,0))
        self.rect = self.image.get_rect(center = (2500, 2500))

        pygame.draw.circle(self.image, (150, 170, 150), (self.radius +25, self.radius+25), self.radius+ 10)
        pygame.draw.circle(self.image, (200, 230, 200), (self.radius +25, self.radius+25), self.radius)

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        pass

class Particles(pygame.sprite.Sprite):
    def __init__(self, radius, location, xvelo, yvelo, color='white', alpha=255, fade_out=True, friction=True):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2)).convert_alpha()
        self.image.fill((0,0,0,0))
        self.image.set_alpha(alpha)
        pygame.draw.circle(self.image, color, (radius, radius), radius)

        self.xvelo = xvelo
        self.yvelo = yvelo
        self.friction = 2

        self.fade_out = fade_out
        self.friction = friction
        self.rect = self.image.get_rect(center = location)
        
    def movement(self):
        
        if self.friction:
            if self.xvelo > 0:
                self.xvelo -= self.friction
            elif self.xvelo < 0:
                self.xvelo += self.friction
            
            if self.yvelo > 0:
                self.yvelo -= self.friction
            elif self.yvelo < 0:
                self.yvelo += self.friction
        
        self.rect.x += self.xvelo
        self.rect.y += self.yvelo

        if self.fade_out:
            try:
                self.image.set_alpha(self.image.get_alpha() - 5)
            except:
                self.kill()
    
    def update(self):
        self.movement()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.map_center = (-1850, -2140)
        self.loc = (land.sprite.rect.centerx - (island.sprite.rect.centerx - 640)), (land.sprite.rect.centery - (island.sprite.rect.centery - 360))

        self.image = pygame.image.load('Assets\Charachters\Player.png').convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (75,75))
        self.rect = self.image.get_rect(center = (self.loc))

        self.xvelo = 0
        self.yvelo = 0
        self.dashing = False

        self.stamina = 5
        self.stamina_refresh_timer = pygame.time.get_ticks() + 2000

        self.off_island = False
        self.radius_points = []
        self.angle = 0

        for x in np.linspace(-50, 50, 360*2):
            y = (2500 - x**2)**(1/2)
            
            self.radius_points.append((x, y))
            self.radius_points.append((x, y*-1))

        self.pointer_surf = pygame.Surface((20,20)).convert_alpha()
        self.pointer_surf.fill((0,0,0,0))
        self.x_pos = 0
        self.y_pos = 0
    def keyboard(self):
        keys = pygame.key.get_pressed()
        if pygame.mouse.get_pressed()[0] and len(attack.sprites()) == 0 and self.stamina > 0:
            attack.add(Attack(self.angle))
            island.sprite.speed_cap_timer = pygame.time.get_ticks() + 200
            island.sprite.xvelo += self.adj
            island.sprite.yvelo -= self.opp

            self.stamina -= 1
            self.stamina_refresh_timer = pygame.time.get_ticks() + 2000
        
        if keys[pygame.K_SPACE] and self.stamina > 0 and island.sprite.speed_cap <= 4:
            island.sprite.speed_cap_timer = pygame.time.get_ticks() + 200
            island.sprite.speed_cap = 12

            xvelo, yvelo = calculate_xy_velo(self.opp, self.adj, margin=10)
            xvelo *= -1
            island.sprite.xvelo = 0
            island.sprite.yvelo = 0

            island.sprite.xvelo += xvelo
            island.sprite.yvelo += yvelo
            self.dashing = True

            self.stamina -= 1
            self.stamina_refresh_timer = pygame.time.get_ticks() + 2000
            
    def stamina_refresh(self):
        if pygame.time.get_ticks() > self.stamina_refresh_timer:
            if self.stamina < 5:
                self.stamina += 1
                self.stamina_refresh_timer = pygame.time.get_ticks() + 10

    def pointer_loc(self):
        mouse_pos = pygame.mouse.get_pos()
        closest_num = 1000000000
        closest_index = 1
        for indx, cord in enumerate(self.radius_points):
            # print(cord, mouse_pos)
            x_pos = (cord[0] + 1280/2)
            y_pos = (cord[1] + 720/2)
            distance = distance_between_two_points(x_pos, y_pos, mouse_pos[0], mouse_pos[1], sqrt=False)
            if distance < closest_num:
                closest_num = distance
                closest_index = indx*1

        self.pointer_surf = pygame.Surface((20,20)).convert_alpha()
        self.pointer_surf.fill((0,0,0,0))
        pygame.draw.circle(self.pointer_surf, 'white', (10,10), 5)
        self.x_pos = self.radius_points[closest_index][0] + self.rect.centerx - 10
        self.y_pos = self.radius_points[closest_index][1] + self.rect.centery - 10
        island.sprite.image.blit((self.pointer_surf), (self.x_pos, self.y_pos))

        self.opp = 720/2 - pygame.mouse.get_pos()[1]
        self.adj = pygame.mouse.get_pos()[0] - 1280/2

        # print(self.opp, self.adj)
        # pygame.draw.line(SCREEN, 'red', (1280/2, 720/2), (1280/2 + self.adj, 720/2))
        # pygame.draw.line(SCREEN, 'yellow', (1280/2, 720/2), (1280/2, 720/2 + self.opp))

        if self.opp == 0:
            if self.adj > 0:
                self.angle = 180
            else:
                self.angle = 0
        elif self.adj == 0:
            if self.opp > 0:
                self.angle = 90
            else:
                self.angle = 270

        else:
            self.angle = degrees(atan(self.opp/self.adj)) % 360

            # Quadrent I
            if self.opp > 0 and self.adj > 0:
                pass
            # Quadrent II
            elif self.opp > 0 and self.adj < 0:
                self.angle -= 180
            # Quadrent III
            elif self.opp <= 0 and self.adj <= 0:
                self.angle += 180
            # Quadrent IV
            elif self.opp < 0 and self.adj > 0:
                pass

    def island_radius(self):
        global ALIVE
        if self.off_island == False:
            if not pygame.sprite.spritecollide(self, land, False, pygame.sprite.collide_mask):
                self.off_island = True
        else:
            try:
                self.image = pygame.transform.smoothscale(self.image, (self.image.get_size()[0] - 5, self.image.get_size()[1] - 5))
                self.rect = self.image.get_rect(center = (1280/2, 720/2))
            except ValueError:
                self.image = pygame.transform.smoothscale(self.image, (0,0))
                if len(gameover.sprites()) == 0:
                    gameover.add(GameOver())
                ALIVE = False

            if distance_between_two_points(island.sprite.rect.x, island.sprite.rect.y, self.map_center[0], self.map_center[1], sqrt=True) < 750:
                if island.sprite.rect.x > self.map_center[0]:
                    island.sprite.xvelo += island.sprite.xvelo * 3
                elif island.sprite.rect.x < self.map_center[0]:
                    island.sprite.xvelo -= island.sprite.xvelo * 3

                if island.sprite.rect.y > self.map_center[1]:
                    island.sprite.yvelo -= island.sprite.yvelo * 3
                elif island.sprite.rect.y < self.map_center[1]:
                    island.sprite.yvelo -= island.sprite.yvelo * 3

    def update(self):
        self.pointer_loc()
        self.keyboard()
        self.stamina_refresh()
        self.island_radius()
        if self.dashing:
            particles.add(Particles(30, (self.rect.centerx + self.xvelo*100, self.rect.centery + self.yvelo*100), 0, 0, alpha=150, color='white'))
            if dash_channel.get_busy() == False:
                dash_channel.play(dash_sfx, fade_ms=1000)
        else:
            dash_channel.fadeout(1000)
        self.rect.center = (land.sprite.rect.centerx - (island.sprite.rect.centerx - 640)), (land.sprite.rect.centery - (island.sprite.rect.centery - 360))

class Attack(pygame.sprite.Sprite):
    def __init__(self, angle):
        super().__init__()
        woosh_sfx.play()
        self.goal_time = pygame.time.get_ticks() + 500
        self.angle = angle
        self.opp = player.sprite.opp
        self.adj = player.sprite.adj
        
        self.xvelo, self.yvelo = calculate_xy_velo(self.opp, self.adj)

        self.loc =  player.sprite.rect.centerx + self.xvelo * 4, player.sprite.rect.centery - self.yvelo * 4

        self.image = pygame.image.load('Assets/attack.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_size()[0]/15, self.image.get_size()[1]/15))
        self.image = pygame.transform.rotate(self.image, self.angle - 90)
        self.image.set_colorkey((0,0,0, 253))

        self.rect = self.image.get_rect(center = self.loc)
        self.mask = pygame.mask.from_surface(self.image)
        
        self.alpha_drop_status = False
        self.alpha = 255

        if self.xvelo > 0:
            self.xsign = True
        else:
            self.xsign = False
        
        if self.yvelo > 0:
            self.ysign = True
        else:
            self.ysign = False
    
    def movement(self):

        if pygame.time.get_ticks() < self.goal_time:
            self.alpha_drop_status = True

        else: 
            if self.xsign == False:
                if self.xvelo < 0:
                    self.xvelo += 0.5
                else:
                    self.xvelo = 0
            
            if self.xsign == True:
                if self.xvelo > 0:
                    self.xvelo -= 0.5
                else:
                    self.xvelo = 0
            

            if self.ysign == False:
                if self.yvelo < 0:
                    self.yvelo += 0.5
                else:
                    self.yvelo = 0
            
            if self.ysign == True:
                if self.yvelo > 0:
                    self.yvelo -= 0.5
                else:
                    self.yvelo = 0
        
        self.rect.x += self.xvelo
        self.rect.y -= self.yvelo

    def alpha_drop(self):
        if self.alpha_drop_status:
            self.image.set_alpha(self.alpha)
            self.alpha -= 5
        if self.alpha < 0:
            self.kill()

    def update(self):
        self.alpha_drop()
        self.movement()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.map_center = (-1850, -2140)

        spawn_location = random.choice(enemy_spawnpoints)
        self.image = pygame.image.load('Assets\Charachters\Enemy.png').convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (75,75))
        self.rect = self.image.get_rect(center = ((land.sprite.rect.centerx + spawn_location[0]), (land.sprite.rect.centery + spawn_location[1])))

        self.mask = pygame.mask.from_surface(self.image)

        self.xvelo = 0
        self.yvelo = 0
        self.friction = 0.01
        self.speed_cap_org = (WAVE_NUMBER/2) + random.randint(3, 6)
        self.speed_cap = self.speed_cap_org*1

        self.start_time = 0

        self.off_island = False

        self.radius_points = []
        self.angle = 0
        self.reaction_time_skill = random.randint(300, 700)
        self.reaction_time_timer = pygame.time.get_ticks() + self.reaction_time_skill
        self.player_loc = land.sprite.rect.centerx - (island.sprite.rect.centerx - 640), (island.sprite.rect.centery - 360) - self.rect.centery

        for x in np.linspace(-50, 50, 360*2):
            y = (2500 - x**2)**(1/2)
            
            self.radius_points.append((x, y))
            self.radius_points.append((x, y*-1))

    def reaction_time(self):
        if pygame.time.get_ticks() > self.reaction_time_timer:
            self.player_loc = land.sprite.rect.centerx - (island.sprite.rect.centerx - 640),  land.sprite.rect.centery - (island.sprite.rect.centery - 360)
            self.reaction_time_timer = pygame.time.get_ticks() + self.reaction_time_skill

    def move_to_player(self):
        if self.off_island == False:
            if self.player_loc[0] > self.rect.centerx:
                self.xvelo += 0.3

            elif self.player_loc[0] < self.rect.centerx:
                self.xvelo -= 0.3
            else:
                self.xvelo = 0    
            
            if self.player_loc[1] > self.rect.centery:
                self.yvelo += 0.3
            elif self.player_loc[1] < self.rect.centery:
                self.yvelo -= 0.3
            
            
        #Speed Capper
        if self.xvelo > self.speed_cap:
            self.xvelo = self.speed_cap
        if self.xvelo < self.speed_cap * -1:
            self.xvelo = self.speed_cap * -1
        
        if self.yvelo > self.speed_cap:
            self.yvelo = self.speed_cap
        if self.yvelo < self.speed_cap * -1:
            self.yvelo = self.speed_cap * -1
        
        # Friction
        if self.xvelo > 0:
            self.xvelo -= self.friction
        elif self.xvelo < 0:
            self.xvelo += self.friction
        
        if self.yvelo > 0:
            self.yvelo -= self.friction
        elif self.yvelo < 0:
            self.yvelo += self.friction
        
        self.rect.x += self.xvelo
        self.rect.y += self.yvelo
    
    def island_radius(self):
        if self.off_island == False:
            if not pygame.sprite.spritecollide(self, land, False, pygame.sprite.collide_mask):
                self.off_island = True
        else:
            try:
                org_loc = self.rect.center*1
                self.image = pygame.transform.smoothscale(self.image, (self.image.get_size()[0] - 5, self.image.get_size()[1] - 5))
                self.rect = self.image.get_rect(center = org_loc)
            except ValueError:
                self.image = pygame.transform.smoothscale(self.image, (0,0))
                self.kill()

            if distance_between_two_points(self.rect.x, self.rect.y, land.sprite.rect.centerx, land.sprite.rect.centery, sqrt=True) < 800:
                if self.rect.x > land.sprite.rect.centerx:
                    self.xvelo += self.xvelo * 3
                elif self.rect.x < land.sprite.rect.centerx:
                    self.xvelo -= self.xvelo * 3

                if self.rect.y > land.sprite.rect.centery:
                    self.yvelo -= self.yvelo * 3
                elif self.rect.y < land.sprite.rect.centery:
                    self.yvelo -= self.yvelo * 3

    def enemey_bounce(self):
        bump_group = enemy.sprites()
        bump_group.remove(self)

        if pygame.sprite.spritecollide(self, bump_group, False, pygame.sprite.collide_mask):
            self_group = pygame.sprite.GroupSingle(self)
            for sprites in bump_group:
                if pygame.sprite.spritecollide(sprites, self_group, False, pygame.sprite.collide_mask):
                    enemy_bump = sprites
                    break
            self.xvelo += (self.rect.centerx/9 - enemy_bump.rect.centerx/9)
            self.yvelo += (self.rect.centery/9 - enemy_bump.rect.centery/9)

            enemy_bump.xvelo -= (self.rect.centerx/9 - enemy_bump.rect.centerx/9)
            enemy_bump.yvelo -= (self.rect.centery/9 - enemy_bump.rect.centery/9)

    def player_impact(self):
        if pygame.sprite.spritecollide(self, player, False, pygame.sprite.collide_mask):
            island.sprite.xvelo = 0
            island.sprite.yvelo = 0

            island.sprite.xvelo = (player.sprite.rect.centerx/7 - self.rect.centerx/7) * -1

            island.sprite.yvelo = (player.sprite.rect.centery/7 - self.rect.centery/7) * -1
            
            island.sprite.speed_cap = 12
            island.sprite.speed_cap_timer = pygame.time.get_ticks() + 1000

    def attack_collision(self):
        if pygame.sprite.spritecollide(self, attack, False, pygame.sprite.collide_mask):
            impact_sfx[str(random.randint(0, 10))].play()
            self.xvelo += (self.rect.x/2 - attack.sprite.rect.x/2)
            self.yvelo += (self.rect.y/2 - attack.sprite.rect.y/2)
            self.speed_cap = 15
            for x in range(1):
                particles.add(Particles(5, self.rect.center, (self.xvelo/5) + random.randint(-5, 25), (self.yvelo/5) + random.randint(-5, 5)))
        else:
            self.speed_cap = self.speed_cap_org*1

    def update(self):
        self.reaction_time()
        self.move_to_player()
        self.enemey_bounce()
        self.island_radius()
        self.attack_collision()

        self.player_impact()

class WeaponUI(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.choice_select = 1 
        self.x_offset = 30
        self.y_margin = 10

        self.sword_surf = pygame.transform.scale(pygame.image.load('Assets/UI Elements/Sword.png').convert_alpha(), (100,43))
        self.sword_rect = self.sword_surf.get_rect(bottomright = (1280 - self.x_offset, 720 - self.y_margin))
        
        self.sword = [self.sword_surf, self.sword_rect]
        
        self.axe_surf = pygame.transform.scale(pygame.image.load('Assets/UI Elements/Axe.png').convert_alpha(), (100, 43))
        self.axe_rect = self.axe_surf.get_rect(bottomright = (1280 - self.x_offset, self.sword_rect.top + self.y_margin - -30))
        self.axe = [self.axe_surf, self.axe_rect]

        self.stam_surf = pygame.transform.scale(pygame.image.load(f'Assets/UI Elements/Stamina/{player.sprite.stamina}.png').convert_alpha(), (239/3, 36/3))
        self.stam_rect = self.stam_surf.get_rect(bottomright = self.axe[1].topright)
        self.stamina = [self.stam_surf, self.stam_rect]

        self.time_font = pygame.font.Font('Assets/Vermin Vibes 1989.ttf', 30)
        self.time_surf = self.time_font.render(f'12 : 34', True, 'white')
        self.time_rect = self.time_surf.get_rect(midtop = (1280/2, 20))
        self.time = [self.time_surf, self.time_rect, self.time_font]

        self.advance_font = pygame.font.Font('Assets\Vermin Vibes 1989.ttf', 30)
        self.advance_surf = self.advance_font.render('Press Enter To Advance', True, 'white')
        self.advance_rect = self.advance_surf.get_rect(midbottom = (1280/2, 700))
        self.advance = [self.advance_surf, self.advance_rect, self.advance_font]

        self.switch_delay_timer = pygame.time.get_ticks() + 200
        self.weapons = [self.sword, self.axe]
        self.image = pygame.Surface((1, 1)).convert_alpha()
        self.image.fill((0,0,0,0))
        self.rect = self.image.get_rect(bottomright = (1280, 720))
    
    def scale_choice(self):
        for weapon in self.weapons:
            if self.choice_select == self.weapons.index(weapon):
                if weapon[0].get_size()[0] < 200:
                    weapon[0] = pygame.transform.scale(weapon[0], (200, 86))


            else:
                if weapon[0].get_size()[0] > 100:
                    weapon[0] = pygame.transform.scale(weapon[0], (100, 43))
    
    def keyboard(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_TAB]:
            if pygame.time.get_ticks() > self.switch_delay_timer:
                self.switch_delay_timer = pygame.time.get_ticks() + 200
                self.choice_select += 1
                if self.choice_select > 1:
                    self.choice_select = 0
    
    def update(self):
        self.scale_choice()
        self.sword[1] = self.sword[0].get_rect(bottomright = (1280 - self.x_offset, 720 - self.y_margin))
        self.axe[1] = self.axe[0].get_rect(bottomright = (1280 - self.x_offset, self.sword[1].top + self.y_margin))
        
        for weapon in self.weapons:
            SCREEN.blit(weapon[0], weapon[1])
        pygame.draw.line(SCREEN, 'white', (self.axe[1].topright[0] + 10, self.axe[1].topright[1]), (self.sword[1].bottomright[0] + 10, self.sword[1].bottomright[1]), 5)

        SCREEN.blit(self.stamina[0], self.stamina[1])
        self.stamina[0] = pygame.transform.scale(pygame.image.load(f'Assets/UI Elements/Stamina/{player.sprite.stamina}.png').convert_alpha(), (239/3, 36/3))
        self.stamina[1] = self.stamina[0].get_rect(bottomright = (self.axe[1].topright[0], self.axe[1].topright[1] - 20))

        SCREEN.blit(self.time[0], self.time[1])
        self.time[0] = self.time[2].render(f'{TIME_REMAINING}', True, 'white')
        self.time[1] = self.time[0].get_rect(midtop = (1280/2, 20))

        if WAVE_ACTIVE == False:
            SCREEN.blit(self.advance[0], self.advance[1])
            self.advance[0].set_alpha(255 * sin(2 * time.time()))
        


        self.keyboard()

class WaveIndicator(pygame.sprite.Sprite):
    def __init__(self, complete):
        super().__init__()
        self.font = pygame.font.Font('Assets\Vermin Vibes 1989.ttf', 30)

        if complete == True:
            self.image = self.font.render(f'Wave {WAVE_NUMBER} Complete', True, 'white')
        else:
            self.image = self.font.render(f'Wave {WAVE_NUMBER}', True, 'white')
        self.rect = self.image.get_rect(midbottom = (1280/2, 0))

        self.yvelo = 5
    
    def float_in(self):
        self.yvelo -= 0.1
        self.rect.y += self.yvelo
    
    def update(self):
        self.float_in()
        if self.rect.bottom < 0 and self.yvelo < 0:
            self.kill()

class GameOver(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font('Assets\Vermin Vibes 1989.ttf', 50)
        self.subfont = pygame.font.Font('Assets\Vermin Vibes 1989.ttf', 30)

        self.image = pygame.Surface((1280, 720)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(center = (1280/2, 720/2))
        self.alpha = 0
        
        self.dead = self.font.render('Game Over', False, 'white')
        self.dead_rect = self.dead.get_rect(center = (1280/2, 720/2 - 100))

        
        self.wave = self.subfont.render(f'Wave: {WAVE_NUMBER}', False, 'white')
        self.wave_rect = self.wave.get_rect(midtop = (1280/2, self.dead_rect.bottom + 50))

        self.retry = self.subfont.render(f'[Space to Restart]', False, 'white')
        self.retry_rect = self.retry.get_rect(midtop = (1280/2, self.wave_rect.bottom + 20))

        self.timer = pygame.time.get_ticks() + 1000
        self.stage = [False, False, False]

    def fade_in(self):
        if self.alpha < 100:
            self.alpha += 10
            self.image.fill((0, 0, 0, self.alpha))
    
    def keyboard(self):
        global land, particles, player, attack, enemy, weaponUI, wave_indicator, gameover, WAVE_ACTIVE, WAVE_NUMBER, TIME_LIMIT, TIME_REMAINING, ALIVE, island
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            WAVE_ACTIVE = False
            WAVE_NUMBER = 1

            TIME_LIMIT = pygame.time.get_ticks() + 500
            TIME_REMAINING = TIME_LIMIT - pygame.time.get_ticks()

            ALIVE = True
            
            island = pygame.sprite.GroupSingle(Island())

            land = pygame.sprite.GroupSingle(Land())

            particles = pygame.sprite.Group()

            player = pygame.sprite.GroupSingle(Player())

            attack = pygame.sprite.GroupSingle()

            enemy = pygame.sprite.Group()

            weaponUI = pygame.sprite.GroupSingle(WeaponUI())

            wave_indicator = pygame.sprite.Group()

            gameover = pygame.sprite.GroupSingle()
    
    def stages(self):
        if self.alpha == 100:
            if self.stage[0] == False:
                if pygame.time.get_ticks() > self.timer:
                    whack_sfx.play()
                    self.stage[0] = True
                    self.timer = pygame.time.get_ticks() + 1000
            elif self.stage[1] == False:
                if pygame.time.get_ticks() > self.timer:
                    whack_sfx.play()
                    self.stage[1] = True
                    self.timer = pygame.time.get_ticks() + 1000

            elif self.stage[2] == False:
                if pygame.time.get_ticks() > self.timer:
                    whack_sfx.play()
                    self.stage[2] = True
                    self.timer = pygame.time.get_ticks() + 1000

    def update(self):
        self.stages()
        self.fade_in()
        self.keyboard()

        if self.stage[0]:
            self.image.blit(self.dead, self.dead_rect)
        if self.stage[1]:
            self.image.blit(self.wave, self.wave_rect)
        if self.stage[2]:
            self.image.blit(self.retry, self.retry_rect)


land = pygame.sprite.GroupSingle(Land())

particles = pygame.sprite.Group()

player = pygame.sprite.GroupSingle(Player())

attack = pygame.sprite.GroupSingle()

enemy = pygame.sprite.Group()

weaponUI = pygame.sprite.GroupSingle(WeaponUI())

wave_indicator = pygame.sprite.Group()

gameover = pygame.sprite.GroupSingle()


mouse_surf = pygame.Surface((10,10)).convert_alpha()
mouse_surf.fill((0,0,0,0))
pygame.draw.circle(mouse_surf, 'red', (5,5), 5)

def new_wave():
    global enemy, TIME_LIMIT, TIME_REMAINING, wave_indicator, WaveIndicator
    for x in range(int((WAVE_NUMBER*2) * random.choice([0.5, 0.6, 0.7, 0.8, 0.9, 1]))):
        enemy.add(Enemy())

    TIME_LIMIT = pygame.time.get_ticks() + (20 * 1000) + random.choice([x*10 for x in range(1, 5)])
    TIME_REMAINING = (TIME_LIMIT - pygame.time.get_ticks()) / 1000

while True:
    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            exit()
        if events.type == pygame.KEYDOWN:
            if WAVE_ACTIVE == False:
                WAVE_ACTIVE = True
                startup_sfx.play()
                wave_indicator.add(WaveIndicator(complete=False))
                new_wave()
    SCREEN.fill('black')

    land.draw(island.sprite.image)
    enemy.draw(island.sprite.image)
    attack.draw(island.sprite.image)
    player.draw(island.sprite.image)
    particles.draw(island.sprite.image)
    island.sprite.image.blit(player.sprite.pointer_surf, (player.sprite.x_pos, player.sprite.y_pos))

    if pygame.time.get_ticks() % 10 == 0:
        particles.add(Particles(random.randint(2, 5), (land.sprite.rect.right, random.randint(land.sprite.rect.top - 100, land.sprite.rect.bottom + 500)), random.randint(-5, -2), 0, alpha=random.randint(0, 255), color='white',fade_out=False, friction=False))

    island.draw(SCREEN)

    weaponUI.draw(SCREEN)

    wave_indicator.draw(SCREEN)

    if ALIVE == False:
        gameover.draw(SCREEN)
        gameover.update()
    
    else:


        land.update()

        enemy.update()

        attack.update()

        player.update()

        particles.update()

        weaponUI.update()

        wave_indicator.update()

        island.update()

        TIME_REMAINING = round((TIME_LIMIT - pygame.time.get_ticks()) / 1000, 1)
        if TIME_REMAINING <= 0 or len(enemy) == 0:
            if WAVE_ACTIVE == True:
                wave_indicator.add(WaveIndicator(complete=True))
                WAVE_ACTIVE = False
                WAVE_NUMBER += 1
                if len(enemy) !=0:
                    for sprites in enemy.sprites():
                        for x in range(5):
                            particles.add(Particles(10, sprites.rect.center, random.randint(-10, 10), random.randint(-10, 10), color='red', friction=True))
                    enemy.empty()
            TIME_REMAINING = 0

    SCREEN.blit(mouse_surf, pygame.mouse.get_pos())
            

    pygame.display.update()
    clock.tick(60)