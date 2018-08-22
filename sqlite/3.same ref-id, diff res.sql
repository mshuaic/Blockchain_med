/*the same ref-id = the same res = the same user */
select node, "ref-id", user,"res",  COUNT(*) from training_all group by "ref-id", user, "res" order by user,node, "ref-id"