codeNested = {"Observation" : 'code', "MedicationAdministration" : 'medicationCodeableConcept'}

codeDict = {'Observation' : 'root-code-coding-coding_0-code', 'MedicationAdministration' : 'root-medicationCodeableConcept-coding-coding_0-code'}

dateDict = {'Observation' : 'root-effectiveDateTime', 'MedicationAdministration' : 'root-effectiveDateTime', 'Consent' : 'root-dateTime'}

filesToDrop = ['BulkRequestHeaderDict.json', 'binariesRequestDict.json']
