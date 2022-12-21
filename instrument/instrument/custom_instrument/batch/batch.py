import frappe
from frappe.model.naming import make_autoname
from frappe.utils import nowdate, cstr, flt, cint, now, getdate,get_datetime,time_diff_in_seconds,add_to_date,time_diff_in_seconds,add_days,today
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import pyqrcode
import requests
import textwrap
import re
import xlsxwriter
def autoname(doc, method):
	if doc.item:
		now = datetime.now()
		currentMonth = datetime.now().month
		currentMonth = '{:02d}'.format(currentMonth)
		currentYear = datetime.now().year
		
		engineering_revision = frappe.db.get_value("Item",{'item_code':doc.item},'engineering_revision')
		# get_naming_prefix(doc,naming_series)
		if doc.reference_doctype == 'Purchase Receipt':
			if doc.reference_name:
				pr_doc = frappe.get_doc("Purchase Receipt",doc.reference_name)
				for item in pr_doc.items:
					if item.item_code == doc.item:
						naming_series = frappe.db.get_value("Item",{'item_code':doc.item},'batch_number_series')
						naming_prefix = get_naming_prefix(doc,item.engineering_revision,currentYear,naming_series)

						doc.name = make_autoname(naming_prefix+'-'+".#####")
						# doc.name = make_autoname('BN-' + str(item.engineering_revision) + '-'+str(currentYear) +'-'+str(currentMonth) + '-' + '.#####')
						doc.batch_id = doc.name
						return doc.name
		elif doc.reference_doctype == 'Stock Entry':
			if doc.reference_name:
				se_doc = frappe.get_doc("Stock Entry",doc.reference_name)
				for item in se_doc.items:
					if item.item_code == doc.item:
						naming_series = frappe.db.get_value("Item",{'item_code':doc.item},'batch_number_series')
						naming_prefix = get_naming_prefix(doc,item.engineering_revision,currentYear,naming_series)

						doc.name = make_autoname(naming_prefix+'-'+".#####")
						# doc.name = make_autoname('BN-' + str(item.engineering_revision) + '-'+str(currentYear) +'-'+str(currentMonth) + '-' + '.#####')
						doc.batch_id = doc.name
						return doc.name
		elif engineering_revision:
			naming_series = frappe.db.get_value("Item",{'item_code':doc.item},'batch_number_series')
			naming_prefix = get_naming_prefix(doc,engineering_revision,currentYear,naming_series)

			doc.name = make_autoname(naming_prefix+'-'+".#####")
			# doc.name = make_autoname('BN-' + str(item.engineering_revision) + '-'+str(currentYear) +'-'+str(currentMonth) + '-' + '.#####')
			doc.batch_id = doc.name
			return doc.name
		else:
			doc.name = make_autoname('BN-' + '-'+str(currentYear) +'-'+str(currentMonth) + '-' + '.#####')
			doc.batch_id = doc.name
			return doc.name

def get_naming_prefix(doc,engineering_revision,currentYear,naming_series):
	now = datetime.now()
	week_no = datetime.date(now).isocalendar()[1]
	naming_series = naming_series.split('-')
	naming_series = naming_series[0]
	new_naming = naming_series
	if 'ENG' in naming_series:
		new_naming = naming_series.replace('ENG',str(engineering_revision))
	if 'YYYY' in naming_series:
		new_naming = new_naming.replace('YYYY',str(currentYear))
	if 'WW' in naming_series:
		new_naming = new_naming.replace('WW',str(week_no))
	return new_naming



def label_img(doc, method):
	url = frappe.db.get_value('URL Data',{'sourcedoctype_name':'Batch'},'url')
	final_string = url +  doc.name
	warehouse = frappe.db.get_value('Stock Ledger Entry',{'batch_no':doc.name,'item_code':doc.item,'posting_date':doc.manufacturing_date},'warehouse')
	if not warehouse:
		warehouse = ""
	img = Image.new('RGB', (384,192), color='white')
	qrc = pyqrcode.create(final_string)
	inmf = io.BytesIO()
	qrc.png(inmf,scale=6)
	qrcimg = Image.open(inmf)
	qrcimg.thumbnail((72,72))
	img.paste(qrcimg,(26,30))
	d = ImageDraw.Draw(img)
	d.multiline_text((120,35), "{0}\n\n{1}\n\nTotal Qty: {2}\nBatch: {3}\nBatch Name: {4}\nLocation: {5}".format(doc.item,textwrap.fill(text=doc.item_name,width=40),doc.batch_qty,doc.batch_id,doc.name,warehouse), fill=(0,0,0), spacing=1)
	d.text((30,160), "Batch Traveler", fill=(0,0,0))
	barcode = requests.get('https://barcode.tec-it.com/barcode.ashx?data={0}&code=Code128&translate-esc=true'.format(doc.item))
	barc = Image.open(io.BytesIO(barcode.content))
	barc = barc.resize((220,15))
	img.paste(barc,(140,160))
	imgbuffer = io.BytesIO()
	img.save(imgbuffer, format='PNG')
	b64str = base64.b64encode(imgbuffer.getvalue())
	fname = frappe.db.get_list('File',filters={'attached_to_name':doc.name},fields=['name','file_name'])
	count=0
	if fname:
		for filedoc in fname:
			if "label" in filedoc.file_name:
				lnum = re.search("label(.*).png",filedoc.file_name)
				count = int(lnum.group(1))+1
				frappe.delete_doc('File',filedoc.name)
	namestr = doc.name + "-label{0}".format(count) + ".png"
	imgfile = frappe.get_doc({'doctype':'File','file_name':namestr,'attached_to_doctype':"Batch",'attached_to_name':doc.name,"content":b64str,"decode":1})
	imgfile.insert()
def after_insert(doc,method):
	# if not doc.get("__islocal"):
	# file_url = '/private/files/' + doc.name + '.pdf'
	# frappe.db.sql("""delete from `tabFile` where attached_to_doctype='Batch' and attached_to_name=%s and file_url = %s""",
	# (doc.name,file_url))
	start_string = doc.name 
	end_string = '.png'
	label_files = frappe.db.sql("""SELECT file_name from `tabFile` where attached_to_name = '{0}' and attached_to_doctype = 'Batch' and file_name like '{1}%{2}'""".format(doc.name,start_string,end_string),as_dict=1)
	if label_files:
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Batch' and attached_to_name=%s and file_name != %s""",
		(doc.name,label_files[0].file_name))
	else:
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Batch' and attached_to_name=%s""",
		(doc.name))
	pdf_data=frappe.attach_print('Batch',doc.name, print_format='Batch Print 8.5" x 11"')
	
	_file = frappe.get_doc({
	"doctype": "File",
	"file_name": pdf_data.get('fname'),
	"attached_to_doctype": "Batch",
	"attached_to_name": doc.name,
	"is_private": 1,
	"content": pdf_data.get('fcontent')
	})
	_file.save()
def validate(doc,method):
	# if not doc.get("__islocal"):
	# file_url = '/private/files/' + doc.name + '.pdf'
	# frappe.db.sql("""delete from `tabFile` where attached_to_doctype='Batch' and attached_to_name=%s and file_url = %s""",
	# (doc.name,file_url))
	start_string = doc.name 
	end_string = '.png'
	label_files = frappe.db.sql("""SELECT file_name from `tabFile` where attached_to_name = '{0}' and attached_to_doctype = 'Batch' and file_name like '{1}%{2}'""".format(doc.name,start_string,end_string),as_dict=1)
	if label_files:
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Batch' and attached_to_name=%s and file_name != %s""",
		(doc.name,label_files[0].file_name))
	else:
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Batch' and attached_to_name=%s""",
		(doc.name))
	pdf_data=frappe.attach_print('Batch',doc.name, print_format='Batch Print 8.5" x 11"')
	
	_file = frappe.get_doc({
	"doctype": "File",
	"file_name": pdf_data.get('fname'),
	"attached_to_doctype": "Batch",
	"attached_to_name": doc.name,
	"is_private": 1,
	"content": pdf_data.get('fcontent')
	})
	_file.save()


@frappe.whitelist()
def print_label(batch_name,part_no):
	print_label_file = frappe.db.sql("""SELECT file_name from `tabFile` where attached_to_doctype = 'Label Print' and file_name = 'batch_travller.xls'""",as_dict=1)
	if print_label_file:
		pass
	else:
		fname = 'batch_travller.xls'
		file = frappe.utils.get_site_path("public")+"/"+ fname
		book = Workbook()
	    sheet = book.active


	    heading_col1 = {'subject': 'Record No'}
	    heading_col2 = {'subject': 'Part Number'}
	    heading_col3 = {'subject': 'Part Description'}
	    heading_col4 = {'subject': 'Total Qty'}
	    heading_col5 = {'subject': 'Batch'}

	    header_list = []
	    header_list.insert(0, heading_col1)
	    header_list.insert(1, heading_col2)
	    header_list.insert(2, heading_col3)
	    header_list.insert(3, heading_col4)
	    header_list.insert(4, heading_col5)

	   
	    book.save(file)

	    

	    return fname




	
 