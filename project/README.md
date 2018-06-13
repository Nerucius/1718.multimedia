# Video Encode and Decoder with Media Player

## Installation

### Regular Installation

**Requires:**
- Python 2.7
- Numpy
- Scipy
- Pygame

### Using VirtualEnv (On Windows)
```
cd .
virtualenv env
call env/Scripts/activate.bat
pip install -r requirements.txt
```

## Usage
Command line interface help:

```
usage: codec.py [-h] [-e] [-d] [-i <filepath>] [-o <filepath>] [-b]
                [--fps <integer>] [-q <int>] [-t <int>] [-gop <int>]
                [-r <int>] [-n <int>] [--scale <int>]
                [--binarization <threshold>] [--negative] [--edges] [--gray]
                [--averaging <radius>]

Encoder / Decoder / Playback of images and video

optional arguments:
  -h, --help            show this help message and exit
  -e, --encode          encoding mode, please specify input and output
  -d, --decode          decoding mode, please specify input and output
  -i <filepath>, --input <filepath>
                        path to input ZIP file
  -o <filepath>, --output <filepath>
                        filename to store movie
  -b, --batch           batch mode
  --fps <integer>       encoding framerate
  -q <int>, --quality <int>
                        quality, lower is better
  -t <int>, --ntiles <int>
                        grid size in pixels
  -gop <int>            GOP length
  -r <int>, --seekRange <int>
                        seek range for motion estimation
  -n <int>              number of frames, leave empty for all
  --scale <int>         Binarization threshold (anything lower will become
                        black
  --binarization <threshold>
                        Binarization threshold (anything lower will become
                        black
  --negative            Invert image
  --edges               Run laplacian Edge detection
  --gray                Show in weighted grayscale
  --averaging <radius>  Average blur filter radius
```

**Considerations**
If both `--encode` and `--decode` are requested, the program first encodes then plays back the
encoded file in a player. If `--batch` mode is specified, a PyGame window is never opened.

**Example**

To encode `assets/Cubo.zip` using default parameters:

```
python main.py -i assets/Cubo.zip -o out/movie.zip --encode
```

To decode `out/movie.zip` and play it back with averaging filter applied:
```
python codec.py --decode -i out/movie.zip --averaging 1
```
