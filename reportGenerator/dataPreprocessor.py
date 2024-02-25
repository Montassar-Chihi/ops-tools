# import libraries
import pandas as pd
import datetime
from reportGenerator.utils import get_3pl_id


def preprocess_automatic_email_data():

    couriers_df = pd.read_csv("data/courier_db.csv")
    couriers_df = couriers_df.rename(
        columns={0: "Glover ID", 1: "First Name", 2: "Surname", 4: "Enabled", 17: "E-Mail", 8: "Phone No.",
                 3: "Address", 19: "IBAN"})
    pls_info = pd.read_csv("data/local database - 3PL data.csv")
    couriers_df["IBAN"] = couriers_df["IBAN"].apply(lambda x: str(x).strip())
    couriers_df["3PL's ID"] = couriers_df["IBAN"].apply(lambda x: get_3pl_id(x, pls_info))
    couriers_df = couriers_df[
        ["Glover ID", "First Name", "Surname", "Enabled", "E-Mail", "Phone No.", "Address", "3PL's ID"]]
    couriers_df.rename(
        columns={"Glover ID": "courier_id", "First Name": "first_name", "Surname": "last_name", "Enabled": "enabled",
                 "E-Mail": "email", "Phone No.": "phone", "Address": "adress", "3PL's ID": "3pl_id"}, inplace=True)
    couriers_df = couriers_df[couriers_df["enabled"] == 1].reset_index(drop=True)
    couriers_df["phone"] = couriers_df["phone"].astype("int").astype("str").apply(lambda x: "+" + x)

    # Load couriers daily performance df
    per_df = pd.read_csv("data/per_df.csv")

    per_df = per_df[["p_aggregation_date", "courier_id", "n_slots_booked", "n_slots_no_show", "n_slots_late_unbooking",
                     "n_slots_checked_in", "order_courier_total_compensation_eur_currency", "num_orders", "num_assignments",
                     "num_manual_reassignments", "num_automatic_reassignments"]]
    per_df.rename(columns={"p_aggregation_date": "date"}, inplace=True)

    # Load metrics df
    metrics_df = pd.read_csv("data/metrics_df.csv")

    metrics_df = metrics_df.groupby(["date", "courier_id", "metric"]).agg({"metric_value": "mean"}).reset_index()
    metrics_df = metrics_df.pivot_table("metric_value", ["date", "courier_id"], "metric").reset_index()
    metrics_df.rename(columns={"Courier_not_moving": "courier_not_moving_metric_value",
                               "Late_unbooks_and_no_shows": "late_unbooks_and_no_shows_metric_value",
                               "Reassignments": "reassignments_metric_value"}, inplace=True)

    df = per_df.merge(metrics_df, on=["date", "courier_id"], how="left")
    df = couriers_df.merge(df, on="courier_id", how="right")
    df = df[df["enabled"].notna()].reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])
    dfs = []
    for i in range(1, 28):
        date = pd.to_datetime(datetime.date.today() - datetime.timedelta(days=i))
        gdf = df[df["date"] == date].groupby(["date", "courier_id"]).agg(
            {"courier_not_moving_metric_value": "first", "late_unbooks_and_no_shows_metric_value": "first",
             "reassignments_metric_value": "first"}).reset_index()
        gdf = gdf.fillna(0)
        gdf.sort_values(
            by=["late_unbooks_and_no_shows_metric_value", "reassignments_metric_value", "courier_not_moving_metric_value"],
            ascending=[False, False, False], inplace=True)
        gdf = gdf.reset_index(drop=True)
        gdf["is_worst_5_percent"] = False
        gdf.loc[:int(0.05 * len(gdf)), "is_worst_5_percent"] = True
        dfs.append(gdf)

    worst_df = pd.concat(dfs).reset_index(drop=True)
    df = df.merge(worst_df[["date", "courier_id", "is_worst_5_percent"]], on=["date", "courier_id"], how="left")

    # Load funnel df
    funnel_df = pd.read_csv("data/funnel_df.csv")
    funnel_df = couriers_df.merge(funnel_df, on="courier_id", how="right")
    acc_funnel_df = funnel_df[(funnel_df["cycle_point"].str.contains("Accelerated Funnel"))]
    acc_funnel_df["accelarted"] = True
    funnel_df = funnel_df.merge(acc_funnel_df[["courier_id", "accelarted"]], on="courier_id", how="left")
    funnel_df["accelarted"] = funnel_df["accelarted"].fillna(False)

    # Load gps fraud data
    gps_fraud_df = pd.read_csv("data/gps_fraud_df.csv")
    gps_fraud_df = gps_fraud_df.merge(couriers_df, on="courier_id", how="left")
    gps_fraud_df["date"] = pd.to_datetime(gps_fraud_df["check_in_time"].apply(lambda x: str(x).split(" ")[0]))
    gps_fraud_df = gps_fraud_df.groupby(["courier_id", "date"]).agg(
        {'first_name': "first", 'last_name': "first", "phone": "first", "adress": "first", "dist_km": "count",
         "3pl_id": "first"}).reset_index().rename(columns={"dist_km": "nombre de fraudes"})
    gps_fraud_df["date"] = gps_fraud_df["date"].apply(lambda x: str(x).split(" ")[0])

    # Load capus data
    capus_df = pd.read_csv("data/capus_df.csv")
    capus_df = capus_df.merge(couriers_df, on="courier_id", how="left")
    capus_df = capus_df.groupby(["courier_id", "order_activated_date"]).agg(
        {'first_name': "first", 'last_name': "first", "phone": "first", "adress": "first",
         "hard_cancellation_number": "count", "3pl_id": "first"}).reset_index()

    # Load check in and no work data
    excellence_score_df = pd.read_csv("data/excellence_score.csv")
    check_in_no_work_df = pd.read_csv("data/check_in_no_work_df.csv")
    check_in_no_work_df = check_in_no_work_df.merge(couriers_df, on="courier_id", how="left")
    check_in_no_work_df = check_in_no_work_df.rename(columns={"p_aggregation_date_date": "date"})
    check_in_no_work_df = check_in_no_work_df.merge(excellence_score_df, on=["date", "courier_id"], how="left")
    check_in_no_work_df = check_in_no_work_df[
        ["date", "courier_id", 'first_name', 'last_name', "phone", "adress", "excellence_score", "n_slots_booked",
         "n_slots_checked_in", "num_assignments", "3pl_id"]]

    return df, couriers_df, per_df, metrics_df, funnel_df, gps_fraud_df, capus_df, check_in_no_work_df
