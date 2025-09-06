SELECT
    t.ticket_no, t.book_ref,
    f.flight_id, f.flight_no, f.departure_airport, f.arrival_airport, f.scheduled_departure, f.scheduled_arrival,
    bp.seat_no, tf.fare_conditions
FROM 
    tickets t
    JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
    JOIN flights f ON tf.flight_id = f.flight_id
    LEFT JOIN boarding_passes bp ON bp.ticket_no = t.ticket_no AND bp.flight_id = f.flight_id
WHERE 
    t.passenger_id = '5102 899977'; 
