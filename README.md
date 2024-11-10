# plasma2350-tinyfx-pir-christmas-tree-comet
pimoroni plasma2350 led strip tiny fx pir sensor Christmas tree comet 🌠🎄🎅

This micropython script for the pimoroni plasma 2350/2040, detects motion with the pimoroni tinyfx PIR sensor connected to the Qwic port then using connected led string, it launches a green comet from the bottom of the led strip, creating a christmas tree with twinkling lights, once the pir sensor detects no motion it will then reverse the comet, leaving the tree lights off.

one small additional feature is that it will interrupt fade-out when motion is detected and captures the current brightness level, allowing LEDs to fade in from the interrupted level back to full brightness. 

Requirements:-
- Plasma 2350: https://shop.pimoroni.com/products/plasma-2350?variant=42092628246611
- PIR Stick for Tiny FX: https://shop.pimoroni.com/products/pir-stick?variant=53489719017851
- Any WS2812/Neopixel compatible LED strip

The Tinyfx pir sensor comes with a 3 pin connector to connect it to the TinyFX system but i spliced together with a 4pin Qwiic connector using just the positive, negative and yellow wire, leaving the blue one unused)

![VideoCapture_20241110-102114](https://github.com/user-attachments/assets/7dcc7790-99bb-48b1-a0b5-bdad03b1f392)


https://github.com/user-attachments/assets/221deb47-5b26-4eee-a803-7f78f45a3116


