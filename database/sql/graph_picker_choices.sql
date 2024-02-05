SELECT DISTINCT
    Station.name AS station,
    Measurement.name AS measurement,
    MeasurementInterval.name AS interval
FROM Reading
LEFT JOIN Station ON Reading.stationId = Station.id
LEFT JOIN Measurement ON Reading.measurementId = Measurement.id
LEFT JOIN MeasurementInterval ON Reading.intervalId = MeasurementInterval.id