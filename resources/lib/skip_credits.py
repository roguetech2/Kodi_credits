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
import xbmcaddon                 # used for settings and "Disable" button
import os                        # Used to manipulate the file folder names
import xbmcgui                   # Used to display "Disable" button
import re                        # Used to match season and episode, and validate time stamp entries
import time                      # Used for button timer

#import time                     # Obviously need time services


#_addon_info = xbmcaddon.Addon().getAddonInfo
#_addon_path = xbmc.translatePath(_addon_info('path'))
_polling_rate = float(0.3)

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
    global _dynamic_name

    _logging = xbmcaddon.Addon().getSetting('logging')
    _dynamic_name = xbmcaddon.Addon().getSetting('dynamic_name')
    
    _old_logging = _logging
    _old_dynamic_name = _dynamic_name

    _logging = xbmcaddon.Addon().getSetting('logging')
    if _old_logging != _logging: log('Set logging to ' + str(_logging) + ' from ' + str(_old_logging))
    _dynamic_name = xbmcaddon.Addon().getSetting('dynamic_name')
    if _old_dynamic_name != _dynamic_name: log('Set statis name to ' + str(_dynamic_name) + ' from ' + str(_old_dynamic_name))

def log(_msg):
    #if logging == True:
        xbmc.log(u'{0}: {1}'.format('scripts.skipcredits', _msg), level=xbmc.LOGFATAL)

class MyPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        _addonName = 'Skip Credits'

    def set_init_vars(self):
        load_settings()
        self.set_polling_rate()
        self.set_playing_video_name()
        self.set_video_folder_name()
        self.set_video_length()
        self.set_timestamps()

    # Performs xbmc.getPlayingFile()
    # Returns null if video not playing
    def set_video_folder_name(self):
        global _video_folder_name
        from contextlib import closing
        try:
            _video_folder_name = xbmc.getInfoLabel('Player.FilenameAndPath')
            _video_folder_name = os.path.dirname(_video_folder_name)
        except RuntimeError:
            pass

    # Performs xbmc.getPlayingFile()
    # Returns null if video not playing
    def set_playing_video_name(self):
        global _playing_video_name
        _playing_video_name = self.get_playing_video_name()
        
        if not _playing_video_name:
            log('No playing file')
            return
        else:
            log('Playing file: ' + _playing_video_name)

    # Performs xbmc.getPlayingFile()
    # Returns null if video not playing
    def get_playing_video_name(self):
        from contextlib import closing
        try:
            _playing_video_name = xbmc.Player().getPlayingFile()
            _playing_video_name = os.path.basename(_playing_video_name).rsplit(".", 1)[0]
            return _playing_video_name
        except RuntimeError:
            pass

    def set_polling_rate(self):
        global _polling_rate
        _old_polling_rate = _polling_rate
        _polling_rate = int(xbmcaddon.Addon().getSetting('polling_rate'))
        if _polling_rate == 0: _return_value = float(0.05)
        if _polling_rate == 1: _return_value = float(0.1)
        if _polling_rate == 2: _return_value = float(0.2)
        if _polling_rate == 3: _return_value = float(0.3)
        if _polling_rate == 4: _return_value = float(0.5)
        if _polling_rate == 5: _return_value = float(0.75)
        if _polling_rate == 6: _return_value = float(1)
        if _polling_rate == 7: _return_value = float(2)
        if _polling_rate == 8: _return_value = float(5)
        if _old_polling_rate != _polling_rate: log('Changed polling rate to ' + str(_return_value) + ' seconds from ' + str(_old_polling_rate) + ' seconds')
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

    def check_season_episode_match(self, _text):
        if self.match_season(_playing_video_name, _text) and self.match_episode(_playing_video_name, _text):
            return True

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
    def set_video_length(self):
        global _video_length
        from contextlib import closing
        _video_length = float(0)
        try:
            _video_length = float(xbmc.Player().getTotalTime())
        except RuntimeError:
            pass


    # Performs xbmc.seekTime()
    # Returns null if video not playing
    def perform_seek(self, _time):
        from contextlib import closing
        try:
            if _time == 999999:
                #_time = self.get_run_time() - 1
                return
            log('Set seek time as ' + str(_time))
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
    # _dynamic_name is expected to be true
    def check_filename_match(self, _time_file_name):
        if not _dynamic_name == 'true': return
        _time_file_name = _time_file_name.lower()

        if _time_file_name == 'skip.txt': return True
        if not _time_file_name.endswith('skip,txt'): return
        if _playing_video_name.lower() in _time_file_name: return True

    def read_file(self, _time_file_name):
        global _timestamps
        from contextlib import closing
        try:
            _file_path = os.path.join(_video_folder_name, _time_file_name)
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
                        _is_match = self.check_season_episode_match(_line)
                        continue

                    # Timestamps
                    if not _is_match: continue
                    if self.read_time_line(_line):
                        _timestamps.append(self.read_time_line(_line))
        except IOError:
            log('Unable to open file:' + _video_folder_name + '\\' + _time_file_name)
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
            if float(_stop) > 0: _stop = float(_stop) + float(_start)

        # Format to 7 digits for sort to work
        # (enough for 11 days)
        return str(_start).rjust(10, '0') + '-' + str(_stop).rjust(10, '0').strip()
    
    def set_timestamps(self):
        global _timestamps

        _timestamps = []
        # If no need to loop through file names
        if not _dynamic_name  == 'true':
            _timestamps = self.read_file('skip.txt')
            _timestamps = self.read_file(_playing_video_name + '_skip.txt')
        
        if _dynamic_name == 'true':
            _files = os.listdir(_video_folder_name)
            for _time_file_name in _files:
                if not _time_file_name.lower().endswith('skip.txt'):
                    continue
                if not self.check_filename_match(_time_file_name):
                    continue

                self.read_file(_time_file_name)
        if _timestamps:
            _timestamps.sort()
            
            # Log all the matching timestamps
            log('Got timestamps:')
            for i in range(0, len(_timestamps), 1):
                log(str(i) + ': ' + str(_timestamps[i]))
        else:
            log('No timestamps')
            self.wait_video_end()

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
            _stop_time =  float(_time_string.rsplit("-", 1)[1])  
        # If no stop time entered, then set it to skip to next video
        if not _stop_time:
            _stop_time = 999999
        # If stop time extends past end time, then set it to skip to next video
        # Don't know if this matters
        elif _stop_time > _video_length:
            log('Stop time '+ str(_stop_time) + ' is greater than video length ' + str(_video_length))
            _stop_time = 999999
        return _stop_time

    def set_seek(self, _start_time, _stop_time):
        # If skipping to the end of the video, play next
        # Then return, since it'll be a new video

        if _stop_time == 999999:
            if int(_start_time) == 0:
                log('Trying to skip the entire video with start ' + str(_start_time) + ' end ' + str(_stop_time))
                self.wait_video_end()
            # Set seek to near end, to set video play as completed (no resume position)
            self.perform_seek(_video_length - 10)
            # If there is a playlist (and not at the end of it), play next
            if self.check_playnext():
                log('Skipping to next video.')
                self.play_next()
            # otherwise, stop
            else:
                log('Stopping playback.')
                self.stop_play()
            # Wait for video end (so not to get stuck in a loop, if Kodi doesn't skip/end fast enough)
            self.wait_video_end()
            return

        if not self.perform_seek(_stop_time):
            return
        log('Skipped from ' + str(self.get_run_time()) + ' (' + str(_start_time) + ') to ' + str(_stop_time) )

    def onAVStarted(self):
        self.set_init_vars()
        log('Done setting vars.')
        if not _playing_video_name:
            log('not video playing')
            return
         
        #loop through each timestamp entry (extracted for this one video)
        # After all timestamps, send it to wait_video_end
        for i in range(0, len(_timestamps), 1):
            # get the (next) timestamp
            _start_time = self.get_start_time(_timestamps[i])
            _stop_time = self.get_stop_time(_timestamps[i])
            # If start = 0, and stop is blank, don't skip the entire video!
            if not _start_time and not _stop_time:
                log('Start and stop is blank (or video stopped playing).')
                continue

            log('Using start time: ' + str(_start_time) + '; end time: ' + str(_stop_time))
            log('Waiting for start time: ' + str(_start_time))

            # Wait for skip time to arrive (or video stops)
            while (self.get_run_time() < _start_time):
                # Check if still playing the same video
                if self.get_playing_video_name() != _playing_video_name: return

            # If already past destination point, skip to the next timestamp
            if (_stop_time < self.get_run_time()):
                log('Stop time (' + str(_stop_time) + ') has passed (' + str(self.get_run_time()) + ').')
                continue

            self.set_seek(_start_time, _stop_time)

        # After all timestamps, send it to wait_video_end
        self.wait_video_end()

    def wait_video_end(self):
        # If after last time stamp, monitor for abort or new video
        log('Waiting for video to end.')
        while self.get_playing_video_name() == _playing_video_name:
            if kodi_monitor.waitForAbort(1):
                break

class MyMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        log('Skip credits initialized')

    def onSettingsChanged(self):
        load_settings()

#class CustomDialog(xbmcgui.WindowXMLDialog):
#    def __init__(self, xmlFile, resourcePath):
#        pass#

#    def onInit(self):
#        global _disabled
#        global _dialog_open
#        _disabled = False
#        _dialog_open = True
#        log('Init dialog')
#        exit

    #def onControl(self, control):
    #    pass

    #def onFocus(self, control):
    #    pass

#    def onClick(self, control):
#        global _disabled
#        log('Here ' + str(control))
#        if control == 201:
#            log('Disabling')
#            _disabled = True
#            self.close()
