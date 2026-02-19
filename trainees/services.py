import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .serializers import TraineeImportSerializer
from django import forms

class CsvImportForm(forms.Form):
    excel_file = forms.FileField(label="اختر ملف الإكسل (.xlsx)")

def handle_excel_import(request):
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        try:
            df = pd.read_excel(excel_file)
            df.columns = df.columns.str.strip()

            rename_map = {
                'Name': 'name', 'name': 'name',
                'ID': 'trainee_id', 'Id': 'trainee_id', 'id': 'trainee_id',
                'MOBILE No.': 'phone', 'MBile No.': 'phone', 'Mobile': 'phone', 'Phone': 'phone', 'phone': 'phone',
                'SPECALITY': 'speciality', 'Speciality': 'speciality', 'speciality': 'speciality', 'spec': 'speciality',
                'Starting DATE': 'start_date', 'Starting Date': 'start_date',
                'Ending Date': 'end_date', 'Ending date': 'end_date',
                'Paid': 'paid', 'paid': 'paid',
                'Group': 'group', 'group': 'group',
                'Note': 'note', 'note': 'note',
                'Department': 'department_name'
            }

            df = df.rename(columns=rename_map)
            success_count, errors = 0, []

            for index, row in df.iterrows():
                s_date = pd.to_datetime(row.get('start_date')).date() if pd.notnull(row.get('start_date')) else None
                e_date = pd.to_datetime(row.get('end_date')).date() if pd.notnull(row.get('end_date')) else None

                paid_val = row.get('paid')
                if isinstance(paid_val, str): paid_val = paid_val.strip().title()

                if request.user.is_superuser:
                    dept_name = row.get('department_name', 'General')
                else:
                    dept_name = request.user.department.name if request.user.department else 'General'

                data = {
                    "trainee_id": row.get('trainee_id'),
                    "name": row.get('name'),
                    "phone": row.get('phone'),
                    "speciality": row.get('speciality'),
                    "start_date": s_date,
                    "end_date": e_date,
                    "paid": paid_val,
                    "group": row.get('group'),
                    "note": row.get('note', '') if pd.notnull(row.get('note')) else '',
                    "department_name": dept_name
                }

                serializer = TraineeImportSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    success_count += 1
                else:
                    errors.append(f"سطر {index + 2}: {serializer.errors}")

            if success_count > 0: messages.success(request, f"تم استيراد {success_count} متدرب.")
            if errors: messages.warning(request, f"أخطاء: {errors[:2]}")

        except Exception as e:
            messages.error(request, f"خطأ: {e}")
        return redirect("..")

    form = CsvImportForm()
    return render(request, "admin/excel_form.html", {"form": form})
