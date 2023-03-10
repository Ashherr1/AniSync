import json
import requests
import secrets

#Reading Token and Api Key for MyAL and Sonarr
with open ('Token.json') as Token_File:
  Token_Json = json.load(Token_File)
MyAl_Token = Token_Json['access_token']
Sonarr_Token = Token_Json['Sonarr_Key']
#Formatting Headers
MyAl_BaseURL = 'https://api.myanimelist.net/v2'
MyAl_Headers = {'Authorization' : 'Bearer ' + MyAl_Token , "Content-Type":"application/json"}
Sonarr_BaseURL="http://192.168.50.250:8999/api/v3/"
Sonarr_Headers= {'accept':'application/json','Content-Type': 'application/json'}

#Add ValidationStep to verify MyAl and Sonarr Instances
def MyALValidation():
   url = MyAl_BaseURL +'/users/@me'
   response = requests.get(url,headers=MyAl_Headers)
   user = response.json()
   #username = user['name']
   try:
      username = user['name']
      print ('My Anime List EndPoint validated. pulling from User : '+ username)
   except:
      response.raise_for_status()

def SonarrValidation():
   url = Sonarr_BaseURL + 'system/status?apikey=' + Sonarr_Token
   response = requests.get(url)
   System = response.json()
   try:
      systemname = System['instanceName']
      print ('Sonarr EndPoint validated pushing shows to : ' + systemname)
   except:
      response.raise_for_status()


def GetAnimeInfo(ID):
   realID = str(ID)
   Url = MyAl_BaseURL + '/anime/' + realID
   Dietails = requests.get(Url,headers=MyAl_Headers,params={'fields':'alternative_titles'})
   AniINFO= json.dumps(Dietails.json(),indent=4)  
   data = json.loads(AniINFO) #Converting the Json response to a Python Dictionary 
  # print(data['alternative_titles']['en'])
   return (data['alternative_titles']['en'])

##Pulling the IDs of the Shows on My anme List
def GetAnimeList():
    TargetShows=[]
    url= MyAl_BaseURL+'/users/@me/animelist?fields=list_status&limit=1000'
    body = {'status':'plan_to_watch'}
    response = requests.get(url,headers=MyAl_Headers,params=body)
    anime= json.dumps(response.json(),indent=4)  
    ##Writing users anime list to a Json file 
    with open('PlantoWatchDB.json' ,'w') as PlantoWatchDB:
        PlantoWatchDB.write(anime)
    with open('PlantoWatchDB.json' ,'r') as PlantoWatchDB:
      jsonlist = json.load(PlantoWatchDB)
      I=0
      while I < len(jsonlist['data']):
        #Return Shows with English translations or Shows without as Standard
        if (GetAnimeInfo((jsonlist['data'][I]['node']['id'])) == ""):
           #print(jsonlist['data'][I]['node']['title'])
           TargetShows.append(jsonlist['data'][I]['node']['title'])
        elif (GetAnimeInfo((jsonlist['data'][I]['node']['id'])) != ""):
            #print(GetAnimeInfo((jsonlist['data'][I]['node']['id'])))
            TargetShows.append(GetAnimeInfo((jsonlist['data'][I]['node']['id'])))
        I+=1
    with open('PlantoWatchDB.json', 'w') as PlantoWatchDB:
       PlantoWatchDB.write(json.dumps(TargetShows))
    return(TargetShows)

def GetSonarrShows():
  SeriesRL = "series/?"
  Full_URL = Sonarr_BaseURL+SeriesRL+"apikey=" + Sonarr_Token
  SonarrList = requests.get(Full_URL,headers=Sonarr_Headers).json()
  AnimeList = json.loads(json.dumps(SonarrList,indent=4))
  SonarrShow = []
  i = 0
  while i < len(AnimeList):
     SonarrShow.append(AnimeList[i]['title'])
     i +=1
  with open('SonarrList.json' ,"w") as AniList:
    AniList.write(json.dumps(SonarrShow))
  return(SonarrShow)

   
#Function to Search for the Shows 
def SearchSonarr(ShowName):
  global AnimeInfo
  SearchURL= "series/lookup?term=" + ShowName +"&apikey=" + Sonarr_Token
  Full_URL = Sonarr_BaseURL+SearchURL
  SearchResponse= requests.get(Full_URL,headers=Sonarr_Headers)
  final_result = json.dumps(SearchResponse.json()[0],indent=4)       ##Converts to a dictionary 
  AnimeInfo= json.loads(final_result)
  return(AnimeInfo)


#Function to Phrase the Animne Body Payload 
def PhrasePayload(AnimeInfo):
  global  SonarrTitle
  AnimeInfo["languageProfileId"] = 1
    ##QUALITY SETTING DEFAULTS, 
  Any = 1 
  SD = 2
  HD_720P = 3
  HD_1080P = 4
  ULTRA_HD = 5
  HD_720_1080P = 6
  AnimeInfo["qualityProfileId"] = HD_720_1080P

  AnimeInfo['seasonFolder'] = True
  AnimeInfo['rootFolderPath']='/tv3/Anime'
  #print(len(AnimeInfo['seasons']))
  I =0
  while I < len(AnimeInfo['seasons']):
    #print(AnimeInfo['seasons'][I]['monitored'])
    AnimeInfo['seasons'][I]['monitored'] = True
    I+=1
  AnimeInfo['addOptions']= {'monitor':'all','searchForMissingEpisodes':True,'searchForCutoffUnmetEpisodes':True}
  AnimeInfo['seriesType'] ='anime'
  Anidata = json.dumps(AnimeInfo,indent=4)
  SonarrTitle = AnimeInfo['title']
  return(Anidata)


#Function to Push the Payload to Sonarr
def AddSonarr():
  AddUrl = "Series/?"
  Full_URL = Sonarr_BaseURL+AddUrl+"apikey=" + Sonarr_Token
  Body= PhrasePayload(AnimeInfo=AnimeInfo)
  AddRequest = requests.post(Full_URL,Body,headers=Sonarr_Headers)
  if ("This series has already been added" in json.dumps(AddRequest.json(),indent=4)):
     print ("Error!" + SonarrTitle + " is Already in Sonarr perhaps there is a misname between Sonarr and My Anime list?")


def Main():
    MyALValidation()
    SonarrValidation()
    SonarrShows = GetSonarrShows()
    i=0 
    TargetShows =GetAnimeList()
    while i < len(TargetShows):
      if TargetShows[i] in SonarrShows:
         print (TargetShows[i] + ' is already in Sonarr')
      else:
        SearchSonarr(TargetShows[i])
        AddSonarr()
      i+=1



Main()
