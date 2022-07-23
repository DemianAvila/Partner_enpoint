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


