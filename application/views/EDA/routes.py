# from application import app
from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from werkzeug.utils import secure_filename
import pandas as pd
# import plotly.graph_objs as go
# import plotly.express as px
# import plotly.offline as pyo
from sklearn.preprocessing import LabelEncoder
import uuid
from datetime import datetime
from application.utils.unique_session import unique_session_id
from application.utils.report_utils import terminal


#utils import
from application.utils.report_utils import output_info, get_report_data
from application.utils.cache_utils import update_csv_file, getting_csv
from application.utils.database_utils import connect_to_database
from application.utils.logger import configure_logger


#configuring logger
logger = configure_logger()


EDA=Blueprint('EDA',__name__, static_folder='application\staticFiles')


@EDA.route("/", methods=["GET", "POST"])
def home():

    if request.method == 'POST':
        print("YEs")
        file = request.files['file']

        submit_button=request.form.get("submit_button")
        use_sample_data=request.form.get("use_sample_data_button")
        
        if submit_button=="submitted":
            if file:
                # if file.content_length > 20 * 1024 * 1024:
                #     flash('File size exceeds limit of 20 MB', 'error')
                # elif not file.filename.endswith('.csv'):
                #     flash('File must be a CSV', 'error')
                # else:
                filename = secure_filename(file.filename)
                df = pd.read_csv(file)
                already_assigned=True
                update_csv_file("root_df",df)
                flash('File uploaded successfully', 'success')

                #log
                logger.info('user uploaded the dataset')

                return redirect(url_for("EDA.initiating"))
        
        elif use_sample_data=="used-sample":
            df=pd.read_csv("application/Data/application_record.csv")
            already_assigned=True
            update_csv_file("root_df",df)

            #log
            logger.info('user used sample data')

            return redirect(url_for("EDA.initiating"))

    vare=False
    question ="can we start cooking the data?"

    try:
        if already_assigned:
            pass
    except:
        session['session_id'] = unique_session_id()
        print("-------------------------",session['session_id'])
        session['session_started_timestamp'] = str(datetime.now())


    
    return render_template("index.html", question=question, button_name="zero",list=False, upload=True,var=vare,show_welcome_popup=True)

@EDA.route("/initiating", methods=["GET", "POST"])
def initiating():

    question = "Do you want to perform data exploration?"
    message = ""

    if request.method == "POST":
        answer = request.form.get("first")
        #print("first",answer)
        if answer == "yes":

            #log
            logger.info('routing to explore - for EDA')

            return redirect(url_for("EDA.explore"))
        elif answer == "no":
            output_info("Proceeding to next step")

            #log
            logger.info('routing to preprocessing - directly without EDA')

            return redirect(url_for("data_preprocessing.preprocessing"))
        
    session["previous_text"]=" "

    info="<b>What is data exploration?</b><br>&nbsp;&nbsp&nbsp;&nbsp;Data exploration is the process of analyzing and summarizing data to gain insights into its characteristics and properties. It involves visually inspecting and manipulating the data to identify patterns, trends, and relationships between variables. Data exploration is an essential step in the data analysis process and typically involves tasks such as data cleaning, descriptive statistics, data visualization, data transformation, and hypothesis testing. The overall goal of data exploration is to build a deeper understanding of the data and its characteristics."

    df=getting_csv("root_df")

    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    print("initializing")
    
    return render_template("index.html", question=question, message=message, button_name="first",list=False,info=info,dataframe=dataframe)

@EDA.route("/explore", methods=["GET", "POST"])
def explore():

    if request.method == "POST":
        answerr = request.form.get("second")
        if answerr == "yes":

            #log
            logger.info('routing to uniquevalues - to see the indepth analysis data')

            return redirect(url_for("EDA.uniquevalues"))
        elif answerr == "no":

            #log
            logger.info('routing to preprocessing - directly without seeing uniquevalues')

            return redirect(url_for("data_preprocessing.preprocessing"))

    df=getting_csv("root_df")

    # Create an empty DataFrame
    df_columns = pd.DataFrame(columns=['Count', 'Column Name'])

    # Initialize an empty list to store data
    data = []

    # Iterate over the column names and positions using enumerate
    for i, col_name in enumerate(df.columns):
        data.append([int(i + 1), col_name])

    # Concatenate the data into df_columns
    df_columns = pd.concat([df_columns, pd.DataFrame(data, columns=['Count', 'Column Name'])], ignore_index=True)

    html_table = df_columns.to_html(index=False, header=True, table_id="column_initial_table")


    ##global numerical,categorical
    categorical=list(df.select_dtypes(['object','bool']).columns)
    numerical=list(df.select_dtypes(['int64','float64']).columns)

    #For distinguish numerical and categorical columns
    temp_col=[]
    for i in numerical:
        if len(df[i].unique()) < 3:
            temp_col.append(i)
    categorical.extend(temp_col)
    numerical = [i for i in numerical if i not in temp_col]

    if len(categorical)!=len(numerical):
        diff=abs((len(categorical)) - (len(numerical)))
        if len(categorical) == (min(len(i) for i in [categorical, numerical])):
            for i in range(1,diff+1):
                categorical.append(" ")
        elif len(numerical) == (min(len(i) for i in [categorical, numerical])):
            for i in range(1,diff+1):
                numerical.append(" ")
    
    nested_list = [[x, y] for x, y in zip(categorical, numerical)]

    df_seperate = pd.DataFrame(nested_list, columns=['categorical Columns', 'Numerical Columns'])
    
    html_table_seperate = df_seperate.to_html(index=False,header="true", table_id="column_seperate_table")


    current_text_list=[terminal+("The shape of the given dataset {}".format(str(df.shape))),
                       terminal+("The dataset has {} rows and {} columns".format(df.shape[0], df.shape[1])),
                       terminal+(("These are the {} columns present in the dataset".format(str(df.shape[1])))),
                       (html_table),
                       terminal+("There are {} categorical columns and {} numerical columns".format(str(len(categorical)),str(len(numerical)))),
                       (html_table_seperate)]
    
    current_text="<br><br>".join(current_text_list)
    
    #Here the previous input that has been stored to db is stored to session and checked whether the data is already stored or not to avoid duplicate
    if session.get('previous_text', None) != current_text:
        output_info(current_text)
        session['previous_text']=current_text

    
    # output_info("The shape of the given dataset {}".format(str(df.shape)))
    # output_info("The dataset has {} rows and {} columns".format(df.shape[0], df.shape[1]))
    # output_info(("These are the {} columns present in the dataset".format(str(df.shape[1]))))
    # output_info(html_table)
    # output_info("There are {} categorical columns and {} numerical columns".format(str(len(categorical)),str(len(numerical))))
    # output_info(html_table_seperate)

    question = "Want to analyse values in categorical column and numerical columns?"

    message=get_report_data()

    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    #assigning the session variables which can be used for next route
    
    session["categorical"]=categorical
    session["numerical"]=numerical

    return render_template("index.html", question=question, message=message, button_name="second",list=False,dataframe=dataframe)



@EDA.route("/uniquevalues", methods=["GET", "POST"])
def uniquevalues():
    #global numerical_li

    if request.method == "POST":
        answerr = request.form.get("third")
        if answerr == "yes":

            #log
            logger.info('routing to preprocessing_process - to preprocess the data after full EDA')

            return redirect(url_for("data_preprocessing.preprocessing_process"))
        elif answerr == "no":

            #log
            logger.info('routing to direct_splitting_data - directly without preprocessing')

            return redirect(url_for("data_splitting.direct_splitting_data"))

    #getting the assignes session variables
    categorical=session["categorical"]
    numerical=session["numerical"]

    df=getting_csv("root_df")

    print("-------------------------------------------------------num & cat columns--------------------")

    #Removing empty string in the list
    categorical_li = [item for item in categorical if item != " "]
    numerical_li = [item for item in numerical if item != " "]

    session["numerical_li"]=numerical_li

    plot_divs = []


    # for col in categorical_li:
    #     unique_vals = df[col].value_counts()
    #     values = unique_vals.values.tolist()
    #     total = sum(values)
    #     percentages = [f"{(val/total)*100:.2f}%" for val in values]
    #     hover_text = [f"{val} ({perc})" for val, perc in zip(values, percentages)]
    #     trace = go.Bar(
    #         x=unique_vals.index.tolist(),
    #         y=unique_vals.values.tolist(),
    #         marker=dict(color=px.colors.qualitative.Pastel),
    #         hovertext=hover_text,
    #         hoverinfo='text'
    #     )
    #     layout = go.Layout(
    #         title=f"{col}",
    #         xaxis=dict(title="Value"),
    #         yaxis=dict(title="Count")
    #     )
    #     fig = go.Figure(data=[trace], layout=layout)
    #     plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div')
    #     plot_divs.append(plot_div)

    # create a list of HTML divs, each containing a plot_div for a categorical column
    divs = []
        
    divs.append('<div class="chart-grid">')
    for plot_div in plot_divs:
        divs.append(f'<div class="chart-cell">{plot_div}</div>')
    divs.append('</div>')
        
    # create a single HTML string by concatenating the HTML divs
    html = ''.join(divs)


    # create a list of HTML divs, each containing a plot_div for a categorical column
    divs = []
    
    divs.append('<div class="chart-grid">')
    for plot_div in plot_divs:
        divs.append(f'<div class="chart-cell">{plot_div}</div>')
    divs.append('</div>')

    # divs.append('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>')
    #create a single HTML string by concatenating the HTML divs
    html = ''.join(divs)

    #output_info(html)
    statistical_analysis=(df[(numerical_li)].describe())

    current_text=(statistical_analysis.to_html(header="true", table_id="table"))

    #Here the previous input that has been stored to db is stored to session and checked whether the data is already stored or not to avoid duplicate
    if session.get('previous_text', None) != current_text:
        output_info(current_text)
        session['previous_text']=current_text

    question="do you want to perform preprocessing?"

    # c.execute("SELECT report_data FROM output_string WHERE session_id=%s", (session['session_id'],))
    # result = c.fetchone()
    # if result:
    #     message = result[0]

    message=get_report_data()

    dataframe=(df.head()).to_html(header="true", table_id="df_table")

    return render_template("index.html", question=question, message=message, button_name="third",list=False,dataframe=dataframe)