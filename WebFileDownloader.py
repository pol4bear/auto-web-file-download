import os
import requests
import requests.exceptions
from requests.exceptions import RequestException
from http import HTTPStatus
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class FileAutoDownloader:
    def __init__(self, url, out):
        self.url = url
        parsedUrl = urlparse(url)
        self.hostname = parsedUrl.hostname
        self.startPath = parsedUrl.path
        if self.startPath == '':
            self.startPath = '/'
        self.hostname = parsedUrl.scheme + "://" + self.hostname

        self.out = out
        self.createDirectory(self.out)
        if self.out[-1:] != "/":
            self.out += "/"

    def download(self):        
        try:
            response = requests.get(self.url)

            if response.status_code == HTTPStatus.OK:

                if response.headers['content-type'].find('text/html') != -1:
                    if response.text.find('Index of'):
                        self.makeDownload(self.startPath)
                    else:
                        print("[!] 디렉토리 리스팅된 페이지가 아닙니다.")
                else:
                    print("[!] 디렉토리 리스팅된 페이지가 아닙니다.")
            elif response.status_code == HTTPStatus.NOTFOUND:
                print('[!] ' + url + ' 페이지를 찾을 수 없습니다.')
            else:
                print('[!] 페이지가 ' + httplib.responses[response.status_code] + '를 응답했습니다.')
        except ConnectionError as e:
            print('[!] 인터넷 연결을 확인하세요.')
        except (requests.exceptions.HTTPError, requests.exceptions.TooManyRedirects) as e:
            print('[!] 정상적이지 않은 사이트에 요청하고 있습니다.')
        except requests.exceptions.Timeout:
            print('[!] 사이트가 요청에 응답하지 않습니다.')
        except requests.exceptions.InvalidURL:
            print('[!] URL을 확인해주세요.')

    def createDirectory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def makeDownload(self, curPath):
        response = requests.get(self.hostname + curPath)

        bs = BeautifulSoup(response.content, 'html.parser')
        files = bs.find_all("a")

        for file in files:
            path = file["href"]

            if path[0] != '?':
                childResponse = requests.head(self.hostname + curPath + path)
                
                try:
                    if childResponse.headers['content-type'].find('text/html') != -1:
                        if len(path) > len(curPath):
                            childResponse = requests.get(self.hostname + curPath + path)

                            if childResponse.text.find('Index of'):
                                print("[+] Found directory " + curPath + path)
                                self.createDirectory(self.out + curPath + path)
                                self.makeDownload(curPath + path)
                            else:
                                self.storeFile(curPath + path, data)
                    else:
                        self.downloadFile(curPath + path)
                except KeyError:
                    self.downloadFile(curPath + path)

    def downloadFile(self, path):
        url = self.hostname + "/" + path
        try:
            mem = urllib.request.urlopen(url).read()
        except Exception:
            print(Exception)
        self.storeFile(path, mem)

    def storeFile(self, path, data):
        if self.out[-1] == '/' and path[0] == '/':
            self.out = self.out[:-1]
        with open(self.out + urllib.parse.unquote(path), mode="wb") as f:
            f.write(data)
        print("[+] " + path + " stored")


def main():
    url = input("웹 디렉토리의 URL을 입력해주세요: ")
    if url.find("://") == -1:
        protocolFlag = False

        while protocolFlag == False:
            protocol = input("프로토콜을 입력하세요(http or https): ")
            if protocol.find("https") != -1:
                protocol = "https://"
                protocolFlag = True
            elif protocol.find("http") != -1:
                protocol = "http://"
                protocolFlag = True

        url = protocol + url

    downloader = FileAutoDownloader(url, "downloads")
    downloader.download()


if __name__ == "__main__":
    main()