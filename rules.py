import pymongo
from flask import jsonify
import datetime

# Initializing Date
date = datetime.datetime.today()
dates = []
# for i in range(7):
#     dates.append(str(date).split(' ')[0])
#     date = date - datetime.timedelta(days=1)
# dates = dates[::-1]


# Database
client = pymongo.MongoClient(
    "localhost", port=27017)
rulesDB = client.list_database_names()

rulesDB = client["Rules"]

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
        #dataDate = {}
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
                        if Criteria.lower() == "greater than":
                            matched = db.find(
                                {targetField[1]: {'$gt': Value}})
                            Rule = rule + \
                                f"-> {rules[grp][rule]['Field']} > {Value}"
                        elif Criteria.lower() == "greater than equal to":
                            matched = db.find(
                                {targetField[1]: {'$gte': Value}})
                            Rule = rule + \
                                f"-> {rules[grp][rule]['Field']} >= {Value}"
                        elif Criteria.lower() == "less than":
                            matched = db.find(
                                {targetField[1]: {'$lt': Value}})
                            Rule = rule + \
                                f"-> {rules[grp][rule]['Field']} < {Value}"
                        elif Criteria.lower() == "less than equal to":
                            matched = db.find(
                                {targetField[1]: {'$lte': Value}})
                            Rule = rule + \
                                f"-> {rules[grp][rule]['Field']} <= {Value}"
                        else:
                            return False
                        passedData = {d['ApplicationName']: {d['TierName']: {
                            "Date": d['Date'], targetField[1]: d[targetField[1]]}} for d in matched}
                        data[Rule] = passedData
                    except Exception:
                        return False
        return {str(date).split(' ')[0]: data}


obj = Rules()
obj.apply()
