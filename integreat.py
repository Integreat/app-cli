#!/usr/bin/env python3
import requests
import json
import time
from distutils.spawn import find_executable
from subprocess import Popen, PIPE, STDOUT
import shlex

"""
CONFIGURATION SECTION
"""
API_DOMAIN		= 'cms.integreat-app.de'
API_BASE_PATH	= 'wp-json/extensions/v3'

stuff = """
  _____       _                            _      _____ _      _____                        
 |_   _|     | |                          | |    / ____| |    |_   _|     /\                
   | |  _ __ | |_ ___  __ _ _ __ ___  __ _| |_  | |    | |      | |      /  \   _ __  _ __  
   | | | '_ \| __/ _ \/ _` | '__/ _ \/ _` | __| | |    | |      | |     / /\ \ | '_ \| '_ \ 
  _| |_| | | | ||  __/ (_| | | |  __/ (_| | |_  | |____| |____ _| |_   / ____ \| |_) | |_) |
 |_____|_| |_|\__\___|\__, |_|  \___|\__,_|\__|  \_____|______|_____| /_/    \_\ .__/| .__/ 
                       __/ |                                                   | |   | |    
                      |___/                                                    |_|   |_|    
"""


def get_sites():
	r = requests.get("https://{}/{}/sites".format(API_DOMAIN, API_BASE_PATH))
	sites_json = json.loads(r.text)
	sites = {}
	n = 1
	print("")
	for site in sites_json:
		if site['live'] == False:
			sites[n] = site
			n = n + 1
	return sites

def select_site(sites):
	print()
	for site in sites:
		print("{}: {}".format(site, sites[site]['name']))
	user_site = input("Please select a region OR leave empty to quit: ")
	try:
		user_site = int(user_site)
	except:
		return False
	if sites[user_site]['live'] == False:
		return sites[user_site]
	return False

def get_pages(site):
	url = "https://{}{}en/{}/pages".format(API_DOMAIN, site['path'], API_BASE_PATH)
	r = requests.get(url)
	pages_json = json.loads(r.text)
	pages = {}
	for page in pages_json:
		pages[page['id']] = page
	return pages

def render_content(content):
	if find_executable('w3m'):
		cmd = shlex.split("w3m -dump -cols 84 -T 'text/html'")
		p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)    
		grep_stdout = p.communicate(input=bytes(content, 'utf-8'))[0]
		print(grep_stdout.decode())
	else:
		print(content)

def display_page(pages, user_page = None):
	list_children(pages, user_page)
	user_page = input("Select page id OR leave empty to go up: ")
	if user_page == "":
		pass
	else:
		try:
			user_page = int(user_page)
			print("------------------------------------------------------------------------")
			print("Page content")
			print("------------------------------------------------------------------------")
			render_content(pages[user_page]['content'])
			print()
			display_page(pages, user_page)
		except ValueError:
			pass
		return

def list_children(pages, user_page):
	children = []
	for page_id in pages:
		if (user_page is None and pages[page_id]['parent']['id'] == 0) or (user_page is not None and pages[page_id]['parent']['id'] == user_page):
				children.append("{}: {}".format(pages[page_id]['id'], pages[page_id]['title']))
	if(len(children) > 0):
		print("""
------------------------------------------------------------------------
This page contains children:""")
		for child in children:
			print(child)
		print("------------------------------------------------------------------------")

def main():
	print(stuff)
	sites = get_sites()
	while True:
		site = select_site(sites)
		if(site == False):
			quit()
		print()
		print("Welcome to {}".format(site['name']))
		print()
		pages = get_pages(site)
		if site is not False:
			display_page(pages)

main()
