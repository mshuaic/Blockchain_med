/* same ts, a user may have multiple activities simultaneously at distinct nodes*/

select * from training_all 
where ts in 
(SELECT ts from training_all GROUP BY ts,user  having count(*)>1)
and user in 
(SELECT user from training_all GROUP BY ts,user  having count(*)>1)
ORDER BY user,ts