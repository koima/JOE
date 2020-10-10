# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 12:35:17 2020
(c) 2020

@author: Josephat Koima
PhD Candidate - Michigan State University
Dual Major: Economics / Agricultural,Food, & Resource Econ
email: koimajos@msu.edu
website: https://sites.google.com/msu.edu/josephat-koima

@Description:
    This code extracts JOE job lists into an excel file. 
    The relevant fields extracted include: 
   'Institution', 'Position','Date Posted','Application Deadline','Location','Country',
   'Citizenship Requirements','Review Date','Application Requirements' 
@Range: Extracted jobs are limited to those between: August 1, 2020-Jan 31, 2021

**Comments are welcome
"""

#import necessary modules/libraries
import pandas as pd 
import requests, re
from bs4 import BeautifulSoup

#url for jobs posted between August 1, 2020-Jan 31, 2021
url='https://www.aeaweb.org/joe/listings?q=eNplj1EKwkAMRO-Sb4XSzx5AELxDiLuxrsZsSbZKEe9uBAuCf-HNZJJ5wqF4Kzr6rtoNhlwnFEVKrdwZBuhgA1deHtUyOpOlc8BgzuGoCoPOXCIbuLCsY3GfP5t913fbrg9vtTIWJdn_KanO2mxB4_FcJ8zpzhlPVTKbrzCR5pKpMXoyuh2FV8U4sTasKsuK5NsI4202PIYQrYK1-fM1UtyWaQpKXCIxTzR-416vN_ovXaE,'

#place a request and convert data to beautiful soup format
website_url = requests.get(url).text
soup = BeautifulSoup(website_url,'lxml')

#Find all listings
results=soup.findAll('div',attrs={'class':'listing-institution-group-item'})

#List to store all jobs
jobs=[]

#Go through each listing and extract important detailes
for result in results:
    job=[]
    #institution
    inst=result.find('h5',attrs={'class':'group-header-title'}).text
    
    #job titles
    titles=result.findAll('h6',attrs={'class':'listing-item-header-title'})
    
    #date job posted
    posted=result.findAll('div',attrs={'class':'listing-item-header-date-posted'})
    
    #contains brief description of the jobs
    bodies=result.findAll('div', attrs={'class':'listing-item-body'})
    
    #Loop through each job title and extract relevant info: Note some employers have more than one job listed
    for i in range(len(titles)):
        #Postition title
        pos=titles[i].find('a').text
        
        #link to the full job description
        joelink='https://www.aeaweb.org/'+titles[i].find('a')['href']
        
        #etract deadline (if listed)
        try:
            deadline=bodies[i].find('div',attrs={'class':'application-deadline app-instruct-deadline'}).text
        except:
            pass
        #Location of the job (Multiple job locations will yield and empty string)
        location=((bodies[i].findAll('h6')[1].text).split(':')[1]).strip()
        
        #Country of the job 
        country=location.split(',')[-1].strip()
       
        #Visit the url with full job description
        website= requests.get(joelink).text
        soup2 = BeautifulSoup(website,'lxml')
        
        #Job application requirements
        req=soup2.find('ul',attrs={'class':'app-instruct-desc'}).find_all('li')
        requirements=req[0].text
        for r in req[1:]:
            requirements+=","+r.text
            
        #citizenship requirements (e.g. US Citizenship Required)
        cit=soup2.find('p', attrs={'class':'full-text'}).text
        cit=cit.replace('U.S.','US')
        citizen=re.findall(r"([^.]*?citizen[^.]*\.)",cit)   
        citizen=(''.join(citizen))
        
        #Contains important info on application review process: Some posts start reviewing applications before deadlines
        review=re.findall(r"([^.]*?review[^.]*\.)",cit)   
        review=(''.join(review))
        if 'peer-review' in review:
            review=''
            
        #Post date
        date_posted=(posted[i].text).split('Date Posted: ')[1]
        
        #Application deadline
        app_deadline=deadline.split('Application deadline: ')[1]
        
        #print out some details
        print(inst+'    '+pos+'    '+posted[i].text+'    '+deadline + '   '+location.strip())
        print(joelink)
        print('Citizenship:'+citizen)
        print('Review:'+review)
        
        #list containing all the info we want
        job=[inst,pos,date_posted,app_deadline,location,country,citizen,review,requirements,joelink]
        
        #add the job to the list containing all jobs
        jobs.append(job)

#Export data to excel using pandas data-frames 
df = pd.DataFrame(jobs, columns =['Institution', 'Position','Date Posted','Application Deadline','Location','Country','Citizenship Requirements','Review Date','Application Requirements','JOE Link']) 
df.to_excel("JOE_jobs.xlsx")
