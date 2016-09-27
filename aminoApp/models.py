from django.db import models

# Create your models here.

class NutritionalValue(models.Model):
    #food = models.ForeignKey(Food, on_delete=models.CASCADE) # models.ForeignKey(Food, on_delete=models.CASCADE) #models.OneToOneField
    #choice_text = models.CharField(max_length=200)
    #dbid = models.IntegerField() # id in source database
    #value = models.FloatField()
    # essential amino acids
    # From 501 to 510 plus 512
    trp_g = models.FloatField()
    thr_g = models.FloatField()
    ile_g = models.FloatField()
    leu_g = models.FloatField()
    lys_g = models.FloatField()
    met_g = models.FloatField()
    cys_g = models.FloatField()
    phe_g = models.FloatField()
    tyr_g = models.FloatField()
    val_g = models.FloatField()
    his_g = models.FloatField()
    # other amino acids: but only proteinogenic
    arg_g = models.FloatField()
    ala_g = models.FloatField()
    asp_g = models.FloatField()
    glu_g = models.FloatField()
    gly_g = models.FloatField()
    pro_g = models.FloatField()
    ser_g = models.FloatField()
    # main components
    prot = models.FloatField() #proteins (procnt)
    fat = models.FloatField()
    carbo = models.FloatField() # carbohydrate chocdf
    fiber = models.FloatField()
    ash = models.FloatField()
    alc = models.FloatField(null=True)
    water = models.FloatField()
    energ = models.FloatField() # enerc_kcal
    prot_adj = models.FloatField(null=True)
    sugars = models.FloatField(null=True)
    # different sugars: later
    # minerals
    ca = models.FloatField()
    fe = models.FloatField()
    mg = models.FloatField()
    p = models.FloatField() #phosphorus
    k = models.FloatField() #potassium
    na = models.FloatField()
    zn = models.FloatField()
    cu = models.FloatField()
    mn = models.FloatField()
    se = models.FloatField(null=True)
    # vitamins: later
    # description
    description = models.CharField(max_length=200)
    def getQuantitativeFields(self):
        quantFields = ('trp_g','thr_g','ile_g','leu_g','lys_g','met_g','cys_g','phe_g','tyr_g','val_g','his_g',\
        'arg_g','ala_g','asp_g','glu_g','gly_g','pro_g','ser_g',
        'prot','fat','ash','water','fiber','carbo','energ',
        'ca','fe','mg','p','k','na','zn','cu','mn','se')
        # about 'prot_adj' we do not know 'sugars',
        return quantFields
    def getValueDict (self):
        quantFields = self.getQuantitativeFields()
        valueDict = {}
        for fieldName in quantFields:
            # setattr(newVector,fieldName,getattr(self,fieldName) * scalar)
            valueDict[fieldName]=getattr(self,fieldName)
        return valueDict

    def getValues (self):
        # can do it with .items from dict
        quantFields = self.getQuantitativeFields()
        nutValues = []
        for fieldName in quantFields:
            nutValues.append(getattr(self,fieldName))
        return nutValues
    def __rmul__(self, scalar):
        # 2 * x # __rmul__
        newVector = self
        # quantitative fields
        quantFields = self.getQuantitativeFields()
        # multiply all the quantitative fields
        for fieldName in quantFields:
            if getattr(self,fieldName) is None:
                setattr(newVector,fieldName,None)
            else:
                setattr(newVector,fieldName,getattr(self,fieldName) * scalar)
        #newVector.trp_g=self.trp_g * scalar
        return newVector
    def __add__(self,other):
        # to sum nutritional values
        newVector = self
        quantFields = self.getQuantitativeFields()
        for fieldName in quantFields:
            # setattr(newVector,fieldName,getattr(self,fieldName) + getattr(other,fieldName))
            if (getattr(self,fieldName) is not None) and (getattr(other,fieldName) is not None):
                setattr(newVector,fieldName,getattr(self,fieldName) + getattr(other,fieldName))
            else:
                setattr(newVector,fieldName,None)
        return newVector
    def __radd__(self,other):
        # to sum nutritional values
        newVector = self
        quantFields = self.getQuantitativeFields()
        for fieldName in quantFields:
            if (getattr(self,fieldName) is not None) and (getattr(other,fieldName) is not None):
                setattr(newVector,fieldName,getattr(self,fieldName) + getattr(other,fieldName))
            else:
                setattr(newVector,fieldName,None)
        return newVector
    def getIndispensableAminoNames(self):
        return ['trp_g', 'thr_g', 'ile_g', 'leu_g', 'lys_g', 'met_g', 'cys_g', 'phe_g', 'tyr_g', 'val_g', 'his_g']
    def getAminoVector(self):
        indispAminoNames = self.getIndispensableAminoNames()
        return [getattr(self,aminoName) for aminoName in indispAminoNames]
        #return [self.trp_g, self.thr_g, self.ile_g, self.leu_g, self.lys_g, self.met_g, self.cys_g, self.phe_g, self.tyr_g, self.val_g, self.his_g]
    def __str__(self):
        #valueStr=str(getAminoVector(self))
        return self.description #+ valueStr #+ str(getAminoVector(self))