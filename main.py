import os
import praw
import youtube_dl
from pathlib import Path
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from datetime import timedelta
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

## Praw setup

reddit = praw.Reddit(client_id = os.environ.get("CLIENT_ID"),
					client_secret = os.environ.get("CLIENT_SECRET"),
					username = "video--bot",
					password = os.environ.get("PASSWORD"),
					user_agent = "foo"
					)

## Config
subreddit = reddit.subreddit("idiotsincars")
directoryToUse = "Videos"
limit = 5

posts = subreddit.top(time_filter = "week")

print("\n\n\nSTARTED\n\n\n")

videoPosts = 0
videoUrls = []
videos = []
authors = []
targetLength = 60 # 8 Minutes
currentLength = 0
dateString = datetime.now().strftime("%y-%m-%d")
for post in posts:
	if post.is_video and currentLength < targetLength:
		videoPosts += 1
		#str("_".join(post.title.split()[0:10]).replace(" ","_"))
		outputName = directoryToUse + "/" + dateString + "/Clips/" + str(post) +".mp4"
		videos.append([outputName,post.author])

		if Path(outputName).is_file():
			print("File already exists, skipping")
		else:
			opts = {
			"outtmpl":outputName,
			"quiet":True
			}
			with youtube_dl.YoutubeDL(opts) as ydl:
				ydl.download([post.url])

		length = VideoFileClip(outputName).duration
		authors.append(["u/"+post.author.name,timedelta(seconds=round(currentLength,0))])

		currentLength += length
		print("Downloaded "+str(post.url) + " - " + str(round(length,2)) + " seconds [" + str(currentLength) + "s Total]")



clips = []
for currentVideo in videos:
	video = VideoFileClip(currentVideo[0], target_resolution=(480, None))
	clips.append(video)

final_clip = concatenate_videoclips(clips, method = "compose")
outputFile = directoryToUse + "/" + dateString + "/exported.mp4"
final_clip.write_videofile(outputFile)

for author in authors:
	print(str(author[1]) + " " + author[0])