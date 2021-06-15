class PatientsData:
    def __init__(self, patients):
        self.patients = patients

    def get_patient(self, id):
        for patient in self.patients:
            if patient.id == id:
                patient.update_observation()
                patient.update_medications()
                return patient

    def get_all_patients(self):
        return self.patients

    def get_patients_count(self):
        return len(self.patients)