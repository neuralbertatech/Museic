# musemidi

This is a simple program that takes in an LSL stream from a Muse 2 headset and outputs a software instrument MIDI stream based on brain state.

This program will theoretically work with any Muse LSL input and any MIDI output, but it was developed using and only tested with:
* PetalMetrics for LSL Input: https://petal.tech/metrics-api
* Garageband for MIDI Output: https://www.apple.com/ca/mac/garageband/

**To use:**
Turn on the Muse
Open PetalMetrics and click stream
Wait for the connection to establish and double check that you are connected to the correct muse

Open Garageband
Create a new file and add a new software instrument

Run `python musemidi.py`

Garageband should notice the new MIDI stream available and notify you of it being 'connected'