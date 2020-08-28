
# Dude Multiplayer (BETA)
Welcome to Dude Multiplayer. This project uses the open source platform for behavioral research called [https://www.otree.org/]. This project currently has two games, Bad Influence and DayTrader. The language for the platform and games is Danish. 

## Set-up steps
1. Clone the project
2. Navigate to the project and use the following commands:
```
    pip install -e .
    cd otree
    cd oTree
    otree devserver
```

## How to create a admin user:
1. Create an admin user by using the following command:
```
    otree createsuperuser
```
...Or, if you are using shellbash, try the following command:
```
    winpty python manage.py createsuperuser
```

2. Run the server again and log in:
```
    otree createsuperuser
    otree devserver
```


