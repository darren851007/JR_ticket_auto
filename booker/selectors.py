LOGIN = {
    "login_button":        "xpath=/html/body/form[2]/div/header/article/section/div/div[2]/a",
    "email_input":         "#TxtUserID",
    "password_input":      "#TxtPassword",
    "submit_button":       "#BtnEkinetLogin",
    "logged_in_indicator": "div.btn02__text:has-text('Purchase tickets')",
    "route_search_page":   "#BtnSelectFromStation",
    "station_search_page": "#TxtRideStation",
}

SEARCH_FORM = {
    "departure_input": "#TxtRideStation",
    "arrival_input":   "#TxtGetoffStation",
    "date_select":     "#DdlBoardingDate",
    "hour_select":     "select[name='Hour']",
    "minute_select":   "select[name='Minute']",
    "departure_radio": "label[for='RdiDepartureArrivalChoice1']",
    "arrival_radio":   "label[for='RdiDepartureArrivalChoice2']",
    "adults_select":   "#DdlAdultNumber",
    "children_select": "#DdlChildNumber",
    "search_button":   "#BtnTrainSearch",
}

TRAIN_SELECT = {
    "results_section": "#trainSearch_result",
    "train_name":      "h3.ts_resultTrainName",
    "departure_time":  "li.ts_resultDetailOutlineWItemDep",
    "expand_button":   "button.ts_DetailTrainCheckBtn",
    "seat_list":       "ul.selService_formTrainSeatSelList",
}

TICKET_TYPE_SELECT = {
    "page_anchor": "#BtnBuyATicketForMagneticTicket",
    "regular":     "#BtnBuyATicketForMagneticTicket",
    "e_ticket":    "#BtnBuyATicketForICCard",
}

SEAT_SELECT = {
    "page_anchor":    "#BtnToNext",
    "confirm_button": "#BtnToNext",
}

RECEIPT_INFO = {
    "page_anchor":    "h2.selService_title:has-text('Receipt Information')",
    "confirm_button": "#BtnToNext",
}

AGREEMENT = {
    "page_anchor":    "#ChkAgreement",
    "checkbox_label": "label[for='ChkAgreement']",
    "confirm_button": "#BtnToNext",
}

PAYMENT = {
    "page_anchor":    "#TxtNewEntryCreditCardNumber",
    "card_number":    "#TxtNewEntryCreditCardNumber",
    "card_type":      "#cardBrand",
    "expiry_month":   "#DdlNewEntryExpirationMonth",
    "expiry_year":    "#TxtNewEntryExpirationYear",
    "security_code":  "#TxtNewEntrySecurityCode",
    "submit_button":  "#BtnOrder",
}
