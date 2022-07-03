import pygame
import random
import colorsys
from pygame.locals import *

pygame.init()
# Constants
SIZE = 30
BORDER = 3
LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
# Colors
WHITE = [255, 255, 255]
YELLOW = [255, 255, 0]
YELLOW_LIGHT = [255, 235, 39]
RED = [254, 8, 59]
BLACK = [0, 0, 0]
BLACK1 = [18, 18, 18]
BLUE = [33, 61, 252]


class Color():
    def __init__(self):
        self.value = [100,100,100]

    def random_color(self):
        # bright colors
        h, s, l = random.random(), random.uniform(0.7, 1.0), random.uniform(0.4, 0.65)
        rgb_color = colorsys.hls_to_rgb(h, l, s)
        for i in range(3):
            self.value[i] = int(rgb_color[i]*256)

    def get_rgb(self):
        return getattr(self, 'value')


class Apple():
    def __init__(self, game_screen, snake):
        self.color = Color()
        self.color.random_color()
        self.game_screen = game_screen
        self.snake = snake
        self.x = 0
        self.y = 0
        self.new_position()

    def draw(self):
        rect1 = pygame.Rect(self.x, self.y, SIZE, SIZE)
        pygame.draw.rect(self.game_screen, self.color.value, rect1)

    def new_position(self):
        coord_x = self.random_xcoordinate()
        coord_y = self.random_ycoordinate()
        if self.coord_in_snake(coord_x, coord_y):
            return self.new_position()
        self.x = coord_x
        self.y = coord_y

    def coord_in_snake(self, coord_x, coord_y):
        for i in range(self.snake.length):
            if coord_x == self.snake.x[i] and coord_y == self.snake.y[i]:
                return True
        return False

    def random_xcoordinate(self):
        coord = random.randrange(self.game_screen.get_width()//SIZE)*SIZE
        return coord

    def random_ycoordinate(self):
        coord = random.randrange(self.game_screen.get_height()//SIZE)*SIZE
        return coord


class Snake():
    def __init__(self, game_screen, length):
        self.game_screen = game_screen
        self.direction = RIGHT
        self.length = length
        self.new()

    def draw(self):
        for i in range(self.length):
            # solid 
            # pygame.draw.rect(self.game_screen, WHITE,
            #                  pygame.Rect(self.x[i], self.y[i], SIZE, SIZE))
            # pygame.draw.rect(self.game_screen, self.color[i],
            #                  pygame.Rect(self.x[i]+BORDER, self.y[i]+BORDER, SIZE-(BORDER*2), SIZE-(BORDER*2)))
            # line
            pygame.draw.rect(self.game_screen, self.color[i],
                             pygame.Rect(self.x[i], self.y[i], SIZE, SIZE))
            pygame.draw.rect(self.game_screen, WHITE,
                             pygame.Rect(self.x[i]+BORDER, self.y[i]+BORDER, SIZE-(BORDER*2), SIZE-(BORDER*2)))

    def move(self):
        # Move body
        for i in range(self.length-1, 0, -1):
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]
        # Move Head and if the head reaches an edge teleport to opposite edge
        if self.length > 0:
            if self.direction == LEFT:
                self.x[0] = (self.x[0] - SIZE) % self.game_screen.get_width()
            elif self.direction == RIGHT:
                self.x[0] = (self.x[0] + SIZE) % self.game_screen.get_width()
            elif self.direction == UP:
                self.y[0] = (self.y[0] - SIZE) % self.game_screen.get_height()
            elif self.direction == DOWN:
                self.y[0] = (self.y[0] + SIZE) % self.game_screen.get_height()

            self.draw()

    def increase_size(self, apple):
        self.x.append(0)
        self.y.append(0)
        local_rgb = apple.color.value.copy()
        self.color.append(local_rgb)

        self.length += 1

    def clear(self):
        self.x.clear()
        self.y.clear()
        self.color.clear()
        self.length = 1
        self.new()

    def new(self):
        center_x = ((self.game_screen.get_width() // 2) // SIZE) * SIZE
        center_y = ((self.game_screen.get_height() // 2) // SIZE) * SIZE
        self.x = [center_x]*self.length
        self.y = [center_y]*self.length
        self.color = [WHITE]*self.length

    def move_left(self):
        if self.length == 1 or self.direction != RIGHT:
            self.direction = LEFT

    def move_right(self):
        if self.length == 1 or self.direction != LEFT:
            self.direction = RIGHT

    def move_up(self):
        if self.length == 1 or self.direction != DOWN:
            self.direction = UP

    def move_down(self):
        if self.length == 1 or self.direction != UP:
            self.direction = DOWN


class SnakeGame:
    def __init__(self):
        pygame.mixer.init()
        self.surface = pygame.display.set_mode(size=(900, 600))
        self.snake = Snake(self.surface, 8)
        self.apple = Apple(self.surface, self.snake)
        # self.play_bg_music()
        self.clock = pygame.time.Clock()
        self.start_time = pygame.time.get_ticks()
        self.speed = 5
        self.scores = []
        self.load_scores()

    def update(self):
        self.render_bg()
        self.snake.move()
        self.ate_apple()
        self.apple.draw()
        self.show_score()
        self.count_time()

        if self.snake_collition():
            self.play_sound("crash")
            raise NameError("pause")

        pygame.display.flip()

    def render_bg(self):
        self.surface.fill(BLACK1)

    def count_time(self):
        font = pygame.font.SysFont("consolas", 30)
        time = pygame.time.get_ticks() - self.start_time

        time_string = self.format_time(time)

        time_text = font.render(str(time_string), 1, WHITE)
        x = self.surface.get_width() - time_text.get_width()
        self.surface.blit(time_text, (x, 0))

    def ate_apple(self):
        if self.is_collition(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.play_sound("ding")
            self.snake.increase_size(self.apple)
            self.apple.color.random_color()
            self.apple.new_position()
            self.speed += 0.5

    def snake_collition(self):
        for i in range(3, self.snake.length):
            if self.is_collition(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                return True
        return False

    def is_collition(self, x1, y1, x2, y2):
        
        if (x1 == x2 and y1 == y2):
            return True
        return False

    def show_score(self):
        font = pygame.font.SysFont("arial", 30)
        score = font.render(f"Score: {self.snake.length}", True, WHITE)
        self.surface.blit(score, (0, 0))

    def play_sound(self, name):
        sound = pygame.mixer.Sound(f"resources/{name}.mp3")
        pygame.mixer.Sound.play(sound)

    def show_game_over(self):
        time = self.get_time()
        self.add_score(time)

        self.render_bg()

        font = pygame.font.SysFont("arial", 20)
        text_line1 = font.render(f"Score: {self.snake.length}", True, WHITE)
        text_line2 = font.render("Press ENTER to play again", True, WHITE)
        text_line3 = font.render("Press ESC to exit", True, WHITE)
        text_line1.get_width()
        center = int(self.surface.get_width() / 2)
        self.surface.blit(text_line1, (center - text_line1.get_width()//2, 50))
        self.surface.blit(text_line2, (center - text_line2.get_width()//2, 80))
        self.surface.blit(
            text_line3, (center - text_line3.get_width()//2, 110))
        self.show_score_list(time)
        pygame.display.flip()
        self.snake.length = 1

    def show_score_list(self, current_time):
        font = pygame.font.SysFont("consolas", 20)
        text = font.render("Time     Points", True, WHITE)
        text_y = 150
        self.surface.blit(text, (400, text_y))
        for score, time in self.scores:
            text_y += 30
            color_render = WHITE
            time_string = self.format_time(time)
            if score == self.snake.length and time == current_time:
                color_render = YELLOW
            else:
                color_render = WHITE
            text = font.render(
                f"{time_string}       {score}", True, color_render)
            self.surface.blit(text, (400, text_y))

    def get_time(self):
        return pygame.time.get_ticks() - self.start_time

    def format_time(self, time):
        time_minutes = str(int(time/60000)).zfill(1)
        time_seconds = str(int((time % 60000)/1000)).zfill(2)
        time_string = "%s:%s" % (time_minutes, time_seconds)
        return time_string

    def add_score(self, time):
        self.scores.append((self.snake.length, time))
        self.scores = sorted(self.scores, key=lambda x: (-x[0], x[1]))
        if len(self.scores) > 10:
            self.scores.pop()

    def new_game(self):
        self.start_time = pygame.time.get_ticks()
        self.speed = 5
        self.snake.clear()

    def load_scores(self):
        with open("resources/data.txt", "r") as file:
            for line in file:
                pair = line.split()
                points = int(pair[0])
                time = int(pair[1])
                self.scores.append((points, time))
        pass

    def save_scores(self):
        with open("resources/data.txt", "w") as file:
            for score, time in self.scores:
                line = str(score) + " " + str(time) + "\n"
                file.write(line)

    def run(self):
        running = True
        pause = False
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if pause:
                        if event.key == K_KP_ENTER:
                            pause = False
                            self.new_game()
                    else:
                        if event.key == K_UP:
                            self.snake.move_up()
                        if event.key == K_DOWN:
                            self.snake.move_down()
                        if event.key == K_LEFT:
                            self.snake.move_left()
                        if event.key == K_RIGHT:
                            self.snake.move_right()
                elif event.type == QUIT:
                    running = False
            try:
                if not pause:
                    self.update()
            except NameError:
                self.show_game_over()
                pause = True

            self.clock.tick(self.speed)
            # time.sleep(0.2)
        self.save_scores()


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
