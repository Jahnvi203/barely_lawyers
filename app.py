from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
from pymongo import MongoClient
from resources.add_annexes import add_annexes_dict
from resources.add_inputs import add_inputs_dict
from resources.annexes import annexes_dict
from resources.glossaries import glossaries_dict
from resources.download_annexes import download_annexes_dict
from flask_weasyprint import HTML, render_pdf, CSS
from suggest_advice import suggest_advice
import random
import ssl
import smtplib
from email.mime.text import MIMEText
import json
import datetime

app = Flask(__name__)
app.secret_key = '1E44M1ixSeNGzO3T0dqIoXra7De5B46n'
app.config['SESSION_PERMANENT'] = True
app.config["SESSION_TYPE"] = "filesystem"

# Database Connection
uri = "mongodb+srv://Jahnvi203:Jahnvi203@cluster0.cn63w2k.mongodb.net/app?retryWrites=true&w=majority"
connection = MongoClient(host = uri, connect = False)        
db = connection['app']
col = db.maintenance_qns
col_pdfs = db.report_pdfs
col_html = db.pdfs_html
col_oslas_criteria = db.OSLAS_Criteria
col_OC_Answers = db.OC_Answers

@app.route('/')
def index():
    # maintenance_df = pd.read_csv("maintenance_qns.csv")
    # maintenance_list = maintenance_df.values.tolist()
    # columns = ['qn_no', 'qn', 'qn_type', 'op1', 'img1', 'op2', 'img2', 'op3', 'img3', 'op4', 'img4', 'prev_qn_no', 'sel_op', 'resource', 'glossary', 'add_annex', 'add_input', 'final_qn']
    # for row in maintenance_list:
    #     col.insert_one(dict(zip(columns, row)))
    return render_template('index.html')

@app.route('/maintenance/<prev_qn_no>', methods = ['POST', 'GET'])
def maintenance(prev_qn_no):
    options_html = """"""
    if int(prev_qn_no) == 0:
        sel_op = "op0"
        if 'user-answers' in session:
            session['user-answers'] = []
    else:
        prev_qn_type = list(col.find({"qn_no": int(prev_qn_no)}))[0]['qn_type']
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
    if request.method == "POST":
        if 'user-answers' in session:
            user_answers_list = session['user-answers']
            print("Before:" + str(session['user-answers']))
            for item in user_answers_list:
                if item[0] == prev_qn_no:
                    user_answers_list.remove(item)
            user_answers_list.append([prev_qn_no, sel_op])
            session['user-answers'] = user_answers_list
            session.permanent = True
            print("After:" + str(session['user-answers']))
        else:
            session['user-answers'] = [[prev_qn_no, sel_op]]
            session.permanent = True
            print("Start:" + str(session['user-answers']))
    search_result = list(col.find({"prev_qn_no": int(prev_qn_no), "sel_op": str(sel_op)}))[0]
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
        add_input_html += '<input type="submit" id="add_input_submit" class="btn btn-primary" value="Submit">'
    if int(resource) == 1:
        is_resource = "Present"
        if str(resource) != "No Path Found":
            resource_name = qn.lower().replace("annex ", "annex_")
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
                    elif op3 != "None" and op4 == "None":
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
        for item in user_answers_temp:
            question = list(col.find({"qn_no": int(item[0])}))[0]['qn']
            question_type = "scq"
            if len(item[1].split(", ")) > 1:
                question_type = "mcq"
            if len(item[1].split(", ")) == 1 and (len(item[1].split(", ")[0]) > 3  or item[1].split(", ")[0][:2] != "op"):
                question_type = "mcq"
            if question_type == "scq":
                selected_option = list(col.find({"qn_no": int(item[0])}))[0][str(item[1])]
            elif question_type == "mcq":
                selected_option = str(item[1])
            user_answers_html += f"<span class='question_text'>{str(question)}</span> <span class='selected_option_text'>{str(selected_option)}</span><br>"
        resource_html = annexes_dict[resource_name]
        annex_download_html = """
            <div class="row" id="download-annex-container">
                <h1 id="download-annex-heading">Your Report</h1>
            </div>
            <br>
        """
        annex_download_html += user_answers_html
        annex_download_html += "<br>"
        annex_download_html += download_annexes_dict[resource_name]
        pdf_html_no = random.randrange(100000, 999999)
        col_html.insert_one({
            'no': pdf_html_no,
            'pdf_html': annex_download_html
        })
        session['user-answers'] = []
    return render_template('maintenance.html', current = current_qn_no, question = qn, option_1 = op1, option_2 = op2, option_3 = op3, option_4 = op4, html = options_html, is_add_annex = is_add_annex, add_annex_html = add_annex_html, is_add_input = is_add_input, add_input_html = add_input_html, is_resource = is_resource, resource_html = resource_html, is_glossary = is_glossary, glossary_html = glossary_html, final_qn = int(final_qn), user_responses = user_answers_html, pdf_no = pdf_html_no)

@app.route('/report/<no>.pdf')
def report(no):
    pdf_html = list(col_html.find({"no": int(no)}))[0]['pdf_html']
    page_html = render_template('download_pdf.html', html = pdf_html)
    css = CSS(filename = 'static/css/style.css')
    return render_pdf(HTML(string = page_html))

@app.route("/OSLAS_Criteria", methods=["POST", "GET"])
def OSLAS_Criteria():
    if request.method == "POST":
        Question1 = request.form.getlist('Question1')
        # print(Question1[0])
        Question2 = request.form.getlist('Question2')
        # print(Question2[0])
        Question3 = request.form.getlist('Question3')
        # print(Question3[0])
        Question4 = request.form.getlist('Question4')
        # print(Question4[0])

        if Question1[0] == "yes":
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company (i.e. Pte Ltd)?": Question1[0],
                "Current Date": datetime.datetime.now()
            })
        
        if Question1[0] == "no" and Question2[0] == "yes":
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company (i.e. Pte Ltd)?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Current Date": datetime.datetime.now()
            })

        if Question1[0] == "no" and Question2[0] == "no" and Question3[0] == "yes":
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company (i.e. Pte Ltd)?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "Current Date": datetime.datetime.now()
            })
        
        if Question1[0] == "no" and Question2[0] == "no" and Question3[0] == "no":
            col_OC_Answers.insert_one({
                "Are you enquiring as a representative of a company (i.e. Pte Ltd)?": Question1[0],
                "Are you currently represented by a lawyer?": Question2[0],
                "Have you sought legal advice on this matter before?": Question3[0],
                "What is the nature of your matter": Question4[0]
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
    Civil_a = Civil_a, Civil_a_op1 = Civil_a_op1, Civil_a_op2 = Civil_a_op2,
    Civil_b = Civil_b, Civil_b_op1 = Civil_b_op1, Civil_b_op2 = Civil_b_op2, Civil_b_op3 = Civil_b_op3, Civil_b_op4 = Civil_b_op4, Civil_b_op5 = Civil_b_op5, Civil_b_op6 = Civil_b_op6, Civil_b_op7 = Civil_b_op7, Civil_b_op8 = Civil_b_op8,
    Civil_c_respondent = Civil_c_respondent, Civil_c_respondent_op1 = Civil_c_respondent_op1, Civil_c_respondent_op2 = Civil_c_respondent_op2, Civil_c_respondent_op3 = Civil_c_respondent_op3, Civil_c_respondent_op4 = Civil_c_respondent_op4, Civil_c_respondent_op5 = Civil_c_respondent_op5, Civil_c_respondent_op6 = Civil_c_respondent_op6,
    Civil_c_claimant = Civil_c_claimant, Civil_c_claimant_op1 = Civil_c_claimant_op1, Civil_c_claimant_op2 = Civil_c_claimant_op2, Civil_c_claimant_op3 = Civil_c_claimant_op3, Civil_c_claimant_op4 = Civil_c_claimant_op4, Civil_c_claimant_op5 = Civil_c_claimant_op5,
    Family_i = Family_i, Family_i_op1 = Family_i_op1, Family_i_op2 = Family_i_op2, Family_i_op3 = Family_i_op3, Family_i_op4 = Family_i_op4, Family_ii = Family_ii, Family_ii_prompt = Family_ii_prompt, Family_ii_op1 = Family_ii_op1, Family_ii_op2 = Family_ii_op2, Family_ii_op3 = Family_ii_op3,
    Criminal = Criminal, Criminal_op1 = Criminal_op1, Criminal_op2 = Criminal_op2, Criminal_op3 = Criminal_op3, Criminal_op4 = Criminal_op4, Criminal_op5 = Criminal_op5, Criminal_op6 = Criminal_op6, Criminal_op7 = Criminal_op7)

@app.route('/send/<email>')
def send(email):
    pass

@app.route('/legal')
def legal():
    return render_template('legal.html')

@app.route('/get_advice', methods=['POST'])
def get_advice():
    # Get the legal issue from the POST request data
    legal_issue = request.form['legal_issue']

    # Call the suggest_advice() function to get the top case facts and advice
    top_case_facts, top_advice = suggest_advice(legal_issue)

    # Return the top case facts and advice as a JSON object
    return jsonify(top_case_facts=top_case_facts, top_advice=top_advice)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
@app.route('/send/<no>/<string:email_input>', methods = ['POST'])
def send(no, email_input):
    email = json.loads(email_input)
    msg = MIMEText(f"""
        Hello,

        Thank you for completing the Preliminary Intake Assessment with CJC.

        You can access you report at http://127.0.0.1:5000/report/{no}.

        Best regards,
        Community Justice Centre (CJC)
    """)
    msg['Subject'] = 'Your Report'
    msg['From'] = "jahnvi@ygroo.com"
    msg['To'] = email
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.ehlo()
    smtp_server.login("jahnvi@ygroo.com", "JRSingh@203")
    smtp_server.sendmail("jahnvi@ygroo.com", email, msg.as_string())
    return smtp_server.close()

if __name__ == '__main__':
    app.debug = True
    app.run()
