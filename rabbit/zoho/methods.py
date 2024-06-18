from zcrmsdk.src.com.zoho.crm.api.record import Record as ZCRMRecord
import zcrmsdk.src.com.zoho.crm.api.record as rec
import zcrmsdk.src.com.zoho.crm.api.query as q
from zcrmsdk.src.com.zoho.crm.api.util import Choice
from zcrmsdk.src.com.zoho.crm.api.record import InventoryLineItems

def get_record(record_id, module_name):
    response = rec.RecordOperations().get_record(int(record_id), module_name, None, None)
    data = get_response_data(response)
    if(len(data)==0):
        return None
    else:
        return data[0]#Потому что только один ID может быть
        
        
def get_coql(select_query):
    # Get instance of BodyWrapper Class that will contain the request body
    body_wrapper = q.BodyWrapper()

    body_wrapper.set_select_query(select_query)
    response = q.QueryOperations().get_records(body_wrapper)
    
    data = get_response_data(response)
    if(data == None):
        return []
    else:
        return data
    
def print_full_recs_info(record_list):
    for record in record_list:
        # Get the ID of each Record
        print("Record ID: " + str(record.get_id()))

        # Get the createdBy User instance of each Record
        created_by = record.get_created_by()

        # Check if created_by is not None
        if created_by is not None:
            # Get the Name of the created_by User
            print("Record Created By - Name: " + created_by.get_name())

            # Get the ID of the created_by User
            print("Record Created By - ID: " + str(created_by.get_id()))

            # Get the Email of the created_by User
            print("Record Created By - Email: " + created_by.get_email())

        # Get the CreatedTime of each Record
        print("Record CreatedTime: " + str(record.get_created_time()))

        if record.get_modified_time() is not None:
            # Get the ModifiedTime of each Record
            print("Record ModifiedTime: " + str(record.get_modified_time()))

        # Get the modified_by User instance of each Record
        modified_by = record.get_modified_by()

        # Check if modified_by is not None
        if modified_by is not None:
            # Get the Name of the modified_by User
            print("Record Modified By - Name: " + modified_by.get_name())

            # Get the ID of the modified_by User
            print("Record Modified By - ID: " + str(modified_by.get_id()))

            # Get the Email of the modified_by User
            print("Record Modified By - Email: " + modified_by.get_email())

        # Get the list of obtained Tag instance of each Record
        tags = record.get_tag()

        if tags is not None:
            for tag in tags:
                # Get the Name of each Tag
                print("Record Tag Name: " + tag.get_name())

                # Get the Id of each Tag
                print("Record Tag ID: " + str(tag.get_id()))

        # To get particular field value
        print("Record Field Value: " + str(record.get_key_value('Last_Name')))

        print('Record KeyValues: ')

        key_values = record.get_key_values()

        for key_name, value in key_values.items():

            if isinstance(value, list):

                if len(value) > 0:

                    if isinstance(value[0], Choice):
                        choice_list = value

                        print(key_name)

                        print('Values')

                        for choice in choice_list:
                            print(choice.get_value())

                    elif isinstance(value[0], InventoryLineItems):
                        product_details = value

                        for product_detail in product_details:
                            line_item_product = product_detail.get_product()

                            if line_item_product is not None:
                                print("Record ProductDetails LineItemProduct ProductCode: " + str(line_item_product.get_product_code()))

                                print("Record ProductDetails LineItemProduct Currency: " + str(line_item_product.get_currency()))

                                print("Record ProductDetails LineItemProduct Name: " + str(line_item_product.get_name()))

                                print("Record ProductDetails LineItemProduct Id: " + str(line_item_product.get_id()))

                            print("Record ProductDetails Quantity: " + str(product_detail.get_quantity()))

                            print("Record ProductDetails Discount: " + str(product_detail.get_discount()))

                            print("Record ProductDetails TotalAfterDiscount: " + str(product_detail.get_total_after_discount()))

                            print("Record ProductDetails NetTotal: " + str(product_detail.get_net_total()))

                            if product_detail.get_book() is not None:
                                print("Record ProductDetails Book: " + str(product_detail.get_book()))

                            print("Record ProductDetails Tax: " + str(product_detail.get_tax()))

                            print("Record ProductDetails ListPrice: " + str(product_detail.get_list_price()))

                            print("Record ProductDetails UnitPrice: " + str(product_detail.get_unit_price()))

                            print("Record ProductDetails QuantityInStock: " + str(product_detail.get_quantity_in_stock()))

                            print("Record ProductDetails Total: " + str(product_detail.get_total()))

                            print("Record ProductDetails ID: " + str(product_detail.get_id()))

                            print("Record ProductDetails ProductDescription: " + str(product_detail.get_product_description()))

                            line_taxes = product_detail.get_line_tax()

                            for line_tax in line_taxes:
                                print("Record ProductDetails LineTax Percentage: " + str(line_tax.get_percentage()))

                                print("Record ProductDetails LineTax Name: " + line_tax.get_name())

                                print("Record ProductDetails LineTax Id: " + str(line_tax.get_id()))

                                print("Record ProductDetails LineTax Value: " + str(line_tax.get_value()))

                    elif isinstance(value[0], Tag):
                        tags = value

                        if tags is not None:
                            for tag in tags:
                                print("Record Tag Name: " + tag.get_name())

                                print("Record Tag ID: " + str(tag.get_id()))

                    elif isinstance(value[0], PricingDetails):
                        pricing_details = value

                        for pricing_detail in pricing_details:
                            print("Record PricingDetails ToRange: " + str(pricing_detail.get_to_range()))

                            print("Record PricingDetails Discount: " + str(pricing_detail.get_discount()))

                            print("Record PricingDetails ID: " + str(pricing_detail.get_id()))

                            print("Record PricingDetails FromRange: " + str(pricing_detail.get_from_range()))

                    elif isinstance(value[0], ZCRMRecord):
                        record_list = value

                        for each_record in record_list:
                            for key, val in each_record.get_key_values().items():
                                print(str(key) + " : " + str(val))

                    elif isinstance(value[0], LineTax):
                        line_taxes = value

                        for line_tax in line_taxes:
                            print("Record LineTax Percentage: " + str(
                                line_tax.get_percentage()))

                            print("Record LineTax Name: " + line_tax.get_name())

                            print("Record LineTax Id: " + str(line_tax.get_id()))

                            print("Record LineTax Value: " + str(line_tax.get_value()))

                    elif isinstance(value[0], Comment):
                        comments = value

                        for comment in comments:
                            print("Comment-ID: " + str(comment.get_id()))

                            print("Comment-Content: " + str(comment.get_comment_content()))

                            print("Comment-Commented_By: " + str(comment.get_commented_by()))

                            print("Comment-Commented Time: " + str(comment.get_commented_time()))

                    elif isinstance(value[0], Attachment):
                        attachments = value

                        for attachment in attachments:
                            # Get the ID of each attachment
                            print('Record Attachment ID : ' + str(attachment.get_id()))

                            # Get the owner User instance of each attachment
                            owner = attachment.get_owner()

                            # Check if owner is not None
                            if owner is not None:
                                # Get the Name of the Owner
                                print("Record Attachment Owner - Name: " + owner.get_name())

                                # Get the ID of the Owner
                                print("Record Attachment Owner - ID: " + str(owner.get_id()))

                                # Get the Email of the Owner
                                print("Record Attachment Owner - Email: " + owner.get_email())

                            # Get the modified time of each attachment
                            print("Record Attachment Modified Time: " + str(attachment.get_modified_time()))

                            # Get the name of the File
                            print("Record Attachment File Name: " + attachment.get_file_name())

                            # Get the created time of each attachment
                            print("Record Attachment Created Time: " + str(attachment.get_created_time()))

                            # Get the Attachment file size
                            print("Record Attachment File Size: " + str(attachment.get_size()))

                            # Get the parentId Record instance of each attachment
                            parent_id = attachment.get_parent_id()

                            if parent_id is not None:
                                # Get the parent record Name of each attachment
                                print(
                                    "Record Attachment parent record Name: " + parent_id.get_key_value("name"))

                                # Get the parent record ID of each attachment
                                print("Record Attachment parent record ID: " + str(parent_id.get_id()))

                            # Check if the attachment is Editable
                            print("Record Attachment is Editable: " + str(attachment.get_editable()))

                            # Get the file ID of each attachment
                            print("Record Attachment File ID: " + str(attachment.get_file_id()))

                            # Get the type of each attachment
                            print("Record Attachment File Type: " + str(attachment.get_type()))

                            # Get the seModule of each attachment
                            print("Record Attachment seModule: " + str(attachment.get_se_module()))

                            # Get the modifiedBy User instance of each attachment
                            modified_by = attachment.get_modified_by()

                            # Check if modifiedBy is not None
                            if modified_by is not None:
                                # Get the Name of the modifiedBy User
                                print("Record Attachment Modified By - Name: " + modified_by.get_name())

                                # Get the ID of the modifiedBy User
                                print("Record Attachment Modified By - ID: " + str(modified_by.get_id()))

                                # Get the Email of the modifiedBy User
                                print("Record Attachment Modified By - Email: " + modified_by.get_email())

                            # Get the state of each attachment
                            print("Record Attachment State: " + attachment.get_state())

                            # Get the createdBy User instance of each attachment
                            created_by = attachment.get_created_by()

                            # Check if created_by is not None
                            if created_by is not None:
                                # Get the Name of the createdBy User
                                print("Record Attachment Created By - Name: " + created_by.get_name())

                                # Get the ID of the createdBy User
                                print("Record Attachment Created By - ID: " + str(created_by.get_id()))

                                # Get the Email of the createdBy User
                                print("Record Attachment Created By - Email: " + created_by.get_email())

                            # Get the linkUrl of each attachment
                            print("Record Attachment LinkUrl: " + str(attachment.get_link_url()))

                    else:
                        print(key_name)

                        for each_value in value:
                            print(str(each_value))

            elif isinstance(value, ZCRMRecord):
                print(key_name + " Record ID: " + str(value.get_id()))

                print(key_name + " Record Name: " + value.get_key_value('name'))

            elif isinstance(value, Choice):
                print(key_name + " : " + value.get_value())

            elif isinstance(value, dict):
                for key, val in value.items():
                    print(key + " : " + str(val))

            else:
                print(key_name + " : " + str(value))


###########################################    
        
def exception_instance(response_o):
    return (isinstance(response_o, rec.APIException)) or (isinstance(response_o, q.APIException))


    #Проверить и получить данные из ответа
def get_response_data(response):
    if(response.get_status_code() == 204):#No Content. HTTP 204. There is no content available for the request. Только для 
        return None
    else:
        response_o = response.get_object()
        if exception_instance(response_o):
            throw_error(response_o)
        else:
            return response_o.get_data()
            
            
            
def throw_error(response):
    # Get the Status
    error = "Status: " + response.get_status().get_value()
    # Get the Code
    error += "\nCode: " + response.get_code().get_value()
    
    # Get the details dict
    error += "\nDetails"
    details = response.get_details()
    for key, value in details.items():
        error += '\n' + key + ' : ' + str(value)
    # Get the Message
    error += "\nMessage: " + response.get_message().get_value()
    raise Exception(error)