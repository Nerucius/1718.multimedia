import sys, zipfile, os
import time
import numpy as np
import pygame

from cStringIO import StringIO
from natural_sort import sort_nicely

def read_zipfile(ZIP_FILENAME):
    zf = zipfile.ZipFile(ZIP_FILENAME, 'r')

    # return values
    tile_info = {}
    config = {}
    frames = []

    # read tile_info
    for line in zf.read('tiles.txt').split('\r\n'):
        if len(line.strip()) == 0:
            continue
        f, tid, dx, dy = [int (x) for x in line.split(',')]
        if f not in tile_info:
            tile_info[f] = []
        tile_info[f] += [(tid, dx, dy)]

    # read tile_info
    for line in zf.read('config.txt').split('\r\n'):
        if len(line.strip()) == 0:
            continue
        setting, val = line.split('=')
        config[setting] = val

    # read frame data
    frames_list = zf.namelist()
    frames_list = filter(lambda x: 'frame' in x, frames_list)
    sort_nicely(frames_list)

    for frame in frames_list:
        image_bits = zf.read(frame)
        image_stream = StringIO(image_bits)
        image = pygame.image.load(image_stream, frame)
        frames += [image]

    return tile_info, config, frames

def decode(tile_info, config, frames):
    GRID = int(config['GRID'])
    GRID_W = int(config['GRID_W'])
    
    last_frame = None
    for i, frame in enumerate(frames):
        if last_frame == None or i not in tile_info:
            last_frame = frame
            yield frame
            continue

        last_frame_px = pygame.surfarray.pixels3d(last_frame)
        frame_px = pygame.surfarray.pixels3d(frame)

        for tid, dx, dy in tile_info[i]:
            tx = tid % GRID_W * GRID
            ty = tid / GRID_W * GRID
            offx, offy = (tx+dx, ty+dy)
            fill_px = last_frame_px[offx:offx+GRID, offy:offy+GRID, :]
            frame_px[tx:tx+GRID, ty:ty+GRID, :] = fill_px

        del frame_px
        del last_frame_px

        yield frame
        

if __name__ == '__main__':
    tile_info, config, frames = read_zipfile('out/movie.zip')
    FPS = int(config['FPS'])

    pygame.init()
    screen = pygame.display.set_mode([400,300])

    for frame in decode(tile_info, config, frames):
        screen.blit(frame, (0,0))
        pygame.display.flip()
        time.sleep(1./FPS)

    raw_input()