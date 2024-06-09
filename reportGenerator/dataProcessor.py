# import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dataframe_image as dfi
from reportGenerator.utils import style_df_in_report,style_fraud_df_in_report,style_checkin_fraud_df_in_report


def prepare_3pl_stats_for_current_3pl(df,date,current_3pl,funnel_df,period):
    # frequency (orders per courier)
    total_number_of_orders = (df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "num_orders"].sum() / df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "num_orders"].count())
    avg_total_number_of_orders = (df.loc[df["date"] >= date, "num_orders"].sum() / df.loc[df["date"] >= date, "num_orders"].count())
    if period == "weekly":
        total_number_of_orders = (df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "num_orders"].sum() / df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "num_orders"].count()) * 7
        avg_total_number_of_orders = (df.loc[df["date"] >= date, "num_orders"].sum() / df.loc[df["date"] >= date, "num_orders"].count()) * 7

        # Plotting the bar chart with custom colors
    colors = [['#78c98e' if value >= np.max([total_number_of_orders, avg_total_number_of_orders]) else '#f08181' for value in [total_number_of_orders]][0], "#137fd0"]
    plt.figure(figsize=(7, 7))
    ax = plt.bar(["Commandes Par Coursier : " + str(int(total_number_of_orders)),"Avg : " + str(int(avg_total_number_of_orders))],[total_number_of_orders, avg_total_number_of_orders], color=colors)
    plt.xlabel('')
    plt.ylabel('# Commandes Par Coursier')
    plt.title('# de Commandes Par Coursier V.S La Moyenne')
    plt.savefig("content/orders.jpg")

    # avg reass rate
    total_manual_reass = df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "num_manual_reassignments"].sum()
    total_automatic_reass = df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "num_automatic_reassignments"].sum()
    total_ass = df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "num_assignments"].sum()

    avg_total_manual_reass = df.loc[(df["date"] >= date), "num_manual_reassignments"].sum() / len(df["3pl_id"].unique())
    avg_total_automatic_reass = df.loc[(df["date"] >= date), "num_automatic_reassignments"].sum() / len(df["3pl_id"].unique())
    avg_total_ass = df.loc[(df["date"] >= date), "num_assignments"].sum() / len(df["3pl_id"].unique())

    avg_reass_rate = (total_manual_reass + total_automatic_reass) / total_ass
    avg_avg_reass_rate = (avg_total_manual_reass + avg_total_automatic_reass) / avg_total_ass
    # Plotting the bar chart with custom colors
    colors = [['#78c98e' if value < np.max([avg_reass_rate, avg_avg_reass_rate]) else '#f08181' for value in [avg_reass_rate]][0], "#137fd0"]
    plt.figure(figsize=(7, 7))
    ax = plt.bar(["réaffectation : " + str(np.round(avg_reass_rate * 100, 2)) + "%","Avg : " + str(np.round(avg_avg_reass_rate * 100, 2)) + "%"], [avg_reass_rate, avg_avg_reass_rate], color=colors)
    plt.xlabel('')
    plt.ylabel('% Réaffectation')
    plt.title('% Réaffectation V.S La Moyenne')
    plt.savefig("content/reass.jpg")

    # avg nslu rate
    total_n_slots_no_show = df.loc[ (df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "n_slots_no_show"].sum()
    total_n_slots_late_unbooking = df.loc[ (df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "n_slots_late_unbooking"].sum()
    total_n_slots_booked = df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)), "n_slots_booked"].sum()

    avg_total_n_slots_no_show = df.loc[(df["date"] >= date), "n_slots_no_show"].sum() / len(df["3pl_id"].unique())
    avg_total_n_slots_late_unbooking = df.loc[(df["date"] >= date), "n_slots_late_unbooking"].sum() / len(df["3pl_id"].unique())
    avg_total_n_slots_booked = df.loc[(df["date"] >= date), "n_slots_booked"].sum() / len(df["3pl_id"].unique())

    avg_nslu_rate = (total_n_slots_no_show +total_n_slots_late_unbooking) / (total_n_slots_booked+total_n_slots_late_unbooking)
    avg_avg_nslu_rate = (avg_total_n_slots_no_show+avg_total_n_slots_late_unbooking ) / (avg_total_n_slots_booked+avg_total_n_slots_late_unbooking)
    # Plotting the bar chart with custom colors
    colors = [['#78c98e' if value < np.max([avg_nslu_rate, avg_avg_nslu_rate]) else '#f08181' for value in [avg_nslu_rate]][0], "#137fd0"]
    plt.figure(figsize=(7, 7))
    ax = plt.bar(["heures non travaillées : " + str(np.round(avg_nslu_rate * 100, 2)) + "%","Avg : " + str(np.round(avg_avg_nslu_rate * 100, 2)) + "%"], [avg_nslu_rate, avg_avg_nslu_rate],color=colors)
    plt.xlabel('')
    plt.ylabel('% heures non travaillées')
    plt.title('% des heures non travaillées V.S La Moyenne')
    plt.savefig("content/noshows.jpg")

    # total blocks
    total_funnel_moves = len(funnel_df.loc[(pd.to_datetime(funnel_df["last_movement_date"]) >= date) & (funnel_df["3pl_id"] == str(current_3pl)) & (funnel_df["action"] == "BLOCK")])
    avg_total_funnel_moves = len(funnel_df.loc[(pd.to_datetime(funnel_df["last_movement_date"]) >= date) & (funnel_df["action"] == "BLOCK")]) / len(df["3pl_id"].unique())
    # Plotting the bar chart with custom colors
    colors = [['#78c98e' if value < np.max([total_funnel_moves, avg_total_funnel_moves]) else '#f08181' for value in [total_funnel_moves]][0], "#137fd0"]
    plt.figure(figsize=(7, 7))
    ax = plt.bar(["# Coursiers de 3PL : " + str(int(total_funnel_moves)), "Avg : " + str(int(avg_total_funnel_moves))],[total_funnel_moves, avg_total_funnel_moves], color=colors)
    plt.xlabel('')
    plt.ylabel('# Coursiers Bloqués')
    plt.title('# Coursiers Bloqués V.S La Moyenne')
    plt.savefig("content/blocks.jpg")

    # total funnel moves (weekly)
    total_funnel_moves = len(funnel_df.loc[(pd.to_datetime(funnel_df["last_movement_date"]) >= date) & (funnel_df["3pl_id"] == str(current_3pl))])

    # Active couriers vs available couriers
    active_couriers = df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)) & (df["num_orders"] > 5)]
    available_couriers = df.loc[(df["date"] >= date) & (df["3pl_id"] == str(current_3pl)) & (df["n_slots_booked"] > 0)]
    active_couriers = active_couriers.groupby("date").agg({"courier_id": "count"}).reset_index()
    available_couriers = available_couriers.groupby("date").agg({"courier_id": "count"}).reset_index()
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111)
    labels = [str(dt).split(" ")[0] + ": " + str(av - ac) for dt, av, ac in zip(available_couriers["date"], available_couriers["courier_id"], active_couriers["courier_id"])]
    ax.bar(labels, available_couriers["courier_id"], color='#f08181')
    p = ax.bar(labels, active_couriers["courier_id"], color='#78c98e')
    for rect in p:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_y() + (height / 2), str(int(height)),ha='center', va='center', color='white', size=9)

    plt.xlabel("Date : Coursiers disponibles non active")
    plt.xticks(rotation=20)
    plt.ylabel("# couriers")
    plt.legend(["Coursiers disponibles non active", "Coursiers Actives"])
    plt.title("Coursiers disponibles non active VS Coursiers Active")
    plt.savefig("content/active.jpg")

    return avg_total_funnel_moves,total_funnel_moves


def prepare_fraud_metrics_for_current_3pl(current_3pl,yesterday, period,gps_fraud_df,capus_df,check_in_no_work_df):
    gps_fraud_couriers = gps_fraud_df[
        (pd.to_datetime(gps_fraud_df["date"]) == yesterday) & (gps_fraud_df["3pl_id"] == str(current_3pl)) & (
                gps_fraud_df["nombre de fraudes"] > 5)]
    gps_fraud_couriers.drop(["date", "3pl_id", "adress", "phone"], axis=1, inplace=True)
    dfi.export(style_fraud_df_in_report(gps_fraud_couriers),
               "content/"+period+"_gps_fraud_" + str(current_3pl) + ".jpg")

    capus_couriers = capus_df[(pd.to_datetime(capus_df["order_activated_date"]) == yesterday) & (
            capus_df["hard_cancellation_number"] > 2) & (capus_df["3pl_id"] == str(current_3pl))].rename(
        columns={"order_activated_date": "date", "hard_cancellation_number": "Nombre d'annulations"})
    capus_couriers.drop(["date", "3pl_id", "adress", "phone"], axis=1, inplace=True)
    dfi.export(style_fraud_df_in_report(capus_couriers),
               "content/"+period+"_capus_couriers_" + str(current_3pl) + ".jpg")

    check_in_no_work_couriers = check_in_no_work_df[
        (pd.to_datetime(check_in_no_work_df["date"]) == yesterday) & (
                check_in_no_work_df["3pl_id"] == str(current_3pl)) & (
            (check_in_no_work_df["excellence_score"] > 3.5))]
    check_in_no_work_couriers.drop(["date", "3pl_id", "adress", "phone"], axis=1, inplace=True)
    dfi.export(style_checkin_fraud_df_in_report(check_in_no_work_couriers),
               "content/"+period+"_check_in_no_work_" + str(current_3pl) + ".jpg")
    return gps_fraud_couriers,capus_couriers,check_in_no_work_couriers

def prepare_afm_metrics_for_current_3pl(df, date, period, current_3pl, reass_abs_threshold_1, reass_abs_threshold_2,
                                        reass_abs_threshold_3, no_shows_late_unbooks_1, no_shows_late_unbooks_2,
                                        no_shows_late_unbooks_3, courier_not_moving_1, courier_not_moving_2,
                                        courier_not_moving_3):

    df_reass_t1 = df[(df["date"] >= date) & (df["reassignments_metric_value"] < reass_abs_threshold_2) & (
            df["reassignments_metric_value"] >= reass_abs_threshold_1) & (df["3pl_id"] == str(current_3pl))]
    df_reass_t1 = df_reass_t1.groupby("courier_id").agg(
        {"date": "first", "first_name": "first", "last_name": "first", "phone": "first",
         "is_worst_5_percent": "first"}).reset_index()
    reass_1_recommandations = " / Appelez le coursier. / Expliquez-lui qu'il doit s'améliorer et cesser de réaffecter les commandes. / S'il ne s'améliore pas dans les 5 prochains jours, il sera au risque de passer à travers le Funnel."
    dfi.export(style_df_in_report(df_reass_t1), "content/"+period+"_reass_t1_" + str(current_3pl) + ".jpg")

    df_reass_t2 = df[(df["date"] >= date) & (df["reassignments_metric_value"] < reass_abs_threshold_3) & (
            df["reassignments_metric_value"] >= reass_abs_threshold_2) & (df["3pl_id"] == str(current_3pl))]
    df_reass_t2 = df_reass_t2.groupby("courier_id").agg(
        {"date": "first", "first_name": "first", "last_name": "first", "phone": "first",
         "is_worst_5_percent": "first"}).reset_index()
    reass_2_recommandations = " / Appelez le coursier. / Expliquez-lui qu'il doit s'améliorer et cesser de réaffecter les commandes. / S'il ne s'améliore pas dans les 5 prochains jours, il sera au risque de passer à travers le Funnel accéléré."
    dfi.export(style_df_in_report(df_reass_t2), "content/"+period+"_reass_t2_" + str(current_3pl) + ".jpg")

    df_reass_t3 = df[(df["date"] >= date) & (df["reassignments_metric_value"] >= reass_abs_threshold_3) & (
            df["3pl_id"] == str(current_3pl))]
    df_reass_t3 = df_reass_t3.groupby("courier_id").agg(
        {"date": "first", "first_name": "first", "last_name": "first", "phone": "first",
         "is_worst_5_percent": "first"}).reset_index()
    reass_3_recommandations = " / Appeler le coursier. / Assurez-vous que le coursier ne souffre pas d'un incident ayant entraîné l'effondrement de ses performances. / Récupérez le solde de trésorerie."
    dfi.export(style_df_in_report(df_reass_t3), "content/"+period+"_reass_t3_" + str(current_3pl) + ".jpg")

    df_nslu_t1 = df[
        (df["date"] >= date) & (df["no_shows_metric_value"] < no_shows_late_unbooks_2) & (
                df["no_shows_metric_value"] >= no_shows_late_unbooks_1) & (
                df["3pl_id"] == str(current_3pl))]
    df_nslu_t1 = df_nslu_t1.groupby("courier_id").agg(
        {"date": "first", "first_name": "first", "last_name": "first", "phone": "first",
         "is_worst_5_percent": "first"}).reset_index()
    nslu_1_recommandations = " / Appelez le coursier. / Expliquez-lui qu'il doit s'améliorer et se présenter au travail à l'heure (faire le check-in à temps). / S'il ne s'améliore pas dans les 5 prochains jours, il sera au risque de passer à travers le Funnel."
    dfi.export(style_df_in_report(df_nslu_t1), "content/"+period+"_nslu_t1_" + str(current_3pl) + ".jpg")

    df_nslu_t2 = df[
        (df["date"] >= date) & (df["no_shows_metric_value"] < no_shows_late_unbooks_3) & (
                df["no_shows_metric_value"] >= no_shows_late_unbooks_2) & (
                df["3pl_id"] == str(current_3pl))]
    df_nslu_t2 = df_nslu_t2.groupby("courier_id").agg(
        {"date": "first", "first_name": "first", "last_name": "first", "phone": "first",
         "is_worst_5_percent": "first"}).reset_index()
    nslu_2_recommandations = " / Appelez le coursier. / Expliquez-lui qu'il doit s'améliorer et se présenter au travail à l'heure (faire le check-in à temps). / S'il ne s'améliore pas dans les 5 prochains jours, il sera au risque de passer à travers le Funnel accéléré."
    dfi.export(style_df_in_report(df_nslu_t2), "content/"+period+"_nslu_t2_" + str(current_3pl) + ".jpg")

    df_nslu_t3 = df[(df["date"] >= date) & (
            df["no_shows_metric_value"] >= no_shows_late_unbooks_3) & (
                            df["3pl_id"] == str(current_3pl))]
    df_nslu_t3 = df_nslu_t3.groupby("courier_id").agg(
        {"date": "first", "first_name": "first", "last_name": "first", "phone": "first",
         "is_worst_5_percent": "first"}).reset_index()
    nslu_3_recommandations = "  / Appeler le coursier. / Assurez-vous que le coursier ne souffre pas d'un incident ayant entraîné l'effondrement de ses performances. / Récupérez le solde de trésorerie."
    dfi.export(style_df_in_report(df_nslu_t3), "content/"+period+"_nslu_t3_" + str(current_3pl) + ".jpg")

    df_cnm_t1 = df[
        (df["date"] >= date) & (df["courier_not_moving_metric_value"] < courier_not_moving_2) & (
                df["courier_not_moving_metric_value"] >= courier_not_moving_1) & (
                df["3pl_id"] == str(current_3pl))]
    df_cnm_t1 = df_cnm_t1.groupby("courier_id").agg(
        {"date": "first", "first_name": "first", "last_name": "first", "phone": "first",
         "is_worst_5_percent": "first"}).reset_index()
    cnm_1_recommandations = " / Appelez le coursier. / Expliquez-lui qu'il doit s'améliorer et suivre les directives de base de Glovo. / S'il ne s'améliore pas dans les 5 prochains jours, il sera au risque de passer à travers le Funnel accéléré."
    dfi.export(style_df_in_report(df_cnm_t1), "content/"+period+"_cnm_t1_" + str(current_3pl) + ".jpg")

    df_cnm_t2 = df[
        (df["date"] >= date) & (df["courier_not_moving_metric_value"] < courier_not_moving_3) & (
                df["courier_not_moving_metric_value"] >= courier_not_moving_2) & (
                df["3pl_id"] == str(current_3pl))]
    df_cnm_t2 = df_cnm_t2.groupby("courier_id").agg(
        {"date": "first", "first_name": "first", "last_name": "first", "phone": "first",
         "is_worst_5_percent": "first"}).reset_index()
    cnm_2_recommandations = " / Appelez le coursier. / Expliquez-lui qu'il doit s'améliorer et suivre les directives de base de Glovo. / S'il ne s'améliore pas dans les 5 prochains jours, il sera au risque de passer à travers le Funnel accéléré."
    dfi.export(style_df_in_report(df_cnm_t2), "content/"+period+"_cnm_t2_" + str(current_3pl) + ".jpg")

    df_cnm_t3 = df[
        (df["date"] >= date) & (df["courier_not_moving_metric_value"] >= courier_not_moving_3) & (
                df["3pl_id"] == str(current_3pl))]
    df_cnm_t3 = df_cnm_t3.groupby("courier_id").agg(
        {"date": "first", "first_name": "first", "last_name": "first", "phone": "first",
         "is_worst_5_percent": "first"}).reset_index()
    cnm_3_recommandations = " / Appeler le coursier. / Assurez-vous que le coursier ne souffre pas d'un incident ayant entraîné l'effondrement de ses performances."
    dfi.export(style_df_in_report(df_cnm_t3), "content/"+period+"_cnm_t3_" + str(current_3pl) + ".jpg")

    return reass_1_recommandations, reass_2_recommandations, reass_3_recommandations, df_reass_t1, df_reass_t2, df_reass_t3, nslu_1_recommandations, nslu_2_recommandations, nslu_3_recommandations, df_nslu_t1, df_nslu_t2, df_nslu_t3, cnm_1_recommandations, cnm_2_recommandations, cnm_3_recommandations, df_cnm_t1, df_cnm_t2, df_cnm_t3


def prepare_funnel_data_for_current_3pl(current_3pl, funnel_df, yesterday, period):
    couriers = []
    yesterday_funnel_df = funnel_df[(pd.to_datetime(funnel_df["last_movement_date"]) == yesterday) & (
            funnel_df["3pl_id"] == str(current_3pl))].copy()
    yesterday_funnel_df = yesterday_funnel_df.drop_duplicates("email")
    for idd in yesterday_funnel_df["courier_id"]:
        courier_funnel_df = yesterday_funnel_df[(yesterday_funnel_df["courier_id"] == idd)]
        name = str(courier_funnel_df["first_name"].values[0]) + " " + str(courier_funnel_df["last_name"].values[0])
        action = courier_funnel_df["action"].values[0]
        reason = courier_funnel_df["reason"].values[0]
        next_step = ""
        recommandations = ""
        pl_id = courier_funnel_df["3pl_id"].values[0]

        if action == "WARN":
            if reason == "NO_SHOWS":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'> d'un avertissement</b> ou <b style='color:#cb0000;'>d'une suspension temporaire de 24 heures</b>."
                recommandations = "Nous recommandons d'informer le coursier sur l'importance de se présenter aux créneaux réservés et de ne pas réserver d'heures à moins que le coursier soit certain de les travailler."
            elif reason == "REASSIGNMENTS":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'> d'un avertissement</b> ou <b style='color:#cb0000;'>d'une suspension temporaire de 24 heures</b>."
                recommandations = "Nous recommandons d'éduquer le coursier sur l'importance d'accepter les commandes et de ne pas les réaffecter et de l'avertir des conséquences de cette action."
            elif reason == "COURIER_NOT_MOVING":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'> d'un avertissement</b> ou <b style='color:#cb0000;'>d'une suspension temporaire de 24 heures</b>."
                recommandations = "Nous recommandons d'éduquer le coursier sur l'importance de suivre correctement les processus Glovo, notamment en cliquant sur les boutons au bon moment et de ne pas s'arrêter pendant une commande."
            elif reason == "LATE_UNBOOKINGS":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'> d'un avertissement</b> ou <b style='color:#cb0000;'>d'une suspension temporaire de 24 heures</b>."
                recommandations = "Nous recommandons d'informer le coursier sur l'importance de ne pas annuler les créneaux réservés avant moins de 24h et de ne pas réserver d'heures à moins que le coursier soit certain de les travailler."

        elif action == "WARN":
            if reason == "NO_SHOWS":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'>  d'un avertissement</b> ou <b style='color:#cb0000;'>d'une suspension temporaire de 24 heures</b>."
                recommandations = "Nous recommandons d'informer le coursier sur l'importance de se présenter aux créneaux réservés et de ne pas réserver d'heures à moins que le coursier soit certain de les travailler."
            elif reason == "REASSIGNMENTS":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'>  d'un avertissement</b> ou <b style='color:#cb0000;'>d'une suspension temporaire de 24 heures</b>."
                recommandations = "Nous recommandons d'éduquer le coursier sur l'importance d'accepter les commandes et de ne pas les réaffecter et de l'avertir des conséquences de cette action."
            elif reason == "COURIER_NOT_MOVING":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'> d'un avertissement</b> ou <b style='color:#cb0000;'>d'une suspension temporaire de 24 heures</b>."
                recommandations = "Nous recommandons d'éduquer le coursier sur l'importance de suivre correctement les processus Glovo, notamment en cliquant sur les boutons au bon moment et de ne pas s'arrêter pendant une commande."
            elif reason == "LATE_UNBOOKINGS":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'> d'un avertissement</b> ou <b style='color:#cb0000;'>d'une suspension temporaire de 24 heures</b>."
                recommandations = "Nous recommandons d'informer le coursier sur l'importance de ne pas annuler les créneaux réservés avant moins de 24h et de ne pas réserver d'heures à moins que le coursier soit certain de les travailler."

        elif action == "TEMPORARY_BLOCK":
            if reason == "NO_SHOWS":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'> d'une suspension définitive.</b> "
                recommandations = "Nous recommandons de punir le coursier et/ou e le sensibiliser à l'importance d'arriver au travail à temps et de ne pas réserver d'heures à moins qu'il soit certain de les travailler."
            elif reason == "REASSIGNMENTS":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'> d'une suspension définitive.</b> "
                recommandations = "Nous recommandons de punir le coursier et/oude le sensibiliser à l'importance de livrer les commandes."
            elif reason == "COURIER_NOT_MOVING":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet<b style='color:#cb0000;'>  d'une suspension définitive.</b> "
                recommandations = "Nous vous recommandons de punir le coursier et/ou e le sensibiliser à l'importance de suivre correctement les processus Glovo, notamment en cliquant sur les boutons au bon moment et en ne vous arrêtant pas pendant une commande. Tout manquement sera considéré comme une fraude et ne sera pas toléré."
            elif reason == "LATE_UNBOOKINGS":
                next_step = "En fonction de l'ensemble de ses performances récentes, le coursier pourrait faire l'objet <b style='color:#cb0000;'> d'un avertissement</b> ou <b style='color:#cb0000;'>d'une suspension temporaire de 24 heures</b>."
                recommandations = "Nous recommandons de punir le coursier et/ou e le sensibiliser de ne pas annuler les créneaux réservés avant moins de 24h et de ne pas réserver d'heures à moins que le coursier soit certain de les travailler."

        elif action == "BLOCK":
            recommandations = "Le coursier est défenitivement bloqué."

        if period == "daily":
            courier = "Le coursier <span style='color:#cb0000;'>" + str(
                        name) + "</span> avec l'ID <b style='color:#cb0000;'>" + str(
                        int(idd)) + "</b> est actuellement dans le \"Funnel\" pour l'indicateur <b style='color:#cb0000;'> \"" + str(reason) + "\"</b>. Il a été le sujet de l'action <b style='color:#cb0000;'> \"" + str(action) + "\"</b> par AFM.<br>"
            if action != "BLOCK":
                courier += "Veuillez noter qu'" + next_step.lower() + ". <br> "
            courier += recommandations

            couriers.append(courier)

    return couriers
