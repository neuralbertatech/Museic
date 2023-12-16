from pylsl import StreamInlet, resolve_stream
import time
import rtmidi
import numpy as np
import matplotlib.pyplot as plt
import threading
import queue

pitchBins = [(35, 45), (45, 55), (55, 65), (65, 75), (75, 85)]
latency = 1  # Window of time (in s) to collect data
samples_per_sec = 220


class MyThread(threading.Thread):
    def __init__(self, queue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue

    def run(self):
        midiout = rtmidi.MidiOut()
        midiout.open_virtual_port("MuseMIDI")

        with midiout:
            while True:
                val = self.queue.get()
                speed = val[0]
                pitchBin = val[1]

                playOneSecOfMusic(midiout, speed, pitchBin)


def main():
    print("looking for an EEG stream...")
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])
    q = queue.Queue()

    # Music MIDI Output Thread
    thread = MyThread(q, args=())
    thread.start()

    # Muse Processing Thread
    while True:
        q.put(processMuse(inlet))


def processMuse(inlet):
    wave = []

    for i in range(0, samples_per_sec):
        sample, timestamp = inlet.pull_sample()
        time.sleep(1/samples_per_sec)
        wave.append(np.average(sample))

    fftData = np.fft.fft(wave)
    freq = np.fft.fftfreq(len(wave))*samples_per_sec

    # Format FFT
    freq = freq[0:int(len(freq)/2)]
    fftData = fftData[0:int(len(fftData)/2)]
    freq = freq[1:50]
    fftData = fftData[1:50]

    bandTotals = [0, 0, 0, 0, 0]
    bandCounts = [0, 0, 0, 0, 0]

    for point in range(len(freq)):
        if (freq[point] < 4):
            bandTotals[0] += fftData[point]
            bandCounts[0] += 1
        elif (freq[point] < 8):
            bandTotals[1] += fftData[point]
            bandCounts[1] += 1
        elif (freq[point] < 12):
            bandTotals[2] += fftData[point]
            bandCounts[2] += 1
        elif (freq[point] < 30):
            bandTotals[3] += fftData[point]
            bandCounts[3] += 1
        elif (freq[point] < 100):
            bandTotals[4] += fftData[point]
            bandCounts[4] += 1

    # Save the average of all points
    bins = list(np.array(bandTotals)/np.array(bandCounts))
    strongestBin = np.argmax(bins)

    return [4, strongestBin]


def playOneSecOfMusic(midiout, speed, pitchBin):
    velocity = 100  # maybe adjust with brainwaves?
    delay = 1/speed

    for i in range(0, speed):
        pitch = np.random.randint(
            pitchBins[pitchBin][0], pitchBins[pitchBin][1])

        print("pitch=", pitch)

        midiout.send_message(getNote(pitch, velocity))
        time.sleep(0.9*delay)
        midiout.send_message(stopNote(pitch))
        time.sleep(0.1*delay)


def getNote(key, velocity):
    return [0x90, key, velocity]


def stopNote(key):
    return [0x80, key, 0]


if __name__ == '__main__':
    main()
