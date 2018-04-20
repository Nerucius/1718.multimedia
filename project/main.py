import sys, zipfile
import pygame
import time

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

frame = 0
last_frame_time = 0
frame_time = 1.0 / 25 # 25FPS

if __name__ == '__main__':
    for arg in sys.argv:
        print arg

    pygame.init()

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        # Load next frame
        img_frame = get_frame(frame % 100)
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