import pygame, sys, random, time

pygame.init()

#Screen Setup
screenDim = width, height = 1000, 1000
screen = pygame.display.set_mode(screenDim)
pygame.display.set_caption('Tetris')
gridSizeX = width // 25
gridSizeY = height // 25
clock = pygame.time.Clock()

#Grid
grid = [[' ' for i in range(10)] for j in range(20)]

#Stats
score = 0
startLevel = 1
level = startLevel
lines = 0

#Text Setup
font = pygame.font.SysFont('couriernew', 48)
fontB = pygame.font.SysFont('couriernewbold', 72)
titleDisplay = fontB.render('Tetris', False, (0, 0, 0))
nextDisplay = font.render('Next', False, (0, 0, 0))
holdDisplay = font.render('Hold', False, (0, 0, 0))
scoreDisplay = font.render('Score', False, (0, 0, 0))
levelDisplay = font.render('Level', False, (0, 0, 0))
linesDisplay = font.render('Lines', False, (0, 0, 0))
pauseDisplay = fontB.render('PAUSED', True, (255, 0, 0))
scoreValueDisplay = font.render(str(score), False, (0, 0, 0))
levelValueDisplay = font.render(str(level), False, (0, 0, 0))
linesValueDisplay = font.render(str(lines), False, (0, 0, 0))
titleDisplayRect = titleDisplay.get_rect(center = (width / 2, height / 20))
nextDisplayRect = nextDisplay.get_rect(center = (width * 0.72, height * 0.16))
holdDisplayRect = holdDisplay.get_rect(center = (width * 0.72, height * 0.36))
scoreDisplayRect = scoreDisplay.get_rect(center = (width * 0.72, height * 0.6))
levelDisplayRect = levelDisplay.get_rect(center = (width * 0.72, height * 0.72))
linesDisplayRect = linesDisplay.get_rect(center = (width * 0.72, height * 0.84))
pauseDisplayRect = pauseDisplay.get_rect(center = (10 * gridSizeX, 13 * gridSizeY))
scoreValueDisplayRect = scoreValueDisplay.get_rect(center = (width * 0.72, height * 0.66))
levelValueDisplayRect = levelValueDisplay.get_rect(center = (width * 0.72, height * 0.78))
linesValueDisplayRect = linesValueDisplay.get_rect(center = (width * 0.72, height * 0.90))

#Block Class
class Block:
    colors = {
        'I': (0, 255, 255),
        'O': (255, 255, 0),
        'T': (175, 0, 255),
        'S': (0, 255, 0),
        'Z': (255, 0, 0),
        'J': (0, 0, 255),
        'L': (255, 150, 0)
    }
    
    def __init__(self, blockType, x, y, scaleX = 1, scaleY = 1, ghost = False):
        self.type = blockType
        self.color = Block.colors[blockType] if not ghost else tuple(int(n * 0.4) for n in Block.colors[blockType])
        self.x, self.y = x, y
        self.rect = pygame.Rect(gridSizeX * (5 + y), gridSizeY * (3 + x), scaleX * gridSizeX, scaleY * gridSizeY)

    def updatePosition(self):
        self.rect.x = gridSizeX * (5 + self.y)
        self.rect.y = gridSizeY * (3 + self.x)

#Tetromino class
class Tetromino:
    shapes = {
        'I': [(0, -1), (0, 0), (0, 1), (0, 2)],
        'O': [(0, 1), (0, 0), (-1, 0), (-1, 1)],
        'T': [(0, -1), (0, 0), (0, 1), (-1, 0)],
        'S': [(0, -1), (0, 0), (-1, 1), (-1, 0)],
        'Z': [(0, 1), (0, 0), (-1, 0), (-1, -1)],
        'J': [(0, -1), (0, 0), (0, 1), (-1, -1)],
        'L': [(0, -1), (0, 0), (0, 1), (-1, 1)]
    }

    def __init__(self, shape, ghost = False):
        self.shape = shape
        self.ghost = ghost
        self.blocks = [Block(shape, 1 + dx, 4 + dy, 1, 1, ghost) for dx, dy in Tetromino.shapes[shape]]

    def move(self, dx, dy):
        if self.canMove(dx, dy):
            for block in self.blocks:
                block.x += dx
                block.y += dy
                block.updatePosition()
            return True
        return False
    
    def canMove(self, dx, dy):
        for block in self.blocks:
            newX = block.x + dx
            newY = block.y + dy
            if not (0 <= newX < 20 and 0 <= newY < 10) or grid[newX][newY] != ' ':
                return False
        return True
    
    def rotate(self, clockwise):
        global lastMoveWasTSpin
        if self.shape == 'O': return True
        center = self.blocks[1]
        kicks = [(0, 0), (0, -1), (0, 1), (-1, 0)]
        for dx, dy in kicks:
            newPositions = []
            valid = True
            for block in self.blocks:
                if clockwise:
                    newX = center.x + block.y - center.y + dx
                    newY = center.y - block.x + center.x + dy
                else:
                    newX = center.x - block.y + center.y + dx
                    newY = center.y + block.x - center.x + dy
                if not (0 <= newX < 20 and 0 <= newY < 10) or grid[newX][newY] != ' ':
                    valid = False
                    break
                newPositions.append((newX, newY))
            if valid:
                for i, block in enumerate(self.blocks):
                    block.x, block.y = newPositions[i]
                    block.updatePosition()
                lastMoveWasTSpin = isTSpin(self)
                return True
        return False
    
    def drop(self):
        global score
        while self.move(1, 0):
            if not self.ghost:
                score += 2
    
    def lock(self):
        for block in self.blocks:
            grid[block.x][block.y] = block
    
    def draw(self):
        for block in self.blocks:
            pygame.draw.rect(screen, block.color, block.rect)
            pygame.draw.rect(screen, (0, 0, 0), block.rect, 1)
            pygame.draw.rect(screen, (0, 0, 0), block.rect.inflate(2, 2), 1)

#Functions
def clearLines():
    global score, lines, level, lastMoveWasTSpin, lastClearWasTetrisOrTSpin
    fullRows = [i for i, row in enumerate(grid) if all(cell != ' ' for cell in row)]
    cleared = len(fullRows)
    if lastMoveWasTSpin:
        scoreGain = [400, 800, 1200, 1600][cleared]
    else:
        scoreGain = [0, 100, 300, 500, 800][cleared]
    if cleared > 0 and (cleared == 4 or lastMoveWasTSpin):
        if lastClearWasTetrisOrTSpin:
            scoreGain = int(scoreGain * 1.5)
        lastClearWasTetrisOrTSpin = True
    else:
        lastClearWasTetrisOrTSpin = False
    for i in fullRows:
        del grid[i]
        grid.insert(0, [' ' for i in range(10)])
    lines += cleared
    level = lines // 10 + startLevel
    score += level * scoreGain
    pygame.time.set_timer(tick, fallSpeed(level))
    for i, row in enumerate(grid):
        for j, block in enumerate(row):
            if block != ' ':
                block.x, block.y = i, j
                block.updatePosition()

def isGameOver(tetromino):
    return any(grid[block.x][block.y] != ' ' for block in tetromino.blocks)

def fallSpeed(level):
    speeds = [800, 717, 633, 550, 467, 383, 300, 217, 133, 100,
              83, 83, 83, 67, 67, 67, 50, 50, 50, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33]
    return speeds[level] if level < len(speeds) else 17

def generateBag():
    bag = pieces[:]
    random.shuffle(bag)
    return bag

def resetLockCounter():
    global lockCounter, lockResets
    if not active.canMove(1, 0) and lockResets < 15:
            lockCounter = 0
            lockResets += 1

def isTSpin(tetromino):
    if tetromino.shape != 'T': return False
    center = tetromino.blocks[1]
    corners = [(center.x - 1, center.y - 1), (center.x - 1, center.y + 1),
               (center.x + 1, center.y - 1), (center.x + 1, center.y + 1)]
    count = 0
    for x, y in corners:
        if not (0 <= x < 20 and 0 <= y < 10) or grid[x][y] != ' ':
            count += 1
    return count >= 3

#Initial Setup
pieces = list(Tetromino.shapes.keys())
bag = generateBag()
active = Tetromino(bag.pop())
next = Tetromino(bag.pop())
hold = None
canHold = True

tick = pygame.USEREVENT + 1
pygame.time.set_timer(tick, fallSpeed(level))

cooldownDown = 0
cooldownSide = 0
paused = False

lockCounter = 0
lockResets = 0

lastClearWasTetrisOrTSpin = False
lastMoveWasTSpin = False

while True:
    clock.tick(60)

    #Board Setup
    screen.fill((255, 255, 255))
    scoreValueDisplay = font.render(str(score), False, (0, 0, 0))
    levelValueDisplay = font.render(str(level), False, (0, 0, 0))
    linesValueDisplay = font.render(str(lines), False, (0, 0, 0))
    scoreValueDisplayRect = scoreValueDisplay.get_rect(center = (width * 0.72, height * 0.66))
    levelValueDisplayRect = levelValueDisplay.get_rect(center = (width * 0.72, height * 0.78))
    linesValueDisplayRect = linesValueDisplay.get_rect(center = (width * 0.72, height * 0.90))
    screen.blit(titleDisplay, titleDisplayRect)
    screen.blit(nextDisplay, nextDisplayRect)
    screen.blit(holdDisplay, holdDisplayRect)
    screen.blit(scoreDisplay, scoreDisplayRect)
    screen.blit(levelDisplay, levelDisplayRect)
    screen.blit(linesDisplay, linesDisplayRect)
    screen.blit(scoreValueDisplay, scoreValueDisplayRect)
    screen.blit(levelValueDisplay, levelValueDisplayRect)
    screen.blit(linesValueDisplay, linesValueDisplayRect)

    for x in range(5 * gridSizeX, 15 * gridSizeX, gridSizeX):
        for y in range(3 * gridSizeY, 23 * gridSizeY, gridSizeY):
            gridLines = pygame.Rect(x, y, gridSizeX, gridSizeY)
            pygame.draw.rect(screen, (200, 200, 200), gridLines, 1)

    gridBorder = pygame.Rect(5 * gridSizeX - 1, 3 * gridSizeY - 1, gridSizeX * 10 + 2, gridSizeY * 20 + 2)
    pygame.draw.rect(screen, (0, 0, 0), gridBorder, 5)
    gridBorderFix = pygame.Rect(5 * gridSizeX - 3, 3 * gridSizeY - 3, gridSizeX * 10 + 6, gridSizeY * 20 + 6)
    pygame.draw.rect(screen, (0, 0, 0), gridBorderFix, 3)
    nextBorder = pygame.Rect(16 * gridSizeX - 1, 3 * gridSizeY - 1, gridSizeX * 4 + 2, gridSizeY * 4 + 2)
    pygame.draw.rect(screen, (0, 0, 0), nextBorder, 5)
    nextBorderFix = pygame.Rect(16 * gridSizeX - 3, 3 * gridSizeY - 3, gridSizeX * 4 + 6, gridSizeY * 4 + 6)
    pygame.draw.rect(screen, (0, 0, 0), nextBorderFix, 3)
    holdBorder = pygame.Rect(16 * gridSizeX - 1, 8 * gridSizeY - 1, gridSizeX * 4 + 2, gridSizeY * 4 + 2)
    pygame.draw.rect(screen, (0, 0, 0), holdBorder, 5)
    holdBorderFix = pygame.Rect(16 * gridSizeX - 3, 8 * gridSizeY - 3, gridSizeX * 4 + 6, gridSizeY * 4 + 6)
    pygame.draw.rect(screen, (0, 0, 0), holdBorderFix, 3)
    holdBorder = pygame.Rect(16 * gridSizeX - 1, 14 * gridSizeY - 1, gridSizeX * 4 + 2, gridSizeY * 9 + 2)
    pygame.draw.rect(screen, (0, 0, 0), holdBorder, 5)
    holdBorderFix = pygame.Rect(16 * gridSizeX - 3, 14 * gridSizeY - 3, gridSizeX * 4 + 6, gridSizeY * 9 + 6)
    pygame.draw.rect(screen, (0, 0, 0), holdBorderFix, 3)

    #Inputs
    if cooldownDown > 0:
        cooldownDown -= 1
    if cooldownSide > 0:
        cooldownSide -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            sys.exit()
        if not paused and event.type == tick:
            if not active.move(1, 0):
                if lockCounter >= 30 or lockResets >= 15:
                    active.lock()
                    clearLines()
                    active = next
                    if not bag: bag = generateBag()
                    next = Tetromino(bag.pop(0))
                    canHold = True
                    lockCounter = 0
                    lockResets = 0
                    if isGameOver(active):
                        print(f"Game Over! Score: {score}")
                        pygame.quit()
                        sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused
            elif not paused:
                if event.key == pygame.K_LEFT:
                    cooldownSide = 10
                    if active.move(0, -1):
                        resetLockCounter()
                elif event.key == pygame.K_RIGHT:
                    cooldownSide = 10
                    if active.move(0, 1):
                        resetLockCounter()
                elif event.key == pygame.K_UP:
                    if active.rotate(True):
                        resetLockCounter()
                elif event.key == pygame.K_x:
                    if active.rotate(False):
                        resetLockCounter()
                elif event.key == pygame.K_SPACE:
                    active.drop()
                    active.lock()
                    clearLines()
                    active = next
                    if not bag: bag = generateBag()
                    next = Tetromino(bag.pop(0))
                    canHold = True
                    lockCounter = 0
                    lockResets = 0
                    if isGameOver(active):
                        print(f"Game Over! Score: {score}")
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_c and canHold:
                    if hold == None:
                        hold = Tetromino(active.shape)
                        active = next
                        if not bag: bag = generateBag()
                        next = Tetromino(bag.pop(0))
                    else:
                        hold, active = Tetromino(active.shape), hold
                    canHold = False
                    lockCounter = 0
                    lockResets = 0

    keys = pygame.key.get_pressed()
    if not paused:
        if cooldownDown == 0:
            if keys[pygame.K_DOWN]:
                cooldownDown = 5
                active.move(1, 0)
                score += 1
        if cooldownSide == 0:
            cooldownSide = 3
            if keys[pygame.K_LEFT]:
                if active.move(0, -1):
                    resetLockCounter()
            if keys[pygame.K_RIGHT]:
                if active.move(0, 1):
                    resetLockCounter()

    if not active.canMove(1, 0):
        lockCounter += 1

    #draw blocks
    for row in grid:
        for block in row:
            if block != ' ':
                pygame.draw.rect(screen, block.color, block.rect)
                pygame.draw.rect(screen, (0, 0, 0), block.rect, 1)
                pygame.draw.rect(screen, (0, 0, 0), block.rect.inflate(2, 2), 1)
    
    nextScale = (0.75, 0.75) if next.shape == 'I' else (1, 1)
    holdScale = (0.75, 0.75) if hold and hold.shape == 'I' else (1, 1)
    nextDisplayBlocks = [Block(next.shape, (2 if next.shape == 'I' else 2.5) + dx * nextScale[0],
                               (12 if next.shape == 'O' else 12.25 if next.shape == 'I' else 12.5) + dy * nextScale[1],
                               *nextScale) for dx, dy in Tetromino.shapes[next.shape]]
    holdDisplayBlocks = [Block(hold.shape, (7 if hold.shape == 'I' else 7.5) + dx * holdScale[0],
                                (12 if hold.shape == 'O' else 12.25 if hold.shape == 'I' else 12.5) + dy * holdScale[1], *holdScale)
                                for dx, dy in Tetromino.shapes[hold.shape]] if hold else []
    ghost = Tetromino(active.shape, True)
    ghost.blocks = [Block(block.type, block.x, block.y, 1, 1, True) for block in active.blocks]
    for block in ghost.blocks:
        block.updatePosition()
    ghost.drop()
    for block in ghost.blocks + nextDisplayBlocks + (holdDisplayBlocks if holdDisplayBlocks else []):
        pygame.draw.rect(screen, block.color, block.rect)
        pygame.draw.rect(screen, (0, 0, 0), block.rect, 1)
        pygame.draw.rect(screen, (0, 0, 0), block.rect.inflate(2, 2), 1)
    active.draw()

    if paused:
        screen.blit(pauseDisplay, pauseDisplayRect)

    pygame.display.flip()
