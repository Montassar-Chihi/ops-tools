# import libraries
import pandas as pd
import datetime
from utilities.queries import *
from utilities.dataLoader import *
from reportGenerator.dataPreprocessor import preprocess_automatic_email_data
from reportGenerator.dataProcessor import *
from reportGenerator.pdfGenerator import generate_pdf_for_current_3pl
from emailManager.emailSender import send_all_emails
from emailManager.emailWriter import write_email_for_current_3pl


def send_reports(current_period=None):

    ###############################################################
    # Params
    ###############################################################
    if current_period is None:
        now = datetime.datetime.now()
        now_name = now.strftime("%A")
        if now_name.lower() == "monday":
            period = "weekly"
            date = pd.to_datetime(datetime.date.today() - datetime.timedelta(days=7))
        else:
            period = "daily"
            date = pd.to_datetime(datetime.date.today() - datetime.timedelta(days=1))
    else:
        if current_period == "weekly":
            period = "weekly"
            date = pd.to_datetime(datetime.date.today() - datetime.timedelta(days=7))
        elif current_period == "daily":
            period = "daily"
            date = pd.to_datetime(datetime.date.today() - datetime.timedelta(days=1))

    # Reass thresholds
    reass_abs_threshold_1 = 0.15
    reass_abs_threshold_2 = 0.3
    reass_abs_threshold_3 = 0.6
    # No_shows_late_unbooks thresholds
    no_shows_late_unbooks_1 = 0.2
    no_shows_late_unbooks_2 = 0.4
    no_shows_late_unbooks_3 = 0.9
    # Courier_not_moving thresholds
    courier_not_moving_1 = 0.2
    courier_not_moving_2 = 0.4
    courier_not_moving_3 = 0.8
    # 3pls
    funnels_3pls = {}
    mail_tables = {}
    messages = {}
    all_3pls = {
        "399": "Yassine Ferjani",
        "401": "Assala Nasser",
        "421": "Courier One",
        "422": "The Castle Delivery Yasser",
        "478": "Urban Courier",
        "2,720": "STE Chalghmi Zied",
        "2,983": "Big 4 Delivery",
        "3,029": "GO2GO Delivery",
        "3,164": "Mayen Express",
        "3,199": "FlexyFleet",
        "101": "Freelancer",
        "3,207": "MAG Delivery",
        "3,206": "Principe de Cayena"
    }
    emails_3pls = {
        "399": "mbekri@outlook.com, ferjaniyassin864@gmail.com",
        "401": "assalanasser896@gmail.com",
        "421": "courierone2023@gmail.com, omarparkour2002@gmail.com ",
        "422": "yasserkhelifa@yahoo.fr",
        "478": "hafedhanane.urbancourier@gmail.com",
        "2,720": "Cd.glovo@gmail.com",
        "2,983": "big4delivery.2023@gmail.com",
        "3,029": "go2godelivery@gmail.com",
        "3,164": "direction@mayen-express.com",
        "3,199": "FlexyFleetTN@gmail.com",
        "101": "ops-tn@glovoapp.com",
        "3,207": "deliveryservicesmag@gmail.com",
        "3,206": "Khmirimouhamedamine@gmail.com"
    }

    ###############################################################
    # Load data from database
    ###############################################################
    # print("start loading from livedb")
    # couriers_df = load_data_from_livedb(courier_df_query)
    # print("courier df data loaded")
    per_df = load_data_from_starburst(query)
    funnel_df = load_data_from_starburst(query_funnel)
    metrics_df = load_data_from_starburst(query_metrics)
    capus_df = load_data_from_starburst(query_capus)
    check_in_no_work_df = load_data_from_starburst(query_check_in_no_no_work)
    gps_fraud_df = load_data_from_starburst(query_gps_fraud)
    excellence_score_df = load_data_from_starburst(query_excellence_score)
    print("step 1 (done): courier data loaded")

    ###############################################################
    # save data for later use
    ###############################################################
    # couriers_df.to_csv("data/courier_db.csv")
    metrics_df.to_csv("data/metrics_df.csv")
    funnel_df.to_csv("data/funnel_df.csv")
    per_df.to_csv("data/per_df.csv")
    capus_df.to_csv("data/capus_df.csv")
    check_in_no_work_df.to_csv("data/check_in_no_work_df.csv")
    gps_fraud_df.to_csv("data/gps_fraud_df.csv")
    excellence_score_df.to_csv('data/excellence_score.csv')
    print("step 2 (done): courier data saved")

    ###############################################################
    # preprocess data
    ###############################################################
    df, couriers_df, per_df, metrics_df, funnel_df, gps_fraud_df, capus_df, check_in_no_work_df = preprocess_automatic_email_data()
    print("step 3 (done): courier data processed")

    ###############################################################
    # Generate reports and email content for all 3pls
    ###############################################################
    for current_3pl in list(all_3pls.keys()):
        try:

            # AFM metrics in the pdf
            reass_1_recommandations, reass_2_recommandations, reass_3_recommandations, df_reass_t1, df_reass_t2, df_reass_t3, \
            nslu_1_recommandations, nslu_2_recommandations,nslu_3_recommandations, df_nslu_t1, df_nslu_t2, df_nslu_t3, \
            cnm_1_recommandations, cnm_2_recommandations, cnm_3_recommandations, df_cnm_t1, df_cnm_t2, df_cnm_t3 = prepare_afm_metrics_for_current_3pl(
                df,date, period, current_3pl, reass_abs_threshold_1, reass_abs_threshold_2,
                                        reass_abs_threshold_3, no_shows_late_unbooks_1, no_shows_late_unbooks_2,
                                        no_shows_late_unbooks_3, courier_not_moving_1, courier_not_moving_2,
                                        courier_not_moving_3)

            # 3pl stats in the pdf
            avg_total_funnel_moves,total_funnel_ends,total_funnel_moves = prepare_3pl_stats_for_current_3pl(df, date, current_3pl, funnel_df,period)

            gps_fraud_couriers = pd.DataFrame()
            capus_couriers = pd.DataFrame()
            check_in_no_work_couriers = pd.DataFrame()
            if period == "daily":
                # Funnel messages in the email
                funnels_3pls[current_3pl] = prepare_funnel_data_for_current_3pl(current_3pl, funnel_df, date,period)

                # Fraudulent couriers in the pdf
                gps_fraud_couriers, capus_couriers, check_in_no_work_couriers = prepare_fraud_metrics_for_current_3pl(
                    current_3pl, date, period, gps_fraud_df, capus_df, check_in_no_work_df)

                # Don't touch
                total_funnel_ends = 0
                total_funnel_moves = 0

            # Generate the pdf report
            report_subtitle = generate_pdf_for_current_3pl(current_3pl, period, all_3pls, date,
                                         df_reass_t1, reass_1_recommandations, df_reass_t2, reass_2_recommandations,
                                         df_reass_t3, reass_3_recommandations,
                                         df_nslu_t1, nslu_1_recommandations, df_nslu_t2, nslu_2_recommandations,
                                         df_nslu_t3, nslu_3_recommandations,
                                         df_cnm_t1, cnm_1_recommandations, df_cnm_t2, cnm_2_recommandations, df_cnm_t3,
                                         cnm_3_recommandations,
                                         gps_fraud_couriers, capus_couriers, check_in_no_work_couriers,
                                         total_funnel_ends, avg_total_funnel_moves, total_funnel_moves)
            # Generate email content
            messages = write_email_for_current_3pl(period, current_3pl, all_3pls, funnels_3pls, messages, report_subtitle)

        except Exception as e:
            print("error :" + str(current_3pl))
            print(e)

    print("step 4 (done): reports generated")
    # Send all emails
    send_all_emails(all_3pls, emails_3pls, messages)
    print("step 5 (done): reports sent")

