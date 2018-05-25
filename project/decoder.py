import sys, zipfile, os
import time
import numpy as np
import pygame

from cStringIO import StringIO
from natural_sort import sort_nicely

def _read_zipfile(filepath):
    ''' Read custom format zipfile structure. '''
    zf = zipfile.ZipFile(filepath, 'r')

    # return values
    tile_info = {}
    config = {}

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

    def frame_gen():
        for frame in frames_list:
            image_bits = zf.read(frame)
            image_stream = StringIO(image_bits)
            image = pygame.image.load(image_stream, frame)
            yield image
        zf.close()

    return tile_info, config, frame_gen()

def _decode_params(tile_info, config, frames):
    ''' Frame generator from an encoded set of frames and tiles. '''
    GRID = int(config['GRID'])
    GRID_W = int(config['GRID_W'])
    
    last_frame = None
    frame_idx = 0

    for frame in frames:
        
        if last_frame == None or frame_idx not in tile_info:
            pass
            
        else:
            last_frame_px = pygame.surfarray.pixels3d(last_frame)
            frame_px = pygame.surfarray.pixels3d(frame)

            for tid, dx, dy in tile_info[frame_idx]:
                tx = tid % GRID_W * GRID
                ty = tid / GRID_W * GRID
                offx, offy = (tx+dx, ty+dy)
                fill_px = last_frame_px[offx:offx+GRID, offy:offy+GRID, :]
                frame_px[tx:tx+GRID, ty:ty+GRID, :] = fill_px

            del frame_px
            del last_frame_px

        last_frame = frame
        frame_idx += 1
        yield frame

def decode(filepath):
    tile_info, config, frames = _read_zipfile(filepath)
    return config, _decode_params(tile_info, config, frames)
