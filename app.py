from flask import Flask, jsonify, request, render_template
from rules import Rules
app = Flask(__name__)


# importing routes

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/addRule/<group>&<rule>&<field>&<criteria>&<int:value>', methods=["GET"])
def addeRule(group, rule, field, criteria, value):
    obj = Rules(group=group, ruleName=rule, field=field,
                criteria=criteria, value=value)
    return jsonify({
        "Response": obj.post()
    })


@app.route('/allRules/', methods=['GET'])
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
    try:
        obj = Rules(group=group, ruleName=rule, field=field,
                    criteria=criteria, value=value)
        return jsonify({
            "Response": obj.update()
        })
    except Exception as e:
        return jsonify({
            "Response": False,
            "Reason": f"{e}"
        })


@app.route("/apply/",methods=["GET"])
def apply():
    obj = Rules()
    return jsonify(obj.apply())



if __name__ == "__main__":
    app.run(debug=True)
