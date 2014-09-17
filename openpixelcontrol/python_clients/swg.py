#!/usr/bin/env python



from __future__ import division
import time
import sys
import optparse
try:
    import json
except ImportError:
    import simplejson as json

import opc
import color_utils


#-------------------------------------------------------------------------------
# command line

parser = optparse.OptionParser()
parser.add_option('-l', '--layout', dest='layout',
                    action='store', type='string',
                    help='layout file')
parser.add_option('-s', '--server', dest='server', default='127.0.0.1:7890',
                    action='store', type='string',
                    help='ip and port of server')
parser.add_option('-f', '--fps', dest='fps', default=20,
                    action='store', type='int',
                    help='frames per second')

options, args = parser.parse_args()

if not options.layout:
    parser.print_help()
    print
    print 'ERROR: you must specify a layout file using --layout'
    print
    sys.exit(1)


#-------------------------------------------------------------------------------
# parse layout file

print
print '    parsing layout file'
print

coordinates = []
for item in json.load(open(options.layout)):
    if 'point' in item:
        coordinates.append(tuple(item['point']))


#-------------------------------------------------------------------------------
# connect to server

client = opc.Client(options.server, verbose=False)
if client.can_connect():
    print '    connected to %s' % options.server
else:
    # can't connect, but keep running in case the server appears later
    print '    WARNING: could not connect to %s' % options.server
print


#-------------------------------------------------------------------------------
# color function

def pixel_color(time, coord, ii, n_pixels):
    """Compute the color of a given pixel.

    t: time in seconds since the program started.
    ii: which pixel this is, starting at 0
    coord: the (x, y, z) position of the pixel as a tuple
    n_pixels: the total number of pixels

    Returns an (r, g, b) tuple in the range 0-255

    """
    # make moving stripes for x, y, and z
    x, y, z = coord

    r = color_utils.cos(z, offset=time * 0.1, period=5, minn=0, maxx=0.7)

    g = color_utils.cos(z, offset=time * 0.2, period=2.5, minn=0, maxx=0.7)

    b = color_utils.cos(x, offset=time * 0.1, period=10, minn=0, maxx=0.7)

    r, g, b = color_utils.contrast((r, g, b), 0.1, 2)


    # make a moving white dot showing the order of the pixels in the layout file
    spark_ii = (time*60) % n_pixels
    spark_rad = 10
    spark_val = max(0, (spark_rad - color_utils.mod_dist(ii, spark_ii, n_pixels)) / spark_rad)
    spark_val = min(1, spark_val*64)
    #r += spark_val
    g += spark_val
    b += spark_val

    if ii % 10:
        if g > 0.3:
            b += spark_val
        else:
            g += spark_val

    else:
        if g < 0.3:
            b += spark_val
            r -= spark_val
        else:
            b = 0


    #print ii
    #
    
    if ii > 60 and ii < 120:
        r, g, b = 100

    # apply gamma curve
    # only do this on live leds, not in the simulator
    #r, g, b = color_utils.gamma((r, g, b), 2.2)

    return (r*256, g*256, b*256)




#-------------------------------------------------------------------------------
# send pixels

print '    sending pixels forever (control-c to exit)...'
print

n_pixels = len(coordinates)
start_time = time.time()
while True:
    t = time.time() - start_time
    pixels = [pixel_color(t, coord, ii, n_pixels) for ii, coord in enumerate(coordinates)]
    #print '     ' + pixels
    client.put_pixels(pixels, channel=0)
    time.sleep(0.002 / options.fps)
