# Youtube_Video_Downloader With Flask

This is a Youtube downloader script written in python which is capable of downloading all shorts and full video From youtube and if flagged then can extract and download audio from the videos .. its free of cost and is simple example created with flask which adds some magic in it ....

>>--> this is a general way of downloading a YouTube video to downloads directory for free you can download shots and full video
>>--> your preferred picture quality and with or without video ie only audio
>>--> the program uses "https://yt5s.biz/en/youtube-to-mp4" to download videos or audios in required qualities if not present then
>>--> the maximum quality present
>>--> it is using flask to take user input in the form of
>>--> http://127.0.0.1/download?url=https://www.youtube.com/shorts/nHx4vzrpgiA&quality=1080&only-audio=False keep it false to download video
>>--> but make it true to download only audio
>>--> #Caution if you require it in the 360p it is downloaded in the downloads folder in the same directory and on the webpage
>>--> there is a link to watch the video online .........

# Pre requirements 
>--> Flask
>--> Requests
>--> PlayWright

# Instructions
>--> as stated earlier the format of the link will be like this "http://127.0.0.1/download?url=https://www.youtube.com/shorts/nHx4vzrpgiA&quality=1080&only-audio=False" and it should be same for both audio and video 
>--> the Parameter only-audio will tell the program to download with or without video 
>--> if it is 'True' this means only audio is downloaded
>--> if it is 'False' this means both video is downlaoded 
>--> url is required and other parameters are optional to 720 and False i.e. both audio and video 
>--> While executing the script if you want to make the selenium part in background use the feature 'headless=True' which causes the fucntion to run in background
>--> Also take care of the errors which might crept in the function which could hardly detectable errors .. Thankyou..

# Youtube Video Downloader API
This is a youtube downlaoder api which is capable of downlaoding video or audio from any youtube or youtube shots link with some hidder browser automations and webpage scapping.. the tools used it his are of new and less knows so it was fun creating this..

>USES : they are mention in main function also but just for sake of ease
>> ### from Youtube_Downloader import Downloader
>> #### yt = Downloader()
>> #### yt.download(url, quality, onlyaudio?(boolean), automatic downlaod in download folder(boolean))

## don't paste this this explains how paramteres are to be given . thankyou

# Pre requirements 
>--> Requests
>--> PlayWright
