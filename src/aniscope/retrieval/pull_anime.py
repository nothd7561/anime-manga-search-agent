import requests
from pathlib import Path
import json
import time

###RETRIVE DATA FROM THE API FOR ANIME 

project_dir = Path(__file__).resolve().parents[3]

mtype = 'anime'

query = '''
            query ($page: Int, $perPage: Int, $type: MediaType) {
                Page (page: $page, perPage: $perPage) {
                    pageInfo { currentPage, hasNextPage, perPage, total, lastPage}
                    media (type: $type, sort: POPULARITY_DESC) {
                        id
                        title {
                            romaji
                            english} 
                        tags {
                            name rank}
                        description
                        genres
                        episodes
                        chapters
                        averageScore
                        popularity
                        countryOfOrigin
                        format
                        status
                        isAdult
                        siteUrl
                }
            }
        }
        ''' #used to pull our information, different from rest API since this is GraphQL

url = 'https://graphql.anilist.co' #anilist API url


if __name__ == "__main__":

    for page in range(1, 3):
        
        save_path = project_dir / 'data' / 'raw' / f'{mtype}' / f'anilist_{mtype}_p{page:03d}.json'
        save_path.parent.mkdir(parents=True, exist_ok=True)

        if save_path.exists():
            continue
            #check if the path for our file already exists

        variables = {
            'page': page,
            'perPage' : 50,
            'type' : f'{mtype.upper()}'
        }

        response = requests.post(url, json={'query':query, 'variables':variables})
        #make the api request

        if response.status_code == 429:
            time.sleep(60)
            #if we have exceeded pull limit (429), wait for 60 seconds then repeat the call
            response = requests.post(url, json={'query':query, 'variables':variables})

        response.raise_for_status()

        data = response.json()
        #convert data into a json file
        if 'errors' in data:
                    raise RuntimeError(data['errors'])

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            #save the call as a json file

        if data['data']['Page']['pageInfo']['hasNextPage'] == False:
                break #stop the code if there is no next page from the current page
        
        time.sleep(4)
        #wait for 4 seconds before going to the next iteration/making next request

