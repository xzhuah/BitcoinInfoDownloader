from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager,Screen,FadeTransition
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
import time
import threading
from kivy.factory import Factory
import CenterDownloader as downloader
import DetailedTransactionDownloader
import WalletTransactionDownloader
import WalletPkDownloader
from kivy.core.window import Window
Window.clearcolor = (0.94, 0.94, 0.94, 1)

download_Task=""
all_task=["All In One","Wallet Public Key","Wallet Transaction","Detailed Transaction"]


class DownloaderScreen(Screen):

    global download_Task

    loadfile = ObjectProperty(None)

    def checkboxE(self):
        h="You are about to download "+ download_Task
        if(self.ids.cb_text.active):
            h+=" \nwith wallet id input, make sure you split your id with comma"
        else:
            h+=" \nwith file input, make sure your file has the correct format"
            h+=" \nFor wallet level transaction, every line of your file should be an url to a csv file \nlike this:https://www.walletexplorer.com/wallet/Poloniex.com?page=2&format=csv"
            h+=" \nFor Detailed transaction, every line should be an transaction id"

        self.showHint(h)



    def updateProgressInner(self,ClassName, pb, btn):

        while (ClassName.finish == False):
            if (isinstance(pb, ProgressBar)):
                print(pb.value, ClassName.flag, ClassName.total_task)
                pb.value = int(ClassName.flag / ClassName.total_task * 1000)
                print(pb.value)
            time.sleep(1)
        if (isinstance(pb, ProgressBar)):
            pb.value = int(ClassName.flag / ClassName.total_task * 1000)
        if (isinstance(btn, Button)):
            btn.disabled = False
    def showHint(self,text):
        self.ids.hint.text=text
    def updateProgress(self,value=0):
        self.ids.progress.value=value
    def downloadTask(self):
        global download_Task
        print(download_Task)
        if(self.ids.cb_text.active):
            # wallet_id
            self.showHint(self.ids.ti_walletid.text)
            self.ids.ti_walletid.text=self.ids.ti_walletid.text.strip()
            all_wallets=self.ids.ti_walletid.text.split(",")
            self.showHint(str(len(all_wallets))+" wallet id detected")
            for w in all_wallets:
                if(w==""):
                    self.showHint("Your input contains invalid id or no id, a typical wallet id should be something like: e50412ea016424be or Poloniex.com")
                    return

            if(download_Task==all_task[0]):
                self.ids.download_btn.disabled = "True"
                main_thred = threading.Thread(target= downloader.main,args=[all_wallets,self.ids.download_btn,self.ids.hint])
                progress_monitor = threading.Thread(target= self.updateProgressInner,args=[DetailedTransactionDownloader,self.ids.progress,""])
                progress_monitor.start()
                main_thred.start()


            elif(download_Task==all_task[1]):
                self.ids.download_btn.disabled = "True"
                main_thred = threading.Thread(target=downloader.downloadWalletPK, args=[all_wallets,self.ids.download_btn,self.ids.hint])
                progress_monitor = threading.Thread(target=self.updateProgressInner,
                                                    args=[WalletPkDownloader, self.ids.progress,""])
                progress_monitor.start()
                main_thred.start()
            elif(download_Task==all_task[2]):
                self.ids.download_btn.disabled = "True"
                main_thred = threading.Thread(target=downloader.downloadWalletTransaction, args=[all_wallets,self.ids.download_btn,self.ids.hint])
                progress_monitor = threading.Thread(target=self.updateProgressInner,
                                                    args=[WalletTransactionDownloader, self.ids.progress,""])
                progress_monitor.start()
                main_thred.start()
            elif(download_Task==all_task[3]):
                self.showHint("Detailed Transaction downloading does not support wallet id as input, please load a file")
            else:
                self.showHint("Download Task: " + download_Task + " not valid")
        else:
            # file
            self.showHint(self.ids.file_path_label.text)
            if(not self.ids.file_path_label.text.endswith(".csv")):
                self.showHint(self.ids.file_path_label.text+" is not a valid csv file. Please load a valid csv file")
                return
            if (download_Task == all_task[0]):
                self.showHint("All in one does not support file loading")
            elif (download_Task == all_task[1]):
                self.showHint("wallet public key does not support a file input")
            elif (download_Task == all_task[2]):
                self.ids.download_btn.disabled = "True"
                main_thred = threading.Thread(target=downloader.downloadWalletTransactionByURL, args=[self.ids.file_path_label.text,self.ids.download_btn,self.ids.hint])
                progress_monitor = threading.Thread(target=self.updateProgressInner,
                                                    args=[WalletTransactionDownloader, self.ids.progress,""])
                progress_monitor.start()
                main_thred.start()
            elif (download_Task == all_task[3]):
                self.ids.download_btn.disabled = "True"
                main_thred = threading.Thread(target=downloader.downloadDetails, args=[self.ids.file_path_label.text,self.ids.download_btn,self.ids.hint])
                progress_monitor = threading.Thread(target=self.updateProgressInner,
                                                    args=[DetailedTransactionDownloader, self.ids.progress,""])
                progress_monitor.start()
                main_thred.start()
            else:
                self.showHint("Download Task: "+download_Task + " not valid")



    def dismiss_popup(self):

        self._popup.dismiss()

    def load(self, path):
        print(path[0])##Get path here
        self.ids.file_path_label.text=path[0]

        self.dismiss_popup()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def checkState(self):
        self.checkboxE()
        if(self.ids.cb_text.active):
            self.ids.ti_walletid.disabled=False
            self.ids.btn_load.disabled = True
        else:
            self.ids.ti_walletid.disabled = True
            self.ids.btn_load.disabled = False





class DownloadChooser(Screen):
    global download_Task
    def listen(self,btn):
        global download_Task
        if isinstance(btn,Button):
            download_Task=btn.text
            self.manager.current="downloader"
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)





class ScreenManagement(ScreenManager):
    pass

class MainGUI(App):
    def __int__(self):
        super(MainGUI,self).__init__()

    def build(self):
        self.title = "Bitcoin Information Downloader"
        return ScreenManagement()

Factory.register('MainGUI', cls=MainGUI)
Factory.register('LoadDialog', cls=LoadDialog)

if __name__=="__main__":
    MainGUI().run()