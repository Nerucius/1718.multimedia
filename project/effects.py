import pygame
from scipy import signal

def fx_scale(surface, dim, target=None):
    if target:
        return pygame.transform.smoothscale(surface, dim, target)
    else:
        return pygame.transform.smoothscale(surface, dim)

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