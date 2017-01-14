from django import forms
# from django.forms.formsets import BaseFormSet
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from .models import Food
from .models import Recipe, Ingredient

class NumberForm(forms.Form):
    # choose an integer between 1 and 10
    int_choices = (
        (1,'1'),
    )
    for ii in range(2,10):
        int_choices = int_choices + ((ii,int(ii)),)
    nExtras = forms.ChoiceField(choices = int_choices, label = 'Number of ingredients')

class FoodPairForm(forms.Form):
    # get food choices (can this be put in function?)
    # foodList= Food.objects.order_by('-pub_date')[:25]
    # # foodOne = foodList[1]
    # food_choices = (
    #     (0,'choose one'),
    # )
    # for food in foodList:
    #     food_choices = food_choices + ((food.food_dbid,food.food_name),)
    # # define fields
    # foodOne = forms.ChoiceField(choices = food_choices, label = 'First food')
    # foodTwo = forms.ChoiceField(choices = food_choices, label = 'Second food')
    foodOne = forms.ModelChoiceField(queryset=Food.objects.order_by('food_name'), empty_label="(select food)")
    foodTwo = forms.ModelChoiceField(queryset=Food.objects.order_by('food_name'), empty_label="(select food)")

class MenuForm(forms.Form):
    # SUPERSEDED
    # # get food choices (can this be put in function?)
    # foodList= Food.objects.order_by('-pub_date')[:25]
    # # foodOne = foodList[1]
    # food_choices = ((0,'choose one'),)
    # for food in foodList: #foodList[2:]:
    #     food_choices = food_choices + ((food.food_dbid,food.food_name),)
    # define fields
    name = forms.CharField(label='Menu name', max_length=25)
    # foodOne = forms.ChoiceField(choices = food_choices, label = 'Food one')
    foodOne = forms.ModelChoiceField(queryset=Food.objects.all())
    quantOne = forms.FloatField(label='Quantity of food one')
    # foodTwo = forms.ChoiceField(choices = food_choices, label = 'Food two')
    foodTwo = forms.ModelChoiceField(queryset=Food.objects.all())
    quantTwo = forms.FloatField(label='Quantity of food two')
    # later: dynamic field generation
    # https://jacobian.org/writing/dynamic-form-generation/
    # http://stackoverflow.com/questions/5478432/making-a-django-form-class-with-a-dynamic-number-of-fields
    # http://kevindias.com/writing/django-class-based-views-multiple-inline-formsets/

# class IngredientForm(forms.Form):
#     foodList= Food.objects.order_by('-pub_date')[:95]
#     food_choices = ((0,'choose one'),)
#     for food in foodList:
#         food_choices = food_choices + ((food.food_dbid,food.food_name),)
#     food_i = forms.ChoiceField(choices = food_choices, label = 'Food')
#     quant_i = forms.FloatField(label='Quantity of food')

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        # fields = '__all__'
        exclude = ('efficiency', 'aa_score', 'date_added', )

IngredientFormSet = inlineformset_factory(Recipe, Ingredient, extra=3, fields=('food','quantity',))

# initial does not work with inlineformset_factory
# IngredientFormSet = inlineformset_factory(Recipe, Ingredient, extra=3, fields='__all__')

# InstructionFormSet = inlineformset_factory(Recipe, Instruction, fields='__all__')

