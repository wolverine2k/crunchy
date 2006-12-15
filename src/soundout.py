"""soundout.py:
system-agnostic wave sound output
"""

import wave
import math
from cStringIO import StringIO
import struct
from threading import Thread, Condition
import errorhandler

from translation import _

try:
    #oss, legacy unix sound system no external dependencies
    import ossaudiodev as oss
    mode = 'oss'
    successful_import = True
except:
    try:
        #windows
        import winsound
        mode = 'win'
        successful_import = True
    except:
        mode = None
        successful_import = False

notemap = {'_':0.0, 'A':220, 'A#':233.1, 'Bb':233.1, 'B':246.9, 'c':261.6, 'c#':277.2, 
            'db':277.2, 'd':293.7, 'd#':311.1, 'eb':311.1, 'e':329.6, 'f':349.2, 
            'f#':370.0, 'gb':370.0, 'g':392.0, 'g#':415.3, 'ab':415.3, 'a':440.0, 
            'a#':466.2, 'bb':466.2, 'b':493.9, 'c1':523.2, 'c1#':554.4, 
            'd1b':554.4, 'd1':587.4, 'd1#':622.2, 'e1b':622.2, 'e1':659.2, 'f1':698.4, 
            'f1#':740.0, 'g1b':740.0, 'g1':784.0, 'g1#':830.6, 'a1b':830.6, 'a1':880, 
            'a1#':932.4, 'b1b':932.4, 'b1':987.8}

class SoundSynth(object):
    """Synthesizes waveforms and plays them"""
    def __init__(self, approximate=False):
        self.approximate = approximate
        if approximate == True:
            if mode == 'win':
                self.approximate = True
                self.notes = []
            else:
                print _("'approximate' settings will be ignored.")
                print _("It is only available under Windows.")
        if mode == 'oss':
            self.dev = oss.open('w')
            self.bits = self.dev.setfmt(oss.AFMT_S16_LE)
            self.channels = self.dev.channels(1)
            self.speed = self.dev.speed(44100)
            self.framesize = self.channels * self.bits
            self.buffer = StringIO()
        elif mode == 'win':
            self.bits = 16
            self.channels = 1
            self.speed = 44100
            self.framesize = self.channels * self.bits
            self.buffer = StringIO()
        else:
            raise NotImplementedError

    def play(self):
        if mode == 'oss':
            self.dev.write(self.buffer.getvalue())
        elif mode == 'win':
            self.thread = WinPlayer(self)
            self.thread.start()

    def addtone(self, pitch, duration):
        """add a note to the playlist, duration is a float in seconds, pitch is in Herz"""
        if mode == 'win' and self.approximate == True:
            # this uses the system beep for near instantenous processing;
            # it does not use external speakers.
            # Notes are rounded to the nearest Hertz value.
            self.notes.append((int(pitch+0.5), duration))
            return
        nsamples = int (self.speed * duration)
        # problem with bad noise for sounds multiple of 233.1 Hz
        temp = int(pitch*10)
        if temp%2331 == 0:
            pitch -= 0.2   # out of tune ... but cures the noise
        temp = 2.0 * math.pi * pitch / self.speed
        for s in xrange(nsamples):
            sample = math.sin(temp * s)
            self.appendsample((sample, ))

    def addharmonics(self, pitch, duration, rel_amp):
        """add a complex note to the playlist, duration is a float in seconds, 
        pitch is in Herz, rel_amp represent the relative amplitudes of a finite
        number of harmonics.  For example, the sawtooth wave would have 
        rel_amp = (1, 1/2, 1/3, 1/4, 1/5, ...)."""
                
        nsamples = int (self.speed * duration)
        # We ignore the problem with bad noise for sounds multiple of 233.1 Hz
        # as it would show up only if one harmonics is requested...
        temp = 2.0 * math.pi * pitch / self.speed
        
        norm = 0
        for a in rel_amp:
            norm += abs(a)
        amplitudes = []
        for a in rel_amp:
            amplitudes.append(a/norm)
        
        for s in xrange(nsamples):
            sample = 0
            for i, a in enumerate(amplitudes):
                sample += a*math.sin((i+1)*temp * s)
            self.appendsample((sample, ))

    def add_tones(self, pitches, duration):
        """Adds sounds of different frequencies and same (default) amplitude;
           The main intention is to demonstrate beats."""
                
        nsamples = int (self.speed * duration)
        temps = []
        
        # problem with bad noise for sounds multiple of 233.1 Hz, with all
        # tones have the same frequency.
        frequency_problem = True
        reference_freq = pitches[0]
        for pitch in pitches:
            if pitch != reference_freq:
                frequency_problem = False
            temp = int(pitch*10)
            if temp%2331 != 0:
                frequency_problem = False
            temps.append( 2.0 * math.pi * pitch / self.speed)
        if frequency_problem:
            print _("WARNING: sounds multiple of 233.1 Hz may be 'noisy' on your computer.")

        n_sounds = len(pitches)
        for s in xrange(nsamples):
            sample = 0
            for temp in temps:
                sample += math.sin(temp * s)/n_sounds
            self.appendsample((sample, ))

    def appendsample(self, sample):
        """append a sample to the buffer,
        sample is a tuple of floats in the range (-1, 1) (not inclusive), 
        one element for each channel"""
        if self.channels == 1:
            if self.bits == 8:
                value = int ((sample[0] + 1) * 64)
                data = struct.pack('<B', value)
            elif self.bits == 16:
                value = int (sample[0] * (2**15))
                data = struct.pack('<h', value)
            elif self.bits == 32:
                value = int (sample[0] * (2**31))
                data = struct.pack('<h', value)
            else:
                raise ValueError
        else:
            raise NotImplementedError
        self.buffer.write(data)
    
    def reset(self):
        """clear the buffer by replacing it"""
        self.buffer = StringIO()
        self.notes = []

class Song(object):
    """Convert a musical (string) representation of a song to 'physical' (frequency/duration) representation
    Each note is a colon seperated pair of note and time. 
    Notes are represented by their musical names (as used in the UK anyway),
    timings are floats representing multiples of crotchets, so 'c:1' is a crotchet c below concert a.
    Songs are represented as space separated lists of notes.
    """
    def __init__(self, notes=None):
        self.out=[]
        self.bpm = 100
        if notes is not None:
            self.append_notes(notes)

    def append_notes(self, data):
        notelist = data.split(' ')
        for n in notelist:
            parts = n.split(':')
            freq = notemap[parts[0]]
            time = float(parts[1]) * (60.0/self.bpm)
            self.out.append((freq, time))

    def play(self, approximate=False):
        """Plays the song with a SoundSynth object"""
        ss = SoundSynth(approximate)
        for t in self.out:
            ss.addtone(t[0], t[1])
        ss.play()

class WinPlayer(Thread):
    def __init__(self, synth):
        Thread.__init__(self)
        self.synth = synth
        self.sleeplock = Condition()
    def run(self):
        if self.synth.approximate == True:
            for freq, duration in self.synth.notes:
                if freq >= 37 and freq <= 32767:
                    winsound.Beep(freq, int(duration*1000))
                else:
                    self.sleeplock.acquire()
                    self.sleeplock.wait(self.synth.notes[0][1])
                    self.sleeplock.release()
        else:
            tbuf = StringIO()
            writer = wave.open(tbuf, 'w')
            writer.setnchannels(self.synth.channels)
            writer.setsampwidth(self.synth.bits/8)
            writer.setframerate(self.synth.speed)
            writer.writeframes(self.synth.buffer.getvalue())
            winsound.PlaySound(tbuf.getvalue(), winsound.SND_MEMORY)

def play_song(songdata, approximate=False):
    """play a song, in the string format described above"""
    s = Song(songdata)
    s.play(approximate)

def play_harmonics(freq, duration, rel_amp):
    '''plays a series of harmonics with relative_amplitudes = (b1, b2, b3, ...)'''
    ss = SoundSynth()
    ss.addharmonics(freq, duration, rel_amp)
    ss.play()

def play_tone(freq, duration):
    '''Plays a single tone.'''
    ss = SoundSynth()
    ss.addtone(freq, duration)
    ss.play()

def play_tones(freqs, duration):
    '''Plays many sounds simultaneously; to demonstrate beat, chose two
       frequencies that are relatively close.'''
    ss = SoundSynth()
    ss.add_tones(freqs, duration)
    ss.play()
    
yesterday = 'g:0.5 f:0.5 f:3 _:1 a:0.5 b:0.5 c1#:0.5 d1:0.5 e1:0.5 f1:0.5 e1:0.75 d1:0.25 d1:3 _:1.0 d1:0.5 d1:0.5 c1:0.5 bb:0.5 a:0.5 g:0.5 bb:1.0 a:0.5 a:1.5 g:1.0 f:1.0 a:0.5 g:1.5 d:1.0 f:1.0 a:0.5 a:2.5'

ode_to_joy = 'd1:2 e1b:1 f1:1 e1b:1 d1:1 c1:1 bb:2 c1:1 d1:1 d1:1.5 c1:0.5 c1:2 d1:2 e1b:1 f1:1 f1:1 e1b:1 d1:1 c1:1 bb:2 c1:1 d1:1 c1:1.5 bb:0.5 bb:2'

chromatic = 'A:1 Bb:1 B:1 c:1 c#:1 d:1 eb:1 e:1 f:1 f#:1 g:1 ab:1 a:1 bb:1 b:1 c1:1 c1#:1 d1:1 e1b:1 e1:1 f1:1 f1#:1 g1:1 a1b:1 a1:1 b1b:1 b1:1'


__yes = {'play_tone': play_tone,
         'play_tones': play_tones,
         'play_harmonics': play_harmonics,
         'play_song': play_song,
         'yesterday': yesterday,
         'ode_to_joy': ode_to_joy,
         'chromatic': chromatic}
        
def no_sound(*args, **kwds):
    msg = _("Sound is not supported on this platform.") + \
           _("You need one of the following 2 choices:") + \
           _(" use MS Windows with winsound installed;") +\
           _(" use a UNIX system that supports OSS (ossaudiodev).") 
    raise errorhandler.NoSoundError(msg)

__no = {}
for key in __yes:
    __no[key] = no_sound

if successful_import:
    all_sounds = __yes
else:
    all_sounds = __no

if __name__ == '__main__':
    if not successful_import:
        print "Sorry, can't import the sound module!"
    else:
        x = SoundSynth()
        s = Song()
        s.append_notes(ode_to_joy)
        s.play()
        # Next, testing system beep faster processing on Windows.
        # Actually, both will be played simultaneously!
        s2 = Song(ode_to_joy)
        s2.play(True)
        play_beat(440, 441, 3)
        play_harmonics(440, 3, (1, 0, 1./3, 0, 1./5, 0, 1./7))
        play_harmonics(440, 3, (1, 1./2, 1./3, 1./4, 1./5, 1./6, 1./7))
