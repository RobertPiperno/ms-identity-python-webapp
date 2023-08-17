import identity.web
import requests
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from worklist import get_worklist
from read_json import read_json_file
from read_text import read_text_file
from inventory import read_inventory
import json
import subprocess
import app_config

__version__ = "0.7.0"  # The version of this sample, for troubleshooting purpose

app = Flask(__name__)
app.config.from_object(app_config)
assert app.config["REDIRECT_PATH"] != "/", "REDIRECT_PATH must not be /"
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)

administrators = read_json_file('./resources/administrators.json')

@app.route("/")
def index():
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template('index.html', user=auth.get_user(), version=__version__)




@app.route("/login")
def login():
    return render_template("login.html", version=__version__, **auth.log_in(
        scopes=app_config.SCOPE, # Have user consent to scopes during log-in
        redirect_uri=url_for("auth_response", _external=True), # Optional. If present, this absolute URL must match your app's redirect_uri registered in Azure Portal
        ))


@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))



@app.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('display.html', result=api_result)

@app.route("/dailyreport")
def test():
    if not auth.get_user():
        return redirect(url_for("login"))
    text_data = read_text_file('./resources/ListCollectorsReport.txt')
    json_data = json.loads(text_data)
    return render_template('app.html', user=auth.get_user(), data = json_data, worklist = get_worklist('./resources/worklist.csv', user=auth.get_user()))

@app.route("/admindaily")
def adreport():
    if not auth.get_user():
        return redirect(url_for("login"))
    user = auth.get_user()
    flag = False
    for i in administrators:
        if i == user["name"]:
            flag = True
    if flag == False:
        return redirect(url_for("autherror"))
    text_data = read_text_file('./resources/ListCollectorsReport.txt')
    json_data = json.loads(text_data)
    return render_template('apptest.html', user=auth.get_user(), data = json_data)

@app.route("/inventory")
def alexinvreport():
    if not auth.get_user():
        return redirect(url_for("login"))
    user = auth.get_user()
    flag = False
    for i in administrators:
        if i == user["name"]:
            flag = True
    if flag == False:
        return redirect(url_for("autherror"))
    text_data = read_text_file('./resources/InventoryReport.txt')
    json_data = json.loads(text_data)
    return render_template('alexinventory.html', user=auth.get_user(), data = json_data)

@app.route("/perfreport")
def perfreport():
    if not auth.get_user():
        return redirect(url_for("login"))
    user = auth.get_user()
    flag = False
    for i in administrators:
        if i == user["name"]:
            flag = True
    if flag == False:
        return redirect(url_for("autherror"))
    text_data = read_text_file('./resources/PerformanceReport.txt')
    json_data = json.loads(text_data)
    return render_template('perfrep.html', user=auth.get_user(), data = json_data)

@app.route("/collreport")
def collreport():
    if not auth.get_user():
        return redirect(url_for("login"))
    user = auth.get_user()
    flag = False
    for i in administrators:
        if i == user["name"]:
            flag = True
    
    text_data = read_text_file('./resources/CollectorPaymentReport.txt')
    json_data = json.loads(text_data)
    
    return render_template('coll_report.html', user=auth.get_user(), 
                           data = json_data, worklist = get_worklist('./resources/worklist.csv', user=auth.get_user()),
                           flagPass = flag)

@app.route("/failreport")
def failreport():
    if not auth.get_user():
        return redirect(url_for("login"))
    text_data = read_text_file('./resources/FailReport.txt')
    json_data = json.loads(text_data)
    return render_template('failrep.html', user=auth.get_user(), data = json_data, worklist = get_worklist('./resources/worklist.csv', user=auth.get_user()))


    
@app.route("/autherror")
def autherror():
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template('autherror.html', user=auth.get_user())


if __name__ == "__main__":
	app.run()
