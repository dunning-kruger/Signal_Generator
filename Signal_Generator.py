# Signal Generator
#   Create and output a user-selected signal
#   The output device is the default speaker of your computer

import matplotlib.pyplot as plt
import numpy as np
import scipy as sci
import sounddevice as sd
import soundfile as sf
import sys
import time
from datetime import datetime
from tkinter import filedialog

# system inputs (only things in this list need be customized)
fs               = 48000      # sample rate (set according to audo card capability) [Hz]
freq             = 2000       # frequency [Hz]
freqStart        = 1000       # inital frequency [Hz]
freqEnd          = 2000       # final frequency [Hz]
pulseRate        = 1          # delay between pulses [sec]
reps             = 2          # number of pulses [count]
pw               = 1.0        # pulse width [sec]
nPCW             = 5          # number of pulses in each train [count]
lowcut           = 500        # filter low cutoff frequency [Hz]
highcut          = 20000      # filter high cutoff frequency [Hz]
filterFlag       = 'bandpass' # select lowpass, highpass, or bandpass filtering
modulation_index = 0.5        # modulation index (controls the depth of modulation)
fc               = 150        # modulation carrier frequency [Hz]
modType          = 'FM'       # select Amplitude Modulation (AM) or Frequency Modulation (FM)
logScaleFlag     = 'log'      # select log or linear scaling
chirpDirection   = 'up'       # select chirp direction (up or down)
recordFlag       = 'off'      # enable or disable write the signal to .WAV file
preambleFlag     = 'off'      # enable or disable preamble CW signal
preambleFreq     = 1600       # preamble frequency [Hz]
randGain         = .4         # scaling factor for the random noise
freqGain1        =  1         # scaling factor for the first tone
freqGain2        = .8         # scaling factor for the second tone
freqGain3        = .6         # scaling factor for the third tone
freqTone1        = 1000       # frequency [Hz] of the first tone
freqTone2        = 1500       # frequency [Hz] of the second tone
freqTone3        = 2000       # frequency [Hz] of the third tone

# create the time vector
t = np.linspace(0, pw, int(fs * pw), endpoint=False) # samples [count]

# receive user input
signalSelect = input("1. Pulsed Continuous Wave\n"
                     "2. Stepped Continuous Wave\n"
                     "3. Chirp\n"
                     "4. Chirp with broadband noise\n"
                     "5. Broadband Noise\n"
                     "6. Broadband Noise with Tones\n"
                     "7. Modulated signal\n"
                     "8. Record mic input and output it\n"
                     "9. Play signal from file\n"
                     "Enter the number of your desired signal: ")

# function save the audio data to a .wav file
def saveSignalToFile(signal,signalType):
    # get the current date and time
    current_datetime = datetime.now()

    # format the time as YYYY-mm-dd_HHMMSS
    current_time = current_datetime.strftime("%Y-%m-%d_%H%M%S")
    
    # save the audio data 
    output_filename = current_time + "_" + signalType + ".wav"
    sci.io.wavfile.write(output_filename, fs, signal)

def processSignal(signal):
    window = sci.signal.windows.tukey(len(signal), .1) # Tukey windowing
    signal = window * signal                           # refactor with Tukey windowing
    signal = signal / max(signal)                      # normalize signal  

def transmit(signal,signalType):
    for i in range(reps):        
        # save the audio data to a .wav file
        if recordFlag == 'on':
            saveSignalToFile(signal,signalType)     

        if signalType == "preamble_signal":
            print(f'Transmitting preamble pulse at {preambleFreq:.2f} Hz')
        elif signalType == "pulsed_cw_signal":
            print(f'Transmitting pulse {1 + i:d} of {reps:d} at {freq:.2f} Hz')
        elif signalType == "stepped_cw_signal":
            print(f'Transmitting pulse {1 + i:d} of {len(freq):d} at {freq[i]:.2f} Hz')
        elif signalType == "chirp_signal":
            print(f'Transmitting chirp {1 + i:d} of {reps:d}')
        elif signalType == "chirp_with_broadband_noise_signal":
            print(f'Transmitting chirp {1 + i:d} of {reps:d}')
        elif signalType == "broadband_noise_signal":
            print(f'Transmitting pulse {1 + i:d} of {reps:d}')
        elif signalType == "broadband_noise_with_tones_signal":
            print(f'Transmitting pulse {1 + i:d} of {reps:d}')
        elif signalType == "modulated_signal":
            print(f'Transmitting pulse {1 + i:d} of {reps:d}')
        elif signalType == "microphone_signal":
            print(f'Transmitting recorded signal {1 + i:d} of {reps:d}')
        elif signalType == "imported_signal":
            print(f'Transmitting imported signal {1 + i:d} of {reps:d}')
        else:
            sys.exit('Signal selection not valid.')

        # print(f'Transmitting pulse {1 + i:d} of {reps:d} at {freq:.2f} Hz')
        sd.play(signal,fs)    # play the signal
        sd.wait()             # wait while the signal plays
        sd.stop()             # stop the signal
        time.sleep(pulseRate) # wait before transmitting the next signal

# preamble signal
if preambleFlag == 'on':
    # set up signal
    signal = np.sin(2*np.pi*preambleFreq*t) # sine wave of specified signal
    
    # process signal
    processSignal(signal)
    
    # output signal
    signalType = "preamble_signal"
    transmit(signal,signalType)

# Pulsed Continuous Wave (PCW)
if signalSelect == '1':
    # set up signal
    signal = np.sin(2 * np.pi * freq * t)  # sine wave of specified signal
    
    # process signal
    processSignal(signal)
    
    # output signal
    signalType = "pulsed_cw_signal"
    transmit(signal,signalType)

# Stepped Continuous Wave (stepped CW)
elif signalSelect == '2':
    # apply log or linear scaling
    if logScaleFlag == 'log': # use log scale
        freqStart = np.log(freqStart) / np.log(10)      # convert initial frequency to log
        freqEnd   = np.log(freqEnd)   / np.log(10)      # convert final frequency to log
        freq      = np.logspace(freqStart,freqEnd,nPCW) # logarithmic frequency vector [Hz]
    else: # use linear scale
        freq      = np.linspace(freqStart,freqEnd,nPCW) # linear frequency vector [Hz]
    
    # account for number of reps
    freq = np.repeat(freq,reps)

    # set up the pulse train
    for i in range(len(freq)):
        signal = np.sin(2 * np.pi * freq[i] * t) # sine wave of specified signal
        
        # process signal
        processSignal(signal)

        # save the audio data to a .wav file
        if recordFlag == 'on':
            signalType = "stepped_cw_signal"
            saveSignalToFile(signal,signalType)

        # output signal
        print(f'Transmitting pulse {1 + i:d} of {len(freq):d} at {freq[i]:.2f} Hz')
        sd.play(signal,fs)    # play the signal
        sd.wait()             # wait while the signal plays
        sd.stop()             # stop the signal
        time.sleep(pulseRate) # wait before transmitting the next signal

# Chirp
elif signalSelect == '3':
    # apply chirp direction
    if chirpDirection == 'down': # use log scale
        temp      = freqStart    # temporary variable to store value
        freqStart = freqEnd      # inital frequency [Hz]
        freqEnd   = temp         # final frequency [Hz]
    
    # apply log or linear scaling
    if logScaleFlag == 'log': # use log scale
        signal = sci.signal.chirp(t,freqStart,t[-1],freqEnd,'logarithmic',phi=-90) # swept-frequency cosine
    else: # use linear scale
        signal = sci.signal.chirp(t,freqStart,t[-1],freqEnd,'linear',phi=-90) # swept-frequency cosine

    # process signal
    processSignal(signal)

    # output signal
    signalType = "chirp_signal"
    transmit(signal,signalType)

# Chirp with broadband noise
elif signalSelect == '4':
    # apply chirp direction
    if chirpDirection == 'down': # use log scale
        temp      = freqStart    # temporary variable to store value
        freqStart = freqEnd      # inital frequency [Hz]
        freqEnd   = temp         # final frequency [Hz]
    
    # apply log or linear scaling
    if logScaleFlag == 'log': # use log scale
        signal = sci.signal.chirp(t,freqStart,t[-1],freqEnd,'logarithmic',phi=-90) # swept-frequency cosine
    else: # use linear scale
        signal = sci.signal.chirp(t,freqStart,t[-1],freqEnd,'linear',phi=-90) # swept-frequency cosine
    
    # random noise signal
    randSignal = np.random.randn(len(t))           # normally distributed random noise
    randSignal = randSignal / max(abs(randSignal)) # normalize signal
    randSignal = randGain * randSignal             # scaled signal
    signal     = randSignal + signal               # composite signal

    # process signal
    processSignal(signal)

    # output signal
    signalType = "chirp_with_broadband_noise_signal"
    transmit(signal,signalType)

# Broadband Noise
elif signalSelect == '5':
    # set the order for the Butterworth filter
    order = 4  # Filter order
    
    # normalize by Nyquist frequency (half of sample rate)
    nyquist      = 0.5 * fs
    lowcut_norm  = lowcut / nyquist
    highcut_norm = highcut / nyquist

    # set up signal
    signal = np.random.randn(len(t)) # normally distributed random noise
    
    # apply lowpass, highpass, or bandpass filtering
    if filterFlag == 'lowpass':
        b, a = sci.signal.butter(order, highcut_norm, btype='low')
        signal = sci.signal.filtfilt(b, a, signal)
    elif filterFlag == 'highpass':
        b, a = sci.signal.butter(order, lowcut_norm, btype='high')
        signal = sci.signal.filtfilt(b, a, signal)
    elif filterFlag == 'bandpass':
        b, a = sci.signal.butter(order, [lowcut_norm, highcut_norm], btype='band')
        signal = sci.signal.filtfilt(b, a, signal)
    
    # process signal
    processSignal(signal)
    
    # output signal
    signalType = "broadband_noise_signal"
    transmit(signal,signalType)

# Broadband Noise with Tones
elif signalSelect == '6':
    # random noise signal
    randSignal = np.random.randn(len(t))           # normally distributed random noise
    randSignal = randSignal / max(abs(randSignal)) # normalize signal
    randSignal = randGain * randSignal             # scaled signal

    # CW signals
    cw1    = freqGain1 * np.sin(2 * np.pi * freqTone1 * t) # sine wave of specified signal
    cw2    = freqGain2 * np.sin(2 * np.pi * freqTone2 * t) # sine wave of specified signal
    cw3    = freqGain3 * np.sin(2 * np.pi * freqTone3 * t) # sine wave of specified signal
    signal = randSignal + cw1 + cw2 + cw3                  # composite signal

    # process signal
    processSignal(signal)
    
    # output signal
    signalType = "broadband_noise_with_tones_signal"
    transmit(signal,signalType)

# Modulated Signal
elif signalSelect == '7':
    # apply chirp direction
    if chirpDirection == 'down': # use log scale
        temp      = freqStart    # temporary variable to store value
        freqStart = freqEnd      # inital frequency [Hz]
        freqEnd   = temp         # final frequency [Hz]

    # apply amplitude or frequency modulation
    if modType == 'AM': # use amplitude modulation
        signalAmp = np.sin(2 * np.pi * fc * t)               # sine wave for amplitude modulation
        signal    = np.sin(2 * np.pi * freq * t) * signalAmp # sine wave of specified signal
    elif modType == 'FM': # use frequency modulation
        freq   = np.linspace(freqStart,freqEnd,len(t))
        signal = np.sin(2 * np.pi * freq * t)
    
    # process signal
    processSignal(signal)

    # output signal
    signalType = "modulated_signal"
    transmit(signal,signalType)

# record microphone input and output it
elif signalSelect == '8':
    # record one channel of data using the computer speakers
    print("Recording audio...")
    recSignal = sd.rec(int(fs * pw), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    print("Recording complete.")

    # normalize the audio data
    recSignal = recSignal / np.max(np.abs(recSignal))

    # create the carrier signal
    carrierSignal = np.sin(2 * np.pi * fc * t)  # Sine wave carrier

    # apply amplitude modulation (AM)
    signal = (1 + modulation_index * recSignal.flatten()) * carrierSignal

    # process signal
    processSignal(signal)

    # output signal
    signalType = "microphone_signal"
    transmit(signal,signalType)

# play signal from file
elif signalSelect == '9':
    # use try/except to handle errors from file selection
    try:
        # open file selection dialog box
        file_path = filedialog.askopenfilename()

        # import signal file
        signal, fs = sf.read(file_path)

        # output signal
        signalType = "imported_signal"
        transmit(signal,signalType)
    except:
        sys.exit('Unsupported file selected, or no file selected.')

# abort execution of the script if signal selection is invalid 
else:
    sys.exit('Signal selection not valid.')

# plot frequency domain data
plt.subplot(121)
f, Pxx = sci.signal.welch(signal, fs, nperseg=1024)
Pxx = np.maximum(Pxx, 1e-10)  # Prevent zero values
plt.plot(f, 20 * np.log10(Pxx))
plt.title('Power Spectral Density')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [re dB/Hz]')
plt.grid()

# plot time series data
plt.subplot(122)
plt.plot(t,signal)
plt.title('Time Series Data')
plt.xlabel('Time [sec]')
plt.ylabel('Amplitude')
plt.grid()
plt.show()
