from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
#from django.template import loader
from django.shortcuts import render, render_to_response
from django.shortcuts import redirect
#from django.http import Http404
from django.utils import timezone
# from django.urls import reverse
from django.views import generic
from django.views.generic import CreateView
from django.utils.encoding import smart_text
from django.db.models import Q #or in queryset
import numpy as np

from .models import Food, NutritionalValue, RelativeAminoScore #, Ingredient, Menu
from .models import Recipe, Ingredient, FoodPair, Nutriment, TargetAminoPattern #, NutrientDefinition

#from utilities.loadFromUsda import loadFoodNutrimentInfo
from aminoApp.utilityFunctions import readFoodNutrimentInfo, getAminoEfficiencyFromNutrimentValue, getAminoProportionsOfComplete
from aminoApp.utilityFunctions import getAminoAcidNames, saveRelativeAminoScores
from aminoApp.utilityFunctions import analyseFoodPair, getBestProportionsForFoods, getCustomPygalStyle
from aminoApp.utilityFunctions import  getFoodAminoPlotAbsolute, getFoodAminoPlotProportions, getMacroNutrientPie, getTargetAminoPlot, getRecipeAminoPlotProportions
from aminoApp.utilityFunctions import getRequirementsPerGramProtein
from .forms import FoodPairForm

from .forms import IngredientFormSet, RecipeForm, NumberForm


import pygal

class IndexView(generic.ListView):
    template_name = 'aminoApp/index.html'
    context_object_name = 'latest_food_list'

    def get_queryset(self):
        """Return the last five published foods."""
        return Food.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        context['lastest_recipe_list'] = Recipe.objects.order_by('-date_added')[:5]
        return context

class DetailView(generic.DetailView):
    model = Food
    template_name = 'aminoApp/detail.html'


def __unicode__(self):
    return smart_text(self.tag)

def loadFoodNames(request):
    #load food non-nutritional information from text file
    f = open(r'/home/tetramino/aminoProject/aminoApp/sourceData/FOOD_DES_unicorrected.txt','r')
    idOfLine=0
    s=''
    response = HttpResponse()
    while idOfLine<8000:
        ligneLue=f.readline()
        splLine=ligneLue.split('~')
        idOfLine=idOfLine+1 #float(splLine[1])
        foodId=int(splLine[1])
        foodName=splLine[5]
        s=s+foodName+' and '
        #if idOfLine==iFood:
        response.write("<p>"+foodName+'('+str(foodId)+").")
        response.write('<a href="/aminoApp/isFoodInDatabase/'+str(foodId)+'/">in database?</a></p>')
    # should we also create Food instances? yes
    return response

def loadFoodNamesKnowingIfLoaded(request):
    # as opposed to previous function loadFoodNames, we also show if food is already in the database
    f = open(r'/home/tetramino/aminoProject/aminoApp/sourceData/FOOD_DES_unicorrected.txt','r')
    idOfLine=0
    response = HttpResponse()
    loadedFoodIds=Food.objects.values_list('food_dbid',flat=True)
    while idOfLine<8000:
        ligneLue=f.readline()
        splLine=ligneLue.split('~')
        idOfLine=idOfLine+1 #float(splLine[1])
        foodId=int(splLine[1])
        foodCat=int(splLine[3])
        #interestingCategories = [100,900,1100,1200,1600,1800,2000]
        interestingCategories = [100,200,900,1100,1200,1600,1800,2000]
        if foodCat > 1: #foodCat in interestingCategories:
            foodName=splLine[5]
            response.write("<p>"+foodName+'('+str(foodId)+"). ")
            if foodId in loadedFoodIds:
                response.write('Already in database</p>')
            else:
                response.write('<a href="/loadFoodInDatabase/'+str(foodId)+'/">load</a></p>')
    return response

# check food id: is it in sql database, is it loaded
# def isFoodInDatabase(request):
#     return HttpResponse("Hello, world. You want to know if there is db entry for food id")

def isFoodInDatabase(request, food_dbid):
    response=HttpResponse("You want to know if there is db entry for food id"+str(food_dbid)+". ")
    try:
        food=Food.objects.get(food_dbid=food_dbid)
        response.write("There is! It is called "+food.food_name)
    except:
        response.write('There is  not. Create it <a href="/aminoApp/loadFoodInDatabase/'+str(food_dbid)+'/">here</a>')
    #question = get_object_or_404(Food, food_dbid=food_dbid)

    return response
    #return render(request, 'polls/detail.html', {'question': question})

# create food in sql
def loadFoodInDatabase(request, food_dbid):
    # warning: food_dbid is a string! see type(food_dbid).__name__
    #load food non-nutritional information from text file
    #f = open(r'/home/tetramino/aminoProject/aminoApp/sourcedata/FOOD_DES.txt','r')
    response=HttpResponse('Loading food in db <br>')

    if len(Food.objects.filter(food_dbid=food_dbid))>0:
        response.write('food id already in database! we do not add it once more')
    else:
        foodFound=0
        with open(r'/home/tetramino/aminoProject/aminoApp/sourceData/FOOD_DES_unicorrected.txt','r') as fp:
            for lineInFile in fp:
                splLine=lineInFile.split('~')
                foodId=int(splLine[1])
                if foodId==int(food_dbid):
                    foodName=splLine[5]
                    foodcat=int(splLine[3])
                    foodFound=1
                    break

        if foodFound:
            food = Food(food_name=foodName, food_dbid=int(food_dbid),food_category=foodcat)
            # newfood.save()
            # we wait until we know nut info is ok to save food

            # load food nutriment and put in sql
            searchId=int(food_dbid)
            response=HttpResponse('Loaded nut info for '+foodName+':<br>')
            nutValue=readFoodNutrimentInfo(searchId)
            # for nutid in nutValue:
                # response.write(str(nutid)+':'+str(nutValue[nutid])+'<br>')
            # food=Food.objects.get(food_dbid=food_dbid)
            # very unsatisfactory this:
            necessaryKeys=[501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,
                            203,204,205,207,208,255,291,301,303,304,305,306,307,309,312,315]
            if all([nk in nutValue.keys() for nk in necessaryKeys]):
                foodNutVal=NutritionalValue(trp_g=nutValue[501],thr_g=nutValue[502],ile_g=nutValue[503],leu_g=nutValue[504],lys_g=nutValue[505],met_g=nutValue[506],
                    cys_g=nutValue[507],phe_g=nutValue[508],tyr_g=nutValue[509],val_g=nutValue[510],his_g=nutValue[512],
                    arg_g=nutValue[511],ala_g=nutValue[513],asp_g=nutValue[514],glu_g=nutValue[515],gly_g=nutValue[516],pro_g=nutValue[517],ser_g=nutValue[518],
                    prot=nutValue[203],fat=nutValue[204],carbo=nutValue[205],ash=nutValue[207],energ=nutValue[208],water=nutValue[255],fiber=nutValue[291],
                    ca=nutValue[301],fe=nutValue[303],mg=nutValue[304],p=nutValue[305],k=nutValue[306],
                    na=nutValue[307],zn=nutValue[309],cu=nutValue[312],mn=nutValue[315],
                    description='nutrValueFood'+food_dbid)
                # nullable fields: prot_adj=nutValue[257], sugars=nutValue[269],alc=nutValue[221],
                optionalKeys = [221,257,269,317]
                availableOptionalKeys = [k for k in optionalKeys if k in nutValue.keys()]
                for aok in availableOptionalKeys:
                    nutr = Nutriment.objects.get(dbid=aok)
                    setattr(foodNutVal,nutr.internal_name,nutValue[aok])
                foodNutVal.save()
                # response.write('foodNutVal should be aved')
                food.nutritional_value=foodNutVal
                food.save()
                return redirect("/listFoodNutValues/"+str(food_dbid))
                # return response
            else:
                missingKeys=[k for k in necessaryKeys if k not in nutValue.keys()]
                response.write('Missing nutrient data'+str(missingKeys))
        else:
            response.write("Food id "+str(food_dbid)+' not in db')
    return response


# # load food nutriment and put in sql
# def loadFoodNutrimentInfo(request,food_dbid):
#     searchId=int(food_dbid)
#     response=HttpResponse('Loaded nut info: ')
#     nutValue=readFoodNutrimentInfo(searchId)
#     for nutid in nutValue:
#         response.write(str(nutid)+':'+str(nutValue[nutid])+'<br>')
#     food=Food.objects.get(food_dbid=food_dbid)
#     # very unsatisfactory this:
#     foodNutVal=NutritionalValue(trp_g=nutValue[501],thr_g=nutValue[502],ile_g=nutValue[503],leu_g=nutValue[504],lys_g=nutValue[505],met_g=nutValue[506],
#         cys_g=nutValue[507],phe_g=nutValue[508],tyr_g=nutValue[509],val_g=nutValue[510],his_g=nutValue[512],
#         prot=nutValue[203],fat=nutValue[204],carbo=nutValue[205],energ=nutValue[208],
#         sugars=nutValue[269],ca=nutValue[301],fe=nutValue[303],mg=nutValue[304],p=nutValue[305],k=nutValue[306],
#         description='nutrValueForFood'+food_dbid)
#     # nullable fields: prot_adj=nutValue[257],
#     foodNutVal.save()
#     response.write('foodNutVal should be aved')
#     food.nutritional_value=foodNutVal
#     food.save()
#     return response


def getFoodEfficiency(request,food_dbid):
    food=Food.objects.get(food_dbid=food_dbid)
    foodValue=food.nutritional_value
    # foodAminoVector=foodValue.getAminoVector()
    # completeProteinValue=NutritionalValue.objects.get(description='complete_protein_62kg')
    # completeAminoVector=completeProteinValue.getAminoVector()
    # aminoEff=getAminoEfficiencyFromVector(foodAminoVector,completeAminoVector)
    aminoEff=getAminoEfficiencyFromNutrimentValue(foodValue)
    return HttpResponse("Efficiency of food: "+str(aminoEff))

def listFoodValues(request,food_dbid):
    food=Food.objects.get(food_dbid=food_dbid)
    foodValue=food.nutritional_value
    valueDict = foodValue.getValueDict()
    stringList = []
    tupleList = []
    for key in valueDict:
        nutrient=Nutriment.objects.get(internal_name=key)
        longName = nutrient.public_name
        value = valueDict[key]
        unit = nutrient.unit
        categ = nutrient.category
        # totalDict[key]={'longName':nutrient.public_name,'unit':nutrient.unit,'value':valueDict[key]}
        stringList.append(longName + str(value) + unit)
        tupleList.append((longName,value,unit,categ))
    orderedTupleList = sorted(tupleList, key=lambda tup:tup[3])

    context = {'orderedTupleList':orderedTupleList,'food': food}
    return render(request, 'aminoApp/listNutritionalValues.html', context)

def pairSearchReturn(request):
    if 'foodOne' in request.GET and 'foodTwo' in request.GET:
        message = 'You searched for: %r' % request.GET['foodOne']
        foodOne=Food.objects.get(food_dbid=request.GET['foodOne'])
        foodTwo=Food.objects.get(food_dbid=request.GET['foodTwo'])
        context = analyseFoodPair(foodOne,foodTwo)
        response = render(request, 'aminoApp/inspectFoodPair.html', context)
    else:
        message = 'You submitted an empty form.'
        response = HttpResponse(message)
    return response
    # return HttpResponse(message)

def pairSearchReturnCreation(request):
    if 'foodOne' in request.GET and 'foodTwo' in request.GET:
        message = 'You searched for: %r' % request.GET['foodOne']
        foodOne=Food.objects.get(pk=request.GET['foodOne'])
        foodTwo=Food.objects.get(pk=request.GET['foodTwo'])
        context = analyseFoodPair(foodOne,foodTwo)
        nameOfPair = foodOne.getNameBegin() + '-' + foodTwo.getNameBegin() #foodOne.food_name[0:12]+'-'+foodTwo.food_name[0:12]
        newpair = FoodPair(foodOneId=foodOne.food_dbid, foodTwoId=foodTwo.food_dbid,
                           pair_name=nameOfPair,
                           bestEfficiency=context['bestEfficiency'],bestProportion=context['bestPropOne'],
                           )
        newpair.save()
        return redirect("/inspectLoadedFoodPair/"+str(newpair.pk))

    else:
        message = 'You submitted an empty form.'
        response = HttpResponse(message)
    return response
    # return HttpResponse(message)

def inspectLoadedFoodPair(request,pair_id):
    pair=FoodPair.objects.get(pk=pair_id)
    foodOne=Food.objects.get(food_dbid=pair.foodOneId)
    foodTwo=Food.objects.get(food_dbid=pair.foodTwoId)
    context = analyseFoodPair(foodOne,foodTwo)
    pair.bestEfficiency = context['bestEfficiency']
    pair.bestProportion = context['bestPropOne']
    pair.angleAbsolute = context['angle']['absolute']
    pair.angleIncomplete = context['angle']['incomplete']
    pair.save()
    return render(request, 'aminoApp/inspectFoodPair.html', context)
    # d) save menu based on food pair

def bestProportionsOfRecipeFoods(request,recipeid):
    # recipe=Recipe.objects.get(pk=recipeid)
    ingreds = Ingredient.objects.filter(recipe = recipeid)
    foods=[ingr.food for ingr in ingreds]
    context = getBestProportionsForFoods(foods)
    return render(request, 'aminoApp/bestProportionsFoods.html', context)



def showFoodList(request):
    foodList= Food.objects.order_by('food_name') #('-pub_date')[:25]
    context = {'foodList': foodList}
    return render(request, 'aminoApp/foodList.html', context)

def showFoodTable(request):
    foodList= Food.objects.order_by('-pub_date')[:25]
    context = {'foodList': foodList}
    return render(request, 'aminoApp/foodTable.html', context)

def showRecipeTable(request):
    recipeList= Recipe.objects.order_by('-date_added')[:25]
    context = {'recipeList': recipeList}
    return render(request, 'aminoApp/recipeTable.html', context)

def showFoodPairList(request):
    pairList= FoodPair.objects.order_by('-pk')[:25]
    context = {'pairList': pairList}
    return render(request, 'aminoApp/foodPairTable.html', context)

def choosePair(request):
    form = FoodPairForm() #FoodForm(initial={'foodOne': 61})
    return render(request, 'aminoApp/foodPairForm.html', {'form': form})




def plotFoodAmino(request,food_dbid):
    food=Food.objects.get(food_dbid=food_dbid)
    foodAminoVector=food.nutritional_value.getAminoVector()
    foodAminoProportions = getAminoProportionsOfComplete(foodAminoVector)

    # custom_style = getCustomPygalStyle()
    # bar_chart = pygal.Bar(title=u'Amino acid quantities (g)',style=custom_style)                                            # Then create a bar graph object
    # bar_chart.add('Amino acids', foodAminoVector)  # Add some values
    # # amino_acid_names = ('trp_g','thr_g','ile_g','leu_g','lys_g','met_g','cys_g','phe_g','tyr_g','val_g','his_g')
    amino_acid_names = getAminoAcidNames()
    # bar_chart.x_labels = amino_acid_names

    # foodAminoProportions = getAminoProportionsOfComplete(foodAminoVector)
    # bar_chart.add('Balanced equivalent', foodAminoProportions['projected'])  # Add some values
    # chartAbsolute=bar_chart.render_data_uri()
    chartAbsolute = getFoodAminoPlotAbsolute(food)

    projProps = foodAminoProportions['propsOfProj']
    minIndex = np.argmin(projProps)
    minAminoAcid = Nutriment.objects.get(internal_name=amino_acid_names[minIndex])
    maxIndex = np.argmax(projProps)
    maxAminoAcid = Nutriment.objects.get(internal_name=amino_acid_names[maxIndex])


    #bar_chart_prop = pygal.Bar(title=u'Amino acid proportions (divided by limiting amino acid)')                                            # Then create a bar graph object
    # bar_chart_prop = pygal.Bar(title=u'Amino acid proportions (divided by quantities in equivalent perfectly-balanced food)',style=custom_style)
    # bar_chart_prop.add('Amino acids', foodAminoProportions['propsOfProj'])
    # bar_chart_prop.x_labels = amino_acid_names
    # chart_prop=bar_chart_prop.render_data_uri()
    chart_prop = getFoodAminoPlotProportions(food)

    context = {'food': food,'chart':chartAbsolute,'propChart':chart_prop,
            'minAminoAcid':minAminoAcid,'maxAminoAcid':maxAminoAcid}

    return render(request, 'aminoApp/aminoPlot.html', context)



def plotRecipeAmino(request,recipeid):
    recipe=Recipe.objects.get(pk=recipeid)
    # here we should check if menu has at least one ingredient
    menuNutrValue=recipe.get_nutritional_value()
    menuAminoVector = menuNutrValue.getAminoVector()
    projectVectorOnComplete = getAminoProportionsOfComplete(menuAminoVector)
    equivCompleteVector = projectVectorOnComplete['projected']
    ingreds = Ingredient.objects.filter(recipe = recipeid) # ingreds = recipe.ingredients.all()

    custom_style = getCustomPygalStyle()
    bar_chart = pygal.StackedBar(title=u'Amino acid quantities (g)',style=custom_style)                                            # Then create a bar graph object
    amino_acid_names = getAminoAcidNames()
    bar_chart.x_labels = amino_acid_names
    bar_chart_props = pygal.StackedBar(title=u'Amino acid proportions',style=custom_style)
    bar_chart_props.x_labels = amino_acid_names

    for ingr in ingreds:
        ingrNutrVal=ingr.get_nutritional_value()
        ingrAminoVector=ingrNutrVal.getAminoVector()
        ingrAminoProps = np.divide(ingrAminoVector, equivCompleteVector)
        bar_chart.add(str(ingr), ingrAminoVector) #ingr.food.food_name
        bar_chart_props.add(str(ingr), ingrAminoProps)

    # get_nutritional_value(self)

    # chart = bar_chart.render_django_response()
    # return chart
    # menuEff=getAminoEfficiencyFromNutrimentValue(menuNutrValue)
    chart=bar_chart.render_data_uri()
    chart_props=bar_chart_props.render_data_uri()
    context = {'recipe': recipe,'chart':chart,'chart_props':chart_props}
    return render(request, 'aminoApp/recipeAminoPlot.html', context)

def presentTargetPattern(request,patternId):
    pattern = TargetAminoPattern.objects.get(pk=patternId)
    chart = getTargetAminoPlot(pattern.nutritional_value)
    context = {'pattern': pattern,'chart':chart}
    return render(request, 'aminoApp/presentTargetPattern.html', context)

def about(request):
    return render(request, 'aminoApp/about.html')

def aboutSomething(request,subject):
    if subject in ('definitions','sources','examples','contact','limitations','disclaimer','further_reading'):
        templateAddress = 'aminoApp/about_'+subject+'.html'
        return render(request, templateAddress)
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

class recipeCreateView(CreateView):
    template_name = 'aminoApp/recipe_add.html'
    model = Recipe
    form_class = RecipeForm
    success_url = 'success/'


    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        ingredient_form = IngredientFormSet()



        number_form = NumberForm()
        if 'nExtras' in self.kwargs:
            nIngredients = int(self.kwargs['nExtras'])
            if nIngredients < 10:
                ingredient_form.extra = nIngredients
        if 'nExtras' in request.GET:
            nIngredients = int(request.GET['nExtras'])
            if nIngredients < 10:
                ingredient_form.extra = nIngredients
        # instruction_form = InstructionFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  ingredient_form=ingredient_form,
                                  number_form=number_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        ingredient_form = IngredientFormSet(self.request.POST)

        if (form.is_valid() and ingredient_form.is_valid()):
            return self.form_valid(form, ingredient_form)
        else:
            return self.form_invalid(form, ingredient_form)

    def form_valid(self, form, ingredient_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        ingredient_form.instance = self.object
        ingredient_form.save()
        # return HttpResponseRedirect(self.get_success_url())
        return redirect("/showRecipe/"+str(self.object.pk))

    def form_invalid(self, form, ingredient_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  ingredient_form=ingredient_form))

def showRecipe(request,recipeid):
    recipe = Recipe.objects.get(pk=recipeid)
    ingredients = Ingredient.objects.filter(recipe = recipeid)
    # menuNutrValue=menu.get_nutritional_value()
    # menuEff=getAminoEfficiencyFromNutrimentValue(menuNutrValue)
    # response = HttpResponse("Recipe "+recipe.title+": ")
    # for ingr in ingredients:
    #     response.write(str(ingr))
    recipeNutrValue=recipe.get_nutritional_value()
    recipeEff=getAminoEfficiencyFromNutrimentValue(recipeNutrValue)
    recipe.efficiency=recipeEff
    recipe.save()

    chartProps = getRecipeAminoPlotProportions(recipe)
    # response.write('Efficiency'+str(recipeEff))
    # return response

    # per grams of protein
    # chartPerProtein = getRequirementsPerGramProtein(foodValue)
    perGramProtInfo = getRequirementsPerGramProtein(recipeNutrValue)

    chartPerProtein = perGramProtInfo['chart']
    zippedInfoPerGramProt = zip(perGramProtInfo['amino_acids'],perGramProtInfo['values'],perGramProtInfo['required'],perGramProtInfo['color'],perGramProtInfo['amino_acid_link'])
    # zippedInfoPerGramProt = sorted(zippedInfoPerGramProt, key = lambda t: t[1])
    context = {'efficiency': recipeEff,'ingredients':ingredients,'recipe':recipe,'chartProps':chartProps,'zippedInfoPerGramProt':zippedInfoPerGramProt,'chartPerProtein':chartPerProtein,}
    return render(request, 'aminoApp/presentRecipe.html', context)

def showFood(request,food_dbid):
    food = Food.objects.get(food_dbid=food_dbid)
    foodValue = food.nutritional_value
    # recalculate efficiency
    aminoEff = getAminoEfficiencyFromNutrimentValue(foodValue)
    food.efficiency = aminoEff
    food.save()
    # get graph (absolute amino acid values)
    chartAbsolute = getFoodAminoPlotAbsolute(food)
    # amino scores: min and max
    foodAminoVector=food.nutritional_value.getAminoVector()
    foodAminoProportions = getAminoProportionsOfComplete(foodAminoVector)
    amino_acid_names = getAminoAcidNames()
    projProps = foodAminoProportions['propsOfProj']
    minIndex = np.argmin(projProps)
    minAminoAcid = Nutriment.objects.get(internal_name=amino_acid_names[minIndex])
    maxIndex = np.argmax(projProps)
    maxAminoAcid = Nutriment.objects.get(internal_name=amino_acid_names[maxIndex])

    # amino acid scores (save)
    saveRelativeAminoScores(food)
    # per grams of protein
    # chartPerProtein = getRequirementsPerGramProtein(foodValue)
    perGramProtInfo = getRequirementsPerGramProtein(foodValue)
    # perGramProtInfo = {'chart':rendered_chart,'values':values,'required':required,'propOfRequirement':propOfRequirement}
    chartPerProtein = perGramProtInfo['chart']
    # zippedInfoPerGramProt = zip(perGramProtInfo['amino_acids'],perGramProtInfo['values'],perGramProtInfo['required'])
    zippedInfoPerGramProt = zip(perGramProtInfo['amino_acids'],perGramProtInfo['values'],perGramProtInfo['required'],perGramProtInfo['color'],perGramProtInfo['amino_acid_link'])
    # pie chart
    pieChartMacro = getMacroNutrientPie(foodValue)
    # pairs
    # pairs including food
    pairList= FoodPair.objects.filter(Q(foodOneId=food.food_dbid) | Q(foodTwoId=food.food_dbid)).order_by('-pk')[:25]
    # pairList= FoodPair.objects.filter(foodOneId=food.food_dbid| foodTwoId=food.food_dbid).order_by('-pk')[:25]
    # form to look for pairs
    formForPair = FoodPairForm(initial={'foodOne': food.pk}) #FoodForm(initial={'foodOne': 61})

    context = {'food': food,'chartAbsolute': chartAbsolute,'pairList':pairList,'formForPair':formForPair,
        'minAminoAcid':minAminoAcid,'maxAminoAcid':maxAminoAcid,'pieChartMacro':pieChartMacro,
        'chartPerProtein':chartPerProtein,'zippedInfoPerGramProt':zippedInfoPerGramProt}

    return render(request, 'aminoApp/presentFood.html', context)


def presentAminoAcid(request,internal_name):
    aminoDefinition = Nutriment.objects.get(internal_name=internal_name)
    # high and low scores of foods for this amino acid
    scores = RelativeAminoScore.objects.filter(aminoAcid=aminoDefinition).order_by('score')
    highScores = scores.filter(score__gt=1).order_by('-score')[0:20]
    lowScores = scores.filter(score__lt=1)[0:20]
    filterProp = '-nutritional_value__'+internal_name
    highContentFoods = Food.objects.order_by(filterProp)[0:20]
    highContentFoodsAndQuantities = [{'food':food,'quantity':getattr(food.nutritional_value,internal_name)} for food in highContentFoods]
    # highContentFoods = [() for ]
    context = {'aminoAcid': aminoDefinition,'highScores':highScores,'lowScores':lowScores,'highContentFoodsAndQuantities':highContentFoodsAndQuantities}
    return render(request, 'aminoApp/presentAminoAcid.html', context)

def showAminoAcidList(request):
    aminoAcids= Nutriment.objects.filter(category='amino acid (essential)').order_by('public_name')[:25]
    context = {'aminoAcids': aminoAcids}
    return render(request, 'aminoApp/aminoAcidList.html', context)
