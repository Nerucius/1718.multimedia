import sys, zipfile, os
import pygame
import time
import numpy as np
import argparse

from cStringIO import StringIO
from natural_sort import sort_nicely
from effects import *

import encoder
import decoder
import player

WHITE   = (255,255,255)
BLACK   = (  0,  0,  0)
RED     = (255,  0,  0)
GREEN   = (  0,255,  0)
BLUE    = (  0,  0,255)
CYAN    = (  0,255,255)
MAGENTA = (255,  0,255)
YELLOW  = (255,255,  0)

def read_frames(filepath):
    ''' Lazy frame reader generator. '''
    z = zipfile.ZipFile(filepath)
    zip_images = z.namelist()
    sort_nicely(zip_images)

    for frame_name in zip_images:
        frame_data = z.read(frame_name)
        frame_stream = StringIO(frame_data)
        frame = pygame.image.load(frame_stream, frame_name)
        yield frame
    z.close()

def draw_screen(sleep=None):
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    pygame.display.flip()
    if sleep is None:
        raw_input()
    else:
        time.sleep(sleep/1000.)

def apply_effects(img_frame, args):
    if args.negative: fx_negative(img_frame)
    if args.averaging: fx_average(img_frame, args.averaging)
    if args.edges: fx_edge(img_frame)
    if args.binarization: fx_binarize(img_frame, args.binarization)
    if args.gray: fx_grayscale(img_frame)

# def encode_progress(frame, frame_idx, tile_info):
#     GRID = args.ntiles
#     GRID_W = FRAME_W / GRID
#     tile_info = [line.strip().split(',') for line in tile_info]
#     screen.blit(frame, (0,0))

#     for tile in tile_info:
#         f, tid, dx, dy = [int(x) for x in tile]
#         if f != frame_idx: continue
#         tx = tid % GRID_W * GRID
#         ty = tid / GRID_W * GRID
#         # offx, offy = (tx+dx, ty+dy)
#         # pygame.draw.rect(screen, GREEN, (tx, ty, GRID, GRID), 1)
#     draw_screen(0)

if __name__ == '__main__':

    # Arguments
    parser = argparse.ArgumentParser(description="Encoder")
    parser.add_argument('-e', '--encode', action='store_true',
        help="encoding mode, please specify input and output")
    parser.add_argument('-d', '--decode', action='store_true',
        help="decoding mode, please specify input and output")
    parser.add_argument('-i', '--input', metavar="<filepath>", type=str,
        help="path to input ZIP file", default='assets/Cubo.zip')
    parser.add_argument('-o', '--output', metavar="<filepath>", type=str,
        default='out/movie.zip', help='filename to store movie' )
    parser.add_argument('-b', '--batch', action='store_true', help="batch mode")

    # Encoding Arguments
    parser.add_argument('--fps', metavar="<integer>", type=int,
        help="encoding framerate")
    parser.add_argument('-q', '--quality', metavar="<int>", type=int, default=15,
        help="quality, lower is better")
    parser.add_argument('-t','--ntiles', metavar="<int>", type=int, default=16,
        help="grid size in pixels")
    parser.add_argument('-gop', metavar="<int>", type=int, default=5,
        help="GOP length")
    parser.add_argument('-r','--seekRange', metavar="<int>", type=int, default=2,
        help="seek range for motion estimation")
    parser.add_argument('-n', metavar="<int>", type=int,
        help="number of frames, leave empty for all")

    # Player Arguments
    parser.add_argument('--scale', metavar="<int>", type=int, default=1,
        help="Binarization threshold (anything lower will become black")

    # Effects arguments
    parser.add_argument('--binarization', metavar="<threshold>", type=int,
        help="Binarization threshold (anything lower will become black")
    parser.add_argument('--negative', action='store_true', help="Invert image")
    parser.add_argument('--edges', action='store_true', help="Run laplacian Edge detection")
    parser.add_argument('--gray', action='store_true', help="Show in weighted grayscale")
    parser.add_argument('--averaging', metavar="<radius>",
        type=int, help="Average blur filter radius")

    
    args = parser.parse_args()
    print args

    pygame.init()
    screen = pygame.display.set_mode([400,300])

    if args.encode:
        frame_reader = read_frames(args.input)

        def progress(frame, frame_idx, tinfo):
            _,_,FW,FH = frame.get_rect()
            player.playback(
                {'FPS':0, 'SCALE':args.scale, 'FRAME_W':FW, 'FRAME_H':FH},
            [frame])

        if args.batch:
            CALLBACK = None
        else:
            CALLBACK = progress

        FPS = 25
        if args.fps: FPS = args.fps

        encoder.encode(frame_reader, args.output,
            GRID=args.ntiles, QUALITY=args.quality, GOP=args.gop,
            RANGE=args.seekRange, RANGE_STEP=max(args.seekRange / 2, 1),
            CALLBACK=CALLBACK, FPS=FPS, MAX_FRAMES=args.n)

    if args.decode:
        config, frames = decoder.decode(args.input)
        if args.fps: config['FPS'] = args.fps

        print config 
        config['SCALE'] = args.scale

        player.playback(config, frames)


    draw_screen(0)

    print "EXIT 0"


