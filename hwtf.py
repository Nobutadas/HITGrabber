import praw, time, datetime, jsonpickle, requests, feedparser, re, sys
from BeautifulSoup import BeautifulSoup


mturkpost = "None"
oldHits = []
currentTitle = "None"

class newpost:
	def __init__(self,title,url,utcTimestamp,source,html):
		self.title = title
		self.url = url
		self.utcTimestamp = utcTimestamp
		self.source = source
		self.html = html

def isDup(newTitle):
	global currentTitle
	matchlist = list(set(currentTitle.split(" ")) & set(newTitle.split(" ")))
	if len(matchlist) > 3:
		print("Duplicate found")
		return True
	else:
		currentTitle = newTitle
		return False

		
def mturkForumSearch():
	try:
		global mturkpost
		feed = feedparser.parse('http://mturkforum.com/external.php?type=RSS2&forumids=30')
		url = feed.entries[0].link
		soup = BeautifulSoup(requests.get(url).content)
		posts = soup.findAll('div', {'class':re.compile('cms_table')})
		if len(posts) > 0:
			for post in posts[-1]:
				post = str(post).replace('"',"'")
				title = soup.find("font").text
				if post != mturkpost:
					print("MturkForum: New post was made \n ---------------------------------")
					updateJsonFiles("New HIT from MturkForum.com. Check main notifier page for details", url,"mturkforum.com",post)
					mturkpost = post

	except Exception:
		print("An error has occured in mturkForumSearch")
			
					
def updateJsonFiles(title, url, source, html):
	try:
		global oldHits
		utcTimestamp = str(datetime.datetime.utcnow()) + "Z"
		currentJSON = open("post.json","w")
		currentJSON.truncate
		JSONObject = jsonpickle.encode(newpost(title,url, utcTimestamp, source, html))
		currentJSON.write(JSONObject)
		currentJSON.close()
		
		if len(oldHits) >= 15:
			del oldHits[0]
			
		oldHits.append(newpost(title,url, utcTimestamp, source, html))
		oldPosts = open('oldPosts.json','w')
		oldPosts.truncate
		oldPosts.write(jsonpickle.encode(oldHits))
		oldPosts.close()

	except Exception:
		print("An error occured while trying to update JSON files")

#### Reddit Configuration options ####
USERNAME = ''
PASSWORD = ''
LIMIT = 1
SUBREDDIT = 'hitsworthturkingfor'
#### End Configuration Options ####

r = praw.Reddit(user_agent='Made by /u/retardeted to grab the latest hits from /r/hitsworthturkingfor')
r.login(USERNAME,PASSWORD, disable_warning=True)
alreadyDone = set()

print("Starting HitHat Notifier...\n")
while True:
    try:
        subreddit = r.get_subreddit(SUBREDDIT).get_new(limit=LIMIT)
        for post in subreddit:
            if post.id not in alreadyDone:
            	alreadyDone.add(post.id)
            	#if isDup(post.title) != True:
		updateJsonFiles("/r/hwtf: " + post.title,post.url,'/r/hitsworthturkingfor','none')
		print("HWTF: " + post.title + "\n ---------------------------------")

    except Exception:
        print("An error occured while getting hits from /r/hitsworthturkingfor")

    mturkForumSearch()
    time.sleep(30)
