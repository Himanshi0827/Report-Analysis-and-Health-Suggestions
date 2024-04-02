# from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
# import pdfplumber
# import pandas as pd
# import logging
# import os
# from werkzeug.utils import secure_filename
# import matplotlib.pyplot as plt

# app = Flask(__name__)
# app.debug = True

# # Define the directory for temporarily storing uploaded files
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SECRET_KEY'] = 'your_secret_key'

# logging.basicConfig(filename='extraction.log', level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

# def parse_range(value_range):
#     value_range = value_range.strip()
#     if 'or lower' in value_range:
#         value = float(value_range.replace(' or lower', '').split()[0])
#         return float('-inf'), value
#     elif 'or higher' in value_range:
#         value = float(value_range.replace(' or higher', '').split()[0])
#         return value, float('inf')
#     elif '-' in value_range:
#         values = value_range.split('-')
#         min_value = float(values[0].split()[0])
#         max_value = float(values[1].split()[0])
#         return min_value, max_value
#     else:
#         raise ValueError("Invalid value range format")

# def get_effect_and_suggestions(blood_report_file, health_conditions_file):
#     try:
#         # Load the CSV files using absolute file paths
#         blood_report = pd.read_csv(blood_report_file)
#         health_conditions = pd.read_csv(health_conditions_file)
#         results = {}  # To store results for each parameter

#         for column in blood_report.columns:
#             for _, row in blood_report.iterrows():
#                 # Extract value for the current parameter
#                 parameter_value = float(row[column])

#                 # Find the matching rows in health_conditions.csv for the current parameter
#                 matching_rows = health_conditions[health_conditions['Conditions'] == column]

#                 category = "No matching data found"
#                 effect = ""
#                 suggestions = ""

#                 for _, matching_row in matching_rows.iterrows():
#                     value_range = matching_row['Value']
#                     min_value, max_value = parse_range(value_range)

#                     if min_value <= parameter_value <= max_value:
#                         category = matching_row['Category']
#                         effect = matching_row['Effect']
#                         suggestions = matching_row['Suggestions']
#                         break

#                 if column not in results:
#                     results[column] = []

#                 results[column].append({
#                     'Value': parameter_value,
#                     'Category': category,
#                     'Effect': effect,
#                     'Suggestions': suggestions
#                 })

#         return results

#     except FileNotFoundError as e:
#         print(f"Error: {e}")
#         return None

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         if 'pdf_file' not in request.files:
#             flash("No file part", "error")
#             return redirect(request.url)

#         pdf_file = request.files['pdf_file']

#         if pdf_file.filename == '':
#             flash("No selected file", "error")
#             return redirect(request.url)

#         if pdf_file and allowed_file(pdf_file.filename):
#             filename = secure_filename(pdf_file.filename)
#             pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#             report_type = request.form.get('report_type')
#             if report_type == 'blood_test':
#                 data, suggestions, csv_filename = blood_test_convert_to_csv(filename)
#                 visualize_data(csv_filename)
#             elif report_type == 'covid':
#                 data, suggestions = covid_convert_to_csv(filename)
#             elif report_type == 'Blood_Pressure':
#                 data, suggestions = blood_pressure_convert_to_csv(filename)
#             else:
#                 data, suggestions = None, None

#             print(suggestions)

#             return render_template('result.html', data=data, suggestions=suggestions)

#     return render_template('index.html')

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# @app.route('/static/<filename>')
# def visualize_data(filename):
#     # Load the CSV data
#     csv_file = filename
#     df = pd.read_csv(csv_file)

#     # List of elements to create bar charts for
#     elements = ['Hemoglobin', 'Total WBC Count', 'Total RBC Count', 'Platelet Count']

#     # Create bar charts for each element and save them as images
#     for element in elements:
#         data = df[element].dropna()
#         title = f'{element} Distribution'
#         x_label = f'{element} Range'
#         y_label = 'Frequency'

#         plt.figure()
#         plt.hist(data, bins=20, alpha=0.7, rwidth=0.85, color='blue', edgecolor='black')
#         plt.xlabel(x_label)
#         plt.ylabel(y_label)
#         plt.title(title)
#         plt.grid(axis='y', linestyle='--', alpha=0.7)
#         file_path = os.path.join(app.root_path, 'static', f'{element}.png')
#         plt.savefig(file_path, format='png')

#     # Render the result template with the visualizations
#     return render_template('result.html', filename=filename)

# def blood_test_convert_to_csv(pdf_file):
#     # Get the selected PDF file path
#     input_pdf = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file)
#     suggestions = "This is the blood_test converting to CSV."

#     try:
#         data = []  # Initialize data list
#         with pdfplumber.open(input_pdf) as pdf:
#             for page in pdf.pages:
#                 text = page.extract_text()

#                 hemoglobin_value = None
#                 wbc_value = None
#                 rbc_value = None
#                 Platelet_Count = None

#                 for line in text.split('\n'):
#                     if "Hemoglobin" in line:
#                         hemoglobin_value = line.split(":")[1].strip()
#                         hemoglobin_value = hemoglobin_value.split(" ")[0].strip()
#                     elif "Total WBC Count" in line:
#                         wbc_value = line.split(":")[1].strip()
#                         wbc_value = wbc_value.split(" ")[0].strip()
#                     elif "Total RBC Count" in line:
#                         rbc_value = line.split(":")[1].strip()
#                         rbc_value = rbc_value.split(" ")[0].strip()
#                     elif "Platelet Count" in line:
#                         Platelet_Count = line.split(":")[1].strip()
#                         Platelet_Count = Platelet_Count.split(" ")[0].strip()

#                 data_point = {
#                     "Hemoglobin": hemoglobin_value,
#                     "Total WBC Count": wbc_value,
#                     "Total RBC Count": rbc_value,
#                     "Platelet Count": Platelet_Count
#                 }

#                 data.append(data_point)

#                 logging.info("Extracted data: %s", data_point)

#         df = pd.DataFrame(data)

#         output_csv = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.replace(".pdf", "_blood_test.csv"))
#         csv_filename = f"{output_csv}"
#         df.to_csv(csv_filename, index=False)
#         logging.info("Data saved to CSV file: %s", csv_filename)
#         logging.info("Conversion Complete - PDF data has been converted and saved to CSV.")
       
#     except Exception as e:
#         logging.error("PDF extraction error: %s", str(e))
#         logging.info("Error - An error occurred while processing the PDF.")
#         return None, suggestions, None

#     return data, suggestions, csv_filename

# def covid_convert_to_csv(pdf_file):
#     input_pdf = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file)
#     suggestions = "This is the COVID test converting to CSV."

#     try:
#         data = []  # Initialize data list
#         with pdfplumber.open(input_pdf) as pdf:
#             for page in pdf.pages:
#                 text = page.extract_text()

#                 ORF_1ab = None
#                 N_gene = None

#                 for line in text.split('\n'):
#                     if "ORF 1ab" in line:
#                         ORF_1ab = line.split()[2]
#                     elif "N gene" in line:
#                         N_gene = line.split()[2]

#                 data_point = {
#                     "ORF 1ab": ORF_1ab,
#                     "N gene": N_gene
#                 }

#                 data.append(data_point)

#                 logging.info("Extracted data: %s", data_point)

#         df = pd.DataFrame(data)

#         output_csv = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.replace(".pdf", "_Covid_test.csv"))
#         csv_filename = f"{output_csv}"
#         df.to_csv(csv_filename, index=False)
#         logging.info("Data saved to CSV file: %s", csv_filename)
#         logging.info("Conversion Complete - PDF data has been converted and saved to CSV.")
#     except Exception as e:
#         logging.error("PDF extraction error: %s", str(e))
#         logging.info("Error - An error occurred while processing the PDF.")
#         return None, suggestions, None

#     return data, suggestions

# def blood_pressure_convert_to_csv(pdf_file):
#     input_pdf = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file)
#     suggestions = "This is the blood pressure test converting to CSV."

#     try:
#         data = []  # Initialize data list
#         with pdfplumber.open(input_pdf) as pdf:
#             for page in pdf.pages:
#                 text = page.extract_text()

#                 systolic_bp = None
#                 diastolic_bp = None
#                 pulse = None

#                 for line in text.split('\n'):
#                     if "Systolic BP" in line:
#                         systolic_bp = line.split(":")[1].strip()
#                     elif "Diastolic BP" in line:
#                         diastolic_bp = line.split(":")[1].strip()
#                     elif "Pulse" in line:
#                         pulse = line.split(":")[1].strip()

#                 data_point = {
#                     "Systolic BP": systolic_bp,
#                     "Diastolic BP": diastolic_bp,
#                     "Pulse": pulse
#                 }

#                 data.append(data_point)

#                 logging.info("Extracted data: %s", data_point)

#         df = pd.DataFrame(data)

#         output_csv = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.replace(".pdf", "_blood_pressure_test.csv"))
#         csv_filename = f"{output_csv}"
#         df.to_csv(csv_filename, index=False)
#         logging.info("Data saved to CSV file: %s", csv_filename)
#         logging.info("Conversion Complete - PDF data has been converted and saved to CSV.")
#     except Exception as e:
#         logging.error("PDF extraction error: %s", str(e))
#         logging.info("Error - An error occurred while processing the PDF.")
#         return None, suggestions, None

#     return data, suggestions

# if __name__ == '__main__':
#     app.run(debug=True)












from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
import pdfplumber
import pandas as pd
import logging
import os
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

app = Flask(__name__)
app.debug = True

# Define the directory for temporarily storing uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key'

logging.basicConfig(filename='extraction.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    # Check if the post request has the file part
    if 'pdf_file' not in request.files:
      flash("No file part", "error")
      return redirect(request.url)

    pdf_file = request.files['pdf_file']

    # If the user does not select a file, the browser also submits an empty part without a filename.
    if pdf_file.filename == '':
      flash("No selected file", "error")
      return redirect(request.url)

    if pdf_file and allowed_file(pdf_file.filename):
      # Secure and save the uploaded PDF file
      filename = secure_filename(pdf_file.filename)
      pdf_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))

      # Process the uploaded PDF and generate visualizations
      report_type = request.form.get('report_type')
      if report_type == 'blood_test':
        data, suggestions,csv_filename = blood_test_convert_to_csv(filename)
        # Provide the absolute file paths to your CSV files
        blood_report_file = csv_filename
        health_conditions_file = r'D:\\data\\sem5\\python\\himanshi\\imp_files\\health_conditions1.csv'

        # Call the function with the absolute file paths
        suggestions = get_effect_and_suggestions(blood_report_file, health_conditions_file)
        visualize_data(csv_filename,suggestions)
        return render_template('result.html', data=data, suggestions=suggestions)
      elif report_type == 'covid':
        data, suggestions,csv_filename = covid_convert_to_csv(filename)
        # Provide the absolute file paths to your CSV files
        test_report_file = csv_filename
        health_conditions_file = r'D:\\data\\sem5\\python\\himanshi\\imp_files\\health_conditions1.csv'

        # Call the function with the absolute file paths
        suggestions = get_effect_and_suggestions_covid(test_report_file, health_conditions_file)
        return render_template('covidResult.html', data=data, suggestions=suggestions)
      elif report_type == 'blood_pressure':
        data, suggestions = blood_pressure_convert_to_csv(filename)
        return render_template('bloodPressureResult.html', data=data, suggestions=suggestions)
      else:
        data, suggestions = None, None

      # Print the suggestions variable
    #   print(suggestions)

    #   return render_template('result.html', data=data, suggestions=suggestions)

  return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/result')
def result():
    data = [...]  # Replace with the actual data
    suggestions = "This is a suggestion."  # Replace with the actual suggestion

    return render_template('result.html', data=data, suggestions=suggestions)
def blood_test_convert_to_csv(pdf_file):
    # Get the selected PDF file path
    input_pdf = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file)
    suggestions = "This is the blood_test converting to CSV."

    try:
        data = []  # Initialize data list
        with pdfplumber.open(input_pdf) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                # Initialize variables
                hemoglobin_value = None
                wbc_value = None
                rbc_value = None
                Platelet_Count = None

                # Parse the text and extract relevant information
                for line in text.split('\n'):
                    if "Hemoglobin" in line:
                        hemoglobin_value = line.split(":")[1].strip()
                        hemoglobin_value=hemoglobin_value.split(" ")[0].strip()
                    elif "Total WBC Count" in line:
                        wbc_value = line.split(":")[1].strip()
                        wbc_value=wbc_value.split(" ")[0].strip()
                    elif "Total RBC Count" in line:
                        rbc_value = line.split(":")[1].strip()
                        rbc_value=rbc_value.split(" ")[0].strip()
                    elif "Platelet Count" in line:
                        Platelet_Count = line.split(":")[1].strip()
                        Platelet_Count=Platelet_Count.split(" ")[0].strip()

                # Create a dictionary
                data_point = {
                    "Hemoglobin": hemoglobin_value,
                    "White Blood Cell Count": wbc_value,
                    "Total Red Blood cell Count": rbc_value,
                    "Platelet Count": Platelet_Count
                }

                # Append the data_point dictionary to the data list
                data.append(data_point)

                # Log the extracted data for this page
                logging.info("Extracted data: %s", data_point)

        # Create a DataFrame from the data list
        df = pd.DataFrame(data)

        # Save the DataFrame to a CSV file
        output_csv = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.replace(".pdf", "_blood_test.csv"))
        csv_filename = f"{output_csv}"
        df.to_csv(csv_filename, index=False)
        logging.info("Data saved to CSV file: %s", csv_filename)
        logging.info("Conversion Complete - PDF data has been converted and saved to CSV.")
        
       
    except Exception as e:
        logging.error("PDF extraction error: %s", str(e))
        logging.info("Error - An error occurred while processing the PDF.")
        return None, suggestions

    return data, suggestions,csv_filename


def parse_range(value_range):
    value_range = value_range.strip()
    if 'or lower' in value_range:
        value = float(value_range.replace(' or lower', '').split()[0])
        return float('-inf'), value
    elif 'or higher' in value_range:
        value = float(value_range.replace(' or higher', '').split()[0])
        return value, float('inf')
    elif '-' in value_range:
        values = value_range.split('-')
        min_value = float(values[0].split()[0])
        max_value = float(values[1].split()[0])
        return min_value, max_value
    else:
        raise ValueError("Invalid value range format")

def get_effect_and_suggestions(blood_report_file, health_conditions_file):
    try:
        # print("Hello")
        # Load the CSV files using absolute file paths
        blood_report = pd.read_csv(blood_report_file)
        health_conditions = pd.read_csv(health_conditions_file)
        # print(health_conditions)
        # print("Hello")
        results = {}  # To store results for each parameter

        for column in blood_report.columns:
                for _, row in blood_report.iterrows():
                    # Extract value for the current parameter
                    # print(row[column])
                    parameter_value = float(row[column])

                    # Find the matching rows in health_conditions.csv for the current parameter
                    matching_rows = health_conditions[health_conditions['Conditions'] == column]
                    # print("It is from blood report matching rows \n",matching_rows)
                    category = "No matching data found"
                    effect = ""
                    suggestions = ""

                    for _, matching_row in matching_rows.iterrows():
                        value_range = matching_row['Value']
                        min_value, max_value = parse_range(value_range)
                        # print("Min value",min_value," Value range",value_range," max value",max_value)
                        if min_value <= parameter_value <= max_value:
                            category = matching_row['Category']
                            effect = matching_row['Effect']
                            suggestions = matching_row['Suggestions']
                            break

                    if column not in results:
                        results[column] = []

                    results[column].append({
                        'Value': parameter_value,
                        'Category': category,
                        'Effect': effect,
                        'Suggestions': suggestions
                    })

        return results

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None

# # Provide the absolute file paths to your CSV files
# blood_report_file = r'D:\\data\\sem5\\python\\himanshi\\uploads\\blood_report_blood_test.csv'
# health_conditions_file = r'D:\\data\\sem5\\python\\himanshi\\imp_files\\health_conditions1.csv'


# # Call the function with the absolute file paths
# results = get_effect_and_suggestions(blood_report_file, health_conditions_file)

# # Display the results for each condition
# for condition, data in results.items():
#     print(condition + ":")
#     for item in data:
#         print(f"Value: {item['Value']}")
#         print(f"Category: {item['Category']}")
#         print(f"Effect: {item['Effect']}")
#         print(f"Suggestions: {item['Suggestions']}")
#         print()

# def parse_range_covid(value_range):
#     print(value_range)
#     if 'NOT' in value_range:
#         return 'NOT'
#     # elif 'or higher' in value_range:
#     #     value = (value_range.replace(' or higher', '').split()[0])
#     #     return value, ('inf')
#     # elif '-' in value_range:
#     #     values = value_range.split('-')
#     #     min_value = float(values[0].split()[0])
#     #     max_value = float(values[1].split()[0])
#     #     return min_value, max_value
#     else:
#         raise ValueError("Invalid value range format")
    
def get_effect_and_suggestions_covid(test_report_file,health_conditions_file):
    try:
        test_report = pd.read_csv(test_report_file)
        health_conditions = pd.read_csv(health_conditions_file)
        results = {}
        # print(test_report)
        for column in test_report.columns:
            # print(column)
            for _,row in test_report.iterrows():
                parameter_value = (row[column])
                # print("It is for parameter",parameter_value)
                matching_rows = health_conditions[health_conditions['Conditions'] == column]
                # print("It is from matching \n",matching_rows)
                category = "No matching data found"
                effect = ""
                suggestions = ""

                for _, matching_row in matching_rows.iterrows():
                    # print("Its matching rows",matching_row)
                    value_range = matching_row['Value']
                    # print("It is from get effect of covid",value_range)
                    if value_range == 'NOT' or value_range == 'NEGATIVE' :
                        # print("Values are going")
                        category = matching_row['Category']
                        effect = matching_row['Effect']
                        suggestions =  matching_row['Suggestions']
                        break
                    elif value_range == 'POSITIVE' or value_range == 'DETECTED':
                        category = matching_row['Category']
                        effect = matching_row['Effect']
                        suggestions =  matching_row['Suggestions']
                        break
                    else :
                        # print("Values are going")
                        category = matching_row['Category']
                        effect = matching_row['Effect']
                        suggestions =  matching_row['Suggestions']
                        break

                if column not in results:
                    results[column] = []

                results[column].append({
                    'Value': parameter_value,
                    'Category': category,
                    'Effect': effect,
                    'Suggestions': suggestions
                })
        return results
    

        # for _, matching_row in matching_rows.iterrows():
        #                 value_range = matching_row['Value']
        #                 min_value, max_value = parse_range(value_range)

        #                 if min_value <= parameter_value <= max_value:
        #                     category = matching_row['Category']
        #                     effect = matching_row['Effect']
        #                     suggestions = matching_row['Suggestions']
        #                     break

        #             if column not in results:
        #                 results[column] = []

        #             results[column].append({
        #                 'Value': parameter_value,
        #                 'Category': category,
        #                 'Effect': effect,
        #                 'Suggestions': suggestions
        #             })

        # return results

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None

# # Provide the absolute file paths to your CSV files
# test_report_file = r'D:\\data\\sem5\\python\\himanshi\\uploads\\TestReport_Covid_test.csv'
# health_conditions_file = r'D:\\data\\sem5\\python\\himanshi\\imp_files\\health_conditions1.csv'

# # Call the function with the absolute file paths
# results1 = get_effect_and_suggestions_covid(test_report_file, health_conditions_file)
# # Display the results for each condition
# for condition, data in results1.items():
#     print(condition + ":")
#     for item in data:
#         print(f"Value: {item['Value']}")
#         print(f"Category: {item['Category']}")
#         print(f"Effect: {item['Effect']}")
#         print(f"Suggestions: {item['Suggestions']}")
#         print()


def covid_convert_to_csv(pdf_file):
    # Get the selected PDF file path
    input_pdf = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file)
    suggestions = "This is the COVID test converting to CSV."

    try:
        data = []  # Initialize data list
        with pdfplumber.open(input_pdf) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                # Initialize variables
                ORF_1ab = None
                N_gene = None
                Conclusion = None

                # Parse the text and extract relevant information
                for line in text.split('\n'):
                    if "ORF 1ab" in line:
                        ORF_1ab = line.split()[2]
                    elif "N gene" in line:
                        N_gene = line.split()[2]
                    elif "Conclusion" in line:
                        Conclusion = line.split()[2]

                # Create a dictionary
                data_point = {
                    "ORF 1ab": ORF_1ab,
                    "N gene": N_gene,
                    "Conclusion" : Conclusion
                }

                # Append the data_point dictionary to the data list
                data.append(data_point)

                # Log the extracted data for this page
                logging.info("Extracted data: %s", data_point)

        # Create a DataFrame from the data list
        df = pd.DataFrame(data)

        # Save the DataFrame to a CSV file
        output_csv = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.replace(".pdf", "_Covid_test.csv"))
        csv_filename = f"{output_csv}"
        df.to_csv(csv_filename, index=False)
        logging.info("Data saved to CSV file: %s", csv_filename)
        logging.info("Conversion Complete - PDF data has been converted and saved to CSV.")
    except Exception as e:
        logging.error("PDF extraction error: %s", str(e))
        logging.info("Error - An error occurred while processing the PDF.")
        return None, suggestions

    return data, suggestions,csv_filename

def blood_pressure_convert_to_csv(pdf_file):
# Get the selected PDF file path
    input_pdf = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file)
    suggestions = "This is the blood pressure test converting to CSV."

    try:
        data = [] # Initialize data list
        with pdfplumber.open(input_pdf) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
# Initialize variables
                systolic_bp = None
                diastolic_bp = None
                pulse = None

# Parse the text and extract relevant information
            for line in text.split('\n'):
                if "Systolic BP" in line:
                    systolic_bp = line.split(":")[1].strip()
                elif "Diastolic BP" in line:
                    diastolic_bp = line.split(":")[1].strip()
                elif "Pulse" in line:
                    pulse = line.split(":")[1].strip()

# Create a dictionary
            data_point = {
                "Systolic BP": systolic_bp,
                "Diastolic BP": diastolic_bp,
                "Pulse": pulse
                }

# Append the data_point dictionary to the data list
            data.append(data_point)

# Log the extracted data for this page
            logging.info("Extracted data: %s", data_point)

# Create a DataFrame from the data list
        df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
        output_csv = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.replace(".pdf", "_blood_pressure_test.csv"))
        csv_filename = f"{output_csv}"
        df.to_csv(csv_filename, index=False)
        logging.info("Data saved to CSV file: %s", csv_filename)
        logging.info("Conversion Complete - PDF data has been converted and saved to CSV.")
    except Exception as e:
        logging.error("PDF extraction error: %s", str(e))
        logging.info("Error - An error occurred while processing the PDF.")
        return None, suggestions

    return data, suggestions

# Define the functions for converting PDF to CSV (blood_test, covid, blood_pressure) here

@app.route('/static/<path:filename>')
def visualize_data(filename,suggestions):
    # Load the CSV data
    # csv_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    csv_file=filename
    df = pd.read_csv(csv_file)

    # List of elements to create bar charts for
    elements = ['Hemoglobin', 'White Blood Cell Count', 'Total Red Blood cell Count', 'Platelet Count']

    # Create bar charts for each element and save them as images
    for element in elements:
        data = df[element].dropna()
        title = f'{element} Distribution'
        x_label = f'{element} Range'
        y_label = 'Frequency'

        plt.figure()
        plt.hist(data, bins=20, alpha=0.7, rwidth=0.85, color='blue', edgecolor='black')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        file_path = os.path.join(app.root_path, 'static', f'{element}.png')
        plt.savefig(file_path, format='png')
        # plt.savefig(os.path.join(app.root_path, 'static', f'{element}.png'))

    # Render the result template with the visualizations
    return render_template('result.html', filename=filename,suggestions=suggestions)
if __name__ == '__main__':
    app.run(debug=True)



















