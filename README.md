# Picsaver-Webapp
Implementation of Picsaver(https://github.com/fumblehool/Picsaver) in flask

## Requirements

* Python 2.7.x
* Pip(to install required python modules)
* Instagram Account

### Optional

* Virtualenv

# How to run

### Download code

## Modules required
Install the modules specified in the requirements.txt file.

### Set up Instagram Credentials
* Create a new database with table named **user** consisting of two colums - **access_token** and **username** (This will help in maintaining track of users who have used your app)
* Enter the *hostname*, *username*, *password* and *database_name* in **dbconnect.py** 


## Create Instagram Developer Account

* Create new app here, <http://instagram.com/developer/clients/register/>.
* Set OAuth redirect uri to
		http://localhost:5000/instagram_callback/
(to run the app locally)

### Set up Instagram Credentials

Find your Application's credentials and enter the same in the config.py file

## Start the app

Start up the terminal and enter the follwing command
```
		$python picsaver.py
```

Open browser, <http://localhost:5000>.

## Stop the app

	Ctrl+C
