#This file help extract transaction id from all wallettransaction files and will deduplicate it
import os
import IOUtil.CsvIO as csv
# wallet_tx_path where the transaction files store
# txid_store_file where to store the result files
default_path="./WalletTransaction/"
default_file="all_txid.csv"

def extractTxid(wallet_tx_path,txid_store_file):
    print("Extracting")
    f = open(txid_store_file, 'a', encoding="utf-8")
    for filename in os.listdir(wallet_tx_path):
        try:
            content = csv.readFile(wallet_tx_path  + filename)
            content = content.split("\n")
            all_txid = []
            for ii in range(2, len(content) - 1):
                all_txid.append(content[ii].split(",")[-1].replace('"', ""))
            for id in all_txid:
                f.write(id + '\n')
        except:
            continue
    f.close()

    print("Deleting duplication")
    content = csv.readFile(txid_store_file)
    content = content.split("\n")

    clear_content = set(content)
    try:
        clear_content.remove("")
    except:
        pass

    csv.writeToFile(txid_store_file, "")  # delete original
    f = open(txid_store_file, 'a', encoding="utf-8")
    for i in clear_content:
        f.write(i + "\n")
    f.close()


    print("Finish")
def main():
    extractTxid(default_path,default_file)
#main()