Not tested for version 20!

This addon skips video playback based on timestamps entered in a text file. After installing, preferences can be set un Services -> Skip Credits - > Configure.

The first setting is for polling rate, which determines how precise it will be in skipping.The only thing performed within this loop is checking the video playback position and check if the filename has changed. A decent computer should be able to do this at the minimum setting, but there isn't much point for anything less than 300 milliseconds.

The second setting determines whether the addon should read through all file names searching for a non-case-sensative matches. If the video may be in a directory with large numbers of files, you may want to disable this. The filename search is only performed when a video begins playing.

The third setting determines whether to match against the directory name, or just file name. For instance, if multiple videos are saved in the same directory, you may wish to name them [video name]skip.txt. However, if the file name is Tv Show S01E03.mkv, the time file would need to be named "Tv Show S01E03_skip.txt" (where the underscore can be any number of non-alphanumeric characters). This setting allows it to match using the directory name.

The fourth retting matches a (potential) time stamp file to video name. Using the same example as above, a time stamp file named "Tv Show_skip.txt" would match a video file name of "Tv Show S01E03.mkv". In this case, the underscore must be a single underscore character.

The fifth setting adds a given amount of time for when to initiate a skip, excluding from the beginning of a video (that is, any starting at zero). It is functionally the same as setting the "stop time" as being later, but allows different users to pick their preference with avoiding abrupt jumps.

The final setting enables logging.

See \resources\example_skip.txt for how to build timestamp files. They should be in as start-stop, where start and stop are in hh:mm:ss formt, such that with 0-1:30, the video would start at 1 minute 30 seconds. If the stop time is only seconds, then it skips forward that far, such that 1:30-15 would skip from 1:30 to 1:45. if no end time is entered, it will skip to near the end to set the video as fully watched, then either stop or if a playlist, advance to the next video. Note that multiple time stamps files can be used for a single video - all potential matches as per the settings above will be combined. Timestamps can be set to apply to seasons and episodes by having a preceding line as, far instance, "s01" or "s01e01". Again, see example_skip.txt for more information.
