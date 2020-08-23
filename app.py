from flask import Flask, render_template, request, redirect
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from werkzeug.utils import secure_filename
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json
import matplotlib
import datetime
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import calendar

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["ALLOWED_FILE_EXTENSIONS"] = ["XLSX"]

nav = Nav()

@nav.navigation()
def mynavbar():
    return Navbar(
        'mysite',
        View('Home','Uploder', 'index'),
    )

nav.init_app(app)


def uploaded_file():
   global df
   if request.method == 'POST':
      f = request.files['file']
      days = request.form['days']
      frequency = request.form['freq']
      if( frequency == 'Daily'):
       fr = 'D'
      elif( frequency == 'Monthly'):
       fr = 'M'
      elif( frequency == 'Weekly'):
       fr = 'W'
      else:
       fr = 'H'


      if allowed_image(f.filename):
                filename = secure_filename(f.filename)

                #image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                f.save(secure_filename(f.filename))
                print("Image saved")

                return redirect(request.url)

      else:
                print("That file extension is not allowed")
                return redirect(request.url)



     # f.save(secure_filename(f.filename))
      df = pd.read_excel(secure_filename(f.filename))

      return df


def allowed_image(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False

def create_plot():


    df = pd.read_excel('inci.xlsx')


    fig = go.Figure(go.Scatter(
            x=df['Date'], # assign x as the dataframe column 'x'
            y=df['Incidents']
        ))

    fig.update_xaxes(
    rangeslider_visible=True
     )

    fig.update_layout(
    title={
        'text': "Time Series"
        })


    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def create_yearly_plot():
    df = pd.read_excel('inci.xlsx')
    df_monthly = df.resample('M', on='Date').sum().reset_index().sort_values(by='Date')
    df_yearly = df.resample('Y', on='Date').sum().reset_index().sort_values(by='Date')
    df_monthly['Year'] = pd.DatetimeIndex(df_monthly['Date']).year
    df_monthly['Month'] = pd.DatetimeIndex(df_monthly['Date']).month
    df_monthly['Month'] = df_monthly['Month'].apply(lambda x: calendar.month_abbr[x])
    df_yearly['Year'] = pd.DatetimeIndex(df_yearly['Date']).year

    colors = ['yellow','orange','red']
    
    fig = go.Figure(go.Bar(
            x=df_yearly['Incidents'],
            y=df_yearly['Year'],
            orientation='h',
            width = 0.3,
            marker_color=colors
            ))
    fig.update_layout(
    title={
        'text': "Yearly Comparision"
        },

    yaxis = dict(
        tickmode = 'linear',
        dtick = 1
    ))


    ygraphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
     
    return ygraphJSON

def create_monthly_plot():
    df = pd.read_excel('inci.xlsx')
    df_monthly = df.resample('M', on='Date').sum().reset_index().sort_values(by='Date')
    df_monthly['Year'] = pd.DatetimeIndex(df_monthly['Date']).year
    df_monthly['Month'] = pd.DatetimeIndex(df_monthly['Date']).month
    df_monthly['Month'] = df_monthly['Month'].apply(lambda x: calendar.month_abbr[x])
    grouped = df_monthly.groupby(df_monthly.Year)    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    df2= df_monthly.groupby(['Year','Month']).size().unstack(fill_value=0).stack()
    x_uni=df_monthly['Year'].unique()
    y_uni=df_monthly['Month'].unique()

    fig = go.Figure()

    for i in range(len(x_uni)):
          datalist=[]
          for j in range(len(y_uni)):   
              filterinfDataframe = df_monthly[(df_monthly['Month'] == y_uni[j]) & (df_monthly['Year'] == x_uni[i])]
              if filterinfDataframe.empty:
                datalist.append(0)
              else:
                datalist.append(filterinfDataframe.Incidents.iloc[0])        
          fig.add_trace(go.Bar(    
          y=datalist,
          x=y_uni,
          visible=True,
          name=str(x_uni[i])
            )) 
    fig.update_layout(barmode='group', title="Monthly Comparision")

    mgraphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return mgraphJSON


def plot_try():
    df = pd.read_excel('inci.xlsx')
    fig = go.Figure(go.Table(
        header=dict(
            values=["Date","Incidents"],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df[k].tolist() for k in df.columns[0:]],
            align = "left")
    ))
    fig.update_layout(
    showlegend=False,
    title_text="Daily Incident count",
    )
     
    pgraphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return pgraphJSON

 
    
     

def create_stat():
    
    df = pd.read_excel('inci.xlsx')

    mean = int(df['Incidents'].mean())
    total = df['Incidents'].sum()
  
    df_weekly = df.resample('W-Sun', on='Date').sum().reset_index().sort_values(by='Date')

    df_weekly = pd.DataFrame(df_weekly).set_index('Date')
    df_daily = pd.DataFrame(df).set_index('Date')

    today = datetime.date.today()
    #last_monday = today - datetime.timedelta(days=today.weekday())
    next_sunday = today + datetime.timedelta(days=-today.weekday()-1, weeks=1)
    #last_monday = str(last_monday)
    next_sunday = str(next_sunday)
    today = str(today)
    

    last_week = df_weekly.tail(1)
    last = str(last_week.iloc[0])
    data_week = last.split(' ')[5]

    last_day = df_daily.tail(1)
    last_data_day = str(last_day.iloc[0])
    data_day = last_data_day.split(' ')[5]


    if ( data_week == next_sunday ):
      oc_weekly = last_week.iloc[0]['Incidents']
    else:
      oc_weekly = "NA"

    if ( data_day == today ):
      oc_today = last_day.iloc[0]['Incidents']
    else:
      oc_today = "NA"


    df_weekly['Trend'] = df_weekly.Incidents > df_weekly.Incidents.shift()
    df_weekly['Trend']= df_weekly.Trend.astype(str)
    df_weekly['Trend'] = df_weekly['Trend'].replace(['False','True'],['down','up'])
 

    if ( data_week == today ):
     wtrend = df_weekly.iloc[-1]['Trend']
    else:
     wtrend = df_weekly.iloc[-2]['Trend']
  

    return (mean,total,oc_weekly,oc_today,wtrend)



@app.route('/home', methods = ['GET', 'POST'])
def home() :
        return render_template('home.html')

@app.route('/login')
def login():
   return render_template('login.html')


@app.route('/upload')
def upload_file():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def index():
#    df  = uploaded_file()
    bar = create_plot()
    mbar = create_monthly_plot()
    ybar = create_yearly_plot()
    stat = create_stat()
    table= plot_try()
    return render_template('uploaded.html', plot=bar, mean=stat[0], total=stat[1], weekly=stat[2], today=stat[3], yplot=ybar, mplot=mbar, wtrend=stat[4],mtrend="down",table=table)


app.run(debug=True,host = '0.0.0.0')

