#!/usr/bin/env python3

import struct
import wave

import math
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import time
import threading


TITLE = ''
WIDTH = 1280
HEIGHT = 720
FPS = 25.0
RERFESH_TIME = 1.0 / FPS
NUM_LINES = 3

nFFT = 2048
CHANNELS = 1
BUF_SIZE = 2 * CHANNELS * nFFT
FORMAT = pyaudio.paInt16
RATE = 48000
FFT_HIST_LENGTH = 2.0


class ProcessThread(threading.Thread):
    def __init__(self, audio):
        threading.Thread.__init__(self)
        self.audio = audio

    def run(self):
        while True:
            start_time = time.time()
            self.audio.process()
            self.audio.getBinsIntensity(3)
            now = time.time()
            time_to_wait = min(RERFESH_TIME, now - start_time + 1.0 / FPS)
#            print("time_to_wait: %s" % str(time_to_wait))
            time.sleep(time_to_wait)

class AudioInput():

    def __init__(self):
        self.FFT = np.zeros(nFFT)
        self.avgFFT = np.zeros(nFFT)
        self.diffFFT = np.zeros(nFFT)
        self.histFFT = list()
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=BUF_SIZE)

        self.MAX_y = 2.0 ** (self.p.get_sample_size(FORMAT) * (8 - 2))
        self.thread = ProcessThread(self)
        self.thread.start()


    def addHistoricalFFT(self, fft):
        now = time.time()
        filtered = [ x for x in self.histFFT if now - x[1] < FFT_HIST_LENGTH]
        filtered.append((fft, now));
        self.histFFT = filtered

    def getAvgFFT(self):
        nbrFFT = len(self.histFFT)
        summed = np.zeros(nFFT)
        for (fft, _) in self.histFFT:
            summed = [x + y for x, y in zip(summed, fft)]
        avg = [x / nbrFFT for x in summed]
        return avg

    def diffMax(self, curr, hist):
        diff = curr / hist
#        print("diffMax %f / %f = %f" % (curr, hist, diff))
        if diff < 0:
            diff = 0
        return diff

    def getDiffFFT(self, FFT, avgFFT):
        diffFFT = [self.diffMax(curr, hist) for curr, hist in zip(FFT, avgFFT)]
#        print("FFT: \n%s\n" % str(FFT))
#        print("avgFFT: \n%s\n" % str(avgFFT))
#        print("diffFFT: \n%s\n" % str(diffFFT))
        return diffFFT

    def fftMainHz(self, fft):
        freqs = np.fft.fftfreq(len(fft), 1/(RATE/2.0))
        idx = np.argmax(fft)
        mainHz = freqs[idx]
        return mainHz
        
    def process(self):
        N = int(max(self.stream.get_read_available() / nFFT, 1) * nFFT)
        data = self.stream.read(N)

#        try:
#            N = max(self.stream.get_read_available() / nFFT, 1) * nFFT
#            data = self.stream.read(N)
#        except:
#            return
        # Unpack data, LRLRLR...
        y = np.array(struct.unpack("%dh" % (N * CHANNELS), data)) / self.MAX_y
        Y_fft = np.fft.fft(y, 2*nFFT)
        
        self.FFT = abs(Y_fft[:nFFT])
        self.addHistoricalFFT(self.FFT)

        self.avgFFT = self.getAvgFFT()
        self.diffFFT = self.getDiffFFT(self.FFT, self.avgFFT)

    def animate(self, i, lines, x_f):
        print("histDepth: %-3d  Main freq: %-4d  HistAvg freq: %-4d" % (
          len(self.histFFT), self.fftMainHz(self.FFT), self.fftMainHz(self.avgFFT)
        ))
#        print("FFT: \n%s" % str(self.FFT))
#        print("avgFFT: \n%s" % str(self.avgFFT))
#        print("diffFFT: \n%s" % str(self.diffFFT))
        lines[0].set_data(x_f, self.FFT)
        lines[1].set_data(x_f, self.avgFFT)
        lines[2].set_data(x_f, self.diffFFT)
        return lines


    def windowInit(self, lines, x_f):
        for line in lines:
          line.set_data(x_f, np.zeros(nFFT))
        return lines

    def main(self):
        dpi = plt.rcParams['figure.dpi']
        plt.rcParams['savefig.dpi'] = dpi
        plt.rcParams["figure.figsize"] = (1.0 * WIDTH / dpi, 1.0 * HEIGHT / dpi)
        fig = plt.figure()

        # Frequency range
        x_f = 1.0 * np.arange(0, nFFT) * RATE / (nFFT * 2)
        ax = fig.add_subplot(111, title=TITLE, xlim=(x_f[0], x_f[-1]),
                           ylim=(0, 2 * np.pi * nFFT ** 2 / RATE))
        ax.set_yscale('symlog', linthreshy=nFFT ** 0.5)

        lines = [plt.plot([],[])[0] for j in range(NUM_LINES)]

        # Change x tick labels for left channel
        def change_xlabel(evt):
            labels = [label.get_text().replace(u'\u2212', '')
                    for label in ax.get_xticklabels()]
            ax.set_xticklabels(labels)
            fig.canvas.mpl_disconnect(drawid)
        drawid = fig.canvas.mpl_connect('draw_event', change_xlabel)

        frames = None

        ani = animation.FuncAnimation(
            fig, self.animate, frames,
            init_func=lambda: self.windowInit(lines, x_f), fargs=(lines, x_f),
            interval=1000.0 / FPS, blit=True
        )

        plt.show()

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def getFFRBinPartition(self, nBulbs):
        nyquistHz = RATE / 2.0
        pct = 1.0 / nBulbs
        divs=[x*pct for x in range(nBulbs)]

        divsexp = [1/(pct**(x/(nBulbs**(1/(nBulbs**0.05))))) for x in range(nBulbs)]
#        print("divsexp = %s" % str(divsexp))

        divssum = np.sum(divsexp)
#        print("divssum = %s" % str(divssum))

        divspart = [x/divssum for x in divsexp]
#        print("divspart = %s" % str(divspart))

        divslen = [x*nyquistHz for x in divspart]
#        print("divslen = %s" % str(divslen))

        # Prevent the first bins from being too small
        MIN_HZ_BIN_SIZE = 50.0
        totAdded = 0
        for idx in range(nBulbs):
            if divslen[idx] < MIN_HZ_BIN_SIZE:
                divslen[idx] = MIN_HZ_BIN_SIZE
                totAdded += MIN_HZ_BIN_SIZE
        divslen[-1] -= totAdded
#        print("divslen fixed = %s" % str(divslen))

        startFreq = 0
        startBin = np.zeros(nBulbs)
        for idx in range(nBulbs):
            startBin[idx] = int(nFFT * startFreq / nyquistHz)
            startFreq += divslen[idx]
#        print("startBin = %s" % str(startBin))

        endBin = np.zeros(nBulbs)
        for idx in range(nBulbs):
            if (idx < len(startBin) -1):
                endBin[idx] = startBin[idx+1] - 1
            else: 
                endBin[idx] = nFFT - 1
#        print("endBin = %s" % str(endBin))
        
        bins = [(int(x), int(y)) for x, y in zip(startBin, endBin)]
#        print("bins = %s" % str(bins))

        return bins
        
    def getFFTBins(self, nBulbs):
        if nBulbs == 0:
            return []
        partitions = self.getFFRBinPartition(nBulbs)
        fftBins = [self.diffFFT[x[0]:x[1]+1] for x in partitions]
#        print("fftBins = %s" % str(fftBins))
        return fftBins

    def getBinIntensity(self, fftBin):
#        print("getBinIntensity() %s" % str(fftBin))
        sums = 0
        maxs = 0
        for f in fftBin:
            sums += f
            if maxs < f:
                maxs = f
        avg = sums / len(fftBin)
        return maxs

    def getBinsIntensity(self, nBulbs):
        if nBulbs == 0:
            return []
        bins = self.getFFTBins(nBulbs)
#        print("bins: %s" % str(bins))
        intensityBins = [self.getBinIntensity(fftBin) for fftBin in self.getFFTBins(nBulbs)]
#        print("bins intensity = %s" % str(intensityBins))
        return intensityBins

    def getDominantFreq(self):
        return self.fftMainHz(self.FFT)


if __name__ == '__main__':
    input = AudioInput()
    input.main()
