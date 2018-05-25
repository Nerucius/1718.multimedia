import sys, zipfile, os
import numpy as np
import pygame

from effects import fx_average

WHITE   = (255,255,255)
BLACK   = (  0,  0,  0)
RED     = (255,  0,  0)
GREEN   = (  0,255,  0)
BLUE    = (  0,  0,255)
CYAN    = (  0,255,255)
MAGENTA = (255,  0,255)
YELLOW  = (255,255,  0)


def find_min_diff_offset(i_frame_lum, p_frame_lum, tile_rect, GRID, RANGE, RANGE_STEP):
    ''' Compare a tile rectangle from a p-frame on the local space in a i-frame.
        i_frame: np.array (2d) 
        p_frame: np.array (2d) 
        tile_rect: (x,y,w,h) rect on the p_frame to find in the i_frame
    '''
    FRAME_W, FRAME_H = i_frame_lum.shape

    # Extract tile
    tx, ty, tw, th = tile_rect
    target_lum = i_frame_lum
    tile_lum = p_frame_lum[tx:tx+tw, ty:ty+th]
    
    # Compare tools
    fill_tile = np.empty(i_frame_lum.shape)

    min_diff = float('inf')

    RANGE_START = -RANGE
    RANGE_END = RANGE + 1

    for dx in xrange(RANGE_START, RANGE_END, RANGE_STEP):
        for dy in xrange(RANGE_START, RANGE_END, RANGE_STEP):
            ox = tx + dx
            oy = ty + dy

            #  Bound check
            if ox < 0 or oy < 0 or ox + GRID > FRAME_W or oy + GRID > FRAME_H:
                continue
            
            # Inline Compare
            fill_tile[:] = np.nan
            fill_tile[ox:ox+tw, oy:oy+th] = tile_lum
            diff = target_lum - fill_tile
            np.nan_to_num(diff, False)
            diff = np.sum(np.sum(np.abs(diff)))
            # End Inline Compare

            # print dx, dy, '->', ox, oy, ':', diff
            if diff < min_diff:
                min_diff = diff
                min_delta = [dx, dy]

    return min_delta, min_diff


def find_tiles(i_frame, p_frame, GRID=16, QUALITY=5, RANGE=4, RANGE_STEP=2):
    _, _, w, h = i_frame.get_rect()

    GRID_W = w / GRID
    GRID_H = h / GRID

    # Quality threshold
    thresh = GRID*GRID * QUALITY

    # preprocess frames
    i_frame_px = pygame.surfarray.pixels3d(i_frame)
    p_frame_px = pygame.surfarray.pixels3d(p_frame)
    i_frame_lum = i_frame_px[:,:,0] * 0.2126 + i_frame_px[:,:,1] * 0.7152 + i_frame_px[:,:,2] * 0.0722
    p_frame_lum = p_frame_px[:,:,0] * 0.2126 + p_frame_px[:,:,1] * 0.7152 + p_frame_px[:,:,2] * 0.0722

    for ty in xrange(0, h, GRID):
        for tx in xrange(0, w, GRID):
            tile_rect = (tx, ty, GRID, GRID)

            # pass luminance and tile coordinates
            pos_delta, min_diff = find_min_diff_offset(i_frame_lum, p_frame_lum, tile_rect, 
                GRID=GRID, RANGE=RANGE, RANGE_STEP=RANGE_STEP)

            # If diff is under threshold, return this tile and delta
            if min_diff < thresh:
                # Tile id
                idx = tx / GRID
                idy = ty / GRID
                tid = (idy * GRID_W) + idx
                yield (tid, pos_delta)


def encode(frames, FILE_OUT, GRID, QUALITY, GOP, RANGE, RANGE_STEP, FPS=24, CALLBACK=None):
    _,_, FRAME_W, FRAME_H = frames[0].get_rect()
    GRID_W, GRID_H = FRAME_W / GRID, FRAME_H / GRID

    ZIP_FILE = zipfile.ZipFile(FILE_OUT, 'w', compression=zipfile.ZIP_DEFLATED)
    tile_info = []

    for FRAME in xrange(len(frames)):

        # Load current frame as P Frame
        p_frame = frames[FRAME]
        IMAGE_FILENAME = 'frame-%03d.jpg' % FRAME

        if FRAME % GOP == 0:
            # Save ref picture if we're at a GOP boundary
            pygame.image.save(p_frame, 'out/frame-%03d.jpg' % FRAME)

        else:
            # Load prev frame for predictions
            i_frame = frames[FRAME - 1]

            # screen.blit(p_frame, (0,0))
            # pygame.display.flip()

            p_frame_out = p_frame.copy()
            p_frame_px = pygame.surfarray.pixels3d(p_frame)
            p_frame_out_px = pygame.surfarray.pixels3d(p_frame_out)

            for tid, (dx, dy) in find_tiles(i_frame, p_frame,
                GRID=GRID, QUALITY=QUALITY, RANGE=RANGE, RANGE_STEP=RANGE_STEP):

                tx = tid % GRID_W * GRID
                ty = tid / GRID_W * GRID
                fill_px = p_frame_px[tx:tx+GRID, ty:ty+GRID, :]
                p_frame_out_px[tx:tx+GRID, ty:ty+GRID, :] = np.mean(fill_px, (0,1,))
                del fill_px

                tile_info += ["%d,%d,%d,%d\n" % (FRAME, tid, dx, dy)]

            del p_frame_px
            del p_frame_out_px
            
            fx_average(p_frame_out, 4)
            pygame.image.save(p_frame_out, 'out/%s' % IMAGE_FILENAME)
        
            if CALLBACK: CALLBACK(p_frame_out, FRAME, tile_info)
        
        ZIP_FILE.write('out/%s' % IMAGE_FILENAME, IMAGE_FILENAME)
        os.unlink('out/%s' % IMAGE_FILENAME)


    CONFIG_FILE = open('out/config.txt', 'w')
    CONFIG_FILE.write("GRID=%d\n" % GRID)
    CONFIG_FILE.write("GRID_W=%d\n" % GRID_W)
    CONFIG_FILE.write("GRID_H=%d\n" % GRID_H)
    CONFIG_FILE.write("FPS=%d\n" % FPS)
    CONFIG_FILE.close()
    ZIP_FILE.write('out/config.txt', 'config.txt')
    os.unlink('out/config.txt')

    TILE_FILE = open('out/tiles.txt', 'w')
    TILE_FILE.writelines(tile_info)
    TILE_FILE.close()
    ZIP_FILE.write('out/tiles.txt', 'tiles.txt')
    ZIP_FILE.close()    
    os.unlink('out/tiles.txt')

