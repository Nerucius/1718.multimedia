import sys, zipfile, os
import pygame
import time
import numpy as np

white = (255,255,255)
black = (  0,  0,  0)

frame = 0
last_frame_time = -999

def playback(config, frame_gen):
    # Setup frametime
    FPS = int(config['FPS'])
    if FPS <= 0:
        frame_time_target = -1
    else:
        frame_time_target = 1.0 / FPS

    # Try to load frame size
    if 'FRAME_W' in config and 'FRAME_H' in config:
        FRAME_SIZE = int(config['FRAME_W']), int(config['FRAME_H'])
    else:
        raise Exception("No frame size information found")

    # Scale up screen
    if 'SCALE' in config:
        FRAME_SIZE = FRAME_SIZE[0] * config['SCALE'], FRAME_SIZE[1] * config['SCALE']

    # PyGame Config
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("TMM Media Player 0.2f1")
    font = pygame.font.SysFont('Consolas', 14)
    screen = pygame.display.set_mode(FRAME_SIZE)


    for img_frame in frame_gen:
        frame_start = time.clock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        frame_scale = pygame.transform.scale(img_frame, FRAME_SIZE)
        screen.blit(frame_scale, (0,0))

        del frame_scale
        del img_frame

        # Calculat elapsed time and real FPS
        frame_end = time.clock()
        frame_time = frame_end - frame_start

        # wait for X seconds, as many as necesary to stay on target frame time
        wait_time = frame_time_target - frame_time
        time.sleep(max(0, wait_time))

        # Calcualte real FPS after wait, and print to screen
        frame_end_wait = time.clock()

        frame_time_wait = frame_end_wait - frame_start
        real_fps = 1.0 / frame_time_wait

        frame_alloc = (1- (frame_time_target - frame_time) / frame_time_target) * 100.0
        text_color = (128,255,128)
        if frame_alloc > 100:
            text_color = (255,128,128)

        font_surf = font.render('%.2f FPS (ft:%.3fms) (fa:%.2f%%)' % (real_fps, frame_time, frame_alloc),
            True, text_color)
        screen.blit(font_surf, [0,0])

        # Show new frame
        pygame.display.flip()
