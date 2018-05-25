import sys, zipfile, os
import pygame
import time
import numpy as np
import argparse

from cStringIO import StringIO
from natural_sort import sort_nicely
from effects import *

FILEPATH = 'assets/Cubo.zip'
# FILEPATH = 'assets/3secuencias_BN.zip'
zip_file = zipfile.ZipFile(FILEPATH)
zip_images = zip_file.namelist()
sort_nicely(zip_images)

WHITE   = (255,255,255)
BLACK   = (  0,  0,  0)
RED     = (255,  0,  0)
GREEN   = (  0,255,  0)
BLUE    = (  0,  0,255)
CYAN    = (  0,255,255)
MAGENTA = (255,  0,255)
YELLOW  = (255,255,  0)

FPS = 1
FRAME = 1

GRID = 16
SCREEN_SIZE = [400,300]


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

def draw_screen(sleep=None):
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    pygame.display.flip()

    if sleep is None:
        raw_input()
    else:
        time.sleep(sleep/1000.)

if __name__ == '__main__':

    # Arguments
    parser = argparse.ArgumentParser(description="Encoder")
    parser.add_argument('-q', metavar="<int>", type=int, default=5,
        help="Quality, lower is better")
    parser.add_argument('-g', metavar="<int>", type=int, default=16,
        help="Grid size")
    args = parser.parse_args()
    # --------------------

    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)

    # Load I and P frames
    i_frame = get_frame(FRAME)
    p_frame = get_frame(FRAME+1)

    screen.blit(p_frame, (0,0))
    pygame.display.flip()

    pygame.display.flip()

    draw_screen(500)

    def find_min_diff_offset(i_frame, p_frame, tile_rect):
        ''' Compare a tile rectangle from a p-frame on the local space in a i-frame.
            i_frame: pygame.Surface 

        '''
        min_diff = float('inf')
        FRAME_SIZE = i_frame.get_rect()

        # Extract tile
        tx, ty, tw, th = tile_rect
        tile    = pygame.surfarray.pixels3d(p_frame)[tx:tx+tw, ty:ty+th, :]
        target  = pygame.surfarray.pixels3d(i_frame)

        # Compare tools
        tile_lum = tile[:,:,0] * 0.2126 + tile[:,:,1] * 0.7152 + tile[:,:,2] * 0.0722
        ts = tile_lum.shape
        target_lum = target[:,:,0] * 0.2126 + target[:,:,1] * 0.7152 + target[:,:,2] * 0.0722
        fill_tile = np.empty(target_lum.shape)
        

        for dx in range(-6,12,3):
            for dy in range(-6,12,3):
                ox = tx + dx
                oy = ty + dy

                #  Bound check
                if ox < 0 or oy < 0 or ox + GRID > FRAME_SIZE[2] or oy + GRID > FRAME_SIZE[3]:
                    continue
                
                # Inline Compare
                fill_tile[:] = np.nan
                fill_tile[ox:ox+ts[0], oy:oy+ts[1]] = tile_lum
                diff = target_lum - fill_tile
                np.nan_to_num(diff, False)
                diff = np.sum(np.sum(abs(diff)))
                # End Inline Compare

                # print dx, dy, '->', ox, oy, ':', diff
                if diff < min_diff:
                    min_diff = diff
                    min_delta = [dx, dy]

        return min_delta, min_diff

        del tile
        del target

    _, _, w, h = i_frame.get_rect()
    GRID_W = w / GRID
    GRID_H = h / GRID

    min_offs = []
    black_tiles = []
    
    for ty in xrange(0, h, GRID):
        for tx in xrange(0, w, GRID):
            tile_rect = (tx, ty, GRID, GRID)

            # Tile id
            idx = tx / GRID
            idy = ty / GRID
            tid = (idy * GRID_W) + idx
                            
            thresh = GRID*GRID * args.q
            
            min_off, min_diff = find_min_diff_offset(i_frame, p_frame, tile_rect)

            if min_diff < thresh:
                min_offs += [(tid, min_off)]
                black_tiles += [(tx, ty)]

            # screen.fill(BLACK)
            # screen.blit(p_frame, (0,0))
            # for moff in min_offs:
            #     moff_rect = (moff[0], moff[1], GRID, GRID)
            #     old_px = pygame.surfarray.pixels3d(i_frame)[moff[0]:moff[0]+GRID, moff[1]:moff[1]+GRID, :]
            #     screen_px = pygame.surfarray.pixels3d(screen)
            #     screen_px[moff[0]:moff[0]+GRID, moff[1]:moff[1]+GRID, :] = old_px
            #     del old_px
            #     del screen_px

                pygame.draw.rect(screen, GREEN, tile_rect, 2)
            draw_screen(16)

    i_frame_px = pygame.surfarray.pixels3d(i_frame)
    p_frame_px = pygame.surfarray.pixels3d(p_frame)
    p_frame_avg = fx_average(p_frame.copy(), 50)
    p_frame_avg_px = pygame.surfarray.pixels3d(p_frame_avg)
    p_frame_black = p_frame.copy()
    p_frame_black_px = pygame.surfarray.pixels3d(p_frame_black)

    # Replace found tiles with average image 
    for tid, (dx, dy) in min_offs:
        tx = tid % GRID_W * GRID
        ty = tid / GRID_W * GRID
        offx, offy = (tx+dx, ty+dy)

        black_px = i_frame_px[offx:offx+GRID, offy:offy+GRID, :]
        # black_px = p_frame_avg_px[offx:offx+GRID, offy:offy+GRID, :]
        # p_frame_black_px[moff[0]:moff[0]+GRID, moff[1]:moff[1]+GRID, :] = np.mean(np.mean(np.mean(black_px)))
        p_frame_black_px[tx:tx+GRID, ty:ty+GRID, :] = 0
        p_frame_black_px[tx:tx+GRID, ty:ty+GRID, :] = black_px

    del p_frame_px
    del p_frame_avg_px
    del p_frame_black_px

    pygame.image.save(p_frame, 'out/p-frame.jpg')
    pygame.image.save(i_frame, 'out/i-frame.jpg')
    pygame.image.save(p_frame_avg, 'out/p-frame-avg.jpg')
    pygame.image.save(p_frame_black, 'out/p-frame-fill.jpg')


    # screen.blit(p_frame, (0,0))
    # pygame.draw.rect(screen, BLACK, (min_offset[0], min_offset[1], GRID, GRID), 0)

    while True:
        draw_screen(16)


    # while True:
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT: sys.exit()

    # frame = get_frame(FRAME)
    # next_frame = get_frame(FRAME+1)
    # FRAME += 1

    # target = pygame.surfarray.pixels3d(next_frame)

    # tile = pygame.surfarray.pixels3d(frame)
    # tile = tile[0:0+GRID, 0:0+GRID, :]

    # print type(tile)

    # find_tile(tile, target, [0, 0])

    # del tile
    # del target



    # # RENDER
    # screen.blit(frame, (0,0))
    # pygame.display.flip()
    # del frame
    # del next_frame

    # # 24FPS
    # # time.sleep(1./FPS)

    # raw_input()