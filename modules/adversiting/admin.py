from django.contrib import admin
from .models import AdvSchedule, AdvPlan, AdvContent, OneNetContent, AdvDataSynch

admin.site.register(AdvSchedule)
admin.site.register(AdvPlan)
admin.site.register(AdvContent)
admin.site.register(AdvDataSynch)
admin.site.register(OneNetContent)