# 
import os, re

def stg_log(msg = "test log", level="info", filename = "./vc.log", do_print = 1):
    """
    msg: info message to be printed
    level: info or warning or error
    """
    from datetime import datetime
    std_log_msg = f"vc: {datetime.now().isoformat(timespec='seconds')}: [{level}]: {msg}"
    try:
        if (do_print):
            print(std_log_msg)
        std_log_msg += "\n"
        with open(filename, 'a') as fo:
            fo.write(std_log_msg)
    except UnicodeEncodeError as e:
        print(e)

def check_platform():
    """
    str returned
    """
    import platform
    return platform.system()

def liegal_filename(raw_name):
    illegal_chars = "\\/*?\"<>|.:"
    for every_char in illegal_chars:
        raw_name = raw_name.replace(every_char, "_")
    return raw_name


class videoExport(object):

    def __init__(self):
        self._tree = {"basic_path": "/", "exp_list": []}
        self._platform = check_platform()
        if self._platform == "Windows":
            self._slash = '\\'
        else:
            self._slash = '/'
        stg_log(f"videoExport loaded in platform: {self._platform}")
    
    def get_file_tree(self):
        from pathlib import PurePath
        local_file_path = os.getcwd()
        pHandle = PurePath(local_file_path)
        # Current path
        self._local_path = pHandle.parents[0]
        self._tree["basic_path"] = str(self._local_path)
        # list all dirs
        self._fp_list = os.listdir(self._local_path)
        # fp_list_copy = self._fp_list
        # self._fpa_list = []
        # stg_log(self._fp_list)
        for every_fp in self._fp_list:
            if not (re.fullmatch(r'edited_(s_)?\d{1,12}', every_fp)):
                continue
            if os.path.isdir(str(self._local_path) + self._slash + every_fp):
                self._tree["exp_list"].append({"exp_dir": every_fp})
        # stg_log(self._tree)
        stg_log("Get file tree done")

    def export_info(self, exp_file = "infoList.csv"):
        import json, csv
        export_csv_file = str(self._local_path) + self._slash + exp_file
        for every_video in self._tree["exp_list"]:
            stg_log(f"export info: {every_video}")
            info_location = str(self._local_path) + self._slash + every_video["exp_dir"] + self._slash + "infoFiles"
            raw_info_list = os.listdir(info_location)
            useable_info_list = []
            for every_info in raw_info_list:
                # episode number is shorter than 5 characters
                if re.fullmatch(r'entry.\d{1,5}.json', every_info):
                    useable_info_list.append(every_info)
                    with open(info_location + self._slash + every_info, 'rb') as fi:
                        # file_reads = fi.read()
                        # print(file_reads)
                        entry_file = json.load(fi)
                        title = entry_file["title"]
                        create_time = entry_file["time_create_stamp"]
                        update_time = entry_file["time_update_stamp"]
                        # avid = entry_file["avid"]
                        if "avid" in entry_file:
                            avid = entry_file["avid"]
                        else:
                            avid = 0
                        # bvid = entry_file["bvid"]
                        if "bvid" in entry_file:
                            bvid = entry_file["bvid"]
                        else:
                            bvid = "0"
                        if "owner_id" in entry_file:
                            owner = entry_file["owner_id"]
                        else:
                            owner = 0
                        full_description = entry_file["page_data"]["download_subtitle"]
                    stg_log(f"title: {title}, create_time: {create_time}," +
                            f"update_time: {update_time}, avid: {avid}, bvid: {bvid}," +
                            f"owner: {owner}, full_description: {full_description}")
                    with open(export_csv_file, "a", newline='') as fo:
                        csv_writer = csv.writer(fo,delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        try:
                            csv_writer.writerow([avid, bvid, owner,
                                                create_time, update_time,
                                                title, full_description])
                        except UnicodeEncodeError as e:
                            print(e)
                            csv_writer.writerow([avid, bvid, owner,
                                                create_time, update_time,
                                                "????", "????"])
        stg_log("export info done")

    def search_for_info(self, keyword=""):
        pass

    # keep sequence
    def rename_video(self):
        import json
        for every_video in self._tree["exp_list"]:
            stg_log(f"rename video: {every_video}")
            info_location = str(self._local_path) + self._slash + every_video["exp_dir"] + self._slash + "infoFiles"
            raw_info_list = os.listdir(info_location)
            for every_info in raw_info_list:
                # episode number is shorter than 5 characters
                if re.fullmatch(r'entry.\d{1,5}.json', every_info):
                    file_name_split = every_info.split('.')
                    episode_num = file_name_split[1]
                    with open(info_location + self._slash + every_info, 'rb') as fi:
                        entry_file = json.load(fi)
                        full_description = entry_file["page_data"]["download_subtitle"]
                        full_description = liegal_filename(full_description)
                    basic_path = str(self._local_path) + self._slash + every_video["exp_dir"]
                    source_file_name = basic_path + self._slash + episode_num + ".mp4"
                    # tbd..
                    rename_file_name = basic_path + self._slash + full_description + ".mp4"
                    # Check if video file for every episode exists
                    stg_log(f"{source_file_name} will be renamed with {rename_file_name}")
                    if os.path.exists(source_file_name):
                        # What if the description contains a char that cannot be used in filename?
                        try:
                            os.rename(source_file_name, rename_file_name)
                            stg_log("rename succeed")
                        except UnicodeEncodeError as e:
                            print(e)
                    else:
                        stg_log("entry.json does not mark a video", "warning")
        stg_log("rename video done")

    def rename_folder(self):
        import json
        for every_video in self._tree["exp_list"]:
            stg_log(f"rename video: {every_video}")
            info_location = str(self._local_path) + self._slash + every_video["exp_dir"] + self._slash + "infoFiles"
            raw_info_list = os.listdir(info_location)
            for every_info in raw_info_list:
                # episode number is shorter than 5 characters
                if re.fullmatch(r'entry.\d{1,5}.json', every_info):
                    # file_name_split = every_info.split('.')
                    # episode_num = file_name_split[1]
                    with open(info_location + self._slash + every_info, 'rb') as fi:
                        entry_file = json.load(fi)
                        title = entry_file["title"]
                        title = liegal_filename(title)
                    # basic_path = str(self._local_path) + self._slash + every_video["exp_dir"]
                    source_folder_name = str(self._local_path) + self._slash + every_video["exp_dir"]
                    # tbd..
                    rename_folder_name = str(self._local_path) + self._slash + title
                    # Check if video file for every episode exists
                    stg_log(f"{source_folder_name} will be renamed with {rename_folder_name}")
                    if os.path.exists(source_folder_name):
                        try:
                            os.rename(source_folder_name, rename_folder_name)
                            stg_log("rename succeed")
                        except UnicodeEncodeError as e:
                            print(e)
                    else:
                        stg_log("entry.json does not mark a video", "warning")
                    break
        stg_log("rename folder done")

    def move_video(self):
        pass

def load_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a',
        '--action',
        required=True,
        type=str,
        help="What to do next?"
    )
    return parser

def main():
    myHandle = videoExport()
    myHandle.get_file_tree()

    args = load_args().parse_args()
    the_action = args.action.replace(" ", '')
    if the_action == "expinfo":
        myHandle.export_info()
    elif the_action == "revideo":
        myHandle.rename_video()
    elif the_action == "refold":
        myHandle.rename_folder()
    else:
        print("what do you want?")

if __name__ == "__main__":
    main()