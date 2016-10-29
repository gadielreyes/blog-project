## BLOG PROJECT

## TABLE OF CONTENTS
- [Quick start](#quick-start)
- [Creator](#creator)

## QUICK START
- Download python 2.7.12 or later [Python](https://www.python.org/downloads/)
- Download and install Google App Engine SDK for python [Google App Engine](https://cloud.google.com/appengine/docs/python/download)
- Sign up for a Google App Engine Account [Google Account](https://console.cloud.google.com/appengine/)
- Create a new project in [Google's Developer Console](https://console.cloud.google.com/)
- From within gtblogproject directory, start the local development server with the following command: dev_appserver.py .
- Visit [http://localhost:8080](http://localhost:8080) in your browser to view the app
- To deploy your app to App Engine, run the following command from within the root directory of your application where the app.yaml file is located: gcloud app deploy
    Optional flags:
        Include the --project flag to specify an alternate Cloud Platform Console project ID to what you initialized as the default in the gcloud tool. Example: --project [YOUR_PROJECT_ID]
        Include the -v flag to specify a version ID, otherwise one is generated for you. Example: -v [YOUR_VERSION_ID]
- To launch your browser and view the app at http://[YOUR_PROJECT_ID].appspot.com, run the following command: gcloud app browse

### What's included
You'll find the following folder and files

```
grblogproject /
|---- static /
|     |---- css /
|           |---- main.css
|---- templates /
|     |---- base.html
|     |---- editcomment.html
|     |---- editpost.html
|     |---- front.html
|     |---- likepost.html
|     |---- login-form.html
|     |---- newpost.html
|     |---- permalink.html
|     |---- signup-form.html
|     |---- welcome.html
|---- app.yaml
|---- blog.ppy
|---- index.yaml
|---- README.md
```
## CREATOR

Gadiel Reyes
- https://github.com/gadielreyes
- https://twitter.com/gadiel182