import re

#-----------------------------------------------
#MULTIPROPOUSE FUNCTIONS
def multi_comparison(reg_exp, case_sensitive, first_comp, second_comp):
    if first_comp == None or first_comp==False:
        first_comp = ''
    if second_comp==None or second_comp==False:
        second_comp = ''

    #IF STRING DON'T MATCH, RETURN FALSE
    #WITH CASE SENSITIVE AND NO REGEXP
    if not reg_exp and case_sensitive:
        if first_comp != second_comp:
            return False
            
    #WITH NO CASE SENSITIVE AND NO REGEXP
    if not reg_exp and not case_sensitive:
        if first_comp.upper() != second_comp.upper():
            return False
            
    #WITH CASE SENSITIVE AND REGEXP
    if reg_exp and case_sensitive: 
        if not re.search(second_comp, first_comp):
            return False
            
    #WITH NO CASE SENSITIVE AND REGEXP
    if reg_exp and not case_sensitive:
        if not re.search(second_comp.upper(), first_comp.upper()):
            return False
           
    #IF FILTERS PASS, RETURN TRUE
    return True

def change_false(field):
    if field == False:
        return ""
    else:
        return field
#-------------------------------------------------

def validate_date(date_string, datetime_module):
    try:
        separated_date = list(
            map(
                lambda x: int(x.strip()),
                date_string.split('-')
            )
        )
    except:
        return {
            "ERROR": True,
            "DESCRIPTION": f"The date {date_string} is not valid for parsing"
        }

    if len(separated_date)!=3:
        return{
            "ERROR": True,
            "DESCRIPTION": f"The date {date_string} is not valid, must be in dd-mm-yyyy format"
        }
    else:
        try:
            date = datetime_module(
                day = separated_date[0],
                month = separated_date[1], 
                year = separated_date[2]
            )
        except: 
            return {
                "ERROR": True,
                "DESCRIPTION": f"Date {date_string} in not a valid date"
            }

        return{
            "ERROR": False,
            "DATE": date
        }


