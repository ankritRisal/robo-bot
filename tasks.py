from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

import os




@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()

    orders = get_orders()

    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        # preview_order()
        submit_order()
        store_receipt_as_pdf(order['Order number'])
        screenshot_robot(order['Order number'])
        embed_screenshot_to_receipt(order['Order number'])
        order_another_robot()
    archive_receipts()



def open_robot_order_website():
    # TODO: Implement your function here
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    
    # download HTTP files
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    
    #read as table 
    tables = Tables()
    orders = tables.read_table_from_csv("orders.csv")
    
    return orders

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def fill_the_form(order):

    page = browser.page()
    
    page.select_option("#head",order['Head'])
    page.click(f'input[name="body"][value="{order["Body"]}"]')
    page.fill('input[placeholder="Enter the part number for the legs"]', order['Legs'])
    page.fill("#address", order["Address"])

def preview_order():
    page = browser.page()
    page.click("#Preview")

def submit_order():
    page = browser.page()

    while True:
        page.click("#order")

        # if error message not visible → success
        if not page.locator(".alert-danger").is_visible():
            break

def store_receipt_as_pdf(order_number):
    page = browser.page()
    order_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_folder = "output/receipt"
    pdf.html_to_pdf(order_html, f"{pdf_folder}/{order_number}.pdf")

def screenshot_robot(order_number):
    page = browser.page()
    page.screenshot(path= f"output/screenshot/{order_number}.png")


def embed_screenshot_to_receipt(order_number):
    page = browser.page()
    pdf = PDF()
    pdf_folder = "output/receipt" 
    pdf_file = f"{pdf_folder}/{order_number}.pdf"
    # take screenshot and save temporarily
    screenshot_file = f"output/screenshot/{order_number}.png"
    

    # immediately append to PDF
    pdf.add_files_to_pdf(
        files=[pdf_file, screenshot_file],
        target_document=pdf_file
    )

def order_another_robot():
    page = browser.page()
    page.click("#order-another") 

def archive_receipts():
    archive_name = "output/receipts.zip"   
    receipts_folder = "output/receipt"

    lib = Archive()
    lib.archive_folder_with_zip(receipts_folder, archive_name, recursive=True)

    # list files in the archive
    files = lib.list_archive(archive_name)
    for file in files:
        print(file)

