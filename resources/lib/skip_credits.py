# -*- coding: utf-8 -*-

'''
    Skip Credits Add-on

    Copyright roguetech.

    It is distributed WITHOUT ANY WARRANTY or any implied warranty of
    MERCHANTABILITY.
'''

# Need file services to read time stamp files
import xbmcvfs
import xbmc
import xbmcaddon
# Need os services to manipulate the file folder names
import os
#import xbmcgui
# Obviously need time services
import time
# Need regular expression
import re

_logging = xbmcaddon.Addon().getSetting('logging')
_static_name = xbmcaddon.Addon().getSetting('static_name')
_match_videoname = xbmcaddon.Addon().getSetting('match_videoname')
_poll_time = float(0.3)

def run():
    global player
    global kodi_monitor

    # Set up our Kodi Monitor & Player...
    kodi_monitor = MyMonitor()
    player = MyPlayer()

    # Run until abort requested
    while not kodi_monitor.abortRequested():
        if kodi_monitor.waitForAbort(1):
            # Abort was requested while waiting. We should exit
            break

def load_settings():
    global _logging
    global _static_name
    global _match_videoname

    _old_logging = _logging
    _old_static_name = _static_name
    _old_match_videoname = _match_videoname

    _logging = xbmcaddon.Addon().getSetting('logging')
    if _old_logging != _logging: log('Set logging to ' + str(_logging) + ' from ' + str(_old_logging))
    _static_name = xbmcaddon.Addon().getSetting('static_name')
    if _old_static_name != _static_name: log('Set logging to ' + str(_static_name) + ' from ' + str(_old_static_name))
    _match_videoname = xbmcaddon.Addon().getSetting('match_videoname')
    if _old_match_videoname != _match_videoname: log('Set logging to ' + str(_match_videoname) + ' from ' + str(_old_match_videoname))

def log(_msg):
    #if logging == True:
        xbmc.log(u'{0}: {1}'.format('scripts.skipcredits', _msg), level=xbmc.LOGFATAL)

class MyPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        _addonName = 'Skip Credits'

    def get_poll_time(self):
        global _poll_time
        _old_poll_time = _poll_time
        _poll_time = int(xbmcaddon.Addon().getSetting('poll_time'))
        if _poll_time == 0: _return_value = float(0.05)
        if _poll_time == 1: _return_value = float(0.1)
        if _poll_time == 2: _return_value = float(0.2)
        if _poll_time == 3: _return_value = float(0.3)
        if _poll_time == 4: _return_value = float(0.5)
        if _poll_time == 5: _return_value = float(0.75)
        if _poll_time == 6: _return_value = float(1)
        if _poll_time == 7: _return_value = float(2)
        if _poll_time == 8: _return_value = float(5)
        if _old_poll_time != _poll_time: log('Changed polling rate to ' + str(_return_value) + ' seconds from ' + str(_old_poll_time) + ' seconds')
        return _return_value

    def extract_season(self, _text):
        _text = _text.lower()
        # Use a regular expression to extract the season and episode numbers
        _match = re.search(r'(s|season)(\d+)', _text, re.I)
        if _match:
            return int(_match.group(2))
        else:
            return None

    def extract_episode(self, _text):
        _text = _text.lower()
        # Use a regular expression to extract the season and episode numbers
        _match = re.search(r'(e|episode|ep)(\d+)', _text, re.I)
        if _match:
            return int(_match.group(2))
        else:
            return None

    #text1 is for video name
    #text2 may either be timestamp file name, or contents of it
    def match_season(self, _text1, _text2):
        _text1_season = self.extract_season(_text1)

        #If no video season, return true
        if not _text1_season: return True

        _pattern = r'(s|season)(\d+)'
        _matches = re.findall(_pattern, _text2, re.I)
        if not _matches: return _text2

        _line_seasons = [int(_match[1]) for _match in _matches]
        if _text1_season in _line_seasons: return _text2

    #text1 is for video name
    #text2 may either be timestamp file name, or contents of it
    def match_episode(self, _text1, _text2):
        _text1_episode = self.extract_episode(_text1)

        #If no video season, return true
        if not _text1_episode: return True

        _pattern = r'(e|episode)(\d+)'
        _matches = re.findall(_pattern, _text2, re.I)
        if not _matches: return _text2

        _line_episodes = [int(_match[1]) for _match in _matches]
        if _text1_episode in _line_episodes: return _text2

    def check_season_episode_match(self, _playing_file_name, _text):
        if self.match_season(_playing_file_name,_text) and self.match_episode(_playing_file_name,_text):
            return True

    # Performs xbmc.getPlayingFile()
    # Returns null if video not playing
    def get_video_folder(self):
        from contextlib import closing
        _foldername = None
        try:
            _foldername = xbmc.getInfoLabel('Player.FilenameAndPath')
            _foldername = os.path.dirname(_foldername)
        except RuntimeError:
            pass
        return _foldername
    
    
    # Performs xbmc.getPlayingFile()
    # Returns null if video not playing
    def get_playing_video_name(self):
        from contextlib import closing
        _playing_file_name = None
        try:
            _playing_file_name = xbmc.Player().getPlayingFile()
        except RuntimeError:
            pass
        return _playing_file_name
    
    # Performs xbmc.getTime()
    # Returns null if video not playing
    def get_run_time(self):
        from contextlib import closing
        _run_time = float(0)
        try:
            _run_time = float(xbmc.Player().getTime())
        except RuntimeError:
            pass
        return _run_time
    
    # Performs xbmc.getTime()
    # Returns null if video not playing
    def get_video_length(self):
        from contextlib import closing
        _video_length = float(0)
        try:
            _video_length = float(xbmc.Player().getTotalTime())
        except RuntimeError:
            pass
        return _video_length


    # Performs xbmc.seekTime()
    # Returns null if video not playing
    def set_seek(self, _time):
        from contextlib import closing
        try:
            if _time == 999999:
                _time = self.get_run_time
            xbmc.Player().seekTime(float(_time))
            return True
        except RuntimeError:
            pass

    def check_playnext(self):
        from contextlib import closing
        try:
            _playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            if _playlist.size() < 2:
                return False
            if _playlist.getposition() < (_playlist.size() - 1):
                return True
        except RuntimeError:
            pass
        
    def play_next(self):
        from contextlib import closing
        try:
            xbmc.Player().playnext()
        except RuntimeError:
            pass

    def stop_play(self):
        from contextlib import closing
        try:
            xbmc.Player().stop()
        except RuntimeError:
            pass

    # Return true if file name matches `skip.txt`, or contains video name while ending in `skip.txt`, as case-insensative
    def check_filename_match(self, _playing_file_name, _time_file_name):
        # Either can be one file with each season/episode enumerated,
        # or separate files named by season and episode
        _match = False
        if _time_file_name.lower() == 'skip.txt':
            if _static_name == 'true':
                _match = True
            elif _time_file_name == 'skip.txt':
                _match = True

        if _match_videoname == 'true':
            if _static_name == 'true':
                if _playing_file_name.lower() in _time_file_name: _match = True
            if not _static_name == 'true':
                if not _playing_file_name in _time_file_name: _match = True
        return _match

    def read_file(self, _foldername, _playing_file_name, _time_file_name, _timestamps):
        from contextlib import closing
        try:
            _file_path = os.path.join(_foldername, _time_file_name)
            with xbmcvfs.File(_file_path,'r') as f:
                _text = f.read()
                if not _text:
                    log('File is blank.')
                    return
                _lines = _text.split('\n')
                for _line in _lines:
                    _line = _line.strip()

                    # skip lines that start with '#' or are empty
                    # would prefer allowing inline comments too
                    if not _line or _line.startswith('#'): continue

                    #season/episode
                    if re.search(r'^s\d{2}', _line):
                        _is_match = self.check_season_episode_match(_playing_file_name, _line)
                        continue

                    # Timestamps
                    if not _is_match: continue
                    if self.read_time_line(_line):
                        _timestamps.append(self.read_time_line(_line))
            return _timestamps
        except IOError:
            log('Unable to open file:' + _foldername + '\\' + _time_file_name)
            pass

    def read_time_line(self, _line):
        # Timestamps
        if not re.match(r'^(\d+:)?(\d+:)?(\d+:)?\d+(-(\d+:)?(\d+:)?(\d+:)?\d+)?', _line): return
        # If timestamp ends with `-`, remove it
        if _line.endswith('-'): _line[:-1]
        _stop = "0"       # Set stop in case there is no stop time
        _start = _line   # Set start to line if it doesn't contains '-'
        if "-" in _line:
            _start = _line.rsplit("-", 1)[0]
            _stop = _line.rsplit("-", 1)[1]

        _start = self.convert_time_to_seconds(_start)
         
        # Check if stop is seconds or a "timestamp"
        if ':' in _stop:
            _stop = self.convert_time_to_seconds(_stop)   # convert to seconds
        # Can't avoid else, since addition would fail if it contains ':'
        else: 
            log(_stop)
            if float(_stop) > 0: _stop = float(_stop) + float(_start)

        # Format to 7 digits for sort to work
        # (enough for 11 days)
        return str(_start).rjust(10, '0') + '-' + str(_stop).rjust(10, '0').strip()
    
    def get_timestamps(self, _playing_file_name):
        _timestamps = []
        _foldername = self.get_video_folder()
        _playing_file_name = os.path.basename(_playing_file_name).rsplit(".", 1)[0]
        # If no need to loop through file names
        if not _static_name  == 'true' and _match_videoname != 'true':
            _timestamps = self.read_file(_foldername, _playing_file_name, 'skip.txt', _timestamps)
        
        if _static_name == 'true' or _match_videoname == 'true':
            _files = os.listdir(_foldername)
            for _time_file_name in _files:
                if not _time_file_name.lower().endswith('skip.txt'):
                    continue
                if not _static_name == 'true':
                    if not _time_file_name.endswith('skip.txt'):
                        continue
                if not self.check_filename_match(_playing_file_name, _time_file_name):
                    continue

                _timestamps = self.read_file(_foldername, _playing_file_name, _time_file_name, _timestamps)
        if _timestamps:
            _timestamps.sort()
        return _timestamps

    def convert_time_to_seconds(self, _time):
        if not ':' in str(_time):
            return _time
        _time_array = _time.split(':')
        _time_array .reverse()            # Since must have seconds, but not hours, minutes, reverse it to reduce if's
        _seconds = _time_array [0]
        _minutes = _time_array [1] if len(_time_array) > 1 else 0
        _hours = _time_array [2] if len(_time_array) > 2 else 0
        _days = _time_array [3] if len(_time_array) > 3 else 0
        return _days * 86400 + int(_hours) * 3600 + int(_minutes) * 60 + float(_seconds)

    def get_start_time(self, _time_string):
        if '-' in _time_string:
             return float(_time_string.rsplit("-", 1)[0])
        return float(_time_string)

    def get_stop_time(self, _time_string):
        if "-" in _time_string:
            return float(_time_string.rsplit("-", 1)[1])

    def onAVStarted(self):
        # Wait a bit for video to load
        #if KODIMONITOR.waitForAbort(0.4):
        #    return
        _poll_time = self.get_poll_time()
        load_settings()

        _playing_file_name = self.get_playing_video_name()
        log('Playing file: ' + _playing_file_name)
        self._timestamps = []
        _timestamps = self.get_timestamps(_playing_file_name)
        if not _playing_file_name:
            log('No playing file')
            return
        if not _timestamps:
            log('No timestamps')
            self.wait_video_end(_playing_file_name)
            return

        # Log all the matching timestamps
        log('Got timestamps:')
        if _logging == 'true':
            for i in range(0, len(_timestamps), 1):
                log(str(i) + ': ' + str(_timestamps[i]))

        # Check if video legth is zero
        #self.waitVideoPlaytime()
         
        #loop through each timestamp entry (extracted for this one video)
        # After all timestamps, send it to wait_video_end
        for i in range(0, len(_timestamps), 1):
            # get the (next) timestamp
            _start_time = self.get_start_time(_timestamps[i])
            _stop_time = self.get_stop_time(_timestamps[i])
            # If start = 0, and stop is blank, don't skip the entire video!
            if not _start_time and not _stop_time:
                log('Start and stop is blank.')
                continue

            # If no stop time entered, then set it to skip to next video
            if not _stop_time:
                _stop_time = 999999
            # If stop time extends past end time, then set it to skip to next video
            # Don't know if this matters
            elif _stop_time > self.get_video_length():
                log('Stop time '+ str(_stop_time) + ' is greater than video length ' + str(self.get_video_length()))
                _stop_time = 999999

            log('Start time: ' + str(_start_time) + '; end time: ' + str(_stop_time))
            log('Waiting for start time: ' + str(_start_time))
            if not self.get_playing_video_name: return
            # Wait for skip time to arrive (or video stops)
            while (self.get_run_time() < _start_time):
                if kodi_monitor.waitForAbort(_poll_time):
                    # Abort was requested while waiting. We should exit
                    return
                # Check if still playing the same video
                if self.get_playing_video_name() != _playing_file_name: return

            # If already past destination point, skip to the next timestamp
            if (self.get_run_time() and _stop_time < self.get_run_time()):
                log('Stop time (' + str(_stop_time) + ') has passed (' + str(self.get_run_time()) + ').')
                continue

            log('Skipped from ' + str(self.get_run_time()) + ' (' + str(_start_time) + ') to ' + str(_stop_time) + ' (' + str(_stop_time) + ')')
            # If skipping to the end of the video, play next
            # Then return, since it'll be a new video
            if _stop_time == 999999:
                if int(_start_time) == 0:
                    log('Trying to skip the entire video with start ' + str(_start_time) + ' end ' + str(_stop_time))
                    self.wait_video_end(_playing_file_name)
                # Set seek to near end, to set video play as completed (no resume position)
                self.set_seek(self.get_video_length() - 10)
                # If there is a playlist (and not at the end of it), play next
                if self.check_playnext():
                    log('Skipping to next video.')
                    self.play_next()
                # otherwise, stop
                else:
                    log('Stopping playback.')
                    self.stop_play()
                # Wait for video end (so not to get stuck in a loop, if Kodi doesn't skip/end fast enough)
                self.wait_video_end(_playing_file_name)
                return

            if not self.set_seek(_stop_time):
                return
        # After all timestamps, send it to wait_video_end
        self.wait_video_end(_playing_file_name)

    def wait_video_end(self, _playing_file_name):
        # If after last time stamp, monitor for abort or new video
        log('Waiting for video to end.')
        while self.get_playing_video_name() == _playing_file_name:
            if kodi_monitor.waitForAbort(1):
                break

class MyMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        log('Skip credits initialized')

    def onSettingsChanged(self):
        load_settings()
