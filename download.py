import pyinotify
import sys
import os
import aria2p
import queue
import time
import threading

exts=[
".jpg",
".pdf",
".mkv",
".webp",
".mp3",
".mp4",
".epub",
".mobi",
".txt",
".flac",
".MP3",
".chm",
".zip",
".log",
".cue",
".mka",
".ts",
".srt",
".mov",
".ass",
".avi",
".nfo",
".md5",
".rar",
".m2ts",
".azw3",
".png",
".cht",
".chs",
".test",
".html",
".wmv",
".ps",
".doc",
".MP4",
".iso",
".exe",
".docx",
".djvu",
".dat",
".7z"
]

def is_file(name):
    for ext in exts:
        if name.endswith(ext):
            return True
    return False

def main():
    if len(sys.argv) < 6:
        print("Script needs 6 arguments")
        return
    watch_path=sys.argv[1]
    if not watch_path.endswith('/'):
        watch_path=watch_path+'/'
    rpc_host=sys.argv[2]
    port=int(sys.argv[3])
    secreat=sys.argv[4]
    url_pre=sys.argv[5]
    if not url_pre.endswith('/'):
        url_pre=url_pre+'/'

    url_queue=queue.Queue()

    def aria2_loop():
        client=aria2p.Client(
            host=rpc_host,
            port=port,
            secret=secreat
        )
        aria2 = aria2p.API(client)
        while True:
            try:
                options=client.get_global_option()
                break
            except Exception as e:
                print("Link error: ", e)
                time.sleep(10)

        options['max_connection_per_server']=1
        base_dir=options['dir']
        if not base_dir.endswith('/'):
            base_dir=base_dir+'/'
        print("Host target dir: ", base_dir)

        while True:
            download_url, ralative_dir=url_queue.get(block=True, timeout=None)
            options['dir']=base_dir+ralative_dir
            uris=[download_url,]
            print ("Downloading: "+download_url)
            try:
                aria2.add_uris(uris,options=options)
            except Exception as e:
                print("Download error", e)
                url_queue.put((download_url, ralative_dir))
                time.sleep(10)
    
    
    # The watch manager stores the watches and provides operations on watches
    wm = pyinotify.WatchManager()
    # watched events
    mask = pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO
    
    class EventHandler(pyinotify.ProcessEvent):

        def process_IN_CREATE(self,event):
            if event.mask & pyinotify.IN_ISDIR:
                wm.add_watch(event.pathname,mask,rec=False)

        # def process_IN_CLOSE_WRITE(self, event):
        #     if len(event.name) > 0 and is_file(event.name):
        #         ralative_url=event.pathname[len(watch_path):]
        #         download_url=url_pre+ralative_url
        #         ralative_dir=""
        #         if '/' in ralative_url:
        #             ralative_dir=event.path[len(watch_path):]                  
        #         url_queue.put((download_url,ralative_dir))

        def process_IN_MOVED_TO(self,event):
            if event.mask & pyinotify.IN_ISDIR:
                wm.add_watch(event.pathname,mask,rec=False)
            elif is_file(event.name):
                ralative_url=event.pathname[len(watch_path):]
                download_url=url_pre+ralative_url
                ralative_dir=""
                if '/' in ralative_url:
                    ralative_dir=event.path[len(watch_path):]                  
                url_queue.put((download_url,ralative_dir))

    handler = EventHandler()

    notifier = pyinotify.Notifier(wm, handler)

    wdd = wm.add_watch(watch_path, mask, rec=True)

    threading.Thread(target=aria2_loop).start()

    notifier.loop()

if __name__=="__main__":
    main()