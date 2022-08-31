from odoo import models, fields, _
import xlrd
import tempfile
import binascii
from datetime import datetime
from odoo.tests.common import Form


class FleksDataWizard(models.Model):
    _name = 'fleks.data.wizard'
    _description = 'Fleks Data Migration Wizard'

    name = fields.Char('Name', required=True, copy=False)
    file = fields.Binary('File', required=True, copy=False)
    filename = fields.Char('File Name', copy=False)
    state = fields.Selection(string="Status",
                             selection=[('purchase', "Purchase"), ('sale', "Sale")],
                             default='purchase', required=True, copy=False)

    def import_data(self):
        try:
            file_string = tempfile.NamedTemporaryFile(suffix=".xlsx")
            file_string.write(binascii.a2b_base64(self.file))
            book = xlrd.open_workbook(file_string.name)
            sheet = book.sheet_by_index(0)
        except Exception as e:
            print(e)
            raise Warning(_("Please choose the correct file"))

        counter = 0

        for i in range(sheet.nrows):
            if counter == 0:
                counter += 1
                continue
            line = list(sheet.row_values(i))
            serial_number = line[1]
            po_no = line[2]
            if self.state == 'purchase':
                picking_obj = self.env['stock.picking'].sudo().search([('origin','=',po_no)], limit=1)
                if picking_obj:
                    move_obj = self.env['stock.move'].sudo().search([('picking_id','=',picking_obj.id)], limit=1)
                    if move_obj:
                        value_list = [
                            serial_number
                        ]
                        values = '\n'.join(value_list)

                        move_form = Form(move_obj, view='stock.view_stock_move_nosuggest_operations')
                        with move_form.move_line_nosuggest_ids.new() as line:
                            line.lot_name = values
                        move = move_form.save()

        return {'type': 'ir.actions.act_window_close'}



