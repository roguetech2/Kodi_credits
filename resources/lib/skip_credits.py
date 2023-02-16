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

logging = xbmcaddon.Addon().getSetting('logging')
static_name = xbmcaddon.Addon().getSetting('static_name')
match_videoname = xbmcaddon.Addon().getSetting('match_videoname')
poll_time = float(0.3)

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
    global logging
    global static_name
    global match_videoname

    old_logging = logging
    old_static_name = static_name
    old_match_videoname = match_videoname

    logging = xbmcaddon.Addon().getSetting('logging')
    if old_logging != logging: log('Set logging to ' + str(logging) + ' from ' + str(old_logging))
    static_name = xbmcaddon.Addon().getSetting('static_name')
    if old_static_name != static_name: log('Set logging to ' + str(static_name) + ' from ' + str(old_static_name))
    match_videoname = xbmcaddon.Addon().getSetting('match_videoname')
    if old_match_videoname != match_videoname: log('Set logging to ' + str(match_videoname) + ' from ' + str(old_match_videoname))

def log(msg):
    #if logging == True:
        xbmc.log(u'{0}: {1}'.format('scripts.skipcredits', msg), level=xbmc.LOGFATAL)

class MyPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        addonName = 'Skip Credits'

    def get_poll_time(self):
        global poll_time
        old_poll_time = poll_time
        poll_time = int(xbmcaddon.Addon().getSetting('poll_time'))
        if poll_time == 0: return_value = float(0.05)
        if poll_time == 1: return_value = float(0.1)
        if poll_time == 2: return_value = float(0.2)
        if poll_time == 3: return_value = float(0.3)
        if poll_time == 4: return_value = float(0.5)
        if poll_time == 5: return_value = float(0.75)
        if poll_time == 6: return_value = float(1)
        if poll_time == 7: return_value = float(2)
        if poll_time == 8: return_value = float(5)
        if old_poll_time != poll_time: log('Changed polling rate to ' + str(return_value) + ' seconds from ' + str(old_poll_time) + ' seconds')
        return return_value

    def extract_season(self,text):
        text = text.lower()
        # Use a regular expression to extract the season and episode numbers
        match = re.search(r'(s|season)(\d+)', text, re.I)
        if match:
            return int(match.group(2))
        else:
            return None

    def extract_episode(self,text):
        text = text.lower()
        # Use a regular expression to extract the season and episode numbers
        match = re.search(r'(e|episode|ep)(\d+)', text, re.I)
        if match:
            return int(match.group(2))
        else:
            return None

    #text1 is for video name
    #text2 may either be timestamp file name, or contents of it
    def match_season(self,text1,text2):
        text1_season = self.extract_season(text1)

        #If no video season, return true
        if not text1_season: return True

        pattern = r'(s|season)(\d+)'
        matches = re.findall(pattern, text2, re.I)
        if not matches: return text2

        line_seasons = [int(match[1]) for match in matches]
        if text1_season in line_seasons: return text2

    #text1 is for video name
    #text2 may either be timestamp file name, or contents of it
    def match_episode(self,text1,text2):
        text1_episode = self.extract_episode(text1)

        #If no video season, return true
        if not text1_episode: return True

        pattern = r'(e|episode)(\d+)'
        matches = re.findall(pattern, text2, re.I)
        if not matches: return text2

        line_episodes = [int(match[1]) for match in matches]
        if text1_episode in line_episodes: return text2

    def check_season_episode_match(self, videoname, text):
        if self.match_season(videoname,text) and self.match_episode(videoname,text):
            return True

    # Performs xbmc.getPlayingFile()
    # Returns null if video not playing
    def getVideoFolder(self):
        from contextlib import closing
        foldername = None
        try:
            foldername = xbmc.getInfoLabel('Player.FilenameAndPath')
            foldername = os.path.dirname(foldername)
            log(foldername)
        except RuntimeError:
            pass
        return foldername
    
    
    # Performs xbmc.getPlayingFile()
    # Returns null if video not playing
    def getVideoName(self):
        from contextlib import closing
        videoName = None
        try:
            videoName = xbmc.Player().getPlayingFile()
        except RuntimeError:
            pass
        return videoName
    
    # Performs xbmc.getTime()
    # Returns null if video not playing
    def getRuntime(self):
        from contextlib import closing
        runTime = float(0)
        try:
            runTime = float(xbmc.Player().getTime())
        except RuntimeError:
            pass
        return runTime
    
    # Performs xbmc.getTime()
    # Returns null if video not playing
    def getVideoLength(self):
        from contextlib import closing
        videoLength = float(0)
        try:
            videoLength = float(xbmc.Player().getTotalTime())
        except RuntimeError:
            pass
        return videoLength


    # Performs xbmc.seekTime()
    # Returns null if video not playing
    def setSeek(self,time):
        from contextlib import closing
        try:
            if time == 999999:
                time = self.getRuntime
            xbmc.Player().seekTime(float(time))
            return True
        except RuntimeError:
            pass

    def check_playnext(self):
        from contextlib import closing
        try:
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            if playlist.size() < 2:
                return False
            if playlist.getposition() < (playlist.size() - 1):
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
    def check_filename_match(self, playing_file_name, time_file_name):
        # Either can be one file with each season/episode enumerated,
        # or separate files named by season and episode
        match = False
        if static_name:
            if time_file_name.lower().endswith('skip.txt'):  match = True
            if time_file_name.lower() == 'skip.txt':  match = True
        if not static_name:
            if time_file_name.endswith('skip.txt'):  match = True
            if time_file_name == 'skip.txt':  match = True
        if match_videoname:
            if static_name:
                if playing_file_name.lower() in time_file_name: match = True
            if not static_name:
                if not playing_file_name in time_file_name: match = True
        return match

    def read_file(self, foldername, playing_file_name, time_file_name,timestamps):
        from contextlib import closing
        try:
            file_path = os.path.join(foldername, time_file_name)
            with xbmcvfs.File(file_path,'r') as f:
                text= f.read()
                if not text:
                    log('File is blank.')
                    return
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()

                    # skip lines that start with '#' or are empty
                    # would prefer allowing inline comments too
                    if not line or line.startswith('#'): continue

                    #season/episode
                    if re.search(r'^s\d{2}', line):
                        isMatch = False
                        if self.check_season_episode_match(playing_file_name, line):
                            isMatch = True
                        continue

                    # Timestamps
                    if not isMatch: continue
                    if self.read_time_line(line):
                        timestamps.append(self.read_time_line(line))
            return timestamps
        except IOError:
            log('Unable to open file:' + foldername + '\\' + time_file_name)
            pass

    def read_time_line(self,line):
        # Timestamps
        if not re.match(r'^(\d+:)?(\d+:)?(\d+:)?\d+(-(\d+:)?(\d+:)?(\d+:)?\d+)?',line): return
        # If timestamp ends with `-`, remove it
        if line.endswith('-'): line[:-1]
        stop = 0
        if "-" in line:
            start = line.rsplit("-", 1)[0]
            stop = line.rsplit("-", 1)[1]
        else:
            start = line
        start = self.convertTimeToSeconds(start)
        # Weird way to check if stop is only seconds
        newStop = 0
        if stop:
            newStop = self.convertTimeToSeconds(stop)   # convert to seconds
            if newStop == stop:                         # If unchanged, must be just seconds
                newStop = float(newStop) + float(start)     # In which case, add it to start time
        stop = newStop
        # Format to 7 digits for sort to work
        # (enough for 11 days)
        return str(start).rjust(10, '0') + '-' + str(stop).rjust(10, '0').strip()
    
    def get_timestamps(self, playing_file_name):
        timestamps = []
        foldername = self.getVideoFolder()
        playing_file_name = os.path.basename(playing_file_name).rsplit(".", 1)[0]
        # No need to loop at all
        if not static_name and not match_videoname:
            time_file_name = 'skip.txt'
            timestamps = self.read_file(foldername,'skip.txt',time_file_name,timestamps)
        
        if static_name or match_videoname:
            files = os.listdir(foldername)
            isMatch = True
            for time_file_name in files:
                isMatch = self.check_filename_match(playing_file_name, time_file_name)

                if static_name:
                    if time_file_name.lower() != 'skip.txt':
                        isMatch = False
                    log(time_file_name + ' match is ' + str(isMatch))

                if not isMatch:
                    continue
                timestamps = self.read_file(foldername,playing_file_name,time_file_name,timestamps)
        if timestamps:
            timestamps.sort()
        return timestamps

    def convertTimeToSeconds(self, strTime):
        if not ':' in str(strTime):
            return strTime
        time_array = strTime.split(':')
        time_array .reverse()
        seconds = time_array [0]
        minutes = time_array [1] if len(time_array) > 1 else 0
        hours = time_array [2] if len(time_array) > 2 else 0
        days = time_array [3] if len(time_array) > 3 else 0
        return days * 86400 + int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    def get_start_time(self, time_string):
        if '-' in time_string:
             return float(time_string.rsplit("-", 1)[0])
        return float(time_string)

    def get_stop_time(self, time_string):
        if "-" in time_string:
            return float(time_string.rsplit("-", 1)[1])
        log(time_string + " does contain a dash.")

    def onAVStarted(self):
        # Wait a bit for video to load
        #if KODIMONITOR.waitForAbort(0.4):
        #    return
        poll_time = self.get_poll_time()
        load_settings()

        playing_file_name = self.getVideoName()
        log('Playing file: ' + playing_file_name)
        self.timestamps = []
        timestamps = self.get_timestamps(playing_file_name)
        if not playing_file_name:
            log('No playing file')
            return
        if not timestamps:
            log('No timestammpes')
            self.waitVideoEnd(playing_file_name)
            return

        # Log all the matching timestamps
        log('Got timestamps:')
        if logging:
            for i in range(0, len(timestamps), 1):
                log(str(i) + ': ' + str(timestamps[i]))

        # Check if video legth is zero
        #self.waitVideoPlaytime()
         
        #loop through each timestamp entry (extracted for this one video)
        # After all timestamps, send it to waitVideoEnd
        for i in range(0, len(timestamps), 1):
            # get the (next) timestamp
            start_time = self.get_start_time(timestamps[i])
            stop_time = self.get_stop_time(timestamps[i])
            # If start = 0, and stop is blank, don't skip the entire video!
            if not start_time and not stop_time:
                log('Start and stop is blank.')
                continue

            # If no stop time entered, then set it to skip to next video
            if not stop_time:
                stop_time = 999999
            # If stop time extends past end time, then set it to skip to next video
            # Don't know if this matters
            elif stop_time > self.getVideoLength():
                log('Stop time '+ str(stop_time) + ' is greater than video length ' + str(self.getVideoLength()))
                stop_time = 999999

            log('Start time: ' + str(start_time) + '; end time: ' + str(stop_time))
            log('Waiting for start time: ' + str(start_time))
            if not self.getVideoName: return
            # Wait for skip time to arrive (or video stops)
            while (self.getRuntime() < start_time):
                if kodi_monitor.waitForAbort(poll_time):
                    # Abort was requested while waiting. We should exit
                    return
                # Check if still playing the same video
                if self.getVideoName() != playing_file_name: return

            # If already past destination point, skip to the next timestamp
            if (self.getRuntime() and stop_time < self.getRuntime()):
                log('Stop time (' + str(stop_time) + ') has passed (' + str(self.getRuntime()) + ').')
                continue

            log('Skipped from ' + str(self.getRuntime()) + ' (' + str(start_time) + ') to ' + str(stop_time) + ' (' + str(stop_time) + ')')
            # If skipping to the end of the video, play next
            # Then return, since it'll be a new video
            if stop_time == 999999:
                if int(start_time) == 0:
                    log('Trying to skip the entire video with start ' + str(start_time) + ' end ' + str(stop_time))
                    self.waitVideoEnd(playing_file_name)
                # Set seek to near end, to set video play as completed (no resume position)
                self.setSeek(self.getVideoLength() - 10)
                # If there is a playlist (and not at the end of it), play next
                if self.check_playnext():
                    log('Skipping to next video.')
                    self.play_next()
                # otherwise, stop
                else:
                    log('Stopping playback.')
                    self.stop_play()
                # Wait for video end (so not to get stuck in a loop, if Kodi doesn't skip/end fast enough)
                self.waitVideoEnd(playing_file_name)
                return

            if not self.setSeek(stop_time):
                return
        # After all timestamps, send it to waitVideoEnd
        self.waitVideoEnd(playing_file_name)

    def waitVideoEnd(self, playing_file_name):
        # If after last time stamp, monitor for abort or new video
        log('Waiting for video to end.')
        while self.getVideoName() == playing_file_name:
            if kodi_monitor.waitForAbort(1):
                break

class MyMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        log('MyMonitor - init')

    def onSettingsChanged(self):
        load_settings()
