import Configurations
from updater.Update_System import GithubDownloader
from updater.Util import checkInternetConnection

url = "https://api.github.com/repos/NLSS-Engineering/21005_Medical_Tube_Capping/releases/latest"


def startup_update():
    if checkInternetConnection():
        gd = GithubDownloader(url, encrypted=True, auto_download=True, path='./', unzip_path="./Files/EXTRACT/")
        # RELEASE: unzip path ve path girilmeyecek
        # gd.download()  # if AutoDownload is True, it's not necessary
        if gd.is_new_version():
            # change screen to update screen
            pass
        gd.upgrade_system()


if __name__ == "__main__":
    if not Configurations.DEV_MOD:
        startup_update()
