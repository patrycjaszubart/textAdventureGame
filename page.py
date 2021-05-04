from flask import Flask, redirect, url_for, render_template, request, jsonify
import random
import enum
import copy
from random import randrange
from collections import defaultdict

app = Flask(__name__)


def makeDict(dict_):
    to_return = defaultdict(int)
    for key, value in dict_.items():
        to_return[key] = value
    return to_return

class Stats:
    def __init__(self): 
        self.strength = 0
        self.dexterity = 0
        self.constitution = 0
        self.wisdom = 0
        self.charisma = 0
        
    def add(self, dict_, max_=10):
        self.strength =  min(max_, self.strength + dict_["strength"])
        self.dexterity = min(max_, self.dexterity + dict_["dexterity"])
        self.constitution = min(max_, self.constitution + dict_["constitution"])
        self.wisdom = min(max_, self.wisdom + dict_["wisdom"])
        self.charisma = min(max_, self.charisma + dict_["charisma"])
           
    def getByName(self, name):
        if name == "strength":
            return self.strength
        if name == "dexterity":
            return self.dexterity
        if name == "constitution":
            return self.constitution
        if name == "wisdom":
            return self.wisdom
        if name == "charisma":
            return self.charisma     
        raise Exception('Unsupported stat: {}'.format(name))
         
        
class MonsterType(enum.Enum):
	Vampire = 15
	Ghost = 12
	Ghoul = 8
	Zombie = 6
	Skeleton = 1
    

monster_hp = {MonsterType.Vampire:30, MonsterType.Ghost:18, MonsterType.Ghoul:12,\
              MonsterType.Zombie:9, MonsterType.Skeleton:3}  

monster_modifier = {MonsterType.Vampire:"dexterity", MonsterType.Ghost:"wisdom",\
                    MonsterType.Ghoul:"constitution", MonsterType.Zombie:"constitution",\
                    MonsterType.Skeleton:"dexterity"}

hero_modifier = {MonsterType.Vampire:"charisma", MonsterType.Ghost:"wisdom",\
                    MonsterType.Ghoul:"strength", MonsterType.Zombie:"dexterity",\
                    MonsterType.Skeleton:"strength"}
                    
item_stats = {"WoodenBat":{"dexterity":5,"constitution":4,"charisma":3},\
              "ThinStick":{"dexterity":2,"constitution":3,"charisma":4},\
              "Garlic":{"dexterity":0,"constitution":0,"charisma":7},\
              "Salt":{"dexterity":0,"constitution":0,"charisma":0},\
              "Aspen-Wood Stake":{"dexterity":0,"constitution":1,"charisma":9},\
              "Revolver":{"dexterity":4,"constitution":2,"charisma":5},\
              "Apple":{"dexterity":0,"constitution":1,"charisma":0},\
              "EmptyCan":{"dexterity":1,"constitution":2,"charisma":0},\
              "BrokenUmbrella":{"dexterity":1,"constitution":2,"charisma":0},\
              "PlantPot":{"dexterity":1,"constitution":1,"charisma":1},\
              "SmallPainting":{"dexterity":2,"constitution":3,"charisma":1},\
              "OldShoe":{"dexterity":2,"constitution":1,"charisma":0},\
              "Pillow":{"dexterity":0,"constitution":5,"charisma":0}}


class Monster:
    def __init__(self, type):
        self.type = type
        self.HP = monster_hp[type]
        self.dead = False

    def getAttack(self, hero_attacking):
        return 10 + randrange(self.type) - hero_attacking.stats.getByName(monster_modifier[self.type])
        
class Hero:
    id_counter = 0
    def __init__(self,  name = "User",  attack_range=5):
        self.id= Hero.id_counter
        Hero.id_counter = Hero.id_counter + 1
        self.name = name
        self.stats = Stats()
        self.HP = 0
        self.stat_points = 0
        self.attack_range = attack_range
        self.collected_items = ""
        self.dead = False

    def upgrade(self, skill_dict):
        self.stats.add(skill_dict)
    
    def addItem(self, item):
        new_thing="\n"+str(item)
        self.collected_items += new_thing
        
        #dict_ = makeDict(item_stats[item])
        #self.stats.add(dict_)
        
    def getAttack(self, monster_attacking):    
        return 10 + randrange(self.attack_range) + self.stats.getByName(hero_modifier[monster_attacking])

    def fight(self, item, monster_attacking):
        dict_ = makeDict(item_stats[item])
        new_stats = copy.deepcopy(self.stats)
        new_stats.add(item_stats[item])
        
        while True:
            self.HP -=  monster_attacking.getAttack(self)
            if not self.HP > 0:
                self.dead = True
                return
            monster_attacking.HP -= self.getAttack(monster_attacking)
            if not monster_attacking.HP > 0:
                monster_attacking.dead = True
                return

@app.route("/")
def home():
    return render_template("index.html")

votes = 0
hero_ = Hero()

def check_minus(val):
    return val > 0

def check_plus(val_HP, val_stats):
    return (val_HP > 0 and val_stats < 10)

@app.route("/story/", methods=['POST', 'GET'])
def story():
    if request.method == 'GET':
        return f"Try going to '/hero' to submit form"
    if request.method == 'POST':
        hero_.name = list(request.form.values())[0]
        if request.form['name'] == "Let's go!" and hero_.HP != 0:
            return render_template("enter.html", inventory = item_stats, hero=hero_)
        if request.form['name'] == "Roll the dice!":
            hero_.stat_points = random.randint(20, 35)
            hero_.HP = random.randint(80, 100)

        if request.form['name'] == "str_plus" and check_plus(hero_.stat_points, hero_.stats.strength):
            hero_.stat_points -= 1
            hero_.upgrade(makeDict({"strength": 1}))
        if request.form['name'] == "str_minus" and check_minus(hero_.stats.strength):
            hero_.stat_points += 1
            hero_.upgrade(makeDict({"strength": -1}))

        if request.form['name'] == "dex_plus" and check_plus(hero_.stat_points, hero_.stats.dexterity):
            hero_.stat_points -= 1
            hero_.upgrade(makeDict({"dexterity": 1}))
        if request.form['name'] == "dex_minus" and check_minus(hero_.stats.dexterity):
            hero_.stat_points += 1
            hero_.upgrade(makeDict({"dexterity": -1}))

        if request.form['name'] == "con_plus" and check_plus(hero_.stat_points, hero_.stats.constitution):
            hero_.stat_points -= 1
            hero_.upgrade(makeDict({"constitution": 1}))
        if request.form['name'] == "con_minus" and check_minus(hero_.stats.constitution):
            hero_.stat_points += 1
            hero_.upgrade(makeDict({"constitution": -1}))

        if request.form['name'] == "wis_plus" and check_plus(hero_.stat_points, hero_.stats.wisdom):
            hero_.stat_points -= 1
            hero_.upgrade(makeDict({"wisdom": 1}))
        if request.form['name'] == "wis_minus" and check_minus(hero_.stats.wisdom):
            hero_.stat_points += 1
            hero_.upgrade(makeDict({"wisdom": -1}))

        if request.form['name'] == "cha_plus" and check_plus(hero_.stat_points, hero_.stats.charisma):
            hero_.stat_points -= 1
            hero_.upgrade(makeDict({"charisma": 1}))
        if request.form['name'] == "cha_minus" and check_minus(hero_.stats.charisma):
            hero_.stat_points += 1
            hero_.upgrade(makeDict({"charisma": -1}))
        return render_template("hero.html", hero=hero_)

@app.route("/hero/")
def hero():
    return render_template("hero.html", hero=hero_)

@app.route("/hall/")
def hall():
    return render_template("hall.html", hero=hero_)

@app.route("/room01/")
def room01():
    return render_template("room01.html", hero=hero_)
    
@app.route("/pick_item", methods=["POST"])
def upvote():
    item = str(request.form)
    item = item[item.find("(")+4 : item.find(",")-1]
    hero_.addItem(item)
    return str(hero_.collected_items)

if __name__ == "__main__":
    app.run(debug=True)

