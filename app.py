from flask import Flask, render_template, request, redirect, url_for, session, make_response
from pymongo import MongoClient
from resources.add_annexes import add_annexes_dict
from resources.add_inputs import add_inputs_dict
from resources.annexes import annexes_dict
from resources.glossaries import glossaries_dict
from resources.download_annexes import download_annexes_dict
from xhtml2pdf import pisa
import pdfkit
import wkhtmltopdf
import random

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
                            <div class="col-lg-3">
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
                            <div class="col-lg-3">
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
                            <div class="col-lg-3">
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
                            <div class="col-lg-3">
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
                                <div class="col-md-4">
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
                                <div class="col-md-4">
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
                                <div class="col-md-4">
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
                                <div class="col-sm-6">
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
                                <div class="col-sm-6">
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
                                <div class="col-lg-3">
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
                                <div class="col-lg-3">
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
                                <div class="col-lg-3">
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
                                <div class="col-lg-3">
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
                                <div class="col-md-4">
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
                                <div class="col-md-4">
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
                                <div class="col-md-4">
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
                                <div class="col-sm-6">
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
                                <div class="col-sm-6">
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

@app.route('/report/<no>')
def report(no):
    path_wkhtmltopdf = f'C:\Program Files\{"wkhtmltopdf"}\{"bin"}\{"wkhtmltopdf"}.exe'
    config_wkhtmltopdf = pdfkit.configuration(wkhtmltopdf = path_wkhtmltopdf)
    pdf_html = list(col_html.find({"no": int(no)}))[0]['pdf_html']
    rendered = render_template('download_pdf.html', html = pdf_html)
    pdf = pdfkit.from_string(rendered, False, configuration = config_wkhtmltopdf, css = "static\css\style.css", options = {"enable-local-file-access": ""})
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=report.pdf'
    return response

@app.route("/criteria")
def OSLAS_criteria():
    return render_template('OSLAS_criteria.html')

def civil():
    return render_template('civil.html')

def criminal():
    return render_template('criminal.html')

def family():
    return render_template('family.html')

@app.route('/send/<email>')
def send(email):
    pass
    

if __name__ == '__main__':
    app.run(debug=True)