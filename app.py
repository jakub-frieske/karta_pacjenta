from flask import Flask, render_template, url_for, request, get_template_attribute,jsonify, redirect, flash
from backend.data.Patient import *
from backend.data.PatientsData import PatientsData
from backend.FHIR_api import FHIRApi
from backend.chart import PatientChart, PatientsChart
import plotly
import json
import plotly.graph_objects as go


app = Flask(__name__)
app.config['SECRET_KEY'] = "some_random"


all_patients= None
all_patients_chart= None

@app.template_filter()
def datetime(value):
    return value[:16].replace('T',' ') #dt.datetime.strptime(value[:16],'%Y-%m-%dT%H:%M')

@app.template_filter()
def history_len(value):
    print(len(value))
    return len(value) #dt.datetime.strptime(value[:16],'%Y-%m-%dT%H:%M')

@app.route('/patient/<id>', methods=['GET','POST'])
def patient_history(id):
    global all_patients_chart
    patient = all_patients.get_patient(id)
    if request.method == 'POST':
        start = request.form['input_from']
        end = request.form['input_to']
        data = patient.get_history_in_range(start,end)

        return render_template('patient.html', patient=patient, data=data, input_data={'from':start, 'to':end })
    today = dt.date.today() - dt.timedelta(days=1)
    input_data = {
        'from': patient.birthday,
        'to': f"{today}"
    }
    data = patient.get_history_in_range(input_data['from'],input_data['to'])
    all_patients_chart.add_patient_chart(PatientChart(id,patient.get_data()))

    return render_template('patient.html', patient=patient, data=data, input_data=input_data)

@app.route('/')
def home():
    data = backend()
    headings = ('Imię','Nazwisko','Płeć','Data urodzenia','Identyfikator')

    return render_template('index.html', headings=headings, data=data)



@app.route('/patient/<id>/chart')
def patient_chart(id):
    data = all_patients_chart.get_patient_data_by_id(id)

    # Create figure
    fig = go.Figure()
    dropdown= []
    count = 0
    rangeselector=dict(
                buttons=list([
                    dict(count=2, label="2d", step="day", stepmode="backward"),
                    dict(count=14, label="2w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]),
                x=0.8
            )
    # Add Traces
    for name in data:
        if 'data' in data[name]:
            for line in data[name]['data']:
                fig.add_trace(go.Scatter(x=line['dates'],
                                         y=line['values'],
                                         name=line['name'],
                                         visible=False if count else True))
                count+=1

        else:
            line = data[name]
            fig.add_trace(go.Scatter(x=line['dates'],
                                     y=line['values'],
                                     name=name,
                                     visible=False if count else True))
            count+=1

    i=0
    unit=''
    for name in data:
        visiable = [False]*count
        if 'data' in data[name]:
            for line in data[name]['data']:
                visiable[i] = True
                i+=1
            elem = dict(label=name,
                        method='update',
                        args=[ {'visible': visiable},
                               {'xaxis': {'title': 'Date', 'rangeselector':rangeselector},
                                'yaxis': {'title':line['unit']}  }]
                        )
            dropdown.append(elem)
        else:
            line = data[name]
            visiable[i] = True
            i+=1
            elem = dict(label=name,
                        method='update',
                        args=[{'visible': visiable},
                              {'xaxis': {'title': 'Date', 'rangeselector':rangeselector},
                               'yaxis': {'title':line['unit']} }]
                        )
            dropdown.append(elem)
        if i==1:
            unit=line['unit']


    fig.update_layout(
        xaxis = dict(rangeselector=rangeselector, title='Date'),
        yaxis = dict(title=unit),
        updatemenus=[go.layout.Updatemenu(
            active=0,
            x=0,
            y=1.15,
            xanchor='left',
            yanchor='top',
            buttons=dropdown)]
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('chart.html', graphJSON=graphJSON)


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        data_id = request.form.get('id')
        patient = all_patients.get_patient(request.form.get('patient'))

        name = request.form['name']

        if request.form.get('type') == 'medication':
            patient.set_medication_name(data_id, name)

        if request.form.get('type') == 'value':
            value = request.form['value']
            patient.set_observation_name_val(data_id, name,value)
        if request.form.get('type') == 'values':
            value=None
            patient.set_observation_name_val(data_id, name,value)

        flash("Updated Successfully")


        # patient.medications.append(
        #     {
        #         'id': 'idc',
        #         'name': 'medication[medicationCodeableConcept].coding[0].display',
        #         'date':  dt.datetime.now().strftime("%Y-%m-%d"),
        #         'type': "medication"
        #     }
        # )
        # .append(history('','',"elo"))
        return redirect(request.referrer)

@app.route('/edit_history', methods=['GET', 'POST'])
def edit_history():
    if request.method == 'POST':
        data_id =  request.form.get('row_id')
        pat = request.form.get('patient')
        patient = all_patients.get_patient(pat)
        data = patient.get_edit_history(data_id)
        print(data[0].id, data[0].before)
        return jsonify({"row_id": "id: " +data_id,"htmlresponse": render_template('response_history.html', data=data)})

@app.errorhandler(500)
def internal_error(error):
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found(error):
    return redirect(url_for('home'))

def backend():
    global all_patients, all_patients_chart
    api = FHIRApi()
    patients_resource = api.get_patients()

    patient_list=[]
    for patient_data in patients_resource:
        patient_list.append(Patient(api,patient_data))

    print("loaded", len(patient_list), "patients")

    all_patients = PatientsData(patient_list)
    all_patients_chart = PatientsChart()

    return all_patients.get_all_patients()

if __name__ == '__main__':
    app.run(debug=True)

