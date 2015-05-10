#!/usr/bin/python

import requests
from bs4 import BeautifulSoup

from sets import Set
import re
import pickle
import os.path
import urlparse
import sys
import time

import data
import email_helper

def dumpStudies():
    """Dumps all the existing old studies. Useful for testing/debugging since we can use this
    to trigger a notification.
    """
    f = open(data.studiesPickle, 'wb')
    empty_set = Set()
    pickle.dump(empty_set, f)
    f.close

def getExperimentId(url):
    """For a given URL, returns the unique experiment_id parameter.

    Argument:
        url (string): a URL containing an experiment_id.

    Returns:
        An experiment ID, represented as a string. If the input is invalid,
        then an error message is instead printed to stderr.
    """
    try:
        return urlparse.parse_qs(urlparse.urlparse(url).query)['experiment_id'][0]
    except:
        print >> sys.stderr, 'bad URL given to', __name__

def getClientValidationParameters(page):
    """Returns a dict with all the HTTP request parameters needed to create/maintain a session
    with Sona by scraping a Sona web page. It includes the login credentials as well as various
    hidden client-side validation values.

    Argument:
        page (string): the HTML text of a Sona web page.

    Returns:
        A dictionary with key-value pairs needed to create/maintain a Sona session.
    """
    payload = {}
    soup = BeautifulSoup(page)
    hiddenValues = soup.findAll(type='hidden')
    for inputTag in hiddenValues:
        name = str(inputTag.get('name'))
        value = str(inputTag.get('value'))
        payload[name] = '' if value is None else value
    payload['ctl00$ContentPlaceHolder1$userid'] = data.username
    payload['ctl00$ContentPlaceHolder1$pw'] = data.password
    payload['ctl00$ContentPlaceHolder1$default_auth_button'] = 'Log In'
    return payload

def getUrl(urlTitleTuple):
    """Returns the URL in a (URL, title) tuple.

    Argument:
        urlTitleTuple (tuple of (string, string)): Contains a two-tuple with the
        URL and title for a study.

    Returns:
        A string containing the URL from the given tuple.
    """
    return urlTitleTuple[0]

def getTitle(urlTitleTuple):
    """Returns the title in a (URL, title) tuple.

    Argument:
        urlTitleTuple (tuple of (string, string)): Contains a two-tuple with the
            URL and title for a study.

    Returns:
        A string containing the title from the given tuple.
    """
    return urlTitleTuple[1]

def main():
    """This function logs in and checks for new studies. If there are any, it sends
    email notifications and 
    """
    domain = 'https://sbe.sona-systems.com/'
    loginURL = domain + 'default.aspx'
    listOfStudiesURL = domain + 'all_exp.aspx'

    # Initiate a connection with Sona by opening the main page.
    s = requests.Session()

    try:
        r = s.get(loginURL)
    except Exception as e:
        print >> sys.stderr, '=============\n'
        print >> sys.stderr, (time.asctime( time.localtime(time.time()) ))
        print >> sys.stderr, e
        sys.exit()
    
    # Parse the main page and attempt to login
    loginPage = BeautifulSoup(r.text)
    payload = getClientValidationParameters(r.text)
    r1 = s.post(loginURL, data=payload)

    # Naviagte to the studies page and retreive all studies visible
    r2 = s.get(listOfStudiesURL)
    studies = BeautifulSoup(r2.text).find('tbody').findAll('tr')
    studiesFound = Set()    # Elements are (URL, title) two-tuples
    for study in studies:
        studyPageCell = study.find('td').find('a')
        if studyPageCell is not None:
            studyURL = domain + studyPageCell.get('href')
            studyTitle = study.findAll('td')[1].find('a').get_text()
            studiesFound.add((studyURL, studyTitle))

    # Only do a comparision if there the program previosuly saved studies
    if os.path.isfile(data.studiesPickle):

        # Open the old studies and do a comparision with the studies just seen
        f = open(data.studiesPickle, 'rb')
        oldStudies = pickle.load(f)
        newStudies = studiesFound - oldStudies
        
        if len(newStudies) > 0:
            print (time.asctime( time.localtime(time.time()) ))
            print 'STUDIES FOUND!'
            print '============='
            print 'Old Studies:'
            print oldStudies
            print '============='
            print 'Studies Found:'
            print studiesFound
            print '============='
            print 'New Studies:'
            print newStudies
            print '=============\n'

            # Create the email body
            email_body = '<html><head></head><body><h1>New Study Timeslots!</h1><br>'

            for urlTitleTuple in newStudies:
                # Insert a new paragraph for each study
                email_body += '<p><a href=\"'
                email_body += getUrl(urlTitleTuple)
                email_body += '\" target=\"_blank\" >'
                email_body += getTitle(urlTitleTuple)
                email_body += '</a></p>'

                # Sign up for a timeslot for this study
                # First, find all the time slots available
                experiment_id = getExperimentId(getUrl(urlTitleTuple))
                r3 = s.get(domain + 'exp_view_slots.aspx?experiment_id=' + experiment_id) 
                URLs = re.findall('exp_sign_up\.aspx\?p_timeslot_id=\d+&amp;timeslot_id=\d+', r3.text)
                
                # Second, need to repopulate the request parameters before attempting sign up
                payload = getClientValidationParameters(r3.text)

                # Third, try to signup for each study timeslot (at most one will be allowed by Sona)
                for URL in URLs:
                    URL = URL.replace('&amp;', '&')
                    r4 = s.post(domain + str(URL), data=payload)

            email_body += '<br><p>The above studies may not be new; they\'re only listed here since they have timeslots that weren\'t previously visible.</p></body></html>'
            
            # Send the notification email
            email_msg = email_helper.GmailClient(data.GMAIL_USERNAME, data.GMAIL_PASSWORD)
            email_msg.send_message('New Sona Study Timeslots', data.recipients, 'Login to see the new timeslots and signup!', email_body.encode('ascii', 'xmlcharrefreplace'))
            email_msg.close()
        f.close()

    # Save the results
    f = open(data.studiesPickle, 'wb')
    pickle.dump(studiesFound, f)
    f.close()
    sys.exit()

if __name__ == '__main__':
    main()
