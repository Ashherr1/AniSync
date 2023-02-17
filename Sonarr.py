import requests
import json

Base_URL = "http://192.168.50.250:8989/api/v3/"
ApiKey = '045fdf958ea74caa9b7bf60a7912b9fe'
Headers = {'accept':'application/json','Content-Type': 'application/json'}
AnimeInfo=[]
def GetSonarr():
  SeriesRL = "series/?"
  Full_URL = Base_URL+SeriesRL+"apikey=" + ApiKey
  SonarrList = requests.get(Full_URL,headers=Headers).json()
  AnimeList = json.dumps(SonarrList,indent=4)
  with open('SonarrList.json' ,"w") as AniList:
    AniList.write(AnimeList)

    

def SearchSonarr():
  global AnimeInfo
  ShowName = "Monster"
  SearchURL= "series/lookup?term=" + ShowName +"&apikey=" + ApiKey
  Full_URL = Base_URL+SearchURL
  SearchResponse= requests.get(Full_URL,headers=Headers)
  final_result = json.dumps(SearchResponse.json()[0],indent=4)       ##Converts to a dictionary 
  with open('SonarrSearch.json' ,"w") as AniList:
    AniList.write(final_result)
  AnimeInfo= json.loads(final_result)
  #print (AnimeInfo)
  return(AnimeInfo)


SearchSonarr()


def PhrasePayload(AnimeInfo):
  AnimeInfo["languageProfileId"] = 1
  AnimeInfo["qualityProfileId"] = 7
  AnimeInfo['seasonFolder'] = True
  AnimeInfo['rootFolderPath']='/tv3/Anime'
  print(len(AnimeInfo['seasons']))
  I =0
  while I < len(AnimeInfo['seasons']):
    print(AnimeInfo['seasons'][I]['monitored'])
    AnimeInfo['seasons'][I]['monitored'] = True
    I+=1
  AnimeInfo['addOptions']= {'monitor':'all','searchForMissingEpisodes':True,'searchForCutoffUnmetEpisodes':True}
  AnimeInfo['seriesType'] ='anime'
  Anidata = json.dumps(AnimeInfo,indent=4)
  with open('SonarrSearchUpdate.json' ,"w") as AniList:
    AniList.write(Anidata) 
  return(Anidata)


def AddSonarr():
  AddUrl = "Series/?"
  Full_URL = Base_URL+AddUrl+"apikey=" + ApiKey
  Body= PhrasePayload(AnimeInfo=AnimeInfo)
  AddRequest = requests.post(Full_URL,Body,headers=Headers)
  print (AddRequest.content)


AddSonarr()





