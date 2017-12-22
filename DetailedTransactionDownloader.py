import singlePageCrawler as sc
import IOUtil.CsvIO as csv
import threading
import os
import time

total_task=1000000000

buffer = []
thread=20

#for writing
error_log = "Tx_Error.csv"
error_url = "Failed_txid"+str(time.time())+".csv"
log_file = "Tx_log.csv"
store_path = "./Transaction/"
log_path = store_path+"log/"
result_file="detail_tx.json"


url_file="all_txid.csv" #for reading

def init():
    global buffer,thread,error_log,error_url,log_file,store_path,log_path,result_file,flag,content,finish
    buffer = []
    thread = 20

    # for writing
    error_log = "Tx_Error.csv"
    error_url = "Failed_txid"+str(time.time())+".csv"
    log_file = "Tx_log.csv"
    store_path = "./Transaction/"
    log_path = store_path + "log/"
    result_file = "detail_tx.json"
    flag = 0
    content = []
    finish = False

    if not os.path.exists(store_path):
        os.makedirs(store_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)




def setParameter(thread_to_download,file_to_read_all_txid,file_to_record_error,file_to_record_failed_txid,file_to_record_progress,path_for_result,path_for_log,file_to_store_all_downloaded_tx):
    global thread,url_file,error_log,error_url,log_file,store_path,log_path,result_file
    thread, url_file, error_log, error_url, log_file, store_path, log_path, result_file=thread_to_download, file_to_read_all_txid, file_to_record_error, file_to_record_failed_txid, file_to_record_progress, path_for_result, path_for_log, file_to_store_all_downloaded_tx





error_num=0
def main():
    global buffer,thread,error_log,error_url,log_file,store_path,url_file,result_file
    init()

    if not os.path.exists(store_path):
        os.makedirs(store_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    error_log = log_path + error_log
    error_url = log_path + error_url
    log_file = log_path + log_file
    result_file = store_path+result_file

    print("Begin downloading transactions")
    beginDownload()
#Call main to start download
flag=0
content=[]
finish=False
def restore():
    beginDownload()

def beginDownload():
    global buffer, thread, error_log, error_url, log_file, store_path, url_file,result_file,flag,content,finish,total_task


    content = csv.readFile(url_file)
    content = content.split("\n")

    start = flag
    old_flag=start
    end = len(content)
    total_task = end
    start_time = time.time()
    while start + thread < end:
        sub_content = content[start:start + thread]
        del buffer[:]

        try:
            thrs = [threading.Thread(target= downloadOneTx, args=[url]) for url in sub_content]
            [thr.start() for thr in thrs]
            [thr.join() for thr in thrs]
        except Exception as e:
            csv.appendToFile(error_log, str(e))
            csv.appendToFile(error_log, "Affected url:"+str(start)+" to "+str(start+thread))
            pass

        with open(result_file,"a",encoding="utf-8") as f:
            for record in buffer:
                f.write(record+"\n")

        del buffer[:]


        start += thread
        flag = start

        if ((end - old_flag) != 0):
            progress = (start - old_flag) / (end - old_flag)
        else:
            progress = 1
        total_time = time.time()-start_time
        expected_time_left = total_time / progress - total_time
        log_str = "Current Progress: "+str(progress*100)+"%, Already run:"+str(total_time/60)+"mins, Expected Left:"+str(expected_time_left/60)+"mins, flag:"+str(flag)
        csv.appendToFile(log_file,log_str)

    sub_content = content[start:end]
    del buffer[:]
    try:
        thrs = [threading.Thread(target=downloadOneTx,
                                 args=[url]) for url in
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

    start = end
    flag=start
    if((end-old_flag)!=0):
        progress = (start - old_flag) / (end - old_flag)
    else:
        progress=1
    total_time = time.time() - start_time
    expected_time_left = total_time / progress -total_time
    log_str = "Current Progress: " + str(progress * 100) + "%, Already run:" + str(
        total_time / 60) + "mins, Expected Left:" + str(expected_time_left / 60) + "mins, flag:"+str(flag)
    csv.appendToFile(log_file, log_str)
    finish=True
    del content[:]
    print("Finish Transaction downloading")



def downloadOneTx(url):
    global buffer, thread, error_log, error_url, log_file, store_path, url_file,error_num,result_file
    if (url==""):
        return

    try:
        result = str(getBlockInfoTran(url))
        buffer.append(result)

    except Exception as e:
        csv.appendToFile(error_log,str(e))
        csv.appendToFile(error_url,url)
        error_num += 1



def getBlockInfoTran(txid):
    obj = sc.transactionQuery(txid)
    result = {}
    result["txid"] = txid
    try:
        result["included_in_block"] = obj["block_height"]
    except:
        result["included_in_block"]="NONE"
    result["time"] = obj["time"]
    result["size"] = obj["size"]
    # result["sender"]=wallet_id

    total_out = 0
    result["outputs"] = []
    outputs = obj["out"]
    for o in outputs:
        o_amount = o["value"] / 1e8
        total_out += o_amount
        try:
            addr = o["addr"]
        except:
            addr = "not-address"
        result["outputs"].append({"publickey": addr, "amount": o_amount, "spent": o["spent"]})

    result["inputs"] = []
    inputs = obj["inputs"]
    total_in = 0
    for i in inputs:
        try:
            ii = i["prev_out"]
            i_amount = ii["value"] / 1e8
            total_in += i_amount
            try:
                addr = ii["addr"]
            except:
                addr = "not-address"

            result["inputs"].append({"publickey": addr, "amount": i_amount,
                                     "tx_index": ii["tx_index"]})  # tx_index may be useful? for pre_txid
        except:

            result["inputs"] = "coinbase (mined bitcoins)"
            total_in = total_out
            break

    result["fee"] = total_in - total_out

    return result


        #Call main to start
#main()