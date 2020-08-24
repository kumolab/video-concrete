# video-concrete
Automated process script for video caches
(under construction)

## Suitable for ME?
Only sprcified APP supported. Please view the list to check.
- bili
  
## How to Use?

**Step1**: Download it behind your caches
```
me@host:~/Videos$ git clone https://github.com/Kumo-YZX/video-concrete.git
```
and your Videos folder will be like that
```
Videos
├───2045104
├───19923713
└───video-concrate
```

**Step2**: Install requirements
```
me@host:~/Videos$ pip install -r requirements.txt
```

**Step3**: Run it
```
me@host:~/Videos$ python edit.py
```

## Guide for Development

There is one object that handles all the process: videoCache.

First of all, get_file_tree() function catches the video list and episode count of every video.

The apply_handle_num() function limits the amount of videos that we are going to handle.

Then we will call the deal_all function, scoll each video and episode, prepare to concrete videos.

The handle_m4() function concretes video and audio together.

The handle_flv() function concretes each clip together.

The move_conf_file() function move danmaku.xml and entry.json files.
