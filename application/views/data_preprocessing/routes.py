# from application import app
from flask import Flask, render_template, request, make_response, redirect, url_for, flash, session, Blueprint
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

from datetime import datetime



#utils import
from application.utils.report_utils import output_info, get_report_data
from application.utils.cache_utils import update_csv_file, getting_csv, view_cache, clear_inactive_cache, clear_inactive_cache_immediate
from application.utils.database_utils import connect_to_database
from application.utils.logger import configure_logger

#configuring logger
logger = configure_logger()

data_preprocessing=Blueprint('data_preprocessing',__name__, static_folder='application\staticFiles')

@data_preprocessing.route("/preprocessing", methods=["GET", "POST"])
def preprocessing():

    if request.method == "POST":
        answerr = request.form.get("temp_third")
        if answerr == "yes":

            #log
            logger.info('routing to preprocessing_process - to preprocess the data')

            return redirect(url_for("data_preprocessing.preprocessing_process"))
        elif answerr == "no":

            #log
            logger.info('routing to direct_splitting_data - directly without preprocessing the data')

            return redirect(url_for("data_splitting.direct_splitting_data"))

    message=get_report_data()

    #getting the stored df from database
    df=getting_csv("root_df")

    question="do you want perform preprocessing?"
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    return render_template("index.html", question=question, message=message, button_name="temp_third",list=False,dataframe=dataframe)

@data_preprocessing.route("/preprocessing_process", methods=["GET", "POST"])
def preprocessing_process():

    if request.method == "POST":
        answerr = request.form.get("forth")
        if answerr == "yes":

            #log
            logger.info('routing to null_values')

            return redirect(url_for("data_preprocessing.null_values"))
        elif answerr == "no":

            #log
            logger.info('routing to duplicate - directly without treating the null values')


            return redirect(url_for("data_preprocessing.duplicate"))

     
    current_text="Preprocessing is on the process"

    #Here the previous input that has been stored to db is stored to session and checked whether the data is already stored or not to avoid duplicate
    if session.get('previous_text', None) != current_text:
        output_info(current_text)
        session['previous_text']=current_text

    message=get_report_data()

    #getting the stored df from database
    print("the csv is retrived for the preprocessing route")
    df=getting_csv("root_df")

    question="do you want treat null values?"
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    return render_template("index.html", question=question, message=message, button_name="forth",list=False,dataframe=dataframe)


@data_preprocessing.route("/null_values", methods=["GET", "POST"])
def null_values():

    #getting the stored df from database
    df=getting_csv("root_df")

    #checking whether any columns has more number of null values
    dic_columns_with_more_null_values={}
    for i in list(df.columns):
        if ((df[i].isnull().sum())/len(df)) >= 0.2:
            dic_columns_with_more_null_values[str(i)]=((df[i].isnull().sum())/len(df))

    #if there is any column with more then 20% of null values when compared to total length of data this condition will be executed
    if len(dic_columns_with_more_null_values)>0:
        #global null_value_columns
        null_value_columns=list(dic_columns_with_more_null_values.keys())

        session["null_value_columns"]=null_value_columns

        suggestion=("SUGGESTION :You would have noticed that {} these columns contains more than 20% of null values. So, it is better to dropping these column which has more null values".format(list(dic_columns_with_more_null_values.keys())))
        question="Do you want to remove these columns to avoid data loss"

        #wait for user response for whether user wants to remove the column that has more null values 
        if request.method == "POST":
            answerr = request.form.get("fifth")

            #if yes redirect to route that removes the columns
            if answerr == "yes":

                #log
                logger.info('routing to drop_null_columns - to remove columns with more null values')

                return redirect(url_for("data_preprocessing.drop_null_columns"))
            elif answerr == "no":

                #log
                logger.info('routing to drop_null_values - to drop null values')


                return redirect(url_for("data_preprocessing.drop_null_values"))


    else:
        question="Do you want to drop these null value rows"
        suggestion=" "

        if request.method == "POST":
            answerr = request.form.get("fifth")
            if answerr == "yes":

                #log
                logger.info('routing to drop_null_values - to drop the null values')

                return redirect(url_for("data_preprocessing.drop_null_values"))
            elif answerr == "no":

                #log
                logger.info('routing to duplicate - to remove the duplicate values')

                return redirect(url_for("data_preprocessing.duplicate"))


    # output_info("These are the sum of null values in each columns of dataset")
    null_df = pd.DataFrame({'columns': (df.isnull().sum()).index, 'number of null values': (df.isnull().sum()).values})
    # output_info(null_df.to_html(header="true", table_id="null_value_table"))

    current_text_list=[("These are the sum of null values in each columns of dataset"),(null_df.to_html(header="true", table_id="null_value_table"))]
    current_text="<br><br>".join(current_text_list)
    
    if session.get('previous_text', None) != current_text:
        output_info(current_text)
        session['previous_text']=current_text

    message=get_report_data()
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    return render_template("index.html", question=question, message=message, button_name="fifth",suggestion=suggestion,list=False,dataframe=dataframe)

@data_preprocessing.route("/drop_null_columns", methods=["GET", "POST"])
def drop_null_columns():

    #getting the stored df from database
    df=getting_csv("root_df")

    null_value_columns=session['null_value_columns']

    options = null_value_columns
    options.append("None_of_these")
    if request.method == "POST":
        # get the selected options from the form
        selected_options = request.form.getlist("options")
        
        #check if user selected none of these columns
        if "None_of_these" in selected_options:
            update_csv_file("root_df",df)

            #log
            logger.info('routing to drop_null_values - to drop the null values')

            return redirect(url_for("data_preprocessing.drop_null_values"))
        else:
            df = df.drop(selected_options, axis=1)
            current_text=("{} columns has be droped from the dataset".format(selected_options))
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text
            # output_info("{} columns has be droped from the dataset".format(selected_options))
            update_csv_file("root_df",df)

            #log
            logger.info('routing to drop_null_values - to drop the null values after droping the columns with more null values')

            return redirect(url_for("data_preprocessing.drop_null_values"))

    question="Which of these columns would you like to drop?"

    message=get_report_data()
    dataframe=(df.head()).to_html(header="true", table_id="df_table")


    return render_template("index.html", question=question, message=message,list=True,options=options,dataframe=dataframe)

@data_preprocessing.route("/drop_null_values", methods=["GET", "POST"])
def drop_null_values():
    #global df

    #getting the stored df from database
    df=getting_csv("root_df")

    if request.method == "POST":
        answerr = request.form.get("sixth")
        if answerr == "yes":
            df = (df.dropna())

            current_text=("In total {} rows has been dropped".format((str(df.isnull().values.sum()))))
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text
            # output_info("In total {} rows has been dropped".format((str(df.isnull().values.sum()))))

            #log
            logger.info('routing to duplicate - to drop the duplicate values after removing null values')

            return redirect(url_for("data_preprocessing.duplicate"))
        elif answerr == "no":

            #log
            logger.info('routing to duplicate - to drop the duplicate values without removing the null values')

            return redirect(url_for("data_preprocessing.duplicate"))

    message=get_report_data()

    question="Do you want to remove null values"
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    update_csv_file("root_df",df)

    return render_template("index.html", question=question, message=message,list=False,button_name="sixth",dataframe=dataframe)

@data_preprocessing.route("/duplicate", methods=["GET", "POST"])
def duplicate():
    #global df
    # =======================================================================================================================================================================================================
    #getting the stored df from database
    df=getting_csv("root_df")

    if request.method == "POST":
        answerr = request.form.get("seventh")
        if answerr == "yes":
            temp2=str("The dataset has {} duplicate rows".format((df.duplicated().sum())))
            # output_info(temp2)

            current_text=(temp2)
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text

            #log
            logger.info('routing to drop_duplicate_rows - to drop the duplicate rows')
            
            return redirect(url_for("data_preprocessing.drop_duplicate_rows"))
        elif answerr == "no":

            #log
            logger.info('routing to outliers - to treat the outliers without removing the duplicate rows')

            return redirect(url_for("data_preprocessing.outliers"))


    message=get_report_data()

    question="Do you want to treat duplicate rows in the dataset?"
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    update_csv_file("root_df",df)

    return render_template("index.html", question=question, message=message,list=False,button_name="seventh",dataframe=dataframe)

@data_preprocessing.route("/drop_duplicate_rows", methods=["GET", "POST"])
def drop_duplicate_rows():
    df=getting_csv("root_df")

    columns_with_more_unique_values=[]
    for i in list(df.columns):
        if (df[i].nunique()/len(df)) > 0.8:
            columns_with_more_unique_values.append(i)
    print(columns_with_more_unique_values)
    session["columns_with_more_unique_values"]=columns_with_more_unique_values

    if len(columns_with_more_unique_values) > 0:
        suggestion=("SUGGESTION : Sometime the dataset will have column which has more unique value such as customer number or application number etc. which will make every column as unique column even if other important features are same. Here the {} has more unique values so it is suggested to drop these kind of columns".format(columns_with_more_unique_values))
        question="Do you want to drop these columns?"
        if request.method == "POST":
            answerr = request.form.get("eigth")
            if answerr == "yes":

                #log
                logger.info('routing to drop_columns_of_more_unique_values - to drop the columns with more unique values')

                return redirect(url_for("data_preprocessing.drop_columns_of_more_unique_values"))
            elif answerr == "no":

                #log
                logger.info('routing to drop_duplicate_rows_values - to drop duplicate rows without removing the columns with more unique values')

                return redirect(url_for("data_preprocessing.drop_duplicate_rows_values"))

    else:
        question="Do you want to drop the duplicate rows?"
        if int(df.duplicated().sum())!=0:
            suggestion=("SUGGESTION : The dataset has {} number of duplicates so it is advised to remove the duplicates".format(str(df.duplicated().sum())))
        if request.method == "POST":
            answerr = request.form.get("eigth")
            if answerr == "yes":
                current_text=("{} number of duplicate rows has been removed".format(str(df.duplicated().sum())))
                if session.get('previous_text', None) != current_text:
                    output_info(current_text)
                    session['previous_text']=current_text
                # output_info("{} number of duplicate rows has been removed".format(str(df.duplicated().sum())))
                df=df.drop_duplicates()

                #log
                logger.info('routing to outliers - to treat the outliers after removing duplicate rows')

                return redirect(url_for("data_preprocessing.outliers"))
            elif answerr == "no":

                #log
                logger.info('routing to outliers - to treat the outliers without removing the duplicate rows')

                return redirect(url_for("data_preprocessing.outliers"))

    message=get_report_data()
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    update_csv_file("root_df",df)

    return render_template("index.html", question=question, message=message,list=False,button_name="eigth",suggestion=suggestion,dataframe=dataframe)

@data_preprocessing.route("/drop_columns_of_more_unique_values", methods=["GET", "POST"])
def drop_columns_of_more_unique_values():
    df=getting_csv("root_df")
    options = session["columns_with_more_unique_values"]
    options.append("None_of_these")

    if request.method == "POST":
        # get the selected options from the form
        selected_options = request.form.getlist("options")
        
        #check if user selected none of these columns
        if "None_of_these" in selected_options:

            #log
            logger.info('routing to drop_duplicate_rows_values - to drop the duplicate rows')

            return redirect(url_for("data_preprocessing.drop_duplicate_rows_values"))
        else:
            df = df.drop(selected_options, axis=1)
            
            current_text=("{} columns has be droped from the dataset".format(selected_options))
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text
            # output_info("{} columns has be droped from the dataset".format(selected_options))

            #log
            logger.info('routing to drop_duplicate_rows_values - to drop the duplicate rows')

            return redirect(url_for("data_preprocessing.drop_duplicate_rows_values"))

    question="Which of these columns would you like to drop?"

    message=get_report_data()
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    update_csv_file("root_df",df)

    return render_template("index.html", question=question, message=message,list=True,options=options,dataframe=dataframe)

@data_preprocessing.route("/drop_duplicate_rows_values", methods=["GET", "POST"])
def drop_duplicate_rows_values():
    df=getting_csv("root_df")

    if request.method == "POST":
        answerr = request.form.get("ninth")
        if answerr == "yes":
            
            current_text=("{} number of duplicate rows has been removed".format(str(df.duplicated().sum())))
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text
            # output_info("{} number of duplicate rows has been removed".format(str(df.duplicated().sum())))
            df=df.drop_duplicates()

            #log
            logger.info('routing to outliers - to treat the outliers after removing the duplicate rows')


            return redirect(url_for("data_preprocessing.outliers"))
        elif answerr == "no":

            #log
            logger.info('routing to outliers - to drop the columns with more unique values')


            return redirect(url_for("data_preprocessing.outliers"))
        
    df=df.drop_duplicates()

    current_text=("The duplicate rows has been removed")
    if session.get('previous_text', None) != current_text:
        output_info(current_text)
        session['previous_text']=current_text


    # output_info("The duplicate rows has been removed")

    question="Do you want to drop the duplicate rows?"

    message=get_report_data()
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    update_csv_file("root_df",df)

    return render_template("index.html", question=question, message=message,list=False,button_name="ninth",dataframe=dataframe)

@data_preprocessing.route("/outliers", methods=["GET", "POST"])
def outliers():

    df=getting_csv("root_df")

    if request.method == "POST":
        answerr = request.form.get("temp_ninth")
        if answerr == "yes":
            return redirect(url_for("data_preprocessing.remove_outliers"))
        elif answerr == "no":
            return redirect(url_for("data_preprocessing.encoding"))


    question="do you want to treat outliers?"

    message=get_report_data()
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    update_csv_file("root_df",df)

    return render_template("index.html", question=question, message=message,list=False,button_name="temp_ninth",dataframe=dataframe)

@data_preprocessing.route("/remove_outliers", methods=["GET", "POST"])
def remove_outliers():
    #global df,numerical_columns
    
    numerical_li=session["numerical_li"]

    df=getting_csv("root_df")

    temp_dataset=df
    numerical_columns=list(set(list(temp_dataset.columns)).intersection(numerical_li))
    for x in numerical_columns:
        q75,q25 = np.percentile(temp_dataset.loc[:,x],[75,25])
        intr_qr = q75-q25
        max = q75+(1.5*intr_qr)
        min = q25-(1.5*intr_qr)
        
        temp_dataset.loc[temp_dataset[x] < min,x] = np.nan
        temp_dataset.loc[temp_dataset[x] > max,x] = np.nan

    if request.method == "POST":
        answerr = request.form.get("tenth")
        if answerr == "yes":
            
            current_text=("In total {} rows has been dropped to remove outliers".format((str(df.isnull().values.sum()))))
            if session.get('previous_text', None) != current_text:
                output_info(current_text)
                session['previous_text']=current_text
                # output_info("In total {} rows has been dropped to remove outliers".format((str(df.isnull().values.sum()))))
            
            df = (temp_dataset.dropna())
            return redirect(url_for("data_preprocessing.encoding"))
        elif answerr == "no":
            return redirect(url_for("data_preprocessing.encoding"))
    
    outliers_df = pd.DataFrame({'columns': (temp_dataset.isnull().sum()).index, 'number of outliers': (temp_dataset.isnull().sum()).values})
    
    current_text=(outliers_df.to_html(header="true", table_id="outliers_table"))
    if session.get('previous_text', None) != current_text:
        output_info(current_text)
        session['previous_text']=current_text
    
    # output_info(outliers_df.to_html(header="true", table_id="outliers_table"))

    message=get_report_data()
    question="Do you want to remove those outliers?"
    dataframe=(df.head()).to_html(header="true", table_id="df_table")



    return render_template("index.html", question=question, message=message,list=False,button_name="tenth",dataframe=dataframe)

@data_preprocessing.route("/encoding", methods=["GET", "POST"])
def encoding():
    #global df,cat_columns

    df=getting_csv("root_df")

    if request.method == "POST":
        answerr = request.form.get("eleventh")
        if answerr == "yes":
            return redirect(url_for("data_preprocessing.perform_encoding"))
        elif answerr == "no":
            return redirect(url_for("data_splitting.direct_splitting_data"))

    cat_columns = list(df.select_dtypes(['object','bool']).columns)

    session["cat_columns"]=cat_columns

    if len(cat_columns) > 0:
        suggestion=("the dataset contains {} categrioal data columns which has to be encoded into numerical value".format(str(cat_columns)))
    else:
        suggestion=" "
    
    message=get_report_data()

    question="Do you want to perform encoding"
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    return render_template("index.html", question=question, message=message,list=False,button_name="eleventh",suggestion=suggestion,dataframe=dataframe)

@data_preprocessing.route("/perform_encoding", methods=["GET", "POST"])
def perform_encoding():

    df=getting_csv("root_df")

    cat_columns=session["cat_columns"]

    #global df,numerical_columns

    if request.method == "POST":
        answerr = request.form.get("twelth")
        if answerr == "yes":
            return redirect(url_for("data_splitting.splitting_data"))
        elif answerr == "no":
            return redirect(url_for("file_download.end_download_dataset"))

    for col in cat_columns:
        globals()['LE_{}'.format(col)] = LabelEncoder()
        df[col] = globals()['LE_{}'.format(col)].fit_transform(df[col])
    
    current_text=("These {} column has been encoded using Label encoding".format(cat_columns))
    if session.get('previous_text', None) != current_text:
        output_info(current_text)
        session['previous_text']=current_text
    # output_info("These {} column has been encoded using Label encoding".format(cat_columns))

    message=get_report_data()

    question="Do you want to split the dataset into train and test?"
    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    return render_template("index.html", question=question, message=message,list=False,button_name="twelth",dataframe=dataframe)
