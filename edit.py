from moviepy.editor import VideoFileClip, concatenate_videoclips
import ffmpy
import os
from os import path
import re

def stg_log(msg = "test log", level="info", filenanme = "./vc.log", do_print = 1):
    """
    msg: info message to be printed
    level: info or warning or error
    """
    from datetime import datetime
    std_log_msg = f"vc: {datetime.now().isoformat(timespec='seconds')}: [{level}]: {msg}"
    if (do_print):
        print(std_log_msg)
    std_log_msg += "\n"
    with open(filenanme, 'a') as fo:
        fo.write(std_log_msg)

def check_platform():
    """
    str returned
    """
    import platform
    return platform.system()



class videoCache(object):

    def __init__(self):
        self._local_path = '/'
        self._tree = {"basic_path": "/", "video_list": []}
        self._handlenum = 5
        self._platform = check_platform()
        if self._platform == "Windows":
            self._slash = '\\'
        else:
            self._slash = '/'
        stg_log(f"videoCache loaded in platform: {self._platform}")

    def get_flv_num(self, fullpath):
        path_split = fullpath.split(self._slash)
        filename_split = path_split[-1].split('.')
        return int(filename_split[0])

    def getFileTree(self):
        from pathlib import PurePath
        local_file_path = os.getcwd()
        pHandle = PurePath(local_file_path)
        self._local_path = pHandle.parents[0]
        self._tree["basic_path"] = str(self._local_path)
        # list all dirs
        self._fp_list = os.listdir(self._local_path)
        # fp_list_copy = self._fp_list
        # self._fpa_list = []
        stg_log(self._fp_list)
        for every_fp in self._fp_list:
            # dir name rule
            if not (re.fullmatch(r'(s_)?\d{1,12}', every_fp)):
                # fp_list_copy.remove(every_fp)
                continue
            # every_fp = 
            # must be a dir and not edited
            if path.isdir(str(self._local_path) + self._slash + every_fp):
                try:
                    edit_status = self._fp_list.index(f"edited_{every_fp}")
                    if edit_status:
                        stg_log(f"{every_fp}: Already edited")
                except ValueError:
                    # self._fpa_list.append(str(self._local_path) + '\\' + every_fp)
                    self._tree["video_list"].append({ "av_number": every_fp })
                # finally:
        stg_log(self._tree)
        # get episode list
        for every_fp in self._tree["video_list"]:
            sp_list = os.listdir(self._tree["basic_path"] + self._slash + every_fp["av_number"])
            every_fp["episode_count"] = len(sp_list)
            every_fp["episode_offset"] = int(min(sp_list)) - 1
            if (int(max(sp_list)) != (every_fp["episode_offset"] + every_fp["episode_count"])):
                raise ValueError("episode number incorrect")
        stg_log(self._tree)
        print('sf')

    def apply_handle_num(self):
        # tbd: read from file
        import json
        with open('settings.json') as fi:
            config_structure = json.load(fi)
        self._handlenum = config_structure["handlenum"]
        self._tree["video_list"] = self._tree["video_list"][0:self._handlenum]
        stg_log(f"apply handle num: {str(self._handlenum)}")
        return 0

    def generate_source_path(self, seq_num, episode_num, flow_type):
        gen_path = self._tree["basic_path"] + self._slash
        gen_path += self._tree["video_list"][seq_num]["av_number"] + self._slash
        gen_path += str(self._tree["video_list"][seq_num]["episode_offset"] + episode_num) + self._slash
        gen_path += flow_type
        return gen_path

    def generate_exp_name(self, seq_num, episode_num):
        temp_av_bumber = self._tree["video_list"][seq_num]["av_number"]
        export_path = self._tree["basic_path"] + self._slash + f"edited_{temp_av_bumber}" # tbd...

        self.check_exp_path(export_path)
        # export_path += self._slash + self.read_video_info(seq_num, episode_num)["title"]
        export_path += self._slash + f"{str(episode_num)}.mp4"
        return export_path

    def generate_conf_exp_path(self, seq_num, episode_num):
        temp_av_bumber = self._tree["video_list"][seq_num]["av_number"]
        export_path = self._tree["basic_path"] + self._slash + f"edited_{temp_av_bumber}" # tbd...
        # export_path += self._slash + self.read_video_info(seq_num, episode_num)["title"]
        export_path += self._slash + "infoFiles"
        return export_path 

    def read_video_info(self, seq_num, episode_num):
        import json
        video_info = {}
        entry_path = self._tree["basic_path"] + self._slash +\
             str(self._tree["video_list"][seq_num]["episode_offset"] + episode_num) + self._slash + "entry.json"
        try:
            with open(entry_path, "r") as fi:
                video_info = json.load(fi)
        except FileNotFoundError:
            stg_log(f"read video info: {entry_path} not exist, ignored", "warning")
        # finally:
        return video_info

    # create if not exists
    def check_exp_path(self, ckpath):
        if not (path.exists(ckpath)):
            os.mkdir(ckpath)
            os.mkdir(ckpath + self._slash + "infoFiles")
            stg_log(f"init for path: {ckpath}")
        return 0


    def handle_m4(self, seq_num, episode_num, flow_type):
        filepath = self.generate_source_path(seq_num, episode_num, flow_type)
        stg_log(f"m4 focusing on {filepath}")
        # from moviepy import *
        default_audio_path = filepath + self._slash + "audio.m4s"
        useable_audio_path = filepath + self._slash + "audio.mp3"

        default_video_path = filepath + self._slash + "video.m4s"
        useable_video_path = filepath + self._slash + "video.mp4"

        if path.exists(default_audio_path):
            os.rename(default_audio_path, useable_audio_path)

        if path.exists(default_video_path):
            os.rename(default_video_path, useable_video_path)

        if not (path.exists(useable_audio_path) and path.exists(useable_video_path)):
            raise ValueError("lack of files")
        
        default_export_name = self.generate_exp_name(seq_num, episode_num)
        stg_log(f"handling mp4: {useable_audio_path}, {useable_video_path}")
        stg_log(f"  and will be exported to: {default_export_name}")

        current_clip = VideoFileClip(useable_video_path)
        current_clip.write_videofile(default_export_name, audio=useable_audio_path)

        stg_log(f"exp: {default_export_name} done")
        # tbd: delete cache files

    def handle_flv(self, seq_num, episode_num, flow_type):
        from operator import itemgetter
        filepath = self.generate_source_path(seq_num, episode_num, flow_type)
        stg_log(f"flv focusing on {filepath}")

        default_video_path = ""
        useable_video_path = ""
        export_video_path = ""
        file_list = os.listdir(filepath)
        file_list_dict = []
        for every_file in file_list:
            file_name_split = every_file.split('.')
            try:
                epi_num = int(file_name_split[0])
                file_list_dict.append({"full_name": every_file, "epi_num":epi_num})
            except Exception as e:
                stg_log(f"unsupported file name: {every_file}")
        file_list_sort = sorted(file_list_dict, key=itemgetter('epi_num'))
        file_list = []
        for every_file in file_list_sort:
            file_list.append(every_file["file_name"])
        stg_log(f"parts: {str(file_list)}")
        # file_list.sort() # ???
        clip_list = []
        exp_list = []
        for every_file in file_list:
            if re.fullmatch(r'\d{0,4}.blv', every_file):
                filename_split = every_file.split('.')
                default_video_path = filepath + self._slash + filename_split[0] + '.blv'
                useable_video_path = filepath + self._slash + filename_split[0] + '.flv'
                export_video_path = filepath + self._slash + filename_split[0] + '.mp4'
                #clip_list.append()
                os.rename(default_video_path, useable_video_path)
                clip_list.append(useable_video_path)
                exp_list.append(export_video_path)
            elif re.fullmatch(r'\d{0,4}.flv', every_file):
                filename_split = every_file.split('.')
                useable_video_path = filepath + self._slash + filename_split[0] + '.flv'
                export_video_path = filepath + self._slash + filename_split[0] + '.mp4'
                clip_list.append(useable_video_path)
                exp_list.append(export_video_path)
            else:
                # stg_log(f"trash file here: {every_file}")
                pass
        
        # check whether files are consequent
        for clip_idx in range(1, len(clip_list)):
            if (self.get_flv_num(clip_list[clip_idx]) - self.get_flv_num(clip_list[clip_idx-1])) != 1:
                stg_log(f"clips not consequecnt: {clip_list[clip_idx]}, {clip_list[clip_idx-1]}", "warning")

        ff_clip = []
        default_export_name = self.generate_exp_name(seq_num, episode_num)
        stg_log(f"handling flv: {filepath}")
        stg_log(f"  and will be exported to: {default_export_name}")
        for clip_idx in range(0, len(clip_list)):
            try:
                flv_name = clip_list[clip_idx]
                mp4_name = exp_list[clip_idx]
                if path.exists(mp4_name):
                    os.remove(mp4_name)
                ff = ffmpy.FFmpeg(
                    inputs = { flv_name: None },
                    outputs = { mp4_name: None }
                )
                ff.run()
                if path.exists(mp4_name):
                    current_clip = VideoFileClip(mp4_name)
                ff_clip.append(current_clip)
            except Exception as err:
                stg_log(f"handling {flv_name}, {str(err)}")
            finally:
                pass
        final_epi = concatenate_videoclips(ff_clip)
        final_epi.write_videofile(default_export_name)
        stg_log(f"exp: {default_export_name} done")
        # tbd: delete cache files


    def move_conf_files(self, seq_num, episode_num):
        import shutil

        conf_path = self._tree["basic_path"] + self._slash
        conf_path += self._tree["video_list"][seq_num]["av_number"] + self._slash
        conf_path += str(self._tree["video_list"][seq_num]["episode_offset"] + episode_num) + self._slash

        dest_path = self.generate_conf_exp_path(seq_num, episode_num)
        
        danmaku_old_file = conf_path + self._slash + 'danmaku.xml'
        danmaku_new_file = conf_path + self._slash + f"danmaku.{str(episode_num)}.xml"
        danmaku_dest_file = dest_path + self._slash + f"danmaku.{str(episode_num)}.xml"
        entry_old_file = conf_path + self._slash + 'entry.json'
        entry_new_file = conf_path + self._slash + f"entry.{str(episode_num)}.json"
        entry_dest_file = dest_path + self._slash + f"entry.{str(episode_num)}.json"

        try:
            os.rename(danmaku_old_file, danmaku_new_file)
            os.rename(entry_old_file, entry_new_file)
        except FileNotFoundError:
            stg_log(f"rename info file: {danmaku_old_file}, {entry_old_file} not found", "warning")
        
        shutil.copy(danmaku_new_file, danmaku_dest_file)
        shutil.copy(entry_new_file, entry_dest_file)

        stg_log(f"info files copied: {danmaku_dest_file}, {entry_dest_file}")

    def deal_all(self):
        stg_log(f"start to deal with all...")
        for video_index in range(0, len(self._tree["video_list"])):
            for epi_index in range(
                self._tree["video_list"][video_index]["episode_offset"] + 1,
                self._tree["video_list"][video_index]["episode_offset"] +\
                self._tree["video_list"][video_index]["episode_count"] + 1):
                stg_log(f"handle video_index, epi_index:{str(video_index)}, {str(epi_index)}")
                basic_path = self._tree["basic_path"] + self._slash
                basic_path += self._tree["video_list"][video_index]["av_number"] + self._slash
                basic_path += str(self._tree["video_list"][video_index]["episode_offset"] + epi_index)
                basic_path += self._slash

                fp_list = os.listdir(basic_path)
                flow_type = ""
                for every_dir in fp_list:
                    if path.isdir(basic_path + self._slash + every_dir):
                        flow_type = every_dir
                        break
                if flow_type == "":
                    stg_log(f"invalid flow type in: {basic_path}", "warning")
                
                source_path = self.generate_source_path(video_index, epi_index, flow_type)

                clip_files = os.listdir(source_path)

                video_type_flag = ""
                for every_clip in clip_files:
                    if re.match(r'\d{0,4}.blv', every_clip) or re.match(r'\d{0,4}.flv', every_clip):
                        video_type_flag = 'flv'
                        self.handle_flv(video_index, epi_index, flow_type)
                        break
                    elif re.fullmatch(r'video.m4s', every_clip) or re.fullmatch(r'video.mp4', every_clip):
                        video_type_flag = 'mp4'
                        self.handle_m4(video_index, epi_index, flow_type)
                        break
                
                self.move_conf_files(video_index, epi_index)

        stg_log(f"all done")



def main():
    myvc = videoCache()
    myvc.getFileTree()

    myvc.apply_handle_num()


    myvc.deal_all()


if __name__ == "__main__":
    main()



