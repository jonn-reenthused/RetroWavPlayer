# RetroWavPlayer
A wav player using a Raspberry Pico for retro computers

This is a simple device that allows selection and playing of WAV files from a headphone port. This is useful for older computers where the software hasn't been encoded into a format that devices like the Casduino can't play.

The project includes the code in Micropython format and a sample board design, although the circuit is simple enough to be knocked up on a breadboard.

The code also uses elements from some other micropython projects, including:

- Dan Perron's PicoAudioPWM https://github.com/danjperron/PicoAudioPWM
- Joeky Zhan's awesome micropython lib https://github.com/joeky888/awesome-micropython-lib/tree/master/Audio

Parts for sample board
- 1 x Raspberry Pi Pico
- 1 x Raspberry Pi screen, the code is based around the Waveshare 1.8" LCD Display
- 1 x Audio Socket
- 1 x SD card board, most should work
- 4 x buttons, Up, Down, Select and Back
- 1 x LM386N
- 2 x 10uf Caps
- 1 x 100uf Cap
- 2 x 10nf Caps
- 1 x 100 resistor
- 1 x 10k resistor
- 1 x variable resistor

=== VERSION 0.1 2023-10-04 ===

Simple interface, list of WAV files from an SD card. Up, Down button to choose, Select button to select. The next screen allows the WAV file to be played using the select button, the back button will stop the wav, if the wav is stopped the back button will return to the menu.
