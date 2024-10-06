import badger2040
import jpegdec
import pngdec
import qrcode
import math


# Global Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

IMAGE_WIDTH = 128

EVENT_PADDING = 20
EVENT_HEIGHT = 30
TITLE_HEIGHT = 20
NAME_HEIGHT = HEIGHT - EVENT_HEIGHT - (TITLE_HEIGHT) - 2
TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 1

EVENT_TEXT_SIZE = 0.6
TITLE_TEXT_SIZE = 0.5

NAME_PADDING = 20
TITLE_SPACING = 10

BADGE_PATH = "/badges/badge.txt"

DEFAULT_TEXT = """Auth0 by Okta
Peter Fernandez
Developer Advocate
https://a0.to/do
"""

# ------------------------------
#      Utility functions
# ------------------------------


# Reduce the size of a string until it fits within a given width
def truncatestring(text, text_size, width):
    while True:
        length = display.measure_text(text, text_size)
        if length > 0 and length > width:
            text = text[:-1]
        else:
            text += ""
            return text

# ------------------------------
#      QR functions
# ------------------------------

def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.set_pen(15)
    display.rectangle(ox, oy, size, size)
    display.set_pen(0)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)

# ------------------------------
#      Badge functions
# ------------------------------

# Draw the badge, including user text
def draw_badge():
    display.set_pen(0)
    display.clear()

    try:
        # Generate QRCode
        code = qrcode.QRCode()
        code.set_text(badge_url)
        size, _ = measure_qr_code(128, code)
        left = WIDTH - 124
        top = int((HEIGHT / 2) - (size / 2))
        draw_qr_code(left, top, 128, code)        
    except (OSError, RuntimeError):
        code = qrcode.QRCode()

    # Draw a border around the image
    display.set_pen(0)
    display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - 1, 0)
    display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - IMAGE_WIDTH, HEIGHT - 1)
    display.line(WIDTH - IMAGE_WIDTH, HEIGHT - 1, WIDTH - 1, HEIGHT - 1)
    display.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1)

    # Uncomment this if a white background is wanted behind the event
    # display.set_pen(15)
    # display.rectangle(1, 1, TEXT_WIDTH, EVENT_HEIGHT - 1)

    # Draw the event
    display.set_pen(15)  # Change this to 0 if a white background is used
    display.set_font("serif")
    event_padding = (TEXT_WIDTH - display.measure_text(event, EVENT_TEXT_SIZE)) // 2    
    display.text(event, event_padding + 3, (EVENT_HEIGHT // 2) + 1, WIDTH, EVENT_TEXT_SIZE)

    # Draw a white background behind the name
    display.set_pen(15)
    display.rectangle(1, EVENT_HEIGHT + 1, TEXT_WIDTH, NAME_HEIGHT)

    # Draw the name, scaling it based on the available width
    display.set_pen(0)
    display.set_font("sans")
    name_offset = -10
    for name in names:
        name_size = 2.0  # A sensible starting scale
        while True:
            name_padding = display.measure_text(name, name_size)
            if name_padding >= (TEXT_WIDTH - NAME_PADDING) and name_size >= 0.1:
                name_size -= 0.01
            else:
                display.text(name, (TEXT_WIDTH - name_padding) // 2, (NAME_HEIGHT // 2) + EVENT_HEIGHT + name_offset, WIDTH, name_size)
                name_offset += math.ceil(10 * name_size) + 15
                break

    # Draw a white backgrounds behind the title
    display.set_pen(15)
    display.rectangle(1, HEIGHT - TITLE_HEIGHT, TEXT_WIDTH, TITLE_HEIGHT - 1)

    # Draw the title text
    display.set_pen(0)
    display.set_font("sans")    
    display.text(title_text, TITLE_SPACING, HEIGHT - (TITLE_HEIGHT // 2), WIDTH, TITLE_TEXT_SIZE)

    display.update()


# ------------------------------
#        Program setup
# ------------------------------

# Create a new Badger and set it to update NORMAL
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_NORMAL)
display.set_thickness(2)

jpeg = jpegdec.JPEG(display.display)
png = pngdec.PNG(display.display)

# Open the badge file
try:
    badge = open(BADGE_PATH, "r")
except OSError:
    with open(BADGE_PATH, "w") as f:
        f.write(DEFAULT_TEXT)
        f.flush()
    badge = open(BADGE_PATH, "r")

# Read in the next 6 lines
event = badge.readline()        
names = badge.readline().split()
title_text = badge.readline()    
badge_url = badge.readline() 

# Truncate all of the text (except for the name as that is scaled)
event = truncatestring(event, EVENT_TEXT_SIZE, TEXT_WIDTH)

title_text = truncatestring(title_text, TITLE_TEXT_SIZE, TEXT_WIDTH - TITLE_SPACING)

# ------------------------------
#       Main program
# ------------------------------

draw_badge()

while True:
    # Sometimes a button press or hold will keep the system
    # powered *through* HALT, so latch the power back on.
    display.keepalive()

    # If on battery, halt the Badger to save power, it will wake up if any of the front buttons are pressed
    display.halt()
