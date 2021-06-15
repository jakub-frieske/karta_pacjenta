from fhirpy import SyncFHIRClient

class FHIRApi:
    def __init__(self):
        HAPI_BASE_URL = "http://localhost:8080/baseR4"
        self.limit = 1000
        self.client = SyncFHIRClient(HAPI_BASE_URL)

    def get_patients(self):
        resources = self.client.resources('Patient')
        resources = resources.search().limit(self.limit)
        return resources.fetch()

    def get_observations_by_id(self, id):
        resources = self.client.resources('Observation')
        resources = resources.search(subject=id).limit(self.limit).sort('date')
        return resources.fetch()

    def get_medications_by_id(self, id):
        resources = self.client.resources('MedicationRequest')
        resources = resources.search(subject=id).limit(self.limit)
        return resources.fetch()

    def update(self,id, type, *data):
        if type == 'Observation':
            resources = self.client.resources('Observation')
            resources = resources.search(_id=id).limit(1)
            observation_res = resources.fetch()
            observation_res[0]["code"].coding[0].display = data[0]
            if data[1]!= None:
                observation_res[0]["valueQuantity"].value = data[1]

            observation_res[0].save()

        elif type == 'MedicationRequest':
            resources = self.client.resources('MedicationRequest')
            resources = resources.search(_id=id).limit(1)
            medication_res = resources.fetch()
            print(medication_res)
            medication_res[0]["medicationCodeableConcept"].coding[0].display = data
            medication_res[0].save()

        elif type == 'Patient':
            resources = self.client.resources('Patient')
            resources = resources.search(_id=id).limit(1)
            patient_res = resources.fetch()
            patient_res[0]["name"][0].family = data
            patient_res[0].save()

    def get_observation_history_by_id(self, id):
        resources = self.client.resources('Observation',vid=8)
        resources = resources.search(_id=id).limit(self.limit).fetch()
        print(resources)
        for observation in resources:
            print(observation['meta']['versionId'])
        return resources



