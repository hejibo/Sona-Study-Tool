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


# Dumps all the existing old studies. Useful for testing/debugging since we can use this
# to trigger a notification.
def dumpStudies():
    f = open (data.studiesPickle, 'wb')
    empty_set = Set()
    pickle.dump(empty_set, f)
    f.close

# For a given URL, returns the unique experiment_id parameter.
def getExperimentId (url):
    try:
        return urlparse.parse_qs(urlparse.urlparse(url).query)['experiment_id'][0]
    except:
        print >> sys.stderr, 'bad URL given to', __name__

# Returns a dict with all the parameters needed to maintain a session.
# Includes the login credentials as well as various hidden client-side validation values.
def getClientValidationParameters(page):
    payload = {}
    soup = BeautifulSoup(page)
    hiddenValues = soup.findAll(type='hidden')
    for inputTag in hiddenValues:
        name = str(inputTag.get('name'))
        value = str(inputTag.get('value'))
        if value is None:
            value = ''
        payload[name] = value
    payload['ctl00$ContentPlaceHolder1$userid'] = data.username
    payload['ctl00$ContentPlaceHolder1$pw'] = data.password
    payload['ctl00$ContentPlaceHolder1$default_auth_button'] = 'Log In'
    return payload

# Returns the URL in a (URL, title) study tuple
def getUrl(urlTitleTuple):
    return urlTitleTuple[0]

# Returns the title in a (URL, title) study tuple
def getTitle(urlTitleTuple):
    return urlTitleTuple[1]

def main():
    domain = 'https://sbe.sona-systems.com/'
    loginURL = domain + 'default.aspx'
    listOfStudiesURL = domain + 'all_exp.aspx'

    s = requests.Session()

    try:
        r = s.get (loginURL)
    except Exception as e:
        print >> sys.stderr, '=============\n'
        print >> sys.stderr, (time.asctime( time.localtime(time.time()) ))
        print >> sys.stderr, e
        sys.exit()

    loginPage = BeautifulSoup(r.text)


    payload = getClientValidationParameters(r.text)

    r1 = s.post (loginURL, data=payload)
    r2 = s.get (listOfStudiesURL)

    studies = BeautifulSoup(r2.text).find('tbody').findAll('tr')

    # Elements are (URL, title) tuples
    studiesFound = Set()

    for study in studies:
        studyPageCell = study.find('td').find('a')
        if studyPageCell is not None:
            studyURL = domain + studyPageCell.get('href')
            studyTitle = study.findAll('td')[1].find('a').get_text()
            studiesFound.add((studyURL, studyTitle))


    # Only do a comparision if there are previous studies
    if os.path.isfile(data.studiesPickle):

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
                # insert a new paragraph for each study
                email_body += '<p><a href=\"'
                email_body += getUrl(urlTitleTuple)
                email_body += '\" target=\"_blank\" >'
                email_body += getTitle(urlTitleTuple)
                email_body += '</a></p>'


                # sign up for a timeslot for this study

                # find all the time slots available
                experiment_id = getExperimentId(getUrl(urlTitleTuple))
                r3 = s.get(domain + 'exp_view_slots.aspx?experiment_id=' + experiment_id) 
                URLs = re.findall('exp_sign_up\.aspx\?p_timeslot_id=\d+&amp;timeslot_id=\d+', r3.text)
                
                # need to repopulate the request parameters before attempting signing up
                payload = getClientValidationParameters(r3.text)

                # try to signup for each study timeslot (at most one will be allowed by Sona)
                for URL in URLs:
                    URL = URL.replace('&amp;', '&')
                    r4 = s.post(domain + str(URL), data=payload)

            email_body += '<br><p>The above studies may not be new; they\'re only listed here since they have timeslots that weren\'t previously visible.</p></body></html>'
            
            email_msg = email_helper.Gmail(data.GMAIL_USERNAME, data.GMAIL_PASSWORD)
            email_msg.send_message('New Sona Study Timeslots', data.recipients, 'Login to see the new timeslots and signup!', email_body.encode('ascii', 'xmlcharrefreplace'))
            email_msg.close()
        f.close()

    # Save the results
    f = open (data.studiesPickle, 'wb')
    pickle.dump(studiesFound, f)
    f.close()
    sys.exit()

if __name__ == '__main__':
    main()
