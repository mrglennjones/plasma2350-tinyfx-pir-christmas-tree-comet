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
LED_ON_DURATION = 10  # Duration to keep the tree lit after motion

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

# Function to animate sparkles randomly on the tree
def animate_sparkles():
    for i in range(NUM_LEDS):
        if random() < LIGHT_CHANGE_CHANCE:
            led_strip.set_hsv(i, *choice(LIGHT_COLOURS))  # Random sparkle color (GRB)
        else:
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], TREE_COLOUR[2])  # Tree color

# Function to create a rocket-like growth effect with a persistent trail
def rocket_launch():
    for rocket_head in range(NUM_LEDS):
        # Light up the LEDs from the bottom to the current rocket head
        for i in range(rocket_head + 1):
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], TREE_COLOUR[2])

        # Draw the fading trail above the current rocket head
        for i in range(rocket_head + 1, min(rocket_head + FADE_TRAIL_LENGTH, NUM_LEDS)):
            distance = i - rocket_head
            # Calculate brightness based on distance from the rocket head
            brightness = TREE_COLOUR[2] * (1 - distance / FADE_TRAIL_LENGTH)
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], brightness)

        time.sleep(ROCKET_SPEED)  # Delay for rocket speed

# Function to create a reverse rocket-like shrink effect with a fading trail
def rocket_reverse():
    for rocket_head in range(NUM_LEDS - 1, -1, -1):
        # If motion is detected during the reverse animation, interrupt and start rocket_launch()
        if pir_pin.value() == 1:
            print("Motion detected! Reversing back to rocket launch.")
            rocket_launch()  # Immediately reverse direction and go back up
            return

        # Keep the LEDs lit from the bottom up to the current rocket head
        for i in range(rocket_head + 1):
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], TREE_COLOUR[2])

        # Draw the fading trail below the current rocket head
        for i in range(rocket_head + 1, min(rocket_head + FADE_TRAIL_LENGTH, NUM_LEDS)):
            distance = i - rocket_head
            # Calculate brightness based on distance from the rocket head
            brightness = TREE_COLOUR[2] * (1 - distance / FADE_TRAIL_LENGTH)
            led_strip.set_hsv(i, TREE_COLOUR[0], TREE_COLOUR[1], brightness)

        time.sleep(ROCKET_SPEED)  # Delay for rocket speed

    # Ensure all LEDs are off at the end
    for i in range(NUM_LEDS):
        led_strip.set_hsv(i, 0, 0, 0)

# Main loop to handle motion detection and animation
while True:
    current_motion_state = pir_pin.value() == 1

    if current_motion_state and not motion_detected:
        print("Motion detected! Rocket launching the tree.")
        motion_detected = True
        last_motion_time = time.time()
        rocket_launch()  # Start the rocket-like launch effect

    elif current_motion_state:
        last_motion_time = time.time()

    elif not current_motion_state and motion_detected:
        if time.time() - last_motion_time >= LED_ON_DURATION:
            print("No recent motion. Rocket reversing the tree.")
            motion_detected = False
            rocket_reverse()  # Start the rocket-like reverse effect

    # Continuously animate sparkles if the tree is lit
    if motion_detected:
        animate_sparkles()
    time.sleep(TWINKLE_SPEED)

