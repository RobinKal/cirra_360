# Copyright (c) 2021, sujay and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class QualityDocumentGroupUpdate(Document):
    pass

@frappe.whitelist()
def daily_reminder():
    quality_document_group = frappe.db.sql("""SELECT `tabQuality Document Group`.quality_document_group_name,`tabQuality Document Group`.frequency,`tabQuality Document Group`.expected_start_date,`tabQuality Document Group`.expected_end_date,`tabQuality Document Group`.percent_complete FROM `tabQuality Document Group`;""")
    for quality_document_groups in quality_document_group:
        quality_document_group_name = quality_document_groups[0]
        frequency = quality_document_groups[1]
        date_start = quality_document_groups[2]
        date_end = quality_document_groups [3]
        progress = quality_document_groups [4]
        draft = frappe.db.sql("""SELECT count(docstatus) from `tabQuality Document Group Update` WHERE `tabQuality Document Group Update`.Quality Document Group = %s AND `tabQuality Document Group Update`.docstatus = 0;""",quality_document_group_name)
        for drafts in draft:
            number_of_drafts = drafts[0]
        update = frappe.db.sql("""SELECT name,date,time,progress,progress_details FROM `tabQuality Document Group Update` WHERE `tabQuality Document Group Update`.quality_document_group = %s AND date = DATE_ADD(CURDATE(), INTERVAL -1 DAY);""",quality_document_group_name)
        email_sending(quality_document_group_name,frequency,date_start,date_end,progress,number_of_drafts,update)


def email_sending(quality_document_group_name,frequency,date_start,date_end,progress,number_of_drafts,update):

    holiday = frappe.db.sql("""SELECT holiday_date FROM `tabHoliday` where holiday_date = CURDATE();""")
    msg = "<p>Quality Document Group Name: " + quality_document_group_name + "</p><p>Frequency: " + " " + frequency + "</p><p>Update Reminder:" + " " + str(date_start) + "</p><p>Expected Date End:" + " " + str(date_end) + "</p><p>Percent Progress:" + " " + str(progress) + "</p><p>Number of Updates:" + " " + str(len(update)) + "</p>" + "</p><p>Number of drafts:" + " " + str(number_of_drafts) + "</p>"
    msg += """</u></b></p><table class='table table-bordered'><tr>
                <th>Quality Document Group ID</th><th>Date Updated</th><th>Time Updated</th><th>Quality Document Group Status</th><th>Notes</th>"""
    for updates in update:
        msg += "<tr><td>" + str(updates[0]) + "</td><td>" + str(updates[1]) + "</td><td>" + str(updates[2]) + "</td><td>" + str(updates[3]) + "</td>" + "</td><td>" + str(updates[4]) + "</td></tr>"

    msg += "</table>"
    if len(holiday) == 0:
        email = frappe.db.sql("""SELECT user from `tabQuality User` WHERE parent = %s;""", quality_document_group_name)
        for emails in email:
            frappe.sendmail(recipients=emails,subject=frappe._(quality_document_group_name + ' ' + 'Summary'),message = msg)
    else:
    	pass
