import os
import CMGTools.RootTools.fwlite.Config as cfg
from CMGTools.Production.datasetToSource import datasetToSource
from CMGTools.Production.datasetInformation import DatasetInformation

class ComponentCreator(object):
    def makeMCComponent(self,name,dataset,user,pattern):
        
         component = cfg.MCComponent(
             dataset=dataset,
             name = name,
             files = self.getFiles(dataset,user,pattern),
             xSection = 1,
             nGenEvents = 1,
             triggers = [],
             effCorrFactor = 1,
#             skimEfficiency = self.getSkimEfficiency(dataset,user)
         )

 #        print 'Skim Efficiency for ',name,'=', component.skimEfficiency
         return component

    def makePrivateMCComponent(self,name,dataset,files):
         if len(files) == 0:
            raise RuntimeError, "Trying to make a component %s with no files" % name
         # prefix filenames with dataset unless they start with "/"
         dprefix = dataset +"/" if files[0][0] != "/" else ""
         component = cfg.MCComponent(
             dataset=dataset,
             name = name,
             files = ['root://eoscms//eos/cms%s%s' % (dprefix,f) for f in files],
             xSection = 1,
             nGenEvents = 1,
             triggers = [],
             effCorrFactor = 1,
#             skimEfficiency = self.getSkimEfficiency(dataset,user)
         )

 #        print 'Skim Efficiency for ',name,'=', component.skimEfficiency
         return component
    
    ### MM
    def makeMyPrivateMCComponent(self,name,dataset,dbsInstance):
        #entries = findMyPrimaryDatasetNumFiles(dataset, -1, -1)
        #dbs = 'das_client.py --query="file dataset=%s instance=prod/phys03"' % dataset
        #dbsOut = os.popen(dbs)
        files = []
        #filesDBS = []
        #for line in dbsOut:
        #    if line.find('/store')==-1:
        #        continue
        #    line = line.rstrip()
        #     # print 'line',line
        #    filesDBS.append(line)
        component = cfg.MCComponent(
            dataset=dataset,
            name = name,
            #files = ['root://eoscms//eos/cms%s' % f for f in filesDBS],
            files = self.getFilesDBS(dataset, dbsInstance),
            xSection = 1,
            nGenEvents = 1,
            triggers = [],
            effCorrFactor = 1,
        )

        return component
    ### MM

    def makeDataComponent(self,name,datasets,user,pattern):
         files=[]

         for dataset in datasets:
             files=files+self.getFiles(dataset,user,pattern)
        
         component = cfgDataComponent(
             dataset=dataset,
             name = name,
             files = files,
             intLumi=1,
             triggers = [],
             json=json
         )

         return component


    def getFiles(self,dataset, user, pattern):
        # print 'getting files for', dataset,user,pattern
        ds = datasetToSource( user, dataset, pattern, True )
        files = ds.fileNames
        return ['root://eoscms//eos/cms%s' % f for f in files]
    

    def getSkimEfficiency(self,dataset,user):
        info=DatasetInformation(dataset,user,'',False,False,'','','')
        fraction=info.dataset_details['PrimaryDatasetFraction']
        if fraction<0.001:
            print 'ERROR FRACTION IS ONLY ',fraction
        return fraction 
        

    ### MM
    ### Function to get files on DBS prod/phys03
    def getFilesDBS(self, dataset, dbsInstance):
        entries = findMyPrimaryDatasetNumFiles(dataset, dbsInstance, -1, -1)
        #print entries
        filesDBS = []
        dbs = 'das_client.py --query="file dataset=%s instance=prod/%s" --limit=%s' % (dataset, dbsInstance, entries)
        dbsOut = os.popen(dbs)
        for line in dbsOut:
            if line.find('/store')==-1:
                continue
            line = line.rstrip()
            # print 'line',line
            filesDBS.append(line)
        return ['root://eoscms//eos/cms%s' % f for f in filesDBS]
    

def findMyPrimaryDatasetNumFiles(dataset, dbsInstance, runmin, runmax):
    
    query, qwhat = dataset, "dataset"
    if "#" in dataset: qwhat = "block"
    if runmin >0 or runmax > 0:
        if runmin == runmax:
            query = "%s run=%d" % (query,runmin)
        else:
            print "WARNING: queries with run ranges are slow in DAS"
            query = "%s run between [%d, %d]" % (query,runmin if runmin > 0 else 1, runmax if runmax > 0 else 999999)
    dbs='das_client.py --query="summary %s=%s instance=prod/%s"'%(qwhat, query, dbsInstance)
    dbsOut = os.popen(dbs).readlines()
    entries = []
    for line in dbsOut:
        line = line.replace('\n','')
        if "nfiles" in line:
            entries.append(int(line.split(":")[1]))
    if entries:
        return sum(entries)
    return -1
    ### MM

