from flask import Flask, jsonify, request, render_template
from rules import Rules
from flask_cors import CORS, cross_origin
import csv

app = Flask(__name__)
CORS(app=app)
csv_dict = {}
with open('fields.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        csv_dict[row[0]] = row[0]+'.'+row[1]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/createGroup/<group>', methods=['GET'])
def createGroup(group):
    obj = Rules()
    response = jsonify(obj.createGroup(group))
    return response


@app.route('/getGroups/', methods=['GET'])
def getGroup():
    obj = Rules()
    response = jsonify(obj.getGroups())
    return response


@app.route('/editGroup/<group>&<newName>', methods=['GET'])
def editGroup(group, newName):
    obj = Rules()
    response = jsonify(obj.editGroups(group, newName))
    return response

@app.route('/deleteGroup/<group>', methods=['GET'])
def deleteGroup(group):
    obj = Rules()
    response = jsonify(obj.deleteGroup(group))
    return response


@app.route('/addRule/<group>&<rule>&<field>&<criteria>&<int:value>', methods=["GET"])
def addeRule(group, rule, field, criteria, value):
    obj = Rules(group=group, ruleName=rule, field=csv_dict[field],
                criteria=criteria, value=value)
    response = jsonify({
        "Response": obj.post()
    })
    return response


@app.route('/getRules/', methods=['GET'])
def get():
    obj = Rules()
    response = jsonify(obj.get())
    return response


@app.route('/deleteRule/<rule>', methods=["GET"])
def deleteRule(rule):
    try:
        obj = Rules(ruleName=rule)
        response = jsonify({
            "Response": obj.delete()
        })
        return response
    except Exception as e:
        response = jsonify({
            "Response": False,
            "Reason": f"{e}"
        })
        return response


@app.route('/updateRule/<group>&<rule>&<field>&<criteria>&<int:value>', methods=["GET"])
def updateRule(group, rule, field, criteria, value):
    try:
        obj = Rules(group=group, ruleName=rule, field=csv_dict[field],
                    criteria=criteria, value=value)
        response = jsonify({
            "Response": obj.update()
        })
        return response
    except Exception as e:
        response = jsonify({
            "Response": False,
            "Reason": f"{e}"
        })
        return response


@app.route("/apply/<int:days>", methods=["GET"])
def apply(days):
    obj = Rules()
    response = jsonify(obj.apply(days=days))
    return response


if __name__ == "__main__":
    app.run(debug=True)
