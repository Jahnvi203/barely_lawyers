from flask import Flask, render_template, request, redirect, url_for, session, make_response, Response, jsonify
from pymongo import MongoClient
from resources.add_inputs import add_inputs_dict
from flask_weasyprint import HTML, render_pdf, CSS
import random
from flask_mail import Mail, Message
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from datetime import datetime
from collections import Counter
import requests
from operator import itemgetter
import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
nltk.download('stopwords')
from nltk.corpus import stopwords

app = Flask(__name__)
app.secret_key = '1E44M1ixSeNGzO3T0dqIoXra7De5B46n'
app.config['SESSION_PERMANENT'] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'jahnvi@ygroo.com'
app.config['MAIL_PASSWORD'] = 'JRSingh@203'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Database Connection
uri = "mongodb+srv://Jahnvi203:Jahnvi203@cluster0.cn63w2k.mongodb.net/app?retryWrites=true&w=majority"
connection = MongoClient(host = uri, connect = False)
db = connection['app']
col_m = db.maintenance_qns
col_d = db.divorce_qns
col_pdfs = db.report_pdfs
col_answers = db.answers
col_annexes = db.annexes
col_glossaries = db.glossaries
col_add_annexes = db.add_annexes
col_html = db.pdfs_html
col_admin = db.admin_users
col_oslas_criteria = db.OSLAS_Criteria
col_OC_Answers = db.OC_Answers

@app.route('/')
def index():
    # df = pd.read_csv('/home/Jahnvi371/fyp/resources/maintenance_qns_new.csv')
    # df_values = df.values.tolist()
    # for row in df_values:
    #     col_m.insert_one({
    #         "qn_no": row[0],
    #         "qn": row[1],
    #         "qn_type": row[2],
    #         "op1": row[3],
    #         "img1": row[4],
    #         "op2": row[5],
    #         "img2": row[6],
    #         "op3": row[7],
    #         "img3": row[8],
    #         "op4": row[9],
    #         "img4": row[10],
    #         "prev_qn_no": row[11],
    #         "sel_op": row[12],
    #         "resource": row[13],
    #         "glossary": row[14],
    #         "add_annex": row[15],
    #         "add_input": row[16],
    #         "final_qn": row[17],
    #         "qn_code": row[18]
    #     })
    # df = pd.read_csv('/home/Jahnvi371/fyp/resources/divorce_qns_new.csv')
    # df_values = df.values.tolist()
    # for row in df_values:
    #     col_d.insert_one({
    #         "qn_no": row[0],
    #         "qn": row[1],
    #         "qn_type": row[2],
    #         "op1": row[3],
    #         "img1": row[4],
    #         "op2": row[5],
    #         "img2": row[6],
    #         "op3": row[7],
    #         "img3": row[8],
    #         "op4": row[9],
    #         "img4": row[10],
    #         "prev_qn_no": row[11],
    #         "sel_op": row[12],
    #         "resource": row[13],
    #         "glossary": row[14],
    #         "add_annex": row[15],
    #         "add_input": row[16],
    #         "final_qn": row[17],
    #         "qn_code": row[18]
    #     })
    # for key in glossaries_dict:
    #     qn = key.split("_")
    #     if qn[0] == "m":
    #         col_glossaries.insert_one({
    #             "type": "maintenance",
    #             "qn_code": int(qn[1].replace("q", "")),
    #             "name": key,
    #             "glossary": glossaries_dict[key]
    #         })
    #     elif qn[0] == "d":
    #         col_glossaries.insert_one({
    #             "type": "divorce",
    #             "qn_code": int(qn[1].replace("q", "")),
    #             "name": key,
    #             "glossary": glossaries_dict[key]
    #         })
    # for key in add_annexes_dict:
    #     qn = key.split("_")
    #     if qn[0] == "m":
    #         col_add_annexes.insert_one({
    #             "type": "maintenance",
    #             "qn_code": int(qn[1].replace("q", "")),
    #             "name": key,
    #             "add_annex": add_annexes_dict[key]
    #         })
    #     elif qn[0] == "d":
    #         col_add_annexes.insert_one({
    #             "type": "divorce",
    #             "qn_code": int(qn[1].replace("q", "")),
    #             "name": key,
    #             "add_annex": add_annexes_dict[key]
    #         })
    # for key in annexes_dict:
    #     col_annexes.insert_one({
    #         "name": key,
    #         "annex": annexes_dict[key]
    #     })
    return render_template('index.html')

@app.route('/maintenance/<prev_qn_no>/<back>', methods = ['POST', 'GET'])
def maintenance(prev_qn_no, back):
    options_html = """"""
    if int(prev_qn_no) == 0:
        sel_op = "op0"
        search_result = list(col_m.find({"prev_qn_no": int(prev_qn_no), "sel_op": str(sel_op)}))[0]
        if 'user-answers' in session:
            session['user-answers'] = []
        if 'additional-inputs' in session:
            session['additional-inputs'] = []
    else:
        if int(back) == 0:
            prev_qn_type = list(col_m.find({"qn_no": int(prev_qn_no)}))[0]['qn_type']
            try:
                if str(prev_qn_type) == "scq":
                    sel_op = request.form.to_dict()['optoption']
                elif str(prev_qn_type) == "mcq":
                    try:
                        check1 = request.form.to_dict()['check1']
                    except:
                        check1 = None
                    try:
                        check2 = request.form.to_dict()['check2']
                    except:
                        check2 = None
                    try:
                        check3 = request.form.to_dict()['check3']
                    except:
                        check3 = None
                    try:
                        check4 = request.form.to_dict()['check4']
                    except:
                        check4 = None
                    sel_op = ""
                    if check1 != None:
                        sel_op += str(check1) + ", "
                    if check2 != None:
                        sel_op += str(check2) + ", "
                    if check3 != None:
                        sel_op += str(check3) + ", "
                    if check4 != None:
                        sel_op += str(check4) + ", "
                    sel_op = sel_op[:-2]
                try:
                    name = request.form.to_dict()['name']
                except:
                    name = None
                try:
                    contact_number = request.form.to_dict()['contact_number']
                except:
                    contact_number = None
                try:
                    email_address = request.form.to_dict()['email_address']
                except:
                    email_address = None
                try:
                    court_case_reference_number = request.form.to_dict()['court_case_reference_number']
                except:
                    court_case_reference_number = None
                if request.method == "POST":
                    if 'user-answers' in session:
                        user_answers_list = session['user-answers']
                        for item in user_answers_list:
                            if item[0] == prev_qn_no:
                                user_answers_list.remove(item)
                        user_answers_list.append([prev_qn_no, sel_op])
                        session['user-answers'] = user_answers_list
                        session.permanent = True
                    else:
                        session['user-answers'] = [[prev_qn_no, sel_op]]
                        session.permanent = True
                    if 'additional-inputs' in session:
                        additional_inputs = session['additional-inputs']
                        if name != None:
                            additional_inputs.append("Name: " + name)
                        if contact_number != None:
                            additional_inputs.append("Contact Number: " + contact_number)
                        if email_address != None:
                            additional_inputs.append("Email Address: " + email_address)
                        if court_case_reference_number != None:
                            additional_inputs.append("Court Case Reference Number: " + court_case_reference_number)
                        session['additional-inputs'] = additional_inputs
                        session.permanent = True
                    else:
                        session['additional-inputs'] = []
                        additional_inputs = []
                        if name != None:
                            additional_inputs.append("Name: " + name)
                        if contact_number != None:
                            additional_inputs.append("Contact Number: " + contact_number)
                        if email_address != None:
                            additional_inputs.append("Email Address: " + email_address)
                        if court_case_reference_number != None:
                            additional_inputs.append("Court Case Reference Number: " + court_case_reference_number)
                        session['additional-inputs'] = additional_inputs
                        session.permanent = True
            except:
                sel_op = "op0"
            search_result = list(col_m.find({"prev_qn_no": int(prev_qn_no), "sel_op": str(sel_op)}))[0]
        else:
            if int(prev_qn_no) == 1:
                return render_template("index.html")
            else:
                search_result = list(col_m.find({"qn_no": int(prev_qn_no)}))[0]['prev_qn_no']
                search_result = list(col_m.find({"qn_no": int(search_result)}))[0]
                user_answers_list = session['user-answers']
                user_answers_list.pop()
                session['user-answers'] = user_answers_list
                session.permanent = True
    current_qn_no = search_result['qn_no']
    qn = search_result['qn']
    qn_type = search_result['qn_type']
    op1 = search_result['op1']
    op2 = search_result['op2']
    op3 = search_result['op3']
    op4 = search_result['op4']
    resource = search_result['resource']
    glossary = search_result['glossary']
    add_annex = search_result['add_annex']
    add_input = search_result['add_input']
    final_qn = search_result['final_qn']
    is_add_annex = None
    add_annex_html = """"""
    is_add_input = None
    add_input_html = """"""
    is_resource = None
    resource_html = """"""
    is_glossary = None
    glossary_html = """"""
    if add_annex != "None":
        is_add_annex = "Present"
        add_annex_html = col_add_annexes.find_one({"name": add_annex})['add_annex']
    if add_input != "None":
        is_add_input = "Present"
        add_inputs = str(add_input).split(", ")
        add_input_html = """"""
        for i in range(len(add_inputs) - 1):
            add_input_html += add_inputs_dict[str(add_inputs[i])]
            add_input_html += "<br>"
        add_input_html += add_inputs_dict[str(add_inputs[-1])]
        add_input_html += "<br>"
    if int(resource) == 1:
        is_resource = "Present"
        if str(resource) != "No Path Found":
            resource_name = qn.lower().replace("annex ", "annex_")
            resource_name += "_m"
            resource_html = col_annexes.find_one({"name": resource_name})['annex']
    if glossary != "None":
        is_glossary = "Present"
        glossary_html = col_glossaries.find_one({"name": glossary})['glossary']
    user_answers_html = ""
    pdf_html_no = ""
    annex_download_html = ""
    if int(final_qn) == 0:
        if int(resource) == 0:
            if op1 != "None" or op2 != "None" or op3 != "None" or op4 != "None":
                img1 = search_result['img1']
                img2 = search_result['img2']
                img3 = search_result['img3']
                img4 = search_result['img4']
                if str(qn_type) == "scq":
                    if op3 != "None" and op4 != "None":
                        options_html = f"""
                        <div class="row" id="options-row">
                            <div class="col-sm-12 col-md-6 col-lg-3">
                                <label>
                                    <input type="radio" class="form-check-input" id="radio1" name="optoption" value="{op1}" required/>
                                        <div class="panel panel-default card-input">
                                            <div class="option-card card">
                                                <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                <p class="option-text">{op1}</p>
                                            </div>
                                        </div>
                                </label>
                            </div>
                            <div class="col-sm-12 col-md-6 col-lg-3">
                                <label>
                                    <input type="radio" class="form-check-input" id="radio2" name="optoption" value="{op2}" required/>
                                        <div class="panel panel-default card-input">
                                            <div class="option-card card">
                                                <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                <p class="option-text">{op2}</p>
                                            </div>
                                        </div>
                                </label>
                            </div>
                            <div class="col-sm-12 col-md-6 col-lg-3">
                                <label>
                                    <input type="radio" class="form-check-input" id="radio3" name="optoption" value="{op3}" required/>
                                        <div class="panel panel-default card-input">
                                            <div class="option-card card">
                                                <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                <p class="option-text">{op3}</p>
                                            </div>
                                        </div>
                                </label>
                            </div>
                            <div class="col-sm-12 col-md-6 col-lg-3">
                                <label>
                                    <input type="radio" class="form-check-input" id="radio4" name="optoption" value="{op4}" required/>
                                        <div class="panel panel-default card-input">
                                            <div class="option-card card">
                                                <div class="op-img-container"><img class="op-img" src="{img4}" alt=""></div>
                                                <p class="option-text">{op4}</p>
                                            </div>
                                        </div>
                                </label>
                            </div>
                        </div>
                        """
                    elif op3 != "None" and op4 == "None":
                        options_html = f"""
                            <div class="row" id="options-row">
                                <div class="col-sm-4 col-md-4 col-lg-4">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio1" name="optoption" value="{op1}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                    <p class="option-text">{op1}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                                <div class="col-sm-4 col-md-4 col-lg-4">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio2" name="optoption" value="{op2}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                    <p class="option-text">{op2}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                                <div class="col-sm-4 col-md-4 col-lg-4">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio3" name="optoption" value="{op3}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                    <p class="option-text">{op3}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                            </div>
                        """
                    elif op3 == "None" and op4 == "None":
                        options_html = f"""
                            <div class="row" id="options-row">
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio1" name="optoption" value="{op1}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                    <p class="option-text">{op1}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio2" name="optoption" value="{op2}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                    <p class="option-text">{op2}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                            </div>
                        """
                elif str(qn_type) == "mcq":
                    if op3 != "None" and op4 != "None":
                        if op4 != "none of the above":
                            options_html = """
                                <script>
                                    function check() {
                                        let check1 = document.getElementById('check1');
                                        let check2 = document.getElementById('check2');
                                        let check3 = document.getElementById('check3');
                                        let check4 = document.getElementById('check4');
                                        if (check1.checked) {
                                            check2.required = false;
                                            check3.required = false;
                                            check4.required = false;
                                        };
                                        if (check2.checked) {
                                            check1.required = false;
                                            check3.required = false;
                                            check4.required = false;
                                        };
                                        if (check3.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check4.required = false;
                                        };
                                        if (check4.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check3.required = false;
                                        };
                                        if (check1.checked === false && check2.checked === false && check3.checked === false && check4.checked === false) {
                                            check1.required = true;
                                            check2.required = true;
                                            check3.required = true;
                                            check4.required = true;
                                        }
                                    }
                                </script>
                            """
                            options_html += f"""
                                <div class="row" id="options-row">
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                        <p class="option-text">{op1}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                        <p class="option-text">{op2}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check3" name="check3" value="{op3}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                        <p class="option-text">{op3}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check4" name="check4" value="{op4}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img4}" alt=""></div>
                                                        <p class="option-text">{op4}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                </div>
                            """
                        else:
                            options_html = """
                                <script>
                                    function check() {
                                        let check1 = document.getElementById('check1');
                                        let check2 = document.getElementById('check2');
                                        let check3 = document.getElementById('check3');
                                        let check4 = document.getElementById('check4');
                                        if (check1.checked) {
                                            check2.required = false;
                                            check3.required = false;
                                            check4.required = false;
                                        };
                                        if (check2.checked) {
                                            check1.required = false;
                                            check3.required = false;
                                            check4.required = false;
                                        };
                                        if (check3.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check4.required = false;
                                        };
                                        if (check4.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check3.required = false;
                                            check1.checked = false;
                                            check2.checked = false;
                                            check3.checked = false;
                                        };
                                        if (check1.checked === false && check2.checked === false && check3.checked === false && check4.checked === false) {
                                            check1.required = true;
                                            check2.required = true;
                                            check3.required = true;
                                            check4.required = true;
                                        }
                                    }
                                </script>
                            """
                            options_html += f"""
                                <div class="row" id="options-row">
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                        <p class="option-text">{op1}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                        <p class="option-text">{op2}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check3" name="check3" value="{op3}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                        <p class="option-text">{op3}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check4" name="check4" value="{op4}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img4}" alt=""></div>
                                                        <p class="option-text">{op4}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                </div>
                            """
                    elif op3 != "None" and op4 == "None":
                        if op3 != "none of the above":
                            options_html = """
                                <script>
                                    function check() {
                                        let check1 = document.getElementById('check1');
                                        let check2 = document.getElementById('check2');
                                        let check3 = document.getElementById('check3');
                                        if (check1.checked) {
                                            check2.required = false;
                                            check3.required = false;
                                        };
                                        if (check2.checked) {
                                            check1.required = false;
                                            check3.required = false;
                                        };
                                        if (check3.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                        };
                                        if (check1.checked === false && check2.checked === false && check3.checked === false) {
                                            check1.required = true;
                                            check2.required = true;
                                            check3.required = true;
                                        }
                                    }
                                </script>
                            """
                            options_html += f"""
                                <div class="row" id="options-row">
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                        <p class="option-text">{op1}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                        <p class="option-text">{op2}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check3" name="check3" value="{op3}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                        <p class="option-text">{op3}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                </div>
                            """
                        else:
                            options_html = """
                                <script>
                                    function check() {
                                        let check1 = document.getElementById('check1');
                                        let check2 = document.getElementById('check2');
                                        let check3 = document.getElementById('check3');
                                        if (check1.checked) {
                                            check2.required = false;
                                            check3.required = false;
                                        };
                                        if (check2.checked) {
                                            check1.required = false;
                                            check3.required = false;
                                        };
                                        if (check3.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check1.checked = false;
                                            check2.checked = false;
                                        };
                                        if (check1.checked === false && check2.checked === false && check3.checked === false) {
                                            check1.required = true;
                                            check2.required = true;
                                            check3.required = true;
                                        }
                                    }
                                </script>
                            """
                            options_html += f"""
                                <div class="row" id="options-row">
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                        <p class="option-text">{op1}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                        <p class="option-text">{op2}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check3" name="check3" value="{op3}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                        <p class="option-text">{op3}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                </div>
                            """
                    elif op3 == "None" and op4 == "None":
                        options_html = """
                            <script>
                                function check() {
                                    let check1 = document.getElementById('check1');
                                    let check2 = document.getElementById('check2');
                                    if (check1.checked) {
                                        check2.required = false;
                                    };
                                    if (check2.checked) {
                                        check1.required = false;
                                    };
                                    if (check1.checked === false && check2.checked === false) {
                                        check1.required = true;
                                        check2.required = true;
                                    }
                                }
                            </script>
                        """
                        options_html += f"""
                            <div class="row" id="options-row">
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                    <p class="option-text">{op1}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                    <p class="option-text">{op2}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                            </div>
                        """
    else:
        user_answers_temp = session['user-answers']
        user_answers_store = []
        for item in user_answers_temp:
            if "op0" not in item:
                question = list(col_m.find({"qn_no": int(item[0])}))[0]['qn']
                question_type = "scq"
                if len(item[1].split(", ")) > 1:
                    question_type = "mcq"
                if len(item[1].split(", ")) == 1 and (len(item[1].split(", ")[0]) > 3  or item[1].split(", ")[0][:2] != "op"):
                    question_type = "mcq"
                if question_type == "scq":
                    selected_option = list(col_m.find({"qn_no": int(item[0])}))[0][str(item[1])]
                elif question_type == "mcq":
                    selected_option = str(item[1])
                user_answers_store.append([question, selected_option])
                user_answers_html += f"<span class='question_text'>{str(question)}</span> <span class='selected_option_text'>{str(selected_option)}</span><br>"
        user_answers_store_dict = {}
        user_answers_store_dict['type'] = "maintenance"
        user_answers_dict = {}
        for item in user_answers_store:
            user_answers_dict[item[0].replace(".", "")] = item[1]
        maintenance_qns = col_m.distinct('qn')
        maintenance_qns = [question.replace('.', '') for question in maintenance_qns]
        user_answers_keys = list(user_answers_dict.keys())
        remaining_qns = list(set(maintenance_qns) - set(user_answers_keys))
        for key in remaining_qns:
            user_answers_dict[key.replace(".", "")] = None
        user_answers_store_dict['user_answers'] = user_answers_dict
        user_inputs_dict = {}
        for item in session['additional-inputs']:
            temp_item = item.split(": ")
            user_inputs_dict[temp_item[0]] = temp_item[1]
        user_answers_store_dict['user_inputs'] = user_inputs_dict
        col_answers.insert_one(user_answers_store_dict)
        resource_html = col_annexes.find_one({"name": resource_name})['annex']
        annex_download_html = """
            <div class="row" id="download-annex-container">
                <h1 id="download-annex-heading">Your Report</h1>
            </div>
            <br>
        """
        annex_download_html += user_answers_html
        annex_download_html += "<br>"
        annex_download_html += ""
        annex_download_html += "<br>"
        annex_download_html += col_annexes.find_one({"name": resource_name})['annex']
        pdf_html_no = random.randrange(100000, 999999)
        col_html.insert_one({
            'no': pdf_html_no,
            'pdf_html': annex_download_html
        })
        session['user-answers'] = []
        session['additional-inputs'] = []
    return render_template('maintenance.html', qn_type = qn_type, current = current_qn_no, question = qn, option_1 = op1, option_2 = op2, option_3 = op3, option_4 = op4, html = options_html, is_add_annex = is_add_annex, add_annex_html = add_annex_html, is_add_input = is_add_input, add_input_html = add_input_html, is_resource = is_resource, resource_html = resource_html, is_glossary = is_glossary, glossary_html = glossary_html, final_qn = int(final_qn), user_responses = user_answers_html, pdf_no = pdf_html_no)

@app.route('/divorce/<prev_qn_no>/<back>', methods = ['POST', 'GET'])
def divorce(prev_qn_no, back):
    options_html = """"""
    if int(prev_qn_no) == 0:
        sel_op = "op0"
        search_result = list(col_d.find({"prev_qn_no": int(prev_qn_no), "sel_op": str(sel_op)}))[0]
        if 'user-answers' in session:
            session['user-answers'] = []
        if 'additional-inputs' in session:
            session['additional-inputs'] = []
    else:
        if int(back) == 0:
            prev_qn_type = list(col_d.find({"qn_no": int(prev_qn_no)}))[0]['qn_type']
            try:
                if str(prev_qn_type) == "scq":
                    sel_op = request.form.to_dict()['optoption']
                    sel_op = sel_op.replace("option", "op")
                elif str(prev_qn_type) == "mcq":
                    try:
                        check1 = request.form.to_dict()['check1']
                    except:
                        check1 = None
                    try:
                        check2 = request.form.to_dict()['check2']
                    except:
                        check2 = None
                    try:
                        check3 = request.form.to_dict()['check3']
                    except:
                        check3 = None
                    try:
                        check4 = request.form.to_dict()['check4']
                    except:
                        check4 = None
                    sel_op = ""
                    if check1 != None:
                        sel_op += str(check1) + ", "
                    if check2 != None:
                        sel_op += str(check2) + ", "
                    if check3 != None:
                        sel_op += str(check3) + ", "
                    if check4 != None:
                        sel_op += str(check4) + ", "
                    sel_op = sel_op[:-2]
                try:
                    name = request.form.to_dict()['name']
                except:
                    name = None
                try:
                    contact_number = request.form.to_dict()['contact_number']
                except:
                    contact_number = None
                try:
                    email_address = request.form.to_dict()['email_address']
                except:
                    email_address = None
                try:
                    court_case_reference_number = request.form.to_dict()['court_case_reference_number']
                except:
                    court_case_reference_number = None
                if request.method == "POST":
                    if 'user-answers' in session:
                        user_answers_list = session['user-answers']
                        for item in user_answers_list:
                            if item[0] == prev_qn_no:
                                user_answers_list.remove(item)
                        user_answers_list.append([prev_qn_no, sel_op])
                        session['user-answers'] = user_answers_list
                        session.permanent = True
                    else:
                        session['user-answers'] = [[prev_qn_no, sel_op]]
                        session.permanent = True
                    if 'additional-inputs' in session:
                        additional_inputs = session['additional-inputs']
                        if name != None:
                            additional_inputs.append("Name: " + name)
                        if contact_number != None:
                            additional_inputs.append("Contact Number: " + contact_number)
                        if email_address != None:
                            additional_inputs.append("Email Address: " + email_address)
                        if court_case_reference_number != None:
                            additional_inputs.append("Court Case Reference Number: " + court_case_reference_number)
                        session['additional-inputs'] = additional_inputs
                        session.permanent = True
                    else:
                        session['additional-inputs'] = []
                        additional_inputs = []
                        if name != None:
                            additional_inputs.append("Name: " + name)
                        if contact_number != None:
                            additional_inputs.append("Contact Number: " + contact_number)
                        if email_address != None:
                            additional_inputs.append("Email Address: " + email_address)
                        if court_case_reference_number != None:
                            additional_inputs.append("Court Case Reference Number: " + court_case_reference_number)
                        session['additional-inputs'] = additional_inputs
                        session.permanent = True
            except:
                sel_op = "op0"
            search_result = list(col_d.find({"prev_qn_no": int(prev_qn_no), "sel_op": str(sel_op)}))[0]
        else:
            if int(prev_qn_no) == 1:
                return render_template("index.html")
            else:
                search_result = list(col_d.find({"qn_no": int(prev_qn_no)}))[0]['prev_qn_no']
                search_result = list(col_d.find({"qn_no": int(search_result)}))[0]
                user_answers_list = session['user-answers']
                user_answers_list.pop()
                session['user-answers'] = user_answers_list
                session.permanent = True
    current_qn_no = search_result['qn_no']
    qn = search_result['qn']
    qn_type = search_result['qn_type']
    op1 = search_result['op1']
    op2 = search_result['op2']
    op3 = search_result['op3']
    op4 = search_result['op4']
    resource = search_result['resource']
    glossary = search_result['glossary']
    add_annex = search_result['add_annex']
    add_input = search_result['add_input']
    final_qn = search_result['final_qn']
    is_add_annex = None
    add_annex_html = """"""
    is_add_input = None
    add_input_html = """"""
    is_resource = None
    resource_html = """"""
    is_glossary = None
    glossary_html = """"""
    if add_annex != "None":
        is_add_annex = "Present"
        add_annex_html = col_add_annexes.find_one({"name": add_annex})['add_annex']
    if add_input != "None":
        is_add_input = "Present"
        add_inputs = str(add_input).split(", ")
        add_input_html = """"""
        for i in range(len(add_inputs) - 1):
            add_input_html += add_inputs_dict[str(add_inputs[i])]
            add_input_html += "<br>"
        add_input_html += add_inputs_dict[str(add_inputs[-1])]
        add_input_html += "<br>"
    if int(resource) == 1:
        is_resource = "Present"
        if str(resource) != "No Path Found":
            resource_name = qn.lower().replace("annex ", "annex_")
            resource_name += "_d"
            resource_html = col_annexes.find_one({"name": resource_name})['annex']
    if glossary != "None":
        is_glossary = "Present"
        glossary_html = col_glossaries.find_one({"name": glossary})['glossary']
    user_answers_html = ""
    pdf_html_no = ""
    annex_download_html = ""
    if int(final_qn) == 0:
        if int(resource) == 0:
            if op1 != "None" or op2 != "None" or op3 != "None" or op4 != "None":
                img1 = search_result['img1']
                img2 = search_result['img2']
                img3 = search_result['img3']
                img4 = search_result['img4']
                if str(qn_type) == "scq":
                    if op3 != "None" and op4 != "None":
                        options_html = f"""
                        <div class="row" id="options-row">
                            <div class="col-sm-12 col-md-6 col-lg-3">
                                <label>
                                    <input type="radio" class="form-check-input" id="radio1" name="optoption" value="{op1}" required/>
                                        <div class="panel panel-default card-input">
                                            <div class="option-card card">
                                                <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                <p class="option-text">{op1}</p>
                                            </div>
                                        </div>
                                </label>
                            </div>
                            <div class="col-sm-12 col-md-6 col-lg-3">
                                <label>
                                    <input type="radio" class="form-check-input" id="radio2" name="optoption" value="{op2}" required/>
                                        <div class="panel panel-default card-input">
                                            <div class="option-card card">
                                                <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                <p class="option-text">{op2}</p>
                                            </div>
                                        </div>
                                </label>
                            </div>
                            <div class="col-sm-12 col-md-6 col-lg-3">
                                <label>
                                    <input type="radio" class="form-check-input" id="radio3" name="optoption" value="{op3}" required/>
                                        <div class="panel panel-default card-input">
                                            <div class="option-card card">
                                                <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                <p class="option-text">{op3}</p>
                                            </div>
                                        </div>
                                </label>
                            </div>
                            <div class="col-sm-12 col-md-6 col-lg-3">
                                <label>
                                    <input type="radio" class="form-check-input" id="radio4" name="optoption" value="{op4}" required/>
                                        <div class="panel panel-default card-input">
                                            <div class="option-card card">
                                                <div class="op-img-container"><img class="op-img" src="{img4}" alt=""></div>
                                                <p class="option-text">{op4}</p>
                                            </div>
                                        </div>
                                </label>
                            </div>
                        </div>
                        """
                    elif op3 != "None" and op4 == "None":
                        options_html = f"""
                            <div class="row" id="options-row">
                                <div class="col-sm-4 col-md-4 col-lg-4">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio1" name="optoption" value="{op1}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                    <p class="option-text">{op1}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                                <div class="col-sm-4 col-md-4 col-lg-4">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio2" name="optoption" value="{op2}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                    <p class="option-text">{op2}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                                <div class="col-sm-4 col-md-4 col-lg-4">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio3" name="optoption" value="{op3}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                    <p class="option-text">{op3}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                            </div>
                        """
                    elif op3 == "None" and op4 == "None":
                        options_html = f"""
                            <div class="row" id="options-row">
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio1" name="optoption" value="{op1}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                    <p class="option-text">{op1}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio2" name="optoption" value="{op2}" required/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                    <p class="option-text">{op2}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                            </div>
                        """
                elif str(qn_type) == "mcq":
                    if op3 != "None" and op4 != "None":
                        if op4 != "none of the above":
                            options_html = """
                                <script>
                                    function check() {
                                        let check1 = document.getElementById('check1');
                                        let check2 = document.getElementById('check2');
                                        let check3 = document.getElementById('check3');
                                        let check4 = document.getElementById('check4');
                                        if (check1.checked) {
                                            check2.required = false;
                                            check3.required = false;
                                            check4.required = false;
                                        };
                                        if (check2.checked) {
                                            check1.required = false;
                                            check3.required = false;
                                            check4.required = false;
                                        };
                                        if (check3.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check4.required = false;
                                        };
                                        if (check4.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check3.required = false;
                                        };
                                        if (check1.checked === false && check2.checked === false && check3.checked === false && check4.checked === false) {
                                            check1.required = true;
                                            check2.required = true;
                                            check3.required = true;
                                            check4.required = true;
                                        }
                                    }
                                </script>
                            """
                            options_html += f"""
                                <div class="row" id="options-row">
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                        <p class="option-text">{op1}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                        <p class="option-text">{op2}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check3" name="check3" value="{op3}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                        <p class="option-text">{op3}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check4" name="check4" value="{op4}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img4}" alt=""></div>
                                                        <p class="option-text">{op4}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                </div>
                            """
                        else:
                            options_html = """
                                <script>
                                    function check() {
                                        let check1 = document.getElementById('check1');
                                        let check2 = document.getElementById('check2');
                                        let check3 = document.getElementById('check3');
                                        let check4 = document.getElementById('check4');
                                        if (check1.checked) {
                                            check2.required = false;
                                            check3.required = false;
                                            check4.required = false;
                                        };
                                        if (check2.checked) {
                                            check1.required = false;
                                            check3.required = false;
                                            check4.required = false;
                                        };
                                        if (check3.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check4.required = false;
                                        };
                                        if (check4.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check3.required = false;
                                            check1.checked = false;
                                            check2.checked = false;
                                            check3.checked = false;
                                        };
                                        if (check1.checked === false && check2.checked === false && check3.checked === false && check4.checked === false) {
                                            check1.required = true;
                                            check2.required = true;
                                            check3.required = true;
                                            check4.required = true;
                                        }
                                    }
                                </script>
                            """
                            options_html += f"""
                                <div class="row" id="options-row">
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                        <p class="option-text">{op1}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                        <p class="option-text">{op2}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check3" name="check3" value="{op3}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                        <p class="option-text">{op3}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-12 col-md-6 col-lg-3">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check4" name="check4" value="{op4}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img4}" alt=""></div>
                                                        <p class="option-text">{op4}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                </div>
                            """
                    elif op3 != "None" and op4 == "None":
                        if op3 != "none of the above":
                            options_html = """
                                <script>
                                    function check() {
                                        let check1 = document.getElementById('check1');
                                        let check2 = document.getElementById('check2');
                                        let check3 = document.getElementById('check3');
                                        if (check1.checked) {
                                            check2.required = false;
                                            check3.required = false;
                                        };
                                        if (check2.checked) {
                                            check1.required = false;
                                            check3.required = false;
                                        };
                                        if (check3.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                        };
                                        if (check1.checked === false && check2.checked === false && check3.checked === false) {
                                            check1.required = true;
                                            check2.required = true;
                                            check3.required = true;
                                        }
                                    }
                                </script>
                            """
                            options_html += f"""
                                <div class="row" id="options-row">
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                        <p class="option-text">{op1}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                        <p class="option-text">{op2}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check3" name="check3" value="{op3}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                        <p class="option-text">{op3}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                </div>
                            """
                        else:
                            options_html = """
                                <script>
                                    function check() {
                                        let check1 = document.getElementById('check1');
                                        let check2 = document.getElementById('check2');
                                        let check3 = document.getElementById('check3');
                                        if (check1.checked) {
                                            check2.required = false;
                                            check3.required = false;
                                        };
                                        if (check2.checked) {
                                            check1.required = false;
                                            check3.required = false;
                                        };
                                        if (check3.checked) {
                                            check1.required = false;
                                            check2.required = false;
                                            check1.checked = false;
                                            check2.checked = false;
                                        };
                                        if (check1.checked === false && check2.checked === false && check3.checked === false) {
                                            check1.required = true;
                                            check2.required = true;
                                            check3.required = true;
                                        }
                                    }
                                </script>
                            """
                            options_html += f"""
                                <div class="row" id="options-row">
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                        <p class="option-text">{op1}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                        <p class="option-text">{op2}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                    <div class="col-sm-4 col-md-4 col-lg-4">
                                        <label>
                                            <input type="checkbox" class="form-check-input" id="check3" name="check3" value="{op3}" required onclick="check()"/>
                                                <div class="panel panel-default card-input">
                                                    <div class="option-card card">
                                                        <div class="op-img-container"><img class="op-img" src="{img3}" alt=""></div>
                                                        <p class="option-text">{op3}</p>
                                                    </div>
                                                </div>
                                        </label>
                                    </div>
                                </div>
                            """
                    elif op3 == "None" and op4 == "None":
                        options_html = """
                            <script>
                                function check() {
                                    let check1 = document.getElementById('check1');
                                    let check2 = document.getElementById('check2');
                                    if (check1.checked) {
                                        check2.required = false;
                                    };
                                    if (check2.checked) {
                                        check1.required = false;
                                    };
                                    if (check1.checked === false && check2.checked === false) {
                                        check1.required = true;
                                        check2.required = true;
                                    }
                                }
                            </script>
                        """
                        options_html += f"""
                            <div class="row" id="options-row">
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="checkbox" class="form-check-input" id="check1" name="check1" value="{op1}" required onclick="check()"/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img1}" alt=""></div>
                                                    <p class="option-text">{op1}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="checkbox" class="form-check-input" id="check2" name="check2" value="{op2}" required onclick="check()"/>
                                            <div class="panel panel-default card-input">
                                                <div class="option-card card">
                                                    <div class="op-img-container"><img class="op-img" src="{img2}" alt=""></div>
                                                    <p class="option-text">{op2}</p>
                                                </div>
                                            </div>
                                    </label>
                                </div>
                            </div>
                        """
    else:
        user_answers_temp = session['user-answers']
        user_answers_store = []
        for item in user_answers_temp:
            if "op0" not in item:
                question = list(col_d.find({"qn_no": int(item[0])}))[0]['qn']
                question_type = "scq"
                if len(item[1].split(", ")) > 1:
                    question_type = "mcq"
                if len(item[1].split(", ")) == 1 and (len(item[1].split(", ")[0]) > 3  or item[1].split(", ")[0][:2] != "op"):
                    question_type = "mcq"
                if question_type == "scq":
                    selected_option = list(col_d.find({"qn_no": int(item[0])}))[0][str(item[1])]
                elif question_type == "mcq":
                    selected_option = str(item[1])
                user_answers_store.append([question, selected_option])
                user_answers_html += f"<span class='question_text'>{str(question)}</span> <span class='selected_option_text'>{str(selected_option)}</span><br>"
        user_answers_store_dict = {}
        user_answers_store_dict['type'] = "divorce"
        user_answers_dict = {}
        for item in user_answers_store:
            user_answers_dict[item[0].replace(".", "")] = item[1]
        divorce_qns = col_d.distinct('qn')
        divorce_qns = [question.replace('.', '') for question in divorce_qns]
        user_answers_keys = list(user_answers_dict.keys())
        remaining_qns = list(set(divorce_qns) - set(user_answers_keys))
        for key in remaining_qns:
            user_answers_dict[key.replace(".", "")] = None
        user_answers_store_dict['user_answers'] = user_answers_dict
        user_inputs_dict = {}
        for item in session['additional-inputs']:
            temp_item = item.split(": ")
            user_inputs_dict[temp_item[0]] = temp_item[1]
        user_answers_store_dict['user_inputs'] = user_inputs_dict
        col_answers.insert_one(user_answers_store_dict)
        resource_html = col_annexes.find_one({"name": resource_name})['annex']
        annex_download_html = """
            <div class="row" id="download-annex-container">
                <h1 id="download-annex-heading">Your Report</h1>
            </div>
            <br>
        """
        annex_download_html += user_answers_html
        annex_download_html += "<br>"
        annex_download_html += ""
        annex_download_html += "<br>"
        annex_download_html += col_annexes.find_one({"name": resource_name})['annex']
        pdf_html_no = random.randrange(100000, 999999)
        col_html.insert_one({
            'no': pdf_html_no,
            'pdf_html': annex_download_html
        })
        session['user-answers'] = []
        session['additional-inputs'] = []
    return render_template('divorce.html', qn_type = qn_type, current = current_qn_no, question = qn, option_1 = op1, option_2 = op2, option_3 = op3, option_4 = op4, html = options_html, is_add_annex = is_add_annex, add_annex_html = add_annex_html, is_add_input = is_add_input, add_input_html = add_input_html, is_resource = is_resource, resource_html = resource_html, is_glossary = is_glossary, glossary_html = glossary_html, final_qn = int(final_qn), user_responses = user_answers_html, pdf_no = pdf_html_no)

@app.route('/report/<no>.pdf')
def report(no):
    pdf_html = list(col_html.find({"no": int(no)}))[0]['pdf_html']
    page_html = render_template('download_pdf.html', html = pdf_html)
    return render_pdf(HTML(string = page_html))

@app.route('/send/<no>/<string:email_input>', methods = ['POST'])
def send(no, email_input):
    email_input = json.loads(email_input)
    email_body = f"""
        Hello,

        Thank you for completing the Preliminary Intake Assessment with the Community Justice Centre .

        You can access your report at http://Jahnvi371.pythonanywhere.com/report/{no}.pdf.

        Best regards,
        Community Justice Centre (CJC)
    """
    msg = Message('Your Preliminary Intake Assessment Report from CJC', sender = 'jahnvi@ygroo.com', recipients = [f'{email_input}'])
    msg.body = email_body
    mail.send(msg)
    return "Email Sent"

@app.route('/admin/login')
def admin_login():
    if 'adminname' in session and 'adminemail' in session and 'adminpassword' in session:
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template("admin_login.html", check_error = 0)

@app.route('/admin/signup')
def admin_signup():
    if 'adminname' in session and 'adminemail' in session and 'adminpassword' in session:
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template("admin_signup.html", check_error = 0)

@app.route('/admin/check-login-details', methods = ['GET', 'POST'])
def check_login_details():
    login_email = request.form.to_dict()['login_email']
    login_pwd = request.form.to_dict()['login_pwd']
    admin_users = list(col_admin.find())
    email_there = 0
    both_there = 0
    if login_email == "" or login_pwd == "":
        return render_template("admin_login.html", check_error = "empty")
    else:
        for user in admin_users:
            if user['email_address'] == login_email:
                email_there = 1
                if user['password'] == login_pwd:
                    both_there = 1
                break
        if both_there == 1:
            session['adminemail'] = login_email
            session['adminpassword'] = login_pwd
            login_name = list(col_admin.find({"email_address": session['adminemail'], "password": session['adminpassword']}))[0]['full_name']
            session['adminname'] = login_name
            return redirect(url_for('admin_dashboard'))
        elif email_there == 1:
            return render_template("admin_login.html", check_error = "wrong password")
        else:
            return render_template("admin_login.html", check_error = "not signed up")

@app.route('/admin/check-signup-details', methods = ['GET', 'POST'])
def check_signup_details():
    signup_name = request.form.to_dict()['signup_name']
    signup_email = request.form.to_dict()['signup_email']
    signup_pwd = request.form.to_dict()['signup_pwd']
    signup_cpwd = request.form.to_dict()['signup_cpwd']
    admin_users = list(col_admin.find())
    email_there = 0
    password_match = 0
    if signup_name == "" or signup_email == "" or signup_pwd == "":
        return render_template("admin_signup.html", check_error = "empty")
    elif signup_pwd != signup_cpwd:
        return render_template("admin_signup.html", check_error = "password mismatch")
    else:
        for user in admin_users:
            if user['email_address'] == signup_email:
                email_there = 1
                break
        if email_there == 1:
            return render_template("admin_signup.html", check_error = "signed up")
        else:
            session['adminemail'] = signup_email
            session['adminpassword'] = signup_cpwd
            session['adminname'] = signup_name
            col_admin.insert_one({
                "full_name": signup_name,
                "email_address": signup_email,
                "password": signup_cpwd
            })
            return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route('/admin/dashboard/maintenance')
def maintenance_dashboard():
    if 'adminname' in session and 'adminemail' in session and 'adminpassword' in session:
        return render_template("maintenance_dashboard.html")
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/dashboard/divorce')
def divorce_dashboard():
    if 'adminname' in session and 'adminemail' in session and 'adminpassword' in session:
        return render_template("divorce_dashboard.html")
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/cms/maintenance')
def maintenance_cms():
    qn_codes = col_m.distinct('qn_code')
    qn_codes.remove(0)
    maintenance_cms_html = ""
    for j in range(len(qn_codes)):
        qn_sample = col_m.find_one({'qn_code': qn_codes[j]})
        qn_text = qn_sample['qn']
        qn_choices = [qn_sample['op1'], qn_sample['op2'], qn_sample['op3'], qn_sample['op4']]
        qn_choices_new = list(filter(("None").__ne__, qn_choices))
        qn_imgs = []
        for i in range(len(qn_choices_new)):
            qn_imgs.append(qn_sample[f'img{str(i+1)}'])
        qn_choices_new_html = ""
        for k in range(len(qn_choices_new)):
            if k == len(qn_choices_new) - 1:
                qn_choices_new_html += f"""
                    <p>&emsp;&emsp;<strong>Option {str(k+1)}: </strong> {qn_choices_new[k]}</p>
                """
            else:
                qn_choices_new_html += f"""
                    <p>&emsp;&emsp;<strong>Option {str(k+1)}: </strong> {qn_choices_new[k]}</p><br>
                """
        maintenance_cms_html += f"""
            <div class="accordion cms" id="q{str(j+1)}_sidebar_accordion">
                <div class="accordion-item cms">
                    <p class="accordion-header cms" id="qh{str(j+1)}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#qc{str(j+1)}" aria-expanded="false" aria-controls="qc{str(j+1)}">
                            {qn_text}
                        </button>
                    </p>
                    <div id="qc{str(j+1)}" class="accordion-collapse collapse" aria-labelledby="qh{str(j+1)}" data-bs-parent="#q{str(j+1)}_sidebar_accordion">
                        <div class="accordion-body cms">
                            {qn_choices_new_html}
                            <button name='edit_button_{str(j+1)}' id='edit_button_{str(j+1)}' class='btn btn-primary edit-button' onClick='get_clicked_button(this.id)'>Edit</button>
                        </div>
                    </div>
                </div>
            </div>
        """
    annexes = list(col_m.find({'qn_code': 0}))
    annexes_new = list(map(itemgetter('qn'), annexes))
    annexes_new = sorted(list(set(annexes_new)))
    annexes_new_html = ""
    for g in range(0, len(annexes_new), 3):
        temp_annexes = ""
        try:
            temp_annexes += f"""
                <div class="col-sm-4">
                    <div class="card annex">
                        <div class="card-body">
                            <h5 class="card-title">{annexes_new[g]}</h5>
                            <button id='annex_edit_button_{annexes_new[g]}' onClick="get_annex_m_button(this.id)" class="btn btn-primary edit-button">Edit</button>
                        </div>
                    </div>
                </div>
            """
        except:
            None
        try:
            temp_annexes += f"""
                <div class="col-sm-4">
                    <div class="card annex">
                        <div class="card-body">
                            <h5 class="card-title">{annexes_new[g+1]}</h5>
                            <button id='annex_edit_button_{annexes_new[g+1]}' onClick="get_annex_m_button(this.id)" class="btn btn-primary edit-button">Edit</button>
                        </div>
                    </div>
                </div>
            """
        except:
            None
        try:
            temp_annexes += f"""
                <div class="col-sm-4">
                    <div class="card annex">
                        <div class="card-body">
                            <h5 class="card-title">{annexes_new[g+2]}</h5>
                            <button id='annex_edit_button_{annexes_new[g+2]}' onClick="get_annex_m_button(this.id)" class="btn btn-primary edit-button">Edit</button>
                        </div>
                    </div>
                </div>
            """
        except:
            None
        temp_row = f"""
            <div class='row' id='options-row'>
                {temp_annexes}
            </div>
            <br>
        """
        annexes_new_html += temp_row
    return render_template('maintenance_cms.html', html = maintenance_cms_html, annex_html = annexes_new_html)

@app.route('/admin/cms/divorce')
def divorce_cms():
    qn_codes = col_d.distinct('qn_code')
    qn_codes.remove(0)
    divorce_cms_html = ""
    for j in range(len(qn_codes)):
        qn_sample = col_d.find_one({'qn_code': qn_codes[j]})
        qn_text = qn_sample['qn']
        qn_choices = [qn_sample['op1'], qn_sample['op2'], qn_sample['op3'], qn_sample['op4']]
        qn_choices_new = list(filter(("None").__ne__, qn_choices))
        qn_imgs = []
        for i in range(len(qn_choices_new)):
            qn_imgs.append(qn_sample[f'img{str(i+1)}'])
        qn_choices_new_html = ""
        for k in range(len(qn_choices_new)):
            if k == len(qn_choices_new) - 1:
                qn_choices_new_html += f"""
                    <p>&emsp;&emsp;<strong>Option {str(k+1)}: </strong> {qn_choices_new[k]}</p>
                """
            else:
                qn_choices_new_html += f"""
                    <p>&emsp;&emsp;<strong>Option {str(k+1)}: </strong> {qn_choices_new[k]}</p><br>
                """
        divorce_cms_html += f"""
            <div class="accordion cms" id="q{str(j+1)}_sidebar_accordion">
                <div class="accordion-item cms">
                    <p class="accordion-header cms" id="qh{str(j+1)}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#qc{str(j+1)}" aria-expanded="false" aria-controls="qc{str(j+1)}">
                            {qn_text}
                        </button>
                    </p>
                    <div id="qc{str(j+1)}" class="accordion-collapse collapse" aria-labelledby="qh{str(j+1)}" data-bs-parent="#q{str(j+1)}_sidebar_accordion">
                        <div class="accordion-body cms">
                            {qn_choices_new_html}
                            <button name='edit_button_{str(j+1)}' id='edit_button_{str(j+1)}' class='btn btn-primary edit-button' onClick='get_clicked_button(this.id)'>Edit</button>
                        </div>
                    </div>
                </div>
        """
    annexes = list(col_d.find({'qn_code': 0}))
    annexes_new = list(map(itemgetter('qn'), annexes))
    annexes_new = sorted(list(set(annexes_new)))
    annexes_new_html = ""
    for g in range(0, len(annexes_new), 3):
        temp_annexes = ""
        try:
            temp_annexes += f"""
                <div class="col-sm-4">
                    <div class="card annex">
                        <div class="card-body">
                            <h5 class="card-title">{annexes_new[g]}</h5>
                            <button id='annex_edit_button_{annexes_new[g]}' onClick="get_annex_d_button(this.id)" class="btn btn-primary edit-button">Edit</button>
                        </div>
                    </div>
                </div>
            """
        except:
            None
        try:
            temp_annexes += f"""
                <div class="col-sm-4">
                    <div class="card annex">
                        <div class="card-body">
                            <h5 class="card-title">{annexes_new[g+1]}</h5>
                            <button id='annex_edit_button_{annexes_new[g+1]}' onClick="get_annex_d_button(this.id)" class="btn btn-primary edit-button">Edit</button>
                        </div>
                    </div>
                </div>
            """
        except:
            None
        try:
            temp_annexes += f"""
                <div class="col-sm-4">
                    <div class="card annex">
                        <div class="card-body">
                            <h5 class="card-title">{annexes_new[g+2]}</h5>
                            <button id='annex_edit_button_{annexes_new[g+2]}' onClick="get_annex_d_button(this.id)" class="btn btn-primary edit-button">Edit</button>
                        </div>
                    </div>
                </div>
            """
        except:
            None
        temp_row = f"""
            <div class='row' id='options-row'>
                {temp_annexes}
            </div>
            <br>
        """
        annexes_new_html += temp_row
    return render_template('divorce_cms.html', html = divorce_cms_html, annex_html = annexes_new_html)

@app.route('/admin/cms/maintenance/update/<qn_code>', methods = ['POST', 'GET'])
def maintenance_cms_update(qn_code):
    qn_sample = col_m.find_one({'qn_code': int(qn_code)})
    qn_text = qn_sample['qn']
    qn_type = qn_sample['qn_type']
    qn_choices = [qn_sample['op1'], qn_sample['op2'], qn_sample['op3'], qn_sample['op4']]
    qn_choices_new = list(filter(("None").__ne__, qn_choices))
    qn_imgs = []
    for i in range(len(qn_choices_new)):
        qn_imgs.append(qn_sample[f'img{str(i+1)}'])
    if qn_sample['glossary'] == "None":
        glossary = None
    else:
        glossary = col_glossaries.find_one({"name": qn_sample['glossary']})['glossary']
    if qn_sample['add_annex'] == "None":
        add_annex = None
    else:
        add_annex = col_add_annexes.find_one({"name": qn_sample['add_annex']})['add_annex']
    choices_html = ""
    if len(qn_choices_new) != 0:
        for l in range(len(qn_choices_new)):
            choices_html += f"""
                <div class="col-sm-3">
                    <label class="edit-question-label" for="op{str(l+1)}"><strong>Option {str(l+1)}</strong></label>
                </div>
                <div class="col-sm-9">
                    <input class="edit-question-input" type="text" name="op{str(l+1)}" required value="{qn_choices_new[l]}">
                </div>
                <br><br>
                <div class="col-sm-3">
                    <label class="edit-question-label" for="img{str(l+1)}"><strong>Image URL for Option {str(l+1)}</strong></label>
                </div>
                <div class="col-sm-9">
                    <input class="edit-question-input" type="text" name="img{str(l+1)}" required value="{qn_imgs[l]}">
                </div>
                <br><br>
            """
    glossary_html = ""
    if glossary != None:
        glossary_html = glossary
    add_annex_html = ""
    if add_annex != None:
        add_annex_html = add_annex
    return render_template("maintenance_cms_update.html", qn_code = qn_code, qn = qn_text, qn_type = qn_type, html = choices_html, glossary_html = glossary_html, add_annex_html = add_annex_html)

@app.route('/admin/cms/divorce/update/<qn_code>', methods = ['POST', 'GET'])
def divorce_cms_update(qn_code):
    qn_sample = col_d.find_one({'qn_code': int(qn_code)})
    qn_text = qn_sample['qn']
    qn_type = qn_sample['qn_type']
    qn_choices = [qn_sample['op1'], qn_sample['op2'], qn_sample['op3'], qn_sample['op4']]
    qn_choices_new = list(filter(("None").__ne__, qn_choices))
    qn_imgs = []
    for i in range(len(qn_choices_new)):
        qn_imgs.append(qn_sample[f'img{str(i+1)}'])
    if qn_sample['glossary'] == "None":
        glossary = None
    else:
        glossary = col_glossaries.find_one({"name": qn_sample['glossary']})['glossary']
    if qn_sample['add_annex'] == "None":
        add_annex = None
    else:
        add_annex = col_add_annexes.find_one({"name": qn_sample['add_annex']})['add_annex']
    choices_html = ""
    if len(qn_choices_new) != 0:
        for l in range(len(qn_choices_new)):
            choices_html += f"""
                <div class="col-sm-3">
                    <label class="edit-question-label" for="op{str(l+1)}"><strong>Option {str(l+1)}</strong></label>
                </div>
                <div class="col-sm-9">
                    <input class="edit-question-input" type="text" name="op{str(l+1)}" required value="{qn_choices_new[l]}">
                </div>
                <br><br>
                <div class="col-sm-3">
                    <label class="edit-question-label" for="img{str(l+1)}"><strong>Image URL for Option {str(l+1)}</strong></label>
                </div>
                <div class="col-sm-9">
                    <input class="edit-question-input" type="text" name="img{str(l+1)}" required value="{qn_imgs[l]}">
                </div>
                <br><br>
            """
    glossary_html = ""
    if glossary != None:
        glossary_html = glossary
    add_annex_html = ""
    if add_annex != None:
        add_annex_html = add_annex
    return render_template("divorce_cms_update.html", qn_code = qn_code, qn = qn_text, qn_type = qn_type, html = choices_html, glossary_html = glossary_html, add_annex_html = add_annex_html)

@app.route('/admin/cms/maintenance/update/effect/<qn_code>', methods = ['POST', 'GET'])
def maintenance_cms_update_effect(qn_code):
    form_response = request.form.to_dict(flat = False)
    qn = form_response['qn'][0]
    col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'qn': qn}})
    glossary = form_response['glossary'][0]
    add_annex = form_response['add_annex'][0]
    glossaries = col_glossaries.distinct("qn_code", {'type': 'maintenance'})
    add_annexes = col_add_annexes.distinct("qn_code", {'type': 'maintenance'})
    if glossary != "" and glossary != "<p><br></p>":
        if int(qn_code) in glossaries:
            col_glossaries.update_one({'qn_code': int(qn_code), 'type': 'maintenance'}, {'$set': {'glossary': glossary}})
        else:
            col_glossaries.insert_one({
                'type': 'maintenance',
                'qn_code': int(qn_code),
                'name': f'm_q{str(qn_code)}_glossary',
                'glossary': glossary
            })
            col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'glossary': f'm_q{str(qn_code)}_glossary'}})
    else:
        if int(qn_code) in glossaries:
            col_glossaries.delete_one({'type': 'maintenance', 'qn_code': int(qn_code)})
            col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'glossary': 'None'}})
    if add_annex != "" and add_annex != "<p><br></p>":
        if int(qn_code) in add_annexes:
            col_add_annexes.update_one({'qn_code': int(qn_code), 'type': 'maintenance'}, {'$set': {'add_annex': add_annex}})
        else:
            col_add_annexes.insert_one({
                'type': 'maintenance',
                'qn_code': int(qn_code),
                'name': f'm_q{str(qn_code)}_add_annex',
                'add_annex': add_annex
            })
            col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'add_annex': f'm_q{str(qn_code)}_add_annex'}})
    else:
        if int(qn_code) in add_annexes:
            col_add_annexes.delete_one({'type': 'maintenance', 'qn_code': int(qn_code)})
            col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'add_annex': 'None'}})
    if 'op1' in form_response:
        col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'op1': form_response['op1'][0]}})
        col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'img1': form_response['img1'][0]}})
    if 'op2' in form_response:
        col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'op2': form_response['op2'][0]}})
        col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'img2': form_response['img2'][0]}})
    if 'op3' in form_response:
        col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'op3': form_response['op3'][0]}})
        col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'img3': form_response['img3'][0]}})
    if 'op4' in form_response:
        col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'op4': form_response['op4'][0]}})
        col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'img4': form_response['img4'][0]}})
    return redirect(url_for('maintenance_cms'))

@app.route('/admin/cms/divorce/update/effect/<qn_code>', methods = ['POST', 'GET'])
def divorce_cms_update_effect(qn_code):
    form_response = request.form.to_dict(flat = False)
    qn = form_response['qn'][0]
    col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'qn': qn}})
    glossary = form_response['glossary'][0]
    add_annex = form_response['add_annex'][0]
    glossaries = col_glossaries.distinct("qn_code", {'type': 'divorce'})
    add_annexes = col_add_annexes.distinct("qn_code", {'type': 'divorce'})
    if glossary != "" and glossary != "<p><br></p>":
        if int(qn_code) in glossaries:
            col_glossaries.update_one({'qn_code': int(qn_code), 'type': 'divorce'}, {'$set': {'glossary': glossary}})
        else:
            col_glossaries.insert_one({
                'type': 'divorce',
                'qn_code': int(qn_code),
                'name': f'd_q{str(qn_code)}_glossary',
                'glossary': glossary
            })
            col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'glossary': f'd_q{str(qn_code)}_glossary'}})
    else:
        if int(qn_code) in glossaries:
            col_glossaries.delete_one({'type': 'divorce', 'qn_code': int(qn_code)})
            col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'glossary': 'None'}})
    if add_annex != "" and add_annex != "<p><br></p>":
        if int(qn_code) in add_annexes:
            col_add_annexes.update_one({'qn_code': int(qn_code), 'type': 'divorce'}, {'$set': {'add_annex': add_annex}})
        else:
            col_add_annexes.insert_one({
                'type': 'divorce',
                'qn_code': int(qn_code),
                'name': f'd_q{str(qn_code)}_add_annex',
                'add_annex': add_annex
            })
            col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'add_annex': f'd_q{str(qn_code)}_add_annex'}})
    else:
        if int(qn_code) in add_annexes:
            col_add_annexes.delete_one({'type': 'divorce', 'qn_code': int(qn_code)})
            col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'add_annex': 'None'}})
    if 'op1' in form_response:
        col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'op1': form_response['op1'][0]}})
        col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'img1': form_response['img1'][0]}})
    if 'op2' in form_response:
        col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'op2': form_response['op2'][0]}})
        col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'img2': form_response['img2'][0]}})
    if 'op3' in form_response:
        col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'op3': form_response['op3'][0]}})
        col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'img3': form_response['img3'][0]}})
    if 'op4' in form_response:
        col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'op4': form_response['op4'][0]}})
        col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'img4': form_response['img4'][0]}})
    return redirect(url_for('divorce_cms'))

@app.route('/admin/cms/annex/update/<type>/<annex_code>', methods = ['POST', 'GET'])
def annex_update(annex_code, type):
    if type == "maintenance":
        annex_name = annex_code.lower().replace(" ", "_") + "_m"
        annex_display_name = annex_name.replace("_m", " (Maintenance)").replace("_", " ").upper().replace("ANNEX", "Annex").replace("MAINTENANCE", "Maintenance")
        annex_html = col_annexes.find_one({'name': annex_name})['annex']
    elif type == "divorce":
        annex_name = annex_code.lower().replace(" ", "_") + "_d"
        annex_display_name = annex_name.replace("_d", " (Divorce)").replace("_", " ").upper().replace("ANNEX", "Annex").replace("DIVORCE", "Divorce")
        annex_html = col_annexes.find_one({'name': annex_name})['annex']
    return render_template('annex_update.html', type = type, annex_name = annex_name, annex_display_name = annex_display_name, annex_html = annex_html)

@app.route('/admin/cms/annex/update/effect/<type>/<annex_name>', methods = ['POST', 'GET'])
def annex_update_effect(annex_name, type):
    edited_annex = request.form.to_dict()['annex']
    col_annexes.update_one({'name': annex_name}, {'$set': {'annex': edited_annex}})
    if type == "maintenance":
        return redirect(url_for('maintenance_cms'))
    elif type == "divorce":
        return redirect(url_for('divorce_cms'))

@app.route("/oslas_criteria", methods=["POST", "GET"])
def oslas_criteria():
    # OSLAS Introduction message database
    OCIntro = list(col_oslas_criteria.find({"QN": "32"}))[0]
    Introduction_message = OCIntro["Introduction_message"]

    # OSLAS Criteria Question 1 database
    OCQuestion1 = list(col_oslas_criteria.find({"QN": "1"}))[0]
    OCQ1 = OCQuestion1["OCQ1"]
    OCQ1op1 = OCQuestion1["OCQ1op1"]
    OCQ1op2 = OCQuestion1["OCQ1op2"]

    # OSLAS Criteria Question 2 database
    OCQuestion2 = list(col_oslas_criteria.find({"QN": "2"}))[0]
    OCQ2 = OCQuestion2["OCQ2"]
    OCQ2op1 = OCQuestion2["OCQ2op1"]
    OCQ2op2 = OCQuestion2["OCQ2op2"]

    # OSLAS Criteria Question 3 database
    OCQuestion3 = list(col_oslas_criteria.find({"QN": "3"}))[0]
    OCQ3 = OCQuestion3["OCQ3"]
    OCQ3op1 = OCQuestion3["OCQ3op1"]
    OCQ3op2 = OCQuestion3["OCQ3op2"]

    # OSLAS Criteria Question 4 database
    OCQuestion4 = list(col_oslas_criteria.find({"QN": "4"}))[0]
    OCQ4 = OCQuestion4["OCQ4"]
    OCQ4op1 = OCQuestion4["OCQ4op1"]
    OCQ4op2 = OCQuestion4["OCQ4op2"]
    OCQ4op3 = OCQuestion4["OCQ4op3"]

    # OSLAS Criteria Question 5 database
    OCQuestion5 = list(col_oslas_criteria.find({"QN": "5"}))[0]
    OCQ5 = OCQuestion5["OCQ5"]

    # OSLAS Criteria Civil(a) database
    OCCivil_a = list(col_oslas_criteria.find({"QN": "6"}))[0]
    Civil_a = OCCivil_a["Civil_a"]
    Civil_a_op1 = OCCivil_a["Civil_a_op1"]
    Civil_a_op2 = OCCivil_a["Civil_a_op2"]

    # OSLAS Criteria Civil(b) database
    OCCivil_b = list(col_oslas_criteria.find({"QN": "7"}))[0]
    Civil_b = OCCivil_b["Civil_b"]
    Civil_b_op1 = OCCivil_b["Civil_b_op1"]
    Civil_b_op2 = OCCivil_b["Civil_b_op2"]
    Civil_b_op3 = OCCivil_b["Civil_b_op3"]
    Civil_b_op4 = OCCivil_b["Civil_b_op4"]
    Civil_b_op5 = OCCivil_b["Civil_b_op5"]
    Civil_b_op6 = OCCivil_b["Civil_b_op6"]
    Civil_b_op7 = OCCivil_b["Civil_b_op7"]
    Civil_b_op8 = OCCivil_b["Civil_b_op8"]

    # OSLAS Criteria Civil(c) respondent database
    OCCivil_c_respondent = list(col_oslas_criteria.find({"QN": "8"}))[0]
    Civil_c_respondent = OCCivil_c_respondent["Civil_c_respondent"]
    Civil_c_respondent_op1 = OCCivil_c_respondent["Civil_c_respondent_op1"]
    Civil_c_respondent_op2 = OCCivil_c_respondent["Civil_c_respondent_op2"]
    Civil_c_respondent_op3 = OCCivil_c_respondent["Civil_c_respondent_op3"]
    Civil_c_respondent_op4 = OCCivil_c_respondent["Civil_c_respondent_op4"]
    Civil_c_respondent_op5 = OCCivil_c_respondent["Civil_c_respondent_op5"]
    Civil_c_respondent_op6 = OCCivil_c_respondent["Civil_c_respondent_op6"]

    # OSLAS Criteria Civil(c) claimant database
    OCCivil_c_claimant = list(col_oslas_criteria.find({"QN": "9"}))[0]
    Civil_c_claimant = OCCivil_c_claimant["Civil_c_claimant"]
    Civil_c_claimant_op1 = OCCivil_c_claimant["Civil_c_claimant_op1"]
    Civil_c_claimant_op2 = OCCivil_c_claimant["Civil_c_claimant_op2"]
    Civil_c_claimant_op3 = OCCivil_c_claimant["Civil_c_claimant_op3"]
    Civil_c_claimant_op4 = OCCivil_c_claimant["Civil_c_claimant_op4"]
    Civil_c_claimant_op5 = OCCivil_c_claimant["Civil_c_claimant_op5"]

    # OSLAS Criteria Civil(c) employment database
    OCCivil_c_employment = list(col_oslas_criteria.find({"QN": "11"}))[0]
    Civil_c_employment = OCCivil_c_employment["Civil_c_employment"]
    Civil_c_claimant_employment_op1 = OCCivil_c_employment["Civil_c_claimant_employment_op1"]
    Civil_c_claimant_employment_op2 = OCCivil_c_employment["Civil_c_claimant_employment_op2"]
    Civil_c_respondent_employment_op1 = OCCivil_c_employment["Civil_c_respondent_employment_op1"]
    Civil_c_employment_none = OCCivil_c_employment["Civil_c_employment_none"]

    # OSLAS Criteria Civil(d) claimant database
    OCCivil_d_claimant = list(col_oslas_criteria.find({"QN": "10"}))[0]
    Civil_d_claimant = OCCivil_d_claimant["Civil_d_claimant"]
    Civil_d_claimant_op1 = OCCivil_d_claimant["Civil_d_claimant_op1"]
    Civil_d_claimant_op2 = OCCivil_d_claimant["Civil_d_claimant_op2"]
    Civil_d_claimant_op3 = OCCivil_d_claimant["Civil_d_claimant_op3"]

    # OSLAS Criteria Civil(d) claimant employment database
    OCCivil_d_claimant_employment = list(col_oslas_criteria.find({"QN": "12"}))[0]
    Civil_d_claimant_employment = OCCivil_d_claimant_employment["Civil_d_claimant_employment"]
    Civil_d_claimant_employment_op1 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op1"]
    Civil_d_claimant_employment_op2 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op2"]
    Civil_d_claimant_employment_op3 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op3"]
    Civil_d_claimant_employment_op4 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op4"]
    Civil_d_claimant_employment_op5 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op5"]
    Civil_d_claimant_employment_op6 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op6"]

    # OSLAS Criteria Civil(d) respondent employment database
    OCCivil_d_respondent_employment = list(col_oslas_criteria.find({"QN": "13"}))[0]
    Civil_d_respondent_employment = OCCivil_d_respondent_employment["Civil_d_respondent_employment"]
    Civil_d_respondent_employment_op1 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op1"]
    Civil_d_respondent_employment_op2 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op2"]
    Civil_d_respondent_employment_op3 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op3"]
    Civil_d_respondent_employment_op4 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op4"]
    Civil_d_respondent_employment_op5 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op5"]
    Civil_d_respondent_employment_op6 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op6"]
    Civil_d_respondent_employment_op7 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op7"]

    # OSLAS Criteria Civil(e) claimant employment database
    OCCivil_e_claimant_employment = list(col_oslas_criteria.find({"QN": "14"}))[0]
    Civil_e_claimant_employment = OCCivil_e_claimant_employment["Civil_e_claimant_employment"]
    Civil_e_claimant_employment_op1 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op1"]
    Civil_e_claimant_employment_op2 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op2"]
    Civil_e_claimant_employment_op3 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op3"]
    Civil_e_claimant_employment_op4 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op4"]
    Civil_e_claimant_employment_op5 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op5"]

    # OSLAS Criteria Resolve the dispute online database
    OCResolve_the_dispute_online = list(col_oslas_criteria.find({"QN": "15"}))[0]
    Resolve_the_dispute_online = OCResolve_the_dispute_online["Resolve_the_dispute_online"]
    Resolve_the_dispute_online_op1 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op1"]
    Resolve_the_dispute_online_op2 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op2"]
    Resolve_the_dispute_online_op3 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op3"]

    # OSLAS Criteria Civil(c) claimant neighbour database
    OCCivil_c_neighbour = list(col_oslas_criteria.find({"QN": "16"}))[0]
    Civil_c_claimant_neighbour = OCCivil_c_neighbour["Civil_c_claimant_neighbour"]
    Civil_c_claimant_neighbour_op1 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op1"]
    Civil_c_claimant_neighbour_op2 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op2"]
    Civil_c_claimant_neighbour_op3 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op3"]
    Civil_c_claimant_neighbour_op4 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op4"]
    Civil_c_claimant_neighbour_op5 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op5"]
    Civil_c_claimant_neighbour_op6 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op6"]

    # OSLAS Criteria Civil(d) claimant neighbour database
    OCCivil_d_claimant_neighbour = list(col_oslas_criteria.find({"QN": "17"}))[0]
    Civil_d_claimant_neighbour = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour"]
    Civil_d_claimant_neighbour_op1 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op1"]
    Civil_d_claimant_neighbour_op2 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op2"]
    Civil_d_claimant_neighbour_op3 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op3"]
    Civil_d_claimant_neighbour_op4 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op4"]
    Civil_d_claimant_neighbour_op5 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op5"]
    Civil_d_claimant_neighbour_op6 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op6"]

    # OSLAS Criteria Civil(c) respondent neighbour database
    OCCivil_c_respondent_neighbour = list(col_oslas_criteria.find({"QN": "18"}))[0]
    Civil_c_respondent_neighbour = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour"]
    Civil_c_respondent_neighbour_op1 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op1"]
    Civil_c_respondent_neighbour_op2 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op2"]
    Civil_c_respondent_neighbour_op3 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op3"]
    Civil_c_respondent_neighbour_op4 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op4"]
    Civil_c_respondent_neighbour_op5 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op5"]
    Civil_c_respondent_neighbour_op6 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op6"]

    # OSLAS Criteria Civil(c) claimant harassment database
    OCCivil_c_claimant_harassment = list(col_oslas_criteria.find({"QN": "19"}))[0]
    Civil_c_claimant_harassment = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment"]
    Civil_c_claimant_harassment_op1 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op1"]
    Civil_c_claimant_harassment_op2 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op2"]
    Civil_c_claimant_harassment_op3 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op3"]
    Civil_c_claimant_harassment_op4 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op4"]
    Civil_c_claimant_harassment_op5 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op5"]
    Civil_c_claimant_harassment_op6 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op6"]

    # OSLAS Criteria Civil(d) claimant harassment database
    OCCivil_d_claimant_harassment = list(col_oslas_criteria.find({"QN": "20"}))[0]
    Civil_d_claimant_harassment = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment"]
    Civil_d_claimant_harassment_op1 = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment_op1"]
    Civil_d_claimant_harassment_op2 = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment_op2"]
    Civil_d_claimant_harassment_op3 = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment_op3"]
    Civil_d_claimant_harassment_op4 = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment_op4"]

    # OSLAS Criteria Civil(e) claimant harassment database
    OCCivil_e_claimant_harassment = list(col_oslas_criteria.find({"QN": "21"}))[0]
    Civil_e_claimant_harassment = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment"]
    Civil_e_claimant_harassment_op1 = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment_op1"]
    Civil_e_claimant_harassment_op2 = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment_op2"]
    Civil_e_claimant_harassment_op3 = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment_op3"]
    Civil_e_claimant_harassment_op4 = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment_op4"]

    # OSLAS Criteria Civil(f) claimant harassment database
    OCCivil_f_claimant_harassment = list(col_oslas_criteria.find({"QN": "22"}))[0]
    Civil_f_claimant_harassment = OCCivil_f_claimant_harassment["Civil_f_claimant_harassment"]
    Civil_f_claimant_harassment_op1 = OCCivil_f_claimant_harassment["Civil_f_claimant_harassment_op1"]
    Civil_f_claimant_harassment_op2 = OCCivil_f_claimant_harassment["Civil_f_claimant_harassment_op2"]

    # OSLAS Criteria Civil(g)(i) claimant harassment database
    OCCivil_g_i_claimant_harassment = list(col_oslas_criteria.find({"QN": "23"}))[0]
    Civil_g_i_claimant_harassment = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment"]
    Civil_g_i_claimant_harassment_op1 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op1"]
    Civil_g_i_claimant_harassment_op2 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op2"]
    Civil_g_i_claimant_harassment_op3 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op3"]
    Civil_g_i_claimant_harassment_op4 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op4"]
    Civil_g_i_claimant_harassment_op5 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op5"]

    # OSLAS Criteria Civil(g)(ii) claimant harassment database
    OCCivil_g_ii_claimant_harassment = list(col_oslas_criteria.find({"QN": "24"}))[0]
    Civil_g_ii_claimant_harassment = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment"]
    Civil_g_ii_claimant_harassment_op1 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op1"]
    Civil_g_ii_claimant_harassment_op2 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op2"]
    Civil_g_ii_claimant_harassment_op3 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op3"]
    Civil_g_ii_claimant_harassment_op4 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op4"]
    Civil_g_ii_claimant_harassment_op5 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op5"]

    # OSLAS Criteria Civil(c) respondent harassment database
    OCCivil_c_respondent_harassment = list(col_oslas_criteria.find({"QN": "25"}))[0]
    Civil_c_respondent_harassment = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment"]
    Civil_c_respondent_harassment_op1 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op1"]
    Civil_c_respondent_harassment_op2 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op2"]
    Civil_c_respondent_harassment_op3 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op3"]
    Civil_c_respondent_harassment_op4 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op4"]
    Civil_c_respondent_harassment_op5 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op5"]

    # OSLAS Criteria Civil(d) respondent harassment database
    OCCivil_d_respondent_harassment = list(col_oslas_criteria.find({"QN": "26"}))[0]
    Civil_d_respondent_harassment = OCCivil_d_respondent_harassment["Civil_d_respondent_harassment"]
    Civil_d_respondent_harassment_op1 = OCCivil_d_respondent_harassment["Civil_d_respondent_harassment_op1"]
    Civil_d_respondent_harassment_op2 = OCCivil_d_respondent_harassment["Civil_d_respondent_harassment_op2"]

    # OSLAS Criteria Civil(e)(i) respondent harassment database
    OCCivil_e_i_respondent_harassment = list(col_oslas_criteria.find({"QN": "27"}))[0]
    Civil_e_i_respondent_harassment = OCCivil_e_i_respondent_harassment["Civil_e_i_respondent_harassment"]
    Civil_e_i_respondent_harassment_op1 = OCCivil_e_i_respondent_harassment["Civil_e_i_respondent_harassment_op1"]
    Civil_e_i_respondent_harassment_op2 = OCCivil_e_i_respondent_harassment["Civil_e_i_respondent_harassment_op2"]
    Civil_e_i_respondent_harassment_op3 = OCCivil_e_i_respondent_harassment["Civil_e_i_respondent_harassment_op3"]

    # OSLAS Criteria Civil(e)(ii) respondent harassment database
    OCCivil_e_ii_respondent_harassment = list(col_oslas_criteria.find({"QN": "28"}))[0]
    Civil_e_ii_respondent_harassment = OCCivil_e_ii_respondent_harassment["Civil_e_ii_respondent_harassment"]
    Civil_e_ii_respondent_harassment_op1 = OCCivil_e_ii_respondent_harassment["Civil_e_ii_respondent_harassment_op1"]

    # OSLAS Criteria Civil(f) respondent harassment database
    OCCivil_f_respondent_harassment = list(col_oslas_criteria.find({"QN": "29"}))[0]
    Civil_f_respondent_harassment = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment"]
    Civil_f_respondent_harassment_op1 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op1"]
    Civil_f_respondent_harassment_op2 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op2"]
    Civil_f_respondent_harassment_op3 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op3"]
    Civil_f_respondent_harassment_op4 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op4"]
    Civil_f_respondent_harassment_op5 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op5"]

    # OSLAS Criteria Family database
    OCFamily = list(col_oslas_criteria.find({"QN": "30"}))[0]
    Family_i = OCFamily["Family_i"]
    Family_i_op1 = OCFamily["Family_i_op1"]
    Family_i_op2 = OCFamily["Family_i_op2"]
    Family_i_op3 = OCFamily["Family_i_op3"]
    Family_i_op4 = OCFamily["Family_i_op4"]
    Family_ii = OCFamily["Family_ii"]
    Family_ii_prompt = OCFamily["Family_ii_prompt"]
    Family_ii_op1 = OCFamily["Family_ii_op1"]
    Family_ii_op2 = OCFamily["Family_ii_op2"]
    Family_ii_op3 = OCFamily["Family_ii_op3"]

    # OSLAS Criteria Criminal database
    OCCriminal = list(col_oslas_criteria.find({"QN": "31"}))[0]
    Criminal = OCCriminal["Criminal"]
    Criminal_op1 = OCCriminal["Criminal_op1"]
    Criminal_op2 = OCCriminal["Criminal_op2"]
    Criminal_op3 = OCCriminal["Criminal_op3"]
    Criminal_op4 = OCCriminal["Criminal_op4"]
    Criminal_op5 = OCCriminal["Criminal_op5"]
    Criminal_op6 = OCCriminal["Criminal_op6"]
    Criminal_op7 = OCCriminal["Criminal_op7"]

    if request.method == "POST":
        Question1 = request.form.getlist('Question1')
        Question2 = request.form.getlist('Question2')
        Question3 = request.form.getlist('Question3')
        Question4 = request.form.getlist('Question4')
        Question5a = request.form.getlist('Question5a')
        Question5b = request.form.getlist('Question5b')

        Question5c_claimant = request.form.getlist('Question5c_claimant')
        Question5d_claimant = request.form.getlist('Question5d_claimant')

        Question5c_claimant_employment = request.form.getlist('Question5c_claimant_employment')
        Question5d_claimant_employment = request.form.getlist('Question5d_claimant_employment')
        Question5e_claimant_employment = request.form.getlist('Question5e_claimant_employment')


        Question5c_respondent = request.form.getlist('Question5c_respondent')
        Question5c_respondent_employment = request.form.getlist('Question5c_respondent_employment')
        Question5d_respondent_employment = request.form.getlist('Question5d_respondent_employment')

        Question5c_claimant_neighbour = request.form.getlist('Question5c_claimant_neighbour')
        Question5d_claimant_neighbour = request.form.getlist('Question5d_claimant_neighbour')

        Question5c_respondent_neighbour = request.form.getlist('Question5c_respondent_neighbour')

        QuestionResolve_the_dispute_online = request.form.getlist('QuestionResolve_the_dispute_online')

        Question5c_claimant_harassment = request.form.getlist('Question5c_claimant_harassment')
        Question5d_claimant_harassment = request.form.getlist('Question5d_claimant_harassment')
        Question5e_claimant_harassment = request.form.getlist('Question5e_claimant_harassment')
        Question5f_claimant_harassment = request.form.getlist('Question5f_claimant_harassment')
        Question5g_i_claimant_harassment = request.form.getlist('Question5g_i_claimant_harassment')
        Question5g_ii_claimant_harassment = request.form.getlist('Question5g_ii_claimant_harassment')

        Question5c_respondent_harassment = request.form.getlist('Question5c_respondent_harassment')
        Question5d_respondent_harassment = request.form.getlist('Question5d_respondent_harassment')
        Question5e_i_respondent_harassment = request.form.getlist('Question5e_i_respondent_harassment')
        Question5e_ii_respondent_harassment = request.form.getlist('Question5e_ii_respondent_harassment')
        Question5f_respondent_harassment = request.form.getlist('Question5f_respondent_harassment')

        Criminal5 = request.form.getlist('Criminal5')

        Family_Question5a = request.form.getlist('Family_Question5a')
        Family_Question5b = request.form.getlist('Family_Question5b')

        # When the answer for Question 1 is "Yes"
        if Question1[0] == OCQ1op1:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 2 is "Yes"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op1:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 3 is "Yes"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op1:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Criminal"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op2:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "Please select all that applies": Criminal5,
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Family"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op3:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "i. Integrated Family Application Management System (iFAMS)": Family_Question5a,
                "ii. Divorce application (simplified track)": Family_Question5b,
                "Current Date": datetime.now()
                })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant/Respondent" and Question 5b is "None of the above"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5b[0] == Civil_b_op8:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Tenancy/Contract for Sale/Provision/Damage to Property", and Question 5c is "Appeal/Set/Execute/None"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and (Question5b[0] == Civil_b_op1 or Question5b[0] == Civil_b_op2 or  Question5b[0] == Civil_b_op3 or Question5b[0] ==  Civil_b_op4) and (Question5c_claimant[0] == Civil_c_claimant_op2 or Question5c_claimant[0] == Civil_c_claimant_op3 or Question5c_claimant[0] == Civil_c_claimant_op4 or Question5c_claimant[0] == Civil_c_claimant_op5):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I want to": Question5c_claimant[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Tenancy/Contract for Sale/Provision/Damage to Property", and Question 5c is "File a Claim"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and (Question5b[0] == Civil_b_op1 or Question5b[0] == Civil_b_op2 or  Question5b[0] == Civil_b_op3 or Question5b[0] == Civil_b_op4) and Question5c_claimant[0] == Civil_c_claimant_op1:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I want to": Question5c_claimant[0],
                "My claim is": Question5d_claimant,
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Employment", Question 5c is both selected, Question 5d is "File a Claim"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op5 and Question5d_claimant_employment[0] == Civil_d_claimant_employment_op1:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "My current situation": Question5c_claimant_employment,
                "I wish to": Question5d_claimant_employment[0],
                "I have...": Question5e_claimant_employment,
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Employment", Question 5c is both selected, Question 5d is "Resolve the dispute online"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op5 and Question5d_claimant_employment[0] == Civil_d_claimant_employment_op2:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "My current situation": Question5c_claimant_employment,
                "I wish to": Question5d_claimant_employment[0],
                "I would like to resolve the dispute filed through the Community Justice and Tribunals System (CJTS), without going to court, via the followings:": QuestionResolve_the_dispute_online[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Employment", Question 5c is both selected, Question 5d is "Appeal/Enforce/Set/None"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op5 and (Question5d_claimant_employment[0] == Civil_d_claimant_employment_op3 or Question5d_claimant_employment[0] == Civil_d_claimant_employment_op4 or Question5d_claimant_employment[0] == Civil_d_claimant_employment_op5 or Question5d_claimant_employment[0] == Civil_d_claimant_employment_op6):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "My current situation": Question5c_claimant_employment,
                "I wish to": Question5d_claimant_employment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Tenancy/Contract for Sale/Provision/Damage to Property"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and (Question5b[0] == Civil_b_op1 or Question5b[0] == Civil_b_op2 or Question5b[0] == Civil_b_op3 or Question5b[0] == Civil_b_op4):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I want to": Question5c_respondent[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Employment", Question 5d is "Settle/Dispute/Counterclaim/Appeal/SetAside/None"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and Question5b[0] == Civil_b_op5 and (Question5d_respondent_employment[0] == Civil_d_respondent_employment_op1 or Question5d_respondent_employment[0] == Civil_d_respondent_employment_op2 or Question5d_respondent_employment[0] == Civil_d_respondent_employment_op3 or Question5d_respondent_employment[0] == Civil_d_respondent_employment_op5 or Question5d_respondent_employment[0] == Civil_d_respondent_employment_op6 or Question5d_respondent_employment[0] == Civil_d_respondent_employment_op7):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "My current situation": Question5c_respondent_employment[0],
                "I wish to": Question5d_respondent_employment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Employment", Question 5d is "Resolve the dispute online"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and Question5b[0] == Civil_b_op5 and Question5d_respondent_employment[0] == Civil_d_respondent_employment_op4:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "My current situation": Question5c_respondent_employment[0],
                "I wish to": Question5d_respondent_employment[0],
                "I would like to resolve the dispute filed through the Community Justice and Tribunals System (CJTS), without going to court, via the followings:": QuestionResolve_the_dispute_online[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Neighbour", Question 5c is "Appeal/Enforce/SetAside/None"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op6 and (Question5c_claimant_neighbour[0] == Civil_c_claimant_neighbour_op3 or Question5c_claimant_neighbour[0] == Civil_c_claimant_neighbour_op4 or Question5c_claimant_neighbour[0] == Civil_c_claimant_neighbour_op5 or Question5c_claimant_neighbour[0] == Civil_c_claimant_neighbour_op6):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_neighbour[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Neighbour", Question 5c is "File a Claim"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op6 and Question5c_claimant_neighbour[0] == Civil_c_claimant_neighbour_op1:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_neighbour[0],
                "I have...": Question5d_claimant_neighbour,
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Neighbour", Question 5c is "Resolve the dispute online"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op6 and Question5c_claimant_neighbour[0] == Civil_c_claimant_neighbour_op2:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_neighbour[0],
                "I would like to resolve the dispute filed through the Community Justice and Tribunals System (CJTS), without going to court, via the followings:": QuestionResolve_the_dispute_online[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Neighbour", Question 5c is "Resolve the dispute online"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and Question5b[0] == Civil_b_op6 and Question5c_respondent_neighbour[0] == Civil_c_respondent_neighbour_op3:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_respondent_neighbour[0],
                "I would like to resolve the dispute filed through the Community Justice and Tribunals System (CJTS), without going to court, via the followings:": QuestionResolve_the_dispute_online[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Neighbour", Question 5c is "Settle/Dispute/Appeal/SetAside/None"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and Question5b[0] == Civil_b_op6 and (Question5c_respondent_neighbour[0] == Civil_c_respondent_neighbour_op1 or Question5c_respondent_neighbour[0] == Civil_c_respondent_neighbour_op2 or Question5c_respondent_neighbour[0] == Civil_c_respondent_neighbour_op4 or Question5c_respondent_neighbour[0] == Civil_c_respondent_neighbour_op5 or Question5c_respondent_neighbour[0] == Civil_c_respondent_neighbour_op6):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_respondent_neighbour[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Harassment", Question 5c is "Appeal against a protection from harassment decision" or "Enforce a protection from harassment order" or "Set aside a protection from harassment order made in my absence" or "Vary, suspend or cancel a protection from harassment order" or "None of the above"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op7 and (Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op2 or Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op3 or Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op4 or Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op5 or Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op6):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_harassment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Harassment", Question 5c is "File a Claim" and Question 5d is "None of the above"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op7 and Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op1 and Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op4:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_harassment[0],
                "My claim is": Question5d_claimant_harassment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Harassment", Question 5c is "File a Claim" and Question 5d is "Against up to 5 respondents"/"By only 1 claimant (myself)"/"Filed within 2 years of the event which creates the cause of action"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op7 and Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op1 and (Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op1 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op2 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op3):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_harassment[0],
                "My claim is": Question5d_claimant_harassment,
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Harassment", Question 5c is "File a Claim" and Question 5d is "Against up to 5 respondents"/"By only 1 claimant (myself)"/"Filed within 2 years of the event which creates the cause of action" and Question 5e is "Punished through a jail term or a fine, or both" or "None of the above"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op7 and Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op1 and (Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op1 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op2 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op3) and (Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op1 or Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op4):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_harassment[0],
                "My claim is": Question5d_claimant_harassment,
                "I want the harasser to be": Question5e_claimant_harassment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Harassment", Question 5c is "File a Claim" and Question 5d is "Against up to 5 respondents"/"By only 1 claimant (myself)"/"Filed within 2 years of the event which creates the cause of action" and Question 5e is "Punished through a jail term or a fine, or both" or "None of the above"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op7 and Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op1 and (Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op1 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op2 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op3) and (Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op1 or Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op4):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_harassment[0],
                "My claim is": Question5d_claimant_harassment,
                "I want the harasser to be": Question5e_claimant_harassment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Harassment", Question 5c is "File a Claim" and Question 5d is "Against up to 5 respondents"/"By only 1 claimant (myself)"/"Filed within 2 years of the event which creates the cause of action" and Question 5e is "Ordered to pay up to $20 000 in monetary compensation." or "Ordered to stop harassing behaviour, undergo psychiatric treatment, stop spreading false statement of fact or comply with other related civil law remedies." and Question 5f is "A Final Order (without an interim order)" and Question 5gi is "None of the above"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op7 and Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op1 and (Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op1 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op2 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op3) and (Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op2 or Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op3) and Question5f_claimant_harassment[0] == Civil_f_claimant_harassment_op1 and Question5g_i_claimant_harassment[0] == Civil_g_i_claimant_harassment_op5:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_harassment[0],
                "My claim is": Question5d_claimant_harassment,
                "I want the harasser to be": Question5e_claimant_harassment[0],
                "I am seeking for": Question5f_claimant_harassment[0],
                "I have": Question5g_i_claimant_harassment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Harassment", Question 5c is "File a Claim" and Question 5d is "Against up to 5 respondents"/"By only 1 claimant (myself)"/"Filed within 2 years of the event which creates the cause of action" and Question 5e is "Ordered to pay up to $20 000 in monetary compensation." or "Ordered to stop harassing behaviour, undergo psychiatric treatment, stop spreading false statement of fact or comply with other related civil law remedies." and Question 5f is "A Final Order (without an interim order)"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op7 and Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op1 and (Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op1 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op2 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op3) and (Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op2 or Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op3) and Question5f_claimant_harassment[0] == Civil_f_claimant_harassment_op1 and (Question5g_i_claimant_harassment[0] == Civil_g_i_claimant_harassment_op1 or Question5g_i_claimant_harassment[0] == Civil_g_i_claimant_harassment_op2 or Question5g_i_claimant_harassment[0] == Civil_g_i_claimant_harassment_op3 or Question5g_i_claimant_harassment[0] == Civil_g_i_claimant_harassment_op4):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_harassment[0],
                "My claim is": Question5d_claimant_harassment,
                "I want the harasser to be": Question5e_claimant_harassment[0],
                "I am seeking for": Question5f_claimant_harassment[0],
                "I have": Question5g_i_claimant_harassment,
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Harassment", Question 5c is "File a Claim" and Question 5d is "Against up to 5 respondents"/"By only 1 claimant (myself)"/"Filed within 2 years of the event which creates the cause of action" and Question 5e is "Ordered to pay up to $20 000 in monetary compensation." or "Ordered to stop harassing behaviour, undergo psychiatric treatment, stop spreading false statement of fact or comply with other related civil law remedies." and Question 5f is "A Final Order and an interim order" and Question 5gii is "None of the above"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op7 and Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op1 and (Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op1 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op2 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op3) and (Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op2 or Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op3) and Question5f_claimant_harassment[0] == Civil_f_claimant_harassment_op2 and Question5g_ii_claimant_harassment[0] == Civil_g_ii_claimant_harassment_op5:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_harassment[0],
                "My claim is": Question5d_claimant_harassment,
                "I want the harasser to be": Question5e_claimant_harassment[0],
                "I am seeking for": Question5f_claimant_harassment[0],
                "I have": Question5g_ii_claimant_harassment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Claimant", Question 5b is "Harassment", Question 5c is "File a Claim" and Question 5d is "Against up to 5 respondents"/"By only 1 claimant (myself)"/"Filed within 2 years of the event which creates the cause of action" and Question 5e is "Ordered to pay up to $20 000 in monetary compensation." or "Ordered to stop harassing behaviour, undergo psychiatric treatment, stop spreading false statement of fact or comply with other related civil law remedies." and Question 5f is "A Final Order and an interim order"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op1 and Question5b[0] == Civil_b_op7 and Question5c_claimant_harassment[0] == Civil_c_claimant_harassment_op1 and (Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op1 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op2 or Question5d_claimant_harassment[0] == Civil_d_claimant_harassment_op3) and (Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op2 or Question5e_claimant_harassment[0] == Civil_e_claimant_harassment_op3) and Question5f_claimant_harassment[0] == Civil_f_claimant_harassment_op2 and (Question5g_ii_claimant_harassment[0] == Civil_g_ii_claimant_harassment_op1 or Question5g_ii_claimant_harassment[0] == Civil_g_ii_claimant_harassment_op2 or Question5g_ii_claimant_harassment[0] == Civil_g_ii_claimant_harassment_op3 or Question5g_ii_claimant_harassment[0] == Civil_g_ii_claimant_harassment_op4):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_claimant_harassment[0],
                "My claim is": Question5d_claimant_harassment,
                "I want the harasser to be": Question5e_claimant_harassment[0],
                "I am seeking for": Question5f_claimant_harassment[0],
                "I have": Question5g_ii_claimant_harassment,
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Harassment", Question 5c is "Appeal against a protection from harassment decision" or "Set aside a protection from harassment order made in my absence" or "Vary, suspend or cancel a protection from harassment order" or "None of the above"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and Question5b[0] == Civil_b_op7 and (Question5c_respondent_harassment[0] == Civil_c_respondent_harassment_op2 or Question5c_respondent_harassment[0] == Civil_c_respondent_harassment_op3 or Question5c_respondent_harassment[0] == Civil_c_respondent_harassment_op4 or Question5c_respondent_harassment[0] == Civil_c_respondent_harassment_op5):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_respondent_harassment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Harassment", Question 5c is "Respond to a Claim", Question 5d is "Notice of Case Management Conference" and 5e is "Settle the claim" or "Dispute the claim: file a response"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and Question5b[0] == Civil_b_op7 and Question5c_respondent_harassment[0] == Civil_c_respondent_harassment_op1 and Question5d_respondent_harassment[0] == Civil_d_respondent_harassment_op1 and (Question5e_i_respondent_harassment[0] == Civil_e_i_respondent_harassment_op1 or Question5e_i_respondent_harassment[0] == Civil_e_i_respondent_harassment_op2):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_respondent_harassment[0],
                "I have received a/an": Question5d_respondent_harassment[0],
                "I am seeking to": Question5e_i_respondent_harassment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Harassment", Question 5c is "Respond to a Claim", Question 5d is "Notice of Case Management Conference" and 5e is "File a counterclaim" and 5f is "None of the above"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and Question5b[0] == Civil_b_op7 and Question5c_respondent_harassment[0] == Civil_c_respondent_harassment_op1 and Question5d_respondent_harassment[0] == Civil_d_respondent_harassment_op1 and Question5e_i_respondent_harassment[0] == Civil_e_i_respondent_harassment_op3 and Question5f_respondent_harassment[0] == Civil_f_respondent_harassment_op5:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_respondent_harassment[0],
                "I have received a/an": Question5d_respondent_harassment[0],
                "I am seeking to": Question5e_i_respondent_harassment[0],
                "I have": Question5f_respondent_harassment[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Harassment", Question 5c is "Respond to a Claim", Question 5d is "Notice of Case Management Conference" and 5e is "File a counterclaim" and 5f is "Completed the pre-filing assessment on the Community Justice and Tribunals System (CJTS)"/"Filed my claim on the Community Justice and Tribunals System (CJTS)"/"Attended the hearing"/"Served the documents on the respondents"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and Question5b[0] == Civil_b_op7 and Question5c_respondent_harassment[0] == Civil_c_respondent_harassment_op1 and Question5d_respondent_harassment[0] == Civil_d_respondent_harassment_op1 and Question5e_i_respondent_harassment[0] == Civil_e_i_respondent_harassment_op3 and (Question5f_respondent_harassment[0] == Civil_f_respondent_harassment_op1 or Question5f_respondent_harassment[0] == Civil_f_respondent_harassment_op2 or Question5f_respondent_harassment[0] == Civil_f_respondent_harassment_op3 or Question5f_respondent_harassment[0] == Civil_f_respondent_harassment_op4):
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_respondent_harassment[0],
                "I have received a/an": Question5d_respondent_harassment[0],
                "I am seeking to": Question5e_i_respondent_harassment[0],
                "I have": Question5f_respondent_harassment,
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Civil", Question 5a is "Respondent", Question 5b is "Harassment", Question 5c is "Respond to a Claim", Question 5d is "Originating Application" and 5e is "Dispute the claim"
        if Question1[0] == OCQ1op2 and Question2[0] == OCQ2op2 and Question3[0] == OCQ3op2 and Question4[0] == OCQ4op1 and Question5a[0] == Civil_a_op2 and Question5b[0] == Civil_b_op7 and Question5c_respondent_harassment[0] == Civil_c_respondent_harassment_op1 and Question5d_respondent_harassment[0] == Civil_d_respondent_harassment_op2 and Question5e_ii_respondent_harassment[0] == Civil_e_ii_respondent_harassment_op1:
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "I am the": Question5a[0],
                "My claim arises from": Question5b[0],
                "I wish to": Question5c_respondent_harassment[0],
                "I have received a/an": Question5d_respondent_harassment[0],
                "I am seeking to": Question5e_ii_respondent_harassment[0],
                "Current Date": datetime.now()
            })

    return render_template('oslas_criteria.html', OCQ1 = OCQ1, OCQ1op1 = OCQ1op1, OCQ1op2 = OCQ1op2,
    OCQ2 = OCQ2, OCQ2op1 = OCQ2op1, OCQ2op2 = OCQ2op2,
    OCQ3 = OCQ3, OCQ3op1 = OCQ3op1, OCQ3op2 = OCQ3op2,
    OCQ4 = OCQ4, OCQ4op1 = OCQ4op1, OCQ4op2 = OCQ4op2, OCQ4op3 = OCQ4op3,
    OCQ5 = OCQ5,
    Introduction_message = Introduction_message,
    Civil_a = Civil_a, Civil_a_op1 = Civil_a_op1, Civil_a_op2 = Civil_a_op2,
    Civil_b = Civil_b, Civil_b_op1 = Civil_b_op1, Civil_b_op2 = Civil_b_op2, Civil_b_op3 = Civil_b_op3, Civil_b_op4 = Civil_b_op4, Civil_b_op5 = Civil_b_op5, Civil_b_op6 = Civil_b_op6, Civil_b_op7 = Civil_b_op7, Civil_b_op8 = Civil_b_op8,
    Civil_c_respondent = Civil_c_respondent, Civil_c_respondent_op1 = Civil_c_respondent_op1, Civil_c_respondent_op2 = Civil_c_respondent_op2, Civil_c_respondent_op3 = Civil_c_respondent_op3, Civil_c_respondent_op4 = Civil_c_respondent_op4, Civil_c_respondent_op5 = Civil_c_respondent_op5, Civil_c_respondent_op6 = Civil_c_respondent_op6,
    Civil_c_claimant = Civil_c_claimant, Civil_c_claimant_op1 = Civil_c_claimant_op1, Civil_c_claimant_op2 = Civil_c_claimant_op2, Civil_c_claimant_op3 = Civil_c_claimant_op3, Civil_c_claimant_op4 = Civil_c_claimant_op4, Civil_c_claimant_op5 = Civil_c_claimant_op5,
    Civil_c_employment = Civil_c_employment, Civil_c_claimant_employment_op1 = Civil_c_claimant_employment_op1, Civil_c_claimant_employment_op2 = Civil_c_claimant_employment_op2, Civil_c_respondent_employment_op1 = Civil_c_respondent_employment_op1, Civil_c_employment_none = Civil_c_employment_none,
    Civil_d_claimant = Civil_d_claimant, Civil_d_claimant_op1 = Civil_d_claimant_op1, Civil_d_claimant_op2 = Civil_d_claimant_op2, Civil_d_claimant_op3 = Civil_d_claimant_op3,
    Civil_d_claimant_employment = Civil_d_claimant_employment, Civil_d_claimant_employment_op1 = Civil_d_claimant_employment_op1, Civil_d_claimant_employment_op2 = Civil_d_claimant_employment_op2, Civil_d_claimant_employment_op3 = Civil_d_claimant_employment_op3, Civil_d_claimant_employment_op4 = Civil_d_claimant_employment_op4, Civil_d_claimant_employment_op5 = Civil_d_claimant_employment_op5, Civil_d_claimant_employment_op6 = Civil_d_claimant_employment_op6,
    Civil_d_respondent_employment = Civil_d_respondent_employment, Civil_d_respondent_employment_op1 = Civil_d_respondent_employment_op1, Civil_d_respondent_employment_op2 = Civil_d_respondent_employment_op2, Civil_d_respondent_employment_op3 = Civil_d_respondent_employment_op3, Civil_d_respondent_employment_op4 = Civil_d_respondent_employment_op4, Civil_d_respondent_employment_op5 = Civil_d_respondent_employment_op5, Civil_d_respondent_employment_op6 = Civil_d_respondent_employment_op6, Civil_d_respondent_employment_op7 = Civil_d_respondent_employment_op7,
    Civil_e_claimant_employment = Civil_e_claimant_employment, Civil_e_claimant_employment_op1 = Civil_e_claimant_employment_op1, Civil_e_claimant_employment_op2 = Civil_e_claimant_employment_op2, Civil_e_claimant_employment_op3 = Civil_e_claimant_employment_op3, Civil_e_claimant_employment_op4 = Civil_e_claimant_employment_op4, Civil_e_claimant_employment_op5 = Civil_e_claimant_employment_op5,
    Resolve_the_dispute_online = Resolve_the_dispute_online, Resolve_the_dispute_online_op1 = Resolve_the_dispute_online_op1, Resolve_the_dispute_online_op2 = Resolve_the_dispute_online_op2, Resolve_the_dispute_online_op3 = Resolve_the_dispute_online_op3,
    Civil_c_claimant_neighbour = Civil_c_claimant_neighbour, Civil_c_claimant_neighbour_op1 = Civil_c_claimant_neighbour_op1, Civil_c_claimant_neighbour_op2 = Civil_c_claimant_neighbour_op2, Civil_c_claimant_neighbour_op3 = Civil_c_claimant_neighbour_op3, Civil_c_claimant_neighbour_op4 = Civil_c_claimant_neighbour_op4, Civil_c_claimant_neighbour_op5 = Civil_c_claimant_neighbour_op5, Civil_c_claimant_neighbour_op6 = Civil_c_claimant_neighbour_op6,
    Civil_d_claimant_neighbour = Civil_d_claimant_neighbour, Civil_d_claimant_neighbour_op1 = Civil_d_claimant_neighbour_op1, Civil_d_claimant_neighbour_op2 = Civil_d_claimant_neighbour_op2, Civil_d_claimant_neighbour_op3 = Civil_d_claimant_neighbour_op3, Civil_d_claimant_neighbour_op4 = Civil_d_claimant_neighbour_op4, Civil_d_claimant_neighbour_op5 = Civil_d_claimant_neighbour_op5, Civil_d_claimant_neighbour_op6 = Civil_d_claimant_neighbour_op6,
    Civil_c_respondent_neighbour = Civil_c_respondent_neighbour, Civil_c_respondent_neighbour_op1 = Civil_c_respondent_neighbour_op1, Civil_c_respondent_neighbour_op2 = Civil_c_respondent_neighbour_op2, Civil_c_respondent_neighbour_op3 = Civil_c_respondent_neighbour_op3, Civil_c_respondent_neighbour_op4 = Civil_c_respondent_neighbour_op4, Civil_c_respondent_neighbour_op5 = Civil_c_respondent_neighbour_op5, Civil_c_respondent_neighbour_op6 = Civil_c_respondent_neighbour_op6,
    Civil_c_claimant_harassment = Civil_c_claimant_harassment, Civil_c_claimant_harassment_op1 = Civil_c_claimant_harassment_op1, Civil_c_claimant_harassment_op2 = Civil_c_claimant_harassment_op2, Civil_c_claimant_harassment_op3 = Civil_c_claimant_harassment_op3, Civil_c_claimant_harassment_op4 = Civil_c_claimant_harassment_op4, Civil_c_claimant_harassment_op5 = Civil_c_claimant_harassment_op5, Civil_c_claimant_harassment_op6 = Civil_c_claimant_harassment_op6,
    Civil_d_claimant_harassment = Civil_d_claimant_harassment, Civil_d_claimant_harassment_op1 = Civil_d_claimant_harassment_op1, Civil_d_claimant_harassment_op2 = Civil_d_claimant_harassment_op2, Civil_d_claimant_harassment_op3 = Civil_d_claimant_harassment_op3, Civil_d_claimant_harassment_op4 = Civil_d_claimant_harassment_op4,
    Civil_e_claimant_harassment = Civil_e_claimant_harassment, Civil_e_claimant_harassment_op1 = Civil_e_claimant_harassment_op1, Civil_e_claimant_harassment_op2 = Civil_e_claimant_harassment_op2, Civil_e_claimant_harassment_op3 = Civil_e_claimant_harassment_op3, Civil_e_claimant_harassment_op4 = Civil_e_claimant_harassment_op4,
    Civil_f_claimant_harassment = Civil_f_claimant_harassment, Civil_f_claimant_harassment_op1 = Civil_f_claimant_harassment_op1, Civil_f_claimant_harassment_op2 = Civil_f_claimant_harassment_op2,
    Civil_g_i_claimant_harassment = Civil_g_i_claimant_harassment, Civil_g_i_claimant_harassment_op1 = Civil_g_i_claimant_harassment_op1, Civil_g_i_claimant_harassment_op2 = Civil_g_i_claimant_harassment_op2, Civil_g_i_claimant_harassment_op3 = Civil_g_i_claimant_harassment_op3, Civil_g_i_claimant_harassment_op4 = Civil_g_i_claimant_harassment_op4, Civil_g_i_claimant_harassment_op5 = Civil_g_i_claimant_harassment_op5,
    Civil_g_ii_claimant_harassment = Civil_g_ii_claimant_harassment, Civil_g_ii_claimant_harassment_op1 = Civil_g_ii_claimant_harassment_op1, Civil_g_ii_claimant_harassment_op2 = Civil_g_ii_claimant_harassment_op2, Civil_g_ii_claimant_harassment_op3 = Civil_g_ii_claimant_harassment_op3, Civil_g_ii_claimant_harassment_op4 = Civil_g_ii_claimant_harassment_op4, Civil_g_ii_claimant_harassment_op5 = Civil_g_ii_claimant_harassment_op5,
    Civil_c_respondent_harassment = Civil_c_respondent_harassment, Civil_c_respondent_harassment_op1 = Civil_c_respondent_harassment_op1, Civil_c_respondent_harassment_op2 = Civil_c_respondent_harassment_op2, Civil_c_respondent_harassment_op3 = Civil_c_respondent_harassment_op3, Civil_c_respondent_harassment_op4 = Civil_c_respondent_harassment_op4, Civil_c_respondent_harassment_op5 = Civil_c_respondent_harassment_op5,
    Civil_d_respondent_harassment = Civil_d_respondent_harassment, Civil_d_respondent_harassment_op1 = Civil_d_respondent_harassment_op1, Civil_d_respondent_harassment_op2 = Civil_d_respondent_harassment_op2,
    Civil_e_i_respondent_harassment = Civil_e_i_respondent_harassment, Civil_e_i_respondent_harassment_op1 = Civil_e_i_respondent_harassment_op1, Civil_e_i_respondent_harassment_op2 = Civil_e_i_respondent_harassment_op2, Civil_e_i_respondent_harassment_op3 = Civil_e_i_respondent_harassment_op3,
    Civil_e_ii_respondent_harassment = Civil_e_ii_respondent_harassment, Civil_e_ii_respondent_harassment_op1 = Civil_e_ii_respondent_harassment_op1,
    Civil_f_respondent_harassment = Civil_f_respondent_harassment, Civil_f_respondent_harassment_op1 = Civil_f_respondent_harassment_op1, Civil_f_respondent_harassment_op2 = Civil_f_respondent_harassment_op2, Civil_f_respondent_harassment_op3 = Civil_f_respondent_harassment_op3, Civil_f_respondent_harassment_op4 = Civil_f_respondent_harassment_op4, Civil_f_respondent_harassment_op5 = Civil_f_respondent_harassment_op5,
    Family_i = Family_i, Family_i_op1 = Family_i_op1, Family_i_op2 = Family_i_op2, Family_i_op3 = Family_i_op3, Family_i_op4 = Family_i_op4, Family_ii = Family_ii, Family_ii_prompt = Family_ii_prompt, Family_ii_op1 = Family_ii_op1, Family_ii_op2 = Family_ii_op2, Family_ii_op3 = Family_ii_op3,
    Criminal = Criminal, Criminal_op1 = Criminal_op1, Criminal_op2 = Criminal_op2, Criminal_op3 = Criminal_op3, Criminal_op4 = Criminal_op4, Criminal_op5 = Criminal_op5, Criminal_op6 = Criminal_op6, Criminal_op7 = Criminal_op7)

def suggest_advice(new_case_fact, threshold = 0.15):
    # Load the dataset
    df = pd.read_csv('/home/Jahnvi371/fyp/static/other/legal_data.csv')

    # Clean the dataset
    df = df.dropna()

    # Define stop words
    stop_words = set(stopwords.words('english'))
    stop_words_list = ["applicant", "maintenance"]
    for word in stop_words_list:
        stop_words.add(word)

    # Remove stop words from case facts and subtype
    df['Case Facts'] = df['Case Facts'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
    df['Sub-case Type'] = df['Sub-case Type'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))

    # Concatenate case facts and subtype
    df['Text'] = df['Case Facts'] + ' ' + df['Sub-case Type']

    # Transform the text into numerical vectors
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(df['Text'])

    # Transform the new case into a vector
    new_vector = vectorizer.transform([new_case_fact])

    # Compute the cosine similarity between the new vector and the past vectors
    similarities = cosine_similarity(new_vector, vectors)

    # Get the indices of the past cases with similarity score above the threshold
    similar_indices = similarities.argsort()[0][::-1]
    top_indices = [i for i in similar_indices if similarities[0][i] >= threshold][:3]

    # Get the corresponding case facts and advice for the top 3 most similar case facts
    top_case_facts = list(df.iloc[top_indices]['Case Facts'])
    top_advice = list(df.iloc[top_indices]['Advice'])

    top_dict = dict(zip(top_case_facts, top_advice))

    # Return the top 3 advice
    return top_case_facts, top_advice

@app.route('/admin/prescriptor')
def prescriptor():
    return render_template('prescriptor.html')

@app.route('/admin/get_advice', methods=['POST'])
def get_advice():
    # Get the legal issue from the POST request data
    case_facts = request.form['case_facts']

    # Call the suggest_advice() function to get the top case facts and advice
    top_case_facts, top_advice = suggest_advice(case_facts)

    # Return the top case facts and advice as a JSON object
    return jsonify(top_case_facts=top_case_facts, top_advice=top_advice)

@app.route('/admin/cms/oslas', methods=["POST", "GET"])
def oslas_cms():
    if request.method == "POST":
        Updated_Question1 = request.form.getlist('Question1')
        Updated_OCQ1op1 = request.form.getlist('OCQ1op1')
        Updated_OCQ1op2 = request.form.getlist('OCQ1op2')

        Updated_Question2 = request.form.getlist('Question2')
        Updated_OCQ2op1 = request.form.getlist('OCQ2op1')
        Updated_OCQ2op2 = request.form.getlist('OCQ2op2')

        Updated_Question3 = request.form.getlist('Question3')
        Updated_OCQ3op1 = request.form.getlist('OCQ3op1')
        Updated_OCQ3op2 = request.form.getlist('OCQ3op2')

        Updated_Question4 = request.form.getlist('Question4')
        Updated_OCQ4op1 = request.form.getlist('OCQ4op1')
        Updated_OCQ4op2 = request.form.getlist('OCQ4op2')
        Updated_OCQ4op3 = request.form.getlist('OCQ4op3')

        Updated_Question5 = request.form.getlist('Question5')

        Updated_Civil_a = request.form.getlist('Civil_a')
        Updated_Civil_a_op1 = request.form.getlist('Civil_a_op1')
        Updated_Civil_a_op2 = request.form.getlist('Civil_a_op2')

        Updated_Civil_b = request.form.getlist('Civil_b')
        Updated_Civil_b_op1 = request.form.getlist('Civil_b_op1')
        Updated_Civil_b_op2 = request.form.getlist('Civil_b_op2')
        Updated_Civil_b_op3 = request.form.getlist('Civil_b_op3')
        Updated_Civil_b_op4 = request.form.getlist('Civil_b_op4')
        Updated_Civil_b_op5 = request.form.getlist('Civil_b_op5')
        Updated_Civil_b_op6 = request.form.getlist('Civil_b_op6')
        Updated_Civil_b_op7 = request.form.getlist('Civil_b_op7')
        Updated_Civil_b_op8 = request.form.getlist('Civil_b_op8')

        Updated_Civil_c_respondent = request.form.getlist('Civil_c_respondent')
        Updated_Civil_c_respondent_op1 = request.form.getlist('Civil_c_respondent_op1')
        Updated_Civil_c_respondent_op2 = request.form.getlist('Civil_c_respondent_op2')
        Updated_Civil_c_respondent_op3 = request.form.getlist('Civil_c_respondent_op3')
        Updated_Civil_c_respondent_op4 = request.form.getlist('Civil_c_respondent_op4')
        Updated_Civil_c_respondent_op5 = request.form.getlist('Civil_c_respondent_op5')
        Updated_Civil_c_respondent_op6 = request.form.getlist('Civil_c_respondent_op6')

        Updated_Civil_c_claimant = request.form.getlist('Civil_c_claimant')
        Updated_Civil_c_claimant_op1 = request.form.getlist('Civil_c_claimant_op1')
        Updated_Civil_c_claimant_op2 = request.form.getlist('Civil_c_claimant_op2')
        Updated_Civil_c_claimant_op3 = request.form.getlist('Civil_c_claimant_op3')
        Updated_Civil_c_claimant_op4 = request.form.getlist('Civil_c_claimant_op4')
        Updated_Civil_c_claimant_op5 = request.form.getlist('Civil_c_claimant_op5')

        Updated_Civil_d_claimant = request.form.getlist('Civil_d_claimant')
        Updated_Civil_d_claimant_op1 = request.form.getlist('Civil_d_claimant_op1')
        Updated_Civil_d_claimant_op2 = request.form.getlist('Civil_d_claimant_op2')
        Updated_Civil_d_claimant_op3 = request.form.getlist('Civil_d_claimant_op3')

        Updated_Civil_c_employment = request.form.getlist('Civil_c_employment')
        Updated_Civil_c_employment_none = request.form.getlist('Civil_c_employment_none')
        Updated_Civil_c_claimant_employment_op1 = request.form.getlist('Civil_c_claimant_employment_op1')
        Updated_Civil_c_claimant_employment_op2 = request.form.getlist('Civil_c_claimant_employment_op2')
        Updated_Civil_c_respondent_employment_op1 = request.form.getlist('Civil_c_respondent_employment_op1')

        Updated_Civil_d_claimant_employment = request.form.getlist('Civil_d_claimant_employment')
        Updated_Civil_d_claimant_employment_op1 = request.form.getlist('Civil_d_claimant_employment_op1')
        Updated_Civil_d_claimant_employment_op2 = request.form.getlist('Civil_d_claimant_employment_op2')
        Updated_Civil_d_claimant_employment_op3 = request.form.getlist('Civil_d_claimant_employment_op3')
        Updated_Civil_d_claimant_employment_op4 = request.form.getlist('Civil_d_claimant_employment_op4')
        Updated_Civil_d_claimant_employment_op5 = request.form.getlist('Civil_d_claimant_employment_op5')
        Updated_Civil_d_claimant_employment_op6 = request.form.getlist('Civil_d_claimant_employment_op6')

        Updated_Civil_d_respondent_employment = request.form.getlist('Civil_d_respondent_employment')
        Updated_Civil_d_respondent_employment_op1 = request.form.getlist('Civil_d_respondent_employment_op1')
        Updated_Civil_d_respondent_employment_op2 = request.form.getlist('Civil_d_respondent_employment_op2')
        Updated_Civil_d_respondent_employment_op3 = request.form.getlist('Civil_d_respondent_employment_op3')
        Updated_Civil_d_respondent_employment_op4 = request.form.getlist('Civil_d_respondent_employment_op4')
        Updated_Civil_d_respondent_employment_op5 = request.form.getlist('Civil_d_respondent_employment_op5')
        Updated_Civil_d_respondent_employment_op6 = request.form.getlist('Civil_d_respondent_employment_op6')
        Updated_Civil_d_respondent_employment_op7 = request.form.getlist('Civil_d_respondent_employment_op7')

        Updated_Civil_e_claimant_employment = request.form.getlist('Civil_e_claimant_employment')
        Updated_Civil_e_claimant_employment_op1 = request.form.getlist('Civil_e_claimant_employment_op1')
        Updated_Civil_e_claimant_employment_op2 = request.form.getlist('Civil_e_claimant_employment_op2')
        Updated_Civil_e_claimant_employment_op3 = request.form.getlist('Civil_e_claimant_employment_op3')
        Updated_Civil_e_claimant_employment_op4 = request.form.getlist('Civil_e_claimant_employment_op4')
        Updated_Civil_e_claimant_employment_op5 = request.form.getlist('Civil_e_claimant_employment_op5')

        Updated_Resolve_the_dispute_online = request.form.getlist('Resolve_the_dispute_online')
        Updated_Resolve_the_dispute_online_op1 = request.form.getlist('Resolve_the_dispute_online_op1')
        Updated_Resolve_the_dispute_online_op2 = request.form.getlist('Resolve_the_dispute_online_op2')
        Updated_Resolve_the_dispute_online_op3 = request.form.getlist('Resolve_the_dispute_online_op3')

        Updated_Civil_c_claimant_neighbour = request.form.getlist('Civil_c_claimant_neighbour')
        Updated_Civil_c_claimant_neighbour_op1 = request.form.getlist('Civil_c_claimant_neighbour_op1')
        Updated_Civil_c_claimant_neighbour_op2 = request.form.getlist('Civil_c_claimant_neighbour_op2')
        Updated_Civil_c_claimant_neighbour_op3 = request.form.getlist('Civil_c_claimant_neighbour_op3')
        Updated_Civil_c_claimant_neighbour_op4 = request.form.getlist('Civil_c_claimant_neighbour_op4')
        Updated_Civil_c_claimant_neighbour_op5 = request.form.getlist('Civil_c_claimant_neighbour_op5')
        Updated_Civil_c_claimant_neighbour_op6 = request.form.getlist('Civil_c_claimant_neighbour_op6')

        Updated_Civil_d_claimant_neighbour = request.form.getlist('Civil_d_claimant_neighbour')
        Updated_Civil_d_claimant_neighbour_op1 = request.form.getlist('Civil_d_claimant_neighbour_op1')
        Updated_Civil_d_claimant_neighbour_op2 = request.form.getlist('Civil_d_claimant_neighbour_op2')
        Updated_Civil_d_claimant_neighbour_op3 = request.form.getlist('Civil_d_claimant_neighbour_op3')
        Updated_Civil_d_claimant_neighbour_op4 = request.form.getlist('Civil_d_claimant_neighbour_op4')
        Updated_Civil_d_claimant_neighbour_op5 = request.form.getlist('Civil_d_claimant_neighbour_op5')
        Updated_Civil_d_claimant_neighbour_op6 = request.form.getlist('Civil_d_claimant_neighbour_op6')

        Updated_Civil_c_respondent_neighbour = request.form.getlist('Civil_c_respondent_neighbour')
        Updated_Civil_c_respondent_neighbour_op1 = request.form.getlist('Civil_c_respondent_neighbour_op1')
        Updated_Civil_c_respondent_neighbour_op2 = request.form.getlist('Civil_c_respondent_neighbour_op2')
        Updated_Civil_c_respondent_neighbour_op3 = request.form.getlist('Civil_c_respondent_neighbour_op3')
        Updated_Civil_c_respondent_neighbour_op4 = request.form.getlist('Civil_c_respondent_neighbour_op4')
        Updated_Civil_c_respondent_neighbour_op5 = request.form.getlist('Civil_c_respondent_neighbour_op5')
        Updated_Civil_c_respondent_neighbour_op6 = request.form.getlist('Civil_c_respondent_neighbour_op6')

        Updated_Civil_c_claimant_harassment = request.form.getlist('Civil_c_claimant_harassment')
        Updated_Civil_c_claimant_harassment_op1 = request.form.getlist('Civil_c_claimant_harassment_op1')
        Updated_Civil_c_claimant_harassment_op2 = request.form.getlist('Civil_c_claimant_harassment_op2')
        Updated_Civil_c_claimant_harassment_op3 = request.form.getlist('Civil_c_claimant_harassment_op3')
        Updated_Civil_c_claimant_harassment_op4 = request.form.getlist('Civil_c_claimant_harassment_op4')
        Updated_Civil_c_claimant_harassment_op5 = request.form.getlist('Civil_c_claimant_harassment_op5')
        Updated_Civil_c_claimant_harassment_op6 = request.form.getlist('Civil_c_claimant_harassment_op6')

        Updated_Civil_d_claimant_harassment = request.form.getlist('Civil_d_claimant_harassment')
        Updated_Civil_d_claimant_harassment_op1 = request.form.getlist('Civil_d_claimant_harassment_op1')
        Updated_Civil_d_claimant_harassment_op2 = request.form.getlist('Civil_d_claimant_harassment_op2')
        Updated_Civil_d_claimant_harassment_op3 = request.form.getlist('Civil_d_claimant_harassment_op3')
        Updated_Civil_d_claimant_harassment_op4 = request.form.getlist('Civil_d_claimant_harassment_op4')

        Updated_Civil_e_claimant_harassment = request.form.getlist('Civil_e_claimant_harassment')
        Updated_Civil_e_claimant_harassment_op1 = request.form.getlist('Civil_e_claimant_harassment_op1')
        Updated_Civil_e_claimant_harassment_op2 = request.form.getlist('Civil_e_claimant_harassment_op2')
        Updated_Civil_e_claimant_harassment_op3 = request.form.getlist('Civil_e_claimant_harassment_op3')
        Updated_Civil_e_claimant_harassment_op4 = request.form.getlist('Civil_e_claimant_harassment_op4')

        Updated_Civil_f_claimant_harassment = request.form.getlist('Civil_f_claimant_harassment')
        Updated_Civil_f_claimant_harassment_op1 = request.form.getlist('Civil_f_claimant_harassment_op1')
        Updated_Civil_f_claimant_harassment_op2 = request.form.getlist('Civil_f_claimant_harassment_op2')

        Updated_Civil_g_i_claimant_harassment = request.form.getlist('Civil_g_i_claimant_harassment')
        Updated_Civil_g_i_claimant_harassment_op1 = request.form.getlist('Civil_g_i_claimant_harassment_op1')
        Updated_Civil_g_i_claimant_harassment_op2 = request.form.getlist('Civil_g_i_claimant_harassment_op2')
        Updated_Civil_g_i_claimant_harassment_op3 = request.form.getlist('Civil_g_i_claimant_harassment_op3')
        Updated_Civil_g_i_claimant_harassment_op4 = request.form.getlist('Civil_g_i_claimant_harassment_op4')
        Updated_Civil_g_i_claimant_harassment_op5 = request.form.getlist('Civil_g_i_claimant_harassment_op5')

        Updated_Civil_g_ii_claimant_harassment = request.form.getlist('Civil_g_ii_claimant_harassment')
        Updated_Civil_g_ii_claimant_harassment_op1 = request.form.getlist('Civil_g_ii_claimant_harassment_op1')
        Updated_Civil_g_ii_claimant_harassment_op2 = request.form.getlist('Civil_g_ii_claimant_harassment_op2')
        Updated_Civil_g_ii_claimant_harassment_op3 = request.form.getlist('Civil_g_ii_claimant_harassment_op3')
        Updated_Civil_g_ii_claimant_harassment_op4 = request.form.getlist('Civil_g_ii_claimant_harassment_op4')
        Updated_Civil_g_ii_claimant_harassment_op5 = request.form.getlist('Civil_g_ii_claimant_harassment_op5')

        Updated_Civil_c_respondent_harassment = request.form.getlist('Civil_c_respondent_harassment')
        Updated_Civil_c_respondent_harassment_op1 = request.form.getlist('Civil_c_respondent_harassment_op1')
        Updated_Civil_c_respondent_harassment_op2 = request.form.getlist('Civil_c_respondent_harassment_op2')
        Updated_Civil_c_respondent_harassment_op3 = request.form.getlist('Civil_c_respondent_harassment_op3')
        Updated_Civil_c_respondent_harassment_op4 = request.form.getlist('Civil_c_respondent_harassment_op4')
        Updated_Civil_c_respondent_harassment_op5 = request.form.getlist('Civil_c_respondent_harassment_op5')

        Updated_Civil_d_respondent_harassment = request.form.getlist('Civil_d_respondent_harassment')
        Updated_Civil_d_respondent_harassment_op1 = request.form.getlist('Civil_d_respondent_harassment_op1')
        Updated_Civil_d_respondent_harassment_op2 = request.form.getlist('Civil_d_respondent_harassment_op2')

        Updated_Civil_e_i_respondent_harassment = request.form.getlist('Civil_e_i_respondent_harassment')
        Updated_Civil_e_i_respondent_harassment_op1 = request.form.getlist('Civil_e_i_respondent_harassment_op1')
        Updated_Civil_e_i_respondent_harassment_op2 = request.form.getlist('Civil_e_i_respondent_harassment_op2')
        Updated_Civil_e_i_respondent_harassment_op3 = request.form.getlist('Civil_e_i_respondent_harassment_op3')

        Updated_Civil_e_ii_respondent_harassment = request.form.getlist('Civil_e_ii_respondent_harassment')
        Updated_Civil_e_ii_respondent_harassment_op1 = request.form.getlist('Civil_e_ii_respondent_harassment_op1')

        Updated_Civil_f_respondent_harassment = request.form.getlist('Civil_f_respondent_harassment')
        Updated_Civil_f_respondent_harassment_op1 = request.form.getlist('Civil_f_respondent_harassment_op1')
        Updated_Civil_f_respondent_harassment_op2 = request.form.getlist('Civil_f_respondent_harassment_op2')
        Updated_Civil_f_respondent_harassment_op3 = request.form.getlist('Civil_f_respondent_harassment_op3')
        Updated_Civil_f_respondent_harassment_op4 = request.form.getlist('Civil_f_respondent_harassment_op4')
        Updated_Civil_f_respondent_harassment_op5 = request.form.getlist('Civil_f_respondent_harassment_op5')

        Updated_Family_i = request.form.getlist('Family_i')
        Updated_Family_i_op1 = request.form.getlist('Family_i_op1')
        Updated_Family_i_op2 = request.form.getlist('Family_i_op2')
        Updated_Family_i_op3 = request.form.getlist('Family_i_op3')
        Updated_Family_i_op4 = request.form.getlist('Family_i_op4')
        Updated_Family_ii = request.form.getlist('Family_ii')
        Updated_Family_ii_prompt = request.form.getlist('Family_ii_prompt')
        Updated_Family_ii_op1 = request.form.getlist('Family_ii_op1')
        Updated_Family_ii_op2 = request.form.getlist('Family_ii_op2')
        Updated_Family_ii_op3 = request.form.getlist('Family_ii_op3')

        Updated_Criminal = request.form.getlist('Criminal')
        Updated_Criminal_op1 = request.form.getlist('Criminal_op1')
        Updated_Criminal_op2 = request.form.getlist('Criminal_op2')
        Updated_Criminal_op3 = request.form.getlist('Criminal_op3')
        Updated_Criminal_op4 = request.form.getlist('Criminal_op4')
        Updated_Criminal_op5 = request.form.getlist('Criminal_op5')
        Updated_Criminal_op6 = request.form.getlist('Criminal_op6')
        Updated_Criminal_op7 = request.form.getlist('Criminal_op7')

        Updated_Introduction_message = request.form.getlist('Introduction_message')

        col_oslas_criteria.update_one({"QN": "1"}, {'$set': {"OCQ1": Updated_Question1[0]}})
        col_oslas_criteria.update_one({"QN": "1"}, {'$set': {"OCQ1op1": Updated_OCQ1op1[0]}})
        col_oslas_criteria.update_one({"QN": "1"}, {'$set': {"OCQ1op2": Updated_OCQ1op2[0]}})

        col_oslas_criteria.update_one({"QN": "2"}, {'$set': {"OCQ2": Updated_Question2[0]}})
        col_oslas_criteria.update_one({"QN": "2"}, {'$set': {"OCQ2op1": Updated_OCQ2op1[0]}})
        col_oslas_criteria.update_one({"QN": "2"}, {'$set': {"OCQ2op2": Updated_OCQ2op2[0]}})

        col_oslas_criteria.update_one({"QN": "3"}, {'$set': {"OCQ3": Updated_Question3[0]}})
        col_oslas_criteria.update_one({"QN": "3"}, {'$set': {"OCQ3op1": Updated_OCQ3op1[0]}})
        col_oslas_criteria.update_one({"QN": "3"}, {'$set': {"OCQ3op2": Updated_OCQ3op2[0]}})

        col_oslas_criteria.update_one({"QN": "4"}, {'$set': {"OCQ4": Updated_Question4[0]}})
        col_oslas_criteria.update_one({"QN": "4"}, {'$set': {"OCQ4op1": Updated_OCQ4op1[0]}})
        col_oslas_criteria.update_one({"QN": "4"}, {'$set': {"OCQ4op2": Updated_OCQ4op2[0]}})
        col_oslas_criteria.update_one({"QN": "4"}, {'$set': {"OCQ4op3": Updated_OCQ4op3[0]}})

        col_oslas_criteria.update_one({"QN": "5"}, {'$set': {"OCQ5": Updated_Question5[0]}})

        col_oslas_criteria.update_one({"QN": "6"}, {'$set': {"Civil_a": Updated_Civil_a[0]}})
        col_oslas_criteria.update_one({"QN": "6"}, {'$set': {"Civil_a_op1": Updated_Civil_a_op1[0]}})
        col_oslas_criteria.update_one({"QN": "6"}, {'$set': {"Civil_a_op2": Updated_Civil_a_op2[0]}})

        col_oslas_criteria.update_one({"QN": "7"}, {'$set': {"Civil_b": Updated_Civil_b[0]}})
        col_oslas_criteria.update_one({"QN": "7"}, {'$set': {"Civil_b_op1": Updated_Civil_b_op1[0]}})
        col_oslas_criteria.update_one({"QN": "7"}, {'$set': {"Civil_b_op2": Updated_Civil_b_op2[0]}})
        col_oslas_criteria.update_one({"QN": "7"}, {'$set': {"Civil_b_op3": Updated_Civil_b_op3[0]}})
        col_oslas_criteria.update_one({"QN": "7"}, {'$set': {"Civil_b_op4": Updated_Civil_b_op4[0]}})
        col_oslas_criteria.update_one({"QN": "7"}, {'$set': {"Civil_b_op5": Updated_Civil_b_op5[0]}})
        col_oslas_criteria.update_one({"QN": "7"}, {'$set': {"Civil_b_op6": Updated_Civil_b_op6[0]}})
        col_oslas_criteria.update_one({"QN": "7"}, {'$set': {"Civil_b_op7": Updated_Civil_b_op7[0]}})
        col_oslas_criteria.update_one({"QN": "7"}, {'$set': {"Civil_b_op8": Updated_Civil_b_op8[0]}})

        col_oslas_criteria.update_one({"QN": "8"}, {'$set': {"Civil_c_respondent": Updated_Civil_c_respondent[0]}})
        col_oslas_criteria.update_one({"QN": "8"}, {'$set': {"Civil_c_respondent_op1": Updated_Civil_c_respondent_op1[0]}})
        col_oslas_criteria.update_one({"QN": "8"}, {'$set': {"Civil_c_respondent_op2": Updated_Civil_c_respondent_op2[0]}})
        col_oslas_criteria.update_one({"QN": "8"}, {'$set': {"Civil_c_respondent_op3": Updated_Civil_c_respondent_op3[0]}})
        col_oslas_criteria.update_one({"QN": "8"}, {'$set': {"Civil_c_respondent_op4": Updated_Civil_c_respondent_op4[0]}})
        col_oslas_criteria.update_one({"QN": "8"}, {'$set': {"Civil_c_respondent_op5": Updated_Civil_c_respondent_op5[0]}})
        col_oslas_criteria.update_one({"QN": "8"}, {'$set': {"Civil_c_respondent_op6": Updated_Civil_c_respondent_op6[0]}})

        col_oslas_criteria.update_one({"QN": "9"}, {'$set': {"Civil_c_claimant": Updated_Civil_c_claimant[0]}})
        col_oslas_criteria.update_one({"QN": "9"}, {'$set': {"Civil_c_claimant_op1": Updated_Civil_c_claimant_op1[0]}})
        col_oslas_criteria.update_one({"QN": "9"}, {'$set': {"Civil_c_claimant_op2": Updated_Civil_c_claimant_op2[0]}})
        col_oslas_criteria.update_one({"QN": "9"}, {'$set': {"Civil_c_claimant_op3": Updated_Civil_c_claimant_op3[0]}})
        col_oslas_criteria.update_one({"QN": "9"}, {'$set': {"Civil_c_claimant_op4": Updated_Civil_c_claimant_op4[0]}})
        col_oslas_criteria.update_one({"QN": "9"}, {'$set': {"Civil_c_claimant_op5": Updated_Civil_c_claimant_op5[0]}})

        col_oslas_criteria.update_one({"QN": "10"}, {'$set': {"Civil_d_claimant": Updated_Civil_d_claimant[0]}})
        col_oslas_criteria.update_one({"QN": "10"}, {'$set': {"Civil_d_claimant_op1": Updated_Civil_d_claimant_op1[0]}})
        col_oslas_criteria.update_one({"QN": "10"}, {'$set': {"Civil_d_claimant_op2": Updated_Civil_d_claimant_op2[0]}})
        col_oslas_criteria.update_one({"QN": "10"}, {'$set': {"Civil_d_claimant_op3": Updated_Civil_d_claimant_op3[0]}})

        col_oslas_criteria.update_one({"QN": "11"}, {'$set': {"Civil_c_employment": Updated_Civil_c_employment[0]}})
        col_oslas_criteria.update_one({"QN": "11"}, {'$set': {"Civil_c_employment_none": Updated_Civil_c_employment_none[0]}})
        col_oslas_criteria.update_one({"QN": "11"}, {'$set': {"Civil_c_claimant_employment_op1": Updated_Civil_c_claimant_employment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "11"}, {'$set': {"Civil_c_claimant_employment_op2": Updated_Civil_c_claimant_employment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "11"}, {'$set': {"Civil_c_respondent_employment_op1": Updated_Civil_c_respondent_employment_op1[0]}})

        col_oslas_criteria.update_one({"QN": "12"}, {'$set': {"Civil_d_claimant_employment": Updated_Civil_d_claimant_employment[0]}})
        col_oslas_criteria.update_one({"QN": "12"}, {'$set': {"Civil_d_claimant_employment_op1": Updated_Civil_d_claimant_employment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "12"}, {'$set': {"Civil_d_claimant_employment_op2": Updated_Civil_d_claimant_employment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "12"}, {'$set': {"Civil_d_claimant_employment_op3": Updated_Civil_d_claimant_employment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "12"}, {'$set': {"Civil_d_claimant_employment_op4": Updated_Civil_d_claimant_employment_op4[0]}})
        col_oslas_criteria.update_one({"QN": "12"}, {'$set': {"Civil_d_claimant_employment_op5": Updated_Civil_d_claimant_employment_op5[0]}})
        col_oslas_criteria.update_one({"QN": "12"}, {'$set': {"Civil_d_claimant_employment_op6": Updated_Civil_d_claimant_employment_op6[0]}})

        col_oslas_criteria.update_one({"QN": "13"}, {'$set': {"Civil_d_respondent_employment": Updated_Civil_d_respondent_employment[0]}})
        col_oslas_criteria.update_one({"QN": "13"}, {'$set': {"Civil_d_respondent_employment_op1": Updated_Civil_d_respondent_employment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "13"}, {'$set': {"Civil_d_respondent_employment_op2": Updated_Civil_d_respondent_employment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "13"}, {'$set': {"Civil_d_respondent_employment_op3": Updated_Civil_d_respondent_employment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "13"}, {'$set': {"Civil_d_respondent_employment_op4": Updated_Civil_d_respondent_employment_op4[0]}})
        col_oslas_criteria.update_one({"QN": "13"}, {'$set': {"Civil_d_respondent_employment_op5": Updated_Civil_d_respondent_employment_op5[0]}})
        col_oslas_criteria.update_one({"QN": "13"}, {'$set': {"Civil_d_respondent_employment_op6": Updated_Civil_d_respondent_employment_op6[0]}})
        col_oslas_criteria.update_one({"QN": "13"}, {'$set': {"Civil_d_respondent_employment_op7": Updated_Civil_d_respondent_employment_op7[0]}})

        col_oslas_criteria.update_one({"QN": "14"}, {'$set': {"Civil_e_claimant_employment": Updated_Civil_e_claimant_employment[0]}})
        col_oslas_criteria.update_one({"QN": "14"}, {'$set': {"Civil_e_claimant_employment_op1": Updated_Civil_e_claimant_employment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "14"}, {'$set': {"Civil_e_claimant_employment_op2": Updated_Civil_e_claimant_employment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "14"}, {'$set': {"Civil_e_claimant_employment_op3": Updated_Civil_e_claimant_employment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "14"}, {'$set': {"Civil_e_claimant_employment_op4": Updated_Civil_e_claimant_employment_op4[0]}})
        col_oslas_criteria.update_one({"QN": "14"}, {'$set': {"Civil_e_claimant_employment_op5": Updated_Civil_e_claimant_employment_op5[0]}})

        col_oslas_criteria.update_one({"QN": "15"}, {'$set': {"Resolve_the_dispute_online": Updated_Resolve_the_dispute_online[0]}})
        col_oslas_criteria.update_one({"QN": "15"}, {'$set': {"Resolve_the_dispute_online_op1": Updated_Resolve_the_dispute_online_op1[0]}})
        col_oslas_criteria.update_one({"QN": "15"}, {'$set': {"Resolve_the_dispute_online_op2": Updated_Resolve_the_dispute_online_op2[0]}})
        col_oslas_criteria.update_one({"QN": "15"}, {'$set': {"Resolve_the_dispute_online_op3": Updated_Resolve_the_dispute_online_op3[0]}})

        col_oslas_criteria.update_one({"QN": "16"}, {'$set': {"Civil_c_claimant_neighbour": Updated_Civil_c_claimant_neighbour[0]}})
        col_oslas_criteria.update_one({"QN": "16"}, {'$set': {"Civil_c_claimant_neighbour_op1": Updated_Civil_c_claimant_neighbour_op1[0]}})
        col_oslas_criteria.update_one({"QN": "16"}, {'$set': {"Civil_c_claimant_neighbour_op2": Updated_Civil_c_claimant_neighbour_op2[0]}})
        col_oslas_criteria.update_one({"QN": "16"}, {'$set': {"Civil_c_claimant_neighbour_op3": Updated_Civil_c_claimant_neighbour_op3[0]}})
        col_oslas_criteria.update_one({"QN": "16"}, {'$set': {"Civil_c_claimant_neighbour_op4": Updated_Civil_c_claimant_neighbour_op4[0]}})
        col_oslas_criteria.update_one({"QN": "16"}, {'$set': {"Civil_c_claimant_neighbour_op5": Updated_Civil_c_claimant_neighbour_op5[0]}})
        col_oslas_criteria.update_one({"QN": "16"}, {'$set': {"Civil_c_claimant_neighbour_op6": Updated_Civil_c_claimant_neighbour_op6[0]}})

        col_oslas_criteria.update_one({"QN": "17"}, {'$set': {"Civil_d_claimant_neighbour": Updated_Civil_d_claimant_neighbour[0]}})
        col_oslas_criteria.update_one({"QN": "17"}, {'$set': {"Civil_d_claimant_neighbour_op1": Updated_Civil_d_claimant_neighbour_op1[0]}})
        col_oslas_criteria.update_one({"QN": "17"}, {'$set': {"Civil_d_claimant_neighbour_op2": Updated_Civil_d_claimant_neighbour_op2[0]}})
        col_oslas_criteria.update_one({"QN": "17"}, {'$set': {"Civil_d_claimant_neighbour_op3": Updated_Civil_d_claimant_neighbour_op3[0]}})
        col_oslas_criteria.update_one({"QN": "17"}, {'$set': {"Civil_d_claimant_neighbour_op4": Updated_Civil_d_claimant_neighbour_op4[0]}})
        col_oslas_criteria.update_one({"QN": "17"}, {'$set': {"Civil_d_claimant_neighbour_op5": Updated_Civil_d_claimant_neighbour_op5[0]}})
        col_oslas_criteria.update_one({"QN": "17"}, {'$set': {"Civil_d_claimant_neighbour_op6": Updated_Civil_d_claimant_neighbour_op6[0]}})

        col_oslas_criteria.update_one({"QN": "18"}, {'$set': {"Civil_c_respondent_neighbour": Updated_Civil_c_respondent_neighbour[0]}})
        col_oslas_criteria.update_one({"QN": "18"}, {'$set': {"Civil_c_respondent_neighbour_op1": Updated_Civil_c_respondent_neighbour_op1[0]}})
        col_oslas_criteria.update_one({"QN": "18"}, {'$set': {"Civil_c_respondent_neighbour_op2": Updated_Civil_c_respondent_neighbour_op2[0]}})
        col_oslas_criteria.update_one({"QN": "18"}, {'$set': {"Civil_c_respondent_neighbour_op3": Updated_Civil_c_respondent_neighbour_op3[0]}})
        col_oslas_criteria.update_one({"QN": "18"}, {'$set': {"Civil_c_respondent_neighbour_op4": Updated_Civil_c_respondent_neighbour_op4[0]}})
        col_oslas_criteria.update_one({"QN": "18"}, {'$set': {"Civil_c_respondent_neighbour_op5": Updated_Civil_c_respondent_neighbour_op5[0]}})
        col_oslas_criteria.update_one({"QN": "18"}, {'$set': {"Civil_c_respondent_neighbour_op6": Updated_Civil_c_respondent_neighbour_op6[0]}})

        col_oslas_criteria.update_one({"QN": "19"}, {'$set': {"Civil_c_claimant_harassment": Updated_Civil_c_claimant_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "19"}, {'$set': {"Civil_c_claimant_harassment_op1": Updated_Civil_c_claimant_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "19"}, {'$set': {"Civil_c_claimant_harassment_op2": Updated_Civil_c_claimant_harassment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "19"}, {'$set': {"Civil_c_claimant_harassment_op3": Updated_Civil_c_claimant_harassment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "19"}, {'$set': {"Civil_c_claimant_harassment_op4": Updated_Civil_c_claimant_harassment_op4[0]}})
        col_oslas_criteria.update_one({"QN": "19"}, {'$set': {"Civil_c_claimant_harassment_op5": Updated_Civil_c_claimant_harassment_op5[0]}})
        col_oslas_criteria.update_one({"QN": "19"}, {'$set': {"Civil_c_claimant_harassment_op6": Updated_Civil_c_claimant_harassment_op6[0]}})

        col_oslas_criteria.update_one({"QN": "20"}, {'$set': {"Civil_d_claimant_harassment": Updated_Civil_d_claimant_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "20"}, {'$set': {"Civil_d_claimant_harassment_op1": Updated_Civil_d_claimant_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "20"}, {'$set': {"Civil_d_claimant_harassment_op2": Updated_Civil_d_claimant_harassment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "20"}, {'$set': {"Civil_d_claimant_harassment_op3": Updated_Civil_d_claimant_harassment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "20"}, {'$set': {"Civil_d_claimant_harassment_op4": Updated_Civil_d_claimant_harassment_op4[0]}})

        col_oslas_criteria.update_one({"QN": "21"}, {'$set': {"Civil_e_claimant_harassment": Updated_Civil_e_claimant_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "21"}, {'$set': {"Civil_e_claimant_harassment_op1": Updated_Civil_e_claimant_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "21"}, {'$set': {"Civil_e_claimant_harassment_op2": Updated_Civil_e_claimant_harassment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "21"}, {'$set': {"Civil_e_claimant_harassment_op3": Updated_Civil_e_claimant_harassment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "21"}, {'$set': {"Civil_e_claimant_harassment_op4": Updated_Civil_e_claimant_harassment_op4[0]}})

        col_oslas_criteria.update_one({"QN": "22"}, {'$set': {"Civil_f_claimant_harassment": Updated_Civil_f_claimant_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "22"}, {'$set': {"Civil_f_claimant_harassment_op1": Updated_Civil_f_claimant_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "22"}, {'$set': {"Civil_f_claimant_harassment_op2": Updated_Civil_f_claimant_harassment_op2[0]}})

        col_oslas_criteria.update_one({"QN": "23"}, {'$set': {"Civil_g_i_claimant_harassment": Updated_Civil_g_i_claimant_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "23"}, {'$set': {"Civil_g_i_claimant_harassment_op1": Updated_Civil_g_i_claimant_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "23"}, {'$set': {"Civil_g_i_claimant_harassment_op2": Updated_Civil_g_i_claimant_harassment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "23"}, {'$set': {"Civil_g_i_claimant_harassment_op3": Updated_Civil_g_i_claimant_harassment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "23"}, {'$set': {"Civil_g_i_claimant_harassment_op4": Updated_Civil_g_i_claimant_harassment_op4[0]}})
        col_oslas_criteria.update_one({"QN": "23"}, {'$set': {"Civil_g_i_claimant_harassment_op5": Updated_Civil_g_i_claimant_harassment_op5[0]}})

        col_oslas_criteria.update_one({"QN": "24"}, {'$set': {"Civil_g_ii_claimant_harassment": Updated_Civil_g_ii_claimant_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "24"}, {'$set': {"Civil_g_ii_claimant_harassment_op1": Updated_Civil_g_ii_claimant_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "24"}, {'$set': {"Civil_g_ii_claimant_harassment_op2": Updated_Civil_g_ii_claimant_harassment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "24"}, {'$set': {"Civil_g_ii_claimant_harassment_op3": Updated_Civil_g_ii_claimant_harassment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "24"}, {'$set': {"Civil_g_ii_claimant_harassment_op4": Updated_Civil_g_ii_claimant_harassment_op4[0]}})
        col_oslas_criteria.update_one({"QN": "24"}, {'$set': {"Civil_g_ii_claimant_harassment_op5": Updated_Civil_g_ii_claimant_harassment_op5[0]}})

        col_oslas_criteria.update_one({"QN": "25"}, {'$set': {"Civil_c_respondent_harassment": Updated_Civil_c_respondent_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "25"}, {'$set': {"Civil_c_respondent_harassment_op1": Updated_Civil_c_respondent_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "25"}, {'$set': {"Civil_c_respondent_harassment_op2": Updated_Civil_c_respondent_harassment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "25"}, {'$set': {"Civil_c_respondent_harassment_op3": Updated_Civil_c_respondent_harassment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "25"}, {'$set': {"Civil_c_respondent_harassment_op4": Updated_Civil_c_respondent_harassment_op4[0]}})
        col_oslas_criteria.update_one({"QN": "25"}, {'$set': {"Civil_c_respondent_harassment_op5": Updated_Civil_c_respondent_harassment_op5[0]}})

        col_oslas_criteria.update_one({"QN": "26"}, {'$set': {"Civil_d_respondent_harassment": Updated_Civil_d_respondent_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "26"}, {'$set': {"Civil_d_respondent_harassment_op1": Updated_Civil_d_respondent_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "26"}, {'$set': {"Civil_d_respondent_harassment_op2": Updated_Civil_d_respondent_harassment_op2[0]}})

        col_oslas_criteria.update_one({"QN": "27"}, {'$set': {"Civil_e_i_respondent_harassment": Updated_Civil_e_i_respondent_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "27"}, {'$set': {"Civil_e_i_respondent_harassment_op1": Updated_Civil_e_i_respondent_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "27"}, {'$set': {"Civil_e_i_respondent_harassment_op2": Updated_Civil_e_i_respondent_harassment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "27"}, {'$set': {"Civil_e_i_respondent_harassment_op3": Updated_Civil_e_i_respondent_harassment_op3[0]}})

        col_oslas_criteria.update_one({"QN": "28"}, {'$set': {"Civil_e_ii_respondent_harassment": Updated_Civil_e_ii_respondent_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "28"}, {'$set': {"Civil_e_ii_respondent_harassment_op1": Updated_Civil_e_ii_respondent_harassment_op1[0]}})

        col_oslas_criteria.update_one({"QN": "29"}, {'$set': {"Civil_f_respondent_harassment": Updated_Civil_f_respondent_harassment[0]}})
        col_oslas_criteria.update_one({"QN": "29"}, {'$set': {"Civil_f_respondent_harassment_op1": Updated_Civil_f_respondent_harassment_op1[0]}})
        col_oslas_criteria.update_one({"QN": "29"}, {'$set': {"Civil_f_respondent_harassment_op2": Updated_Civil_f_respondent_harassment_op2[0]}})
        col_oslas_criteria.update_one({"QN": "29"}, {'$set': {"Civil_f_respondent_harassment_op3": Updated_Civil_f_respondent_harassment_op3[0]}})
        col_oslas_criteria.update_one({"QN": "29"}, {'$set': {"Civil_f_respondent_harassment_op4": Updated_Civil_f_respondent_harassment_op4[0]}})
        col_oslas_criteria.update_one({"QN": "29"}, {'$set': {"Civil_f_respondent_harassment_op5": Updated_Civil_f_respondent_harassment_op5[0]}})

        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_i": Updated_Family_i[0]}})
        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_i_op1": Updated_Family_i_op1[0]}})
        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_i_op2": Updated_Family_i_op2[0]}})
        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_i_op3": Updated_Family_i_op3[0]}})
        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_i_op4": Updated_Family_i_op4[0]}})
        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_ii": Updated_Family_ii[0]}})
        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_ii_prompt": Updated_Family_ii_prompt[0]}})
        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_ii_op1": Updated_Family_ii_op1[0]}})
        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_ii_op2": Updated_Family_ii_op2[0]}})
        col_oslas_criteria.update_one({"QN": "30"}, {'$set': {"Family_ii_op3": Updated_Family_ii_op3[0]}})

        col_oslas_criteria.update_one({"QN": "31"}, {'$set': {"Criminal": Updated_Criminal[0]}})
        col_oslas_criteria.update_one({"QN": "31"}, {'$set': {"Criminal_op1": Updated_Criminal_op1[0]}})
        col_oslas_criteria.update_one({"QN": "31"}, {'$set': {"Criminal_op2": Updated_Criminal_op2[0]}})
        col_oslas_criteria.update_one({"QN": "31"}, {'$set': {"Criminal_op3": Updated_Criminal_op3[0]}})
        col_oslas_criteria.update_one({"QN": "31"}, {'$set': {"Criminal_op4": Updated_Criminal_op4[0]}})
        col_oslas_criteria.update_one({"QN": "31"}, {'$set': {"Criminal_op5": Updated_Criminal_op5[0]}})
        col_oslas_criteria.update_one({"QN": "31"}, {'$set': {"Criminal_op6": Updated_Criminal_op6[0]}})
        col_oslas_criteria.update_one({"QN": "31"}, {'$set': {"Criminal_op7": Updated_Criminal_op7[0]}})

        col_oslas_criteria.update_one({"QN": "32"}, {'$set': {"Introduction_message": Updated_Introduction_message[0]}})

    # OSLAS Introduction message database
    OCIntro = list(col_oslas_criteria.find({"QN": "32"}))[0]
    Introduction_message = OCIntro["Introduction_message"]

    # OSLAS Criteria Question 1 database
    OCQuestion1 = list(col_oslas_criteria.find({"QN": "1"}))[0]
    OCQ1 = OCQuestion1["OCQ1"]
    OCQ1op1 = OCQuestion1["OCQ1op1"]
    OCQ1op2 = OCQuestion1["OCQ1op2"]

    # OSLAS Criteria Question 2 database
    OCQuestion2 = list(col_oslas_criteria.find({"QN": "2"}))[0]
    OCQ2 = OCQuestion2["OCQ2"]
    OCQ2op1 = OCQuestion2["OCQ2op1"]
    OCQ2op2 = OCQuestion2["OCQ2op2"]

    # OSLAS Criteria Question 3 database
    OCQuestion3 = list(col_oslas_criteria.find({"QN": "3"}))[0]
    OCQ3 = OCQuestion3["OCQ3"]
    OCQ3op1 = OCQuestion3["OCQ3op1"]
    OCQ3op2 = OCQuestion3["OCQ3op2"]

    # OSLAS Criteria Question 4 database
    OCQuestion4 = list(col_oslas_criteria.find({"QN": "4"}))[0]
    OCQ4 = OCQuestion4["OCQ4"]
    OCQ4op1 = OCQuestion4["OCQ4op1"]
    OCQ4op2 = OCQuestion4["OCQ4op2"]
    OCQ4op3 = OCQuestion4["OCQ4op3"]

    # OSLAS Criteria Question 5 database
    OCQuestion5 = list(col_oslas_criteria.find({"QN": "5"}))[0]
    OCQ5 = OCQuestion5["OCQ5"]

    # OSLAS Criteria Civil(a) database
    OCCivil_a = list(col_oslas_criteria.find({"QN": "6"}))[0]
    Civil_a = OCCivil_a["Civil_a"]
    Civil_a_op1 = OCCivil_a["Civil_a_op1"]
    Civil_a_op2 = OCCivil_a["Civil_a_op2"]

    # OSLAS Criteria Civil(b) database
    OCCivil_b = list(col_oslas_criteria.find({"QN": "7"}))[0]
    Civil_b = OCCivil_b["Civil_b"]
    Civil_b_op1 = OCCivil_b["Civil_b_op1"]
    Civil_b_op2 = OCCivil_b["Civil_b_op2"]
    Civil_b_op3 = OCCivil_b["Civil_b_op3"]
    Civil_b_op4 = OCCivil_b["Civil_b_op4"]
    Civil_b_op5 = OCCivil_b["Civil_b_op5"]
    Civil_b_op6 = OCCivil_b["Civil_b_op6"]
    Civil_b_op7 = OCCivil_b["Civil_b_op7"]
    Civil_b_op8 = OCCivil_b["Civil_b_op8"]

    # OSLAS Criteria Civil(c) respondent database
    OCCivil_c_respondent = list(col_oslas_criteria.find({"QN": "8"}))[0]
    Civil_c_respondent = OCCivil_c_respondent["Civil_c_respondent"]
    Civil_c_respondent_op1 = OCCivil_c_respondent["Civil_c_respondent_op1"]
    Civil_c_respondent_op2 = OCCivil_c_respondent["Civil_c_respondent_op2"]
    Civil_c_respondent_op3 = OCCivil_c_respondent["Civil_c_respondent_op3"]
    Civil_c_respondent_op4 = OCCivil_c_respondent["Civil_c_respondent_op4"]
    Civil_c_respondent_op5 = OCCivil_c_respondent["Civil_c_respondent_op5"]
    Civil_c_respondent_op6 = OCCivil_c_respondent["Civil_c_respondent_op6"]

    # OSLAS Criteria Civil(c) claimant database
    OCCivil_c_claimant = list(col_oslas_criteria.find({"QN": "9"}))[0]
    Civil_c_claimant = OCCivil_c_claimant["Civil_c_claimant"]
    Civil_c_claimant_op1 = OCCivil_c_claimant["Civil_c_claimant_op1"]
    Civil_c_claimant_op2 = OCCivil_c_claimant["Civil_c_claimant_op2"]
    Civil_c_claimant_op3 = OCCivil_c_claimant["Civil_c_claimant_op3"]
    Civil_c_claimant_op4 = OCCivil_c_claimant["Civil_c_claimant_op4"]
    Civil_c_claimant_op5 = OCCivil_c_claimant["Civil_c_claimant_op5"]

    # OSLAS Criteria Civil(c) employment database
    OCCivil_c_employment = list(col_oslas_criteria.find({"QN": "11"}))[0]
    Civil_c_employment = OCCivil_c_employment["Civil_c_employment"]
    Civil_c_claimant_employment_op1 = OCCivil_c_employment["Civil_c_claimant_employment_op1"]
    Civil_c_claimant_employment_op2 = OCCivil_c_employment["Civil_c_claimant_employment_op2"]
    Civil_c_respondent_employment_op1 = OCCivil_c_employment["Civil_c_respondent_employment_op1"]
    Civil_c_employment_none = OCCivil_c_employment["Civil_c_employment_none"]

    # OSLAS Criteria Civil(d) claimant database
    OCCivil_d_claimant = list(col_oslas_criteria.find({"QN": "10"}))[0]
    Civil_d_claimant = OCCivil_d_claimant["Civil_d_claimant"]
    Civil_d_claimant_op1 = OCCivil_d_claimant["Civil_d_claimant_op1"]
    Civil_d_claimant_op2 = OCCivil_d_claimant["Civil_d_claimant_op2"]
    Civil_d_claimant_op3 = OCCivil_d_claimant["Civil_d_claimant_op3"]

    # OSLAS Criteria Civil(d) claimant employment database
    OCCivil_d_claimant_employment = list(col_oslas_criteria.find({"QN": "12"}))[0]
    Civil_d_claimant_employment = OCCivil_d_claimant_employment["Civil_d_claimant_employment"]
    Civil_d_claimant_employment_op1 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op1"]
    Civil_d_claimant_employment_op2 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op2"]
    Civil_d_claimant_employment_op3 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op3"]
    Civil_d_claimant_employment_op4 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op4"]
    Civil_d_claimant_employment_op5 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op5"]
    Civil_d_claimant_employment_op6 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op6"]

    # OSLAS Criteria Civil(d) respondent employment database
    OCCivil_d_respondent_employment = list(col_oslas_criteria.find({"QN": "13"}))[0]
    Civil_d_respondent_employment = OCCivil_d_respondent_employment["Civil_d_respondent_employment"]
    Civil_d_respondent_employment_op1 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op1"]
    Civil_d_respondent_employment_op2 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op2"]
    Civil_d_respondent_employment_op3 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op3"]
    Civil_d_respondent_employment_op4 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op4"]
    Civil_d_respondent_employment_op5 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op5"]
    Civil_d_respondent_employment_op6 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op6"]
    Civil_d_respondent_employment_op7 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op7"]

    # OSLAS Criteria Civil(e) claimant employment database
    OCCivil_e_claimant_employment = list(col_oslas_criteria.find({"QN": "14"}))[0]
    Civil_e_claimant_employment = OCCivil_e_claimant_employment["Civil_e_claimant_employment"]
    Civil_e_claimant_employment_op1 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op1"]
    Civil_e_claimant_employment_op2 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op2"]
    Civil_e_claimant_employment_op3 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op3"]
    Civil_e_claimant_employment_op4 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op4"]
    Civil_e_claimant_employment_op5 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op5"]

    # OSLAS Criteria Resolve the dispute online database
    OCResolve_the_dispute_online = list(col_oslas_criteria.find({"QN": "15"}))[0]
    Resolve_the_dispute_online = OCResolve_the_dispute_online["Resolve_the_dispute_online"]
    Resolve_the_dispute_online_op1 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op1"]
    Resolve_the_dispute_online_op2 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op2"]
    Resolve_the_dispute_online_op3 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op3"]

    # OSLAS Criteria Civil(c) claimant neighbour database
    OCCivil_c_neighbour = list(col_oslas_criteria.find({"QN": "16"}))[0]
    Civil_c_claimant_neighbour = OCCivil_c_neighbour["Civil_c_claimant_neighbour"]
    Civil_c_claimant_neighbour_op1 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op1"]
    Civil_c_claimant_neighbour_op2 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op2"]
    Civil_c_claimant_neighbour_op3 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op3"]
    Civil_c_claimant_neighbour_op4 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op4"]
    Civil_c_claimant_neighbour_op5 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op5"]
    Civil_c_claimant_neighbour_op6 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op6"]

    # OSLAS Criteria Civil(d) claimant neighbour database
    OCCivil_d_claimant_neighbour = list(col_oslas_criteria.find({"QN": "17"}))[0]
    Civil_d_claimant_neighbour = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour"]
    Civil_d_claimant_neighbour_op1 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op1"]
    Civil_d_claimant_neighbour_op2 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op2"]
    Civil_d_claimant_neighbour_op3 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op3"]
    Civil_d_claimant_neighbour_op4 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op4"]
    Civil_d_claimant_neighbour_op5 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op5"]
    Civil_d_claimant_neighbour_op6 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op6"]

    # OSLAS Criteria Civil(c) respondent neighbour database
    OCCivil_c_respondent_neighbour = list(col_oslas_criteria.find({"QN": "18"}))[0]
    Civil_c_respondent_neighbour = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour"]
    Civil_c_respondent_neighbour_op1 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op1"]
    Civil_c_respondent_neighbour_op2 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op2"]
    Civil_c_respondent_neighbour_op3 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op3"]
    Civil_c_respondent_neighbour_op4 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op4"]
    Civil_c_respondent_neighbour_op5 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op5"]
    Civil_c_respondent_neighbour_op6 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op6"]

    # OSLAS Criteria Civil(c) claimant harassment database
    OCCivil_c_claimant_harassment = list(col_oslas_criteria.find({"QN": "19"}))[0]
    Civil_c_claimant_harassment = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment"]
    Civil_c_claimant_harassment_op1 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op1"]
    Civil_c_claimant_harassment_op2 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op2"]
    Civil_c_claimant_harassment_op3 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op3"]
    Civil_c_claimant_harassment_op4 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op4"]
    Civil_c_claimant_harassment_op5 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op5"]
    Civil_c_claimant_harassment_op6 = OCCivil_c_claimant_harassment["Civil_c_claimant_harassment_op6"]

    # OSLAS Criteria Civil(d) claimant harassment database
    OCCivil_d_claimant_harassment = list(col_oslas_criteria.find({"QN": "20"}))[0]
    Civil_d_claimant_harassment = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment"]
    Civil_d_claimant_harassment_op1 = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment_op1"]
    Civil_d_claimant_harassment_op2 = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment_op2"]
    Civil_d_claimant_harassment_op3 = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment_op3"]
    Civil_d_claimant_harassment_op4 = OCCivil_d_claimant_harassment["Civil_d_claimant_harassment_op4"]

    # OSLAS Criteria Civil(e) claimant harassment database
    OCCivil_e_claimant_harassment = list(col_oslas_criteria.find({"QN": "21"}))[0]
    Civil_e_claimant_harassment = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment"]
    Civil_e_claimant_harassment_op1 = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment_op1"]
    Civil_e_claimant_harassment_op2 = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment_op2"]
    Civil_e_claimant_harassment_op3 = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment_op3"]
    Civil_e_claimant_harassment_op4 = OCCivil_e_claimant_harassment["Civil_e_claimant_harassment_op4"]

    # OSLAS Criteria Civil(f) claimant harassment database
    OCCivil_f_claimant_harassment = list(col_oslas_criteria.find({"QN": "22"}))[0]
    Civil_f_claimant_harassment = OCCivil_f_claimant_harassment["Civil_f_claimant_harassment"]
    Civil_f_claimant_harassment_op1 = OCCivil_f_claimant_harassment["Civil_f_claimant_harassment_op1"]
    Civil_f_claimant_harassment_op2 = OCCivil_f_claimant_harassment["Civil_f_claimant_harassment_op2"]

    # OSLAS Criteria Civil(g)(i) claimant harassment database
    OCCivil_g_i_claimant_harassment = list(col_oslas_criteria.find({"QN": "23"}))[0]
    Civil_g_i_claimant_harassment = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment"]
    Civil_g_i_claimant_harassment_op1 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op1"]
    Civil_g_i_claimant_harassment_op2 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op2"]
    Civil_g_i_claimant_harassment_op3 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op3"]
    Civil_g_i_claimant_harassment_op4 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op4"]
    Civil_g_i_claimant_harassment_op5 = OCCivil_g_i_claimant_harassment["Civil_g_i_claimant_harassment_op5"]

    # OSLAS Criteria Civil(g)(ii) claimant harassment database
    OCCivil_g_ii_claimant_harassment = list(col_oslas_criteria.find({"QN": "24"}))[0]
    Civil_g_ii_claimant_harassment = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment"]
    Civil_g_ii_claimant_harassment_op1 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op1"]
    Civil_g_ii_claimant_harassment_op2 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op2"]
    Civil_g_ii_claimant_harassment_op3 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op3"]
    Civil_g_ii_claimant_harassment_op4 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op4"]
    Civil_g_ii_claimant_harassment_op5 = OCCivil_g_ii_claimant_harassment["Civil_g_ii_claimant_harassment_op5"]

    # OSLAS Criteria Civil(c) respondent harassment database
    OCCivil_c_respondent_harassment = list(col_oslas_criteria.find({"QN": "25"}))[0]
    Civil_c_respondent_harassment = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment"]
    Civil_c_respondent_harassment_op1 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op1"]
    Civil_c_respondent_harassment_op2 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op2"]
    Civil_c_respondent_harassment_op3 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op3"]
    Civil_c_respondent_harassment_op4 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op4"]
    Civil_c_respondent_harassment_op5 = OCCivil_c_respondent_harassment["Civil_c_respondent_harassment_op5"]

    # OSLAS Criteria Civil(d) respondent harassment database
    OCCivil_d_respondent_harassment = list(col_oslas_criteria.find({"QN": "26"}))[0]
    Civil_d_respondent_harassment = OCCivil_d_respondent_harassment["Civil_d_respondent_harassment"]
    Civil_d_respondent_harassment_op1 = OCCivil_d_respondent_harassment["Civil_d_respondent_harassment_op1"]
    Civil_d_respondent_harassment_op2 = OCCivil_d_respondent_harassment["Civil_d_respondent_harassment_op2"]

    # OSLAS Criteria Civil(e)(i) respondent harassment database
    OCCivil_e_i_respondent_harassment = list(col_oslas_criteria.find({"QN": "27"}))[0]
    Civil_e_i_respondent_harassment = OCCivil_e_i_respondent_harassment["Civil_e_i_respondent_harassment"]
    Civil_e_i_respondent_harassment_op1 = OCCivil_e_i_respondent_harassment["Civil_e_i_respondent_harassment_op1"]
    Civil_e_i_respondent_harassment_op2 = OCCivil_e_i_respondent_harassment["Civil_e_i_respondent_harassment_op2"]
    Civil_e_i_respondent_harassment_op3 = OCCivil_e_i_respondent_harassment["Civil_e_i_respondent_harassment_op3"]

    # OSLAS Criteria Civil(e)(ii) respondent harassment database
    OCCivil_e_ii_respondent_harassment = list(col_oslas_criteria.find({"QN": "28"}))[0]
    Civil_e_ii_respondent_harassment = OCCivil_e_ii_respondent_harassment["Civil_e_ii_respondent_harassment"]
    Civil_e_ii_respondent_harassment_op1 = OCCivil_e_ii_respondent_harassment["Civil_e_ii_respondent_harassment_op1"]

    # OSLAS Criteria Civil(f) respondent harassment database
    OCCivil_f_respondent_harassment = list(col_oslas_criteria.find({"QN": "29"}))[0]
    Civil_f_respondent_harassment = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment"]
    Civil_f_respondent_harassment_op1 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op1"]
    Civil_f_respondent_harassment_op2 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op2"]
    Civil_f_respondent_harassment_op3 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op3"]
    Civil_f_respondent_harassment_op4 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op4"]
    Civil_f_respondent_harassment_op5 = OCCivil_f_respondent_harassment["Civil_f_respondent_harassment_op5"]

    # OSLAS Criteria Family database
    OCFamily = list(col_oslas_criteria.find({"QN": "30"}))[0]
    Family_i = OCFamily["Family_i"]
    Family_i_op1 = OCFamily["Family_i_op1"]
    Family_i_op2 = OCFamily["Family_i_op2"]
    Family_i_op3 = OCFamily["Family_i_op3"]
    Family_i_op4 = OCFamily["Family_i_op4"]
    Family_ii = OCFamily["Family_ii"]
    Family_ii_prompt = OCFamily["Family_ii_prompt"]
    Family_ii_op1 = OCFamily["Family_ii_op1"]
    Family_ii_op2 = OCFamily["Family_ii_op2"]
    Family_ii_op3 = OCFamily["Family_ii_op3"]

    # OSLAS Criteria Criminal database
    OCCriminal = list(col_oslas_criteria.find({"QN": "31"}))[0]
    Criminal = OCCriminal["Criminal"]
    Criminal_op1 = OCCriminal["Criminal_op1"]
    Criminal_op2 = OCCriminal["Criminal_op2"]
    Criminal_op3 = OCCriminal["Criminal_op3"]
    Criminal_op4 = OCCriminal["Criminal_op4"]
    Criminal_op5 = OCCriminal["Criminal_op5"]
    Criminal_op6 = OCCriminal["Criminal_op6"]
    Criminal_op7 = OCCriminal["Criminal_op7"]

    return render_template('oslas_cms.html', OCQ1 = OCQ1, OCQ1op1 = OCQ1op1, OCQ1op2 = OCQ1op2,
    OCQ2 = OCQ2, OCQ2op1 = OCQ2op1, OCQ2op2 = OCQ2op2,
    OCQ3 = OCQ3, OCQ3op1 = OCQ3op1, OCQ3op2 = OCQ3op2,
    OCQ4 = OCQ4, OCQ4op1 = OCQ4op1, OCQ4op2 = OCQ4op2, OCQ4op3 = OCQ4op3,
    OCQ5 = OCQ5,
    Introduction_message = Introduction_message,
    Civil_a = Civil_a, Civil_a_op1 = Civil_a_op1, Civil_a_op2 = Civil_a_op2,
    Civil_b = Civil_b, Civil_b_op1 = Civil_b_op1, Civil_b_op2 = Civil_b_op2, Civil_b_op3 = Civil_b_op3, Civil_b_op4 = Civil_b_op4, Civil_b_op5 = Civil_b_op5, Civil_b_op6 = Civil_b_op6, Civil_b_op7 = Civil_b_op7, Civil_b_op8 = Civil_b_op8,
    Civil_c_respondent = Civil_c_respondent, Civil_c_respondent_op1 = Civil_c_respondent_op1, Civil_c_respondent_op2 = Civil_c_respondent_op2, Civil_c_respondent_op3 = Civil_c_respondent_op3, Civil_c_respondent_op4 = Civil_c_respondent_op4, Civil_c_respondent_op5 = Civil_c_respondent_op5, Civil_c_respondent_op6 = Civil_c_respondent_op6,
    Civil_c_claimant = Civil_c_claimant, Civil_c_claimant_op1 = Civil_c_claimant_op1, Civil_c_claimant_op2 = Civil_c_claimant_op2, Civil_c_claimant_op3 = Civil_c_claimant_op3, Civil_c_claimant_op4 = Civil_c_claimant_op4, Civil_c_claimant_op5 = Civil_c_claimant_op5,
    Civil_c_employment = Civil_c_employment, Civil_c_claimant_employment_op1 = Civil_c_claimant_employment_op1, Civil_c_claimant_employment_op2 = Civil_c_claimant_employment_op2, Civil_c_respondent_employment_op1 = Civil_c_respondent_employment_op1, Civil_c_employment_none = Civil_c_employment_none,
    Civil_d_claimant = Civil_d_claimant, Civil_d_claimant_op1 = Civil_d_claimant_op1, Civil_d_claimant_op2 = Civil_d_claimant_op2, Civil_d_claimant_op3 = Civil_d_claimant_op3,
    Civil_d_claimant_employment = Civil_d_claimant_employment, Civil_d_claimant_employment_op1 = Civil_d_claimant_employment_op1, Civil_d_claimant_employment_op2 = Civil_d_claimant_employment_op2, Civil_d_claimant_employment_op3 = Civil_d_claimant_employment_op3, Civil_d_claimant_employment_op4 = Civil_d_claimant_employment_op4, Civil_d_claimant_employment_op5 = Civil_d_claimant_employment_op5, Civil_d_claimant_employment_op6 = Civil_d_claimant_employment_op6,
    Civil_d_respondent_employment = Civil_d_respondent_employment, Civil_d_respondent_employment_op1 = Civil_d_respondent_employment_op1, Civil_d_respondent_employment_op2 = Civil_d_respondent_employment_op2, Civil_d_respondent_employment_op3 = Civil_d_respondent_employment_op3, Civil_d_respondent_employment_op4 = Civil_d_respondent_employment_op4, Civil_d_respondent_employment_op5 = Civil_d_respondent_employment_op5, Civil_d_respondent_employment_op6 = Civil_d_respondent_employment_op6, Civil_d_respondent_employment_op7 = Civil_d_respondent_employment_op7,
    Civil_e_claimant_employment = Civil_e_claimant_employment, Civil_e_claimant_employment_op1 = Civil_e_claimant_employment_op1, Civil_e_claimant_employment_op2 = Civil_e_claimant_employment_op2, Civil_e_claimant_employment_op3 = Civil_e_claimant_employment_op3, Civil_e_claimant_employment_op4 = Civil_e_claimant_employment_op4, Civil_e_claimant_employment_op5 = Civil_e_claimant_employment_op5,
    Resolve_the_dispute_online = Resolve_the_dispute_online, Resolve_the_dispute_online_op1 = Resolve_the_dispute_online_op1, Resolve_the_dispute_online_op2 = Resolve_the_dispute_online_op2, Resolve_the_dispute_online_op3 = Resolve_the_dispute_online_op3,
    Civil_c_claimant_neighbour = Civil_c_claimant_neighbour, Civil_c_claimant_neighbour_op1 = Civil_c_claimant_neighbour_op1, Civil_c_claimant_neighbour_op2 = Civil_c_claimant_neighbour_op2, Civil_c_claimant_neighbour_op3 = Civil_c_claimant_neighbour_op3, Civil_c_claimant_neighbour_op4 = Civil_c_claimant_neighbour_op4, Civil_c_claimant_neighbour_op5 = Civil_c_claimant_neighbour_op5, Civil_c_claimant_neighbour_op6 = Civil_c_claimant_neighbour_op6,
    Civil_d_claimant_neighbour = Civil_d_claimant_neighbour, Civil_d_claimant_neighbour_op1 = Civil_d_claimant_neighbour_op1, Civil_d_claimant_neighbour_op2 = Civil_d_claimant_neighbour_op2, Civil_d_claimant_neighbour_op3 = Civil_d_claimant_neighbour_op3, Civil_d_claimant_neighbour_op4 = Civil_d_claimant_neighbour_op4, Civil_d_claimant_neighbour_op5 = Civil_d_claimant_neighbour_op5, Civil_d_claimant_neighbour_op6 = Civil_d_claimant_neighbour_op6,
    Civil_c_respondent_neighbour = Civil_c_respondent_neighbour, Civil_c_respondent_neighbour_op1 = Civil_c_respondent_neighbour_op1, Civil_c_respondent_neighbour_op2 = Civil_c_respondent_neighbour_op2, Civil_c_respondent_neighbour_op3 = Civil_c_respondent_neighbour_op3, Civil_c_respondent_neighbour_op4 = Civil_c_respondent_neighbour_op4, Civil_c_respondent_neighbour_op5 = Civil_c_respondent_neighbour_op5, Civil_c_respondent_neighbour_op6 = Civil_c_respondent_neighbour_op6,
    Civil_c_claimant_harassment = Civil_c_claimant_harassment, Civil_c_claimant_harassment_op1 = Civil_c_claimant_harassment_op1, Civil_c_claimant_harassment_op2 = Civil_c_claimant_harassment_op2, Civil_c_claimant_harassment_op3 = Civil_c_claimant_harassment_op3, Civil_c_claimant_harassment_op4 = Civil_c_claimant_harassment_op4, Civil_c_claimant_harassment_op5 = Civil_c_claimant_harassment_op5, Civil_c_claimant_harassment_op6 = Civil_c_claimant_harassment_op6,
    Civil_d_claimant_harassment = Civil_d_claimant_harassment, Civil_d_claimant_harassment_op1 = Civil_d_claimant_harassment_op1, Civil_d_claimant_harassment_op2 = Civil_d_claimant_harassment_op2, Civil_d_claimant_harassment_op3 = Civil_d_claimant_harassment_op3, Civil_d_claimant_harassment_op4 = Civil_d_claimant_harassment_op4,
    Civil_e_claimant_harassment = Civil_e_claimant_harassment, Civil_e_claimant_harassment_op1 = Civil_e_claimant_harassment_op1, Civil_e_claimant_harassment_op2 = Civil_e_claimant_harassment_op2, Civil_e_claimant_harassment_op3 = Civil_e_claimant_harassment_op3, Civil_e_claimant_harassment_op4 = Civil_e_claimant_harassment_op4,
    Civil_f_claimant_harassment = Civil_f_claimant_harassment, Civil_f_claimant_harassment_op1 = Civil_f_claimant_harassment_op1, Civil_f_claimant_harassment_op2 = Civil_f_claimant_harassment_op2,
    Civil_g_i_claimant_harassment = Civil_g_i_claimant_harassment, Civil_g_i_claimant_harassment_op1 = Civil_g_i_claimant_harassment_op1, Civil_g_i_claimant_harassment_op2 = Civil_g_i_claimant_harassment_op2, Civil_g_i_claimant_harassment_op3 = Civil_g_i_claimant_harassment_op3, Civil_g_i_claimant_harassment_op4 = Civil_g_i_claimant_harassment_op4, Civil_g_i_claimant_harassment_op5 = Civil_g_i_claimant_harassment_op5,
    Civil_g_ii_claimant_harassment = Civil_g_ii_claimant_harassment, Civil_g_ii_claimant_harassment_op1 = Civil_g_ii_claimant_harassment_op1, Civil_g_ii_claimant_harassment_op2 = Civil_g_ii_claimant_harassment_op2, Civil_g_ii_claimant_harassment_op3 = Civil_g_ii_claimant_harassment_op3, Civil_g_ii_claimant_harassment_op4 = Civil_g_ii_claimant_harassment_op4, Civil_g_ii_claimant_harassment_op5 = Civil_g_ii_claimant_harassment_op5,
    Civil_c_respondent_harassment = Civil_c_respondent_harassment, Civil_c_respondent_harassment_op1 = Civil_c_respondent_harassment_op1, Civil_c_respondent_harassment_op2 = Civil_c_respondent_harassment_op2, Civil_c_respondent_harassment_op3 = Civil_c_respondent_harassment_op3, Civil_c_respondent_harassment_op4 = Civil_c_respondent_harassment_op4, Civil_c_respondent_harassment_op5 = Civil_c_respondent_harassment_op5,
    Civil_d_respondent_harassment = Civil_d_respondent_harassment, Civil_d_respondent_harassment_op1 = Civil_d_respondent_harassment_op1, Civil_d_respondent_harassment_op2 = Civil_d_respondent_harassment_op2,
    Civil_e_i_respondent_harassment = Civil_e_i_respondent_harassment, Civil_e_i_respondent_harassment_op1 = Civil_e_i_respondent_harassment_op1, Civil_e_i_respondent_harassment_op2 = Civil_e_i_respondent_harassment_op2, Civil_e_i_respondent_harassment_op3 = Civil_e_i_respondent_harassment_op3,
    Civil_e_ii_respondent_harassment = Civil_e_ii_respondent_harassment, Civil_e_ii_respondent_harassment_op1 = Civil_e_ii_respondent_harassment_op1,
    Civil_f_respondent_harassment = Civil_f_respondent_harassment, Civil_f_respondent_harassment_op1 = Civil_f_respondent_harassment_op1, Civil_f_respondent_harassment_op2 = Civil_f_respondent_harassment_op2, Civil_f_respondent_harassment_op3 = Civil_f_respondent_harassment_op3, Civil_f_respondent_harassment_op4 = Civil_f_respondent_harassment_op4, Civil_f_respondent_harassment_op5 = Civil_f_respondent_harassment_op5,
    Family_i = Family_i, Family_i_op1 = Family_i_op1, Family_i_op2 = Family_i_op2, Family_i_op3 = Family_i_op3, Family_i_op4 = Family_i_op4, Family_ii = Family_ii, Family_ii_prompt = Family_ii_prompt, Family_ii_op1 = Family_ii_op1, Family_ii_op2 = Family_ii_op2, Family_ii_op3 = Family_ii_op3,
    Criminal = Criminal, Criminal_op1 = Criminal_op1, Criminal_op2 = Criminal_op2, Criminal_op3 = Criminal_op3, Criminal_op4 = Criminal_op4, Criminal_op5 = Criminal_op5, Criminal_op6 = Criminal_op6, Criminal_op7 = Criminal_op7)

@app.route('/admin/dashboard/oslas')
def oslas_dashboard():
    return render_template("oslas_dashboard.html")

if __name__ == '__main__':
    app.debug = True
    app.run()