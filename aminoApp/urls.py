from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

app_name = 'aminoApp'



urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^loadFoods/', views.loadFoodNamesKnowingIfLoaded, name='index'),
    url(r'^listFoods/', views.showFoodList, name='foodList'),
    url(r'^listFoodTable/', views.showFoodTable, name='foodTable'),
    # url(r'^menuTable/', views.showMenuTable, name='menuTable'),
    url(r'^recipeTable/', views.showRecipeTable, name='recipeTable'),
    url(r'^foodPairList/', views.showFoodPairList, name='foodPairTable'),
    url(r'^about/', views.about, name='about'),
    url(r'^about_(?P<subject>[\w]+)/', views.aboutSomething, name='aboutSomething'),

    url(r'^choosePair/', views.choosePair, name='choosePair'),
    # url(r'^composeMenu/', views.composeMenu, name='composeMenu'),
    url(r'^composeRecipe/', views.recipeCreateView.as_view(), name='composeRecipe'),
    url(r'^composeRecipeIngrNr/(?P<nExtras>[0-9]+)/', views.recipeCreateView.as_view(), name='composeRecipe'),
    url(r'^pairSearchReturn/', views.pairSearchReturnCreation),
    url(r'^isFoodInDatabase/(?P<food_dbid>[0-9]+)/$', views.isFoodInDatabase, name='isItThere'),
    url(r'^loadFoodInDatabase/(?P<food_dbid>[0-9]+)/$', views.loadFoodInDatabase, name='loadIt'),
    url(r'^loadFoodNutInfoInDatabase/(?P<food_dbid>[0-9]+)/$', views.loadFoodNutrimentInfo, name='loadNut'),
    url(r'^listFoodNutValues/(?P<food_dbid>[0-9]+)/$', views.listFoodValues, name='listFoodNutValues'),
    url(r'^getFoodEfficiency/(?P<food_dbid>[0-9]+)/$', views.getFoodEfficiency, name='foodEff'),
    url(r'^plotFoodAmino/(?P<food_dbid>[0-9]+)/$', views.plotFoodAmino, name='foodAminoPlot'),
    url(r'^plotRecipeAmino/(?P<recipeid>[0-9]+)/$', views.plotRecipeAmino, name=''),
    # url(r'^plotMenuAmino/(?P<menuid>[0-9]+)/$', views.plotMenuAmino, name='menuAminoPlot'),
    # url(r'^getMenuEfficiency/(?P<menuid>[0-9]+)/$', views.getMenuEfficiency, name='menuEff'),
    url(r'^showRecipe/(?P<recipeid>[0-9]+)/$', views.showRecipe, name='r'),
    url(r'^showFood/(?P<food_dbid>[0-9]+)/$', views.showFood, name='presentFood'),
    # url(r'^inspectFoodPair/(?P<food_dbid_one>[0-9]+)_(?P<food_dbid_two>[0-9]+)/$', views.inspectFoodPair, name='foodPair'),
    url(r'^inspectLoadedFoodPair/(?P<pair_id>[0-9]+)/$', views.inspectLoadedFoodPair, name='foodPair'),
    url(r'^bestProportionsOfRecipeFoods/(?P<recipeid>[0-9]+)/$', views.bestProportionsOfRecipeFoods, name='assocBestProps'),
    url(r'^aminoAcid_(?P<internal_name>[\w]+)/', views.presentAminoAcid, name='presentAminoAcid'),
    url(r'^listAminoAcids/', views.showAminoAcidList, name='listAminoAcid'),
]

urlpatterns += staticfiles_urlpatterns()
