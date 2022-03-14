#!/usr/bin/env python3


from datetime import datetime
import time
from Actions import ActionDllFile
from config import url, SavePath, DaysToKeep
from pathlib import Path
from xmlreq import DllXmlReq
import os

starttime = ""
endtime = ""
name = ""


def parsertspuri(rtspuri):
    # starttime=20220311T073025Z&amp;endtime=20220311T073547Z&amp;
    # name=08000000014000713&amp;size=27635176
    #rtspuri = rtspuri.replace('rtsp://' + url + '/Streaming/tracks/101/?', '')
    Delrtspurl = rtspuri.split("/Streaming/tracks/101/?")
    tmpdic = Delrtspurl[1].split("&")
    starttime = tmpdic[0].replace('starttime=', '').replace('T', '-') + "-"
    endtime = tmpdic[1].replace('endtime=', '').replace('T', '-') + "-"
    size = int(tmpdic[3].replace('size=', ''))
    name = tmpdic[2].replace('name=', '') + ".mp4"
    #filename = starttime + endtime + name
    print("Downloading : " + name)
    print("size= " + str(size/1000000) + " M")
    FsName = PrepareDir(starttime[0:8]) + starttime[0:15] + endtime[0:15] + name
    ValidSize(FsName, size)
    return FsName


def donloadfs(rtspuris):
    print(str(len(rtspuris)) + " file(s) to Download")
    for rtspuri in rtspuris:
        #rtspuri = GetLocalip(rtspuri)
        print("rtspuri= " + rtspuri)
        DestFs = parsertspuri(rtspuri)
        if not os.path.exists(DestFs):
            ActionDllFile('/ISAPI/ContentMgmt/download?playbackURI=' +
                          rtspuri, DestFs, DllXmlReq(rtspuri))
            print(DestFs + " Downloaded")
    DelOldestDir()


def GetLocalip(rtspuri):
    Delrtspurl = rtspuri.split("/Streaming/tracks/101/?")
    Delrtspurl[0] = 'rtsp://' + url
    return Delrtspurl[0] + "/Streaming/tracks/101/?" + Delrtspurl[1]


def PrepareDir(Day):
    path = SavePath + Day + os.path.sep
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)

    return path


def ValidSize(Fs, size):
    if os.path.exists(Fs):
        b = os.path.getsize(Fs)
        if b < size:
            try:
                os.remove(Fs)
                print("Existing file have not the good size, deleting it")
            except:
                print("Problem to delete file")
        else:
            print("Existing file have the good size, pass")


def DelOldestDir():

    # Get list of all dir only in the given directory
    list_of_dir = os.listdir(SavePath)
    # Sort list of dir based on last modification time in ascending order
    list_of_dir = sorted(list_of_dir)
    # Iterate over sorted list of dir and print file path
    # along with last modification time of dir
    """ 
    for dir_name in list_of_dir:
        dir_path = os.path.join(SavePath, dir_name)
        timestamp_str = time.strftime('%m/%d/%Y',
                                time.gmtime(os.path.getmtime(dir_path))) 
        print(timestamp_str, ' -->', dir_name)
    """

    lendirs = len(list_of_dir)
    if lendirs > DaysToKeep:
        for ExtraDir in list_of_dir[:DaysToKeep - lendirs]:
            remove_path(Path(os.path.join(SavePath, ExtraDir)))


def remove_path(path: Path):
    if path.is_file() or path.is_symlink():
        path.unlink()
        return
    for p in path.iterdir():
        remove_path(p)
    path.rmdir()