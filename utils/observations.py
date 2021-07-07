from utils.inOut import inOut
import pandas as pd
import os

class ObsDF(inOut):
    def __init__(self, date = "2021-05-29", MAX=3):
        super(ObsDF, self).__init__(date = date, MAX=MAX)
        '''
            Takes the Observations object and turns it into a CSV file.
        '''
        try:
            self.createDataFrame(MAX=10)
            self.createDataFrame()
            self.createDataFrame()
        except:
            print("Oh oh... No Obs resources...")
        try:
            self.createDataFrame(resourceType = "CodeSystem")
            self.createDataFrame(resourceType = "CodeSystem")
            self.createDataFrame(resourceType = "CodeSystem")
        except:
            print("Oh oh... No CodeSystem resources...")
        try:
            self.createDataFrame(resourceType = "Questionnaire")
            self.createDataFrame(resourceType = "Questionnaire")
            self.createDataFrame(resourceType = "Questionnaire")
        except:
            print("Oh oh... No Questionnaire resources...")
        try:
            self.createDataFrame(resourceType = "QuestionnaireResponse")
            self.createDataFrame(resourceType = "QuestionnaireResponse")
            self.createDataFrame(resourceType = "QuestionnaireResponse")
        except:
            print("Oh oh... No QuestionnaireResponse resources...")

    def createDataFrame(self, resourceType = "Observation", MAX=0):
        if resourceType == "Observation":
            if MAX > 0 and MAX <= len(self.Obs):
                limit = MAX
            else:
                limit = len(self.Obs)

            self.temp = self.JSONToDFRow(self.Obs[0])
            self.df = pd.DataFrame(index=range(limit), columns=self.temp.keys())
            print(self.df.shape)
            for i in range(limit):
                self.temp = self.JSONToDFRow(self.Obs[i])
                for key in self.temp:
                    self.df.iloc[i][key] = self.temp[key]

            self.saveDataFrame()
        elif resourceType == "CodeSystem":
            if MAX > 0 and MAX <= len(self.CodeSystem):
                limit = MAX
            else:
                limit = len(self.CodeSystem)

            self.temp = self.JSONToDFRow(self.CodeSystem[0])
            self.dfCodeSystem = pd.DataFrame(index=range(limit), columns=self.temp.keys())
            print(self.dfCodeSystem.shape)
            for i in range(limit):
                self.temp = self.JSONToDFRow(self.CodeSystem[i])
                for key in self.temp:
                    self.dfCodeSystem.iloc[i][key] = self.temp[key]

            self.saveDataFrame(filename="CodeSystem.csv")
        elif resourceType == "Questionnaire":
            if MAX > 0 and MAX <= len(self.Questionnaire):
                limit = MAX
            else:
                limit = len(self.Questionnaire)

            self.temp = self.JSONToDFRow(self.Questionnaire[0])
            self.dfQuestionnaire = pd.DataFrame(index=range(limit), columns=self.temp.keys())
            print(self.dfQuestionnaire.shape)
            for i in range(limit):
                self.temp = self.JSONToDFRow(self.Questionnaire[i])
                for key in self.temp:
                    self.dfQuestionnaire.iloc[i][key] = self.temp[key]

            self.saveDataFrame(filename="Questionnaire.csv")
        elif resourceType == "QuestionnaireResponse":
            if MAX > 0 and MAX <= len(self.QuestionnaireResponse):
                limit = MAX
            else:
                limit = len(self.QuestionnaireResponse)

            self.temp = self.JSONToDFRow(self.QuestionnaireResponse[0])
            self.dfQuestionnaireResponse = pd.DataFrame(index=range(limit), columns=self.temp.keys())
            print(self.dfQuestionnaireResponse.shape)
            for i in range(limit):
                self.temp = self.JSONToDFRow(self.QuestionnaireResponse[i])
                for key in self.temp:
                    self.dfQuestionnaireResponse.iloc[i][key] = self.temp[key]

            self.saveDataFrame(filename="QuestionnaireResponse.csv")

    def isList(self, d, keyword):
        if type(d.get(keyword)) == list:
            keywordUP = keyword.upper()
            d[keywordUP] = d[keyword]
            d[keyword] = {}
            for i, el in enumerate(d[keywordUP]):
                d[keyword][f'{keyword}_{i}'] = d[keywordUP][i]
            d.pop(keywordUP, None)

    def recursive_items(self, dictionary, prepend = ['root']):
        '''
        https://stackoverflow.com/questions/39233973/get-all-keys-of-a-nested-dictionary
        '''
        for key, value in dictionary.items():
            # print(type(value))
            if type(value) is list:
                # print(key)
                self.isList(dictionary, key)
            elif type(value) is dict:
                yield (key, value, type(value))
                # prepend.append(key)
                yield from self.recursive_items(value, prepend + [key])
            else:
                string = self.listToString(prepend)
                yield (f'{string}{key}', value, type(value))

    def listToString(self, l):
        # string =
        string = ''
        for i in l:
            string = string + i + '-'
        return string

    def getStrings(self, array):
        l = dict()
        for i in range(len(array)):
            if array[i][2] != dict:
                # l.append({arr[i][0] : arr[i][1]})
                l[array[i][0]] = array[i][1]
        return l

    def JSONToDFRow(self, obj, getColumnNames=False):
        tripleArray = list(self.recursive_items(obj))
        rowToDataFrame = self.getStrings(tripleArray)
        # if getColumnNames:
        #     return rowToDataFrame.keys()
        # else:
        #     return list(rowToDataFrame.values())
        return rowToDataFrame

    def saveDataFrame(self, filename='Observations.csv'):
        if filename=='Observations.csv':
            self.df.to_csv(os.path.join(os.getcwd(), self.pathToDump, filename), index=False)
        elif filename=='CodeSystem.csv':
            self.dfCodeSystem.to_csv(os.path.join(os.getcwd(), self.pathToDump, filename), index=False)
        elif filename=='Questionnaire.csv':
            self.dfQuestionnaire.to_csv(os.path.join(os.getcwd(), self.pathToDump, filename), index=False)
        elif filename=='QuestionnaireResponse.csv':
            self.dfQuestionnaireResponse.to_csv(os.path.join(os.getcwd(), self.pathToDump, filename), index=False)


# r = ObsDF("2021-06-01")

# r.saveJSON()
#
# r.loadJSON()


if __name__ == '__main__':
    ObsDF("2021-06-01")
