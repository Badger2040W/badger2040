import badger2040
import jpegdec
import pngdec
import qrcode
import math

# Global Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

IMAGE_WIDTH = 128

COMPANY_PADDING = 8
COMPANY_HEIGHT = 30
DETAILS_HEIGHT = 20
NAME_HEIGHT = HEIGHT - COMPANY_HEIGHT - (DETAILS_HEIGHT) - 2
TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 1

COMPANY_TEXT_SIZE = 0.6
DETAILS_TEXT_SIZE = 0.5

LEFT_PADDING = 5
NAME_PADDING = 20
DETAIL_SPACING = 10

BADGE_PATH = "/badges/badge.txt"

DEFAULT_TEXT = """Auth0 by Okta
Advocate Name
Event
The Event
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

    # Uncomment this if a white background is wanted behind the company
    # display.set_pen(15)
    # display.rectangle(1, 1, TEXT_WIDTH, COMPANY_HEIGHT - 1)

    # Draw the company
    display.set_pen(15)  # Change this to 0 if a white background is used
    display.set_font("serif")
    display.text(company, COMPANY_PADDING + LEFT_PADDING, (COMPANY_HEIGHT // 2) + 1, WIDTH, COMPANY_TEXT_SIZE)

    # Draw a white background behind the name
    display.set_pen(15)
    display.rectangle(1, COMPANY_HEIGHT + 1, TEXT_WIDTH, NAME_HEIGHT)

    # Draw the name, scaling it based on the available width
    display.set_pen(0)
    display.set_font("sans")
    name_offset = -10
    for name in names:
        name_size = 2.0  # A sensible starting scale
        while True:
            name_length = display.measure_text(name, name_size)
            if name_length >= (TEXT_WIDTH - NAME_PADDING) and name_size >= 0.1:
                name_size -= 0.01
            else:
                display.text(name, (TEXT_WIDTH - name_length) // 2, (NAME_HEIGHT // 2) + COMPANY_HEIGHT + name_offset, WIDTH, name_size)
                name_offset += math.ceil(10 * name_size) + 15
                break

    # Draw a white backgrounds behind the details
    display.set_pen(15)
    display.rectangle(1, HEIGHT - DETAILS_HEIGHT, TEXT_WIDTH, DETAILS_HEIGHT - 1)

    # Draw the second detail's title and text
    display.set_pen(0)
    display.set_font("sans")    
    name_length = display.measure_text(detail_text, DETAILS_TEXT_SIZE) // 4
    display.text(detail_text, LEFT_PADDING + name_length + DETAIL_SPACING, HEIGHT - (DETAILS_HEIGHT // 2), WIDTH, DETAILS_TEXT_SIZE)

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
company = badge.readline()        
names = badge.readline().split()  
detail_title = badge.readline()   
detail_text = badge.readline()    
badge_url = badge.readline()     

# Truncate all of the text (except for the name as that is scaled)
company = truncatestring(company, COMPANY_TEXT_SIZE, TEXT_WIDTH)

detail_title = truncatestring(detail_title, DETAILS_TEXT_SIZE, TEXT_WIDTH)
detail_text = truncatestring(detail_text, DETAILS_TEXT_SIZE,
                              TEXT_WIDTH - DETAIL_SPACING - display.measure_text(detail_title, DETAILS_TEXT_SIZE))

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
