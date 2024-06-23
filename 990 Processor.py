import requests
from bs4 import BeautifulSoup
import openpyxl
import time
import datetime 
import re
from tabulate import tabulate
import xml.etree.ElementTree as ET
import os
import tkinter as tk
from tkinter import messagebox


def fetch_html_content(url):
    try:
        # Make the request with the default user-agent
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.content
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request exception occurred: {e}")
        return None

    
def check_keywords(*investment_lists):
    # Define the list of keywords
    keywords = [
        "Venture", "capital", "Listed", "Unlisted", "Un-listed", "Quoted", "Unquoted", "Un-quoted",
        "Private debt", "Real estate", "Real-estate", "Property", "REIT", "Hedge fund", "Absolute return",
        "Infrastructure", "Real asset", "Natural resource", "Timber", "Agriculture", "Energy", "Farmland",
        "Oil", "Gas", "Metal", "Gold", "Silver", "Real Asset", "Natural Resources", "Real Estate",
        "Restructuring", "Turnaround", "secondary buyer", "Sovereign Wealth Fund", "Timber", "Venture Capital",
        "Early Stage", "Later Stage", "Buyout", "Co-Investments", "Co Investment", "Collateralized loan obligation",
        "CLO", "Collateralized loan", "credit special situation", "Venture Debt", "Metal", "mining", "Mezzanine",
        "Captive", "Oil and Gas", "Oil", "Gas", "Growth Expansion", "Project financing", "Private Equity",
        "Funds of Funds", "FOF", "Hedge Fund", "Infrastructure", "Greenfield", "Core", "opportunistic",
        "value add", "Diversified Private Equity", "Debt", "Direct Lending", "Distressed Debt", "Agriculture",
        "Bridge Financing", "Crowd Source", "Private Debt", "buyouts", "hedge", "Endowment", "real assets",
        "alternatives", "public equities", "funds of funds", "fixed income", "Mutual Fund", "Private Investment Fund"
    ]
    
    matched_keywords = set()

    # Iterate through each investment list
    for investments in investment_lists:
        # Iterate through the investments list and check for keywords
        for investment in investments:
            description = investment[0]
            found_keywords = [keyword for keyword in keywords if keyword.lower() in description.lower()]
            if found_keywords:
                matched_keywords.update(found_keywords)

    if matched_keywords:
        return ", ".join(sorted(matched_keywords))  # Return unique keywords as a single line, sorted for consistency
    else:
        return "No keywords matched"


state_abbreviations = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming"
    }
#**********************************************************___990___***************************************************************************************
#**********************************************************start of 990*************************************************************************************** 
# Function to extract data from the webpage
def extract_data(soup):
    #response = requests.get(url)
    #file.write(response.content)
    #soup = BeautifulSoup(response.content, 'html.parser')

    organization_name, address, suite, city, state, zipcode, ein, phone, preparer_firm_name,AoD_formatted, AoD_row = organization_details(soup)

    # Extracting website address
    website_span = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990[1]/WebsiteAddressTxt[1]')
    website = website_span.text.strip() if website_span else "Website address not found"

    
    # Find all <td> elements with class 'styTableCellText'
    td_elements = soup.find_all('td', class_='styTableCellText')

    # Initialize lists to store person names and titles
    person_names = []
    titles = []
    # Iterate through each <td> element
    for td in td_elements:
        # Find <span> elements containing person name and title
        person_span = td.find('span', id=lambda x: x and x.endswith('/PersonNm[1]'))
        title_span = td.find('span', id=lambda x: x and x.endswith('/TitleTxt[1]'))

        # Extract person name and title if found
        if person_span and title_span:
            person_name = person_span.text.strip()
            title = title_span.text.strip()
            
            # Append extracted data to lists
            person_names.append(person_name)
            titles.append(title)
    
    return organization_name, address, suite, city, state, zipcode, ein, phone, website, preparer_firm_name, person_names, titles,AoD_formatted, AoD_row

# Function to extract and calculate AUM data
def extract_aum_data(soup):
    #soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize variables for AUM categories
    alternatives = 0
    private_equity = 0
    real_estate = 0
    spl_oppm = 0
    hedge = 0
    equity = 0
    fixed_income = 0
    cash = 0
    not_in_allocation = 0

    # Extract data for each AUM category
    cash += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990[1]/CashNonInterestBearingGrp[1]/EOYAmt[1]')
    cash += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990[1]/SavingsAndTempCashInvstGrp[1]/EOYAmt[1]')

    not_in_allocation += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990[1]/InvestmentsPubTradedSecGrp[1]/EOYAmt[1]')
    not_in_allocation += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990[1]/InvestmentsOtherSecuritiesGrp[1]/EOYAmt[1]')
    not_in_allocation += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990[1]/InvestmentsProgramRelatedGrp[1]/EOYAmt[1]')

    # Calculate total AUM
    total_aum = alternatives + private_equity + real_estate + spl_oppm + hedge + equity + fixed_income + cash + not_in_allocation
    
    return total_aum, alternatives , private_equity , real_estate, spl_oppm , hedge, equity, fixed_income, cash, not_in_allocation
        
# Helper function to extract value from HTML content and format in millions
"""
def extract_value(soup, element_id):
    element = soup.find('span', id=element_id)
    if element:
        value_str = element.text.strip().replace(',', '')
        value = float(value_str) / 10**6  # Convert to millions
        return round(value, 6)  # Limit to 6 digits after the decimal point
    else:
        return 0"""

def extract_value(soup, element_id):
    element = soup.find('span', id=element_id)
    if element:
        value_str = element.text.strip().replace(',', '')
        try:
            value = float(value_str)
            if value < 0:
                return 0  # Return 0 if the value is negative
            value_in_millions = value / 10**6  # Convert to millions
            return round(value_in_millions, 6)  # Limit to 6 digits after the decimal point
        except ValueError:
            return 0  # Return 0 if the value is not a valid number
    else:
        return 0  # Return 0 if the element is not found

def extract_checked_states(soup):
    checkboxes = {
        "AddressChangeInd": "Address change",
        "NameChangeInd": "Name change",
        "InitialReturnInd": "Initial return",
        "TerminatedReturnInd": "Final return/terminated",
        "AmendedReturnInd": "Amended return",
        "ApplicationPendingInd": "Application pending"
    }
    
    checked_states = []
    for key, value in checkboxes.items():
        # Find checkboxes by checking for the id containing the key string
        checkbox = soup.find('input', {'id': lambda x: x and key in x})
        if checkbox:
            if 'checked' in checkbox.attrs or checkbox.get('checked') == 'checked':
                checked_states.append(value)
    
    return checked_states

def extract_contractor_data(soup):
    contractor_data = []

    rows = soup.find_all('tr')
    for row in rows:
        try:
            name = row.find('span', id=lambda x: x and x.endswith('/BusinessNameLine1Txt[1]')).text.strip()
            #address = row.find('span', id=lambda x: x and x.endswith('/AddressLine1Txt[1]')).text.strip()
            #address_line2 = row.find('span', id=lambda x: x and x.endswith('/AddressLine2Txt[1]'))
            #if address_line2:
             #   address += f", {address_line2.text.strip()}"
            city = row.find('span', id=lambda x: x and x.endswith('/CityNm[1]')).text.strip()
            state = row.find('span', id=lambda x: x and x.endswith('/StateAbbreviationCd[1]')).text.strip()
            #zipcode = row.find('span', id=lambda x: x and x.endswith('/ZIPCd[1]')).text.strip()
            services = row.find('span', id=lambda x: x and x.endswith('/ServicesDesc[1]')).text.strip()
            compensation = row.find('span', id=lambda x: x and x.endswith('/CompensationAmt[1]')).text.strip()
            
            contractor_data.append([name, city, state, services, compensation])
        except AttributeError:
            continue
    
    return contractor_data
#**********************************************************End of 990*************************************************************************************** 

#**********************************************************Start of Dchedule D*************************************************************************************** 
def extract_endowment_funds_value(url2):
    html_content = fetch_html_content(url2)
    if html_content is None:
        endowment_value = 0
    else:
        soup = BeautifulSoup(html_content, 'html.parser')
        endowment_value = 0
        endowment_value_element = soup.find('span', id=lambda x: x and x.endswith('/EndYearBalanceAmt[1]'))
        if endowment_value_element:
            endowment_value_text = endowment_value_element.text.strip().replace(',', '')
            endowment_value = float(endowment_value_text)
        return endowment_value

def extraction_990_data_from_xml(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        xml_data = response.text
        if not xml_data.strip():  # Check if the XML data is empty
            raise Exception("XML data is empty. Exiting.")
        root = ET.fromstring(xml_data)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to retrieve XML data: {e}")
    except ET.ParseError as e:
        # Raise an exception for the specific error
        raise Exception(f"Failed to parse XML data: {e}")

    namespaces = {'irs': 'http://www.irs.gov/efile'}  # Define the namespaces

    investments = []
    Other_Securities = root.findall('.//irs:OtherSecuritiesGrp', namespaces)
    if not Other_Securities:
        investments = []
    
    for Other_Securitie in Other_Securities:
        Other_Securitie_Desc = Other_Securitie.find('.//irs:Desc', namespaces)
        Other_Securitie_BookValueAmt = Other_Securitie.find('irs:BookValueAmt', namespaces)
        if Other_Securitie_Desc is not None and Other_Securitie_Desc is not None:
            investments.append([Other_Securitie_Desc.text, f"{int(Other_Securitie_BookValueAmt.text):,}"])

    if not investments:
        investments = []
    
    Program_Related_investments = []
    Program_Relateds = root.findall('.//irs:InvstProgramRelatedOrgGrp', namespaces)
    if not Program_Relateds:
       Program_Related_investments = []

    for Program_Related in Program_Relateds:
        Program_Related_Desc = Program_Related.find('.//irs:Desc', namespaces)
        Program_Related_BookValueAmt = Program_Related.find('irs:BookValueAmt', namespaces)
        if Program_Related_Desc is not None and Program_Related_BookValueAmt is not None:
            Program_Related_investments.append([Program_Related_Desc.text, f"{int(Program_Related_BookValueAmt.text):,}"])

    if not Program_Related_investments:
        Program_Related_investments = []

    Other_Assets_ = []
    Other_Assets = root.findall('.//irs:OtherAssetsOrgGrp', namespaces)
    if not Other_Assets:
        Other_Assets_ = []
    
    for Other_Asset in Other_Assets:
        Other_Asset_Desc = Other_Asset.find('.//irs:Desc', namespaces)
        Other_Asset_BookValueAmt = Other_Asset.find('irs:BookValueAmt', namespaces)
        if Other_Asset_Desc is not None and Other_Asset_BookValueAmt is not None:
            Other_Assets_.append([Other_Asset_Desc.text, f"{int(Other_Asset_BookValueAmt.text):,}"])

    if not Other_Assets_:
        Other_Assets_ = []
    
    return investments, Program_Related_investments, Other_Assets_

#**********************************************************End of Sdchedule D*************************************************************************************** 
#**********************************************************___990___*************************************************************************************** 

#**********************************************************___PF___*************************************************************************************** 
def extract_table_data_pf(table, col1_index, col2_index):
    person_names = []
    titles =  []
    for row in table.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) > max(col1_index, col2_index):
            name = columns[col1_index].get_text(strip=True)
            title_or_service = columns[col2_index].get_text(strip=True)
            # Clean title_or_service to remove any numbers (hours per week)
            title_or_service = re.sub(r'\s*\d+\.\d+\s*', '', title_or_service).strip()
            person_names.append(name)
            titles.append(title_or_service)    
            
    return person_names, titles


def organization_details(soup):
        # Extracting organization name
    organization_name_elem = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/Filer[1]/BusinessName[1]/BusinessNameLine1Txt[1]')
    organization_name = organization_name_elem.text.strip() if organization_name_elem else "Organization name not found"

    # Extracting address
    address_span = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/Filer[1]/USAddress[1]/AddressLine1Txt[1]')
    address = address_span.text.strip() if address_span else "Address not found"

    address_suite = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/Filer[1]/USAddress[1]/AddressLine2Txt[1]')
    suite = address_suite.text.strip() if address_suite else "Address not found"

    # Extracting city
    city_elem = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/Filer[1]/USAddress[1]/CityNm[1]')
    city = city_elem.text.strip() if city_elem else "City not found"

    # Extracting state
    state_elem = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/Filer[1]/USAddress[1]/StateAbbreviationCd[1]')
    state_abbreviation = state_elem.text.strip() if state_elem else "State not found"
    state = state_abbreviations.get(state_abbreviation, state_abbreviation)

    # Extracting ZIP code
    zipcode_elem = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/Filer[1]/USAddress[1]/ZIPCd[1]')
    zipcode = zipcode_elem.text.strip() if zipcode_elem else "ZIP code not found"

    # Extracting EIN
    ein_span = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/Filer[1]/EIN[1]')
    ein = ein_span.text.strip() if ein_span else "EIN not found"

    # Extracting telephone number
    phone_span = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/Filer[1]/PhoneNum[1]')
    phone = phone_span.text.strip() if phone_span else "Phone number not found"

    # Extracting as of date and formatting it
    as_of_date_span = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/TaxPeriodEndDt[1]')
    AoD_row = as_of_date_span.text.strip() if as_of_date_span else "As of date not found"
    try:
        AoD_formatted = datetime.datetime.strptime(AoD_row, '%m-%d-%Y').strftime('%B %d, %Y')
    except ValueError:
        AoD_formatted = AoD_row


    # Extracting preparer firm name
    preparer_span = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/ReturnHeader[1]/PreparerFirmGrp[1]/PreparerFirmName[1]/BusinessNameLine1Txt[1]')
    preparer_firm_name = preparer_span.text.strip() if preparer_span else "Preparer firm name not found"
    
    return organization_name, address, suite, city, state, zipcode, ein, phone, preparer_firm_name,AoD_formatted, AoD_row

def extract_data_pf(soup):
    #response = requests.get(url)
    #file.write(response.content)
    #soup = BeautifulSoup(response.content, 'html.parser')

    organization_name, address, suite, city, state, zipcode, ein, phone, preparer_firm_name,AoD_formatted, AoD_row = organization_details(soup)

    # Extracting website address
    website_span = soup.find('span', id='/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990PF[1]/StatementsRegardingActyGrp[1]/WebsiteAddressTxt[1]')
    website = website_span.text.strip() if website_span else "Website address not found"

    person_names = []
    person_titles = []
    # Find and extract Table 1
    part_vii = soup.find('div', string="Part VII")
    if part_vii is None:
        print("Div with string 'Part VII' not found.")
    else:
        table = part_vii.find_next('table')
        if table is None:
            print("Table following 'Part VII' not found.")
        else:
            person_names, person_titles = extract_table_data_pf(table, 0, 1)
    
   # part_vii = soup.find('div', string="Part VII").find_next('table')
    #person_names, person_titles  = extract_table_data_pf(part_vii, 0, 1)
    
    return organization_name, address, suite, city, state, zipcode, ein, phone, website, preparer_firm_name, person_names, person_titles,AoD_formatted, AoD_row

# Function to extract and calculate AUM data
def extract_aum_data_pf(soup):
    #soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize variables for AUM categories
    alternatives = 0
    private_equity = 0
    real_estate = 0
    spl_oppm = 0
    hedge = 0
    equity = 0
    fixed_income = 0
    cash = 0
    not_in_allocation = 0

    # Extract data for each AUM category
    cash += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990PF[1]/Form990PFBalanceSheetsGrp[1]/CashEOYFMVAmt[1]')
    cash += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990PF[1]/Form990PFBalanceSheetsGrp[1]/SavAndTempCashInvstEOYFMVAmt[1]')

    fixed_income += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990PF[1]/Form990PFBalanceSheetsGrp[1]/USGovtObligationsEOYFMVAmt[1]')
    equity += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990PF[1]/Form990PFBalanceSheetsGrp[1]/CorporateStockEOYFMVAmt[1]')
    fixed_income += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990PF[1]/Form990PFBalanceSheetsGrp[1]/CorporateBondsEOYFMVAmt[1]')
    alternatives += extract_value(soup, '/AppData/SubmissionHeaderAndDocument/SubmissionDocument/IRS990PF[1]/Form990PFBalanceSheetsGrp[1]/OtherInvestmentsEOYFMVAmt[1]')

    # Calculate total AUM
    total_aum = alternatives + private_equity + real_estate + spl_oppm + hedge + equity + fixed_income + cash + not_in_allocation
    
    return total_aum, alternatives , private_equity , real_estate, spl_oppm , hedge, equity, fixed_income, cash, not_in_allocation
    
def extract_endowment_funds_value_pf(soup):
    endowment_value = 0
    endowment_value_element = soup.find('span', id=lambda x: x and x.endswith('/RetainedEarningEOYAmt[1]'))
    if endowment_value_element:
        endowment_value_text = endowment_value_element.text.strip().replace(',', '')
        endowment_value = float(endowment_value_text)
    return endowment_value


def extract_checked_states_pf(soup):
    checkboxes = {
        "AddressChangeInd": "Address change",
        "NameChangeInd": "Name change",
        "InitialReturnInd": "Initial return",
        "FinalReturnInd": "Final return",
        "AmendedReturnInd": "Amended return"
    }
    
    checked_states = []
    for key, value in checkboxes.items():
        # Find checkboxes by checking for the id containing the key string
        checkboxes_found = soup.find_all('input', {'id': lambda x: x and key in x})
        for checkbox in checkboxes_found:
            if 'checked' in checkbox.attrs or checkbox.get('checked') == 'checked':
                checked_states.append(value)
    
    return checked_states


def extract_investments_pf(url2):
    html_content = fetch_html_content(url2)
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    investments = []
    try:
        table = soup.find('table', id='InvestmentsOtherSchedule2Tbl')
        rows = table.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            cells = row.find_all('td')
            if cells:
                category = cells[0].text.strip()
                EOYFMVAmt = cells[3].text.strip()
                investments.append([category, EOYFMVAmt])
    except AttributeError:
        pass
    return investments

def extract_names_and_titles__business_names_and_services_from_xml(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        xml_data = response.text
        if not xml_data.strip():  # Check if the XML data is empty
            raise Exception("XML data is empty. Exiting.")
        root = ET.fromstring(xml_data)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to retrieve XML data: {e}")
    except ET.ParseError as e:
        # Raise an exception for the specific error
        raise Exception(f"Failed to parse XML data: {e}")

    namespaces = {'irs': 'http://www.irs.gov/efile'}  # Define the namespaces

    employee_data = []

    employee_elements = root.findall('.//irs:CompensationHighestPaidEmplGrp', namespaces)
    if not employee_elements:
        #raise Exception("No 'CompensationHighestPaidEmplGrp' elements found in the XML. Exiting.")
        employee_data = [] 

    for employee in employee_elements:
        name_elem = employee.find('irs:PersonNm', namespaces)
        title_elem = employee.find('irs:TitleTxt', namespaces)
        if name_elem is not None and title_elem is not None:
            employee_data.append([name_elem.text, title_elem.text])

    if not employee_data:
        #print("No valid entries found. Please check the structure of your XML data.")
        employee_data = []    
    
    business_names_and_services =[]
    
    contractor_business = root.findall('.//irs:CompensationOfHghstPdCntrctGrp', namespaces)
    if not contractor_business:
        #raise Exception("No 'CompensationOfHghstPdCntrctGrp' elements found in the XML. Exiting.")
        business_names_and_services = []
    
    for contractor in contractor_business:
        business_name_elem = contractor.find('.//irs:BusinessNameLine1Txt', namespaces)
        service_type_elem = contractor.find('irs:ServiceTypeTxt', namespaces)
        if business_name_elem is not None and service_type_elem is not None:
            business_names_and_services.append([business_name_elem.text, service_type_elem.text])

    if not business_names_and_services:
        #print("No entries found. Please check the structure of your XML data.")
        business_names_and_services = []
        
    
    return employee_data, business_names_and_services

#**********************************************************___PF___*************************************************************************************** 
#directory = "C:\Users\mcontra\OneDrive - MORNINGSTAR INC\990"
# Create the directory if it doesn't exist
#os.makedirs(directory, exist_ok=True)

def generate_urls(unique_id):
    base_url = "https://projects.propublica.org/nonprofits/full_text/"
    url1 = f"{base_url}{unique_id}/IRS990"
    url2 = f"{base_url}{unique_id}/IRS990ScheduleD"
    url3 = f"https://projects.propublica.org/nonprofits/download-xml?object_id={unique_id}"
    return url1, url2, url3
def process_990(unique_id):
    #unique_ids = list_990
    #for unique_id in unique_ids:
        url1, url2,url3 = generate_urls(unique_id)
        html_content = fetch_html_content(url1)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extracting data from the webpage 990
        organization_name, address, suite, city, state_, zipcode, ein, phone, website, preparer_firm_name, person_names, person_titles, AoD_formatted, AoD_row = extract_data(soup)
        total_aum, alternatives , private_equity , real_estate, spl_oppm , hedge, equity, fixed_income, cash, not_in_allocation = extract_aum_data(soup)

        # Extract checked states 990
        checked_states = extract_checked_states(soup)
        contractor_data = extract_contractor_data(soup)

        #Sdchedule D        
        endowment_funds = extract_endowment_funds_value(url2)

        try:
            investments_data, program_related_investments, other_assets = extraction_990_data_from_xml(url3)
        except Exception as e:
            investments_data = []
            program_related_investments = [] 
            other_assets = []

        matched_keywords = check_keywords(investments_data, program_related_investments, other_assets)


        # Construct the file name
        file_name = f"{organization_name} {ein} {AoD_row}.txt"
        #file_path = os.path.join(directory, file_name)
        with open(file_name, "w") as file:
            #990
            file.write("990:  https://projects.propublica.org/nonprofits/organizations/{str(ein).replace('-', '')}/{unique_id_pf}/full\n")
            # Writing checked states to the file
            if checked_states:
                file.write("States:\n")
                for state in checked_states:
                    file.write(f"- {state}\n")
                file.write("\n")
            else:
                file.write("States: NA\n")


            # Writing extracted as of date to the file
            file.write("As of Date: {} OR {}\n\n".format(AoD_row, AoD_formatted))
            
            # Writing extracted data to the file
            file.write("Organization Name: {}\n".format(organization_name))
            file.write("Address: {}\n".format(address))
            file.write("Room/suite: {}\n".format(suite))
            file.write("City: {}\n".format(city))
            file.write("State: {}\n".format(state_))
            file.write("ZIP Code: {}\n".format(zipcode))

            file.write("Employer Identification Number (EIN): {}\n".format(ein))
            file.write("Telephone Number: {}\n".format(phone))
            file.write("Website Address: {}\n".format(website))
            file.write("Paid Preparer Use Only: {}\n\n".format(preparer_firm_name))
            
            # Writing extracted person data to the file
            for i, (person_name, person_title) in enumerate(zip(person_names, person_titles), start=1):
                file.write("Person {}:\n".format(i))
                file.write("Name: {}\n".format(person_name))
                file.write("Title: {}\n\n".format(person_title))

            # Writing AUM data to the file
            file.write("AUM Data:\n")
            file.write("Alternatives: {:.6f}\n".format(alternatives))
            file.write("Private Equity: {:.6f}\n".format(private_equity))
            file.write("Real Estate: {:.6f}\n".format(real_estate))
            file.write("Spl Oppm: {:.6f}\n".format(spl_oppm))
            file.write("Hedge: {:.6f}\n".format(hedge))
            file.write("Equity: {:.6f}\n".format(equity))
            file.write("Fixed Income: {:.6f}\n".format(fixed_income))
            file.write("Cash: {:.6f}\n".format(cash))
            file.write("Not In Allocation: {:.6f}\n".format(not_in_allocation))
            file.write("Total AUM: {:.6f}\n\n".format(total_aum))
            file.write("Total AUM: {:.2f} billion\n\n".format(total_aum / 1000))

            #Endowment
            if endowment_funds:
                endowment_value_in_millions = endowment_funds / 1_000_000
                endowment_value_in_billions = endowment_funds / 1_000_000_000
                file.write("\nEndowment Funds: {:.6f} millions\n".format(endowment_value_in_millions))
                file.write("Endowment Funds: {:.2f} billions\n\n".format(endowment_value_in_billions))
            else:
                file.write("\nNo Endowment Funds found.\n\n")

            # Print the matched keywords or "No keywords matched"
            file.write(matched_keywords)
    

            #Independent Contractors
            if contractor_data:
                headers = ["Name", "City", "State", "Services", "Compensation"]
                table = tabulate(contractor_data, headers, tablefmt="grid")
                file.write("\nIndependent Contractors:\n\n")
                file.write(table)
            else:
                file.write("\nNo Independent Contractors found.\n\n")

            #Sdchedule D        
            if investments_data:
                headers = ["Description of security or category", "Book Value"]
                table = tabulate(investments_data, headers, tablefmt="grid")
                file.write("\nInvestments - Other Securities:\n")
                file.write(table + "\n")
            else:
                file.write("\nNo Investments - Other Securities found.\n")
                 
            if program_related_investments:
                headers = ["Description of investment", "Book Value", "Method of Valuation"]
                table = tabulate(program_related_investments, headers, tablefmt="grid")
                file.write("\nInvestments - Program Related:\n")
                file.write(table)
                file.write("\n\n")
            else:
                file.write("\nNo Program Related Investments found.\n\n")      
            

            if other_assets:
                headers = ["Description", "Book Value"]
                table = tabulate(other_assets, headers, tablefmt="grid")
                file.write("\nOther Assets:\n")
                file.write(table)
                file.write("\n\n")
            else:
                file.write("\nNo Other Assets found.\n\n")
        os.system(f'notepad.exe {file_name}')


def generate_urls_pf(unique_id):
    base_url = "https://projects.propublica.org/nonprofits/full_text/"
    url1 = f"{base_url}{unique_id}/IRS990PF"
    url2 = f"{base_url}{unique_id}/InvestmentsOtherSchedule2"
    url3 = f"https://projects.propublica.org/nonprofits/download-xml?object_id={unique_id}"
    
    return url1, url2, url3
def process_990_pf(unique_id_pf):
    #unique_ids_pf = list_990_pf
    #for unique_id_pf in unique_ids_pf:
            url1, url2, url3 = generate_urls_pf(unique_id_pf)
            html_content = fetch_html_content(url1)
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extracting data from the webpage 990
            organization_name, address, suite, city, state_, zipcode, ein, phone, website, preparer_firm_name, person_names, person_titles, AoD_formatted, AoD_row = extract_data_pf(soup)
            total_aum, alternatives , private_equity , real_estate, spl_oppm , hedge, equity, fixed_income, cash, not_in_allocation = extract_aum_data_pf(soup)
            endowment_funds = extract_endowment_funds_value_pf(soup)
            checked_states = extract_checked_states_pf(soup)

            try:
                employee_data,business_names_and_services = extract_names_and_titles__business_names_and_services_from_xml(url3)
            except Exception as e:
                employee_data = []
                business_names_and_services = []
               # business_names_and_services =[]

            #Sdchedule 
            investments_data = extract_investments_pf(url2)

            matched_keywords = check_keywords(investments_data)

            # Construct the file name
            file_name = f"{organization_name} {ein} {AoD_row}.txt"
            #file_path = os.path.join(directory, file_name)
            with open(file_name, "w") as file:
                #990pf
                file.write(f"990-PF:  https://projects.propublica.org/nonprofits/organizations/{str(ein).replace('-', '')}/{unique_id_pf}/full\n")

                #Writing checked states to the file
                if checked_states:
                    file.write("\nStates:\n")
                    for state in checked_states:
                        file.write("- {}\n".format(state))
                    file.write("\n")
                else:
                    file.write("States:NA\n")

                # Writing extracted as of date to the file
                file.write("As of Date: {} OR {}\n\n".format(AoD_row, AoD_formatted))
                
                # Writing extracted data to the file
                file.write("Organization Name: {}\n".format(organization_name))
                file.write("Address: {}\n".format(address))
                file.write("Room/suite: {}\n".format(suite))
                file.write("City: {}\n".format(city))
                file.write("State: {}\n".format(state_))
                file.write("ZIP Code: {}\n".format(zipcode))

                file.write("Employer Identification Number (EIN): {}\n".format(ein))
                file.write("Telephone Number: {}\n".format(phone))
                file.write("Website Address: {}\n".format(website))

                file.write("Paid Preparer Use Only: {}\n\n".format(preparer_firm_name))
                
                # Writing extracted person data to the file
                for i, (person_name, person_title) in enumerate(zip(person_names, person_titles), start=1):
                    file.write("Person {}:\n".format(i))
                    file.write("Name: {}\n".format(person_name))
                    file.write("Title: {}\n\n".format(person_title))
                
                # Writing AUM data to the file
                file.write("AUM Data:\n")
                file.write("Alternatives: {:.6f}\n".format(alternatives))
                file.write("Private Equity: {:.6f}\n".format(private_equity))
                file.write("Real Estate: {:.6f}\n".format(real_estate))
                file.write("Spl Oppm: {:.6f}\n".format(spl_oppm))
                file.write("Hedge: {:.6f}\n".format(hedge))
                file.write("Equity: {:.6f}\n".format(equity))
                file.write("Fixed Income: {:.6f}\n".format(fixed_income))
                file.write("Cash: {:.6f}\n".format(cash))
                file.write("Not In Allocation: {:.6f}\n".format(not_in_allocation))
                file.write("Total AUM: {:.6f}\n\n".format(total_aum))
                file.write("Total AUM: {:.2f} billion\n\n".format(total_aum / 1000))
                file.write("Note: Investments—other is taken in alternatives please check the table and update accordingly")

                
                
                #Endowment
                if endowment_funds:
                    endowment_value_in_millions = endowment_funds / 1_000_000
                    endowment_value_in_billions = endowment_funds / 1_000_000_000
                    file.write("\nEndowment Funds: {:.6f} millions\n".format(endowment_value_in_millions))
                    file.write("Endowment Funds: {:.2f} billions\n\n".format(endowment_value_in_billions))
                else:
                    file.write("\nNo Endowment Funds found.\n\n")


                # Print the matched keywords or "No keywords matched"
                file.write(matched_keywords)
                
                #Sdchedule D        
                if investments_data:
                    headers = ["Category/ Item", "End of Year Fair Market Value"]
                    table = tabulate(investments_data, headers, tablefmt="grid")
                    file.write("\nInvestments - Other Securities:\n")
                    file.write(table + "\n")
                else:
                    file.write("\nNo Investments - Other Securities found.\n")

                # Print employee names and titles in tabular form
                if employee_data:
                    file.write("Employee Names and Titles:\n")
                    headers = ["Name", "Title"]
                    table = tabulate(employee_data, headers, tablefmt="grid")
                    file.write(table + "\n")
                else:
                    file.write("\nNo employee data found.\n")

                # Print business names and services in tabular form
                if business_names_and_services:
                    file.write("\nBusiness Names and Services:\n")
                    headers = ["Business Name", "Service Type"]
                    table = tabulate(business_names_and_services, headers, tablefmt="grid")
                    #contractor_data = list(zip(business_names, services))
                    file.write(table + "\n")
                else:
                    file.write("\nNo contractor data found.\n")
            os.system(f'notepad.exe {file_name}')

    
def process_ein(ein):
    # URL construction
    url = f"https://projects.propublica.org/nonprofits/organizations/{str(ein).replace('-', '')}"

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the section with filed on date
        filed_on_span = soup.find('span', class_='filed-on')
        filed_on = filed_on_span.text if filed_on_span else 'Not found'

        # Find the filing ID from the link
        view_filing_link = soup.find('a', class_='btn', href=True)
        filing_id = view_filing_link['href'].split('/')[-2] if view_filing_link else 'Not found'

        # Find the <h5> tag within the specific section
        document_section = soup.find('section', class_='document-links padded-box read-more-wrapper')
        h5_tag = document_section.find('h5') if document_section else None
        h5_text = h5_tag.text if h5_tag else 'Not found'

        # Return the results
        return filed_on, filing_id, h5_text
    else:
        return None, None, None

def start_processing():
    ein = entry.get()
    if not ein:
        messagebox.showerror("Input Error", "Please enter an EIN.")
        return

    result_label.config(text="Processing...", fg="blue")
    root.update()

    start_time = time.time()

    filed_on, filing_id, h5_text = process_ein(ein)
    
    #list_990 = []
    #list_990_pf = []

    if filed_on and filing_id and h5_text:
        if h5_text == '990':
            process_990(filing_id)
        elif h5_text == '990-PF':
            process_990_pf(filing_id)
        
        # Call processing functions
        #process_990(list_990)
        #process_990_pf(list_990_pf)
        end_time = time.time()
        elapsed_time = end_time - start_time
        result_text = (f"Filed On: {filed_on}\n"
                       f"Filing ID: {filing_id}\n"
                       f"990 Section: {h5_text}\n"
                       f"Processed in {elapsed_time:.2f} seconds.")
        result_label.config(text=result_text, fg="green")
    else:
        result_label.config(text="Failed to retrieve data. Please check the EIN and try again.", fg="red")
    # Bind Ctrl+W to close the application
    
   

# Create the main window
root = tk.Tk()
root.title("990 Processor")
root.geometry("500x400")  # Set the window size to 500x400 pixels

# Create and place the widgets
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True)

label = tk.Label(frame, text="Enter EIN:", font=("Arial", 14))
label.grid(row=0, column=0, padx=5, pady=5)

entry = tk.Entry(frame, font=("Arial", 14))
entry.grid(row=0, column=1, padx=5, pady=5)
entry.bind("<Return>", lambda event: start_processing())  # Add this line


start_button = tk.Button(frame, text="Start", command=start_processing, font=("Arial", 14))
start_button.grid(row=1, columnspan=2, pady=10)

result_label = tk.Label(frame, text="", font=("Arial", 12), wraplength=460, justify="left")
result_label.grid(row=2, columnspan=2, pady=10)

# Add the copyright information
copyright_label = tk.Label(root, text="Developed by Murtaza Contractor\n If any error found, report it to me on teams ", font=("Arial", 10), fg="grey")
copyright_label.pack(side="bottom", pady=10)

# Run the Tkinter event loop
root.mainloop()
