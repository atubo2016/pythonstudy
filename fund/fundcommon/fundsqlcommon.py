# 基金 load data local infile 命令行（天天基金网）
fund_load_data_infile_cmd = "mysql -uroot -p123456 myfund --local-infile -e" \
      " \"load data local infile '{0}' " \
      "REPLACE into table fundhistory " \
      "CHARACTER SET gbk " \
      "FIELDS TERMINATED BY ',' " \
      "ENCLOSED BY '''' " \
      "LINES TERMINATED BY '\\r\\n' " \
      "IGNORE 1 LINES " \
      "(fundcode,fundname,@businessday,@netassetvalue,@accumulatedtotolnetvalue," \
      "@dailygrowthrate,@weekgrowthrate,@monthgrowthrate,@threemonthgrowthrate,@halfyeargrowthrate) " \
      "SET " \
      "businessday = CASE WHEN @businessday<>'---' THEN @businessday ELSE '{1}' END," \
      "netassetvalue = CASE WHEN @netassetvalue<>'---' THEN @netassetvalue END," \
      "accumulatedtotolnetvalue = CASE WHEN @accumulatedtotolnetvalue<>'---' THEN @accumulatedtotolnetvalue END," \
      "dailygrowthrate = CASE WHEN @dailygrowthrate<>'---' THEN @dailygrowthrate END," \
      "weekgrowthrate = CASE WHEN @weekgrowthrate<>'---' THEN @weekgrowthrate END," \
      "monthgrowthrate = CASE WHEN @monthgrowthrate<>'---' THEN @monthgrowthrate END," \
      "threemonthgrowthrate = CASE WHEN @threemonthgrowthrate<>'---' THEN @threemonthgrowthrate END," \
      "halfyeargrowthrate = CASE WHEN @halfyeargrowthrate<>'---' THEN @halfyeargrowthrate END, " \
      "downloaddate = now();\""

# 基金 load data local infile 命令行（和讯网）
fund_load_data_infile_cmd_hexun = "mysql -uroot -p123456 myfund --local-infile -e" \
      " \"load data local infile '{0}' " \
      "REPLACE into table fundhistory_hexun " \
      "CHARACTER SET gbk " \
      "FIELDS TERMINATED BY ',' " \
      "ENCLOSED BY '''' " \
      "LINES TERMINATED BY '\\r\\n' " \
      "IGNORE 1 LINES " \
      "(fundcode,fundname,@businessday,@netassetvalue,@accumulatedtotolnetvalue," \
      "@dailygrowthrate,@weekgrowthrate,@monthgrowthrate,@threemonthgrowthrate,@halfyeargrowthrate) " \
      "SET " \
      "businessday = CASE WHEN @businessday<>'--' THEN @businessday ELSE '{1}' END," \
      "netassetvalue = CASE WHEN @netassetvalue<>'--' THEN @netassetvalue END," \
      "accumulatedtotolnetvalue = CASE WHEN @accumulatedtotolnetvalue<>'--' THEN @accumulatedtotolnetvalue END," \
      "dailygrowthrate = CASE WHEN @dailygrowthrate<>'--' THEN @dailygrowthrate END," \
      "weekgrowthrate = CASE WHEN @weekgrowthrate<>'--' THEN @weekgrowthrate END," \
      "monthgrowthrate = CASE WHEN @monthgrowthrate<>'--' THEN @monthgrowthrate END," \
      "threemonthgrowthrate = CASE WHEN @threemonthgrowthrate<>'--' THEN @threemonthgrowthrate END," \
      "halfyeargrowthrate = CASE WHEN @halfyeargrowthrate<>'--' THEN @halfyeargrowthrate END, " \
      "downloaddate = now();\""
