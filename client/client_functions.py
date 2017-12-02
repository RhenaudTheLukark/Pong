ball = 0
ball_coords = 0
rackets = [0,0]
rackets_coord = [0,0]

#Play an online game of Pong
def play(s):
    print("Game starts")
    init()
    load(ball,ball_coords,rackets,rackets_coord)

    while True:
    for e in pygame.event.get():
        # Check for exit
        if e.type == pygame.QUIT:
            sys.exit()

        # Check for racket movements
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP:
                #update upTrue
            if e.key == pygame.K_DOWN:
                #update downTrue
        elif e.type == pygame.KEYUP:
            if e.key == pygame.K_UP:
                #update upFalse
            if e.key == pygame.K_DOWN:
                #s=update downFalse
    return
