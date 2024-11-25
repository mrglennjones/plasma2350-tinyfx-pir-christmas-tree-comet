from plasma import plasma2040
import plasma
import machine
import time
from random import random, choice

# Configuration constants for animation and motion detection
NUM_LEDS = 50
ROCKET_SPEED = 0.05  # Speed of the rocket animation (higher value for slower speed)
FADE_TRAIL_LENGTH = 15  # Length of the fading trail behind the rocket for a smooth effect
TWINKLE_SPEED = 0.2  # Speed of the twinkle animation
LED_ON_DURATION = 20  # Duration (in seconds) to keep the tree lit after motion stops
DEBOUNCE_TIME = 0.5  # Time in seconds to debounce the PIR sensor
MOTION_CHECK_INTERVAL = 0.1  # Time between PIR sensor checks

# Tree light constants (GRB color order)
TREE_COLOUR = [0.0, 1.0, 0.6]  # Green tree color (HSV for GRB)
LIGHT_RATIO = 8  # Ratio for fairy lights

# Updated sparkle colors for GRB with more variety
LIGHT_COLOURS = (
    (0.0, 1.0, 1.0),   # Red (HSV for GRB)
    (0.16, 1.0, 1.0),  # Yellow (HSV for GRB)
    (0.33, 1.0, 1.0),  # Green (HSV for GRB)
    (0.5, 1.0, 1.0),   # Cyan (HSV for GRB)
    (0.66, 1.0, 1.0),  # Blue (HSV for GRB)
    (0.83, 1.0, 1.0),  # Magenta (HSV for GRB)
    (0.1, 0.8, 1.0),   # Orange (HSV for GRB, with lower saturation)
    (0.95, 0.7, 1.0)   # Pink (HSV for GRB, with lower saturation)
)
LIGHT_CHANGE_CHANCE = 0.05  # Probability of sparkles for a subtle effect

# Initialize the WS2812 LED strip
led_strip = plasma.WS2812(NUM_LEDS, pio=0, sm=0, dat=plasma2040.DAT, color_order=plasma.COLOR_ORDER_GRB)
led_strip.start()

# Initialize the PIR sensor
pir_pin = machine.Pin(21, machine.Pin.IN)

# Track the state of motion and time
motion_detected = False
last_motion_time = 0
tree_active = False  # Tracks if the tree is in its "launched" state
idle_state = True  # Tracks if the tree is fully idle
last_motion_check = time.time()  # Tracks the last time we checked the PIR sensor
reversing_index = None  # Tracks the progress of rocket_reverse()

# Function to debounce the PIR sensor
def debounce_pir():
    """Check for consistent motion detection over a debounce period."""
    if pir_pin.value() == 1:
        time.sleep(DEBOUNCE_TIME)  # Wait for the debounce time
        if pir_pin.value() == 1:  # Check again to confirm motion
            return True
    return False

# Function to animate sparkles randomly on the tree
def animate_sparkles():
    for i in range(NUM_LEDS):
        if random() < LIGHT_CHANGE_CHANCE:
            led_strip.set_hsv(i, *choice(LIGHT_COLOURS))  # Random sparkle color (GRB)
        else:
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], TREE_COLOUR[2])  # Tree color

# Function to grow the tree from a given starting position
def grow_tree_from(start_position):
    global tree_active, last_motion_time
    tree_active = True
    last_motion_time = time.time()  # Reset timeout timer
    for rocket_head in range(start_position, NUM_LEDS):
        # Light up the LEDs from the bottom to the current rocket head
        for i in range(max(0, rocket_head + 1)):
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], TREE_COLOUR[2])

        # Draw the fading trail above the current rocket head
        for i in range(max(0, rocket_head + 1), min(rocket_head + FADE_TRAIL_LENGTH, NUM_LEDS)):
            distance = i - rocket_head
            brightness = TREE_COLOUR[2] * (1 - distance / FADE_TRAIL_LENGTH)
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], brightness)

        time.sleep(ROCKET_SPEED)

# Function to create a reverse rocket-like shrink effect with a fading trail
def rocket_reverse():
    global tree_active, reversing_index, idle_state
    tree_active = False  # Tree is now reversing
    for rocket_head in range(reversing_index if reversing_index is not None else NUM_LEDS - 1, -1, -1):
        reversing_index = rocket_head  # Save progress in case motion is detected

        # Check motion only during rocket_reverse
        if debounce_pir():
            print("Motion detected! Growing tree from current reverse position.")
            grow_tree_from(reversing_index)  # Regrow the tree from the current position
            reversing_index = None  # Clear the reversing state
            return

        # Turn off LEDs from the current rocket head
        for i in range(rocket_head + 1):
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], TREE_COLOUR[2])

        # Draw the fading trail below the current rocket head
        for i in range(rocket_head + 1, min(rocket_head + FADE_TRAIL_LENGTH, NUM_LEDS)):
            distance = i - rocket_head
            brightness = TREE_COLOUR[2] * (1 - distance / FADE_TRAIL_LENGTH)
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], brightness)

        time.sleep(ROCKET_SPEED)

    reversing_index = None  # Reset reversing index
    idle_state = True  # Set tree to idle
    for i in range(NUM_LEDS):
        led_strip.set_hsv(i, 0, 0, 0)  # Ensure all LEDs are off

# Function to handle motion detection during idle or reverse
def check_motion():
    global motion_detected, last_motion_time, idle_state, reversing_index

    # Detect motion only if idle or during rocket_reverse
    if idle_state or not tree_active:
        current_motion_state = debounce_pir()
        if current_motion_state:
            print("Motion detected! Launching or regrowing tree.")
            motion_detected = True
            idle_state = False  # Reset idle state
            grow_tree_from(reversing_index if reversing_index is not None else 0)  # Grow tree from start or reverse position
            reversing_index = None  # Clear reverse state

# Main loop for animation and motion detection
while True:
    # Handle motion detection at its own pace
    if time.time() - last_motion_check >= MOTION_CHECK_INTERVAL:
        last_motion_check = time.time()
        check_motion()

    # Continuously animate sparkles if the tree is active
    if tree_active:
        animate_sparkles()

    # Trigger rocket_reverse() if timeout expires and no motion is detected
    if tree_active and time.time() - last_motion_time >= LED_ON_DURATION:
        print("Tree timeout expired. Starting rocket_reverse().")
        rocket_reverse()

    time.sleep(TWINKLE_SPEED)

