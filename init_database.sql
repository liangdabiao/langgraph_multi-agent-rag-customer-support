-- Multi-Agent RAG Customer Support Database Schema
-- This script creates the complete database schema for the travel booking system

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Drop tables if they exist (for clean initialization)
DROP TABLE IF EXISTS boarding_passes;
DROP TABLE IF EXISTS ticket_flights;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS flights;
DROP TABLE IF EXISTS trip_recommendations;
DROP TABLE IF EXISTS car_rentals;
DROP TABLE IF EXISTS hotels;

-- Create flights table
CREATE TABLE flights (
    flight_id INTEGER PRIMARY KEY,
    flight_no TEXT NOT NULL,
    departure_airport TEXT NOT NULL,
    arrival_airport TEXT NOT NULL,
    scheduled_departure TIMESTAMP NOT NULL,
    scheduled_arrival TIMESTAMP NOT NULL,
    actual_departure TIMESTAMP,
    actual_arrival TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'Scheduled',
    aircraft_code TEXT
);

-- Create tickets table  
CREATE TABLE tickets (
    ticket_no TEXT PRIMARY KEY,
    book_ref TEXT NOT NULL,
    passenger_id TEXT NOT NULL
);

-- Create ticket_flights junction table
CREATE TABLE ticket_flights (
    ticket_no TEXT NOT NULL,
    flight_id INTEGER NOT NULL,
    fare_conditions TEXT NOT NULL DEFAULT 'Economy',
    PRIMARY KEY (ticket_no, flight_id),
    FOREIGN KEY (ticket_no) REFERENCES tickets(ticket_no) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE
);

-- Create boarding_passes table
CREATE TABLE boarding_passes (
    ticket_no TEXT NOT NULL,
    flight_id INTEGER NOT NULL,
    seat_no TEXT,
    PRIMARY KEY (ticket_no, flight_id),
    FOREIGN KEY (ticket_no) REFERENCES tickets(ticket_no) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE
);

-- Create hotels table
CREATE TABLE hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    price_tier TEXT NOT NULL CHECK (price_tier IN ('Budget', 'Mid-tier', 'Luxury')),
    checkin_date DATE,
    checkout_date DATE,
    booked INTEGER NOT NULL DEFAULT 0 CHECK (booked IN (0, 1))
);

-- Create car_rentals table
CREATE TABLE car_rentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    price_tier TEXT NOT NULL CHECK (price_tier IN ('Budget', 'Mid-tier', 'Luxury')),
    start_date DATE,
    end_date DATE,
    booked INTEGER NOT NULL DEFAULT 0 CHECK (booked IN (0, 1))
);

-- Create trip_recommendations table (for excursions)
CREATE TABLE trip_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    keywords TEXT,
    details TEXT,
    booked INTEGER NOT NULL DEFAULT 0 CHECK (booked IN (0, 1))
);

-- Create indexes for performance optimization
CREATE INDEX idx_tickets_passenger_id ON tickets(passenger_id);
CREATE INDEX idx_flights_departure_airport ON flights(departure_airport);
CREATE INDEX idx_flights_arrival_airport ON flights(arrival_airport);
CREATE INDEX idx_flights_scheduled_departure ON flights(scheduled_departure);
CREATE INDEX idx_hotels_location ON hotels(location);
CREATE INDEX idx_hotels_booked ON hotels(booked);
CREATE INDEX idx_car_rentals_location ON car_rentals(location);
CREATE INDEX idx_car_rentals_booked ON car_rentals(booked);
CREATE INDEX idx_trip_recommendations_location ON trip_recommendations(location);
CREATE INDEX idx_trip_recommendations_booked ON trip_recommendations(booked);