from odoo import fields, models, api, _
import xlsxwriter
import base64
from io import BytesIO


class EmpReportWizard(models.Model):
    _name = "emp.report.excel.wizard"
    _description = "Employee Report .xlsx"

    employee_id = fields.Many2one('hr.employee', string='Employee')

    # حقل ثنائي (Binary) لتخزين ملف الإكسل الناتج
    datas = fields.Binary('File', readonly=True)
    # حقل نصي لتخزين اسم الملف (مثلاً: Employee Report.xlsx)
    datas_fname = fields.Char('File Name', readonly=True)

    def print_excel_report(self):
        # 1. قراءة البيانات المدخلة في الـ Wizard الحالي
        # self.read() تعيد قائمة بها قاموس يحتوي على قيم الحقول
        data = self.read()[0]

        # جلب القيمة من حقل Many2one والتي تكون على شكل (ID, Name)
        employee_id = data.get('employee_id')

        # 2. تحويل المعرف (ID) إلى سجل (Recordset) للوصول لبيانات الموظف
        employee = self.env['hr.employee']
        if employee_id:
            # استخدام browse للوصول للسجل باستخدام الـ ID (العنصر الأول في الـ Tuple)
            employee = employee.browse(employee_id[0])

        # 3. تعريف عناوين الأعمدة في ملف الإكسل
        headers = [
            "NAME",
            "WORK EMAIL",
            "WORK PHONE",
            "MOBILE PHONE",
            "DEPARTMENT",
        ]

        report_name = "Employee Report"

        # 4. إعداد حاوية في الذاكرة (Buffer) لتخزين ملف الإكسل مؤقتاً
        file = BytesIO()

        # إنشاء كتاب العمل (Workbook) داخل حاوية الذاكرة
        workbook = xlsxwriter.Workbook(file)

        # إضافة ورقة عمل (Sheet) جديدة وتسميتها
        worksheet = workbook.add_worksheet(report_name)

        # 5. تنسيق ودمج الخلايا للعنوان الرئيسي للتقرير
        worksheet.merge_range("A2:E2", report_name, workbook.add_format(
            {
                "bold": True,
                "font_size": "20",
                "font_name": "Georgia",
                "align": "center",
                "valign": "vcenter",
            }
        ))

        # ضبط ارتفاع الصف الثاني وعرض الأعمدة من A إلى E
        worksheet.set_row(1, 30)
        worksheet.set_column("A:E", 20)

        # 6. كتابة صف العناوين (Headers) مع تنسيق خاص (لون خلفية وخط عريض)
        worksheet.write_row('A3', headers, workbook.add_format({
            "bold": True,
            "font_size": "12",
            "font_name": "Georgia",
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#f0f0f0"
        }))

        # 7. كتابة بيانات الموظف في الصف
        worksheet.write('A4', employee.name or '')
        worksheet.write('B4', employee.work_email or '')
        worksheet.write('C4', employee.work_phone or '')
        worksheet.write('D4', employee.mobile_phone or '')
        worksheet.write('E4', employee.department_id.name or '')

        # 8. إغلاق ملف الإكسل لحفظ كافة البيانات المكتوبة في الذاكرة
        workbook.close()

        # 9. تحويل محتوى الذاكرة إلى تنسيق Base64 (المطلوب في حقول Binary في Odoo)
        out = base64.encodebytes(file.getvalue())

        # تحديث السجل الحالي بالملف الناتج واسمه
        self.write({
            "datas": out,
            "datas_fname": report_name
        })

        # إغلاق حاوية الذاكرة لتحرير الموارد
        file.close()

        # 10. إرجاع "Action" للمتصفح ليقوم بتحميل الملف فوراً
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',  # فتح التحميل في نافذة/تبويب جديد
            # إنشاء رابط التحميل الذي يشير للموديل الحالي والسجل الحالي وحقل البيانات
            'url': '/web/content/?model=' + self._name + '&id=' + str(self.id) +
                   '&field=datas&download=true&filename=' + report_name,
        }