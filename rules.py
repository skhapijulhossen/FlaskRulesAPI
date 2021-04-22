import pymongo
from flask import jsonify
import datetime

# Initializing Date
date = datetime.datetime.today()

# Database
client = pymongo.MongoClient(
    "localhost", port=27017)

#Rules Database
rulesDB = client.list_database_names()
rulesDB = client["Rules"]

# Server Database
dataDB = client["ServerData"]
Datacollections = [collection.lower()
                   for collection in dataDB.list_collection_names()]


# Class Defination for Rule CRUD Operation
class Rules:

    def __init__(self, group=None, ruleName=None, field=None, criteria=None, value=None):
        self.Group = group
        self.Rule = ruleName
        self.Field = field
        self.Criteria = criteria
        self.Value = value

    def createGroup(self, group):
        try:
            rulesDB['Groups'].insert_one({'_id':group})
            return {'Response': True}
        except Exception as e:
            return {'Response': False, 'Reasons': str(e)}
    
    def getGroups(self):
        try:
            resultSet = rulesDB['Groups'].find()
            groups = {group['_id']: group['_id'] for group in resultSet}
            return {'Groups':groups}
        except Exception as e:
            return {'Response': False, 'Reasons': str(e)}


    def editGroups(self, groupName, newName):
        if groupName in self.getGroups()['Groups'].values():
            try:
                self.collection = rulesDB["Groups"]
                self.collection.delete_one({"_id": groupName})
                self.createGroup(newName)
                self.rules= rulesDB["Rules"]
                self.rules.update_many({"Group":groupName},{'$set':{'Group':newName}})
                return {"Response":True}
            except Exception:
                return {"Response":False}


    def deleteGroup(self, groupName):
        if groupName in self.getGroups()['Groups'].values():
            try:
                self.collection = rulesDB["Groups"]
                self.collection.delete_one({"_id": groupName})
                return {"Response":True}
            except Exception as e:
                return {'Response': False, 'Reasons': str(e)}
        else:
            return {"Response":False}


    def get(self):
        try:
            collection = rulesDB["Rules"]
            groups = set(document["Group"] for document in collection.find())
            data = {group: {doc['_id']: doc for doc in collection.find(
                {"Group": group})} for group in groups}
            return data
        except Exception:
            return False

    def post(self):
        self.collection = rulesDB["Rules"]
        try:
            self.collection.insert_one({
                "_id": self.Rule,
                "Group": self.Group,
                "Field": self.Field,
                "Criteria": self.Criteria,
                "Value": self.Value
            })
            return True
        except Exception:
            return False

    def update(self):
        try:
            self.collection = rulesDB["Rules"]
            self.collection.update_one({"_id": self.Rule}, {
                "$set": {"Group": self.Group, "Field": self.Field,
                         "Criteria": self.Criteria, "Value": self.Value}})
            return True
        except Exception:
            return False

    def delete(self):
        try:
            self.collection = rulesDB["Rules"]
            result = self.collection.delete_one({"_id": self.Rule})
            return result.deleted_count
        except Exception:
            return False

    def apply(self, days=1):
        previousDates = []
        today = date
        for day in range(days):
            previousDates.append((str(today).split(' ')[0])) 
            today = today - datetime.timedelta(days=1)
        rules = self.get()
        groups = list(rules.keys())
        dataWithDate = {}
        for day in previousDates:
            data = {}
            for grp in groups:
                for rule in list(rules[grp].keys()):
                    targetField = rules[grp][rule]["Field"].lower().split(".")
                    Value = rules[grp][rule]["Value"]
                    Criteria = rules[grp][rule]["Criteria"]
                    target = targetField[0]
                    if target.lower() in Datacollections:
                        try:
                            db = dataDB[target]
                            if Criteria.lower() == "gt":
                                matched = db.find(
                                    {targetField[1]: {'$gt': Value}})
                                Rule = rule + \
                                    f"-> {rules[grp][rule]['Field']} > {Value}"
                            elif Criteria.lower() == "gte":
                                matched = db.find(
                                    {targetField[1]: {'$gte': Value}})
                                Rule = rule + \
                                    f"-> {rules[grp][rule]['Field']} >= {Value}"
                            elif Criteria.lower() == "lt":
                                matched = db.find(
                                    {targetField[1]: {'$lt': Value}})
                                Rule = rule + \
                                    f"-> {rules[grp][rule]['Field']} < {Value}"
                            elif Criteria.lower() == "lte":
                                matched = db.find(
                                    {targetField[1]: {'$lte': Value}})
                                Rule = rule + \
                                    f"-> {rules[grp][rule]['Field']} <= {Value}"
                            elif Criteria.lower() == "eq":
                                matched = db.find(
                                    {targetField[1]: {'$eq': Value}})
                                Rule = rule + \
                                    f"-> {rules[grp][rule]['Field']} == {Value}"
                            elif Criteria.lower() == "neq":
                                matched = db.find(
                                    {targetField[1]: {'$not':{'$eq': Value}}})
                                Rule = rule + \
                                    f"-> {rules[grp][rule]['Field']} != {Value}"
                            else:
                                return False
                            passedData = {}
                            for d in matched:
                                check = d['Date'].split(' ')[0]
                                if day == check:
                                    passedData[d['ApplicationName']] = {d['TierName']: {
                                        "Date": d['Date'], targetField[1]: d[targetField[1]]}}
                            data[Rule] = passedData

                        except Exception:
                            return False
            dataWithDate[day] = data
        return dataWithDate


