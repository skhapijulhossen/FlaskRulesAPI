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

    def createGroup(self):
        try:
            rulesDB[self.Group]
            return {'Response': True}
        except Exception as e:
            return {'Response': False, 'Reasons': str(e)}

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

    def apply(self):
        rules = self.get()
        groups = list(rules.keys())
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
                        else:
                            return False
                        passedData = {}
                        for d in matched:
                            today = str(date).split(' ')[0]
                            check = d['Date'].split(' ')[0]
                            print(f'{today}=={check}')
                            if str(date).split(' ')[0] == d['Date'].split(' ')[0]:
                                print(d)
                                passedData[d['ApplicationName']] = {d['TierName']: {
                                    "Date": d['Date'], targetField[1]: d[targetField[1]]}}
                        # passedData = {d['ApplicationName']: {d['TierName']: {
                        #         "Date": d['Date'], targetField[1]: d[targetField[1]]}} for d in matched if str(d['Date'].split[0]) == str(date)}
                        data[Rule] = passedData
                        
                    except Exception:
                        return False
        print(data)
        return {str(date).split(' ')[0]: data}


