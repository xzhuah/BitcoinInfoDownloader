#multiPageCrawler defines functions that will do more than one http request. Besides, the information will be write to a local file


import re
import time
import os
import csv
from IOUtil import NetIO
from IOUtil import CsvIO
import pandas as pd
import threading
from singlePageCrawler import transactionWalletQuery as tq
from bs4 import BeautifulSoup
# return the page number of public key of a wallet

pk_progress_moniter={}
tx_progress_moniter={}

def __getKeyPageNum(wallet_id):
    url = 'https://www.walletexplorer.com/wallet/'+wallet_id+'/addresses'
    data =  NetIO.readDataFrom(url)
    pattern = re.compile(r'Page 1 / [0-9]+')

    match = re.search(pattern, data)

    num = match.group()
    num=int(num[9:])
    return num

#return a list of all public key of a wallet on page page
def __getPublicAdr(wallet_id,page=1):
    url = 'https://www.walletexplorer.com/wallet/'+wallet_id+'/addresses?page='+str(page)
    data =  NetIO.readDataFrom(url)
    flag = 0
    pattern2 = re.compile(r'<tr><td><a href=[^>]+')
    result = []
    match=True

    while match:
        match = pattern2.search(data,flag)
        if match:
            flag = int(match.span()[-1])
            sub = match.group()[26:-1]
            result.append(sub)
        else:
            break
    return result

# call this method to download all public address of a wallet given its id

def downloadAllPublicAddressOf(wallet_id, local_file="",start_page = 1, show_time = False,clear_file = False):
    if local_file == "":
        local_file = wallet_id+".csv" # if the user doesn't provide a file to store the key, the function will generate one

    if(clear_file):
        CsvIO.writeToFile(local_file,"") #Clear the file first

    total_page = __getKeyPageNum(wallet_id)
    #total_time = 0;

    pattern2 = re.compile(r'<tr><td><a href=[^>]+')
    pattern_balance = re.compile(r'amount">[^&<]+')
    pattern_incomTx = re.compile(r"<td>[0-9]+")
    pattern_incomBlock = re.compile(r"<td>[0-9]+")

    for i in range(start_page, total_page + 1):
        pk_progress_moniter[wallet_id] = (i-1) / total_page
        #start = time.time()
        url = 'https://www.walletexplorer.com/wallet/' + wallet_id + '/addresses?page=' + str(i)
        data = NetIO.readDataFrom(url)

        flag = 0

        match=True
        while match:
            match = pattern2.search(data, flag)

            if match:
                flag = int(match.span()[-1])
                sub = match.group()[26:-1]


                match_balance =  pattern_balance.search(data,flag)
                flag = int(match_balance.span()[-1])
                balance = match_balance.group()[8:]

                match_incomTx = pattern_incomTx.search(data,flag)
                flag = int(match_incomTx .span()[-1])
                incomTx = match_incomTx .group()[4:]

                match_block = pattern_incomBlock.search(data, flag)
                flag = int(match_block.span()[-1])
                blockID = match_block.group()[4:]



                #print(sub+","+balance+","+incomTx+","+blockID)
                CsvIO.appendToFile(local_file, sub+","+balance+","+incomTx+","+blockID)
            else:
                break
        pk_progress_moniter[wallet_id] = (i) / total_page




        # finish = time.time()
        # t = finish-start
        # total_time += t
        # expect_left = (total_page - i) * t
        #
        # if show_time:
        #     print (str(i),'tooks ', t,"secs")
        #     print(total_page, "time left:",expect_left/60,"mins")


# return the total page number of transaction of a wallet
#downloadAllPublicAddressOf("YoBit.net",start_page=26)
def __getPageNum(wallet_id):
    url = 'https://www.walletexplorer.com/wallet/' + wallet_id
    data = NetIO.readDataFrom(url)
    pattern = re.compile(r'Page 1 / [0-9]+')

    match = re.search(pattern, data)

    num = match.group()
    num = int(num[9:])
    return num


def __findTime(data):
    all_time = re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', data)
    start = all_time[-1]
    end = all_time[1]
    return end, start
def __getTransactionID(data):
    df = pd.read_csv(data)
    saved_column = df.transaction
    return saved_column
# call this method to download all transaction history of a given wallet id
def downloadTransactionBetweenTime(wallet_id, end_time, start_time, store_path="",download_transaction_detail = True,show_time=False):  # [start_time,end_time]
    # for easily update, accuracy to date end = 2017-10-26 start = 2017-02-21. The path should be a directory instead of a file
    total_page = __getPageNum(wallet_id)
    page = range(1, total_page + 1)
    #find_end = False

    if (store_path == ""):
        store_path = wallet_id +"_"+ start_time + "To" + end_time
    if not os.path.exists(store_path):
        os.makedirs(store_path)
    if (download_transaction_detail):
        append_file = store_path + "/Txdetail"
        if not os.path.exists(append_file):
            os.makedirs(append_file)


    #total_time = 0;
    for i in page: #
        tx_progress_moniter[wallet_id] = (i-1) / total_page
        detail_file = append_file + "/transactionDetail_"+str(i)+".json"
        #start = time.time()
        url = 'https://www.walletexplorer.com/wallet/' + wallet_id + '?page=' + str(i) + '&format=csv'
        local_file = store_path + "/" + wallet_id +"_"+ str(i) + '.csv'
        data = NetIO.readDataFrom(url)
        end, start = __findTime(data)
        if (end >= start_time and end <= end_time) or (start >= start_time and start <= end_time):
            CsvIO.writeToFile(local_file, data)
        elif (end < start_time):
            break
        if (download_transaction_detail):
            # Also go through the transaction id on every page and append the json to a file
            d_data = CsvIO.readFile(local_file)
            dd = d_data.split("\n")
            all_txid = []
            for ii in range(2,len(dd)-1):
                all_txid.append(dd[ii].split(",")[-1].replace('"',""))

            for txid in all_txid:
                #bottle neck here
                try:
                    CsvIO.appendToFile(detail_file,str(tq(txid)))
                except:
                    pass
            #boost a lot
            # thrs = [threading.Thread(target=__appendDetailFile, args=[detail_file,txid]) for txid in all_txid]
            # [thr.start() for thr in thrs]
            # [thr.join() for thr in thrs]
        tx_progress_moniter[wallet_id] = i / total_page


def __appendDetailFile(detail_file,txid):

    text = str(tq(txid))

    CsvIO.appendToFile(detail_file, text)

def __test():
    downloadAllPublicAddressOf("00022feb0ded1f9c",start_page = 544)
    downloadTransactionBetweenTime("Btc38.com","2017-10-29","2016-12-16")

#__test()
#downloadAllPublicAddressOf("000dd25b40be9265",start_page = 1)
#downloadTransactionBetweenTime("Btc38.com","2017-10-30","2016-12-16")

