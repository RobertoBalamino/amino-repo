import numpy as np
from pulp import *

from .models import NutritionalValue, Nutriment, Ingredient, RelativeAminoScore

import pygal
from pygal.style import Style

def readFoodNutrimentInfo(searchId):
    # searchId: int, USDA database food id
    nutValue=dict.fromkeys([501])
    with open(r'/home/tetramino/aminoProject/aminoApp/sourceData/NUT_DATA_selected.txt','r') as fp:
        for lineInFile in fp:
            splLine=lineInFile.split('~')
            idOfLine=int(splLine[1])
            if idOfLine==searchId:
                nutrId=int(splLine[3])
                nutValueLine=splLine[4] #value^nDataPoints^standardDev
                nutValueSplit=nutValueLine.split('^')
                nutValue[nutrId]=float(nutValueSplit[1]) #'nMeas':nutValueSplit[3],'stDev':nutValueSplit[2]}
            elif idOfLine > searchId:
                break
    return nutValue

def getAminoEfficiencyFromVector(aminoVector,completeAminoVector):
    aminoDiv=np.divide(aminoVector, completeAminoVector)
    # old: not consistent with optimization formula
    #aminoEfficiency=min(aminoDiv)/np.mean(aminoDiv)
    # new: consistent with optimization formula
    aminoEfficiency = min(aminoDiv)*np.sum(completeAminoVector)/np.sum(aminoVector)
    return aminoEfficiency

def getCompleteAminoVector():
    completeProteinValue=NutritionalValue.objects.get(description='complete_protein_62kg')
    completeAminoVector=completeProteinValue.getAminoVector()
    return completeAminoVector

def getAminoProportionsOfComplete(aminoVector):
    completeAminoVector= getCompleteAminoVector()
    aminoDiv=np.divide(aminoVector, completeAminoVector)
    aminoPropsOfMin = aminoDiv /min(aminoDiv)
    projectAminoOnComplete = projectOnLineWithCoefficients(aminoVector, completeAminoVector)
    projectedAmino = projectAminoOnComplete['projected']
    aminoPropsOfProj = np.divide(aminoVector, projectedAmino)
    return {'propsOfProj':aminoPropsOfProj,'propsOfMin':aminoPropsOfMin,'projected':projectedAmino}

def projectOnLineWithCoefficients(x, a):
    # x=[x1,..,xn]
    # a=[a1,..,an]
    # projection z will be equal to vector a multiplied by scalar factor f
    # returning vector perpendicular to the line (x-z)
    f=sum(np.multiply(x,a))/sum(np.multiply(a,a))
    z=[f * ai for ai in a]
    perp=np.subtract(z,x)
    return {'projected':z,'perpendicular':perp}

def getAminoEfficiencyFromNutrimentValue(nutritValue):
    aminoVector=nutritValue.getAminoVector()
    # completeProteinValue=NutritionalValue.objects.get(description='complete_protein_62kg')
    # completeAminoVector=completeProteinValue.getAminoVector()
    completeAminoVector = getCompleteAminoVector()
    aminoEff=getAminoEfficiencyFromVector(aminoVector,completeAminoVector)
    return aminoEff

def getPairAminoEfficiencyDifferentProps(foodOne,foodTwo,nProps,bestProp):
    propsToCompute = [k/(nProps-1) for k in range(nProps)]
    propsToCompute = np.union1d (propsToCompute,(round(bestProp,2),))
    # calculate efficiency for different proportions
    nutVecOne=np.array(foodOne.nutritional_value.getAminoVector())
    nutVecTwo=np.array(foodTwo.nutritional_value.getAminoVector())
    completeAminoVector= getCompleteAminoVector()

    # propOne = [k/(nProps-1) for k in range(nProps) ]
    efficiencies = []
    proportions = []
    pairs = []
    for prop in propsToCompute: #for k in range(nProps):
        # prop = k/(nProps-1)
        proportions.append(prop)
        mixVec = np.add(prop*nutVecOne,(1-prop)*nutVecTwo)
        eff = getAminoEfficiencyFromVector(mixVec,completeAminoVector)
        efficiencies.append(eff)
        pairs.append((prop,eff))
    return {'efficiencies':efficiencies,'proportions':proportions,'pairs':pairs}

def getAngleBetweenVectors(vecOne,vecTwo):
    dotProd=np.dot(vecOne,vecTwo)
    angle=dotProd/pow(np.dot(vecOne,vecOne)*np.dot(vecTwo,vecTwo),0.5)
    return angle

def getPairAminoAngle(foodOne,foodTwo):
    nutVecOne=np.array(foodOne.nutritional_value.getAminoVector())
    nutVecTwo=np.array(foodTwo.nutritional_value.getAminoVector())
    # the angle between the vectors of amino acid quantities
    # dotProd=np.dot(nutVecOne,nutVecOne)
    # absAngle=dotProd/pow(np.dot(nutVecOne,nutVecOne)*np.dot(nutVecTwo,nutVecTwo),0.5)
    absAngle=getAngleBetweenVectors(nutVecOne,nutVecTwo)
    # the angle between the "incomplete parts" of these vectors
    completeAminoVector= getCompleteAminoVector()
    projVecOne=projectOnLineWithCoefficients(nutVecOne, completeAminoVector)
    perpVecOne=projVecOne['perpendicular']
    projVecTwo=projectOnLineWithCoefficients(nutVecTwo, completeAminoVector)
    perpVecTwo=projVecTwo['perpendicular']
    incompleteAngle=getAngleBetweenVectors(perpVecOne,perpVecTwo)
    return {'absolute':absAngle,'incomplete':incompleteAngle}

def getBestProportionForFoodPair(foodOne,foodTwo):
    aminoValuesOne=np.array(foodOne.nutritional_value.getAminoVector())
    aminoValuesTwo=np.array(foodTwo.nutritional_value.getAminoVector())
    aminoValuesComplete= getCompleteAminoVector()
    # constraints: all aminos at least something (one if using aminoDiv)
    x = LpVariable("x", 0, None)
    y = LpVariable("y", 0, None)
    prob = LpProblem("myProblem", LpMinimize)
    for ia in range(len(aminoValuesComplete)):
        # constraints: all aminos at least something (one if using aminoDiv)
        prob += x * aminoValuesOne[ia] + y * aminoValuesTwo[ia] >= aminoValuesComplete[ia]
    # to minimize: total weight of food
    # prob += x + y
    # ( or total weight of amino acids), or or
    prob += x*sum(aminoValuesOne) + y* sum(aminoValuesTwo)
    status = prob.solve()
    LpStatus[status]
    bestPropOne=value(x)/(value(x)+value(y))#[value(x),value(y)]

    aminoValuesSum=np.multiply(bestPropOne,aminoValuesOne)+np.multiply(1-bestPropOne,aminoValuesTwo)
    # effOne=getAminoEfficiency(aminoValuesOne)
    # effTwo=getAminoEfficiency(aminoValuesTwo)
    # effSum=getAminoEfficiency(aminoValuesSum)
    effSum=getAminoEfficiencyFromVector(aminoValuesSum,aminoValuesComplete)
    #print('efficiency rises from '+str(effOne)+' and '+str(effTwo)+' to '+str(effSum) )
    return {'bestPropOne':bestPropOne,'efficiency':effSum}

def getBestProportionsForFoods(foods):
    nFoods = len(foods)
    aminoValuesFoods = []
    for food_i in foods:
        aminoValuesFoods.append(food_i.nutritional_value.getAminoVector())
    # aminoValuesOne=np.array(foodOne.nutritional_value.getAminoVector())
    # aminoValuesTwo=np.array(foodTwo.nutritional_value.getAminoVector())
    aminoValuesComplete= getCompleteAminoVector()
    # constraints: all aminos at least something (one if using aminoDiv)
    # variable definition
    foodPropVars = []
    for iFood in range(nFoods):
        foodPropVars.append(LpVariable("x"+str(iFood), 0, None))
    prob = LpProblem("myProblem", LpMinimize)
    # inequality definition
    for ia in range(len(aminoValuesComplete)):
        # constraints: all aminos at least the values for complete proteins
        sumValue = 0
        for iFood in range(nFoods):
            sumValue += foodPropVars[iFood] * aminoValuesFoods[iFood][ia]
        prob += ( sumValue >= aminoValuesComplete[ia] )
    # to minimize: total weight of food
    # prob += x + y
    # ( or total weight of amino acids), or or
    # to minimize: sum of sums
    sumToMin = 0
    for iFood in range(nFoods):
        sumToMin += foodPropVars[iFood] * sum (aminoValuesFoods[iFood])
    prob += sumToMin

    status = prob.solve()
    LpStatus[status]
    optimalValues = [value(foodPropVars[iFood]) for iFood in range(nFoods)]
    optimalSum = sum(optimalValues)
    optimalProportions = [optimalValues[iFood]/optimalSum for iFood in range(nFoods)]

    aminoValuesSum = sum([np.multiply(optimalValues[iFood],aminoValuesFoods[iFood])  for iFood in range(nFoods)])
    effSum=getAminoEfficiencyFromVector(aminoValuesSum,aminoValuesComplete)

    return {'foods':foods,'bestProps':optimalProportions,'efficiency':effSum}


def getAminoAcidNames():
    amino_acid_names = ('trp_g','thr_g','ile_g','leu_g','lys_g','met_g','cys_g','phe_g','tyr_g','val_g','his_g')
    return amino_acid_names

def analyseFoodPair(foodOne,foodTwo):

    context = {'foodOne': foodOne,'foodTwo': foodTwo}
    # b) calculate "angle"
    aminoPairAngle=getPairAminoAngle(foodOne,foodTwo)
    context['angle']=aminoPairAngle #['absolute']
    # c) calculate optimal proportion (linear programming)
    solveBestProp=getBestProportionForFoodPair(foodOne,foodTwo)
    context['bestEfficiency']=solveBestProp['efficiency']
    context['bestPropOne']=solveBestProp['bestPropOne']

    nameOfPair = foodOne.getNameBegin() + '-' + foodTwo.getNameBegin()
    context['pairName'] = nameOfPair
    # a) calculating efficiencies at different proportions (brute force)
    nProps = 21
    effAndProps = getPairAminoEfficiencyDifferentProps(foodOne,foodTwo,nProps,context['bestPropOne'])

    custom_style = getCustomPygalStyle()
    # line_chart = pygal.Line(title=u'Efficiencies at different proportions',
    #     x_title='Proportion of food one ('+foodOne.getNameBegin()+')',y_title='efficiency of combination',
    #     style=custom_style,legend_at_bottom=True)
    # line_chart.add('efficiency', effAndProps['efficiencies'])
    # line_chart.x_labels = map(str, effAndProps['proportions'])
    # line_chart.x_labels_major = [str(prop) for prop in effAndProps['proportions'] if round(prop,1)==prop]
    # # x_labels_major_every=2
    # line_chart.show_minor_x_labels=False
    # line_chart.x_labels = [str(k/10) for k in range(11)]
    # chart_rendered = chart.render_django_response()
    # return chart_rendered
    #return HttpResponse("Inspecting food pair: "+foodOne.food_name+" and "+foodTwo.food_name)

    line_chart = pygal.XY(title=u'Efficiencies at different proportions',
        x_title='Proportion of food one ('+foodOne.getNameBegin()+')',y_title='efficiency of combination',
        style=custom_style,legend_at_bottom=True)
    line_chart.add('efficiency', effAndProps['pairs'])
    # line_chart.x_labels = map(str, effAndProps['proportions'])
    # line_chart.x_labels_major = [str(prop) for prop in effAndProps['proportions'] if round(prop,1)==prop]
    # x_labels_major_every=2
    # line_chart.show_minor_x_labels=False

    chart_rendered=line_chart.render_data_uri()
    context['chart'] = chart_rendered
    return context

def getCustomPygalStyle(defaultFontSize=16):
    custom_style = Style(
        background='transparent',
        plot_background='rgb(255,255,255)',
        font_family='googlefont:Raleway',
        title_font_size=defaultFontSize+4,
        major_label_font_size=defaultFontSize,
        label_font_size=defaultFontSize-2,
        legend_font_size=defaultFontSize,
        value_font_size=defaultFontSize,
        tooltip_font_size=defaultFontSize,
        value_label_font_size=defaultFontSize)
    return custom_style

def saveRelativeAminoScores(food):
    # food=Food.objects.get(food_dbid=food_dbid)
    foodAminoVector=food.nutritional_value.getAminoVector()
    foodAminoProportions = getAminoProportionsOfComplete(foodAminoVector)

    amino_acid_names = food.nutritional_value.getIndispensableAminoNames() #getAminoAcidNames()
     # essential amino acid score
    # minIndex = np.argmin(foodAminoProportions['propsOfProj'])
    # minScore = foodAminoProportions['propsOfProj'][minIndex]
    # minAminoAcid = Nutriment.objects.get(internal_name=amino_acid_names[minIndex])
    # newAminoScore = RelativeAminoScore(food=food,aminoAcid=minAminoAcid,score=minScore)
    # newAminoScore.save()

    projProps = foodAminoProportions['propsOfProj']
    # interestingIndices = np.where(np.logical_or(projProps > 1.5 , projProps < 0.75))
    interestingIndices = [ia for ia in range(len(projProps)) if (projProps[ia] > 1.05 or projProps[ia] < 0.8)]
    for ia in interestingIndices:
        scoredAminoAcid = Nutriment.objects.get(internal_name=amino_acid_names[ia])
        if RelativeAminoScore.objects.filter(food=food,aminoAcid=scoredAminoAcid).exists():
            pass # score already there
        else:
            # create it
            newAminoScore = RelativeAminoScore(food=food,aminoAcid=scoredAminoAcid,score=projProps[ia])
            newAminoScore.save()

def getFoodAminoPlotAbsolute(food):
    foodAminoVector=food.nutritional_value.getAminoVector()
    custom_style = getCustomPygalStyle()
    # title=u'Amino acid quantities (g)',
    bar_chart = pygal.Bar(style=custom_style,legend_at_bottom=True,)                                            # Then create a bar graph object
    bar_chart.add('Amino acids in the food', foodAminoVector)  # Add some values
    # amino_acid_names = ('trp_g','thr_g','ile_g','leu_g','lys_g','met_g','cys_g','phe_g','tyr_g','val_g','his_g')
    amino_acid_names = getAminoAcidNames()
    bar_chart.x_labels = amino_acid_names

    foodAminoProportions = getAminoProportionsOfComplete(foodAminoVector)
    bar_chart.add('Balanced equivalent', foodAminoProportions['projected'])  # Add some values
    chartAbsolute=bar_chart.render_data_uri()
    return chartAbsolute

def getFoodAminoPlotProportions(food):
    foodAminoVector=food.nutritional_value.getAminoVector()
    foodAminoProportions = getAminoProportionsOfComplete(foodAminoVector)
    custom_style = getCustomPygalStyle()
    # title=u'Amino acid ratios',
    bar_chart_prop = pygal.Bar(style=custom_style,legend_at_bottom=True)
    bar_chart_prop.add('Amino acids', foodAminoProportions['propsOfProj'])
    amino_acid_names = getAminoAcidNames()
    bar_chart_prop.x_labels = amino_acid_names
    chartProp=bar_chart_prop.render_data_uri()
    return chartProp

def getRecipeAminoPlotProportions(recipe):
    custom_style = getCustomPygalStyle()

    menuNutrValue=recipe.get_nutritional_value()
    menuAminoVector = menuNutrValue.getAminoVector()
    projectVectorOnComplete = getAminoProportionsOfComplete(menuAminoVector)
    equivCompleteVector = projectVectorOnComplete['projected']
    ingreds = Ingredient.objects.filter(recipe = recipe)
    # title=u'Amino acid proportions',
    bar_chart_props = pygal.StackedBar(style=custom_style,legend_at_bottom=True)
    amino_acid_names = getAminoAcidNames()
    bar_chart_props.x_labels = amino_acid_names

    for ingr in ingreds:
        ingrNutrVal=ingr.get_nutritional_value()
        ingrAminoVector=ingrNutrVal.getAminoVector()
        ingrAminoProps = np.divide(ingrAminoVector, equivCompleteVector)
        bar_chart_props.add(str(ingr), ingrAminoProps)

    chart_props = bar_chart_props.render_data_uri()

    return chart_props

def getTargetAminoPlot(nutValue):
    foodAminoVector=nutValue.getAminoVector()
    custom_style = getCustomPygalStyle()
    # title=u'Amino acid quantities (g)',
    bar_chart = pygal.Bar(style=custom_style,legend_at_bottom=True,)                                            # Then create a bar graph object
    bar_chart.add('Amino acids in the food', foodAminoVector)  # Add some values
    # amino_acid_names = ('trp_g','thr_g','ile_g','leu_g','lys_g','met_g','cys_g','phe_g','tyr_g','val_g','his_g')
    amino_acid_names = getAminoAcidNames()
    bar_chart.x_labels = amino_acid_names

    chartAbsolute=bar_chart.render_data_uri()
    return chartAbsolute

def getMacroNutrientPie(foodValue):
    custom_style = getCustomPygalStyle(defaultFontSize=30)
    pie_chart = pygal.Pie(style=custom_style,legend_at_bottom=True)
    # pie_chart.title = 'Browser usage in February 2012 (in %)'
    pie_chart.add('fiber', foodValue.fiber)
    pie_chart.add('water', foodValue.water)
    pie_chart.add('carbohydrates', foodValue.carbo)
    pie_chart.add('fat', foodValue.fat)
    pie_chart.add('protein', foodValue.prot)
    renderedChart = pie_chart.render_data_uri()
    return renderedChart

def getRequirementsPerGramProtein(nutVal):
    # WHO protein and aa requirements p.245
    amino_acids = ['histidine','isoleucine','leucine','lysine','methionine','methionine + cysteine','phenylalanine + tyrosine','threonine','tryptophan','valine']
    amino_acids_short = ['his','ile','leu','lys','met','met + cys','phe + tyr','thr','trp','val']
    amino_acid_link = ['his','ile','leu','lys','met','met','phe','thr','trp','val']
    required = [15,30,59,45,16,22,30,23,6,39]
    absoluteValues = [nutVal.his_g,nutVal.ile_g,nutVal.leu_g,nutVal.lys_g,nutVal.met_g,nutVal.met_g+nutVal.cys_g,nutVal.phe_g+nutVal.tyr_g,nutVal.thr_g,nutVal.trp_g,nutVal.val_g]
    values = [1000*aval/nutVal.prot for aval in absoluteValues]
    propOfRequirement = np.divide(values,required)


    # ordering
    allZipped = zip(propOfRequirement,amino_acids,amino_acids_short,required,absoluteValues,values,amino_acid_link)
    allZippedSorted = sorted(allZipped, key = lambda t: t[0])
    unzipped = list(zip(*allZippedSorted))
    propOfRequirement = unzipped[0]
    amino_acids = unzipped[1]
    amino_acids_short = unzipped[2]
    required = unzipped[3]
    absoluteValues = unzipped[4]
    values = unzipped[5]
    amino_acid_link = unzipped[6]
    color = [getColorFromProportion(prop) for prop in propOfRequirement]

    # plot
    custom_style = getCustomPygalStyle(defaultFontSize=30)
    # title=u'Amino acid/protein (mg/g)',
    bar_chart = pygal.Bar(style=custom_style,legend_at_bottom=True,x_label_rotation=40,)                                            # Then create a bar graph object
    bar_chart.add('Actual', values)
    bar_chart.add('Required', required)
    bar_chart.x_labels = amino_acids_short
    rendered_chart=bar_chart.render_data_uri()
    perGramProtInfo = {'chart':rendered_chart,'amino_acids':amino_acids,'values':values,'required':required,'propOfRequirement':propOfRequirement,'color':color,'amino_acid_link':amino_acid_link}
    return perGramProtInfo

def getColorFromProportion(prop):
    if prop>1.1:
        color = 'greenColor'
    elif prop>0.8:
        color = 'yellowColor'
    else:
        color = 'redColor'
    return color