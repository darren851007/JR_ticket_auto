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
    "departure_radio": "#RdiDepartureArrivalChoice1",
    "arrival_radio":   "#RdiDepartureArrivalChoice2",
    "adults_select":   "#DdlAdultNumber",
    "children_select": "#DdlChildNumber",
    "search_button":   "#BtnTrainSearch",
}
