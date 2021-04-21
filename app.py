from flask import Flask, jsonify, request, render_template
from rules import Rules
from flask_cors import CORS, cross_origin
import csv

app = Flask(__name__)
CORS(app=app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

csv_dict = {}
with open('fields.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        csv_dict[row[0]] = row[0]+'.'+row[1]


@app.route('/')
@cross_origin()
def index():
    return render_template('index.html')


@app.route('/createGroup/<group>', methods=['GET'])
@cross_origin()
def createGroup(group):
    obj = Rules(group=group)
    response = jsonify(obj.createGroup())
    return response


@app.route('/addRule/<group>&<rule>&<field>&<criteria>&<int:value>', methods=["GET"])
@cross_origin()
def addeRule(group, rule, field, criteria, value):
    field = field.lower()
    obj = Rules(group=group, ruleName=rule, field=csv_dict[field],
                criteria=criteria, value=value)
    response = jsonify({
        "Response": obj.post()
    })
    return response


@app.route('/getRules/', methods=['GET'])
@cross_origin()
def get():
    obj = Rules()
    response = jsonify(obj.get())
    return response


@app.route('/deleteRule/<rule>', methods=["GET"])
@cross_origin()
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
@cross_origin()
def updateRule(group, rule, field, criteria, value):
    field = field.lower()
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
@cross_origin()
def apply(days):
    obj = Rules()
    response = jsonify(obj.apply(days=days))
    return response


if __name__ == "__main__":
    app.run(debug=True)
