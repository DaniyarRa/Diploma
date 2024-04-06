select
    *
from (
    select
        id,
        score,
        round(min(distance)) as next_police_dep_distance,
        round(avg(distance)) as near_3_police_dep_distance
    from (
        select
            *,
            row_number() over (PARTITION BY temp.id ORDER BY distance) as rn
        from (
            select
                ar.id,
                ar.score,
                ST_Distance(
                    ST_Transform(ST_SetSRID(ST_MakePoint(ar.longitude + 0.00125, ar.latitude - 0.00125), 4326), 26986),
                    ST_Transform(ST_SetSRID(ST_MakePoint(pd.longitude, pd.latitude), 4326), 26986)
                ) AS distance
            from mart.area_scoring as ar
                cross join public.police_department as pd
            where ar.step_id = 1) temp) temp2
    where temp2.rn <= 3
    group by id, score) temp3
order by score desc;