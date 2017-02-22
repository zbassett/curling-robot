from django.contrib import admin

from .models import Club
admin.site.register(Club)

from .models import Sheet
admin.site.register(Sheet)

from .models import Person
admin.site.register(Person)

from .models import Rock
admin.site.register(Rock)

