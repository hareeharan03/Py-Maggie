from flask import Flask, render_template, request, make_response, redirect, url_for, flash, session, send_file, Blueprint
from werkzeug.utils import secure_filename
import zipfile
import io

#utils import
from application.utils.report_utils import output_info, get_report_data
from application.utils.cache_utils import update_csv_file, getting_csv, view_cache, clear_inactive_cache, clear_inactive_cache_immediate
from application.utils.database_utils import connect_to_database
from application.utils.logger import configure_logger

#configuring logger
logger = configure_logger()

file_download=Blueprint('file_download',__name__, static_folder='application\staticFiles')

@file_download.route("/end_download_dataset", methods=["GET", "POST"])
def end_download_dataset():

    df=getting_csv("root_df")

    options = session['dataframes_saved_in_cache']

    substring_to_remove = "_"+session['session_id']

    options = [s.replace(substring_to_remove, "") for s in options]

    if request.method == "POST":
        # get the selected options from the form
        selected_options = request.form.getlist("options")
        session["download_files"]=selected_options

        return redirect(url_for("file_download.download_zip"))

    output_info("Thank you for using PyMaggie")

    message=get_report_data()

    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    question=""

    return render_template("index.html", question=question, message=message,list=False,show_download_popup=True,options=options,dataframe=dataframe)

def replace_substring_in_list(my_list, substring_to_replace, replacement):
    result_list = []
    for string in my_list:
        new_string = string.replace(substring_to_replace, replacement)
        result_list.append(new_string)
    return result_list

@file_download.route('/download_zip', methods=["GET", "POST"])
def download_zip():
    # Get the selected options from the session
    selected_options = session.get("download_files", [])

    # Fetch the DataFrames corresponding to the selected options from the cache
    dataframes = [getting_csv(option) for option in selected_options]

    # Create an in-memory buffer to store the zip data
    zip_buffer = io.BytesIO()

    # Convert DataFrames to CSVs in memory and add to the zip buffer
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for i, df in enumerate(dataframes):
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            zipf.writestr(selected_options[i] + ".csv", csv_buffer.getvalue())

    zip_buffer.seek(0)

    # Clear the cache immediately after sending the file
    clear_inactive_cache_immediate()

    return send_file(zip_buffer, download_name='data.zip', as_attachment=True)