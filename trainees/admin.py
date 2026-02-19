from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.utils.html import format_html
from datetime import date
from .models import Trainee, Department, User, Registration
from .services import handle_excel_import



admin.site.register(Department)





@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('معلومات الموظف', {'fields': ('department',)}),)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'national_id', 'documnts')



@admin.register(Trainee)
class TraineeAdmin(admin.ModelAdmin):
    list_display = ('trainee_id', 'name', 'phone', 'department', 'paid', 'end_date', 'status_colored', 'custom_button')
    list_filter = ('department', 'paid', 'end_date')
    search_fields = ('name', 'phone', 'trainee_id')
    change_list_template = "admin/trainees_changelist.html"

    def custom_button(self, obj):
        # إذا كان منتهي، لا تظهر الزر
        #if str(obj.status) == 'منتهي' or str(obj.status) == 'Finished':
         #   return format_html('<span style="color:gray">منتهي</span>')

        # هنا نستخدم obj.id (الرقم 90)
        return format_html(
            '''
            <a href="/end-training/{}/" style="
                background-color: #d9534f;
                color: white;
                padding: 5px 10px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;">
                إنهاء التدريب
            </a>
            ''',
            obj.id
        )

    custom_button.short_description = 'إجراءات'

    def status_colored(self, obj):
        if not obj.end_date: return "-"
        days = (obj.end_date - date.today()).days
        if days < 0:
            color, bg = "red", "#ffe6e6"
            msg = f"منتهي ({abs(days)})"
        elif days <= 7:
            color, bg = "#b35900", "#fff3cd"
            msg = f"قريب ({days})"
        else:
            color, bg = "green", "#e6fffa"
            msg = f"نشط ({days})"
        return format_html(
            '<span style="color:{};background:{};padding:3px 10px;border-radius:15px;font-weight:bold;">{}</span>',
            color, bg, msg)

    status_colored.short_description = "الحالة"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(handle_excel_import), name="import-excel"),
        ]
        return custom_urls + urls

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        if request.user.department: return qs.filter(department=request.user.department)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.department_id:
            obj.department = request.user.department
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['department'].disabled = True
            form.base_fields['department'].initial = request.user.department
        return form
