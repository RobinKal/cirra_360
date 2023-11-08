import frappe

from frappe import _
from frappe import publish_progress
from frappe.core.doctype.file.file import create_new_folder
from frappe.utils.file_manager import save_file

@frappe.whitelist()
def attach_pdf(doc_name):
    doc = frappe.get_doc("Quality Document",doc_name)
    fallback_language = frappe.db.get_single_value("System Settings", "language") or "en"
    args = {
        "doctype": doc.doctype,
        "name": doc.name,
        "title": doc.get_title(),
        "lang": getattr(doc, "language", fallback_language),
        "show_progress": False
    }
    execute(**args)


# def enqueue(args):
#     """Add method `execute` with given args to the queue."""
#     frappe.enqueue(method=execute, queue='long',
#                    timeout=30, is_async=True, **args)


def execute(doctype, name, title, lang=None, show_progress=True):
    """
    Queue calls this method, when it's ready.
    1. Create necessary folders
    2. Get raw PDF data
    3. Save PDF file and attach it to the document
    """
    progress = frappe._dict(title=_("Creating PDF ..."), percent=0, doctype=doctype, docname=name)

    if lang:
        frappe.local.lang = lang

    if show_progress:
        publish_progress(**progress)

    # doctype_folder = create_folder(_(doctype), "Home")
    # title_folder = create_folder(title, doctype_folder)

    if show_progress:
        progress.percent = 33
        publish_progress(**progress)

    pdf_data = get_pdf_data(doctype, name)

    if show_progress:
        progress.percent = 66
        publish_progress(**progress)

    save_and_attach(pdf_data, doctype, name)

    if show_progress:
        progress.percent = 100
        publish_progress(**progress)


def create_folder(folder, parent):
    """Make sure the folder exists and return it's name."""
    new_folder_name = "/".join([parent, folder])
    
    if not frappe.db.exists("File", new_folder_name):
        create_new_folder(folder, parent)
    
    return new_folder_name


def get_pdf_data(doctype, name):
    """Document -> HTML -> PDF."""
    default_print_format = frappe.db.get_value('Property Setter', dict(property='default_print_format', doc_type=doctype), "value")
    html = frappe.get_print(doctype, name,print_format=default_print_format or 'Standard')
    return frappe.utils.pdf.get_pdf(html)


def save_and_attach(content, to_doctype, to_name):
    """
    Save content to disk and create a File document.
    File document is linked to another document.
    """
    file_name = "{}.pdf".format(to_name.replace(" ", "-").replace("/", "-"))
    save_file(file_name, content, to_doctype,
              to_name, is_private=1)

@frappe.whitelist()
def get_attach_quality_document(doc_name):
	quality_document = frappe.get_all("File",filters={"attached_to_doctype":"Quality Document","attached_to_name":doc_name},fields=["name"])
	quality_document_list = [row.name for row in quality_document]
	return quality_document_list or []

@frappe.whitelist()
def get_file_url(file_name):
    return frappe.db.get_value("File",file_name,"file_url")