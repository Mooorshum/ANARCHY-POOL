import pygame
import time
import os
from math import sqrt, sin, cos, atan2, degrees, hypot, ceil
from statistics import mean
import random


pygame.init()

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)




class Ball:
    def __init__(self, object_folder, x, y):
        self.image = pygame.image.load(f'{object_folder}/balls/idle.png').convert_alpha()
        self.x = x
        self.y = y
        self.radius = int(self.image.get_width()/2) + 1
        self.displacement_ball_collisions = 0
        self.displacement_boundary_collisions = 2
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0 
        self.mass = 1
        self.drag = 1/(50*sqrt(self.vx**2 + self.vy**2) + 100)
        self.damping = 0.5
        self.dt = 0.1
        self.acceleration = 30
        self.goal_status = False
        self.owner = object_folder

    def move(self, background_hitbox):
        self.vx += self.ax * self.dt - self.vx*self.drag
        self.vy += self.ay * self.dt - self.vy*self.drag

        new_x = self.x + self.vx * self.dt
        new_y = self.y + self.vy * self.dt
        hit_boundary_top = background_hitbox.get_at((int(new_x + self.radius), int(new_y))) != WHITE
        hit_boundary_bottom = background_hitbox.get_at((int(new_x + self.radius), int(new_y + 2*self.radius))) != WHITE
        hit_boundary_left = background_hitbox.get_at((int(new_x), int(new_y + self.radius))) != WHITE
        hit_boundary_right = background_hitbox.get_at((int(new_x + 2*self.radius), int(new_y + self.radius))) != WHITE
        if hit_boundary_top:
            self.vy = -self.vy * (1 - self.damping)
        if hit_boundary_bottom:
            self.vy = -self.vy * (1 - self.damping)
        if hit_boundary_left:
            self.vx = -self.vx * (1 - self.damping)
        if hit_boundary_right:
            self.vx = -self.vx * (1 - self.damping)
        if hit_boundary_top:
            new_y += self.displacement_boundary_collisions
        if hit_boundary_bottom:
            new_y -= self.displacement_boundary_collisions
        if hit_boundary_left:
            new_x += self.displacement_boundary_collisions
        if hit_boundary_right:  
            new_x -= self.displacement_boundary_collisions
        self.x = new_x
        self.y = new_y

    def check_collision(self, other_ball):
        dx = (self.x + self.radius) - (other_ball.x + other_ball.radius)
        dy = (self.y + self.radius) - (other_ball.y + other_ball.radius)
        distance = sqrt(dx**2 + dy**2)
        if distance < self.radius + other_ball.radius:
            normal_x = dx/distance
            normal_y = dy/distance
            relative_velocity_x = self.vx - other_ball.vx
            relative_velocity_y = self.vy - other_ball.vy
            velocity_normal = (relative_velocity_x * normal_x) + (relative_velocity_y * normal_y)
            if velocity_normal > 0:
                return
            impulse = (2 * velocity_normal) / (self.mass + other_ball.mass)
            self.vx -= impulse * other_ball.mass * normal_x
            self.vy -= impulse * other_ball.mass * normal_y
            other_ball.vx += impulse * self.mass * normal_x
            other_ball.vy += impulse * self.mass * normal_y
            self.x += self.displacement_ball_collisions * normal_x
            self.y += self.displacement_ball_collisions * normal_y
            other_ball.x -= self.displacement_ball_collisions * normal_x
            other_ball.y -= self.displacement_ball_collisions * normal_y

    def check_goal(self, goal_hitbox):
        goal_status = goal_hitbox.get_at((int(self.x + self.radius), int(self.y + self.radius))) != WHITE
        if goal_status:
            self.vx = 0
            self.vy = 0
            if self.owner != "house":
                game.goal_animations.append({
                    'coords': (self.x, self.y),
                    'start_time': pygame.time.get_ticks(),
                    'owner': self.owner
                })
            self.goal_status = True



    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))




class MainBall(Ball):
    def __init__(self, object_folder, x, y, x_start, y_start):
        super().__init__(object_folder, x, y)
        self.image = pygame.image.load(f'{object_folder}/balls/idle_main.png').convert_alpha()
        self.x_start = x_start
        self.y_start = y_start

    def check_goal(self, goal_hitbox):
        goal_status = goal_hitbox.get_at((int(self.x + self.radius), int(self.y + self.radius))) != WHITE
        if goal_status:
            self.vx = 0
            self.vy = 0
            self.goal_status = True
            game.teleport = True
            game.teleport_start_time = pygame.time.get_ticks()
            game.teleport_x_start = self.x + self.radius
            game.teleport_y_start = self.y + self.radius
            self.x = self.x_start
            self.y = self.y_start




class FunBall(Ball):
    def __init__(self, object_folder, x, y):
        super().__init__(object_folder, x, y)
        self.image = pygame.image.load(f'{object_folder}/balls/idle_fun.png').convert_alpha()
        self.mass = 1
    
    def check_goal(self, goal_hitbox):
        goal_status = goal_hitbox.get_at((int(self.x + self.radius), int(self.y + self.radius))) != WHITE
        if goal_status:
            self.vx = 0
            self.vy = 0
            self.goal_status = True
            counter = 0
            x_bomb = 0
            y_bomb = 0
            for ball in game.balls:
                x_bomb += ball.x
                y_bomb += ball.y
                counter += 1
            x_bomb /= counter
            y_bomb /= counter
            game.bomb_countdown_start_time = pygame.time.get_ticks()
            game.x_bomb = x_bomb
            game.y_bomb = y_bomb
            game.bomb_flag = True




class Cue:
    def __init__(self, object_folder):
        self.image_original = pygame.image.load(f'{object_folder}/cue/cue.png').convert_alpha()
        self.image = self.image_original
        self.strikeline_images = [pygame.image.load(f'{object_folder}/cue/strikeline_{i}.png').convert_alpha() for i in range(10)]
        self.length = int(self.image_original.get_width())
        self.angle = 0
        self.distance_to_ball = 0
        self.max_distance_to_ball = 150
        self.display_threshold = 10
        self.strike_force = 0
        self.ready_status = False
        self.striking = False
        self.has_stricken = False
        self.max_force = 300
        self.wobble_1 = 0.01
        self.wobble_2 = 0.02
        self.wobble_f1 = 3
        self.wobble_f2 = 10

    def get_angle(self, main_ball):
        x_cursor, y_cursor = pygame.mouse.get_pos()
        true_angle = atan2(main_ball.y + main_ball.radius - y_cursor, main_ball.x + main_ball.radius - x_cursor)
        if self.striking:
            wobble_offset = (self.wobble_1 * self.distance_to_ball/self.max_distance_to_ball * sin(time.time() * self.wobble_f1)) + (self.wobble_2 * self.distance_to_ball/self.max_distance_to_ball * sin(time.time() * self.wobble_f2))
        else:
            wobble_offset = 0
        self.angle = true_angle + wobble_offset

    def check_status(self, balls):
        main_ball = balls[0]
        main_ball_v = sqrt(main_ball.vx**2 + main_ball.vy**2)
        if (game.total_v < self.display_threshold) and main_ball_v < self.display_threshold:
            self.ready_status = True


    def calculate_force(self, main_ball):
        x_cursor, y_cursor = pygame.mouse.get_pos()
        self.distance_to_ball = sqrt((x_cursor - (main_ball.x + main_ball.radius)) ** 2 + (y_cursor - (main_ball.y + main_ball.radius)) ** 2)
        if self.distance_to_ball > self.max_distance_to_ball:
            self.distance_to_ball = self.max_distance_to_ball
        self.strike_force = self.max_force*self.distance_to_ball/self.max_distance_to_ball

    def draw(self, main_ball, screen):
        if self.ready_status and not game.win_con:
            rotated_cue = pygame.transform.rotate(self.image_original, -degrees(self.angle))
            rotated_rect_cue = rotated_cue.get_rect()
            self.image = pygame.transform.smoothscale(rotated_cue, (rotated_rect_cue.width, rotated_rect_cue.height))
            self.x = main_ball.x + main_ball.radius - (self.length/2 + self.distance_to_ball)*cos(self.angle) - rotated_rect_cue.width // 2
            self.y = main_ball.y + main_ball.radius - (self.length/2 + self.distance_to_ball)*sin(self.angle) - rotated_rect_cue.height // 2
            screen.blit(self.image, (self.x, self.y))

            if self.striking:
                n = round(self.distance_to_ball / self.max_distance_to_ball * 9)
                strikeline_image = self.strikeline_images[n]
                strikeline_length = int(strikeline_image.get_width())
                strikeline_image_rotated = pygame.transform.rotate(strikeline_image, -degrees(self.angle))
                rotated_strikeline_rect = strikeline_image_rotated.get_rect()
                strikeline_x = (main_ball.x + main_ball.radius) - (self.distance_to_ball - strikeline_length/2)*cos(self.angle) - rotated_strikeline_rect.width // 2
                strikeline_y = (main_ball.y + main_ball.radius) - (self.distance_to_ball - strikeline_length/2)*sin(self.angle) - rotated_strikeline_rect.height // 2
                screen.blit(strikeline_image_rotated, (strikeline_x, strikeline_y))


    def strike(self, main_ball):
        if self.ready_status:
            self.striking = True
            main_ball.vx = self.strike_force*cos(self.angle)
            main_ball.vy = self.strike_force*sin(self.angle)
            self.displacement = 0
            self.striking = False
            self.ready_status = False
            self.has_stricken = True




class Game:
    def __init__(self):
        self.screen_width = 960
        self.screen_height = 540
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.SCALED)
        pygame.display.set_caption("ANARCHY POOL")

        self.background = pygame.image.load("background/background.png").convert()
        self.startscreen_background = pygame.image.load("startscreen/startscreen_background.png").convert()

        self.background_hitbox = pygame.image.load("background/background_hitbox.png").convert()
        self.goal_hitbox = pygame.image.load("background/goal_hitbox.png").convert()

        self.startscreen_clickbox = pygame.image.load("startscreen/startscreen_clickbox.png").convert()
        self.menu_mini_clickbox = pygame.image.load("menu/menu_mini/menu_mini_clickbox.png")
        self.rules_clickbox = pygame.image.load("menu/rules/rules_clickbox.png").convert_alpha()
        self.about_clickbox = pygame.image.load("menu/about/about_clickbox.png").convert_alpha()
        self.menu_detailed_clickbox = pygame.image.load("menu/menu_detailed/menu_detailed_clickbox.png")
        self.pause_region = pygame.image.load("menu/pause_region.png")

        self.goal_animation_duration = 500
        self.goal_num_frames = 24
        self.goal_positions = [
            (63, 87),
            (418, 80),
            (773,87),
            (63, 454),
            (418, 460),
            (773, 454),
        ]
        self.x_main_start, self.y_main_start = (210, 260)
        self.x_leftmost_ball_start, self.y_leftmost_ball_start = (560, 260)
        self.offset_extra = 1

        self.teleport = False
        self.teleport_animation_duration = 500
        self.teleport_start_time = 0
        self.teleport_x_start = 0
        self.teleport_y_start = 0
        self.teleport_x_end = self.x_main_start
        self.teleport_y_end = self.y_main_start
        
        self.bomb_flag = False
        self.explode_flag = False
        self.explosion_animation_flag = False
        self.bomb_countdown_start_time = 0
        self.explosion_time = 0
        self.x_bomb = 0
        self.y_bomb =0

        self.player_number = 0
        self.player_number_init = 0
        
        self.players_start = ["player_1", "player_2", "player_3", "player_4", "house"]
        self.players = self.players_start
        self.cue = Cue(self.players[0])
        self.active_player_index = 0
        self.ball_ownership = []
        self.balls = []
        self.main_ball = None
        self.total_v = 0
        self.scored_this_turn = False
        self.win_con = False
        self.paused = False
        self.start_flag = False
        self.startscreen_flag = True
        self.goal_animations = []
        self.menu_opened = False
        self.rules_opened = False
        self.about_opened = False
        self.click = False

        self.clock = pygame.time.Clock()
        self.running = True


    def run(self):
        while self.running:
            if (self.startscreen_flag == True):
                self.show_and_monitor_startscreen(self.screen)
                self.clock.tick(60)
            else:
                if self.start_flag:
                    self.balls_start()
                self.check_for_pause()
                self.handle_events()
                self.update_screen_game()
                self.handle_collisions()
                self.get_total_speed()
                self.check_turn_switch()
                self.remove_player()
                self.check_win_con(self.players)
            self.clock.tick(60)
        pygame.quit()


    def handle_events(self):
        self.click = False
        if self.paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.click = True
                    if (self.open_close_menu):
                        if not self.menu_opened:
                            self.menu_opened = True
                        else:
                            self.menu_opened = False

                    if (self.rules_close):
                        self.rules_opened = False

                    if (self.about_opened):
                        self.about_opened = False
        if not self.paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if (self.cue.ready_status):
                        self.cue.striking = True
                        self.cue.calculate_force(self.main_ball)
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.cue.ready_status:
                        self.cue.strike(self.main_ball)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.main_ball.ax = -self.main_ball.acceleration
            elif keys[pygame.K_RIGHT]:
                self.main_ball.ax = self.main_ball.acceleration
            elif keys[pygame.K_SPACE]:
               self.cue.strike(self.main_ball)
            else:
                self.main_ball.ax = 0
            if keys[pygame.K_UP]:
                self.main_ball.ay = -self.main_ball.acceleration
            elif keys[pygame.K_DOWN]:
                self.main_ball.ay = self.main_ball.acceleration
            else:
                self.main_ball.ay = 0
            if self.cue.ready_status:
                self.cue.calculate_force(self.main_ball)
            if self.explode_flag:
                    self.explosion(self.x_bomb, self.y_bomb)
            self.monitor_balls()
            self.cue.check_status(self.balls)
            self.cue.get_angle(self.main_ball)


    def update_screen_game(self):
        self.screen.blit(self.background, (0, 0))
        for ball in self.balls:
            ball.draw(self.screen)
        if not self.win_con:
            self.cue.draw(self.main_ball, self.screen)
        else:
            self.show_winscreen(self.screen)
        if self.teleport:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.teleport_start_time
            if elapsed_time <= self.teleport_animation_duration:
                self.main_ball_teleporting_animation(self.screen, elapsed_time, self.teleport_x_start, self.teleport_y_start, self.teleport_x_end, self.teleport_y_end)
            else:
                self.teleport = False
        if self.bomb_flag:
            self.display_bomb_countdown_animation(self.screen, self.x_bomb, self.y_bomb)
        if self.explosion_animation_flag:
            self.display_explosion(self.screen, self.x_bomb, self.y_bomb)
        self.display_goal_animation(self.screen)
        self.show_and_monitor_menu(self.screen)
        self.show_and_update_turn_indicators_and_healthbars(self.screen)
        pygame.display.update()



    def balls_start(self):
        self.players = self.players_start
        self.balls = []
        self.cue = Cue(self.players[0])
        default_ball = pygame.image.load("house/balls/idle.png").convert()
        r = default_ball.get_height()/2
        offset_x = 2 * sin(3.1415 / 3) * r
        offset_y = 2 * cos(3.1415 / 3) * r
        x1, y1 = (self.x_leftmost_ball_start, self.y_leftmost_ball_start)
        x2, y2 = (x1 + offset_x + self.offset_extra, y1 - offset_y - self.offset_extra)
        x3, y3 = (x1 + offset_x + self.offset_extra, y1 + offset_y + self.offset_extra)
        x4, y4 = (x1 + 2 * (offset_x + self.offset_extra), y1 - 2 * (offset_y + self.offset_extra))
        x5, y5 = (x1 + 2 * (offset_x + self.offset_extra), y1 + 2 * (offset_y + self.offset_extra))
        x6, y6 = (x1 + 2 * (offset_x + self.offset_extra), y1)
        x7, y7 = (x1 + 3 * (offset_x + self.offset_extra), y1 - (offset_y + self.offset_extra))
        x8, y8 = (x1 + 3 * (offset_x + self.offset_extra), y1 + (offset_y + self.offset_extra))
        x9, y9 = (x1 + 3 * (offset_x + self.offset_extra), y1 - 3 * (offset_y + self.offset_extra))
        x10, y10 = (x1 + 3 * (offset_x + self.offset_extra), y1 + 3 * (offset_y + self.offset_extra))
        x11, y11 = (x1 + 4 * (offset_x + self.offset_extra), y1 + 4 * (offset_y + self.offset_extra))
        x12, y12 = (x1 + 4 * (offset_x + self.offset_extra), y1 + 2 * (offset_y + self.offset_extra))
        x13, y13 = (x1 + 4 * (offset_x + self.offset_extra), y1 - 4 * (offset_y + self.offset_extra))
        x14, y14 = (x1 + 4 * (offset_x + self.offset_extra), y1 - 2 * (offset_y + self.offset_extra))
        x15, y15 = (x1 + 4 * (offset_x + self.offset_extra), y1)
        x_list = [x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15]
        y_list = [y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12, y13, y14, y15]
        combined_list = list(zip(x_list, y_list))
        random.shuffle(combined_list)
        x_list, y_list = zip(*combined_list)
        x_list = list(x_list)
        y_list = list(y_list)
        if self.player_number == 2:
            self.ball_ownership = [0, 1, 1, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 2, 0]
        if self.player_number == 3:
            self.ball_ownership = [0, 1, 1, 1, 1, 2, 2, 2, 0, 2, 3, 3, 3, 3, 0, 0]
        if self.player_number == 4:
            self.ball_ownership = [0, 1, 1, 1, 2, 2, 2, 3, 0, 3, 3, 4, 4, 4, 0, 0]
        white_flag = False
        for i in range(16):
            if self.ball_ownership[i] != 0:
                ball = Ball(self.players[self.ball_ownership[i] - 1], x_list[i - 1], y_list[i - 1])
            elif self.ball_ownership[i] == 0:
                if not white_flag:
                    ball = MainBall(self.players[-1], self.x_main_start, self.y_main_start, self.x_main_start, self.y_main_start)
                    self.main_ball = ball
                    white_flag = True
                else:
                    ball = FunBall(self.players[-1], x_list[i - 1], y_list[i - 1])
            self.balls.append(ball)
        self.start_flag = False


    def handle_collisions(self):
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                self.balls[i].check_collision(self.balls[j])


    def remove_player(self):
        players_left = []
        for ball in self.balls:
            if (ball.owner not in players_left) and (ball.owner != "house"):
                players_left.append(ball.owner)
        players_left.sort()
        self.players = players_left


    def main_ball_teleporting_animation(self, screen, elapsed_time, x, y, x_end, y_end):
        num_frames = 10
        frame_index = (elapsed_time % self.teleport_animation_duration) // (self.teleport_animation_duration // num_frames)
        try:
            current_image = pygame.image.load(f"house/balls/teleport_animation/teleport_{frame_index}.png").convert_alpha()
            screen.blit(current_image, (x - int(current_image.get_width() / 2), y - int(current_image.get_height() / 2)))
            screen.blit(current_image, (x_end - int(current_image.get_width() / 2), y_end - int(current_image.get_height() / 2)))
        except (FileNotFoundError, UnboundLocalError):
            pass


    def display_bomb_countdown_animation(self, screen, x, y):
        countdown_duration = 1500
        num_frames = 24
        start_time = self.bomb_countdown_start_time
        current_time = pygame.time.get_ticks()
        frame_index = int(current_time - start_time)//(countdown_duration // num_frames)
        try:
            current_image = pygame.image.load(f"house/balls/explosion/countdown_{frame_index}.png").convert_alpha()
            screen.blit(current_image, (x - current_image.get_width() // 2, y - current_image.get_height() // 2))
        except FileNotFoundError:
            pass
        if current_time - start_time >= countdown_duration:
            self.explode_flag = True
            

    def explosion(self, x_bomb, y_bomb):
        explosion_radius = 300
        explosion_force = 200
        self.explosion_animation_flag = True
        for ball in self.balls:
            distance_x = ball.x - x_bomb
            distance_y = ball.y - y_bomb
            distance = (distance_x ** 2 + distance_y ** 2) ** 0.5
            if distance < explosion_radius:
                force = explosion_force * (1 - distance / explosion_radius)
                angle = atan2(distance_y, distance_x)
                ball.vx += force * cos(angle) / ball.mass
                ball.vy += force * sin(angle) / ball.mass
        self.explosion_time = pygame.time.get_ticks()
        self.bomb_flag = False
        self.explode_flag = False
        

    def display_explosion(self, screen, x, y):
        animation_duration = 500
        num_frames = 10
        start_time = self.explosion_time
        current_time = pygame.time.get_ticks()
        frame_index = int(current_time - start_time)//(animation_duration // num_frames)
        if frame_index < num_frames:
            try:
                current_image = pygame.image.load(f"house/balls/explosion/explosion_{frame_index}.png").convert_alpha()
                screen.blit(current_image, (x - current_image.get_width() // 2, y - current_image.get_height() // 2))
            except FileNotFoundError:
                pass
        if current_time > start_time + animation_duration:
            self.explosion_animation_flag = False
        

    def check_turn_switch(self):
        if len(self.players) > 1:
            if self.cue.ready_status and self.cue.has_stricken:
                if not self.scored_this_turn:
                    if self.active_player_index >= (len(self.players)-1):
                        self.active_player_index = 0
                    else:
                        self.active_player_index += 1
                    self.cue = Cue(self.players[self.active_player_index])
                self.cue.has_stricken = False
                self.scored_this_turn = False


    def check_win_con(self, players):
        if (len(players) == 1) and not(self.paused):
            self.win_con = True


    def show_winscreen(self, screen):
        x_winscreen = self.screen_width/2
        y_winscreen = self.screen_height/2
        player_win_screen = pygame.image.load(f'{self.players[0]}/win_screen.png').convert_alpha()
        self.screen.blit(player_win_screen, (x_winscreen - player_win_screen.get_width()/2, y_winscreen - player_win_screen.get_height()/2))


    def monitor_balls(self):
        for ball in self.balls:
            ball.move(self.background_hitbox)
            ball.check_goal(self.goal_hitbox)
            try:
                if (ball.goal_status) and (not isinstance(ball, MainBall)) and (ball.owner != self.players[self.active_player_index]):
                    self.scored_this_turn = True
            except IndexError:
                pass
        self.balls = [ball for ball in self.balls if not ball.goal_status or isinstance(ball, MainBall)]


    def display_goal_animation(self, screen):
        current_time = pygame.time.get_ticks()
        if self.goal_animations:
            for animation in self.goal_animations[:]:
                if current_time - animation['start_time'] > self.goal_animation_duration:
                    self.goal_animations.remove(animation)
                    continue
                elapsed_time = current_time - animation['start_time']
                current_frame = (elapsed_time // (self.goal_animation_duration // self.goal_num_frames))
                try:
                    goal_image = pygame.image.load(f'{animation["owner"]}/balls/goal_{current_frame}.png').convert_alpha()
                    x, y = animation['coords']
                    image_width = goal_image.get_width()
                    image_height = goal_image.get_height()
                    closest_position = min(self.goal_positions, key=lambda pos: hypot(pos[0] - x, pos[1] - y))
                    centered_x = closest_position[0] - image_width // 2
                    centered_y = closest_position[1] - image_height // 2
                    screen.blit(goal_image, (centered_x, centered_y))
                except FileNotFoundError:
                    pass


    def show_and_monitor_menu(self, screen):
        x_menu = 837
        y_menu = 46

        x_rules = 107
        y_rules = 149

        menu_mini = pygame.image.load("menu/menu_mini/menu_mini_0.png").convert_alpha()
        menu_mini_hovering_menu = pygame.image.load("menu/menu_mini/menu_mini_1.png").convert_alpha()
        menu_mini_hovering_restart = pygame.image.load("menu/menu_mini/menu_mini_2.png").convert_alpha()
        menu_detailed_opened = pygame.image.load("menu/menu_detailed/menu_0.png").convert_alpha()
        menu_detailed_hovering_rules = pygame.image.load("menu/menu_detailed/menu_1.png").convert_alpha()
        menu_detailed_hovering_about = pygame.image.load("menu/menu_detailed/menu_2.png").convert_alpha()
        menu_detailed_hovering_exit = pygame.image.load("menu/menu_detailed/menu_3.png").convert_alpha()

        rules_idle = pygame.image.load("menu/rules/rules_0.png").convert_alpha()
        rules_hover_close = pygame.image.load("menu/rules/rules_1.png").convert_alpha()

        about_idle = pygame.image.load("menu/about/about_0.png").convert_alpha()
        about_hover_close = pygame.image.load("menu/about/about_1.png").convert_alpha()

        x_cursor, y_cursor = pygame.mouse.get_pos()
     
        self.rules_close = (self.rules_clickbox.get_at((int(x_cursor), int(y_cursor))) == RED)
        self.open_close_menu = (self.menu_mini_clickbox.get_at((int(x_cursor), int(y_cursor))) == RED)
        restart = self.menu_mini_clickbox.get_at((int(x_cursor), int(y_cursor))) == GREEN 

        if self.menu_opened:
            open_rules = self.menu_detailed_clickbox.get_at((int(x_cursor), int(y_cursor))) == RED
            open_about_page = self.menu_detailed_clickbox.get_at((int(x_cursor), int(y_cursor))) == GREEN
            finish_game = self.menu_detailed_clickbox.get_at((int(x_cursor), int(y_cursor))) == BLUE

        if not self.menu_opened:
            screen.blit(menu_mini, (x_menu, y_menu))
            if (self.open_close_menu):
                screen.blit(menu_mini_hovering_menu, (x_menu, y_menu))
        
        if self.menu_opened:
            screen.blit(menu_detailed_opened, (x_menu, y_menu))

            if open_rules:
                screen.blit(menu_detailed_hovering_rules, (x_menu, y_menu))
                if self.click:
                    self.menu_opened = False
                    self.rules_opened = True

            if open_about_page:
                screen.blit(menu_detailed_hovering_about, (x_menu, y_menu))
                if self.click:
                    self.menu_opened = False
                    self.about_opened = True

            if finish_game:
                screen.blit(menu_detailed_hovering_exit, (x_menu, y_menu))
                if self.click == True:
                    self.win_con = False
                    self.startscreen_flag = True
                    self.player_number = 0
                    self.menu_opened = False
                    self.paused = False

        if self.rules_opened:
            screen.blit(rules_idle, (x_rules, y_rules))
            if self.rules_close:
                screen.blit(rules_hover_close, (x_rules, y_rules))

        if self.about_opened:
            screen.blit(about_idle, (x_rules, y_rules))
            if self.rules_close:
                screen.blit(about_hover_close, (x_rules, y_rules))

        if restart and not self.menu_opened:
            screen.blit(menu_mini_hovering_restart, (x_menu, y_menu))
            if self.click == True:
                self.start_flag = True
                self.win_con = False


    def show_and_monitor_startscreen(self, screen):
        y_offset_jumping_ball = -80
        x_jumping_ball = self.startscreen_background.get_width()/2 + 285
        y_jumping_ball = self.startscreen_background.get_height()/2 - y_offset_jumping_ball
        y_offset_cues = 100
        x_cues = self.startscreen_background.get_width()/2
        y_cues = self.startscreen_background.get_height()/2 - y_offset_cues
        x_exit_button = 838
        y_exit_button = 46
        y_offset_play_button = 214
        x_play_button = self.startscreen_background.get_width()/2
        y_play_button = self.startscreen_background.get_height()/2 + y_offset_play_button
        x_offset_choices = 200
        y_offset_choices = 150
        x_two_players = self.startscreen_background.get_width()/2 - x_offset_choices
        y_two_players = self.startscreen_background.get_height()/2 + y_offset_choices
        x_three_players = self.startscreen_background.get_width()/2
        y_three_players = self.startscreen_background.get_height()/2 + y_offset_choices
        x_four_players = self.startscreen_background.get_width()/2 + x_offset_choices
        y_four_players = self.startscreen_background.get_height()/2 + y_offset_choices
        x_cursor, y_cursor = pygame.mouse.get_pos()
        two_players = pygame.image.load("startscreen/2_players.png").convert_alpha()
        two_players_hovering = pygame.image.load("startscreen/2_players_hovering.png").convert_alpha()
        two_players_chosen = pygame.image.load("startscreen/2_players_chosen.png").convert_alpha()
        two_cues = pygame.image.load("startscreen/2_cues.png").convert_alpha()
        three_players = pygame.image.load("startscreen/3_players.png").convert_alpha()
        three_players_hovering = pygame.image.load("startscreen/3_players_hovering.png").convert_alpha()
        three_players_chosen = pygame.image.load("startscreen/3_players_chosen.png").convert_alpha()
        three_cues = pygame.image.load("startscreen/3_cues.png").convert_alpha()
        four_players = pygame.image.load("startscreen/4_players.png").convert_alpha()
        four_players_hovering = pygame.image.load("startscreen/4_players_hovering.png").convert_alpha()
        four_players_chosen = pygame.image.load("startscreen/4_players_chosen.png").convert_alpha()
        four_cues = pygame.image.load("startscreen/4_cues.png").convert_alpha()
        play_button = pygame.image.load("startscreen/play_button.png").convert_alpha()
        play_button_hovering = pygame.image.load("startscreen/play_button_hovering.png").convert_alpha()
        exit_button = pygame.image.load("startscreen/exit_button.png").convert_alpha()
        exit_button_hovering = pygame.image.load("startscreen/exit_button_hovering.png").convert_alpha()
        choose_player_number_tip = pygame.image.load("startscreen/choose_button_default.png").convert_alpha()
        two_players_hover_flag = self.startscreen_clickbox.get_at((int(x_cursor), int(y_cursor))) == RED
        three_players_hover_flag = self.startscreen_clickbox.get_at((int(x_cursor), int(y_cursor))) == GREEN
        four_players_hover_flag = self.startscreen_clickbox.get_at((int(x_cursor), int(y_cursor))) == BLUE
        play_button_hover_flag = self.startscreen_clickbox.get_at((int(x_cursor), int(y_cursor))) == YELLOW
        choose_exit = self.startscreen_clickbox.get_at((int(x_cursor), int(y_cursor))) == WHITE
        screen.blit(self.startscreen_background, (0, 0))
        self.blit_jumping_ball_animation(screen, x_jumping_ball, y_jumping_ball)
        screen.blit(exit_button, (x_exit_button, y_exit_button))
        if self.player_number == 2:
            screen.blit(two_players_chosen, (x_two_players - two_players_chosen.get_width()/2, y_two_players - two_players_chosen.get_height()/2))
            screen.blit(two_cues, (x_cues - two_cues.get_width()/2, y_cues - two_cues.get_height()/2))
        elif two_players_hover_flag:
            screen.blit(two_players_hovering, (x_two_players - two_players_hovering.get_width()/2, y_two_players - two_players_hovering.get_height()/2))
        else:
            screen.blit(two_players, (x_two_players - two_players.get_width()/2, y_two_players - two_players.get_height()/2))
        if self.player_number == 3:
            screen.blit(three_players_chosen, (x_three_players - three_players_chosen.get_width()/2, y_three_players - three_players_chosen.get_height()/2))
            screen.blit(three_cues, (x_cues - three_cues.get_width()/2, y_cues - three_cues.get_height()/2))
        elif three_players_hover_flag:
            screen.blit(three_players_hovering, (x_three_players - three_players_hovering.get_width()/2, y_three_players - three_players_hovering.get_height()/2))
        else:
            screen.blit(three_players, (x_three_players - three_players.get_width()/2, y_two_players - three_players.get_height()/2))
        if self.player_number == 4:
            screen.blit(four_players_chosen, (x_four_players - four_players_chosen.get_width()/2, y_four_players - four_players_chosen.get_height()/2))
            screen.blit(four_cues, (x_cues - four_cues.get_width()/2, y_cues - four_cues.get_height()/2))
        elif four_players_hover_flag:
            screen.blit(four_players_hovering, (x_four_players - four_players_hovering.get_width()/2, y_four_players - four_players_hovering.get_height()/2))
        else:
            screen.blit(four_players, (x_four_players - four_players.get_width()/2, y_four_players - four_players.get_height()/2))
        if (self.player_number == 0):
            self.blit_choose_player_number_tip_animation(screen, x_play_button - choose_player_number_tip.get_width() / 2, y_play_button - choose_player_number_tip.get_height() / 2)
        elif play_button_hover_flag:
            screen.blit(play_button_hovering, (x_play_button - play_button.get_width()/2, y_play_button - play_button.get_height()/2))
        else:
            self.blit_blay_button_animation(screen, x_play_button - play_button.get_width()/2, y_play_button - play_button.get_height()/2)
        if choose_exit:
            screen.blit(exit_button_hovering, (x_exit_button, y_exit_button))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if choose_exit:
                    self.running = False
                if two_players_hover_flag:
                    self.player_number = 2
                    self.player_number_init = 2
                if three_players_hover_flag:
                    self.player_number = 3
                    self.player_number_init = 3
                if four_players_hover_flag:
                    self.player_number = 4
                    self.player_number_init = 4
                if (play_button_hover_flag) and (self.player_number > 1):
                    self.start_flag = True
                    self.startscreen_flag = False
        pygame.display.update()


    def blit_choose_player_number_tip_animation(self, screen, x, y):
        animation_duration = 1200
        num_frames = 20
        current_time = pygame.time.get_ticks()
        frame_index = (current_time % animation_duration) // (animation_duration // num_frames)
        current_image = pygame.image.load(f"startscreen/player_number_tip_{frame_index}.png").convert_alpha()
        screen.blit(current_image, (x, y))


    def blit_blay_button_animation(self, screen, x, y):
        animation_duration = 1200
        num_frames = 20
        current_time = pygame.time.get_ticks()
        frame_index = (current_time % animation_duration) // (animation_duration // num_frames)
        current_image = pygame.image.load(f"startscreen/play_button_{frame_index}.png").convert_alpha()
        screen.blit(current_image, (x, y))


    def blit_jumping_ball_animation(self, screen, x, y):
        animation_duration = 3000
        num_frames = 114
        current_time = pygame.time.get_ticks()
        frame_index = (current_time % animation_duration) // (animation_duration // num_frames)
        try:
            current_image = pygame.image.load(f"startscreen/jump_{frame_index}.png").convert_alpha()
        except FileNotFoundError:
            pass
        try:
            screen.blit(current_image, (x - int(current_image.get_width()/2), y - int(current_image.get_height()/2)))
        except UnboundLocalError:
            pass


    def show_and_update_turn_indicators_and_healthbars(self, screen):

        x_player_emblem = 837
        y_player_emblems = {
            "player_1": 200,
            "player_2": 270,
            "player_3": 340,
            "player_4": 410
        }
        y_healthbar_offset = 30

        player_1 = pygame.image.load("player_1/emblem.png").convert_alpha()
        player_1_active = pygame.image.load("player_1/emblem_active.png").convert_alpha()
        
        player_2 = pygame.image.load("player_2/emblem.png").convert_alpha()
        player_2_active = pygame.image.load("player_2/emblem_active.png").convert_alpha()

        player_3 = pygame.image.load("player_3/emblem.png").convert_alpha()
        player_3_active = pygame.image.load("player_3/emblem_active.png").convert_alpha()

        player_4 = pygame.image.load("player_4/emblem.png").convert_alpha()
        player_4_active = pygame.image.load("player_4/emblem_active.png").convert_alpha()

        player_emblems = {
            "player_1": player_1,
            "player_2": player_2,
            "player_3": player_3,
            "player_4": player_4
        }

        player_emblems_active = {
            "player_1": player_1_active,
            "player_2": player_2_active,
            "player_3": player_3_active,
            "player_4": player_4_active
        }

        for player in self.players:
            if player != "house":
                screen.blit(player_emblems[player], (x_player_emblem, y_player_emblems[player]))
                screen.blit(self.get_healthbar(player), (x_player_emblem, y_player_emblems[player] + y_healthbar_offset))
                try:
                    if self.players[self.active_player_index] == player:
                        screen.blit(player_emblems_active[player], (x_player_emblem, y_player_emblems[player]))
                except IndexError:
                    pass


    def get_healthbar(self, player):
        current_health = 0
        if self.player_number_init == 2:
            max_health = 6
        if self.player_number_init == 3:
            max_health = 4
        if self.player_number_init == 4:
            max_health = 3
        for ball in self.balls:
            if player == ball.owner:
                current_health += 1
        health_percentage = (current_health / max_health) * 100
        healthbar_index = min(ceil(health_percentage / 10) * 10, 100)
        healthbar_image = pygame.image.load(f"{player}/healthbar/healthbar_{healthbar_index}.png").convert_alpha()
        return healthbar_image


    def check_for_pause(self):
        x_cursor, y_cursor = pygame.mouse.get_pos()
        pause_condition = (self.pause_region.get_at((int(x_cursor), int(y_cursor))) == WHITE) or self.win_con
        if pause_condition or self.menu_opened or self.rules_opened or self.about_opened:
            self.paused = True
        else:
            self.paused = False


    def get_total_speed(self):
        total_v = 0
        for ball in self.balls:
            total_v += sqrt(ball.vx**2 + ball.vy**2)
        self.total_v = total_v


if __name__ == "__main__":
    game = Game()
    game.run()
