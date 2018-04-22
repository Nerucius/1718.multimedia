import sys, zipfile, os
import argparse
import pygame
import time

import numpy as np
from scipy import signal

from cStringIO import StringIO

white = (255,255,255)
black = (  0,  0,  0)

def get_frame(f):
    next_frame = f % len(zip_images)

    img_data = zip_file.read(zip_images[next_frame])
    img_stream = StringIO(img_data)
    return pygame.image.load(img_stream, zip_images[next_frame])

def fx_negative(surface):
    # Get direct access to pixel data
    arr = pygame.surfarray.pixels3d(surface)
    # Invert all 3 channels, numpy broadcasting
    arr[:,:,:] = 255 - arr[:,:,:]
    return surface

def fx_grayscale(surface):
    # Get direct access to pixel data
    arr = pygame.surfarray.pixels3d(surface)
    # BT.709 Grayscale weights
    grayscale = arr[:,:,0] * 0.2126 + arr[:,:,1] * 0.7152 + arr[:,:,2] * 0.0722
    for i in range(3):
        arr[:,:,i] = grayscale

    return surface

def fx_binarize(surface, thres):
    # Get direct access to pixel data
    arr = pygame.surfarray.pixels3d(surface)

    # BT.709 Grayscale weights
    grayscale = arr[:,:,0] * 0.2126 + arr[:,:,1] * 0.7152 + arr[:,:,2] * 0.0722
    mask = grayscale < thres
    arr[ mask, :] = 0
    arr[~mask, :] = 255

    return surface

def fx_average(surface, radius):
    # Get direct access to pixel data
    arr = pygame.surfarray.pixels3d(surface)

    kernel = np.ones([radius, radius])
    kernel = kernel / kernel.sum()

    # 2D convolution using Fast Fourier Transform
    for i in range(3):
        arr[:,:,i] = signal.fftconvolve(arr[:,:,i], kernel, mode="same")

    return surface

def fx_scale(surface, scale):
    if scale == 2:
        return pygame.transform.scale2x(surface)

    w, h = (np.array(surface.get_size()) * scale).astype(int)
    return pygame.transform.scale(surface, (w,h))

def fx_edge(surface):
    # Get direct access to pixel data
    grayscale = fx_grayscale(surface)
    arr = pygame.surfarray.pixels3d(grayscale)
    kernel = np.array(
        [[ 0,-1, 0],
         [-1, 4,-1],
         [ 0,-1, 0]]
    )
    # 2D convolution using Fast Fourier Transform
    arr[:,:,0] = signal.fftconvolve(arr[:,:,0], kernel, mode="same")
    arr[:,:,1] = arr[:,:,0]
    arr[:,:,2] = arr[:,:,0]

    return surface

frame = 0
last_frame_time = -999

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Media Player")
    parser.add_argument('-i', metavar="<filepath>", type=str, default="assets/Cubo.zip",
        help="path to input ZIP file")
    parser.add_argument('-o', metavar="<filepath>", type=str,
        help="path to output folder to store resulting frames")
    parser.add_argument('--scale', metavar="<float>", type=float, default=1,
        help="Scale factor for final graphics")
    parser.add_argument('--fps', metavar="<integer>", type=int, default=25,
        help="Playback framerate")
    parser.add_argument('--binarization', metavar="<threshold>", type=int,
        help="Binarization threshold (anything lower will become black")
    parser.add_argument('--negative', action='store_true', help="Set flag to invert image")
    parser.add_argument('--edges', action='store_true', help="Set flag run laplacian Edge detection")
    parser.add_argument('--averaging', metavar="<radius>", type=int, help="Average blur filter radius")

    args = parser.parse_args()
    print args

    # Load Image List from zip file, and sort using "human" logic
    zip_file = zipfile.ZipFile(args.i)
    zip_images = zip_file.namelist()
    from natural_sort import sort_nicely
    sort_nicely(zip_images)

    # Frametive is the inverse of the FPS
    if args.fps <= 0:
        frame_time_target = -1
    else:
        frame_time_target = 1.0 / args.fps

    # PyGame Config
    pygame.init()
    pygame.display.set_caption("TMM Media Player 0.1f1")
    pygame.font.init()
    font = pygame.font.SysFont('Consolas', 16)

    # Screen Resolution
    size = np.array(get_frame(0).get_size())
    size = (size * args.scale + 0.5).astype(int)
    screen = pygame.display.set_mode(size)

    while 1:
        frame_start = time.clock()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        # Load next frame
        img_frame = get_frame(frame)

        # Apply filters
        if args.negative:
            img_frame = fx_negative(img_frame)

        if args.averaging:
            img_frame = fx_average(img_frame, args.averaging)

        if args.edges:
            img_frame = fx_edge(img_frame)

        if args.binarization:
            img_frame = fx_binarize(img_frame, args.binarization)

        if args.o:
            out_path = os.path.join(args.o, "frame_%04d.jpg" % frame)
            pygame.image.save(img_frame, out_path)

        if args.scale != 1:
            img_frame = fx_scale(img_frame, args.scale)

        screen.fill(black)
        screen.blit(img_frame, [0,0])
            
        # Free frame memory
        del img_frame
        # Advance Frame
        frame += 1

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
