#this is a YouTube Downloader API which can download both audio and video(with audio) in requested quality efficiently
#this can be helpful for later projects at least for me it is ...
#this is created and modified by Mr. Maheshwar a student of CSJMU First Year B.TECH in CSE
#this is just a prototype in later version QR code of the links will also be available
#also some changes are required in logic such as controlling the downloading of 360p video and,
#if the video is downloaded earlier with same quality it should not be downloaded again
import os
from googleapiclient.mimeparse import quality#this can be used to check the quality of a media but for me of no use.. till now
from playwright.sync_api import sync_playwright
import requests #to directly download video from the link
import time
import re

class Downloader:
    #there was no need of init function

    @staticmethod
    def sanitize_name(filename):  # need of sanitizing is there because when saving the file the name is causing error
        # Remove any character that is not a letter, number, space, or common punctuation
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def download_withLink(self,url_, save_path_folder, name,red_quality):  # directly download the video/audio with the link
        #print(red_quality)
        # Send GET request to download the video
        # naming the file
        name = self.sanitize_name(name)
        cwd = os.getcwd()
        file_url = ''
        save_path = os.path.join(cwd,f"{save_path_folder}",f"{name}_{red_quality}.mp4")
        if red_quality.__eq__('360'):  #for 360p the download link gives a html response.. handling that

            response = requests.get(url_)#this gives a html response which contains the video url
            # Use regex to find the URL within the var url definition in html response
            url_pattern = r'var url = "(https?://[^\"]+)"'

            # Search for the URL in the response
            match = re.search(url_pattern, response.text)
            file_url = match.group(1)
        else :
            file_url = url_

        if red_quality.__eq__('MP3'):#it means it is an audio
            save_path = os.path.join(cwd,f"{save_path_folder}",f"{name}_{red_quality}.mp3")

        link_response = requests.get(file_url, stream=True)
        #print(match.group(1)) # match.group(1) it contains the extracted url
        # Check if the request was successful
        if link_response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in link_response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            print(f"downloaded to {save_path}")
            return "!!Download Success!!",file_url
        return "!!Download Failed!!"

    def startDownload(self,target_url,Render_quality,only_audio=False):
        with sync_playwright() as playwright:
            # Launch browser instance
            self.browser = playwright.chromium.launch(headless=True)  # Set headless=True for background execution
            page = self.browser.new_page()
            page.on("dialog", lambda dialog: dialog.dismiss())  # handles any alert on the page
            # Go to a URL
            self.baseUrl = "https://yt5s.biz/en/youtube-to-mp4"
            page.goto(self.baseUrl)

            # Functions
            page.fill("input[name=query]", target_url)
            page.click("#btn-submit")
            time.sleep(3)
            # it will wait for some time for loading the table of video and audio
            page.wait_for_selector(".tabs.row")

            # now my tables with video link have appeared
            if not only_audio:  # user want both audio and video
                # by default the page is set to download videos
                self.isDownloadInitiated = False
                self.special_360p_download = False
                rows = page.query_selector_all("table.table-bordered.table-hover.table-responsive-sm")
                skip = 1  # skips first iteration
                for row in rows[0].query_selector_all("tr"):
                    if skip == 1:
                        skip = 0
                        continue
                    columns = row.query_selector_all("td")

                    if len(columns) < 3:
                        continue

                    quality = columns[0].inner_text()
                    quality = quality.split('p')[0].strip()

                    # checking for 360p edge case
                    if quality.__eq__('360') and Render_quality == quality:  # special 360p case
                        link = columns[2].query_selector(".btn.btn-sm.btn-success").get_attribute("href")
                        name_of_the_video = page.query_selector("#video_title").inner_text()
                        result,link = self.download_withLink(link, "downloads", name_of_the_video,quality)
                        if result == "!!Download Success!!":
                            return {
                                'name_of_the_video': name_of_the_video,
                                'watch_online': link,
                                'Location': 'The Video is downloaded in the the downloads folder in same directory',
                                'quality': quality,
                            }
                        return {
                            'error': 'Video Downloading has failed due to unknown reasons',
                            'solutions': 'Either retry or check your parameters or try again later'
                        }

                    # video is not of 360p type therefore continue as usual
                    if quality == Render_quality:
                        button = columns[2].query_selector(".btn.btn-sm.btn-success")
                        try:  # downloading with the said link
                            button.click()
                            self.isDownloadInitiated = True
                            break
                        except Exception as e:
                            print("Alert Occurred or something!")
                            continue

                if not self.isDownloadInitiated:  # downloading the highest quality possible
                    # because the said quality is not present
                    skip = 1
                    for row in rows[0].query_selector_all("tr"):
                        if skip == 1:
                            skip = 0
                            continue
                        columns = row.query_selector_all("td")
                        quality = columns[0].inner_text()
                        quality = quality.split('p')[0].strip()

                        if quality.__eq__('360'):  # rare case when only 360p is available for download
                            link = columns[2].query_selector(".btn.btn-sm.btn-success").get_attribute("href")
                            name_of_the_video = page.query_selector("#video_title").inner_text()
                            result,link = self.download_withLink(link, "downloads", name_of_the_video,quality)
                            if result == "!!Download Success!!":
                                return {
                                    'name_of_the_video': name_of_the_video,
                                    'watch_online': link,
                                    'Location': 'The Video is downloaded in the the downloads folder in same directory',
                                    'quality': quality,
                                }
                            return {
                                'error': 'Video Downloading has failed due to unknown reasons',
                                'solutions': 'Either retry or check your parameters or try again later'
                            }

                        if len(columns) < 3:
                            continue
                        button = row.query_selector_all("td")[2].query_selector(".btn.btn-sm.btn-success")
                        try:
                            button.click()
                            Render_quality = columns[0].inner_text().split('p')[0].strip()
                            break
                        except Exception as e:
                            print("Alert Occurred or something!")
                            continue

                if not self.special_360p_download:  # now popup will appear but for 360p popup does not appear which is handled
                    page.wait_for_selector(".modal-content")
                    name_of_video = page.query_selector(".modal-header h4").inner_text()
                    dwnld_Link = page.query_selector(".modal-body a").get_attribute("href")
                    self.browser.close()
                    return {
                        'name_of_the_video': name_of_video,
                        'download_link': dwnld_Link,
                        'quality': Render_quality,
                        'Location': 'This will download into you default downloads directory'
                    }

            # now extract the audio from the link and give download link
            audio_page = page.query_selector_all('.nav-item.p-0.col-6')[1]
            audio_page.query_selector("a").click()  # switches to download audio
            # get the <tr> of this class
            rows = page.query_selector_all("table.table-bordered.table-hover.table-responsive-sm")
            skip = 1
            for row in rows[1].query_selector_all("tr"):
                if skip == 1:
                    skip = 0
                    continue
                columns = row.query_selector_all("td")

                if len(columns) < 3:
                    continue

                quality = columns[0].inner_text()

                button = columns[2].query_selector(".btn.btn-sm.btn-success")
                try:
                    button.click()
                    Render_quality = quality
                    break
                except Exception as e:
                    print("Alert Occurred or something!wow")
                    continue

            page.wait_for_selector(".modal-content")
            name_of_audio = page.query_selector(".modal-header h4").inner_text()
            dwnld_Link = page.query_selector(".modal-body a").get_attribute("href")
            self.browser.close()
            return {
                'name_of_the_audio': name_of_audio,
                'download_link': dwnld_Link,
                'quality': Render_quality,
                'Location': 'This will download into you default downloads directory'
            }

    def getLink(self,target_url, Render_quality, only_audio=False):# to reduce human effort
        response = self.startDownload(target_url, Render_quality, only_audio)

        nameKey= list(response.keys())[0]#extracts the name of the vide
        name = response[nameKey]# extracts the name from the response

        qualityKey = list(response.keys())[2]
        if not qualityKey.__eq__('quality'):
            qualityKey = list(response.keys())[3]
        qualty = response[qualityKey] #extract the quality of the video

        download_Link = response.get('download_link', 'not found')
        if download_Link == 'not found':
            download_Link = response.get('watch_online')
            print(
                f"We have downloaded the video inside a ../downloads folder please check there and here is a link to watch online = {download_Link}")
        else:
            if qualty.__eq__('MP3'):
                print(f"The Download Link of The Audio = {download_Link}")
            else :
                print(f"The Download Link of The Video = {download_Link}")
        return download_Link,self.sanitize_name(name),qualty


    def download(self,target_url,Render_quality,only_audio=False,should_Download = False):#peak function which indirectly calls each function
        d_link, f_name, f_quality = self.getLink(target_url, Render_quality, only_audio)  # if the video is asked and required quality is 360p then it is automatically downloaded
        if not f_quality.__eq__('360'): #it's not pre downloaded
            if should_Download:
                try:
                    self.download_withLink(d_link, "downloads", f_name, f_quality)
                    print(f"We have downloaded it {f_name} to ./downloads folder")
                    return d_link,f_name,f_quality,"Success"
                except Exception as e:
                    return d_link,f_name,f_quality,"Failed"




if __name__ == '__main__':
    downloader = Downloader()
    url = 'https://www.youtube.com/shorts/WbSifSn_sXg'
    r_quality = '360'
    downloader.download(url,r_quality,True,True)# for video of 360p ,till now you can not control the downloading
    #here should download parameter deals if the video has to be downloaded or not
    #this also returns 1)download_link , 2) file name ,3) quality in which it has been downloaded and 4)Success or Failed message
    #It can be modified later for returning more information


