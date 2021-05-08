
# 本SQL 找出同一股票，按交易日排序，最新日期往前数，第一次出现跌幅的序号，亦即 连涨天数为2的股票
sql_rise2day = "    select d.stockcode as stockcode " \
      "    from ( " \
      "        select c.stockcode as stockcode, min(c.rownum) as ranking " \
      "        from  " \
      "        ( " \
      "            select " \
      "                a.stockcode as stockcode, " \
      "                a.businessday as businessday, " \
      "                a.changepercent as changepercent, " \
      "                if(@stockcode = a.stockcode, " \
      "                @rownum := @rownum + 1, " \
      "                @rownum := 1 ) as rownum, " \
      "                (@stockcode := a.stockcode) as stockcodetmp " \
      "            from " \
      "                stockhistory a, " \
      "                (select @rownum := 0,@stockcode := NULL) b " \
      "            where  " \
      "                a.changepercent is not null " \
      "            order by " \
      "                stockcode asc, " \
      "                businessday desc " \
      "        ) c " \
      "        where  " \
      "            c.changepercent < 0  " \
      "        group by  " \
      "            c.stockcode  " \
      "        order by  " \
      "            ranking asc  " \
      "    ) d " \
      "    where  " \
      "        ranking = 3 " \

# 本SQL 关联 sql_rise2day 选出的连涨2天的股票，求出 连涨2天的 单日交易量均值
sql_after2day = "    select " \
      "        c.stockcode as stockcode " \
      "        ,avg(c.dailyturnover) as avg2day_after " \
      "    from " \
      "        ( " \
      "        select " \
      "            a.stockcode as stockcode " \
      "            ,a.businessday as businessday " \
      "            ,a.changepercent as changepercent " \
      "            ,a.dailyturnover as dailyturnover  " \
      "            ,if(@stockcode = a.stockcode, " \
      "                @rownum := @rownum + 1, " \
      "                @rownum := 1 ) as rownum " \
      "            ,(@stockcode := a.stockcode) as stockcodetmp " \
      "        from " \
      "            stockhistory a, " \
      "            (select @rownum := 0,@stockcode := NULL) b " \
      "        where  " \
      "            a.changepercent is not null " \
      "        order by " \
      "            stockcode asc, " \
      "            businessday desc " \
      "        ) c " \
      "        ,rise2day " \
      "    where " \
      "        c.rownum <= 2 " \
      "        and c.stockcode = rise2day.stockcode " \
      "    group by  " \
      "        c.stockcode " \

# 本SQL 关联 sql_rise2day 选出的连涨2天的股票，求出 连涨之前 所有交易日 单日交易量均值
sql_before2day = "    select " \
      "        c.stockcode as stockcode " \
      "        ,avg(c.dailyturnover) as avg2day_before " \
      "    from " \
      "        ( " \
      "        select " \
      "            a.stockcode as stockcode " \
      "            ,a.businessday as businessday " \
      "            ,a.changepercent as changepercent " \
      "            ,a.dailyturnover as dailyturnover " \
      "            ,if(@stockcode = a.stockcode, " \
      "                @rownum := @rownum + 1, " \
      "                @rownum := 1 ) as rownum " \
      "            ,(@stockcode := a.stockcode) as stockcodetmp " \
      "        from " \
      "            stockhistory a, " \
      "            (select @rownum := 0,@stockcode := NULL) b " \
      "        where  " \
      "            a.changepercent is not null " \
      "        order by " \
      "            stockcode asc, " \
      "            businessday desc " \
      "        ) c " \
      "        , rise2day " \
      "    where " \
      "        c.rownum > 2 " \
      "        and c.stockcode = rise2day.stockcode " \
      "    group by  " \
      "        c.stockcode " \

# 本SQL 从股票履历表取出 最新 股票名称 和 股票价格
sql_lateststock = "select " \
      "    b.stockcode as stockcode , " \
      "    b.stockname as stockname , " \
      "    b.price as price " \
      "from " \
      "    ( " \
      "    select " \
      "        s.stockcode as stockcode, " \
      "        max(s.businessday) as businessday " \
      "    from " \
      "        stockhistory s " \
      "    group by " \
      "        s.stockcode ) a, " \
      "    stockhistory b " \
      "where " \
      "    a.stockcode = b.stockcode " \
      "    and a.businessday = b.businessday "
