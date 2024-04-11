# lawpeer-api

## Flask API for LAWPEER.PK FYP

***This repository hosts files for backend api of LAWPEER.PK***

## Specifications
> * python >= 3.11
> * flask

## Running server on localhost (MacOS/Linux):
### Initial setup:
* clone the repo.
```bash
git clone https://github.com/umer-r/lawpeer-api.git
```
* open terminal in the application folder.
```bash
cd lawpeer-api
```
* Create .env file and put the following variables with modifications:
```js
ALLOWED_ORIGIN = 'Front end app URL (http://localhost:3000/)'
DEVELOPMENT_DATABASE_URL = 'postgresql+psycopg2://username:password@localhost:5432/databasename'
JWT_SECRET = 'my_secret_key'
```
* activate the virtual environment *(venv will be written infront of the terminal prompt line)*:
```bash
./venv/Scripts/activate
```
* Install the dependencies (only once on initial setup):
* This step is equivalent to ```npm install```
```bash
pip install -r requirements.txt
```
* Make flask postgres migrations to initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```
* You can deactivate the virtual environment by:
```bash
deactivate
```

### After the initial setup:
* make sure the virtual environment is activated:
```bash
./venv/Scripts/activate
```
* export the flask variable:
```bash
export FLASK_APP=api
```
* Run local server:
```bash
python -m flask run
```

### Single liner runner script:
Use this single liner to run the flask server **AFTER** initial setup of the api:
* Make sure you are cd into the main directory:
```bash
./venv/Scripts/activate && export FLASK_APP=api && python -m flask run
```
## Connect with Creator 🤝🏻 &nbsp;

<p align="center">
<a href="https://www.linkedin.com/in/umer-r-437120214/"><img src="https://img.shields.io/badge/-Umer%20R-0077B5?style=flat&logo=Linkedin&logoColor=white"/></a>
<a href="mailto:russs3400@gmail.com"><img src="https://img.shields.io/badge/-Umer R-D14836?style=flat&logo=Gmail&logoColor=white"/></a>
<a href="https://instagram.com/umer_r74"><img src="https://img.shields.io/badge/-@umer__r74-E4405F?style=flat&logo=Instagram&logoColor=white"/></a>
<a href="https://twitter.com/umer_74"><img src="https://img.shields.io/badge/-@umer__74-1877F2?style=flat&logo=Twitter&logoColor=white"/></a>
</p>