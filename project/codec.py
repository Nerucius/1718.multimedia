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

def get_frame(f):
    next_frame = f % len(zip_images)
    img_data = zip_file.read(zip_images[next_frame])
    img_stream = StringIO(img_data)
    return pygame.image.load(img_stream, zip_images[next_frame])

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

if __name__ == '__main__':

    # Arguments
    parser = argparse.ArgumentParser(description="Encoder")
    parser.add_argument('-e', '--encode', action='store_true',
        help="encoding mode, please specify input and output")
    parser.add_argument('-d', '--decode', action='store_true',
        help="decoding mode, please specify input and output")
    parser.add_argument('-i', '--input', metavar="<filepath>", type=str,
        help="path to input ZIP file")
    parser.add_argument('-o', '--output', metavar="<filepath>", type=str,
        help="path to output folder to store resulting frames")

    # Encoding Arguments
    parser.add_argument('--fps', metavar="<integer>", type=int, default=25,
        help="encoding/decoding/playback framerate")
    parser.add_argument('-q', '--quality', metavar="<int>", type=int, default=5,
        help="quality, lower is better")
    parser.add_argument('-t','--ntiles', metavar="<int>", type=int, default=16,
        help="grid size in pixels")
    parser.add_argument('-gop', metavar="<int>", type=int, default=5,
        help="GOP length")
    parser.add_argument('-r','-seekRange', metavar="<int>", type=int, default=2,
        help="seek range for motion estimation")
    parser.add_argument('-n', metavar="<int>", type=int,
        help="number of frames, leave empty for all")

    # Effects arguments
    parser.add_argument('--binarization', metavar="<threshold>", type=int,
        help="Binarization threshold (anything lower will become black")
    parser.add_argument('--negative', action='store_true', help="Invert image")
    parser.add_argument('--edges', action='store_true', help="Run laplacian Edge detection")
    parser.add_argument('--gray', action='store_true', help="Show in weighted grayscale")
    parser.add_argument('--averaging', metavar="<radius>",
        type=int, help="Average blur filter radius")

    
    args = parser.parse_args()
    # --------------------

    if args.n:
        n_frames = args.n
    else:
        n_frames = len(zip_images)

    frames = [get_frame(x) for x in range(args.n+1)]
    _,_, FRAME_W, FRAME_H = frames[0].get_rect()
    SCREEN_SIZE = [FRAME_W,FRAME_H]

    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)

    GOP = args.gop
    GRID = args.g
    GRID_W = FRAME_W / args.g 
    QUALITY = args.q
    RANGE, RANGE_STEP = 2, 1


    def encode_progress(frame, frame_idx, tile_info):
        screen.blit(frame, (0,0))
        # for f, tid, dx, dy in filter(lambda x : x[0] == frame_idx, tile_info):
        #     tx = tid % GRID_W * GRID
        #     ty = tid / GRID_W * GRID
        #     # offx, offy = (tx+dx, ty+dy)
        #     pygame.draw.rect(screen, GREEN, (tx, ty, GRID, GRID), 1)
        
        draw_screen(0)

    encoder.encode(frames, 'out/movie.zip', GRID, QUALITY, GOP, RANGE, RANGE_STEP,
        CALLBACK=encode_progress)

    while True:
        draw_screen(16)

