import base64
from io import BytesIO

import xlsxwriter
from odoo import _, api, fields, models


class XlsxPropertyWizard(models.TransientModel):
    _name = "xlsx.property.wizard"

    property_ids = fields.Many2many("property", string="Properties")
    file = fields.Binary("File", readonly=True)
    file_name = fields.Char("File Name", readonly=True)

    HEADERS = ["Name", "Post Code", "Selling Price", "Garden"]

    # --- 1. Data Retrieval Logic ---
    def _get_report_data(self):
        """Returns the recordset to be processed in the report"""
        return self.property_ids

    # --- 2. Formatting Logic ---
    def _get_header_format(self, workbook):
        """Defines and returns the format for the header row"""
        return workbook.add_format(
            {
                "bold": True,
                "bg_color": "#366092",  # Professional Blue
                "font_color": "white",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )

    def _get_data_format(self, workbook):
        """Defines and returns the standard format for data cells"""
        return workbook.add_format(
            {"border": 1, "align": "center", "valign": "vcenter"}
        )

    # --- 3. Writing Logic ---
    def _prepare_worksheet(self, worksheet):
        """Sets column widths and row heights for visual clarity"""
        worksheet.set_column("A:D", 25)  # Set width for all 4 columns
        worksheet.set_row(0, 30)  # Set height for the header row

    def _write_headers(self, worksheet, header_format):
        """Writes the static header labels to the first row"""
        worksheet.write_row(0, 0, self.HEADERS, header_format)

    def _write_body(self, worksheet, data_format):
        """Iterates through records and writes data to the worksheet"""
        row = 1
        for prop in self._get_report_data():
            worksheet.write(row, 0, prop.name or "", data_format)
            worksheet.write(row, 1, prop.postcode or "", data_format)
            worksheet.write(row, 2, prop.selling_price or 0, data_format)
            worksheet.write(row, 3, "YES" if prop.garden else "NO", data_format)
            row += 1

    # --- 4. Main Controller Function ---
    def action_download_xlsx_report(self):
        """Orchestrates the report generation process"""
        self.ensure_one()

        # Initialize the memory buffer and workbook
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Properties Report")

        # Prepare formats
        header_format = self._get_header_format(workbook)
        data_format = self._get_data_format(workbook)

        # Execute writing operations
        self._prepare_worksheet(worksheet)
        self._write_headers(worksheet, header_format)
        self._write_body(worksheet, data_format)

        # Close workbook to finalize the binary data
        workbook.close()

        # Encode the data and prepare file name
        file_data = base64.b64encode(output.getvalue())
        name = "Properties_Report.xlsx"

        # Save results back to the Wizard record
        self.write({"file": file_data, "file_name": name})
        output.close()

        # Return the download action URL
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": f"/web/content/?model={self._name}&id={self.id}&field=file&download=true&filename={name}",
        }
