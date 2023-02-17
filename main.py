import json
import requests
import secrets

TargetShows =[]
#Reading Token and Api Key for MyAL and Sonarr
Token_File = open('Token.json')
Token_Json = json.load(Token_File)
MyAl_Token = Token_Json['access_token']
Sonarr_Token = Token_Json['Sonarr_Key']
#Formatting Headers
MyAl_BaseURL = 'https://api.myanimelist.net/v2'
MyAl_Headers = {'Authorization' : 'Bearer ' + MyAl_Token , "Content-Type":"application/json"}
Sonarr_BaseURL="http://192.168.50.250:8989/api/v3/"
Sonarr_Headers= {'accept':'application/json','Content-Type': 'application/json'}

#Add ValidationStep to verify MyAl and Sonarr Instances


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
    global TargetShows
    url= MyAl_BaseURL+'/users/@me/animelist?fields=list_status&limit=1000'
    body = {'status':'plan_to_watch'}
    response = requests.get(url,headers=MyAl_Headers,params=body)
    anime= json.dumps(response.json(),indent=4)  
    ##Writing users anime list to a Json file 
    with open('demolist.json' ,'w') as demolist:
        demolist.write(anime)
    with open('demolist.json' ,'r') as demolist:
      jsonlist = json.load(demolist)
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
    return(TargetShows)

#Function to Search for the Shows 
def SearchSonarr(ShowName):
  global AnimeInfo
  SearchURL= "series/lookup?term=" + ShowName +"&apikey=" + Sonarr_Token
  Full_URL = Sonarr_BaseURL+SearchURL
  SearchResponse= requests.get(Full_URL,headers=Sonarr_Headers)
  final_result = json.dumps(SearchResponse.json()[0],indent=4)       ##Converts to a dictionary 
  with open('SonarrSearch.json' ,"w") as AniList:
    AniList.write(final_result)
  AnimeInfo= json.loads(final_result)
  return(AnimeInfo)


#Function to Phrase the Animne Body Payload 
def PhrasePayload(AnimeInfo):
  AnimeInfo["languageProfileId"] = 1
  AnimeInfo["qualityProfileId"] = 7
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
  with open('SonarrSearchUpdate.json' ,"w") as AniList:
    AniList.write(Anidata) 
  return(Anidata)


#Function to Push the Payload to Sonarr
def AddSonarr():
  AddUrl = "Series/?"
  Full_URL = Sonarr_BaseURL+AddUrl+"apikey=" + Sonarr_Token
  Body= PhrasePayload(AnimeInfo=AnimeInfo)
  AddRequest = requests.post(Full_URL,Body,headers=Sonarr_Headers)
  print (AddRequest.content)


def Main():
    i=0 
    GetAnimeList()
    while i < len(TargetShows):
      SearchSonarr(TargetShows[i])
      AddSonarr()
      i+=1

Main()
