import sys, zipfile, os
import pygame
import time
import numpy as np

from cStringIO import StringIO
from natural_sort import sort_nicely

FILEPATH = 'assets/Cubo.zip'
zip_file = zipfile.ZipFile(FILEPATH)
zip_images = zip_file.namelist()
sort_nicely(zip_images)

WHITE   = (255,255,255)
BLACK   = (  0,  0,  0)
RED     = (255,  0,  0)
GREEN   = (  0,255,  0)
BLUE    = (  0,  0,255)
CYAN    = (255,255,  0)
MAGENTA = (255,  0,255)
YELLOW  = (  0,255,255)

FPS = 1
FRAME = 1

GRID = 8

def get_frame(f):
    next_frame = f % len(zip_images)
    img_data = zip_file.read(zip_images[next_frame])
    img_stream = StringIO(img_data)
    return pygame.image.load(img_stream, zip_images[next_frame])

def find_tile(tile, target, pos):
    print tile.shape
    print target.shape

    SEARCH = 2

    for dx in xrange(SEARCH):
        for dy in xrange(SEARCH):
            toff = (pos[0]+dx, pos[1]+dy)
            print toff, compare(tile, target, toff)


def compare(tile, target, offset):
    tile_lum = tile[:,:,0] * 0.2126 + tile[:,:,1] * 0.7152 + tile[:,:,2] * 0.0722
    target_lum = target[:,:,0] * 0.2126 + target[:,:,1] * 0.7152 + target[:,:,2] * 0.0722
    fill_tile = np.empty(target_lum.shape)
    fill_tile[:] = np.nan

    ts = tile_lum.shape
    fill_tile[offset[0]:offset[0]+ts[0], offset[1]:offset[1]+ts[1]] = tile_lum

    diff = target_lum - fill_tile
    np.nan_to_num(diff, False)

    return np.sum(np.sum(abs(diff)))

if __name__ == '__main__':

    pygame.init()
    screen = pygame.display.set_mode([400,300])

    # while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    frame = get_frame(FRAME)
    next_frame = get_frame(FRAME+1)
    FRAME += 1

    target = pygame.surfarray.pixels3d(next_frame)

    tile = pygame.surfarray.pixels3d(frame)
    tile = tile[0:0+GRID, 0:0+GRID, :]

    find_tile(tile, target, [0, 0])

    del tile
    del target

    _,_,w,h = frame.get_rect()
    for x in xrange(0, w, GRID):
        for y in xrange(0, h, GRID):
            pass
            # pygame.draw.rect(frame, CYAN, (x, y, GRID, GRID), 1)


    # RENDER
    screen.blit(frame, (0,0))
    pygame.display.flip()
    del frame
    del next_frame

    # 24FPS
    # time.sleep(1./FPS)

    raw_input()