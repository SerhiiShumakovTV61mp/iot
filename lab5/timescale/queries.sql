-- 1) Сирі дані за останню годину
SELECT time, irradiance, temp, power, pr
FROM telemetry
WHERE device = 'panel01' AND time > now() - INTERVAL '1 hour'
ORDER BY time;

-- 2) Середнє за 5-хвилинні вікна за останню годину
SELECT time_bucket('5 minutes', time) AS bucket,
       round(avg(power)::numeric, 1)  AS avg_power,
       round(avg(temp)::numeric, 1)   AS avg_temp
FROM telemetry
WHERE device = 'panel01' AND time > now() - INTERVAL '1 hour'
GROUP BY bucket
ORDER BY bucket;
