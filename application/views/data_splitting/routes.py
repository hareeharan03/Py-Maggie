from flask import Flask, render_template, request, make_response, redirect, url_for, flash, session, Blueprint
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

from sklearn.model_selection import train_test_split

from datetime import datetime



#utils import
from application.utils.report_utils import output_info, get_report_data
from application.utils.cache_utils import update_csv_file, getting_csv, view_cache, clear_inactive_cache, clear_inactive_cache_immediate
from application.utils.database_utils import connect_to_database
from application.utils.logger import configure_logger

#configuring logger
logger = configure_logger()

data_splitting=Blueprint('data_splitting',__name__, static_folder='application\staticFiles')

@data_splitting.route("/direct_splitting_data", methods=["GET", "POST"])
def direct_splitting_data():

    df=getting_csv("root_df")

    if request.method == "POST":
        answerr = request.form.get("thirteen")
        if answerr == "yes":
            return redirect(url_for("data_splitting.splitting_data"))
        elif answerr == "no":
            return redirect(url_for("file_download.end_download_dataset"))
        
    message=get_report_data()

    question="Do you want to split the dataset into train and test?"
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    return render_template("index.html", question=question, message=message,list=False,button_name="thirteen",dataframe=dataframe)


@data_splitting.route("/splitting_data", methods=["GET", "POST"])
def splitting_data():
    #global df,predictor,target

    df=getting_csv("root_df")

    options = list(df.columns)
    if request.method == "POST":
        # get the selected options from the form
        selected_options = request.form.getlist("options")
        predictor=df.drop(columns=list(selected_options))

        update_csv_file("predictor",predictor)

        target=df[selected_options]

        update_csv_file("target",target)

        current_text=("The target(dependent) column is {} and predictor(independent) columns are {}".format(list(target.columns),list(predictor.columns)))
        if session.get('previous_text', None) != current_text:
            output_info(current_text)
            session['previous_text']=current_text
        # output_info("The target(dependent) column is {} and predictor(independent) columns are {}".format(list(target.columns),list(predictor.columns)))
        return redirect(url_for("data_splitting.select_splitting_type"))


    message=get_report_data()

    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    question="Please select the target variable!!"

    return render_template("index.html", question=question, message=message,list=False,dropdown=True,options=options,dataframe=dataframe)

@data_splitting.route("/select_splitting_type", methods=["GET", "POST"])
def select_splitting_type():
    #global df,predictor,target

    df=getting_csv("root_df")

    options = ['stratified sampling', 'random sampling']

    if request.method == "POST":
        selected_option = request.form['options']

        if selected_option == "random sampling":
            return redirect(url_for("data_splitting.random_sample_splitting"))
        
        elif selected_option == "stratified sampling":
            return redirect(url_for("data_splitting.stratified_sample_splitting"))
        
    message=get_report_data()

    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    question="Please select the method that has to be used to split the data?"
    
    return render_template("index.html", question=question, message=message,list=False,dropdown=True,options=options,dataframe=dataframe)

@data_splitting.route("/random_sample_splitting", methods=["GET", "POST"])
def random_sample_splitting():
    #global df,predictor,target,X_train, X_test, y_train, y_test

    df=getting_csv("root_df")

    predictor=getting_csv("predictor")

    target=getting_csv("target")

    options = ['70 : 30', '80 : 20']

    if request.method == "POST":
        selected_option = request.form['options']

        if selected_option == "70 : 30":

            current_text=("Random sampling is used to split the train and test data in 70 : 30 ratio")
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text
            # output_info("Random sampling is used to split the train and test data in 70 : 30 ratio")

            X_train, X_test, y_train, y_test = train_test_split(predictor,target,test_size=0.3,random_state = 10)

            #loading the X_train, X_test, y_train, y_test to the cache
            update_csv_file("X_train",X_train)

            update_csv_file("X_test",X_test)

            update_csv_file("y_train",y_train)

            update_csv_file("y_test",y_test)

            return redirect(url_for("file_download.end_download_dataset"))
        
        elif selected_option == "80 : 20":
            
            current_text=("Random sampling is used to split the train and test data in 80 : 20 ratio")
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text
            output_info("Random sampling is used to split the train and test data in 80 : 20 ratio")

            X_train, X_test, y_train, y_test = train_test_split(predictor,target,test_size=0.2,random_state = 10)

            #loading the X_train, X_test, y_train, y_test to the cache
            update_csv_file("X_train",X_train)

            update_csv_file("X_test",X_test)

            update_csv_file("y_train",y_train)

            update_csv_file("y_test",y_test)

            return redirect(url_for("file_download.end_download_dataset"))

    message=get_report_data()

    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    question="Please select the method that has to be used to split the data?"

    return render_template("index.html", question=question, message=message,list=False,dropdown=True,options=options,dataframe=dataframe)

@data_splitting.route("/stratified_sample_splitting", methods=["GET", "POST"])
def stratified_sample_splitting():
    #global df,predictor,target,X_train, X_test, y_train, y_test

    df=getting_csv("root_df")

    predictor=getting_csv("predictor")

    target=getting_csv("target")

    options = ['70 : 30', '80 : 20']

    if request.method == "POST":
        selected_option = request.form['options']

        if selected_option == "70 : 30":

            current_text=("stratified sampling is used to split the train and test data in 70 : 30 ratio")
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text
            # output_info("stratified sampling is used to split the train and test data in 70 : 30 ratio")

            X_train, X_test, y_train, y_test = train_test_split(predictor,target, test_size=0.3, random_state=0, stratify=target)

            #loading the X_train, X_test, y_train, y_test to the cache
            update_csv_file("X_train",X_train)

            update_csv_file("X_test",X_test)

            update_csv_file("y_train",y_train)

            update_csv_file("y_test",y_test)

            return redirect(url_for("file_download.end_download_dataset"))
        
        elif selected_option == "80 : 20":

            current_text=("stratified sampling is used to split the train and test data in 80 : 20 ratio")
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text
                # output_info("stratified sampling is used to split the train and test data in 80 : 20 ratio")
            
            X_train, X_test, y_train, y_test = train_test_split(predictor,target, test_size=0.2, random_state=0, stratify=target)

            #loading the X_train, X_test, y_train, y_test to the cache
            update_csv_file("X_train",X_train)

            update_csv_file("X_test",X_test)

            update_csv_file("y_train",y_train)

            update_csv_file("y_test",y_test)

            return redirect(url_for("file_download.end_download_dataset"))

    message=get_report_data()

    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    question="Please select the method that has to be used to split the data?"

    return render_template("index.html", question=question, message=message,list=False,dropdown=True,options=options,dataframe=dataframe)
