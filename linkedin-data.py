import argparse, os, time
import urlparse, random
from selenium import webdriver
from bs4 import BeautifulSoup
import io

"""
	Given a page soure get links of user profiles
	Input: HTML page source
	Output: Links of people profile
"""
def getPeopleLinks(page):
	links = []
	# Find all hyper links
	for link in page.find_all('a'):
		# Get href of hyper link
		url = link.get('href')
		if url:
			# If it contains 'profile/view?id='  add it to result list
			if 'profile/view?id=' in url:
				links.append(url)
	return links

"""
	Given user profile url, find user id
	Input: User profile url
	Output: User ID
"""
def getUserID(url):
	pUrl = urlparse.urlparse(url)
	return urlparse.parse_qs(pUrl.query)['id'][0]

"""
	Given a page soure get links of job postings
	Input: HTML page source
	Output: Links of job posting
"""
def getJobLinks(page):
	links = []
	# Find all hyper links
	for link in page.find_all('a'):
		# Get href of hyper link
		url = link.get('href')
		if url:		
			# If it contains '/jobs?viewJob=' or 'jobs2/view/' add it to result list
			if '/jobs?viewJob=' in url or 'jobs2/view/' in url:
				links.append(url)
	return links

"""
	Given Job posting url, find job id
	Input: Job posting url
	Output: Job ID
"""
def getJobID(url):
	pUrl = urlparse.urlparse(url)
	try:
		# If jobId is present in state params return jobId from state param
		return urlparse.parse_qs(pUrl.query)['jobId'][0]
	except:
		# Return jobId from path
		path = pUrl.path.split('/')
		return path[len(path)-1]

"""
	Given Job Details, create file in Jobs directory & puts the info
	Input: Job Details
	Output: None
"""
def createJobDetailFile(count, jobTitle, jobCompany, jobLocation, jobDescription):
	fileName = 'jobs/job'+ str(count) + '.txt'
	file = io.open(fileName, 'w', encoding='utf8')
	file.write(jobTitle);
	file.write(jobCompany);
	file.write(jobLocation);
	file.write(jobDescription);
	file.close()

"""
	Given User Details, create file in Users directory & puts the info
	Input: User Details
	Output: None
"""
def createUserDetailFile(count, userName, userHeadLine, userLocation, userSummary, userBackground):
	fileName = 'users/user'+ str(count) + '.txt'
	file = io.open(fileName, 'w', encoding='utf8')
	file.write(userName);
	file.write(userHeadLine);
	file.write(userLocation);
	file.write(userSummary);
	file.write(userBackground);
	file.close()

"""
	Given Browser and count of total people needs to be retrieved, returns people profile data
	Input: Browser control & count of profile
	Output: Files with people profile data
"""
def getPeopleData(browser, total):
	# For no duplication check
	visited = {}
	# User Ids retrieved from links (All pages)
	userList = []
	# To check number of profiles retrieved
	count = 0
	# Wait for initial page to load - 5 sec
	time.sleep(5) 
	print "User Data Retrieval in progress!"
	while count < total:
		# Parsing the page as HTML
		page = BeautifulSoup(browser.page_source, "html.parser")
		# Retrieve all people links from page
		people = getPeopleLinks(page)
		if people:
			# Make list of user Ids
			for person in people:
				ID = getUserID(person)
				if ID not in visited:
					userList.append(person)
					visited[ID] = 1
		if userList: #if there is users to look at look at them
			# Get last added person
			person = userList.pop()
			# Browse to user link 
			browser.get(person)
			# Wait for page to load - 5 sec
			time.sleep(5)
			userPage = BeautifulSoup(browser.page_source, "html.parser")
			# Get user info using xpath (Unique path to the element in HTML)
			try:
				userName = userPage.find(id="top-card").h1.string + '\n'
				userHeadLine = userPage.find(id="headline").string + '\n'
				userLocation = userPage.find(id="location").a.string + '\n'
				userSummary = userPage.find(id="summary-item-view").get_text() + '\n'
				userBackground = ""
				for experience in userPage.find(id="background-experience").find_all('a'):
					userBackground += experience.get_text() + '\n'
				for experience in userPage.find(id="background-experience").find_all('p', { "class" : "description" }):
					userBackground += experience.get_text() + '\n'
				# Create document with retrieved information
				createUserDetailFile(count, userName, userHeadLine, userLocation, userSummary, userBackground)
				count += 1
			except:
				continue
		else:
			print "No More users to look at! Exiting..."
			break
		# Prints status of the retrieved users
		print "(" + str(count) + "/"+ str(total) +" Visited/Queue)"
					

"""
	Given Browser and count of total jobs needs to be retrieved, returns posted job data
	Input: Browser control & count of jobs
	Output: Files with posted job data
"""
def getJobData(browser, total):
	# For no duplication check
	visited = {}
	# Job Ids retrieved from links (All pages)
	jobList = []
	# To check number of jobs retrieved
	count = 0
	print "Job Data Retrieval in progress!"
	# Wait for initial page to load - 5 sec
	time.sleep(5)
	while count < total:
		# Parsing the page as HTML
		page = BeautifulSoup(browser.page_source, "html.parser")
		# Getting job links available on page
		jobs = getJobLinks(page)


		if jobs:
			# Make list of jobIds
			for job in jobs:
				ID = getJobID(job)
				if ID not in visited:
					jobList.append(job)
					visited[ID] = 1
		if jobList:
			# Get latest job url
			job = jobList.pop()
			root = 'http://www.linkedin.com'
			roots = 'https://www.linkedin.com'
			# Check if url contains root url of LinkedIn - (Resolves the issue we were facing due to no root)
			if root not in job:
				if roots not in job:
					continue
			# Opens the job url in browser
			browser.get(job)
			# Wait for page to load - 5 sec
			time.sleep(5)
			# Retrieve job data using xpath 
			try:
				jobPage = BeautifulSoup(browser.page_source, "html.parser")
				jobTitle = jobPage.find(id="top-card").h1.string + '\n'
				jobCompany = jobPage.find(id="top-card").find(itemprop="name").string + '\n'
				jobLocation = jobPage.find(id="top-card").find(itemprop="jobLocation").span.string + '\n'
				jobDescription = jobPage.findAll("div", { "class" : "description-section" })[0].find(itemprop="description").get_text() + '\n'
				createJobDetailFile(count, jobTitle, jobCompany, jobLocation, jobDescription);
				count += 1
			except:
				continue
		else:
			print "Error: No-data - Exiting"
			break
		# Prints the status/count of jobs retrieved
		print "(" + str(count) + "/"+ str(total) +" Visited/Queue)"

def Main():
	# Parsing the arguments from command line
	parser = argparse.ArgumentParser()
	# Argument - Email
	parser.add_argument("email", help="linkedin email")
	# Argument - Password
	parser.add_argument("password", help="linkedin password")
	args = parser.parse_args()

	# Opens Firefox browser
	browser = webdriver.Firefox()

	# Opens LinkedIn login page
	browser.get("https://linkedin.com/uas/login")

	# Gets email/user name text box
	emailElement = browser.find_element_by_id("session_key-login")
	# Puts email argument into the email field
	emailElement.send_keys(args.email)
	# Gets password field from web page
	passElement = browser.find_element_by_id("session_password-login")
	# Put passed argument of password 
	passElement.send_keys(args.password)
	# Submit the form
	passElement.submit()

	os.system('clear')
	print "Success! Logged In, Data Retrieval in progress!"

	# Retrieve Jobs data, pass number of jobs data you need to retrieve as second argument (1000 here)
	getJobData(browser, 1000)
	# Open home page
	browser.get("https://linkedin.com/")
	# Retrieve User prfoile data, pass number of users data you need to retrieve as second argument (1000 here)
	getPeopleData(browser, 1000)
	# Closes the browser
	browser.close()

if __name__ == '__main__':
	Main()