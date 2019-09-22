import numpy as np
from datahandler_lw import DataHandlerLW

class lw_data():
    def __init__(self,Id,accessProperties):
        self.Id=Id
        self.accessProperties=accessProperties
        self.dataH=DataHandlerLW(accessProperties)
        self.sample=self.dataH.sample
        self.data_size,self.cols=self.dataH.data_size,self.dataH.cols

    def getMetadata(self):
        if "EnvType" in self.accessProperties:
            return {"Action_space": self.dataH.action_space}
        else:
            return {"Dataset_size": self.data_size, "Columns": self.cols}    

    def getPartitionSummary(self):
        if "EnvType" in self.accessProperties:
            return ""
        else:
            train_len=0
            validation_len=0
            test_len=0
            totalDataSize=self.data_size
            
            for path, partition in zip(self.accessProperties["Path"], self.accessProperties["Partition_list"]):
                datasetsize=np.atleast_1d(self.dataH.datasets[path]).shape[0]
                train_len+=datasetsize*partition[0]
                validation_len+=datasetsize*partition[1]
                test_len+=datasetsize*partition[2]
            return [round(train_len/totalDataSize),round(validation_len/totalDataSize),round(test_len/totalDataSize)]

    def updateProperties(self, accessProperties):
        if "EnvType" in self.accessProperties:
            pass
        else:
            if accessProperties!=self.accessProperties:
                self.accessProperties=accessProperties
                print("DataProperties has changed, updating the data and sample")
                self.dataH.updateProperties(accessProperties)
                self.sample=self.dataH.sample

    def getData(self, accessProperties):
        if accessProperties!=self.accessProperties:
            print("DataProperties has changed, updating the data and sample")
            self.dataH.updateProperties(accessProperties)
            self.sample=self.dataH.sample

        D=np.array(self.sample)

        if isinstance(D, np.integer):
            D=int(D)
        elif isinstance(D, np.floating):
            D=float(D)
        elif isinstance(D, np.ndarray):
            D=D.tolist()

        if type(D).__name__=="int" or type(D).__name__=="float":
            D=[D]

        t=self.getPlot(D)

        if t=="grayscale":
            (height,width)=np.shape(D)[0:2]
            D=self.grayscale2RGBa(D)
            output={
                    "series":[{
                        "data":D,
                        "height":height,
                        "type":"rgba",
                        "width":width
                    }]
                }
        elif t=="RGB":
            (height,width)=np.shape(D)[0:2]
            D=self.RGB2RGBa(D)
            output={
                    "series":[{
                        "data":D,
                        "height":height,
                        "type":"rgba",
                        "width":width
                    }]
                }
        else:
            output={
                "xLength":np.shape(D)[0],
                "series":[{
                    "type":t,
                    "data":D
                }]
            }            
        return output

    def __del__(self):
        print("Cleaning up and deleting")
        try:
            self.dataH.clean_up()
        except:
            pass
        self.dataH=[]
        del self

    def grayscale2RGBa(self,data):
        data=np.squeeze(data)
        (w,h)=np.shape(data)
        newData=np.empty((w, h, 4))
        normalizedData=np.around((data/data.max())*255)
        newData[:, :, 0] = normalizedData
        newData[:, :, 1] = newData[:, :, 2] = newData[:, :, 0]
        newData[:,:,3]=255
        flatData=list(np.reshape(newData,-1))
        return flatData

    def RGB2RGBa(self,data):
        data=np.squeeze(data)
        (w,h,d)=np.shape(data)
        newData=np.empty((w, h, 4))
        normalizedData=np.around((data/data.max(0).max(0))*255)
        newData[:, :, 0:3] = normalizedData
        newData[:,:,3]=255
        flatData=list(np.reshape(newData,-1))
        return flatData

    def getPlot(self,D):
        if len(np.shape(np.squeeze(D)))==0:
            t="scatter"
        elif len(np.shape(np.squeeze(D)))==1:
            if np.shape(np.squeeze(D))[0]<25:
                t="bar"
            else:
                t="line"
        elif len(np.shape(np.squeeze(D)))==2:
            t="grayscale"
        elif len(np.shape(np.squeeze(D)))==3:
            if np.shape(np.squeeze(D))[-1]==1:
                t="grayscale"
            elif np.shape(np.squeeze(D))[-1]==3:
                t="RGB"    #Assume RGB, Replace with a button later on
            # elif np.shape(np.squeeze(self.variables[self.currentView]["input"]))[0]==np.shape(np.squeeze(self.variables[self.currentView]["input"]))[1]==np.shape(np.squeeze(self.variables[self.currentView]["input"]))[2]:
            #     pass 
            else:
                t="heatmap"
            #     self.plot1.imshow(self.variables[self.currentView]["input"][:,:,0])
        else:
            t="scatter" #Just something which works for all
        return t


if __name__ == "__main__":
    def setup(paths,partitions):
        accessProperties = {"Category": "Local",
                            "Path": paths,
                            "Partition_list":partitions,
                            "Columns": [0]}        
        return accessProperties


    paths=['C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\data_banknote_authentication.csv','C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\data_banknote_authentication - Copy.csv']
    partitions=[[75,15,10],[75,15,10]]

    ap = setup(paths,partitions)

    dh_lw=lw_data('1',ap)

    print(dh_lw.getPartitionSummary())

  