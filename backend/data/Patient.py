import datetime as dt
from ..history import history
STRFORMAT = "%Y-%m-%d"

class Patient:
    def __init__(self, api, patient):
        self.api = api
        self.id = patient['id']
        self.name = patient['name'][0].given[0]
        self.surname = patient['name'][0].family
        self.gender = patient['gender']
        self.birthday = patient['birthDate']
        self.identifier = patient["identifier"][0].value

        self.observations = []
        self.medications = []
        self.history={}


    def show_info(self):
        print(self.id ,
        self.name ,
        self.surname ,
        self.gender ,
        self.birthDate ,
        self.identifier )

    def show_medication(self):
        for med in self.medications:
            print(med)

    def show_observations(self):
        for obs in self.observations:
            print(obs)

    def update_observation(self):
        observations = self.api.get_observations_by_id(self.id)
        num_observation= self.get_observation_count()

        if num_observation != len(observations):
            for observation in observations:
                data ={
                    'id': observation['id'],
                    'name': observation['code'].coding[0].display,
                    'category': observation['category'][0].coding[0].display,
                    'date': observation['effectiveDateTime'],
                    'type': "Brak info"
                }

                if 'valueQuantity' in observation.keys():
                    data['type'] = "value"
                    data['value'] = observation['valueQuantity'].value
                    data['unit'] = observation['valueQuantity'].unit
                elif 'component' in observation.keys():
                    data['type'] = "values"

                    data['values'] = []
                    # data['unit'] = []
                    # data['names'] = []
                    for com in observation['component']:
                        data_helper = {
                            'name': com['code'].coding[0].display,
                            'value': com['valueQuantity'].value,
                            'unit': com['valueQuantity'].unit
                        }
                        # data['names'].append(com['code'].coding[0].display)
                        # data['value'].append(com['valueQuantity'].value)
                        # data['unit'].append(com['valueQuantity'].unit)

                        data['values'].append(data_helper)

                self.observations.append(data)
        self.observations = sorted(self.observations, key= lambda k: k['date'], reverse=True)

    def update_medications(self):
        medications = self.api.get_medications_by_id(self.id)
        num_medications = self.get_medications_count()

        if num_medications != len(medications):
            for medication in medications:
                data = {
                    'id': medication['id'],
                    'name': medication['medicationCodeableConcept'].coding[0].display,
                    'date': medication['authoredOn'],
                    'type': "medication"
                }
                self.medications.append(data)
        self.medications = sorted(self.medications, key= lambda k: k['date'], reverse=True)


    def get_history_in_range(self, start_date, end_date):
        start_date = dt.datetime.strptime(start_date,STRFORMAT)
        end_date = dt.datetime.strptime(end_date,STRFORMAT)

        patient_history = self.observations + self.medications
        patient_history = sorted(patient_history, key=lambda k: k['date'], reverse=True)

        history = []
        for post in patient_history:
            if start_date <= dt.datetime.strptime(post['date'][:10],STRFORMAT) <= end_date:
                history.append(post)

        return history

    def get_observation_count(self):
        return len(self.observations)

    def get_medications_count(self):
        return len(self.medications)

    def set_surname(self, surname):
        self.surname = surname
        self.api.update('Observation',surname)

    def set_medication_name(self, med_id, med_name):
        for med in self.medications:
            if med['id'] == med_id:
                date_now = dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if med_id not in self.history.keys():
                    med['history']=[]
                if med_id not in self.history.keys():
                    self.history[med_id]=[]
                new=history(med_id,date_now,med['name'],'')
                med['history'].append(new)
                self.history[med_id].append(new)
                print(self.history)
                med['name'] = med_name
                self.api.update(med_id,'MedicationRequest',med_name)

                return

        print(f"Nie znaleziono obiektu z id: {med_id}")

    def set_observation_name_val(self, obs_id, obs_name,value):
        for obs in self.observations:
            if obs['id'] == obs_id:
                date_now = dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if 'history' not in obs.keys():
                    obs['history']=[]
                if obs_id not in self.history.keys():
                    self.history[obs_id]=[]
                new=history(obs_id, date_now, obs['name'],obs['value'])
                obs['history'].append(new)
                self.history[obs_id].append(new)
                obs['name'] = obs_name
                obs['value']=value
                self.api.update(obs_id,'Observation',obs_name, value)

                return

        print(f"Nie znaleziono obiektu z id: {obs_id}")

    def get_data(self):
        patient_history = sorted(self.observations, key=lambda k: k['date'])

        plot_data = {}
        data = {
            'name': '',
            'values': [],
            'dates': [],
            'unit': ''
        }
        for post in patient_history:
            if post['type'] not in ['medication', 'Brak info']:
                if post['name'] not in plot_data:
                    if post['type'] == 'value':
                        plot_data[post['name']] = {
                            'values': [post['value']],
                            'dates': [post['date'][:16].replace('T',' ')],
                            'unit': post['unit']
                        }
                    elif post['type'] == 'values':

                        plot_data[post['name']] = {
                            'data': []
                        }
                        for post_rec in post['values']:
                            data = {
                                'name':post_rec['name'],
                                'values': [post_rec['value']],
                                'dates': [post['date'][:16].replace('T',' ')],
                                'unit': post_rec['unit']
                            }

                            plot_data[post['name']]['data'].append(data)

                else:
                    if post['type'] == 'value':
                        plot_data[post['name']]['values'].append(post['value'])
                        plot_data[post['name']]['dates'].append(post['date'][:16].replace('T', ' '))
                    elif post['type'] == 'values':

                        i=0
                        for post_rec in post['values']:
                            plot_data[post['name']]['data'][i]['values'].append(post_rec['value'])
                            plot_data[post['name']]['data'][i]['dates'].append(post['date'][:16].replace('T', ' '))
                            i+=1

        return plot_data

    def get_edit_history(self,id):
        if id in self.history.keys():
            return self.history[id]