import WalletPkDownloader
import WalletTransactionDownloader
import TransactionExtractor
import DetailedTransactionDownloader
import time
import threading
import IOUtil.CsvIO as csv
from kivy.uix.button import Button
from kivy.uix.label import Label
wallets=["004307252736419e"] #you can get wallet id by wallet kind, or a public key in that using the methods in singlepagecrawler
# all main can only be called once in one main!!!!

center_log="centerlog.csv"


def downloadWalletPK(wallets,btn="None",hint=""):
    time_inter = 30
    WalletPkDownloader.init()
    WalletPkDownloader.all_wallet = wallets
    main_thred = threading.Thread(target=WalletPkDownloader.main)
    moniter = threading.Thread(target=addMonitorFor, args=[WalletPkDownloader, time_inter])
    main_thred.start()
    moniter.start()
    main_thred.join()
    moniter.join()
    if (isinstance(btn,Button)):
        btn.disabled=False
    if (isinstance(hint, Label)):
        hint.text = "Finish Downloading"

def downloadWalletPKByURL(url_files,btn="None",hint=""):
    time_inter = 30
    WalletPkDownloader.init()
    WalletPkDownloader.url_file=url_files
    main_thred = threading.Thread(target=WalletPkDownloader.beginDownload)
    moniter = threading.Thread(target=addMonitorFor, args=[WalletPkDownloader, time_inter])
    main_thred.start()
    moniter.start()
    main_thred.join()
    moniter.join()
    if (isinstance(btn,Button)):
        btn.disabled=False
    if (isinstance(hint, Label)):
        hint.text = "Finish Downloading"


def downloadWalletTransaction(wallets,btn="None",hint=""):
    time_inter = 30
    WalletTransactionDownloader.init()
    WalletTransactionDownloader.all_wallet = wallets

    main_thred = threading.Thread(target=WalletTransactionDownloader.main)
    moniter = threading.Thread(target=addMonitorFor, args=[WalletTransactionDownloader, time_inter])
    main_thred.start()
    moniter.start()
    main_thred.join()
    moniter.join()
    if (isinstance(hint, Label)):
        hint.text = "Finish Downloading, now extracting all transaction id from the result"
    TransactionExtractor.extractTxid('./WalletTransaction/', "all_txid" + str(time.time()) + ".csv")
    if (isinstance(btn,Button)):
        btn.disabled=False
    if (isinstance(hint, Label)):
        hint.text = "Finish"




def downloadWalletTransactionByURL(url_file,btn="None",hint=""):
    time_inter = 30
    WalletTransactionDownloader.init()
    WalletTransactionDownloader.url_file=url_file
    print(WalletTransactionDownloader.url_file)
    main_thred = threading.Thread(target=WalletTransactionDownloader.beginDownload)
    moniter = threading.Thread(target=addMonitorFor, args=[WalletTransactionDownloader, time_inter])
    main_thred.start()
    moniter.start()
    main_thred.join()
    moniter.join()
    if (isinstance(hint, Label)):
        hint.text = "Finish Downloading, now extracting all transaction id from the result"
    TransactionExtractor.extractTxid('./WalletTransaction/', "all_txid" + str(time.time()) + ".csv")
    if (isinstance(btn,Button)):
        btn.disabled=False
    if (isinstance(hint, Label)):
        hint.text = "Finish"



def downloadDetails(txid_file,btn="None",hint=""):
    downloadTxOnly(txid_file,True,hint)
    if (isinstance(btn,Button)):
        btn.disabled=False
    if (isinstance(hint, Label)):
        hint.text = "Finish Downloading"


#Full stack download
def main(wallets,btn="None",hint=""):
    #download all wallet information in one time: the most easy way to use
    time_inter = 30
    if(isinstance(hint,Label)):
        hint.text="Begin downloading Wallet Public keys"
    downloadWalletPK(wallets)

    if (isinstance(hint, Label)):
        hint.text = "Begin downloading Wallet level transaction"

    downloadWalletTransaction(wallets)

    if (isinstance(hint, Label)):
        hint.text = "Begin Extracting transaction ids and deduplication"

    TransactionExtractor.main()

    if (isinstance(hint, Label)):
        hint.text = "Begin downloading Detailed transaction"

    main_thred = threading.Thread(target=DetailedTransactionDownloader.main)
    moniter = threading.Thread(target=addMonitorFor, args=[DetailedTransactionDownloader, time_inter])
    main_thred.start()
    moniter.start()
    main_thred.join()
    moniter.join()
    if (isinstance(btn,Button)):
        btn.disabled=False
    if (isinstance(hint, Label)):
        hint.text = "Finish Downloading"


    #re download error transactions

def downloadTxOnly(txidpath,deduplicate=True,hint=""):
    if deduplicate:
        content = csv.readFile(txidpath)
        content = content.split("\n")
        clear_content = set(content)
        try:
            clear_content.remove("")
        except:
            pass
        csv.writeToFile(txidpath, "")  # delete original
        f = open(txidpath, 'a', encoding="utf-8")
        for i in clear_content:
            f.write(i + "\n")
        f.close()
    DetailedTransactionDownloader.init()
    DetailedTransactionDownloader.url_file = txidpath

    main_thred = threading.Thread(target=DetailedTransactionDownloader.main)
    moniter = threading.Thread(target=addMonitorFor, args=[DetailedTransactionDownloader, 30])
    main_thred.start()
    moniter.start()
    main_thred.join()
    moniter.join()

#
# def deal_with_failed_pkurl():
#     time_inter=30
#     WalletPkDownloader.url_file = WalletTransactionDownloader.error_url
#     WalletTransactionDownloader.error_url=WalletTransactionDownloader.error_url.replace(".csv","again.csv")
#     WalletPkDownloader.finish=False
#     WalletPkDownloader.flag=0
#     main_thred = threading.Thread(target=WalletPkDownloader.restore)
#     moniter = threading.Thread(target=addMonitorFor, args=[WalletPkDownloader, time_inter])
#     main_thred.start()
#     moniter.start()
#     main_thred.join()
#     moniter.join()
#





def addMonitorFor(target_function,time_inter):
    while(not target_function.finish):
        remember=target_function.flag
        time.sleep(time_inter)
        if(remember==target_function.flag):
            csv.appendToFile(center_log,str(time.time())+":" +str(target_function)+" stopped, restoring...")
            main_thred = threading.Thread(target=target_function.restore)
            moniter = threading.Thread(target=addMonitorFor,args=[target_function,time_inter])
            main_thred.start()
            moniter.start()
            main_thred.join()
            moniter.join()



if __name__=="__main__":

    main(wallets)
# content = csv.readFile("filtered_transaction_2016.csv")
# content = content.split("\n")
# print(len(content))
#
# content=set(content)
# try:
#     content.remove("")
# except:
#     pass
# print(len(content))
# csv.writeToFile("filtered_transaction_2016.csv","")
# f=open("filtered_transaction_2016.csv","w",encoding="utf-8")
# for c in content:
#     f.write(c+"\n")