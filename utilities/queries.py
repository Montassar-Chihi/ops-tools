courier_df_query = '''
SELECT 
    couriers.id, users.name, CONCAT(users.first_surname, ' ', IF(users.second_surname IS NULL,'',users.second_surname)), 
    couriers.address, couriers.enabled, couriers.transport, couriers.city_code, couriers.birth_day, phone_numbers.number, 
    d.app_version, d.os, users.preferred_language, cities.country_code, couriers.box, couriers.nif, couriers.postal_code, 
    couriers.city_code, users.email, 0 AS code, couriers.iban 
FROM couriers JOIN users ON couriers.id = users.id JOIN phone_numbers ON phone_numbers.user_id = users.id 
JOIN cities ON cities.code = couriers.city_code LEFT OUTER JOIN devices d ON users.id = d.user_id 
WHERE couriers.city_code in ('TIS','SOU','TIE','BES','SFX','NSO') 
GROUP BY couriers.id
'''

query_kickouts_during_saturation = '''
SELECT 
     kicked_courier_slots.creation_time as kickout_time, start_time as slot_start_time, city_code, courier_id, slot_id,
     kickout_reason, kickout_type, kickout_details 
 FROM kicked_courier_slots LEFT JOIN scheduling_slots ON kicked_courier_slots.slot_id = scheduling_slots.id 
 left join cities ON scheduling_slots.city_code = cities.code 
 WHERE country_code = 'TN' AND kickout_reason in (4,2) and start_time between now() - INTERVAL 0 HOUR and now() + INTERVAL 1 HOUR 
ORDER BY courier_id, kickout_time, city_code
'''

query = '''
SELECT 
*
FROM 
"delta"."courier__courier_performance_analytics__odp"."courier_performance_analytics_courier_day_level_components" 
WHERE country_code = 'TN'
AND p_aggregation_date >= DATE_ADD('day', -28,CURRENT_DATE)

'''

query_funnel = '''
SELECT 
last_movement_date,
courier_id,
city_code,
CASE
    WHEN metric_id = 1 THEN 'Reassignments'
    WHEN metric_id = 2 THEN 'Late_unbooks_and_no_shows'
    ELSE 'Courier_not_moving'
END AS metric,
CASE
    WHEN step_id = 1 THEN '1'
    WHEN step_id = 2 THEN '2'
    WHEN step_id = 3 THEN '3'
    WHEN step_id = 4 THEN '4'
    ELSE 'left the funnel'
END AS step,
CASE 
    WHEN step_id > 1 AND cycle_point = 'START' THEN 'START Accelerated Funnel'
    ELSE cycle_point 
END AS cycle_point,
metric_value,
reason
FROM 
"delta"."courier_fleet_quality_odp"."funnel_tracker" AS funnel_tracker
WHERE city_code IN ('TIS','SOU','SFX')
AND cycle_point NOT IN ('NO_CHANGE')
AND funnel_tracker.p_calculation_date >= DATE_ADD('day', -28,CURRENT_DATE)

'''
query_metrics = '''
SELECT 
p_calculation_date AS "date",
courier_id,
CASE
    WHEN metric_id = 1 THEN 'Reassignments'
    WHEN metric_id = 2 THEN 'Late_unbooks_and_no_shows'
    ELSE 'Courier_not_moving'
END AS metric,
metric_value 
FROM 
"delta"."courier_fleet_quality_odp"."metric_value"
WHERE city_code in ('TIS','SOU','SFX')
AND p_calculation_date >= DATE_ADD('day', -28,CURRENT_DATE)

'''
query_check_in_no_no_work = '''
SELECT
    courier_performance_analytics_courier_day_level_components.courier_id  AS "courier_id",
        (DATE_FORMAT(courier_performance_analytics_courier_day_level_components.p_aggregation_date , '%Y-%m-%d')) AS "p_aggregation_date_date",
    COALESCE(SUM(courier_performance_analytics_courier_day_level_components.n_slots_booked ), 0) AS "n_slots_booked",
    COALESCE(SUM(courier_performance_analytics_courier_day_level_components.n_slots_checked_in ), 0) AS "n_slots_checked_in",
    COALESCE(SUM(courier_performance_analytics_courier_day_level_components.num_assignments ), 0) AS "num_assignments",
    COALESCE(SUM(courier_performance_analytics_courier_day_level_components.num_orders ), 0) AS "num_orders"
FROM delta.courier__courier_performance_analytics__odp
  .courier_performance_analytics_courier_day_level_components  AS courier_performance_analytics_courier_day_level_components
WHERE ( courier_performance_analytics_courier_day_level_components.p_aggregation_date  ) >= DATE_ADD('day',-7,CURRENT_DATE)
        AND (courier_performance_analytics_courier_day_level_components.city_code ) = 'TIS'
        AND num_orders = 0 
        AND n_slots_checked_in > 1
        AND num_assignments = 0
        AND (n_slots_checked_in >= 0.5 * n_slots_booked)
GROUP BY
    1,
    2
ORDER BY
    2
'''

query_gps_fraud = '''
WITH speed_and_fraud AS (
    WITH location_pairs AS (
        WITH check_in_location_history AS (
            SELECT DISTINCT
                check_in_data.courier_id,
                check_in_data.event_created_at AS check_in_time,
                location_data.event_created_at AS location_time,

                --location_data.app_version,
                --location_data.device_id,
                --location_data.device_platform,

                location_data.position_latitude,
                location_data.position_longitude

            FROM delta.courier_logistics_scheduling_odp.courier_slot_checked_in_event check_in_data
            LEFT JOIN
                (
                 SELECT *
                 FROM delta.courier_glovo_maps_odp.courier_tracking_states
                 WHERE p_event_date >= DATE_ADD('day',-7,CURRENT_DATE) ) 
                 location_data ON check_in_data.courier_id = location_data.courier_id
                                    AND location_data.event_created_at >= DATE_ADD('minute',-10,check_in_data.event_created_at)
                                    AND location_data.event_created_at <= DATE_ADD('minute',60,check_in_data.event_created_at)
            WHERE check_in_data.p_creation_date >= DATE_ADD('day',-7,CURRENT_DATE)
            AND check_in_data.courier_id IN (
                SELECT DISTINCT courier_id FROM delta.central_order_descriptors_odp.order_descriptors_v2
                WHERE order_handling_strategy = 'GEN2'
                AND order_final_status = 'DeliveredStatus'
                AND order_city_code = 'TIS'
                AND p_creation_date >= DATE_ADD('month',-3,CURRENT_DATE)
                AND DATE(order_activated_local_at) >=  DATE_ADD('day',-7,CURRENT_DATE)
                )
            ORDER BY 1,2,3
        )
        SELECT
            courier_id,
            check_in_time,
            location_time,
            LAG(location_time) OVER (PARTITION BY check_in_time ORDER BY location_time) AS prev_location_time,

            position_latitude,
            position_longitude,

            LAG(position_latitude) OVER (PARTITION BY check_in_time ORDER BY location_time) AS prev_latitude,
            LAG(position_longitude) OVER (PARTITION BY check_in_time ORDER BY location_time) AS prev_longitude

        FROM check_in_location_history
        ORDER BY 1,2,3
    )
    SELECT
        courier_id,
        check_in_time,
        location_time,
        CASE WHEN location_time <= check_in_time THEN 'before_check_in' ELSE 'after_check_in' END AS fraud_timing,
        position_latitude,
        position_longitude,
        prev_location_time,
        1.000 * DATE_DIFF('millisecond',prev_location_time,location_time) / 1000 AS seconds_time,
        ROUND(6371 * ACOS(SIN(RADIANS(position_latitude)) * SIN(RADIANS(prev_latitude)) + COS(RADIANS(position_latitude)) * COS(RADIANS(prev_latitude)) * COS(RADIANS(position_longitude - prev_longitude))),2) AS dist_km,
        ROUND(6371 * ACOS(SIN(RADIANS(position_latitude)) * SIN(RADIANS(prev_latitude)) + COS(RADIANS(position_latitude)) * COS(RADIANS(prev_latitude)) * COS(RADIANS(position_longitude - prev_longitude))) / (1.000000 * DATE_DIFF('millisecond',prev_location_time,location_time) / 3600000),2) AS speed_kph
    FROM location_pairs
    ORDER BY 1,2,3
)
SELECT
    *
FROM speed_and_fraud
WHERE speed_and_fraud.speed_kph >= 150
AND speed_and_fraud.dist_km >= 0.2

'''

query_capus = '''
SELECT
    order_descriptors.order_cancel_reason  AS "order_cancel_reason",
    order_descriptors.courier_id  AS "courier_id",
        (DATE_FORMAT(order_descriptors.order_activated_at , '%Y-%m-%d')) AS "order_activated_date",
    ( COUNT(DISTINCT CASE WHEN (order_descriptors.order_final_status = 'CanceledStatus') THEN order_descriptors.order_id  ELSE NULL END) ) - ( COUNT(DISTINCT(CASE WHEN
        order_descriptors.order_final_status = 'CanceledStatus'
        AND (DATE_DIFF('second', order_descriptors.order_created_local_at, order_descriptors.order_terminated_local_at) / 60.0 <= 5
        OR (order_descriptors.order_scheduled_local_at IS NOT NULL
        AND (order_descriptors.order_activated_local_at IS NULL
        OR DATE_DIFF('second', order_descriptors.order_activated_local_at, order_descriptors.order_terminated_local_at) / 60.0 <= 5)))
        AND (order_descriptors.order_cancel_reason IS NULL OR order_descriptors.order_cancel_reason IN
        ('SELF_CANCELLATION', 'UNKNOWN','OTHER', 'DELIVERY_TAKING_TOO_LONG',
        'COURIER_NOT_ASSIGNED', 'CUSTOMER_DOESNT_WANT_PRODUCTS'))
        THEN order_descriptors.order_id ELSE NULL END
        ))) AS "hard_cancellation_number",
    COUNT(DISTINCT order_descriptors.order_id ) AS "number_of_orders"
FROM delta.central_order_descriptors_odp.order_descriptors_v2  AS order_descriptors
WHERE (order_descriptors.order_country_code ) = 'TN' 
AND (( order_descriptors.order_activated_local_at  )) >= ((DATE_ADD('day', -7, CAST(CAST(DATE_TRUNC('DAY', NOW()) AS DATE) AS TIMESTAMP)))) 
GROUP BY
    1,
    2,
    3
HAVING (((( (COUNT(DISTINCT CASE WHEN (order_descriptors.order_final_status = 'CanceledStatus') THEN order_descriptors.order_id  ELSE NULL END)) - (COUNT(DISTINCT(CASE WHEN
        order_descriptors.order_final_status = 'CanceledStatus'
        AND (DATE_DIFF('second', order_descriptors.order_created_local_at, order_descriptors.order_terminated_local_at) / 60.0 <= 5
        OR (order_descriptors.order_scheduled_local_at IS NOT NULL
        AND (order_descriptors.order_activated_local_at IS NULL
        OR DATE_DIFF('second', order_descriptors.order_activated_local_at, order_descriptors.order_terminated_local_at) / 60.0 <= 5)))
        AND (order_descriptors.order_cancel_reason IS NULL OR order_descriptors.order_cancel_reason IN
        ('SELF_CANCELLATION', 'UNKNOWN','OTHER', 'DELIVERY_TAKING_TOO_LONG',
        'COURIER_NOT_ASSIGNED', 'CUSTOMER_DOESNT_WANT_PRODUCTS'))
        THEN order_descriptors.order_id ELSE NULL END
        ))) )) > 0)) AND AVG(( date_diff('minute', order_descriptors.order_picked_up_by_courier_local_at , order_descriptors.order_courier_arrival_to_delivery_local_at ) ) ) IS NOT NULL
ORDER BY
    1
'''
query_excellence_score = '''
SELECT
    (DATE_FORMAT(excellence_score_courier_level_features.p_calculation_date , '%Y-%m-%d')) AS "date",
    excellence_score_courier_level_features.courier_id  AS "courier_id",
    excellence_score_courier_level_features.city_code  AS "city_code",
    excellence_score_courier_level_features.excellence_score_displayed  AS "excellence_score"
FROM delta.courier__excellence_score_analytics__odp.excellence_score_courier_level_features  AS excellence_score_courier_level_features
WHERE ((( excellence_score_courier_level_features.p_calculation_date  ) >= ((DATE_ADD('day', -28, CAST(CAST(DATE_TRUNC('DAY', NOW()) AS DATE) AS TIMESTAMP)))) AND 
city_code IN ('TIS','SOU','SFX') AND is_working_date = TRUE  ))
ORDER BY
    1 DESC
'''


