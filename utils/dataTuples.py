codeNested = {"Observation" : 'code', "MedicationAdministration" : 'medicationCodeableConcept'}

codeDict = {'Observation' : 'root-code-coding-coding_0-code', 'MedicationAdministration' : 'root-medicationCodeableConcept-coding-coding_0-code'}

dateDict = {'Observation' : 'root-effectiveDateTime', 'MedicationAdministration' : 'root-effectiveDateTime', 'Consent' : 'root-dateTime'}

valueDict = {'440404000' : 'root-valueQuantity-value', '9059-7' : 'root-valueQuantity-value', '39543009' : 'root-dosage-dose-value'}

patientDict = {'440404000' : 'root-subject-reference', '9059-7' : 'root-subject-reference', '39543009' : 'root-subject-reference'}

codes = {'CGM' : '440404000', 'CarbIntake' : '9059-7', 'Insulin' : '39543009'}

filesToDrop = ['BulkRequestHeaderDict.json', 'binariesRequestDict.json']
