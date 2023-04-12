import unittest
from unittest.mock import MagicMock
from suggest_advice import suggest_advice
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class TestSuggestAdvice(unittest.TestCase):
    
    def test_suggest_advice(self):
        # Define the input to the function
        new_case_fact = "Applicant wants to know how much maintenance to give"
        threshold = 0.1
        
        # Call the function and get the output
        top_case_facts, top_advice = suggest_advice(new_case_fact, threshold)
        
        # Define the expected output
        expected_case_facts = ["Recently, ex husband's contract renewed would going back overseas. Ex husband wanted apply total exemption maintenance. paid $500 month September. wants extract order, unable to. contacted ex husband since went back overseas. Ex husband agree giving sole custody child applicant.", 'Facts: client says agreed upon mediation different set court order. agreed joint care control child live claiming maintenance. wants know would happen give maintenance.', 'wants know even husband left overseas']
        expected_advice = ['Even if the ex husband does not extract the order, the applicant would still be able to do so. Even after the 14 days, she would still be able to extract the order. Make the according amendment and the applicant would still be able to extract.\r\nThe applicant would be able to apply for sole custody and also remove the clause which states that the applicant has to make consent in regards to bringing her children overseas. ', "First, the client needs to ask legal aid to send her a copy of the consent order (1st Feb) so she has a record of it.\r\n\r\nIf the client has previously gone to legal aid for help, she can go back to them and tell them that a summons was issued against her for the same case to ask for help. It is unlikely that they will conduct another means test for her since she already has a case open with them. All she has to mention to legal aid is that her understanding of the mediation was that in exchange for letting the child stay with the husband, she will not have to pay a maintenance. However, now there is a court order that she has to pay a maintenance. She should also send them the letter from her previous lawyers sent a letter to the other side's lawyers enquiring why they started a suit for maintenance. \r\n\r\nShe is advised to send a separate email to the judge regarding the agreement on 1st February. She was advised to do this by the Family Justice Courts.\r\n\r\nThe court told her to pay $150 a month. There is a possibility that what is recorded in a consent order is that parties are at liberty to apply for maintenance. \r\n\r\nThe client is advised to pay the maintenance as the court has the power to deduct the money from the bank account directly or even send her to prison for contempt of court.", 'Applicant was advised to hire an overseas Lawyer to serve the summons on A/P as our court cannot serve documents out of Singapore due to jurisdiction reasons.  Applicant is also unable to serve the summons on her own and would require a lawyer.\r\n\r\nApplicant was also advised to hire a lawyer to make an application for substituted service. If  applicant is unable to afford legal counsel, she was asked to seek aid from the legal aid bureau. \r\n\r\nApplicant was also advised to hire her own private lawyer if she earns beyond the expected amount to qualify for legal aid.']

        
        # Compare the actual and expected outputs
        self.assertEqual(top_case_facts, expected_case_facts)
        self.assertEqual(top_advice, expected_advice)


if __name__ == "__main__": 
    unittest.main()
