import os
import sys
import csv
import re
import fileinput
import yaml

fix_c1s_headers = { 'c1s_2a_npsylan' : 'c1s_2_npsycloc',
                    'c1s_2a_npsylanx' : 'c1s_2a_npsylan',
                    'b6s_2a1_npsylanx' : 'c1s_2a1_npsylanx'}

fix_fvp_headers = { 'fu_otherneur' : 'fu_othneur',
                    'fu_otherneurx' : 'fu_othneurx',
                    'fu_strokedec' : 'fu_strokdec' }

fill_default_values = { 'nogds' : 0,
                        'arthupex' : 0,
                        'arthloex' : 0,
                        'arthspin' : 0,
                        'arthunk' : 0,
                        'adcid' : 41,
                        'formver' : 3 }

fill_non_blank_values = { 'adcid' : '41' }

# def connect_to_redcap(config_path):
#     #Read in the config file. If the config file is missing or the wrong format, exit the program.
#     print config_path
#     try:
#         with open(config_path, 'r') as config_file:
#             config = yaml.load(config_file.read())
#     except:
#         print("Error: Check config file")
#         exit()
#     return config

# def control_filters():
#     check_filters(input_ptr,filter_meta,output_ptr)
#     return

# def get_data():
#
#     # config = connect_to_redcap(filters_config.yaml)
#
#     cmd = '''curl -v -d  '{"token": "10.0.0.1/32", "content": "", "format": "csv", "type": "flat"}' https://my.redcap.server/redcap/api'''
#     args = cmd.split()
#     process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     stdout, stderr = process.communicate()

# def filter_clean_ptid(input_ptr, filter_meta, output_ptr):
# # TODO  To run anything on followup visit Packet in future
#
#     reader = csv.DictReader(input_ptr)
#     output = csv.DictWriter(output_ptr, None)
#     curr_ptid = csv.DictReader(ptid_file)
#     write_headers(reader, output)
#
#     # with open(filter_meta, 'r') as ptid_file:
#     for record in reader:
#         ptid = record['ptid']
#         for to_rem_ptid in curr_ptid:
#             # Cases to remove the following Packets
#             packet_type = to_rem_ptid['Packet type']
#             if ptid == to_rem_ptid["Patient ID"]:
#                 if packet_type == "I" and record['redcap_event_name']=="":
#                     print >> sys.stderr, 'Eliminated ptid : ' + ptid
#
#             prog_initial_visit = re.compile("followup.*")
#             if ptid in ptids and prog_initial_visit.match(record['redcap_event_name'])!=None:
#                 print >> sys.stderr, 'Eliminated ptid : ' + ptid
#             else:
#                 output.writerow(record)
#     return

def write_headers(reader, output):
    if output.fieldnames is None:
        # Initially empty file. Write column headers.
        output.fieldnames = reader.fieldnames
        output_header = dict((h,h) for h in reader.fieldnames)
        output.writerow(output_header)

def filter_replace_drug_id(input_ptr, filter_meta, output_ptr):

    reader = csv.DictReader(input_ptr)
    output = csv.DictWriter(output_ptr, None)
    write_headers(reader, output)
    for record in reader:
        count = 0
        prefixes = ['','fu_']
        for prefix in prefixes:
            for i in range(1, 31):
                col_name = prefix + 'drugid_' + str(i)
                if col_name in record.keys():
                    col_value = record[col_name]
                    if len(col_value) > 0 :
                        record[col_name] = 'd' + col_value[1:]
                        count += 1
        output.writerow(record)
        print >> sys.stderr, 'Processed ptid : ' + record['ptid'] + ' Updated ' + str(count) + ' fields.'
    return

def filter_fix_c1s(input_ptr, filter_meta, output_ptr):

    lines = input_ptr.read().splitlines()
    header = True
    for line in lines:
        if header:
            header = False
            for key in fix_c1s_headers.keys():
                line=line.replace(key, fix_c1s_headers[key],1)
        print line
    return

def filter_fix_fvpheader(input_ptr, filter_meta, output_ptr):

    lines = input_ptr.read().splitlines()
    header = True
    for line in lines:
        if header:
            header = False
            for key in fix_fvp_headers.keys():
                print >> sys.stderr, 'key : ' + key + ' Value : '+  fix_fvp_headers[key]
                line=line.replace(key, fix_fvp_headers[key],1)
        print line
    return


def filter_remove_ptid(input_ptr, filter_meta, output_ptr):

    reader = csv.DictReader(input_ptr)
    output = csv.DictWriter(output_ptr, None)
    write_headers(reader, output)
    for record in reader:
        prog = re.compile("11\d.*")
        if prog.match(record['ptid'])!=None:
            output.writerow(record)
        else:
            print >> sys.stderr, 'Removed ptid : ' + record['ptid']

def filter_eliminate_empty_date(input_ptr, filter_meta, output_ptr):

    reader = csv.DictReader(input_ptr)
    output = csv.DictWriter(output_ptr, None)
    write_headers(reader, output)
    for record in reader:
        if record['visitmo']=='' and record['visitday']=='' and record['visityr']=='':
            print >> sys.stderr, 'Removed ptid : ' + record['ptid']
        else:
            output.writerow(record)

def fill_value_of_fields(input_ptr, output_ptr, keysDict, blankCheck=False, defaultCheck=False):

    reader = csv.DictReader(input_ptr)
    output = csv.DictWriter(output_ptr, None)
    write_headers(reader, output)
    for record in reader:
        count = 0
        for col_name in keysDict.keys():
            if col_name in record.keys():
                if blankCheck and (len(record[col_name]) > 0) and (record[col_name] != keysDict[col_name]):
                        record[col_name] = keysDict[col_name]
                        count += 1
                elif defaultCheck and len(record[col_name]) == 0:
                        record[col_name] = keysDict[col_name]
                        count += 1
        output.writerow(record)
        print >> sys.stderr, 'Processed ptid : ' + record['ptid'] + ' Updated ' + str(count) + ' fields.'
    return

def filter_fill_default(input_ptr, filter_meta, output_ptr):
    fill_value_of_fields(input_ptr, output_ptr, fill_default_values, defaultCheck=True)

def filter_update_field(input_ptr, filter_meta, output_ptr):
    fill_value_of_fields(input_ptr, output_ptr, fill_non_blank_values, blankCheck=True)
