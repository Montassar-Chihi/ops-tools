# import libraries
import requests
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error,mean_squared_error
from datetime import date
from datetime import timedelta
from sklearn.tree import DecisionTreeRegressor
import pickle
from utilities.dataLoader import load_data_from_starburst
from utilities.queries import active_query,expected_query


class Forecaster():

    city = "TIS"
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    def __init__(self,city):
        # Get the city urls
        self.city = city
        if self.city == "TIS":
            self.url_historical = "https://archive-api.open-meteo.com/v1/archive?latitude=36.7498325&longitude=10.2676506&start_date=2022-11-01&end_date=" + str(
                self.yesterday) + "&hourly=temperature_2m,relativehumidity_2m,apparent_temperature,precipitation,rain,cloudcover,windspeed_100m,winddirection_100m,is_day&daily=sunrise,sunset,precipitation_sum,rain_sum&timezone=Europe%2FLondon"
            self.url_pred = "https://api.open-meteo.com/v1/forecast?latitude=36.7498325&longitude=10.2676506&hourly=precipitation_probability,temperature_2m,relativehumidity_2m,apparent_temperature,precipitation,rain,cloudcover,windspeed_80m,winddirection_80m,is_day&daily=sunrise,sunset,precipitation_sum,rain_sum&timezone=Europe%2FLondon&start_date=" + str(
                self.today) + "&end_date=" + str(self.tomorrow)
        elif self.city == "SOU":
            self.url_historical = "https://archive-api.open-meteo.com/v1/archive?latitude=35.8059273&longitude=10.6488785&start_date=2022-11-01&end_date=" + str(
                self.yesterday) + "&hourly=temperature_2m,relativehumidity_2m,apparent_temperature,precipitation,rain,cloudcover,windspeed_100m,winddirection_100m,is_day&daily=sunrise,sunset,precipitation_sum,rain_sum&timezone=Europe%2FLondon"
            self.url_pred = "https://api.open-meteo.com/v1/forecast?latitude=35.8059273&longitude=10.6488785&hourly=precipitation_probability,temperature_2m,relativehumidity_2m,apparent_temperature,precipitation,rain,cloudcover,windspeed_80m,winddirection_80m,is_day&daily=sunrise,sunset,precipitation_sum,rain_sum&timezone=Europe%2FLondon&start_date=" + str(
                self.today) + "&end_date=" + str(self.tomorrow)
        elif self.city == "SFX":
            self.url_historical = "https://archive-api.open-meteo.com/v1/archive?latitude=35.0177587&longitude=10.5943665&start_date=2022-11-01&end_date=" + str(
                self.yesterday) + "&hourly=temperature_2m,relativehumidity_2m,apparent_temperature,precipitation,rain,cloudcover,windspeed_100m,winddirection_100m,is_day&daily=sunrise,sunset,precipitation_sum,rain_sum&timezone=Europe%2FLondon"
            self.url_pred = "https://api.open-meteo.com/v1/forecast?latitude=35.0177587&longitude=10.5943665&hourly=precipitation_probability,temperature_2m,relativehumidity_2m,apparent_temperature,precipitation,rain,cloudcover,windspeed_80m,winddirection_80m,is_day&daily=sunrise,sunset,precipitation_sum,rain_sum&timezone=Europe%2FLondon&start_date=" + str(
                self.today) + "&end_date=" + str(self.tomorrow)

        # Get the city model
        if self.city == "TIS":
            self.model_pkl_file = "models/model_tis.pkl"
        elif self.city == "SOU":
            self.model_pkl_file = "models/model_sou.pkl"
        elif self.city == "SFX":
            self.model_pkl_file = "models/model_sfx.pkl"

        self.expected_couriers = load_data_from_starburst(expected_query)
        self.active_couriers = load_data_from_starburst(active_query)
        self.expected_couriers["date_data"] = pd.to_datetime(self.expected_couriers["date_data"])
        self.active_couriers["date_data"] = pd.to_datetime(self.active_couriers["date_data"])
        self.data = pd.merge(self.expected_couriers, self.active_couriers, on=["date_data", 'hour_data', "weekday", 'city_code'],
                        how="outer")
        self.data_train = self.data[self.data["active_couriers"].isna() == False].copy()
        self.data_predict = self.data[(self.data["active_couriers"].isna()) & (pd.to_datetime(self.data["date_data"]).dt.date >= self.today)].copy()

    def extract_action(self,row):
        return None

    def adjust_active_coureirs(self,row):
        if row["active_couriers"] > row["expected_couriers"]:
            return row["expected_couriers"]
        else:
            return row["active_couriers"]

    def encode_weekday(self,weekday):
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        if weekday in weekdays:
            return weekdays.index(weekday)
        else:
            assert ("Verify that weekday is in the correct format ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']")

    def decode_week_day(self,weekday):
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return weekdays[weekday]

    def encode_match_range(self,match_range):
        match_ranges = ["national", "international"]
        if match_range in match_ranges:
            return match_ranges.index(match_range) + 1
        else:
            assert ('Verify that match_range is in the correct format ["national","international"]')

    def encode_match_type(self,match_type):
        match_types = ["league", "cup", "final", "friendly"]
        if match_type in match_types:
            return match_types.index(match_type) + 1
        else:
            assert ('Verify that match_type is in the correct format ["league","cup","final","friendly"]')

    def encode_event_type(self,event_type):
        event_types = ["sudden_event", "expected_event"]
        if event_type in event_types:
            return event_types.index(event_type) + 1
        else:
            assert ('Verify that event_type is in the correct format ["sudden_event","expected_event"]')

    def encode_event_category(self,event_category):
        event_categorys = ["sports_event", "political_event", "holiday", "social_event", "festival"]
        if event_category in event_categorys:
            return event_categorys.index(event_category) + 1
        else:
            assert (
                'Verify that event_category is in the correct format ["sports_event","political_event","holiday","social_event","festival"]')

    def encode_event_range(self,event_range):
        event_ranges = ["local", "regional", "national", "international"]
        if event_range in event_ranges:
            return event_ranges.index(event_range) + 1
        else:
            assert ('Verify that event_range is in the correct format ["local","regional","national","international"]')

    def encode_event_impact(self,event_impact):
        event_impacts = ["national", "international"]
        if event_impact in event_impacts:
            return event_impacts.index(event_impact) + 1
        else:
            assert ('Verify that event_impact is in the correct format ["small","moderate","big"]')

    def encode_hour_data(self,hour_data):
        hours = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00",
                 "20:00", "21:00", "22:00", "23:00", "00:00", "01:00"]
        if hour_data in hours:
            return hours.index(hour_data) + 1
        else:
            assert ('Verify that hour_data is in the correct format hh:mm ')

    def decode_hour_data(self,hour_data):
        hours = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00",
                 "20:00", "21:00", "22:00", "23:00", "00:00", "01:00"]
        return hours[hour_data - 1]

    def get_special_events(self):
        special_events_rows = []
        football_matches_rows = []
        conti = input('Do you want to add an event ? y/n: ')
        if conti == "y":
            while conti == "y":
                event = input('Enter event, choose from ["f" for football match,"e" for other events]: ')
                if event == "f":
                    match_range = input('Enter match type, choose from ["national","international"]: ')
                    match_type = input('Enter match type, choose from ["league","cup","final","friendly"]: ')
                    match_date = input('Enter match date, use this format "dd-mm-yyyy" : ')
                    match_start_hour = input('Enter match start hour, use this format "hh:00" : ')
                    match_city = input('Enter event city, choose from ["SOU","TIS","SFX","ALL"]: ')
                    for i in range(-1, 3, 1):
                        if match_city == "ALL":
                            for city in ["TIS", "SFX", "SOU"]:
                                football_matches_row = []
                                football_matches_row.append(match_date)
                                football_matches_row.append(str(int(match_start_hour.split(":")[0]) + i) + ":00")
                                football_matches_row.append(match_range)
                                football_matches_row.append(match_type)
                                football_matches_row.append(city)
                                football_matches_rows.append(football_matches_row)
                        else:
                            city = match_city
                            football_matches_row = []
                            football_matches_row.append(match_date)
                            football_matches_row.append(str(int(match_start_hour.split(":")[0]) + i) + ":00")
                            football_matches_row.append(match_range)
                            football_matches_row.append(match_type)
                            football_matches_row.append(city)
                            football_matches_rows.append(football_matches_row)
                else:
                    special_events_row = []
                    event_type = input('Enter event type, choose from ["sudden_event","expected_event"]: ')
                    event_category = input(
                        'Enter event category, choose from ["sports_event","political_event","holiday","social_event","festival"]: ')
                    event_range = input(
                        'Enter event range, choose from ["local","regional","national","international"]: ')
                    event_impact = input('Enter event impact, choose from ["small","moderate","big"]: ')
                    event_date = input('Enter event date, use this format "dd-mm-yyyy" : ')
                    event_start_hour = input('Enter event start hour, use this format "hh:00" : ')
                    event_duration = input('Enter event duration, use this format "hh" : ')
                    event_city_code = input('Enter event city, choose from ["SOU","TIS","SFX","ALL"]: ')
                    special_events_row.append(event_type)
                    special_events_row.append(event_category)
                    special_events_row.append(event_range)
                    special_events_row.append(event_impact)
                    special_events_row.append(event_date)
                    special_events_row.append(event_start_hour)
                    special_events_row.append(event_duration)
                    special_events_row.append(event_city_code)
                    special_events_rows.append(special_events_row)
                conti = input('add another event ? y/n: ')

            special_events_final_rows = []
            for cells in special_events_rows:
                duration = int(cells[6].split(":")[0])
                for i in range(duration):
                    if cells[7] == "ALL":
                        for city in ["TIS", "SFX", "SOU"]:
                            ser = []
                            hour = str(int(cells[5].split(":")[0]) + i) + ":00"
                            ser.append(cells[4])
                            ser.append(hour)
                            ser.append(city)
                            ser.append(cells[0])
                            ser.append(cells[1])
                            ser.append(cells[2])
                            ser.append(cells[3])
                            special_events_final_rows.append(ser)
                    else:
                        ser = []
                        city = cells[7]
                        hour = str(int(cells[5].split(":")[0]) + i) + ":00"
                        ser.append(cells[4])
                        ser.append(hour)
                        ser.append(city)
                        ser.append(cells[0])
                        ser.append(cells[1])
                        ser.append(cells[2])
                        ser.append(cells[3])
                        special_events_final_rows.append(ser)

            special_events_df = pd.DataFrame(special_events_final_rows)
            special_events_df.rename(
                columns={0: "date_data", 1: "hour_data", 2: "city_code", 3: "event_type", 4: "event_category",
                         5: "event_range", 6: "event_impact"}, inplace=True)
            football_matches_df = pd.DataFrame(football_matches_rows)
            football_matches_df["match_range"] = football_matches_df["match_range"].apply(
                lambda x: 0 if str(x) == "nan" else self.encode_match_range(x))
            football_matches_df["match_type"] = football_matches_df["match_type"].apply(
                lambda x: 0 if str(x) == "nan" else self.encode_match_type(x))
            football_matches_df.sort_values(["date_data", "city_code", "hour_data", "match_range", "match_type"],
                                            inplace=True, ascending=[True, True, True, False, False])
            football_matches_df.drop_duplicates(subset=["date_data", "hour_data", "city_code"], keep="first",
                                                inplace=True)
            football_matches_df.rename(
                columns={0: "date_data", 1: "hour_data", 3: "match_type", 2: "match_range", 4: "city_code"},
                inplace=True)
            final_df = pd.merge(football_matches_df, special_events_df, on=["date_data", "hour_data", "city_code"],
                                how="outer")
            final_df["date_data"] = pd.to_datetime(final_df["date_data"])
            final_df["hour_data"] = final_df["hour_data"].apply(lambda x: self.encode_hour_data(x))
            return final_df
        else:
            return pd.DataFrame(columns=["date_data", "hour_data", "city_code", "match_range", "match_type"])

    def train_model(self):
        ######################################## Training Process ########################################

        # Get the data train for the city
        city_data_train = self.data_train[self.data_train["city_code"] == self.city].copy()

        ########################### Process the data to prepare it for modeling ###########################

        #### Prepare Weather Data

        # Load and process weather data for the city

        historical_response = requests.get(self.url_historical)
        data_historical = json.loads(historical_response.content)
        weather_data = pd.DataFrame(data_historical["hourly"])
        weather_data["date_data"] = weather_data["time"].apply(lambda x: x.split("T")[0])
        weather_data["hour_data"] = weather_data["time"].apply(lambda x: x.split("T")[1])
        weather_data["city_code"] = self.city
        weather_data["hour_data"] = weather_data["hour_data"].apply(
            lambda x: x if x not in ["02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00"] else None)
        weather_data["date_data"] = pd.to_datetime(weather_data["date_data"])
        weather_data = weather_data.dropna()
        # Drop rows from weather_data with dates higher than those in data_train
        weather_data = weather_data[
            (pd.to_datetime(weather_data["date_data"]) <= pd.to_datetime(self.data_train["date_data"].max()))].reset_index(
            drop=True)
        weather_data = weather_data.sort_values(['date_data', 'hour_data', 'city_code'],
                                                ascending=[True, False, True]).reset_index(drop=True)
        # Merge the dfs and keep processing
        city_data_train = pd.merge(weather_data, self.data_train, on=['date_data', 'hour_data', 'city_code'])
        city_data_train["month"] = city_data_train["date_data"].apply(lambda x: int(str(x).split("-")[1]))
        city_data_train["weekday"] = city_data_train["weekday"].apply(self.encode_weekday)
        # drop unnacessary rows and columns
        city_data_train.rename(columns={"winddirection_100m": "wind_direction", "windspeed_100m": "wind_speed"},
                               inplace=True)
        city_data_train.dropna()
        city_data_train = city_data_train[city_data_train["active_couriers"] > 1]
        city_data_train = city_data_train[city_data_train["expected_couriers"] >= city_data_train["active_couriers"]]

        #### Prepare special events data

        final_df = pd.read_csv("data/special_events_historical.csv")
        final_df = final_df.iloc[:, 1:]
        final_df["date_data"] = pd.to_datetime(final_df["date_data"])
        city_data_train = city_data_train.merge(final_df, on=["date_data", "hour_data", "city_code"], how="left")
        city_data_train["hour_data"] = city_data_train["hour_data"].apply(lambda x: self.encode_hour_data(x))
        city_data_train["match_range"] = city_data_train["match_range"].apply(
            lambda x: 0 if str(x) == "nan" else self.encode_match_range(x))
        city_data_train["match_type"] = city_data_train["match_type"].apply(
            lambda x: 0 if str(x) == "nan" else self.encode_match_type(x))
        # city_data_train["event_type"] = city_data_train["event_type"].apply(lambda x: 0 if str(x) == "nan" else encode_event_type(x))
        # city_data_train["event_category"] = city_data_train["event_category"].apply(lambda x: 0 if str(x) == "nan" else encode_event_category(x))
        # city_data_train["event_range"] = city_data_train["event_range"].apply(lambda x: 0 if str(x) == "nan" else encode_event_range(x))
        # city_data_train["event_impact"] = city_data_train["event_impact"].apply(lambda x: 0 if str(x) == "nan" else encode_event_impact(x))

        ########################### Train Model ###########################

        y = city_data_train["active_couriers"]
        X = city_data_train.drop(
            ["temperature_2m", "active_couriers", "precipitation", "time", "date_data", "is_day", "city_code",
             "wind_direction"], axis=1)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
        regressor = DecisionTreeRegressor(criterion="poisson", splitter="best", max_depth=10).fit(X_train,
                                                                                                  np.log(y_train))
        regressor_pred = np.exp(regressor.predict(X_test))

        ########################### Print results ###########################

        print('tree R-squared score (test): {:.3f}'.format(regressor.score(X_test, np.log(y_test))))
        print('tree Mean squared error: {:.3f}'.format(mean_squared_error(y_test, regressor_pred)))
        print('tree Mean absolute error: {:.3f}'.format(mean_absolute_error(y_test, regressor_pred)))

        ########################### Save the model ###########################

        with open(self.model_pkl_file, 'wb') as file:
            pickle.dump(regressor, file)


    def predict_next_two_days(self):
        ######################################## Prediction Process ########################################

        # Get the data pedict for the city
        city_data_predict = self.data_predict[self.data_predict["city_code"] == self.city].copy()

        ########################### Process the data to prepare it for modeling ###########################

        #### Prepare Weather Data

        # Load weather data for the city
        pred_response = requests.get(self.url_pred)
        data_pred = json.loads(pred_response.content)
        weather_data = pd.DataFrame(data_pred["hourly"])
        weather_data["date_data"] = weather_data["time"].apply(lambda x: x.split("T")[0])
        weather_data["hour_data"] = weather_data["time"].apply(lambda x: x.split("T")[1])
        weather_data["city_code"] = self.city
        weather_data["hour_data"] = weather_data["hour_data"].apply(
            lambda x: x if x not in ["02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00"] else None)
        weather_data["date_data"] = pd.to_datetime(weather_data["date_data"])
        weather_data = weather_data.dropna()
        # Drop rows from weather_data with dates lower than those in city_data_predict
        weather_data = weather_data[(pd.to_datetime(weather_data["date_data"]) <= pd.to_datetime(
            city_data_predict["date_data"].max()))].reset_index(drop=True)
        weather_data = weather_data.sort_values(['date_data', 'hour_data', 'city_code'],
                                                ascending=[True, False, True]).reset_index(drop=True)
        # Merge the dfs and keep processing
        city_data_predict = pd.merge(weather_data, city_data_predict, on=['date_data', 'hour_data', 'city_code'])
        city_data_predict["month"] = city_data_predict["date_data"].apply(lambda x: int(str(x).split("-")[1]))
        city_data_predict["weekday"] = city_data_predict["weekday"].apply(self.encode_weekday)
        # drop unnacessary rows and columns
        city_data_predict.rename(columns={"winddirection_80m": "wind_direction", "windspeed_80m": "wind_speed"},
                                 inplace=True)
        city_data_predict.drop(["precipitation", "time"], inplace=True, axis=1)

        #### Prepare special events data

        final_df = self.get_special_events()
        final_df["date_data"] = pd.to_datetime(final_df["date_data"])
        city_data_predict = city_data_predict.merge(final_df, on=["date_data", "hour_data", "city_code"], how="left")
        city_data_predict["match_range"] = city_data_predict["match_range"].apply(
            lambda x: 0 if str(x) == "nan" else self.encode_match_range(x))
        city_data_predict["match_type"] = city_data_predict["match_type"].apply(
            lambda x: 0 if str(x) == "nan" else self.encode_match_type(x))
        city_data_predict["hour_data"] = city_data_predict["hour_data"].apply(lambda x: self.encode_hour_data(x))
        # city_data_predict["event_type"] = city_data_predict["event_type"].apply(lambda x: 0 if str(x) == "nan" else encode_event_type(x))
        # city_data_predict["event_category"] = city_data_predict["event_category"].apply(lambda x: 0 if str(x) == "nan" else encode_event_category(x))
        # city_data_predict["event_range"] = city_data_predict["event_range"].apply(lambda x: 0 if str(x) == "nan" else encode_event_range(x))
        # city_data_predict["event_impact"] = city_data_predict["event_impact"].apply(lambda x: 0 if str(x) == "nan" else encode_event_impact(x))

        ################## make predictions and display results ####################

        # Load Model
        with open(self.model_pkl_file, 'rb') as file:
            model = pickle.load(file)

        # Make predictions
        data_test = city_data_predict.drop(
            ["precipitation_probability", "temperature_2m", "active_couriers", "is_day", "city_code", "wind_direction"],
            axis=1)
        preds = np.exp(model.predict(data_test.drop("date_data", axis=1)))
        data_test["active_couriers"] = np.round(preds, 0)
        data_test["active_couriers"] = data_test.apply(self.adjust_active_coureirs, axis=1)
        # data_test["potentiel_action"] = data_test.apply(extract_action,axis = 1)
        data_test["hour_data"] = data_test["hour_data"].apply(self.decode_hour_data)
        data_test["weekday"] = data_test["weekday"].apply(self.decode_week_day)
        return data_test[["date_data", "hour_data", "weekday", "expected_couriers", "active_couriers"]]

# def get_historical_football_data(self):
# football_matches_rows = []
# competetion_ids = {362: "FIFA World Cup",387 : "EURO", 227 : "AFCON", 244 : "CL",245 : "EL" , 223:"ACL",1 : "bundesliga",
#                   2:"premier league",3:"laliga",4:"serieA",5:"ligue 1",427:"tunisia cup",42:"tunisia league"}

# for competetion_id in list(competetion_ids.keys()) :
#     lll=requests.get("http://livescore-api.com/api-client/scores/history.json?from=2022-11-01&competition_id="+str(competetion_id)+"&key=ilfcBNNH7eyenwHH&secret=hfrVN6M8GP2S6sgpOwCpjp6rEFF2bnJt")
#     ss = json.loads(lll.content)
#     for match in ss["data"]["match"]:
#         mdate = match["date"]
#         mhour = match["scheduled"]
#         mteamh = match["home_name"]
#         mteama = match["away_name"]
#         match_date = mdate
#         if (mteamh in ["Tunisia","Brazil",'Club Africain', 'CS Sfaxien', 'Manchester City','Real Madrid', 'Etoile du Sahel', 'Esperance']) or (mteama in ["Tunisia","Brazil",'Club Africain', 'CS Sfaxien', 'Manchester City','Real Madrid', 'Etoile du Sahel', 'Esperance']):
#             if competetion_id in [362,381,227,244,245,223,427]:
#                 match_range = "international"
#                 city = "ALL"
#             else:
#                 match_range = "national"
#                 city = "TIS"

#             if competetion_id in [1,2,3,4,5,42] :
#                 match_type = "league"
#             elif competetion_id in [362,387,227,244,245,223,427] :
#                 if True:
#                     match_type = "final"
#                 else:
#                     match_type = "cup"

#             for i in range(-1,3,1):
#                 if city =="ALL":
#                     for match_city in ["TIS","SFX","SOU"]:
#                         football_matches_row = []
#                         football_matches_row.append(match_date)
#                         football_matches_row.append(str(int(mhour.split(":")[0])+i)+":00")
#                         football_matches_row.append(match_range)
#                         football_matches_row.append(match_type)
#                         football_matches_row.append(match_city)
#                         football_matches_rows.append(football_matches_row)
#                 else :
#                     football_matches_row = []
#                     football_matches_row.append(match_date)
#                     football_matches_row.append(str(int(mhour.split(":")[0])+i)+":00")
#                     football_matches_row.append(match_range)
#                     football_matches_row.append(match_type)
#                     football_matches_row.append(match_city)
#                     football_matches_rows.append(football_matches_row)

#     #         break


# football_matches_df = pd.DataFrame(football_matches_rows)
# football_matches_df.rename(columns={0:"date_data",1:"hour_data",3:"match_type",2:"match_range",4:"city_code",5:"away",6:"home"},inplace=True)
# display(football_matches_df)
# football_matches_df.to_csv("special_events_historical.csv")