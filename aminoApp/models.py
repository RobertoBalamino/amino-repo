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

class FoodCategory(models.Model):
    cat_dbid = models.IntegerField(null=True)
    name = models.CharField(max_length=200)
    address_name = models.CharField(max_length=80,null=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name

class Food(models.Model):
    # food: name, category, nutriment info...
    food_name = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date added', null=True, blank=True,auto_now_add=True) #models.DateTimeField('date published',null=timezone.now())
    # question_text = models.CharField(max_length=200)
    # pub_date = models.DateTimeField('date published')
    food_category = models.IntegerField(null=True)
    food_dbid = models.IntegerField(default=0)
    nutritional_value = models.ForeignKey('NutritionalValue', on_delete=models.CASCADE,null=True)
    efficiency = models.FloatField(null=True)
    food_description = models.TextField(null=True, blank=True)
    picture_file = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.getNameBegin() #+str(self.food_dbid) #self.food_name
    def getNameBegin(self):
        # return two first words of food name
        fullName = self.food_name
        nameSplit = fullName.split(',')
        if len(nameSplit)>1:
            shortName = nameSplit[0]+','+nameSplit[1]
        else:
            shortName = fullName
        return shortName
    def getKeywordName(self):
        shortName = self.getNameBegin()
        keyName = shortName.replace(',','')
        return keyName
    def getNameWithoutSaltInfo(self):
        # deletes unwanted information at the end of food name
        unneededInfo = [', without salt',', solids and liquids',', drained']
        foodName = self.food_name
        # nameSplit = fullName.split(',')
        # if nameSplit[-1] in unneededInfo:
        #     nameSplitNoSalt = nameSplit[0:-1]
        # else:
        #     nameSplitNoSalt = nameSplit
        # nameNoSalt = ",".join(nameSplitNoSalt)
        # # nameSplit[0]+','+nameSplit[1]
        # return nameNoSalt
        for unneededStr in unneededInfo:
            foodName = foodName.replace(unneededStr,'')
        return foodName
    class Meta:
        ordering = ['food_name']

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=20, null=True, blank=True) # or a choice
    link = models.CharField(max_length=80, null=True, blank=True)
    date_added = models.DateTimeField('date added', null=True, blank=True,auto_now_add=True)
    efficiency = models.FloatField(null=True)
    def __str__(self):
        return self.title
    def get_nutritional_value(self):
        # ingreds=self.ingredients.all()
        ingreds = Ingredient.objects.filter(recipe = self.pk)
        ingrValues=[ingr.get_nutritional_value() for ingr in ingreds]
        return sum(ingrValues[1:],ingrValues[0])

DEFAULT_FOOD_ID = 1
class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, default=DEFAULT_FOOD_ID)
    quantity = models.FloatField()
    def __str__(self):
        # return (str(self.quantity*100))
        return ("{:4.0f}".format(self.quantity)+' g of '+self.food.food_name)
    def get_nutritional_value(self):
        return (self.quantity*0.01*self.food.nutritional_value)

class FoodPair(models.Model):
    foodOneId = models.IntegerField()
    foodTwoId = models.IntegerField() #models.ForeignKey(Food)
    pair_name = models.CharField(max_length=30, null=True)
    bestEfficiency = models.FloatField(null=True)
    bestProportion = models.FloatField(null=True)
    angleAbsolute = models.FloatField(null=True)
    angleIncomplete = models.FloatField(null=True)
    def __str__(self):
        if self.pair_name is None:
            pairName = 'no name'
        else:
            pairName = self.pair_name
        return pairName


class Nutriment(models.Model):
    # a nutrient (for instance an amino acid)
    dbid = models.IntegerField()
    internal_name = models.CharField(max_length=10)
    public_name = models.CharField(max_length=20)
    unit = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)
    abbreviations = models.CharField(max_length=100, null=True, blank=True )
    category = models.CharField(max_length=30)
    RDA_AI = models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.public_name
    def capitalName(self):
        return self.public_name.capitalize()
    def link_name(self):
        # foodName = foodName.replace(unneededStr,'')
        return self.public_name.replace(' ','_')

class RelativeAminoScore(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, default=DEFAULT_FOOD_ID)
    aminoAcid = models.ForeignKey(Nutriment, on_delete=models.CASCADE)
    score = models.FloatField()
    # scoringPattern: TargetAminoPattern
    def __str__(self):
        return 'score of '+self.aminoAcid.internal_name+'in '+self.food.food_name+str(self.score)

class TargetAminoPattern(models.Model):
    nutritional_value = models.ForeignKey('NutritionalValue', on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name


class QuestionAnswer(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=30, null=True, blank=True)
    showQuestion = models.NullBooleanField(default=True)
    def __str__(self):
        if self.showQuestion:
            questionString = self.question
        else:
            questionString = self.question+'(hidden)'
        return questionString

class LiteratureReference(models.Model):
    in_text = models.CharField(max_length=100)
    reference_APA = models.TextField()
    abstract = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=30, null=True, blank=True)
    def __str__(self):
        return self.in_text

class ReferenceSupportsAnswer(models.Model):
    reference = models.ForeignKey(LiteratureReference, on_delete=models.CASCADE)
    answer = models.ForeignKey(QuestionAnswer, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.reference)