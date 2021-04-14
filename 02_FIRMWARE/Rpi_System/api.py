from Update_System import GithubDownloader
from Util import checkInternetConnection


url = "https://api.github.com/repos/NLSS-Engineering/21005_Medical_Tube_Capping/releases/latest"


if checkInternetConnection():
    gd = GithubDownloader(url, encrypted=True, auto_download=True, path='.', unzip_path="Files/EXTRACT/")
    # gd.download()  # if AutoDownload is True, it's not necessary
    if gd.is_new_version():
        # change screen to update screen
        pass
    gd.upgrade_system()
