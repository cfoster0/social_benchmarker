Social Benchmarker
===================

Hello! This project contains tools for generating social media benchmarks for WBR artists. Don't delete me, I'm very helpful!

----------


Overview
-------------



**Before you can run any of the scripts, you will need to have [Python 3.x](https://www.python.org/downloads/), [pip](https://stackoverflow.com/questions/40868345/checking-whether-the-pip-is-installed), and the [requests](https://pypi.python.org/pypi/requests) module installed.**
1. Download this project by clicking on "Clone or Download" or by clicking [here](https://github.com/cfoster0/social_benchmarker/archive/master.zip).
2. Create an Excel or Google Sheets spreadsheet containing metadata for the peer artists you care about and export it to a .csv on your machine.
3. Run the extraction script, **run.py**, to get data from the social media accounts.
4. Wait . . . Los Angeles wasn't built in a day.
5. Run the analysis script, **generate_report.py**, to convert the data into benchmarks.

----------

Walkthrough
-------------


#### Creating the spreadsheets

**Each social media platform should have its own spreadsheet**, since artist usernames may differ across platforms. In order for the extraction script to know what data to extract, the spreadsheet for each platform needs to have the following format:

| Genre(s)      | Artist Name      | Username               | Start Date        | End Date          |
|---------------|------------------|------------------------|-------------------|-------------------|
| URBAN/POP     | Rihanna          | rihanna                | 17-01-01 00:00:00 | 17-12-31 23:59:59 |
| ROCK          | Prophets of Rage | prophetsofrageofficial | 17-01-01 00:00:00 | 17-12-31 23:59:59 |
| ADULT CONTEMP | Quiet Riot       | quietriot              | 17-01-01 00:00:00 | 17-12-31 23:59:59 |

Once this spreadsheet has been created, you will need to export it to a .csv file so it can be easily read later on. 
> **FYI:** This conversion will ignore formatting, convert all values into plain text, and separate them by commas and line breaks instead of columns and rows. Excel may warn you of this, but don't worry: we are doing that intentionally.

----------

#### Registering for API credentials

For Facebook and YouTube, you will need special credentials in order to access profile data programmatically. This requires you to register an "application" as a developer.

##### Facebook

1. Sign into Facebook.
2. Go to https://developers.facebook.com/apps/.
3. On the top right corner, click the green '+ Add New App' button.
4. Choose a display name and contact email for the new app.
5. You will then be taken to the app window.
5. Click the Dashboard tab (on the sidebar).
6. Within the Dashboard window you will be able to view both the:
	* App ID, also found at the top (towards the left) of the main view page.
	* App secret, by clicking the button 'show' next to the the 'App Secret' field.

These IDs are what you need to substitute in **run.py** for `facebook_app` and `facebook_secret`.

##### YouTube

1. Go to https://developers.google.com/youtube/registering_an_application.
2. Click on the credentials page link (bullet point 1) & sign in using a Gmail account.
3. Once you've signed in, you will be redirected to the credentials page, with a pop up asking to either 'select' or 'create' a project. 
4. Click create, and follow through with the instructions (which simply involves choosing a project name of your choice).
5. Once you're in the credentials window, click the blue 'create credentials' button, and select 'API key' in the drop down menu (first option).
6. A pop up will appear with your Youtube API key.

This key is what you need to substitute in **run.py** for `youtube_key`.

----------

#### Running the extraction script

**run.py** within the [crawlers](crawlers) directory is what you need to run in order to pull data from Facebook, Instagram, or YouTube. It can be run from inside the project with Unix commands of the form `python3 run.py [platform] [input] [data folder]` like:
```
python3 ./crawlers/run.py facebook FacebookArtists.csv ./results/
```
Each social media service has its own flag, which you must specify to run the script. `facebook` is for Facebook, `instagram` is for Instagram, and `youtube` is for YouTube.

The .csv file should be the one you converted earlier from your spreadsheet.

Once it has finished running, it should have saved its data as .json files within whatever folder you specified as your `results` directory.

> **Tip:** Pressing <kbd>Ctrl+Z</kbd> will pause a Python script by suspending its process, and it can be resumed with `fg %1`. If you need to completely stop the script, <kbd>Ctrl+C</kbd> will kill the script.

----------

#### Running the analysis script
**generate_report.py** is what you need to turn the data you have collected into a set of benchmarks. 

It can be run from inside the project with Unix commands of the form `python3 generate_report.py [platform] [input] [data folder] [output]` like:
```
python3 generate_report.py instagram InstagramArtists.csv InstagramBenchmarks.csv
```
Similar to the extraction script, each social media service has its own flag that must be specified to run analysis. `facebook` for Facebook, `instagram` for Instagram, and `youtube` for YouTube.

This script should run quickly, and once completed, spit out a .csv with the calculated benchmarks.

Enjoy!

C & T
