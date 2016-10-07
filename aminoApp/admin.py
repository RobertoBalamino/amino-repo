from django.contrib import admin

from .models import Food, NutritionalValue, Recipe, Ingredient, FoodPair, Nutriment
from .models import RelativeAminoScore, TargetAminoPattern
#admin.site.register(Question)
#admin.site.register(Choice)

admin.site.register(Food)
admin.site.register(NutritionalValue)
# admin.site.register(Ingredient)
# admin.site.register(Menu)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(FoodPair)
admin.site.register(Nutriment)
admin.site.register(RelativeAminoScore)
admin.site.register(TargetAminoPattern)
