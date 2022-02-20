import sys
import os
import aria2p
import queue
import time
import threading
from configparser import ConfigParser

def make_end(string, end):
    if not string.endswith(end):
        return string+end
    else:
        return string

def contain_word(name, word_list):
    if len(word_list)==0: return True
    for word in word_list:
        if word in name: return True
    return False



def main():
    if len(sys.argv) < 3:
        print("Example: python3 manual.py download.ini path_to_file")
        return
    word_list = []
    if len(sys.argv) >= 4:
        word_list=sys.argv[3].split()
        print("Match files with key words "+str(word_list))
    else:
        print("Match all files")
    config_ini=sys.argv[1]
    config = ConfigParser()
    config.read(config_ini, encoding='UTF-8')

    watch_path=config['inotify']['watch_dir']
    if not watch_path.endswith('/'):
        watch_path=watch_path+'/'
    rpc_host=config['aria2']['host']
    port=int(config['aria2']['port'])
    secret=config['aria2']['secret']
    url_pre=config['aria2']['url_pre']
    if not url_pre.endswith('/'):
        url_pre=url_pre+'/'

    url_queue=queue.Queue()

    dir_list=[watch_path+sys.argv[2],]
    while len(dir_list)>0:
        pathname=dir_list.pop()
        if os.path.isdir(pathname):  
            for name in os.listdir(pathname):
                dir_list.append(pathname+'/'+name)
        elif os.path.isfile(pathname):
            if not contain_word(os.path.basename(pathname), word_list): continue
            ralative_url=pathname[len(watch_path):]
            download_url=url_pre+ralative_url
            ralative_dir=""
            if '/' in ralative_url:
                ralative_dir=os.path.dirname(pathname)[len(watch_path):]                  
            url_queue.put((download_url,ralative_dir))
        else:  
            print("Skip "+pathname)
    print(str(url_queue.qsize())+" files to be downlaoded")

    # download files
    client=aria2p.Client(
        host=rpc_host,
        port=port,
        secret=secret
    )
    aria2 = aria2p.API(client)
    while True:
        try:
            options=client.get_global_option()
            break
        except Exception as e:
            print("Link error: ", e)
            time.sleep(10)

    options['max_connection_per_server']=config['aria2']['connections']
    base_dir=options['dir']
    if not base_dir.endswith('/'):
        base_dir=base_dir+'/'
    print("Host target dir: ", base_dir)

    while not url_queue.empty():
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

if __name__=="__main__":
    main()