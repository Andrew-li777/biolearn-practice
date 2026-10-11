"""Presentation-only MultiQC 1.35 adapter; preserve exact RGB palette values."""
import re
from multiqc.utils import mqc_colour

original = mqc_colour.color_to_rgb_string
def color_to_rgb_string(color):
    if isinstance(color, str) and re.fullmatch(r'\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*', color):
        channels = [int(x.strip()) for x in color.split(',')]
        if all(0 <= x <= 255 for x in channels):
            color = 'rgb(' + ','.join(map(str, channels)) + ')'
    return original(color)
mqc_colour.color_to_rgb_string = color_to_rgb_string
