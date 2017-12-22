import os
import IOUtil.NetIO as NetIO
import IOUtil.CsvIO as csv
import crawlerUtil as util
import singlePageCrawler as sc
import multiPageCrawler as mc
import time
import threading
import re

total_task=1000000000

buffer = []
thread=100
url_file="WalletPkUrl.csv"  # write and read this


#write the following
error_log = "PK_Error.csv"
error_url = "Failed_URL"+str(time.time())+".csv"
log_file = "PK_log.csv"
result_file="table.csv"

#store in here
store_path = "./WalletID_PK/"
log_path=store_path+"log/"

#all_wallet = sc.getAllWallet("Exchange")
all_wallet=["cbfb0b9e120c7a70","004307252736419e"]

def init():
    global buffer,thread,url_file,error_log,error_url,log_file,result_file,store_path,log_path,content,flag,finish,total_task
    buffer = []
    thread = 100
    total_task = 1000000000
    url_file = "WalletPkUrl.csv"  # write and read this

    # write the following
    error_log = "PK_Error.csv"
    error_url = "Failed_URL"+str(time.time())+".csv"
    log_file = "PK_log.csv"
    result_file = "table.csv"

    # store in here
    store_path = "./WalletID_PK/"
    log_path = store_path + "log/"

    content = []
    flag = 0
    finish = False

    if not os.path.exists(store_path):
        os.makedirs(store_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)




# to set all global parameter, only a description for variables
def setParameter(thread_to_download,file_to_store_all_url,file_to_record_error,file_to_record_failed_url,file_to_record_progress,file_to_store_pk,path_for_result,path_for_log,wallet_to_download):
    global thread,url_file,error_log,error_url,log_file,result_file,store_path,log_path,all_wallet
    thread, url_file, error_log, error_url, log_file, result_file, store_path, log_path, all_wallet=thread_to_download, file_to_store_all_url, file_to_record_error, file_to_record_failed_url, file_to_record_progress, file_to_store_pk, path_for_result, path_for_log, wallet_to_download

def main():
    global buffer,thread,error_log,error_url,log_file,store_path,url_file,all_wallet,result_file

    init()
    if not os.path.exists(store_path):
        os.makedirs(store_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    error_log=log_path+error_log
    error_url=log_path+error_url
    log_file=log_path+log_file

    url_file=log_path+url_file

    result_file=store_path+result_file

    csv.writeToFile(url_file, "")  # clear the file


    downladPkFor(all_wallet)
#Call main to start download


def downladPkFor(wallet_ids):
    global buffer, thread, error_log, error_url, log_file, store_path, url_file, all_wallet,result_file
    print("Searching for related URLs")
    searchUrls(wallet_ids)
    print("Begin Downloading")
    beginDownload()

#To make a rubust crawler, we must record a table of all url so that the error can be fixed in the future
def searchUrls(wallet_ids):
    global buffer, thread, error_log, error_url, log_file, store_path, url_file, all_wallet,result_file
    pageNum=[]
    for wallet in wallet_ids:
        pageNum.append(mc.__getKeyPageNum(wallet))

    with open(url_file,"a",encoding="utf-8") as f:
        for i in range(len(pageNum)):
            for k in range(1, pageNum[i]+1):
                url = "https://www.walletexplorer.com/wallet/"+wallet_ids[i]+"/addresses?page="+str(k)
                f.write(url+"\n")
            print("Done for ",wallet_ids[i])
    print("Searching Complete")



content=[]
flag=0
finish=False
def restore():
    beginDownload()

def beginDownload():
    global buffer, thread, error_log, error_url, log_file, store_path, url_file, all_wallet,result_file,content,flag,finish,total_task
    pattern2 = re.compile(r'<tr><td><a href=[^>]+')
    pattern_balance = re.compile(r'amount">[^&<]+')
    pattern_incomTx = re.compile(r"<td>[0-9]+")
    pattern_incomBlock = re.compile(r"<td>[0-9]+")

    content = csv.readFile(url_file)
    content = content.split("\n")

    start = flag
    old_flag=start
    end = len(content)
    total_task=end

    start_time = time.time()
    while start + thread < end:
        sub_content = content[start:start + thread]
        del buffer[:]

        try:
            thrs = [threading.Thread(target=downloadOneUrlPk, args=[url,pattern2,pattern_balance,pattern_incomTx,pattern_incomBlock]) for url in sub_content]
            [thr.start() for thr in thrs]
            [thr.join() for thr in thrs]
        except Exception as e:
            csv.appendToFile(error_log, str(e))
            csv.appendToFile(error_log, "Affected url:"+str(start)+" to "+str(start+thread))
            pass

        with open(result_file,"a",encoding="utf-8") as f:
            for record in buffer:
                f.write(record+"\n")
        start += thread
        del buffer[:]
        flag=start # update the flag
        if ((end - old_flag) != 0):
            progress = (start - old_flag) / (end - old_flag)
        else:
            progress = 1
        total_time = time.time()-start_time
        expected_time_left = total_time / progress - total_time
        log_str = "Current Progress: "+str(progress*100)+"%, Already run:"+str(total_time/60)+"mins, Expected Left:"+str(expected_time_left/60)+"mins"+",flag:"+str(flag)
        csv.appendToFile(log_file,log_str)
    sub_content = content[start:end]
    del buffer[:]
    try:
        thrs = [threading.Thread(target=downloadOneUrlPk,
                                 args=[url, pattern2, pattern_balance, pattern_incomTx, pattern_incomBlock]) for url in
                sub_content]
        [thr.start() for thr in thrs]
        [thr.join() for thr in thrs]
    except Exception as e:
        csv.appendToFile(error_log, str(e))
        csv.appendToFile(error_log, "Affected url:" + str(start) + " to " + str(start + end))
        pass

    with open(result_file, "a", encoding="utf-8") as f:
        for record in buffer:
            f.write(record + "\n")
    del buffer[:]

    start =end
    flag=start
    del buffer[:]
    if ((end - old_flag) != 0):
        progress = (start - old_flag) / (end - old_flag)
    else:
        progress = 1
    total_time = time.time() - start_time
    expected_time_left = total_time / progress - total_time
    log_str = "Current Progress: " + str(progress * 100) + "%, Already run:" + str(
        total_time / 60) + "mins, Expected Left:" + str(expected_time_left / 60) + "mins"+",flag:"+str(flag)
    csv.appendToFile(log_file, log_str)
    finish=True
    del content[:]
    print("Finish wallet public key downloading",total_task,flag)


def downloadOneUrlPk(url,pattern2,pattern_balance,pattern_incomTx,pattern_incomBlock):
    global buffer, thread, error_log, error_url, log_file, store_path, url_file, all_wallet,result_file
    if (url==""):
        return
    try:
        data = NetIO.readDataFrom(url)

        local_flag = 0

        match = True
        while match:
            match = pattern2.search(data, local_flag)

            if match:
                local_flag = int(match.span()[-1])
                sub = match.group()[26:-1]

                match_balance = pattern_balance.search(data, local_flag)
                local_flag = int(match_balance.span()[-1])
                balance = match_balance.group()[8:]

                match_incomTx = pattern_incomTx.search(data, local_flag)
                local_flag = int(match_incomTx.span()[-1])
                incomTx = match_incomTx.group()[4:]

                match_block = pattern_incomBlock.search(data, local_flag)
                local_flag = int(match_block.span()[-1])
                blockID = match_block.group()[4:]

                # print(sub+","+balance+","+incomTx+","+blockID)
                buffer.append( util.find_between(url, "https://www.walletexplorer.com/wallet/","/addresses")+","+sub + "," + balance + "," + incomTx + "," + blockID)

            else:
                break
    except Exception as e:
        csv.appendToFile(error_log,str(e))
        csv.appendToFile(error_url,url)





#Call main to start
#main()