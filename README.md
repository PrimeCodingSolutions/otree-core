
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

## How to create an admin user:
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
    otree devserver
```

# The games
## Bad Influence
Bad Influence is a multiplayer network voting game for the whole class. The players vote about ten different questions and dilemmas, and their objective is to convince their network to choose the same preference as yours.

<img src="https://github.com/PrimeCodingSolutions/otree-core/blob/master/otree/static/main_platform/otree/media/bad-influence-network.gif" width="200" height="200">

## Daytrader
Daytrader is a game about how bubbles can arise in the financial world. The players are 'daytraders' in a fictitious stock exchange, and trade in shares in a number of fictitious companies, while at the same time gain insight into the real state of the companies.

<img src="https://github.com/PrimeCodingSolutions/otree-core/blob/master/otree/static/main_platform/otree/media/sack-images/sack-questionmark.svg" width="200" height="200">
