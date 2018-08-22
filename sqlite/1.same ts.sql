/* at the same ts,  multiple activities happen */
select * from training_all where ts in
(SELECT ts from training_all GROUP BY ts  having count(*)>1) ORDER BY ts