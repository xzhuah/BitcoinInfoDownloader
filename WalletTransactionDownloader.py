import singlePageCrawler as sc
import multiPageCrawler as mc
import IOUtil.CsvIO as csv
import IOUtil.NetIO as NetIO
import threading
import os
import time

total_task=1000000000

buffer = []
thread=100
error_log = "Wtx_Error.csv"
error_url = "Failed_URL"+str(time.time())+".csv"
log_file = "Wtx_log.csv"
store_path = "./WalletTransaction/"
log_path=store_path+"log/"
url_file="WalletTxUrl.csv"
#all_wallet = sc.getAllWallet("Exchange")
all_wallet=["cbfb0b9e120c7a70","004307252736419e"]
def init():
    global buffer,thread,error_log,error_url,log_file,store_path,log_path,url_file,flag,content,finish
    buffer = []
    thread = 100
    error_log = "Wtx_Error.csv"
    error_url = "Failed_URL"+str(time.time())+".csv"
    log_file = "Wtx_log.csv"
    store_path = "./WalletTransaction/"
    log_path = store_path + "log/"
    url_file = "WalletTxUrl.csv"
    flag = 0
    content = []
    finish = False

    if not os.path.exists(store_path):
        os.makedirs(store_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)






def setParameter(thread_to_download,file_to_store_all_url,file_to_record_error,file_to_record_failed_url,file_to_record_progress,path_for_result,path_for_log,wallet_to_download):
    global thread,url_file,error_log,error_url,log_file,store_path,log_path,all_wallet
    thread, url_file, error_log, error_url, log_file, store_path, log_path, all_wallet=thread_to_download, file_to_store_all_url, file_to_record_error, file_to_record_failed_url, file_to_record_progress, path_for_result, path_for_log, wallet_to_download

def main():
    global buffer,thread,error_log,error_url,log_file,store_path,url_file,all_wallet

    init()
    if not os.path.exists(store_path):
        os.makedirs(store_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    error_log = log_path + error_log
    error_url = log_path + error_url
    log_file = log_path + log_file
    url_file = log_path + url_file



    downladTxFor(all_wallet)
#Call main to start download


def downladTxFor(wallet_ids):
    global buffer, thread, error_log, error_url, log_file, store_path, url_file, all_wallet
    print("Searching for related URLs")
    searchUrls(wallet_ids)
    print("Begin Downloading")
    beginDownload()

#To make a rubust crawler, we must record a table of all url so that the error can be fixed in the future
def searchUrls(wallet_ids):
    global buffer, thread, error_log, error_url, log_file, store_path, url_file, all_wallet
    pageNum=[]
    for wallet in wallet_ids:
        pageNum.append(mc.__getPageNum(wallet))

    with open(url_file,"a",encoding="utf-8") as f:
        for i in range(len(pageNum)):
            for k in range(1, pageNum[i]+1):
                url = "https://www.walletexplorer.com/wallet/"+wallet_ids[i]+"?page="+str(k)+"&format=csv"
                f.write(url+"\n")
            print("Done for ",wallet_ids[i])
    print("Searching Complete")

flag=0
content=[]
finish=False
def restore():
    beginDownload()

def beginDownload():
    global buffer, thread, error_log, error_url, log_file, store_path, url_file, all_wallet,flag,content,finish,total_task


    content = csv.readFile(url_file)

    content = content.split("\n")

    start = flag
    old_flag=start
    end = len(content)
    total_task = end
    start_time = time.time()
    while start + thread < end:
        sub_content = content[start:start + thread]

        try:
            thrs = [threading.Thread(target= downloadOneCSV, args=[url]) for url in sub_content]
            [thr.start() for thr in thrs]
            [thr.join() for thr in thrs]
        except Exception as e:
            csv.appendToFile(error_log, str(e))
            csv.appendToFile(error_log, "Affected url:"+str(start)+" to "+str(start+thread))
            pass


        start += thread
        flag=start

        if ((end - old_flag) != 0):
            progress = (start - old_flag) / (end - old_flag)
        else:
            progress = 1
        total_time = time.time()-start_time
        expected_time_left = total_time / progress-total_time
        log_str = "Current Progress: "+str(progress*100)+"%, Already run:"+str(total_time/60)+"mins, Expected Left:"+str(expected_time_left/60)+"mins, flag:"+str(flag)
        csv.appendToFile(log_file,log_str)

    sub_content = content[start:end]

    try:
        thrs = [threading.Thread(target=downloadOneCSV,
                                 args=[url]) for url in
                sub_content]
        [thr.start() for thr in thrs]
        [thr.join() for thr in thrs]
    except Exception as e:
        csv.appendToFile(error_log, str(e))
        csv.appendToFile(error_log, "Affected url:" + str(start) + " to " + str(start + end))
        pass
    start =end
    flag=start
    if ((end - old_flag) != 0):
        progress = (start - old_flag) / (end - old_flag)
    else:
        progress = 1
    total_time = time.time() - start_time
    expected_time_left = total_time / progress - total_time
    log_str = "Current Progress: " + str(progress * 100) + "%, Already run:" + str(
        total_time / 60) + "mins, Expected Left:" + str(expected_time_left / 60) + "mins, flag:"+str(flag)
    csv.appendToFile(log_file, log_str)
    finish=True
    del content[:]
    print("Finish WalletTransaction downloading")


def downloadOneCSV(url):
    global buffer, thread, error_log, error_url, log_file, store_path, url_file, all_wallet
    if (url==""):
        return

    try:
        filename = url.replace("https://www.walletexplorer.com/wallet/", "").replace("?", "_").replace("format=csv",".csv")
        content = NetIO.readDataFrom(url)
        csv.writeToFile(store_path + filename, content)

    except Exception as e:
        csv.appendToFile(error_log,str(e))
        csv.appendToFile(error_url,url)





#Call main to start
#main()