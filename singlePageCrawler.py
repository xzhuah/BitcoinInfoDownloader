# singlePageCrawler defined a set of realtime function that will do at most one http request, the data will only be stored in memory
from crawlerUtil import str2Object
from crawlerUtil import find_between
import re
import time as time_tool

from bs4 import BeautifulSoup
from IOUtil import NetIO
from crawlerUtil import find_between

from datetime import datetime

# The following functions are designed for using the API on https://blockchain.info/api/blockchain_api

def blockQuery(block_hash):
    url = "https://blockchain.info/rawblock/" + block_hash
    return str2Object(NetIO.readDataFrom(url))


def transactionQuery(tx_hash):
    url = "https://blockchain.info/rawtx/" + tx_hash
    return str2Object(NetIO.readDataFrom(url))


def blockHeight(block_height):
    url = "https://blockchain.info/block-height/" + str(block_height) + "?format=json"
    return str2Object(NetIO.readDataFrom(url))


def balanceQuery(address):
    # Multiple Addresses Allowed separated by "|" , Address can be base58 or xpub
    url = "https://blockchain.info/balance?active=" + address
    #return NetIO.readDataFrom(url)
    return str2Object(NetIO.readDataFrom(url))


def addressQuery(address):
    url = "https://blockchain.info/rawaddr/"+address
    return str2Object(NetIO.readDataFrom(url))


def addressesQuery(addresses):
    query = ''
    for add in addresses:
        query += add + "|"
    url = "https://blockchain.info/multiaddr?active=" + query[0:-1]
    return str2Object(NetIO.readDataFrom(url))


def unspentOutput(address, limit=250, confirmNum=6):
    # Multiple Addresses Allowed separated by "|" , Address can be base58 or xpub

    if limit > 1000:
        limit = 1000
    url = "https://blockchain.info/unspent?active=" + address + "&limit=" + str(limit) + "&confirmations=" + str(
        confirmNum)
    return str2Object(NetIO.readDataFrom(url))




###################################################
        # The following function will read data from www.walletexplorer.com

# query transaction from walletExplorer
  #
    # {
    #     "txid": ,
    #     "block":,
    #     "time":,
    #     "sender":,
    #     "fee":,
    #     "input":[{"key":value,"amount":value,"prev":value},{"key":value}],
    #     "output":{{"receiver1":[{"key",value,"amount":value,"next":}],"receiver2":[{},{}]}}
    # }

# return an object of transaction given transaction id
def transactionWalletQuery(txid):
    result = {}
    rawdata = NetIO.readDataFrom("https://www.walletexplorer.com/txid/" + txid)
    soup = BeautifulSoup(rawdata, "lxml")
    # soup.find('table',class_="info")
    info = soup.find('table', class_="info").get_text()
    sender_wallet_id = soup.find('table', class_="info").find("a")
    try:
        sender_wallet_id = str(sender_wallet_id["href"])[8:]
    except:
        sender_wallet_id = "Multiple"

    #print(sender_wallet_id)
    # print(info)
    pattern_block = re.compile(r"block[0-9]+")
    pattern_time = re.compile(r"Time[^a-z]+")

    block = int(pattern_block.search(info).group()[5:])
    block_col = int(find_between(info,"(pos ",")"))
    time = pattern_time.search(info).group()


    fee = float(find_between(info, "Fee", "BTC"))
    size = int(find_between(info,"Size"," bytes"))
    # print(block,time,sender,fee)
    result["included_in_block"] = (block,block_col)

    date = datetime.strptime(time[4:-1], '%Y-%m-%d %H:%M:%S')
    #time_tool.mktime(date.timetuple())
    result["time"]=int(time_tool.mktime(date.timetuple()))
    result["sender"] = sender_wallet_id
    result["fee"] = fee
    result["txid"] = txid
    result["size"]=size

    inout = soup.find_all('table', class_="empty")
    inAddress = inout[0]
    outAddress = inout[1]

    all_line = inAddress.find_all("tr")
    input_list = []
    for line in all_line:
        cols = line.find_all("td")
        try:
            public_add = cols[0].find('a').get_text()
        except:
            public_add="NONE"
        value = float(find_between(">" + cols[1].get_text(), ">", "BTC"))

        pre = find_between(str(cols[2]), "txid/", '">')
        input_list.append({"publickey": public_add, "amount": value, "prev_tx_id": pre})
    result["inputs"] = input_list
    all_line = outAddress.find_all("tr")


    my_set = []
    for line in all_line:
        cols = line.find_all("td")
        try:
            public_add = cols[0].find('a').get_text()
        except:
            #print("Not valid transaction:",txid)
            public_add = "NONE"
        wallet_id = find_between(str(cols[1]), "wallet/", '">')

        value = float(find_between(">" + cols[2].get_text(), ">", "BTC"))
        next = find_between(str(cols[3]), "/txid/", '">')
        if next == "":
            next = "NONE"
        my_set.append({"wallet_id":wallet_id,"publickey": public_add, "amount": value, "next_tx_id": next})


    result["outputs"] = my_set
    return result

# return the wallet id that the public address belongs to
def findWalletByAddre(address):
    url='https://www.walletexplorer.com/address/'+address
    data= NetIO.readDataFrom(url)
    leading = 'part of wallet <a href="/wallet/'
    pattern=re.compile(r'part of wallet <a href="/wallet/[^>]+')
    match = re.search(pattern, data)
    addre = match.group()
    #print(addre)
    return addre[len(leading):-1]

# return a list of all wallet id of given type on "https://www.walletexplorer.com/"
def getAllWallet(Wtype="Exchanges"):
    url = "https://www.walletexplorer.com/"
    result = []

    data = NetIO.readDataFrom(url)
    # print(data)

    info = find_between(data, "<h3>" + Wtype, "</ul>")

    match = True
    pattern = re.compile(r'"/wallet/[^>]+')
    flag = 0
    while match:

        match = pattern.search(info, flag)
        if (match):
            result.append(match.group()[9:-1])
            # print(match.group())
            flag = int(match.span()[-1])


        else:
            break
    return result



# print(findWalletByAddre("12t9YDPgwueZ9NyMgw519p7AA8isjr6SMw"))
# print(findWalletByAddre("13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94"))
#
# print(findWalletByAddre("115p7UMMngoj1pMvkpHijcRdfJNXj6LrLn"))

# result = transactionWalletQuery("d238e1e3533ee75e55b64ba1a5a0cf73a9fb87150ac97621a72d300d3ff157c7")
# print({result["txid"]:result})