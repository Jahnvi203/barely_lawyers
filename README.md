About the Documentation
=======================

Purpose
-------

The purpose of this documentation is to help Community Justice Centre (CJC) understand the web app developed by 26\_CL\_BA\_Barely Lawyers\_Justice is Managed as part of IS483 IS/SMT Project Experience at Singapore Management University in collaboration with CJC.

Product Definition
------------------

### **Product 1**

Preliminary Intake Assessment for Maintenance and Divorce for the user as well as the Maintenance Dashboard and the Divorce Dashboard as part of the Admin Dashboard for CJC

### **Product 2**

OSLAS Eligibility Assessment

### **Product 3**

Prescriptive Analysis for prescribe Case Advice for new Cases based on previous Cases data

### **Product 4**

Content Management System to update the questions and their details for the Preliminary Intake Assessment and the OSLAS Eligibility Assessment

Authors
-------

Singh Jahnvi Raj ([jahnvirajs.2020@scis.smu.edu.sg](mailto:jahnvirajs.2020@scis.smu.edu.sg))

Wong Ju Da ([juda.wong.2020@scis.smu.edu.sg](mailto:juda.wong.2020@scis.smu.edu.sg))

Understanding the Code
======================

Architecture
------------

An overview of the constituents of the **fyp** folder is given below:

<img width="466" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/12b7b180-25b4-499c-a52d-3c5deac3c315">

General
-------

In app.py, the logic and function is divided into multiple functions.

Before going into the functions, it is important to note the following:

1.  session

<img width="840" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/7fa45821-d84d-427c-b91d-baaed16f0899">

- The secret key which is mostly used for maintaining sessions is 1E44M1ixSeNGzO3T0dqIoXra7De5B46n
- Currently, the sessions created are set as permanent, however, this is not recommended so in the future, SESSION_PERMANENT should be set to False or a a duration for the permanent session should be added

2.  database connection

<img width="831" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/0535f2bf-4339-47e1-8335-922039befd4a">

- The URI at which the MongoDB database is connected is [mongodb+srv://Jahnvi203:Jahnvi203@cluster0.cn63w2k.mongodb.net/app?retryWrites=true&w=majority](https://www.mongodb.com/docs/atlas/driver-connection/)
- The name of the MongoDB database is **app**
- The different collections in the MongoDB database are in lines 38 to 48

Product 1
---------

### For Preliminary Intake Assessment (for users)

A description of each function is given below:

<img width="467" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/538f323c-03a7-4c30-b922-2a3e594badac">

### For Admin Dashboard (for CJC)

Before going into the functions, it is important that you have access to the Admin Dashboard for Preliminary Intake Assessment which consists of 2 dashboards:

1.  PIA Maintenance Dashboard
2.  PIA Divorce Dashboard

These dashboards are hosted with MongoDB.

A description of each function is given below:

<img width="468" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/e49e2b5c-a91e-4199-97c0-85bf68db9e28">

Product 2
---------

### For OSLAS Eligibility Questionnaire (for users)

A description of each function is given below:

<img width="467" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/3ee688c2-caee-4f24-a334-c8ee0689efa4">

### For OSLAS Eligibility Questionnaire (for CJC)

A description of each function is given below:

<img width="467" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/61fcd9a4-1242-4aed-a4c9-54fbe0eec789">

Product 3
---------

<img width="455" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/502b1498-e027-4c9c-8c2a-48034742679c"><br />

<img width="455" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/dcd4c5be-ce4d-482a-b15e-592316be3961"><br />

<img width="455" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/6b65ef11-1b31-4f0e-b40b-94e52695dee0"><br />

<img width="466" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/8d24da41-b4c6-4d99-835c-7134f5aa6b72"><br />

<img width="467" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/f6017b87-4429-417b-b397-cc2eeba9dd71"><br />

<img width="467" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/c9aa08d8-d665-465e-99d9-ebd573944f9f">

Product 4
---------

A description of each function is given below:

<img width="467" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/a1b2e8db-f625-4371-aa7b-548981e0b372"><br />

<img width="466" alt="image" src="https://github.com/Jahnvi203/barely_lawyers/assets/85999744/131be0f5-4c8e-45ff-9062-e7eb221f24b0">
