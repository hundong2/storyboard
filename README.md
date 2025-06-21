# storyboard

https://hundong2.github.io/storyboard/

## docker 

```sh
docker build -t my-python-app
docker run my-python-app
```

## execute python venv environment 

```sh
python3 -m venv venv
source venv/bin/activate
which python3 #check python execute path 
python3 -m pip install python-dotenv
```

## requirement.txt setting 

```sh
pip freeze > requirements.txt
or 
python3 -m pip freeze > requirements.txt
```

### load 

```sh
pip install -r requirements.txt
or
python3 -m pip install -r requirements.txt
```