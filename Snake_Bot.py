import pygame, sys, time, random

difficulty = 8
frame_size_x = 400
frame_size_y = 400

check_errors = pygame.init()
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')

# Initialise game window
pygame.display.set_caption('Snake AI')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))

# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

# If the food is in snake, assign it a set position
food_pos = [random.randrange(1, (frame_size_x//50)) * 50, random.randrange(1, (frame_size_y//50)) * 50]
for x in [[200, 50], [200-50, 50], [200-(2*50), 50], [200-(3*50), 50]]:
    if food_pos == x:
        food_pos = [100,300]
food_spawn = True

direction = 'R'
score = 0

# Stole it from itertools (yeah, I know)
def product(*args, repeat=1):
    pools = [tuple(pool) for pool in args] * repeat
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)

class Snake:
    snake_pos = [200, 50]
    snake_body = [[200, 50], [200-50, 50], [200-(2*50), 50], [200-(3*50), 50]]
    
    def optimized_possible(start_pos,direction,body,end_pos):
        out = ['U','D','R','L']
        
        body = body[1], body[2], body[3]
        
        # Check if apple is straight up/down and if body is between the apple and snake
        up, down, right, left = False, False, False, False
        
        if start_pos[0] == end_pos[0]:
            # up
            if start_pos[1] > end_pos[1]:
                up = True
                for x in body:
                    if start_pos[0] == x[0] and start_pos[1] > x[1]:
                        up = False
                        
            # down
            if start_pos[1] < end_pos[1]:
                down = True
                for x in body:
                    if start_pos[0] == x[0] and start_pos[1] < x[1]:
                        down = False
                        
        if start_pos[1] == end_pos[1]:
            # right
            if start_pos[0] < end_pos[0]:
                right = True
                for x in body:
                    if start_pos[1] == x[1] and start_pos[0] <= x[0]:
                        right = False
                        
            # left
            if start_pos[0] > end_pos[0]:
                left = True
                for x in body:
                    if start_pos[1] == x[1] and start_pos[0] >= x[0]:
                        left = False
                        
        if up:
            return "U"
        if down:
            return "D"
        if right:
            return "R"
        if left:
            return "L"
        
        # Secondary Check if up/down/right/left all return false
        # Check if we can eliminate a direction
        # If the body is between the snake and apple along the x-axis we can't
        optim = True
        for x in body:
            # Check if apple has same x as body   Check if apple is below the body
            if end_pos[0] == x[0] and end_pos[1] > x[1]:
                for y in body:
                    if start_pos[0] == y[0] and start_pos[1] < y[1]:
                        optim = False
                        
        # Check inverse of above
        for x in body:
            if end_pos[0] == x[0] and end_pos[1] < x[1]:
                for y in body:
                    if start_pos[0] == y[0] and start_pos[1] > y[1]:
                        optim = False
        
        if optim:
            if start_pos[0] > end_pos[0]:
                out.remove("R")
            if start_pos[0] < end_pos[0]:
                out.remove("L")
        
        return ''.join(out)
    
    def get_dist(start_pos,end_pos):
        start_pos = [start_pos[0]/50,start_pos[1]/50]
        end_pos = [end_pos[0]/50,end_pos[1]/50]
        
        dist = abs(start_pos[0]-end_pos[0])
        dist += abs(start_pos[1]-end_pos[1])
        if dist == 0:
            dist = 1
        return int(dist)
    
    def test_path(test_pos2,test_body2,path,food_pos):
        
        numerical_path = []
        
        for x in path:
            if x == "U":
                test_pos2 = [test_pos2[0],test_pos2[1] - 50]
            if x == "D":
                test_pos2 = [test_pos2[0],test_pos2[1] + 50]
            if x == "R":
                test_pos2 = [test_pos2[0] + 50,test_pos2[1]]
            if x == "L":
                test_pos2 = [test_pos2[0] - 50,test_pos2[1]]
            
            numerical_path.append(test_pos2)
            
            if test_pos2[0] < 0 or test_pos2[0] > frame_size_x-50:
                return False
            if test_pos2[1] < 0 or test_pos2[1] > frame_size_y-50:
                return False
        
        for block in test_body2[1:]:
            if block in numerical_path:
                return False
        
        if test_pos2 == food_pos:
            return True
        else:
            return False
    
    def get_path(test_pos, test_body, food_pos):
        global direction
        
        possible = Snake.optimized_possible(test_pos,direction,test_body,food_pos)
        print("Using Set:",possible)
        
        begin = Snake.get_dist(test_pos,food_pos)
        print("Beginning Search at:",str(begin))
        
        for i in range(begin, 16):
            for path in product(possible, repeat=i):
                if Snake.test_path(test_pos,test_body,path,food_pos):
                    return list(path)

# Game Over
def game_over():
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (frame_size_x/2, frame_size_y/4)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(1, red, 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

# Score
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x/10, 15)
    else:
        score_rect.midtop = (frame_size_x/2, frame_size_y/1.25)
    game_window.blit(score_surface, score_rect)

# Main logic
def main_loop():
    global direction, food_pos, snake_pos, food_spawn, score, snake_body, config_path

    snake_pos = Snake.snake_pos
    snake_body = Snake.snake_body
    dir_array = []
        
    while True:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    
        # Moving the snake
        if direction == 'U':
            snake_pos[1] -= 50
        if direction == 'D':
            snake_pos[1] += 50
        if direction == 'L':
            snake_pos[0] -= 50
        if direction == 'R':
            snake_pos[0] += 50
            
        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            food_spawn = False
            snake_body.pop()
        else:
            snake_body.pop()

        # Spawning food on the screen
        if not food_spawn:
            food_in_snake = True
            while food_in_snake:
                food_pos = [random.randrange(1, (frame_size_x//50)) * 50, random.randrange(1, (frame_size_y//50)) * 50]
                if food_pos not in snake_body:
                    food_in_snake = False
        food_spawn = True
        
        # Pathfinding and stats
        if dir_array == []:
            print("Snake Position:",snake_pos,"        Food Position:",food_pos)
            print("Snake body:",snake_body)
            dir_array = Snake.get_path(snake_pos,snake_body,food_pos)
            print("Path Length:",len(dir_array))
            print(dir_array,"\n")
        direction = dir_array.pop(0)

        # Draw Snake
        game_window.fill(white)
        for pos in snake_body:
            pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 50, 50))

        # Snake food
        pygame.draw.rect(game_window, red, pygame.Rect(food_pos[0], food_pos[1], 50, 50))

        # Game Over conditions
        # Getting out of bounds
        if snake_pos[0] < 0 or snake_pos[0] > frame_size_x-50:
            game_over()

        if snake_pos[1] < 0 or snake_pos[1] > frame_size_y-50:
            game_over()

        # Touching the snake body
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over()

        show_score(0, black, 'consolas', 20)
                
        # Refresh game screen
        pygame.display.update()
        # Refresh rate
        fps_controller.tick(difficulty)
        
if __name__ == '__main__':
    main_loop()
