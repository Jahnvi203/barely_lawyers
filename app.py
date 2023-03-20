from flask import Flask, render_template, request, redirect, url_for, session, make_response, Response, jsonify
from pymongo import MongoClient
from resources.add_annexes import add_annexes_dict
from resources.add_inputs import add_inputs_dict
from resources.annexes import annexes_dict
from resources.glossaries import glossaries_dict
from resources.download_annexes import download_annexes_dict
from flask_weasyprint import HTML, render_pdf, CSS
import random
import ssl
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from datetime import datetime
from collections import Counter
import requests
from flask_ckeditor import CKEditor
from operator import itemgetter
from suggest_advice import suggest_advice

app = Flask(__name__)
app.secret_key = '1E44M1ixSeNGzO3T0dqIoXra7De5B46n'
app.config['SESSION_PERMANENT'] = True
app.config["SESSION_TYPE"] = "filesystem"
ckeditor = CKEditor(app)

# Database Connection
uri = "mongodb+srv://Jahnvi203:Jahnvi203@cluster0.cn63w2k.mongodb.net/app?retryWrites=true&w=majority"
connection = MongoClient(host = uri, connect = False)        
db = connection['app']
col_m = db.maintenance_qns
col_d = db.divorce_qns
col_pdfs = db.report_pdfs
col_answers = db.answers
col_html = db.pdfs_html
col_admin = db.admin_users
col_oslas_criteria = db.OSLAS_Criteria
col_OC_Answers = db.OC_Answers

@app.route('/')
def index():
    # maintenance_df = pd.read_csv("maintenance_qns.csv")
    # maintenance_list = maintenance_df.values.tolist()
    # columns = ['qn_no', 'qn', 'qn_type', 'op1', 'img1', 'op2', 'img2', 'op3', 'img3', 'op4', 'img4', 'prev_qn_no', 'sel_op', 'resource', 'glossary', 'add_annex', 'add_input', 'final_qn', 'qn_code']
    # for row in maintenance_list:
    #     col_m.insert_one(dict(zip(columns, row)))
    # divorce_df = pd.read_csv("divorce_qns.csv")
    # divorce_list = divorce_df.values.tolist()
    # columns = ['qn_no', 'qn', 'qn_type', 'op1', 'img1', 'op2', 'img2', 'op3', 'img3', 'op4', 'img4', 'prev_qn_no', 'sel_op', 'resource', 'glossary', 'add_annex', 'add_input', 'final_qn', 'qn_code']
    # for row in divorce_list:
    #     col_d.insert_one(dict(zip(columns, row)))
    print(glossaries_dict.keys())
    print(add_annexes_dict.keys())
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
        sel_op = "op0"
        if int(back) == 0:
            prev_qn_type = list(col_m.find({"qn_no": int(prev_qn_no)}))[0]['qn_type']
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
                    print("Next Before:" + str(session['user-answers']))
                    for item in user_answers_list:
                        if item[0] == prev_qn_no:
                            user_answers_list.remove(item)
                    user_answers_list.append([prev_qn_no, sel_op])
                    session['user-answers'] = user_answers_list
                    session.permanent = True
                    print("Next After:" + str(session['user-answers']))
                else:
                    session['user-answers'] = [[prev_qn_no, sel_op]]
                    session.permanent = True
                    print("Next Start:" + str(session['user-answers']))
                if 'additional-inputs' in session:
                    additional_inputs = session['additional-inputs']
                    print("Input Before:" + str(session['additional-inputs']))
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
                    print("Input After:" + str(session['additional-inputs']))
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
            search_result = list(col_m.find({"prev_qn_no": int(prev_qn_no), "sel_op": str(sel_op)}))[0]
        else:
            if int(prev_qn_no) == 1:
                return render_template("index.html")
            else:
                search_result = list(col_m.find({"qn_no": int(prev_qn_no)}))[0]['prev_qn_no']
                search_result = list(col_m.find({"qn_no": int(search_result)}))[0]
                user_answers_list = session['user-answers']
                print("Back Before:" + str(session['user-answers']))
                user_answers_list.pop()
                session['user-answers'] = user_answers_list
                session.permanent = True
                print("Back After:" + str(session['user-answers']))
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
        add_annex_html = add_annexes_dict[str(add_annex)]
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
            resource_html = annexes_dict[resource_name]
    if glossary != "None":
        is_glossary = "Present"
        glossary_html = glossaries_dict[str(glossary)]
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
                                    <input type="radio" class="form-check-input" id="radio1" name="optoption" value="option1" required/>
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
                                    <input type="radio" class="form-check-input" id="radio2" name="optoption" value="option2" required/>
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
                                    <input type="radio" class="form-check-input" id="radio3" name="optoption" value="option3" required/>
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
                                    <input type="radio" class="form-check-input" id="radio4" name="optoption" value="option4" required/>
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
                                        <input type="radio" class="form-check-input" id="radio1" name="optoption" value="option1" required/>
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
                                        <input type="radio" class="form-check-input" id="radio2" name="optoption" value="option2" required/>
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
                                        <input type="radio" class="form-check-input" id="radio3" name="optoption" value="option3" required/>
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
                        options_html = f"""
                            <div class="row" id="options-row">
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio1" name="optoption" value="option1" required/>
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
                                        <input type="radio" class="form-check-input" id="radio2" name="optoption" value="option2" required/>
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
            user_answers_dict[item[0]] = item[1]
        user_answers_store_dict['user_answers'] = user_answers_dict
        user_inputs_dict = {}
        for item in session['additional-inputs']:
            temp_item = item.split(": ")
            user_inputs_dict[temp_item[0]] = temp_item[1]
        user_answers_store_dict['user_inputs'] = user_inputs_dict
        col_answers.insert_one(user_answers_store_dict)
        resource_html = annexes_dict[resource_name]
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
        annex_download_html += annexes_dict[resource_name]
        pdf_html_no = random.randrange(100000, 999999)
        col_html.insert_one({
            'no': pdf_html_no,
            'pdf_html': annex_download_html
        })
        session['user-answers'] = []
        session['additional-inputs'] = []
    return render_template('maintenance.html', current = current_qn_no, question = qn, option_1 = op1, option_2 = op2, option_3 = op3, option_4 = op4, html = options_html, is_add_annex = is_add_annex, add_annex_html = add_annex_html, is_add_input = is_add_input, add_input_html = add_input_html, is_resource = is_resource, resource_html = resource_html, is_glossary = is_glossary, glossary_html = glossary_html, final_qn = int(final_qn), user_responses = user_answers_html, pdf_no = pdf_html_no)

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
        sel_op = "op0"
        if int(back) == 0:
            prev_qn_type = list(col_d.find({"qn_no": int(prev_qn_no)}))[0]['qn_type']
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
                    print("Next Before:" + str(session['user-answers']))
                    for item in user_answers_list:
                        if item[0] == prev_qn_no:
                            user_answers_list.remove(item)
                    user_answers_list.append([prev_qn_no, sel_op])
                    session['user-answers'] = user_answers_list
                    session.permanent = True
                    print("Next After:" + str(session['user-answers']))
                else:
                    session['user-answers'] = [[prev_qn_no, sel_op]]
                    session.permanent = True
                    print("Next Start:" + str(session['user-answers']))
                if 'additional-inputs' in session:
                    additional_inputs = session['additional-inputs']
                    print("Input Before:" + str(session['additional-inputs']))
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
                    print("Input After:" + str(session['additional-inputs']))
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
            search_result = list(col_d.find({"prev_qn_no": int(prev_qn_no), "sel_op": str(sel_op)}))[0]
        else:
            if int(prev_qn_no) == 1:
                return render_template("index.html")
            else:
                search_result = list(col_d.find({"qn_no": int(prev_qn_no)}))[0]['prev_qn_no']
                search_result = list(col_d.find({"qn_no": int(search_result)}))[0]
                user_answers_list = session['user-answers']
                print("Back Before:" + str(session['user-answers']))
                user_answers_list.pop()
                session['user-answers'] = user_answers_list
                session.permanent = True
                print("Back After:" + str(session['user-answers']))
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
        add_annex_html = add_annexes_dict[str(add_annex)]
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
            resource_html = annexes_dict[resource_name]
    if glossary != "None":
        is_glossary = "Present"
        glossary_html = glossaries_dict[str(glossary)]
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
                                    <input type="radio" class="form-check-input" id="radio1" name="optoption" value="option1" required/>
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
                                    <input type="radio" class="form-check-input" id="radio2" name="optoption" value="option2" required/>
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
                                    <input type="radio" class="form-check-input" id="radio3" name="optoption" value="option3" required/>
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
                                    <input type="radio" class="form-check-input" id="radio4" name="optoption" value="option4" required/>
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
                                        <input type="radio" class="form-check-input" id="radio1" name="optoption" value="option1" required/>
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
                                        <input type="radio" class="form-check-input" id="radio2" name="optoption" value="option2" required/>
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
                                        <input type="radio" class="form-check-input" id="radio3" name="optoption" value="option3" required/>
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
                        options_html = f"""
                            <div class="row" id="options-row">
                                <div class="col-sm-6 col-md-6 col-lg-6">
                                    <label>
                                        <input type="radio" class="form-check-input" id="radio1" name="optoption" value="option1" required/>
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
                                        <input type="radio" class="form-check-input" id="radio2" name="optoption" value="option2" required/>
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
            user_answers_dict[item[0]] = item[1]
        user_answers_store_dict['user_answers'] = user_answers_dict
        user_inputs_dict = {}
        for item in session['additional-inputs']:
            temp_item = item.split(": ")
            user_inputs_dict[temp_item[0]] = temp_item[1]
        user_answers_store_dict['user_inputs'] = user_inputs_dict
        col_answers.insert_one(user_answers_store_dict)
        resource_html = annexes_dict[resource_name]
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
        annex_download_html += annexes_dict[resource_name]
        pdf_html_no = random.randrange(100000, 999999)
        col_html.insert_one({
            'no': pdf_html_no,
            'pdf_html': annex_download_html
        })
        session['user-answers'] = []
        session['additional-inputs'] = []
    return render_template('divorce.html', current = current_qn_no, question = qn, option_1 = op1, option_2 = op2, option_3 = op3, option_4 = op4, html = options_html, is_add_annex = is_add_annex, add_annex_html = add_annex_html, is_add_input = is_add_input, add_input_html = add_input_html, is_resource = is_resource, resource_html = resource_html, is_glossary = is_glossary, glossary_html = glossary_html, final_qn = int(final_qn), user_responses = user_answers_html, pdf_no = pdf_html_no)

@app.route('/report/<no>.pdf')
def report(no):
    pdf_html = list(col_html.find({"no": int(no)}))[0]['pdf_html']
    page_html = render_template('download_pdf.html', html = pdf_html)
    return render_pdf(HTML(string = page_html))

def send_email(from_email, to_email, no):
    msg = EmailMessage()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Your Preliminary Intake Assessment Report from CJC"
    msg.set_content(f"""
        Hello,

        Thank you for completing the Preliminary Intake Assessment with the Community Justice Centre .

        You can access your report at http://Jahnvi371.pythonanywhere.com/report/{no}.pdf.

        Best regards,
        Community Justice Centre (CJC)
    """, subtype = "plain", charset = "us-ascii")
    with smtplib.SMTP('smtp.gmail.com') as s:
        s.starttls()
        s.send_message(msg)
    return None

@app.route('/send/<no>/<string:email_input>', methods = ['POST'])
def send(no, email_input):
    email = json.loads(email_input)
    return send_email("jahnvi@ygroo.com", email, no)

@app.route("/OSLAS_Criteria", methods=["POST", "GET"])
def OSLAS_Criteria():
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

        Criminal5 = request.form.getlist('Criminal5')

        Family_Question5a = request.form.getlist('Family_Question5a')
        Family_Question5b = request.form.getlist('Family_Question5b')

        # When the answer for Question 1 is "Yes"
        if Question1[0] == "Yes":
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 2 is "Yes"
        if Question1[0] == "No" and Question2[0] == "Yes":
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 3 is "Yes"
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "Yes":
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Criminal"
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Criminal":
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0],
                "Please select all that applies": Criminal5,
                "Current Date": datetime.now()
            })

        # When the answer for Question 1, 2, 3 is "No", Question 4 is "Family"
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Family":
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5b[0] == "None of the above":
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Claimant" and (Question5b[0] == "Tenancy agreement for residential premises not exceeding 2 years" or Question5b[0] == "Contract for sale of good" or  Question5b[0] == "Contract for provision of services" or Question5b[0] == "Damage to property not arising from or in connection with the use of a motor vehicle, or caused by a neighbour") and (Question5c_claimant[0] == "Appeal against a Small Claims Order" or Question5c_claimant[0] == "Set aside a Small Claims Order made in my absence" or Question5c_claimant[0] == "Execute or Enforce a Small Claims Order" or Question5c_claimant[0] == "None of the above"):
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Claimant" and (Question5b[0] == "Tenancy agreement for residential premises not exceeding 2 years" or Question5b[0] == "Contract for sale of good" or  Question5b[0] == "Contract for provision of services" or Question5b[0] == "Damage to property not arising from or in connection with the use of a motor vehicle, or caused by a neighbour") and Question5c_claimant[0] == "File a Claim":
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Claimant" and Question5b[0] == "Employment matters (i.e. Salary-related/ wrongful dismissal)" and Question5d_claimant_employment[0] == "File a Claim":
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Claimant" and Question5b[0] == "Employment matters (i.e. Salary-related/ wrongful dismissal)" and Question5d_claimant_employment[0] == "Resolve the dispute online":
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Claimant" and Question5b[0] == "Employment matters (i.e. Salary-related/ wrongful dismissal)" and (Question5d_claimant_employment[0] == "Appeal against an Employment Claims Order" or Question5d_claimant_employment[0] == "Enforce an Employment Claims Order" or Question5d_claimant_employment[0] == "Set aside an Employment Claims Order made in my absence" or Question5d_claimant_employment[0] == "None of the above"):
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Respondent" and (Question5b[0] == "Tenancy agreement for residential premises not exceeding 2 years" or Question5b[0] == "Contract for sale of good" or Question5b[0] == "Contract for provision of services" or Question5b[0] == "Damage to property not arising from or in connection with the use of a motor vehicle, or caused by a neighbour"):
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Respondent" and Question5b[0] == "Employment matters (i.e. Salary-related/ wrongful dismissal)" and (Question5d_respondent_employment[0] == "Settle the claim" or Question5d_respondent_employment[0] == "Dispute the claim" or Question5d_respondent_employment[0] == "File a Counterclaim" or Question5d_respondent_employment[0] == "Appeal against an Employment Claims Order" or Question5d_respondent_employment[0] == "Set aside an Employment Claims Order made in my absence" or Question5d_respondent_employment[0] == "None of the above"):
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Respondent" and Question5b[0] == "Employment matters (i.e. Salary-related/ wrongful dismissal)" and Question5d_respondent_employment[0] == "Resolve the dispute online":
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Claimant" and Question5b[0] == "Neighbour Disputes" and (Question5c_claimant_neighbour[0] == "Appeal against a Neighbour Dispute Claim Order" or Question5c_claimant_neighbour[0] == "Enforce an Neighbour Dispute Claim Order" or Question5c_claimant_neighbour[0] == "Set aside Neighbour Dispute Claim Order made in my absence" or Question5c_claimant_neighbour[0] == "None of the above"):
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Claimant" and Question5b[0] == "Neighbour Disputes" and Question5c_claimant_neighbour[0] == "File a Claim":
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Claimant" and Question5b[0] == "Neighbour Disputes" and Question5c_claimant_neighbour[0] == "Resolve the dispute online":
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Respondent" and Question5b[0] == "Neighbour Disputes" and Question5c_respondent_neighbour[0] == "Resolve the dispute(s) online":
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
        if Question1[0] == "No" and Question2[0] == "No" and Question3[0] == "No" and Question4[0] == "Civil" and Question5a[0] == "Respondent" and Question5b[0] == "Neighbour Disputes" and (Question5c_respondent_neighbour[0] == "Settle the claim" or Question5c_respondent_neighbour[0] == "Dispute the claim" or Question5c_respondent_neighbour[0] == "Appeal against a Neighbour Dispute Claim" or Question5c_respondent_neighbour[0] == "Set aside a Neighbour Dispute Claim made in my absence" or Question5c_respondent_neighbour[0] == "None of the above"):
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

    # OSLAS Criteria Question 1 database
    OCQuestion1 = list(col_oslas_criteria.find({"OCQ1": "1. Are you enquiring as a representative of a company (i.e. Pte Ltd)?"}))[0]
    OCQ1 = OCQuestion1["OCQ1"]
    OCQ1op1 = OCQuestion1["OCQ1op1"]
    OCQ1op2 = OCQuestion1["OCQ1op2"]

    # OSLAS Criteria Question 2 database
    OCQuestion2 = list(col_oslas_criteria.find({"OCQ2": "2. Are you currently represented by a lawyer?"}))[0]
    OCQ2 = OCQuestion2["OCQ2"]
    OCQ2op1 = OCQuestion2["OCQ2op1"]
    OCQ2op2 = OCQuestion2["OCQ2op2"]

    # OSLAS Criteria Question 3 database
    OCQuestion3 = list(col_oslas_criteria.find({"OCQ3": "3. Have you sought legal advice on this matter before?"}))[0]
    OCQ3 = OCQuestion3["OCQ3"]
    OCQ3op1 = OCQuestion3["OCQ3op1"]
    OCQ3op2 = OCQuestion3["OCQ3op2"]

    # OSLAS Criteria Question 4 database
    OCQuestion4 = list(col_oslas_criteria.find({"OCQ4": "4. What is the nature of your matter"}))[0]
    OCQ4 = OCQuestion4["OCQ4"]
    OCQ4op1 = OCQuestion4["OCQ4op1"]
    OCQ4op2 = OCQuestion4["OCQ4op2"]
    OCQ4op3 = OCQuestion4["OCQ4op3"]

    # OSLAS Criteria Question 5 database
    OCQuestion5 = list(col_oslas_criteria.find({"OCQ5": "5. Which of the following category best describes the matter you are seeking advice on?"}))[0]
    OCQ5 = OCQuestion5["OCQ5"]

    # OSLAS Criteria Civil(a) database
    OCCivil_a = list(col_oslas_criteria.find({"Civil_a": "a. I am the:"}))[0]
    Civil_a = OCCivil_a["Civil_a"]
    Civil_a_op1 = OCCivil_a["Civil_a_op1"]
    Civil_a_op2 = OCCivil_a["Civil_a_op2"]

    # OSLAS Criteria Civil(b) database
    OCCivil_b = list(col_oslas_criteria.find({"Civil_b": "b. My claim arises from:"}))[0]
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
    OCCivil_c_respondent = list(col_oslas_criteria.find({"Civil_c_respondent": "c. I want to:"}))[0]
    Civil_c_respondent = OCCivil_c_respondent["Civil_c_respondent"]
    Civil_c_respondent_op1 = OCCivil_c_respondent["Civil_c_respondent_op1"]
    Civil_c_respondent_op2 = OCCivil_c_respondent["Civil_c_respondent_op2"]
    Civil_c_respondent_op3 = OCCivil_c_respondent["Civil_c_respondent_op3"]
    Civil_c_respondent_op4 = OCCivil_c_respondent["Civil_c_respondent_op4"]
    Civil_c_respondent_op5 = OCCivil_c_respondent["Civil_c_respondent_op5"]
    Civil_c_respondent_op6 = OCCivil_c_respondent["Civil_c_respondent_op6"]

    # OSLAS Criteria Civil(c) claimant database
    OCCivil_c_claimant = list(col_oslas_criteria.find({"Civil_c_claimant": "c. I want to:"}))[0]
    Civil_c_claimant = OCCivil_c_claimant["Civil_c_claimant"]
    Civil_c_claimant_op1 = OCCivil_c_claimant["Civil_c_claimant_op1"]
    Civil_c_claimant_op2 = OCCivil_c_claimant["Civil_c_claimant_op2"]
    Civil_c_claimant_op3 = OCCivil_c_claimant["Civil_c_claimant_op3"]
    Civil_c_claimant_op4 = OCCivil_c_claimant["Civil_c_claimant_op4"]
    Civil_c_claimant_op5 = OCCivil_c_claimant["Civil_c_claimant_op5"]

    # OSLAS Criteria Civil(c) employment database
    OCCivil_c_employment = list(col_oslas_criteria.find({"Civil_c_employment": "c. My current situation:"}))[0]
    Civil_c_employment = OCCivil_c_employment["Civil_c_employment"]
    Civil_c_claimant_employment_op1 = OCCivil_c_employment["Civil_c_claimant_employment_op1"]
    Civil_c_claimant_employment_op2 = OCCivil_c_employment["Civil_c_claimant_employment_op2"]
    Civil_c_respondent_employment_op1 = OCCivil_c_employment["Civil_c_respondent_employment_op1"]
    Civil_c_employment_none = OCCivil_c_employment["Civil_c_employment_none"]

    # OSLAS Criteria Civil(d) claimant database
    OCCivil_d_claimant = list(col_oslas_criteria.find({"Civil_d_claimant": "d. My claim is:"}))[0]
    Civil_d_claimant = OCCivil_d_claimant["Civil_d_claimant"]
    Civil_d_claimant_op1 = OCCivil_d_claimant["Civil_d_claimant_op1"]
    Civil_d_claimant_op2 = OCCivil_d_claimant["Civil_d_claimant_op2"]
    Civil_d_claimant_op3 = OCCivil_d_claimant["Civil_d_claimant_op3"]

    # OSLAS Criteria Civil(d) claimant employment database
    OCCivil_d_claimant_employment = list(col_oslas_criteria.find({"Civil_d_claimant_employment": "d. I wish to:"}))[0]
    Civil_d_claimant_employment = OCCivil_d_claimant_employment["Civil_d_claimant_employment"]
    Civil_d_claimant_employment_op1 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op1"]
    Civil_d_claimant_employment_op2 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op2"]
    Civil_d_claimant_employment_op3 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op3"]
    Civil_d_claimant_employment_op4 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op4"]
    Civil_d_claimant_employment_op5 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op5"]
    Civil_d_claimant_employment_op6 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op6"]

    # OSLAS Criteria Civil(d) respondent employment database
    OCCivil_d_respondent_employment = list(col_oslas_criteria.find({"Civil_d_respondent_employment": "d. I wish to:"}))[0]
    Civil_d_respondent_employment = OCCivil_d_respondent_employment["Civil_d_respondent_employment"]
    Civil_d_respondent_employment_op1 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op1"]
    Civil_d_respondent_employment_op2 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op2"]
    Civil_d_respondent_employment_op3 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op3"]
    Civil_d_respondent_employment_op4 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op4"]
    Civil_d_respondent_employment_op5 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op5"]
    Civil_d_respondent_employment_op6 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op6"]
    Civil_d_respondent_employment_op7 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op7"]

    # OSLAS Criteria Civil(e) claimant employment database
    OCCivil_e_claimant_employment = list(col_oslas_criteria.find({"Civil_e_claimant_employment": "I have..."}))[0]
    Civil_e_claimant_employment = OCCivil_e_claimant_employment["Civil_e_claimant_employment"]
    Civil_e_claimant_employment_op1 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op1"]
    Civil_e_claimant_employment_op2 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op2"]
    Civil_e_claimant_employment_op3 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op3"]
    Civil_e_claimant_employment_op4 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op4"]
    Civil_e_claimant_employment_op5 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op5"]

    # OSLAS Criteria Resolve the dispute online database
    OCResolve_the_dispute_online = list(col_oslas_criteria.find({"Resolve_the_dispute_online": "I would like to resolve the dispute filed through the Community Justice and Tribunals System (CJTS), without going to court, via the followings:"}))[0]
    Resolve_the_dispute_online = OCResolve_the_dispute_online["Resolve_the_dispute_online"]
    Resolve_the_dispute_online_op1 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op1"]
    Resolve_the_dispute_online_op2 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op2"]
    Resolve_the_dispute_online_op3 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op3"]

    # OSLAS Criteria Civil(c) claimant neighbour database 
    OCCivil_c_neighbour = list(col_oslas_criteria.find({"Civil_c_claimant_neighbour": "c. I wish to:"}))[0]
    Civil_c_claimant_neighbour = OCCivil_c_neighbour["Civil_c_claimant_neighbour"]
    Civil_c_claimant_neighbour_op1 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op1"]
    Civil_c_claimant_neighbour_op2 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op2"]
    Civil_c_claimant_neighbour_op3 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op3"]
    Civil_c_claimant_neighbour_op4 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op4"]
    Civil_c_claimant_neighbour_op5 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op5"]
    Civil_c_claimant_neighbour_op6 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op6"]

    # OSLAS Criteria Civil(d) claimant neighbour database
    OCCivil_d_claimant_neighbour = list(col_oslas_criteria.find({"Civil_d_claimant_neighbour": "I have..."}))[0]
    Civil_d_claimant_neighbour = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour"]
    Civil_d_claimant_neighbour_op1 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op1"]
    Civil_d_claimant_neighbour_op2 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op2"]
    Civil_d_claimant_neighbour_op3 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op3"]
    Civil_d_claimant_neighbour_op4 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op4"]
    Civil_d_claimant_neighbour_op5 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op5"]
    Civil_d_claimant_neighbour_op6 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op6"]

    # OSLAS Criteria Civil(c) respondent neighbour database 
    OCCivil_c_respondent_neighbour = list(col_oslas_criteria.find({"Civil_c_respondent_neighbour": "c. I wish to:"}))[0]
    Civil_c_respondent_neighbour = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour"]
    Civil_c_respondent_neighbour_op1 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op1"]
    Civil_c_respondent_neighbour_op2 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op2"]
    Civil_c_respondent_neighbour_op3 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op3"]
    Civil_c_respondent_neighbour_op4 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op4"]
    Civil_c_respondent_neighbour_op5 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op5"]
    Civil_c_respondent_neighbour_op6 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op6"]

    # OSLAS Criteria Family database
    OCFamily = list(col_oslas_criteria.find({"Family_i": "i. Integrated Family Application Management System (iFAMS)"}))[0]
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
    OCCriminal = list(col_oslas_criteria.find({"Criminal": "Please select all that applies"}))[0]
    Criminal = OCCriminal["Criminal"]
    Criminal_op1 = OCCriminal["Criminal_op1"]
    Criminal_op2 = OCCriminal["Criminal_op2"]
    Criminal_op3 = OCCriminal["Criminal_op3"]
    Criminal_op4 = OCCriminal["Criminal_op4"]
    Criminal_op5 = OCCriminal["Criminal_op5"]
    Criminal_op6 = OCCriminal["Criminal_op6"]
    Criminal_op7 = OCCriminal["Criminal_op7"]

    return render_template('OSLAS_criteria.html', OCQ1 = OCQ1, OCQ1op1 = OCQ1op1, OCQ1op2 = OCQ1op2,
    OCQ2 = OCQ2, OCQ2op1 = OCQ2op1, OCQ2op2 = OCQ2op2, 
    OCQ3 = OCQ3, OCQ3op1 = OCQ3op1, OCQ3op2 = OCQ3op2, 
    OCQ4 = OCQ4, OCQ4op1 = OCQ4op1, OCQ4op2 = OCQ4op2, OCQ4op3 = OCQ4op3,
    OCQ5 = OCQ5,
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
    Family_i = Family_i, Family_i_op1 = Family_i_op1, Family_i_op2 = Family_i_op2, Family_i_op3 = Family_i_op3, Family_i_op4 = Family_i_op4, Family_ii = Family_ii, Family_ii_prompt = Family_ii_prompt, Family_ii_op1 = Family_ii_op1, Family_ii_op2 = Family_ii_op2, Family_ii_op3 = Family_ii_op3,
    Criminal = Criminal, Criminal_op1 = Criminal_op1, Criminal_op2 = Criminal_op2, Criminal_op3 = Criminal_op3, Criminal_op4 = Criminal_op4, Criminal_op5 = Criminal_op5, Criminal_op6 = Criminal_op6, Criminal_op7 = Criminal_op7)

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

def graph(n, type):
    fig = plt.figure(figsize = (12, 10), dpi = 100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('equal')
    plt.rcParams.update({'font.size': 42})
    plt.rcParams.update({'font.weight': 'bold'})
    plt.rcParams.update({'text.color': 'white'})
    plt.rcParams.update({'legend.fontsize': 42})
    plt.rcParams.update({'legend.labelcolor': '#000000'})
    labels = session[f'graph{n}'][0]
    values = session[f'graph{n}'][1]
    if type == "maintenance":
        if Counter(values)[0] == len(values):
            with open(f'./static/images/m_graph{n}.png', 'wb') as f:
                f.write(requests.get('https://ouch-cdn2.icons8.com/5hna5mhG7hpfR1YAEraMYePOhGpBUprTy7CTxxXSJRg/rs:fit:256:192/czM6Ly9pY29uczgu/b3VjaC1wcm9kLmFz/c2V0cy9zdmcvNzgy/L2FiMGEyZmFkLTJm/N2QtNGM2Ni04ZmQy/LWQ3OWE4YmIxOTM3/NC5zdmc.png').content)
        else:
            ax.pie(values, autopct = lambda p: '{:.0f}%'.format(round(p)) if p > 0 else '')
            plt.legend(labels, loc = "lower center", framealpha = 0, bbox_to_anchor = (0.5, -0.3))
            plt.savefig(f'./static/images/m_graph{n}.png', bbox_inches = 'tight', transparent = True)
    elif type == "divorce":
        if Counter(values)[0] == len(values):
            with open(f'./static/images/d_graph{n}.png', 'wb') as f:
                f.write(requests.get('https://ouch-cdn2.icons8.com/5hna5mhG7hpfR1YAEraMYePOhGpBUprTy7CTxxXSJRg/rs:fit:256:192/czM6Ly9pY29uczgu/b3VjaC1wcm9kLmFz/c2V0cy9zdmcvNzgy/L2FiMGEyZmFkLTJm/N2QtNGM2Ni04ZmQy/LWQ3OWE4YmIxOTM3/NC5zdmc.png').content)
        else:
            ax.pie(values, autopct = lambda p: '{:.0f}%'.format(round(p)) if p > 0 else '')
            plt.legend(labels, loc = "lower center", framealpha = 0, bbox_to_anchor = (0.5, -0.3))
            plt.savefig(f'./static/images/d_graph{n}.png', bbox_inches = 'tight', transparent = True)
    plt.close(fig)
    return True

@app.route('/admin/dashboard/maintenance')
def maintenance_dashboard():
    if 'adminname' in session and 'adminemail' in session and 'adminpassword' in session:
        responses = list(col_answers.find({'type': 'maintenance'}))
        n_responses = len(responses)
        user_answers = []
        for response in responses:
            user_answers.append(response['user_answers'])
        q1 = []
        q2 = []
        q3 = []
        q4 = []
        q5 = []
        q6 = []
        q9 = []
        q10 = []
        for answer in user_answers:
            if 'I am currently...' in answer:
                q1.append(answer['I am currently...'])
            if 'I am seeking to...' in answer:
                q2.append(answer['I am seeking to...'])
            if 'I am seeking to apply for maintenance for...' in answer:
                q3.append(answer['I am seeking to apply for maintenance for...'])
            if 'I am...' in answer:
                q4.append(answer['I am...'])
            if 'I need...' in answer:
                q5.append(answer['I need...'])
            if 'I...' in answer:
                q6.append(answer['I...'])
            if 'My child(ren) is/are...' in answer:
                q9.append(answer['My child(ren) is/are...'])
            if 'My child(ren)...' in answer:
                q10.append(answer['My child(ren)...'])
        q1_labels = ['married', 'undergoing divorce', 'not married', 'divorced']
        q1_values = [Counter(q1)['married'], Counter(q1)['undergoing divorce'], Counter(q1)['not married'], Counter(q1)['divorced']]
        q2_labels = ['enforce', 'vary', 'unsure']
        q2_values = [Counter(q2)['enforce'], Counter(q2)['vary'], Counter(q2)['unsure']]
        q3_labels = ['myself', 'my child(ren)', 'both myself and my child(ren)']
        q3_values = [Counter(q3)['myself'], Counter(q3)['my child(ren)'], Counter(q3)['both myself and my child(ren)']]
        q4_labels = ['willing to consider mediation', 'not willing to consider mediation']
        q4_values = [Counter(q4)['willing to consider mediation'], Counter(q4)['not willing to consider mediation']]
        q5_labels = ['financial support', 'social and emotional support', 'both', 'none']
        q5_values = [Counter(q5)['financial support'], Counter(q5)['social and emotional support'], Counter(q5)['financial support, social and emotional support'], Counter(q5)['none of the above']]
        q6_labels = ['have a maintenance order', 'do not have a maintenance order']
        q6_values = [Counter(q6)['have a maintenance order'], Counter(q6)['do not have a maintenance order']]
        q9_labels = ['below 21 years old', 'above 21 years old']
        q9_values = [Counter(q9)['below 21 years old'], Counter(q9)['above 21 years old']]
        q10_labels = ['is/are full time NSman or student', 'has/have mental or physical disability', 'none']
        q10_values = [Counter(q10)['is/are full time NSman or student'], Counter(q10)['has/have mental or physical disability'], Counter(q10)['none of the above']]
        session['graph1'] = [q1_labels, q1_values]
        graph1 = graph(1, type = "maintenance")
        session['graph2'] = [q2_labels, q2_values]
        graph2 = graph(2, type = "maintenance")
        session['graph3'] = [q3_labels, q3_values]
        graph3 = graph(3, type = "maintenance")
        session['graph4'] = [q5_labels, q5_values]
        graph4 = graph(4, type = "maintenance")
        session['graph5'] = [q4_labels, q4_values]
        graph5 = graph(5, type = "maintenance")
        session['graph6'] = [q9_labels, q9_values]
        graph6 = graph(6, type = "maintenance")
        session['graph7'] = [q10_labels, q10_values]
        graph7 = graph(7, type = "maintenance")
        return render_template("maintenance_dashboard.html", n_responses = n_responses, n_mo = q6_values[0], n_no_mo = q6_values[1])
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/dashboard/divorce')
def divorce_dashboard():
    if 'adminname' in session and 'adminemail' in session and 'adminpassword' in session:
        responses = list(col_answers.find({'type': 'divorce'}))
        n_responses = len(responses)
        user_answers = []
        for response in responses:
            user_answers.append(response['user_answers'])
        q1 = []
        q2 = []
        q3 = []
        q4 = []
        q5 = []
        q6 = []
        q7 = []
        q8 = []
        q9 = []
        q10 = []
        for answer in user_answers:
            if 'I am a...' in answer:
                q1.append(answer['I am a...'])
            if 'I am currenly...' in answer:
                q2.append(answer['I am seeking to...'])
            if 'I am married under the...' in answer:
                q3.append(answer['I am married under the...'])
            if 'I have been married for...' in answer:
                q4.append(answer['I have been married for...'])
            if 'I need an interim order for...' in answer:
                q5.append(answer['I need an interim order for...'])
            if 'I...' in answer:
                q6.append(answer['I...'])
            if "My child(ren) is/are..." in answer:
                q7.append(answer['My child(ren) is/are...'])
            if 'My spouse and I agree on...' in answer:
                q8.append(answer['My spouse and I agree on...'])
            if 'My spouse and I are...' in answer:
                q9.append(answer['My spouse and I are...'])
            if 'Prior to the filing of a divorce application, I have been living in Singapore for...' in answer:
                q10.append(answer['Prior to the filing of a divorce application, I have been living in Singapore for…'])
        q1_labels = ['Singapore Citizen', 'Foreigner']
        q1_values = [Counter(q1)['Singapore Citizen'], Counter(q1)['Foreigner']]
        q2_labels = ['preparing for divorce', 'undergoing divorce', 'unsure if I should get a divorce']
        q2_values = [Counter(q2)['preparing for divorce'], Counter(q2)['undergoing divorce'], Counter(q2)['unsure if I should get a divorce']]
        q3_labels = ['civil law', 'syariah law']
        q3_values = [Counter(q3)['civil law'], Counter(q3)['syariah law']]
        q4_labels = ['3 years or more', 'less than 3 years']
        q4_values = [Counter(q4)['3 years or more'], Counter(q4)['less than 3 years']]
        q5_labels = ['maintenance', 'personal protection', 'both', 'none']
        q5_values = [Counter(q5)['maintenance'], Counter(q5)['personal protection'], Counter(q5)['maintenance, personal protection'], Counter(q5)['none of the above']]
        q6_labels = ['have', 'do not have']
        q6_values = [Counter(q6)['have child(ren)'], Counter(q6)['do not have child(ren)']]
        q7_labels = ['below 21 years old', 'above 21 years old']
        q7_values = [Counter(q7)['below 21 years old'], Counter(q7)['above 21 years old']]
        q8_labels = ['divorce', 'all ancillary matters', 'both', 'none']
        q8_values = [Counter(q8)['divorce'], Counter(q8)['all ancillary matters'], Counter(q8)['divorce, all ancillary matters'], Counter(q8)['none of the above']]
        q9_labels = ['willing to consider mediation', 'not willing to consider mediation']
        q9_values = [Counter(q9)['willing to consider mediation'], Counter(q9)['not willing to consider mediation']]
        q10_labels = ['3 continuous years or more', 'less than 3 continuous years']
        q10_values = [Counter(q10)['3 continuous years or more'], Counter(q10)['less than 3 continuous years']]
        session['graph8'] = [q1_labels, q1_values]
        graph8 = graph(8, type = 'divorce')
        session['graph9'] = [q10_labels, q10_values]
        graph9 = graph(9, type = 'divorce')
        session['graph10'] = [q4_labels, q4_values]
        graph10 = graph(10, type = 'divorce')
        session['graph11'] = [q6_labels, q6_values]
        graph11 = graph(11, type = 'divorce')
        session['graph12'] = [q7_labels, q7_values]
        graph12 = graph(12, type = 'divorce')
        session['graph13'] = [q3_labels, q3_values]
        graph13 = graph(13, type = 'divorce')
        session['graph14'] = [q8_labels, q8_values]
        graph14 = graph(14, type = 'divorce')
        session['graph15'] = [q9_labels, q9_values]
        graph15 = graph(15, type = 'divorce')
        session['graph16'] = [q5_labels, q5_values]
        graph16 = graph(16, type = 'divorce')
        return render_template("divorce_dashboard.html", n_responses = n_responses, n_un = q2_values[2], n_pd = q2_values[0], n_ud = q2_values[1])
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
        if qn_sample['glossary'] == "None":
            glossary = None
        else:
            glossary = glossaries_dict[qn_sample['glossary']]
        if qn_sample['add_annex'] == "None":
            add_annex = None
        else:
            add_annex = add_annexes_dict[qn_sample['add_annex']]
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
        if qn_sample['glossary'] == "None":
            glossary = None
        else:
            glossary = glossaries_dict[qn_sample['glossary']]
        if qn_sample['add_annex'] == "None":
            add_annex = None
        else:
            add_annex = add_annexes_dict[qn_sample['add_annex']]
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
        glossary = glossaries_dict[qn_sample['glossary']]
    if qn_sample['add_annex'] == "None":
        add_annex = None
    else:
        add_annex = add_annexes_dict[qn_sample['add_annex']]
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
    glossary_html = None
    if glossary != None:
        glossary_html = glossary
    add_annex_html = None
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
        glossary = glossaries_dict[qn_sample['glossary']]
    if qn_sample['add_annex'] == "None":
        add_annex = None
    else:
        add_annex = add_annexes_dict[qn_sample['add_annex']]
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
    glossary_html = None
    if glossary != None:
        glossary_html = glossary
    add_annex_html = None
    if add_annex != None:
        add_annex_html = add_annex
    return render_template("divorce_cms_update.html", qn_code = qn_code, qn = qn_text, qn_type = qn_type, html = choices_html, glossary_html = glossary_html, add_annex_html = add_annex_html)

@app.route('/admin/cms/maintenance/update/effect/<qn_code>', methods = ['POST', 'GET'])
def maintenance_cms_update_effect(qn_code):
    form_response = request.form.to_dict(flat = False)
    qn = form_response['qn'][0]
    col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'qn': qn}})
    glossary = form_response['ckeditor'][0]
    add_annex = form_response['ckeditor'][1]
    if glossary != "":
        if f'm_q{str(qn_code)}_glossary' not in glossaries_dict:
            glossaries_dict[f'm_q{str(qn_code)}_glossary'] = glossary
            col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'glossary': f'm_q{str(qn_code)}_glossary'}})
        else:
            glossaries_dict.pop('m_q{str(qn_code)}_glossary')
            col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'glossary': 'None'}})
    if add_annex != "":
        if f'm_q{str(qn_code)}_add_annex' not in add_annexes_dict:
            add_annexes_dict[f'm_q{str(qn_code)}_add_annex'] = add_annex
            col_m.update_many({'qn_code': int(qn_code)}, {'$set': {'add_annex': f'm_q{str(qn_code)}_add_annex'}})
        else:
            add_annexes_dict[f'm_q{str(qn_code)}_add_annex'] = add_annex
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
    glossary = form_response['ckeditor'][0]
    add_annex = form_response['ckeditor'][1]
    if glossary != "":
        if f'd_q{str(qn_code)}_glossary' not in glossaries_dict:
            glossaries_dict[f'd_q{str(qn_code)}_glossary'] = glossary
            col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'glossary': f'd_q{str(qn_code)}_glossary'}})
        else:
            print(glossaries_dict.keys())
            if f'd_q{str(qn_code)}_glossary' in glossaries_dict:
                glossaries_dict.pop(f'd_q{str(qn_code)}_glossary')
            col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'glossary': 'None'}})
    if add_annex != "":
        if f'd_q{str(qn_code)}_add_annex' not in add_annexes_dict:
            add_annexes_dict[f'd_q{str(qn_code)}_add_annex'] = add_annex
            col_d.update_many({'qn_code': int(qn_code)}, {'$set': {'add_annex': f'd_q{str(qn_code)}_add_annex'}})
        else:
            print(add_annexes_dict.keys())
            if f'd_q{str(qn_code)}_add_annex' in add_annexes_dict:
                add_annexes_dict[f'd_q{str(qn_code)}_add_annex'] = add_annex
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
        annex_html = annexes_dict[annex_name]
    elif type == "divorce":
        annex_name = annex_code.lower().replace(" ", "_") + "_d"
        annex_display_name = annex_name.replace("_d", " (Divorce)").replace("_", " ").upper().replace("ANNEX", "Annex").replace("DIVORCE", "Divorce")
        annex_html = annexes_dict[annex_name]
    return render_template('annex_update.html', type = type, annex_name = annex_name, annex_display_name = annex_display_name, annex_html = annex_html)

@app.route('/admin/cms/annex/update/effect/<type>/<annex_name>', methods = ['POST', 'GET'])
def annex_update_effect(annex_name, type):
    annexes_dict[annex_name] = request.form.to_dict()['annex']
    if type == "maintenance":
        return redirect(url_for('maintenance_cms'))
    elif type == "divorce":
        return redirect(url_for('divorce_cms'))
    
@app.route('/admin/cms/oslas', methods=["POST", "GET"])
def oslas_cms():
    if request.method == "POST":
        Updated_Question1 = request.form.getlist('Question1')
        Updated_OCQ1op1 = request.form.getlist('OCQ1op1')
        Updated_OCQ1op2 = request.form.getlist('OCQ1op2')

        col_oslas_criteria.update_one({"QN": "1"}, {'$set': {"OCQ1op1": Updated_OCQ1op1[0]}})

        print(Updated_Question1)
        print(Updated_OCQ1op1)
        print(Updated_OCQ1op2)

    # OSLAS Criteria Question 1 database
    OCQuestion1 = list(col_oslas_criteria.find({"OCQ1": "1. Are you enquiring as a representative of a company (i.e. Pte Ltd)?"}))[0]
    OCQ1 = OCQuestion1["OCQ1"]
    OCQ1op1 = OCQuestion1["OCQ1op1"]
    OCQ1op2 = OCQuestion1["OCQ1op2"]

    # OSLAS Criteria Question 2 database
    OCQuestion2 = list(col_oslas_criteria.find({"OCQ2": "2. Are you currently represented by a lawyer?"}))[0]
    OCQ2 = OCQuestion2["OCQ2"]
    OCQ2op1 = OCQuestion2["OCQ2op1"]
    OCQ2op2 = OCQuestion2["OCQ2op2"]

    # OSLAS Criteria Question 3 database
    OCQuestion3 = list(col_oslas_criteria.find({"OCQ3": "3. Have you sought legal advice on this matter before?"}))[0]
    OCQ3 = OCQuestion3["OCQ3"]
    OCQ3op1 = OCQuestion3["OCQ3op1"]
    OCQ3op2 = OCQuestion3["OCQ3op2"]

    # OSLAS Criteria Question 4 database
    OCQuestion4 = list(col_oslas_criteria.find({"OCQ4": "4. What is the nature of your matter"}))[0]
    OCQ4 = OCQuestion4["OCQ4"]
    OCQ4op1 = OCQuestion4["OCQ4op1"]
    OCQ4op2 = OCQuestion4["OCQ4op2"]
    OCQ4op3 = OCQuestion4["OCQ4op3"]

    # OSLAS Criteria Question 5 database
    OCQuestion5 = list(col_oslas_criteria.find({"OCQ5": "5. Which of the following category best describes the matter you are seeking advice on?"}))[0]
    OCQ5 = OCQuestion5["OCQ5"]

    # OSLAS Criteria Civil(a) database
    OCCivil_a = list(col_oslas_criteria.find({"Civil_a": "a. I am the:"}))[0]
    Civil_a = OCCivil_a["Civil_a"]
    Civil_a_op1 = OCCivil_a["Civil_a_op1"]
    Civil_a_op2 = OCCivil_a["Civil_a_op2"]

    # OSLAS Criteria Civil(b) database
    OCCivil_b = list(col_oslas_criteria.find({"Civil_b": "b. My claim arises from:"}))[0]
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
    OCCivil_c_respondent = list(col_oslas_criteria.find({"Civil_c_respondent": "c. I want to:"}))[0]
    Civil_c_respondent = OCCivil_c_respondent["Civil_c_respondent"]
    Civil_c_respondent_op1 = OCCivil_c_respondent["Civil_c_respondent_op1"]
    Civil_c_respondent_op2 = OCCivil_c_respondent["Civil_c_respondent_op2"]
    Civil_c_respondent_op3 = OCCivil_c_respondent["Civil_c_respondent_op3"]
    Civil_c_respondent_op4 = OCCivil_c_respondent["Civil_c_respondent_op4"]
    Civil_c_respondent_op5 = OCCivil_c_respondent["Civil_c_respondent_op5"]
    Civil_c_respondent_op6 = OCCivil_c_respondent["Civil_c_respondent_op6"]

    # OSLAS Criteria Civil(c) claimant database
    OCCivil_c_claimant = list(col_oslas_criteria.find({"Civil_c_claimant": "c. I want to:"}))[0]
    Civil_c_claimant = OCCivil_c_claimant["Civil_c_claimant"]
    Civil_c_claimant_op1 = OCCivil_c_claimant["Civil_c_claimant_op1"]
    Civil_c_claimant_op2 = OCCivil_c_claimant["Civil_c_claimant_op2"]
    Civil_c_claimant_op3 = OCCivil_c_claimant["Civil_c_claimant_op3"]
    Civil_c_claimant_op4 = OCCivil_c_claimant["Civil_c_claimant_op4"]
    Civil_c_claimant_op5 = OCCivil_c_claimant["Civil_c_claimant_op5"]

    # OSLAS Criteria Civil(c) employment database
    OCCivil_c_employment = list(col_oslas_criteria.find({"Civil_c_employment": "c. My current situation:"}))[0]
    Civil_c_employment = OCCivil_c_employment["Civil_c_employment"]
    Civil_c_claimant_employment_op1 = OCCivil_c_employment["Civil_c_claimant_employment_op1"]
    Civil_c_claimant_employment_op2 = OCCivil_c_employment["Civil_c_claimant_employment_op2"]
    Civil_c_respondent_employment_op1 = OCCivil_c_employment["Civil_c_respondent_employment_op1"]
    Civil_c_employment_none = OCCivil_c_employment["Civil_c_employment_none"]

    # OSLAS Criteria Civil(d) claimant database
    OCCivil_d_claimant = list(col_oslas_criteria.find({"Civil_d_claimant": "d. My claim is:"}))[0]
    Civil_d_claimant = OCCivil_d_claimant["Civil_d_claimant"]
    Civil_d_claimant_op1 = OCCivil_d_claimant["Civil_d_claimant_op1"]
    Civil_d_claimant_op2 = OCCivil_d_claimant["Civil_d_claimant_op2"]
    Civil_d_claimant_op3 = OCCivil_d_claimant["Civil_d_claimant_op3"]

    # OSLAS Criteria Civil(d) claimant employment database
    OCCivil_d_claimant_employment = list(col_oslas_criteria.find({"Civil_d_claimant_employment": "d. I wish to:"}))[0]
    Civil_d_claimant_employment = OCCivil_d_claimant_employment["Civil_d_claimant_employment"]
    Civil_d_claimant_employment_op1 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op1"]
    Civil_d_claimant_employment_op2 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op2"]
    Civil_d_claimant_employment_op3 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op3"]
    Civil_d_claimant_employment_op4 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op4"]
    Civil_d_claimant_employment_op5 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op5"]
    Civil_d_claimant_employment_op6 = OCCivil_d_claimant_employment["Civil_d_claimant_employment_op6"]

    # OSLAS Criteria Civil(d) respondent employment database
    OCCivil_d_respondent_employment = list(col_oslas_criteria.find({"Civil_d_respondent_employment": "d. I wish to:"}))[0]
    Civil_d_respondent_employment = OCCivil_d_respondent_employment["Civil_d_respondent_employment"]
    Civil_d_respondent_employment_op1 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op1"]
    Civil_d_respondent_employment_op2 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op2"]
    Civil_d_respondent_employment_op3 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op3"]
    Civil_d_respondent_employment_op4 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op4"]
    Civil_d_respondent_employment_op5 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op5"]
    Civil_d_respondent_employment_op6 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op6"]
    Civil_d_respondent_employment_op7 = OCCivil_d_respondent_employment["Civil_d_respondent_employment_op7"]

    # OSLAS Criteria Civil(e) claimant employment database
    OCCivil_e_claimant_employment = list(col_oslas_criteria.find({"Civil_e_claimant_employment": "I have..."}))[0]
    Civil_e_claimant_employment = OCCivil_e_claimant_employment["Civil_e_claimant_employment"]
    Civil_e_claimant_employment_op1 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op1"]
    Civil_e_claimant_employment_op2 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op2"]
    Civil_e_claimant_employment_op3 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op3"]
    Civil_e_claimant_employment_op4 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op4"]
    Civil_e_claimant_employment_op5 = OCCivil_e_claimant_employment["Civil_e_claimant_employment_op5"]

    # OSLAS Criteria Resolve the dispute online database
    OCResolve_the_dispute_online = list(col_oslas_criteria.find({"Resolve_the_dispute_online": "I would like to resolve the dispute filed through the Community Justice and Tribunals System (CJTS), without going to court, via the followings:"}))[0]
    Resolve_the_dispute_online = OCResolve_the_dispute_online["Resolve_the_dispute_online"]
    Resolve_the_dispute_online_op1 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op1"]
    Resolve_the_dispute_online_op2 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op2"]
    Resolve_the_dispute_online_op3 = OCResolve_the_dispute_online["Resolve_the_dispute_online_op3"]

    # OSLAS Criteria Civil(c) claimant neighbour database 
    OCCivil_c_neighbour = list(col_oslas_criteria.find({"Civil_c_claimant_neighbour": "c. I wish to:"}))[0]
    Civil_c_claimant_neighbour = OCCivil_c_neighbour["Civil_c_claimant_neighbour"]
    Civil_c_claimant_neighbour_op1 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op1"]
    Civil_c_claimant_neighbour_op2 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op2"]
    Civil_c_claimant_neighbour_op3 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op3"]
    Civil_c_claimant_neighbour_op4 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op4"]
    Civil_c_claimant_neighbour_op5 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op5"]
    Civil_c_claimant_neighbour_op6 = OCCivil_c_neighbour["Civil_c_claimant_neighbour_op6"]

    # OSLAS Criteria Civil(d) claimant neighbour database
    OCCivil_d_claimant_neighbour = list(col_oslas_criteria.find({"Civil_d_claimant_neighbour": "I have..."}))[0]
    Civil_d_claimant_neighbour = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour"]
    Civil_d_claimant_neighbour_op1 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op1"]
    Civil_d_claimant_neighbour_op2 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op2"]
    Civil_d_claimant_neighbour_op3 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op3"]
    Civil_d_claimant_neighbour_op4 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op4"]
    Civil_d_claimant_neighbour_op5 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op5"]
    Civil_d_claimant_neighbour_op6 = OCCivil_d_claimant_neighbour["Civil_d_claimant_neighbour_op6"]

    # OSLAS Criteria Civil(c) respondent neighbour database 
    OCCivil_c_respondent_neighbour = list(col_oslas_criteria.find({"Civil_c_respondent_neighbour": "c. I wish to:"}))[0]
    Civil_c_respondent_neighbour = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour"]
    Civil_c_respondent_neighbour_op1 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op1"]
    Civil_c_respondent_neighbour_op2 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op2"]
    Civil_c_respondent_neighbour_op3 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op3"]
    Civil_c_respondent_neighbour_op4 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op4"]
    Civil_c_respondent_neighbour_op5 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op5"]
    Civil_c_respondent_neighbour_op6 = OCCivil_c_respondent_neighbour["Civil_c_respondent_neighbour_op6"]

    # OSLAS Criteria Family database
    OCFamily = list(col_oslas_criteria.find({"Family_i": "i. Integrated Family Application Management System (iFAMS)"}))[0]
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
    OCCriminal = list(col_oslas_criteria.find({"Criminal": "Please select all that applies"}))[0]
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
    Family_i = Family_i, Family_i_op1 = Family_i_op1, Family_i_op2 = Family_i_op2, Family_i_op3 = Family_i_op3, Family_i_op4 = Family_i_op4, Family_ii = Family_ii, Family_ii_prompt = Family_ii_prompt, Family_ii_op1 = Family_ii_op1, Family_ii_op2 = Family_ii_op2, Family_ii_op3 = Family_ii_op3,
    Criminal = Criminal, Criminal_op1 = Criminal_op1, Criminal_op2 = Criminal_op2, Criminal_op3 = Criminal_op3, Criminal_op4 = Criminal_op4, Criminal_op5 = Criminal_op5, Criminal_op6 = Criminal_op6, Criminal_op7 = Criminal_op7)
    
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

if __name__ == '__main__':
    app.debug = True
    app.run()