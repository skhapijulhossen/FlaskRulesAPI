from flask import Flask, jsonify, request, render_template
from rules import Rules
import csv
app = Flask(__name__)





csv_dict = {}
with open('fields.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        csv_dict[row[0]] = row[0]+'.'+row[1]
        print(f'{row[0]}.{row[1]}')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/createGroup/<group>', methods=['GET'])
def createGroup(group):
    obj = Rules(group=group)
    return jsonify(obj.createGroup())


@app.route('/addRule/<group>&<rule>&<field>&<criteria>&<int:value>', methods=["GET"])
def addeRule(group, rule, field, criteria, value):
    field = field.lower()
    obj = Rules(group=group, ruleName=rule, field=csv_dict[field],
                criteria=criteria, value=value)
    return jsonify({
        "Response": obj.post()
    })


@app.route('/getRules/', methods=['GET'])
def get():
    obj = Rules()
    return jsonify(obj.get())


@app.route('/deleteRule/<rule>', methods=["GET"])
def deleteRule(rule):
    try:
        obj = Rules(ruleName=rule)
        return jsonify({
        "Response": obj.delete()
    })
    except Exception as e:
        return jsonify({
            "Response": False,
            "Reason": f"{e}"
        })


@app.route('/updateRule/<group>&<rule>&<field>&<criteria>&<int:value>', methods=["GET"])
def updateRule(group, rule, field, criteria, value):
    field = field.lower()
    try:
        obj = Rules(group=group, ruleName=rule, field=csv_dict[field],
                    criteria=criteria, value=value)
        return jsonify({
            "Response": obj.update()
        })
    except Exception as e:
        return jsonify({
            "Response": False,
            "Reason": f"{e}kkk"
        })


@app.route("/apply/<int:days>",methods=["GET"])
def apply(days):
    obj = Rules()
    return jsonify(obj.apply(days=days))



if __name__ == "__main__":
    app.run(debug=True)
