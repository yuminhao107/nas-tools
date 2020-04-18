import pyinotify
import sys
import os
import queue
import time
import threading
from configparser import ConfigParser

def main():
    if len(sys.argv) < 2:
        print("Script input path to config.ini as argument")
        return

    config_ini=sys.argv[1]
    config = ConfigParser()
    config.read(config_ini, encoding='UTF-8')

    watch_path=config['inotify']['watch_dir']
    remote_path=config['ssh']['remote_dir']
    if not remote_path.endswith('/'):
        remote_path=remote_path+'/'
    port=int(config['ssh']['port'])

    print('Upload to remote path: {0} -P {1}'.format(remote_path, port))
    print('Watch path: '+watch_path)
    scp_queue=queue.Queue()

    def scp_loop():
        while True:
            pathname=scp_queue.get(block=True, timeout=None)
            print ("Uploading: "+pathname)
            # ret=os.system('scp -P {0} \"{1}\" \"{2}\"'.format(port,pathname,remote_path))
            ret = 0
            if ret != 0:
                print("Scp Error. The server may be down.")
                scp_queue.put(pathname)
                time.sleep(10)
                continue
            ret=os.system('rm \"{0}\"'.format(pathname))
            if ret != 0:
                print("Fail to delete.")

    def upload_torrent(event):
        if event.name.endswith('torrent'):
            scp_queue.put(event.pathname)

    # The watch manager stores the watches and provides operations on watches
    wm = pyinotify.WatchManager()
    # watched events
    mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_MOVED_TO
    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_CLOSE_WRITE(self, event):
            upload_torrent(event)
        
        def process_IN_MOVED_TO(self,event):
            upload_torrent(event)

    handler = EventHandler()

    notifier = pyinotify.Notifier(wm, handler)

    wdd = wm.add_watch(watch_path, mask, rec=True)

    threading.Thread(target=scp_loop).start()

    notifier.loop()

if __name__=="__main__":
    main()