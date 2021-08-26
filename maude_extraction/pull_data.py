# -*- coding: utf-8 -*-
"""
This script pulls data from the FDA MAUDE database based on a date range
and FDA assigned product code

Payload Structure meta { disclaimer, terms, license, last_updated, 
    results {skip, limit, total}
    }  
results { manufacturer_contact_zip_ext, manufacturer_g1_address_2,  
    event_location, report_to_fda, manufacturer_contact_t_name,  
    manufacturer_contact_state, manufacturer_link_flag,  
    manufacturer_g1_city, manufacturer_contact_address_2,  
    manufacturer_contact_address_1, event_type, manufacturer_contact_pcity,  
    report_number, type_of_report [Initial submission, Followup]  
    product_problem_flag, date_received, manufacturer_address_2  
    date_of_event, reprocessed_and_reused_flag, manufacturer_address_1,  
    manufacturer_contact_zip_code, manufacturer_contact_plocal,  
    reporter_occupation_code, manufacturer_contact_1_name, source_type,  
    distributor_zip_code_ext, manufacturer_g1_postal_code,  
    manufacturer_g1_state, manufacturer_contact_f_name,  
    device_date_of_manufacturer, previous_use_code,  
    device { manufacturer_d_address_1, manufacturer_d_address_2,  
        device_event_key, device_sequence_number, manufacturer_d_state,  
        manufacturer_d_zip_code, manufacturer_d_city, lot_number,  
        manufacturer_d_postal_code, manufacturer_d_zip_code_ext,  
        model_number, date_received, device_report_product_code,  
        device_operator, device_availability, other_id_number,  
        generic_name, manufacturer_d_name, manufacturer_d_country,  
        brand_name,  
        openfda {device_name, medical_specialty_description, device_class,  
            regulation_number}  
        device_age_text, device_evaluated_by_manufacturer, catalog_number,  
        implant_flag, date_removed_flag}  
    product_problems, manufacturer_zip_code, manufacturer_contact_country,  
    health_professional, manufacturer_g1_zip_code_ext, manufacturer_city,  
    manufacturer_contact_extension, manufacturer_contact_phone_number,  
    patient {sequence_number_treatment, patient_sequence_number, date_received,  
        sequence_number_outcome}  
    distributor_city, distributor_state, date_report, initial_report_to_fda,  
    manufacturer_g1_country, event_key, manufacturer_contact_city,  
    mdr_report_key, removal_correction_number, number_devices_in_event,  
    date_manufacturer_received, manufacturer_name, report_source_code,  
    remedial_action, manufacturer_g1_zip_code, manufacturer_zip_code_ext,   
    report_to_manufacturer, manufacturer_g1_name, distributor_address_1,   
    adverse_event_flag, manufacturer_state, distributor_address_2,  
    manufacturer_postal_code, manufacturer_country, single_use_flag,  
    mdr_text [{mdr_text_key, text_type_code, patient_sequence_number, text}],  
    number_patients_in_event, distributor_name, manufacturer_g1_address_1,  
    distributor_zip_code, manufacturer_contact_exchange,  
    manufacturer_contact_postal_code, manufacturer_contact_pcountry }

    99 Records max per request
    Not clear how API is exactly joining the base tables that make up MAUDE
    togeter - event_key which should be the unique key for events is absent 
      from the MAUDE data and request is returning redundant events with 
      distinct report keys
    No hierarchical structure or validation for what products are put under 
      what product code - thus need to search all applicable and filter
    number_of_patients_in_event = multiple patients may be associated with a 
      single report; number of patients greater than 1 need special parsing 
      for patient outcome sequence since all codes are simply concatenated 
      together (can split on sequence 1)"""

import os
import argparse
import csv
import math
import datetime
import requests

patient_seq = {"L":"Life Threatening", "H":"Hospitalization", "S":"Disability",
               "C":"Congenital Anomaly", "R":"Required Intervention", "O":"Other",
               "*":"Invalid Data", "U":"Unknown", "I":"No Information", "A":"Not Applicable",
               "D":"Death"}

def build_requests(initial_get, total, limit=99):  
    loops = math.floor(total/limit)
    extra = total % limit

    if loops < (total/limit):
        loops += 1
    
    request_list = []   
    skip = 0
    for i in range(loops):
        request_str = initial_get + "&skip=" + str(skip) + "&limit=" + str(limit)
        request_list.append(request_str)
        if i == loops - 2:
            limit = extra
            skip += 99
        else:
            skip += 99
    return request_list
    
def main(prd_code, 
         date1, 
         date2=datetime.date.today().strftime("%Y%m%d"), 
         log=False,
         export=True):
    # GET request from FDA API, default today's date, return json
    get_request = ("https://api.fda.gov/device/event.json?search=device.device"
        "_report_product_code:{}"
        "+AND+date_of_event:[{}+TO+{}]").format(prd_code, date1, date2)
    r = requests.get(get_request)
    r.raise_for_status()
    # Get total, build how many loop/requests, add to json
    data = r.json()
    total = int(data['meta']['results']['total'])
    print("Total Records" + " : " + str(total))
    maude_requests = build_requests(get_request, total)
    
    # Delete all logs at start
    if log == True:
        path = os.getcwd()
        log_dir = 'json_raw'
        path = os.path.join(path, log_dir)
        if os.path.isdir(path)== False:  
            os.mkdir(path)
        path = os.path.join (path, 'json_request_')
        i = 1
        
    for r in maude_requests:
        output = requests.get(r)
        output.raise_for_status()
        if log == True:
            filepath = path + str(i) + '.json'
            with open(filepath, 'wb') as f:
                f.write(output.content)
            i += 1
                
        data['results'].extend(output.json()['results'])
    data = [data, [prd_code, date1, date2, str(total)]]
    if export:
        export_data(data)
    return data

def process_MDR_text(mdr_text_list):
    desc_event = ''
    addit_nar = ''
    
    descs = [text[2] for text in mdr_text_list if text[1] == 'Description of Event or Problem']
    addits = [[text[0], text[2]] for text in mdr_text_list if text[1] == 'Additional Manufacturer Narrative']
    
    # Keep the largest description (initial)
    try:
        desc_event = sorted(descs)[0]
    # These are actual reports - this is a bug
    except IndexError:
        desc_event = "No Description Available"
        return desc_event
    
    # Concatenate additional narrative (if different) in order of increasing IDs
    # Default behavior to sort on first
    addits = sorted(addits)
    addit_nar = ' '.join([ele[1] for ele in addits])
    if len(addit_nar) > 0:
        return 'Description of Event or Problem : ' + desc_event + ' Additional Manufacturer Narrative: ' + addit_nar
    else:
        return 'Description of Event or Problem : ' + desc_event
            

def export_data(data, datatype = 'unique'):
    report_numbers = set()
    with open('data/data_output.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Search Parameters
        csv_writer.writerow(['Product Code: ' + data[1][0]])
        csv_writer.writerow(['Date Range: ' + data[1][1] + ' - ' + data[1][2]])
        csv_writer.writerow(['Total Results: ' + data[1][3]])
        # Headers
        csv_writer.writerow(['Report Number', 'Manufacturer', 'Brand : Model Number', 'Reportable Event Type',
                             'Reporter', 'Event Location', 'Date of Event', 'Device Operator', 'Health Professional Type', 'Product Problem(s)', 
                             'Device Sequence', 'Outcome Sequence', 'MDR Text'])
        if datatype == 'unique':
            for record in data[0]['results']:
                date_of_event = record['date_of_event']
                event_location = record['event_location']
                rpt_num = record['report_number']
                if rpt_num in report_numbers:
                    # do not add repeat report
                    continue
                else:
                    report_numbers.add(rpt_num)
                try:
                    product_problems = ','.join(record['product_problems'])
                except TypeError:
                    product_problems = "No Problem in Record (blank field)"
                except KeyError:
                    # print('No product problem field in record ---', record)
                    product_problems = "No Problem in Record (no field)"
                health_professional = record['health_professional']
                event_type = record['event_type']
                reporter = record['reporter_occupation_code']
                mdr_text = []
                for mdr_report in record['mdr_text']:
                    mdr_text_key = mdr_report['mdr_text_key']
                    text_type = mdr_report['text_type_code']
                    text = mdr_report['text']
                    mdr_text.append([mdr_text_key, text_type, text])
                mdr_text_export = process_MDR_text(mdr_text)
                devices = ''
                for device_info in record['device']:
                    if device_info['brand_name'] == "" and device_info['model_number'] == "":
                        devices += device_info['generic_name'] + " : " + "No Model Listed"
                    elif device_info['brand_name'] == "":
                        devices += device_info['generic_name'] + " : " + device_info['model_number']
                    else:
                        devices += device_info['brand_name'] + " : " + device_info['model_number']
                    device_operator = device_info['device_operator']
                    manufacturer = device_info['manufacturer_d_name']
                for patient_info in record['patient']:
                    device_seq = ','.join(patient_info['sequence_number_treatment'])
                    outcome_seq = ""
                    if patient_info['sequence_number_outcome'][0] != "":
                        outcome_seq = ','.join([patient_seq[(code.replace(' ','').replace('.',''))[1]] for code in patient_info['sequence_number_outcome']])
                csv_writer.writerow([rpt_num, manufacturer, devices, event_type, reporter, event_location, date_of_event,
                                     device_operator, health_professional, product_problems,
                                     device_seq, outcome_seq, mdr_text_export])
                # Raw = multiple rows for each difference in record (ie multiple AEs, devices)
        if datatype == 'raw':
            for record in data[0]['results']:
                date_of_event = record['date_of_event']
                rpt_num = record['report_number']
                try:
                    product_problems = ','.join(record['product_problems'])
                except TypeError:
                    product_problems = "No Problem in Record"
                health_professional = record['health_professional']
                
                combined_MDR = ''
                combined_device_info = ''
                
                for mdr_report in record['mdr_text']:
                    mdr_text_key = mdr_report['mdr_text_key']
                    text_type = mdr_report['text_type_code']
                    patient_sequence_number = mdr_report['patient_sequence_number']
                    text = mdr_report['text']
                    for device_info in record['device']:
                        csv_writer.writerow([rpt_num, device_info['brand_name'], 
                                              device_info['model_number'], date_of_event,
                                              health_professional, product_problems,
                                              mdr_text_key, text_type,
                                              patient_sequence_number, text])

def parse_args():
    parser = argparse.ArgumentParser(description="""Retrieve data using the 
                                     openFDA api (https://open.fda.gov/) from
                                     the MAUDE medical device adverse event 
                                     database""")
    parser.add_argument("product_code", type=str,
                        help="""The FDA product code corresponding to device type""")
    parser.add_argument("start_date", type=str,
                        help="Start date in YYYYMMDD format")
    # Can still omit end_date to use today but not represented here
    parser.add_argument("end_date", type=str,
                        help="End date in YYYYMMDD format")
    parser.add_argument("-l", "--log", action="store_true", default=False,
                        help="Indicate if logging")
    parser.add_argument("-n", "--noexport", action="store_false", 
                        help="Do not save data to disk")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(args)
    data = main(args.product_code, args.start_date, args.end_date,
                log=args.log, export=args.noexport)
