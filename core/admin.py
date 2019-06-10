from django.contrib import admin
from core.models import CustomUser, ExcersiceData, ExcersiceDataDificultyWise


admin.site.register(CustomUser)
admin.site.register(ExcersiceData)
admin.site.register(ExcersiceDataDificultyWise)
# Register your models here.
