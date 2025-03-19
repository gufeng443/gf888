import pygame
import random
import sys

# 初始化
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("植物大战僵尸")
clock = pygame.time.Clock()

# 资源路径
IMAGE_PATH = 'imgs/'
PLANTS = {'Sunflower': 'sunflower.png', 'Peashooter': 'peashooter.png'}
ZOMBIES = {'Basic': 'zombie.png'}

# 游戏主类
class MainGame:
    def __init__(self):
        self.plants = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.sun = 50  # 初始阳光值
        self.score = 0

    def create_plant(self, plant_type, x, y):
        if plant_type == 'Sunflower':
            plant = Sunflower(x, y)
        elif plant_type == 'Peashooter':
            plant = Peashooter(x, y)
        self.plants.add(plant)

    def create_zombie(self):
        zombie = Zombie(screen_width, random.randint(50, 550))
        self.zombies.add(zombie)

# 植物基类（网页3、网页5）
class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, cost):
        super().__init__()
        self.image = pygame.image.load(IMAGE_PATH + PLANTS[self.__class__.__name__])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hp = hp
        self.cost = cost

class Sunflower(Plant):
    def __init__(self, x, y):
        super().__init__(x, y, hp=100, cost=50)
        self.sun_timer = 0

    def update(self):
        self.sun_timer += 1
        if self.sun_timer % 100 == 0:  # 每100帧产生阳光
            MainGame.sun += 25

class Peashooter(Plant):
    def __init__(self, x, y):
        super().__init__(x, y, hp=200, cost=100)
        self.shoot_timer = 0

    def shoot(self):
        if self.shoot_timer % 30 == 0:  # 每30帧发射豌豆
            bullet = PeaBullet(self.rect.x + 60, self.rect.y + 15)
            MainGame.bullets.add(bullet)

# 僵尸类（网页3、网页6）
class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(IMAGE_PATH + ZOMBIES['Basic'])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hp = 200
        self.speed = 0.5

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -100:  # 僵尸到达左侧边界游戏结束
            pygame.quit()
            sys.exit()

# 子弹类（网页3）
class PeaBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(IMAGE_PATH + 'peabullet.png')
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > screen_width:
            self.kill()

# 游戏主循环
def main():
    game = MainGame()
    zombie_spawn_timer = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # 添加植物（网页5的实现思路）
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if event.button == 1:  # 左键种向日葵
                    if game.sun >= 50:
                        game.create_plant('Sunflower', x, y)
                        game.sun -= 50
                elif event.button == 3:  # 右键种豌豆射手
                    if game.sun >= 100:
                        game.create_plant('Peashooter', x, y)
                        game.sun -= 100

        # 生成僵尸（网页6的随机生成逻辑）
        zombie_spawn_timer += 1
        if zombie_spawn_timer % 300 == 0:
            game.create_zombie()

        # 更新游戏对象
        game.plants.update()
        game.zombies.update()
        game.bullets.update()

        # 绘制界面
        screen.fill((135, 206, 235))  # 天空蓝背景
        game.plants.draw(screen)
        game.zombies.draw(screen)
        game.bullets.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()