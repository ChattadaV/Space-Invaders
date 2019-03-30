## SPACE INVADERS ##
import pygame
import sys
from random import shuffle
from pygame.locals import *
## Constants ##
# colors
WHITE     = (255, 255, 255)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
BLUE      = (  0,   0, 255)
PURPLE    = (255,   0, 255)
NEARBLACK = ( 19,  15,  48)
# player
PLAYERWIDTH = 40
PLAYERHEIGHT = 10
PLAYER1 = 'Player 1'
PLAYERSPEED = 5
PLAYERCOLOR = BLUE
# display
GAMETITLE = "Space Invaders"
DISPLAYWIDTH = 640
DISPLAYHEIGHT = 480
BACKGROUNDCOLOR = NEARBLACK
XMARGIN = 50
YMARGIN = 50
# bullet
BULLETSIZE = 5
BULLETOFFSET = 700
# enemy
ENEMYSIZE = 25
ENEMYNAME = 'Enemy'
ENEMYGAP = 20
ARRAYWIDTH = 10
ARRAYHEIGHT = 4
MOVETIME = 1000
MOVEX = 10
MOVEY = ENEMYSIZE
TIMEOFFSET = 300
# movement
KEYSPRESSED = {pygame.K_LEFT  : (-1),
               pygame.K_RIGHT : ( 1)}
# player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.width  = PLAYERWIDTH
        self.height = PLAYERHEIGHT
        self.image  = pygame.Surface((self.width, self.height))
        self.color  = PLAYERCOLOR
        self.image.fill(self.color)
        self.rect   = self.image.get_rect()
        self.name   = PLAYER1
        self.speed  = PLAYERSPEED
        self.vectorx= 0
    def update(self, keys, *args):
        for key in KEYSPRESSED:
            if keys[key]:
                self.rect.x += KEYSPRESSED[key] * self.speed
        self.checkForSide()
        self.image.fill(self.color)
    def checkForSide(self):
        if self.rect.right > DISPLAYWIDTH:
            self.rect.left = 0
            self.vectorx = 0
        elif self.rect.left < 0:
            self.rect.right = DISPLAYWIDTH
            self.vectorx = 0
class Bullet(pygame.sprite.Sprite):
    def __init__(self, rect, color, vectory, speed):
        pygame.sprite.Sprite.__init__(self)
        self.width = BULLETSIZE
        self.height = BULLETSIZE
        self.color = color
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.centerx = rect.centerx
        self.rect.top = rect.bottom
        self.name = 'bullet'
        self.vectory = vectory
        self.speed = speed
    def update(self, *args):
        self.oldLocation = (self.rect.x, self.rect.y)
        self.rect.y += self.vectory * self.speed
        if self.rect.bottom < 0:
            self.kill()
        elif self.rect.bottom > DISPLAYHEIGHT:
            self.kill()
class Enemy(pygame.sprite.Sprite):
    def __init__(self, row, column):
        pygame.sprite.Sprite.__init__(self)
        self.width = ENEMYSIZE
        self.height = ENEMYSIZE
        self.row = row
        self.column = column
        self.image = self.setImage()
        self.rect = self.image.get_rect()
        self.name = 'enemy'
        self.vectorx = 1
        self.moveNumber = 0
        self.moveTime = MOVETIME
        self.timeOffSet = row * TIMEOFFSET
        self.timer = pygame.time.get_ticks() - self.timeOffSet
    def update(self, keys, currentTime):
        if currentTime - self.timer > self.moveTime:
            if self.moveNumber < 6:
                self.rect.x += MOVEX * self.vectorx
                self.moveNumber += 1
            elif self.moveNumber >= 6:
                self. vectorx *= -1
                self.moveNumber = 0
                self.rect.y += MOVEY
                if self.moveTime >100:
                    self.moveTime -= 50
            self.timer = currentTime
    def setImage(self):
        if self.row == 0:
            image = pygame.image.load('alien1.png')
        elif self.row == 1:
            image = pygame.image.load('alien2.png')
        elif self.row == 2:
            image = pygame.image.load('alien3.png')
        else:
            image = pygame.image.load('alien1.png')
        image.convert_alpha()
        image = pygame.transform.scale(image, (self.width, self.height))
        return image
class Text(object):
    def __init__(self, font, size, message, color, rect, surface):
        self.font = pygame.font.Font(font, size)
        self.message = message
        self.surface = self.font.render(self.message, True, color)
        self.rect = self.surface.get_rect(center=(DISPLAYWIDTH/2, DISPLAYHEIGHT/2))
        self.setRect(rect)
    def setRect(self, rect):
        self.rect.centerx, self.rect.centery = self.rect.centerx, self.rect.centery - 5
    def draw(self, surface):
        surface.blit(self.surface, self.rect)
class App(object):
    def __init__(self):
        pygame.init()
        self.displaySurf, self.displayRect = self.makeScreen()
        self.gameStart = True
        self.gameOver = False
        self.gameWin = False
        self.beginGame = False
        self.laserSound = pygame.mixer.Sound('laser.ogg')
        self.startLaser = pygame.mixer.Sound('alienLaser.ogg')
        self.oof = pygame.mixer.Sound('oof.ogg')
        self.playIntroSound = True
    def resetGame(self):
        self.gameStart = True
        self.gameOver = False
        self.gameWin = False
        self.needToMakeEnemies = True
        self.introMessage1 = Text('KS.ttf', 60, 
                                  'Space Invaders!',
                                  PURPLE, self.displayRect, self.displaySurf)
        self.introMessage2 = Text('OpenSans.ttf', 16,
                                  '--- Press Any Key to Continue ---',
                                  GREEN, self.displayRect, self.displaySurf)
        self.introMessage2.rect.top = self.introMessage1.rect.bottom + 25
        self.gameOverMessage = Text('OpenSans.ttf', 40,
                                    'OOF',
                                    GREEN, self.displayRect, self.displaySurf)
        self.gameWinMessage = Text('OpenSans.ttf', 40,
                                    'YOU ARE THE CHAMPION',
                                    WHITE, self.displayRect, self.displaySurf)
        self.player = self.makePlayer()
        self.bullets = pygame.sprite.Group()
        self.greenBullets = pygame.sprite.Group()
        self.allSprites = pygame.sprite.Group(self.player)
        self.keys = pygame.key.get_pressed()
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.enemyMoves = 0
        self.enemyBulletTimer = pygame.time.get_ticks()
        self.gameOverTime = pygame.time.get_ticks()
        if self.playIntroSound:
            self.startLaser.play()
            self.playIntroSound = False
    def checkForEnemyBullets(self):
        redBulletsGroup = pygame.sprite.Group()
        for bullet in self.bullets:
            if bullet.color == RED:
                redBulletsGroup.add(bullet)
        for bullet in redBulletsGroup:
            if pygame.sprite.collide_rect(bullet, self.player):
                if self.player.color == BLUE:
                    self.player.color = PURPLE
                elif self.player.color == PURPLE:
                    self.player.color = RED
                elif self.player.color == RED:
                    self.gameOver = True
                    self.gameOverTime = pygame.time.get_ticks()
                bullet.kill()
    def shootEnemyBullet(self, rect):
        if (pygame.time.get_ticks() - self.enemyBulletTimer) > BULLETOFFSET:
            self.bullets.add(Bullet(rect, RED, 1, 5))
            self.allSprites.add(self.bullets)
            self.enemyBulletTimer = pygame.time.get_ticks()
    def findEnemyShooter(self):
        columnList = []
        for enemy in self.enemies:
            columnList.append(enemy.column)
        #get rid of duplicate columns
        columnSet = set(columnList)
        columnList = list(columnSet)
        shuffle(columnList)
        column = columnList[0]
        enemyList = []
        rowList = []
        for enemy in self.enemies:
            if enemy.column == column:
                rowList.append(enemy.row)
        row = max(rowList)
        for enemy in self.enemies:
            if enemy.column == column and enemy.row == row:
                self.shooter = enemy
    def makeScreen(self):
        pygame.display.set_caption(GAMETITLE)
        displaySurf = pygame.display.set_mode((DISPLAYWIDTH, DISPLAYHEIGHT))
        displayRect = displaySurf.get_rect()
        displaySurf.fill(BACKGROUNDCOLOR)
        displaySurf.convert()
        return displaySurf, displayRect
    def makePlayer(self):
        player = Player()
        ##Place the player centerx and five pixels from the bottom
        player.rect.centerx = self.displayRect.centerx
        player.rect.bottom = self.displayRect.bottom - 5
        return player
    def makeEnemies(self):
        enemies = pygame.sprite.Group()
        for row in range(ARRAYHEIGHT):
            for column in range(ARRAYWIDTH):
                enemy = Enemy(row, column)
                enemy.rect.x = XMARGIN + (column * (ENEMYSIZE + ENEMYGAP))
                enemy.rect.y = YMARGIN + (row * (ENEMYSIZE + ENEMYGAP))
                enemies.add(enemy)
        return enemies
    def checkInput(self):
        for event in pygame.event.get():
            self.keys = pygame.key.get_pressed()
            if event.type == QUIT:
                self.terminate()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE and len(self.greenBullets) < 1:
                    bullet = Bullet(self.player.rect, GREEN, -1, 20)
                    self.greenBullets.add(bullet)
                    self.bullets.add(self.greenBullets)
                    self.allSprites.add(self.bullets)
                    self.laserSound.play()
                elif event.key == K_ESCAPE:
                    self.terminate()
    def gameStartInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate()
            elif event.type == KEYUP:
                self.gameOver = False
                self.gameWin = False
                self.gameStart = False
                self.beginGame = True
    def gameOverInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate()
            elif event.type == KEYUP:
                self.gameStart = True
                self.beginGame = False
                self.gameOver = False
                self.gameWin = False
    def checkCollisions(self):
        self.checkForEnemyBullets()
        pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
    def checkGameWin(self):
        if len(self.enemies) == 0:
            self.gameWin = True
            self.gameOver = False
            self.gameStart = False
            self.beginGame = False
            self.gameOverTime = pygame.time.get_ticks()
        else:
            for enemy in self.enemies:
                if enemy.rect.bottom > DISPLAYHEIGHT:
                    self.gameOver = True
                    self.gameStart = False
                    self.beginGame = False
                    self.gameOverTime = pygame.time.get_ticks()
    def terminate(self):
        pygame.quit()
        sys.exit()
    def mainLoop(self):
        while True:
            if self.gameStart:
                self.resetGame()
                self.gameOver = False
                self.displaySurf.fill(BACKGROUNDCOLOR)
                self.introMessage1.draw(self.displaySurf)
                self.introMessage2.draw(self.displaySurf)
                self.gameStartInput()
                pygame.display.update()
            elif self.gameOver:
                self.playIntroSound = True
                self.displaySurf.fill(BACKGROUNDCOLOR)
                self.gameOverMessage.draw(self.displaySurf)
                #prevent users from exiting the GAME OVER screen too quickly
                if (pygame.time.get_ticks() - self.gameOverTime) > 2000:
                    self.gameOverInput()
                    self.oof.play()
                pygame.display.update()
            elif self.gameWin:
                self.playIntroSound = True
                self.displaySurf.fill(BACKGROUNDCOLOR)
                self.gameWinMessage.draw(self.displaySurf)
                if (pygame.time.get_ticks() - self.gameOverTime) > 3000:
                    self.gameOverInput()
                pygame.display.update()
            elif self.beginGame:
                if self.needToMakeEnemies:
                    self.enemies = self.makeEnemies()
                    self.allSprites.add(self.enemies)
                    self.needToMakeEnemies = False
                    pygame.event.clear()
                else:
                    currentTime = pygame.time.get_ticks()
                    self.displaySurf.fill(BACKGROUNDCOLOR)
                    self.checkInput()
                    self.allSprites.update(self.keys, currentTime)
                    if len(self.enemies) > 0:
                        self.findEnemyShooter()
                        self.shootEnemyBullet(self.shooter.rect)
                    self.checkCollisions()
                    self.allSprites.draw(self.displaySurf)
                    pygame.display.update()
                    self.checkGameWin()
                    self.clock.tick(self.fps) 
if __name__ == '__main__':
    app = App()
    app.mainLoop()