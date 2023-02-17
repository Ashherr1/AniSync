import json
import requests
import secrets
#Reading the Token File 
Token_File = open('Token.json')
Token_Json = json.load(Token_File)

Token = Token_Json['access_token']
BaseURL = 'https://api.myanimelist.net/v2'
##Formating the needed Headers 
Headers = {'Authorization' : 'Bearer ' +Token ,
           "Content-Type":"application/json"}
TargetShows =[]

##Getting the User Name 
def getUserINFO():
    url = BaseURL+'/users/@me'
    response = requests.get(url, headers = {'Authorization': f'Bearer {Token}' })
    user = response.json()
    print (user)



def GetAnimeInfo(ID):
   realID = str(ID)
   Url = BaseURL + '/anime/' + realID
   Dietails = requests.get(Url,headers=Headers,params={'fields':'alternative_titles'})
   AniINFO= json.dumps(Dietails.json(),indent=4)  
   data = json.loads(AniINFO) #Converting the Json response to a Python Dictionary 
  # print(data['alternative_titles']['en'])
   return (data['alternative_titles']['en'])

##Pulling the IDs of the Shows on My anme List
def GetAnimeList():
    global TargetShows
    url= BaseURL+'/users/@me/animelist?fields=list_status&limit=1000'
    body = {'status':'plan_to_watch'}
    response = requests.get(url,headers=Headers,params=body)
    anime= json.dumps(response.json(),indent=4)  
    ##Writing users anime list to a Json file 
    with open('demolist.json' ,'w') as demolist:
        demolist.write(anime)
    with open('demolist.json' ,'r') as demolist:
      jsonlist = json.load(demolist)
      I=0
      while I < len(jsonlist['data']):
        #Print Shows with English translations or Shows without as Standard
        if (GetAnimeInfo((jsonlist['data'][I]['node']['id'])) == ""):
           #print(jsonlist['data'][I]['node']['title'])
           TargetShows.append(jsonlist['data'][I]['node']['title'])
        elif (GetAnimeInfo((jsonlist['data'][I]['node']['id'])) != ""):
            #print(GetAnimeInfo((jsonlist['data'][I]['node']['id'])))
            TargetShows.append(GetAnimeInfo((jsonlist['data'][I]['node']['id'])))
        I+=1
    return(TargetShows)

  
GetAnimeList()

