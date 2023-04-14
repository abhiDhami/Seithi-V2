# seithi-onecms-analytics-api

## Main Branch Reference
- Cloned the Main Branch on 12-04-2023
- Last Ticket enhancement- AN-1898

## Testing Steps
### Install python-lambda-local library
- pip install python-lambda-local
- More Info: https://pypi.org/project/python-lambda-local/

### Script to run each endpoint
- Provide CMS Data point URL in ./Test/env.json file
- Provide Query parameter details in respected endpoint's .json file. (inside Test folder)

#### Method - 1 
    - Directly Running command in cmd. It will return response in cmd panel (terminal)
##### Section Page API
- python-lambda-local -f lambda_handler SectionPage.py ./local-testing/configs/sectionpage.json -e ./local-testing/configs/env.json

##### Article Page API
- python-lambda-local -f lambda_handler Article.py ./local-testing/configs/article.json -e ./local-testing/configs/env.json

##### Media API
- python-lambda-local -f lambda_handler Media.py ./local-testing/configs/media.json -e ./local-testing/configs/env.json

#### Method - 2
    - Running server locally, where it will act as API.
    - To use this method, one should have Nodejs installed.
##### Step-1
    - From the cms panel, navigate to "local-testing" folder.
    - Run "npm init"
    - Run "npm run start", it will start server locally, hosted at 3000 port
##### Step-2
    - Hurray! Start using the API!
        -Media: http://localhost:3000/media?id=557806&platform=online&site=seithi&sitelang=ta&path=/watch
        -Section Page: http://localhost:3000/sectionpage?site=seithi&path=/asia&sitelang=ta&platform=online&uuid=2019e1c2-463f-4b22-898d-73388c6feeeb
        -Article: http://localhost:3000/article?id=660466&platform=online&site=seithi&sitelang=ta&path=/watch/ihc-sweet-celebration-660466


#### Some of the Example IDs
- Video-Id        : 557086
- Podcast-Id      : 487721
- Live Radio-Id   : 171626
- Article content : 660466