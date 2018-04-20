import sys, zipfile
import argparse
import pygame
import time
import numpy

from cStringIO import StringIO

# Screen Resolution
size = width, height = [320, 240]
screen = pygame.display.set_mode(size)

white = (255,255,255)
black = (  0,  0,  0)

zip_filepath = "assets/Cubo.zip"
zip_file = zipfile.ZipFile(zip_filepath)
zip_images = zip_file.namelist()

def get_frame(f):
    img_data = zip_file.read(zip_images[f])
    img_stream = StringIO(img_data)
    return pygame.image.load(img_stream, zip_images[f])

def fx_negative(surface):
    # Get direct access to pixel data
    arr = pygame.surfarray.pixels3d(surface)
    # Invert all 3 channels, numpy broadcasting
    arr[:,:,:] = 255 - arr[:,:,:]
    return surface

def fx_binarize(surface, thres):
    # Get direct access to pixel data
    arr = pygame.surfarray.pixels3d(surface)

    # BT.709 Grayscale weights
    grayscale = arr[:,:,0] * 0.2126 + arr[:,:,1] * 0.7152 + arr[:,:,2] * 0.0722
    mask = grayscale < thres
    for i in range(3):
        arr[mask,i] = 0
        arr[~mask,i] = 255

    return surface

frame = 0
last_frame_time = -999

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Media Player")
    parser.add_argument('-i', metavar="<filepath>", type=str, help="path to input ZIP file")
    parser.add_argument('--fps', metavar="<integer>", type=int, default=25,
        help="Playback framerate")
    parser.add_argument('--binarization', metavar="<threshold>", type=int,
        help="Binarization threshold (anything lower will become black")
    parser.add_argument('--negative', action='store_true', help="Set flag to invert image")
    parser.add_argument('--averaging', metavar="<radius>", type=int, help="Average blur filter radius")

    args = parser.parse_args()

    print args

    frame_time = 1.0 / args.fps

    pygame.init()
    pygame.display.set_caption("TMM Media Player 0.1f1")

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        # Load next frame
        img_frame = get_frame(frame % 100)

        if args.binarization:
            img_frame = fx_binarize(img_frame, args.binarization)

        if args.negative:
            img_frame = fx_negative(img_frame)

        screen.fill(black)
        screen.blit(img_frame, [0,0])
            
        frame += 1
        # Free frame memory
        del img_frame

        # wait for X seconds, as many as necesary to stay on target frame time
        wait_time = frame_time - (time.clock() - last_frame_time)
        time.sleep(max(0,frame_time))
        last_frame_time = time.clock()

        # Show new frame
        pygame.display.flip()