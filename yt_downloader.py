#this is a general way of downloading a YouTube video to downloads directory for free you can download shots and full video
#your preferred picture quality and with or without video ie only audio
#the program uses "https://yt5s.biz/en/youtube-to-mp4" to download videos or audios in required qualities if not present then
#the maximum quality present
#it is using flask to take user input in the form of
#http://127.0.0.1/download?url=https://www.youtube.com/shorts/nHx4vzrpgiA&quality=1080&only-audio=False keep it false to download video
#but make it true to download only audio
####Caution if you require it in the 360p it is downloaded in the downloads folder in the same directory and on the webpage
#there is a link to watch the video online .........

from playwright.sync_api import sync_playwright
import requests #to directly download video from the link
from flask import Flask, request, jsonify,render_template
import time
import re
app = Flask(__name__)

def sanitize_name(filename):#need of sanitizing is there because when saving the file the name is causing error
    # Remove any character that is not a letter, number, space, or common punctuation
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_video_withLink(video_url, save_path,name):#direclty download the video with the link
    # Send GET request to download the video
    #naming the file
    name = sanitize_name(name)
    save_path = f"{save_path}/{name}.mp4"
    response = requests.get(video_url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Video downloaded to {save_path}")
        return "Video Downloaded"
    return "Failed to download video"


def start_download(target_url,Render_quality,only_audio=False):
    with sync_playwright() as playwright:
        # Launch browser instance
        browser = playwright.chromium.launch(headless=False)  # Set headless=True for background execution
        page = browser.new_page()
        page.on("dialog", lambda dialog: dialog.dismiss())#handles any alert on the page
        # Go to a URL
        baseUrl = "https://yt5s.biz/en/youtube-to-mp4"
        page.goto(baseUrl)

        # Functions
        page.fill("input[name=query]", target_url)
        page.click("#btn-submit")
        time.sleep(3)
        #it will wait for some time for loading the table of video and audio
        page.wait_for_selector(".tabs.row")

        #now my tables with video link have appeared
        if not only_audio:#user want both audio and video
            #by default the page is set to download videos
            isDownloadInitiated = False
            special_360p_download = False
            rows = page.query_selector_all("table.table-bordered.table-hover.table-responsive-sm")
            skip = 1 #skips first iteration
            for row in rows[0].query_selector_all("tr"):
                if skip==1 :
                    skip=0
                    continue
                columns = row.query_selector_all("td")

                if len(columns) < 3:
                    continue

                quality = columns[0].inner_text()
                quality = quality.split('p')[0].strip()

                #checking for 360p edge case
                if quality.__eq__('360') and Render_quality==quality:#special 360p case
                    link = columns[2].query_selector(".btn.btn-sm.btn-success").get_attribute("href")
                    name_of_the_video = page.query_selector("#video_title").inner_text()
                    result = download_video_withLink(link,"downloads",name_of_the_video)
                    if result=="Video Downloaded":
                        return{
                            'name_of_the_video': name_of_the_video,
                            'watch_online': f'<a href="{link}" target="_blank">Click here to watch online</a>',
                            'Location' : 'The Video is downloaded in the the downloads folder in same directory',
                            'quality': quality,
                        }
                    return{
                        'error' : 'Video Downloading has failed due to unknown reasons',
                        'solutions' : 'Either retry or check your parameters or try again later'
                    }

                #video is not of 360p type therefore continue as usual
                if quality == Render_quality:
                    button = columns[2].query_selector(".btn.btn-sm.btn-success")
                    try:#downloading with the said link
                        button.click()
                        isDownloadInitiated = True
                        break
                    except Exception as e:
                        print("Alert Occurred or something!")
                        continue

            if not isDownloadInitiated :#downloading the highest quality possible
                #because the said quality is not present
                skip=1
                for row in rows[0].query_selector_all("tr"):
                    if skip==1 :
                        skip=0
                        continue
                    columns = row.query_selector_all("td")
                    quality = columns[0].inner_text()
                    quality = quality.split('p')[0].strip()

                    if quality.__eq__('360') :#rare case when only 360p is available for download
                        link = columns[2].query_selector(".btn.btn-sm.btn-success").get_attribute("href")
                        name_of_the_video = page.query_selector("#video_title").inner_text()
                        result = download_video_withLink(link, "downloads", name_of_the_video)
                        if result == "Video Downloaded":
                            return {
                                'name_of_the_video': name_of_the_video,
                                'watch_online': f'<a href="{link}" target="_blank">Click here to watch online</a>',
                                'Location' : 'The Video is downloaded in the the downloads folder in same directory',
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

            if not special_360p_download:#now popup will appear but for 360p popup does not appear which is handled
                page.wait_for_selector(".modal-content")
                name_of_video = page.query_selector(".modal-header h4").inner_text()
                dwnld_Link = page.query_selector(".modal-body a").get_attribute("href")
                browser.close()
                return {
                    'name_of_the_video': name_of_video,
                    'download_link': f'<a href="{dwnld_Link}" target="_blank">Click here to download</a>',
                    'quality': Render_quality,
                    'Location' : 'This will download into you default downloads directory'
                }

        #now extract the audio from the link and give download link
        audio_page = page.query_selector_all('.nav-item.p-0.col-6')[1]
        audio_page.query_selector("a").click()#switches to download audio
        # get the <tr> of this class
        rows = page.query_selector_all("table.table-bordered.table-hover.table-responsive-sm")
        skip=1
        for row in rows[1].query_selector_all("tr"):
            if skip==1:
                skip=0
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
        browser.close()
        return {
            'name_of_the_audio': name_of_audio,
            'download_link': f'<a href="{dwnld_Link}" target="_blank">Click here to download</a>',
            'quality': Render_quality,
            'Location': 'This will download into you default downloads directory'
        }


# Flask route for downloading video
@app.route('/download', methods=['GET'])
def download():
    yt_url = request.args.get('url')
    quality = request.args.get('quality', default=720)  # Default quality is 1080p
    only_audio = request.args.get('only-audio', default=False).lower() == 'true'
    if not yt_url:
        return jsonify({'error': 'x`URL is required'}), 400

    try:
        # Call the Playwright function to get the download link
        result = start_download(yt_url, quality, only_audio)
        if not only_audio:#video
            downld_link = result.get('download_link','not found')
            if downld_link == 'not found':
                downld_link = result.get('watch_online')
            return render_template('video_download.html',
                                   name_of_the_video=result['name_of_the_video'],
                                   quality=result['quality'],
                                   download_link=downld_link,
                                   location=result['Location'])
        #audio
        return render_template('audio_download.html',
                               name_of_the_audio=result['name_of_the_audio'],
                               quality=result['quality'],
                               download_link=result['download_link'],
                               location=result['Location']
        )
        #return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)

