class PatientChart:
    def __init__(self,id,data):
        self.id = id
        self.data = data

    def get_data(self):
        return self.data


class PatientsChart:
    def __init__(self):
        self.patients_chart = []

    def add_patient_chart(self,patient):
        self.patients_chart.append(patient)

    def get_patient_data_by_id(self,id):
        for patient in self.patients_chart:
            if patient.id == id:
                return patient.get_data()

    def get_patients_chart(self):
        return self.patients_chart


