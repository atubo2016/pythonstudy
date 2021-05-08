from datetime import datetime


# 休：工作日 变 节假日 （干脆把节日全部计入，不分周末了。反正都是休息日）
holidays_exception = [
    '20210405',  # 清明节,周一
    '20210501',  # 劳动节,周六
    '20210502',  # 劳动节,周日
    '20210503',  # 劳动节,周一
    '20210504',  # 劳动节,周二
    '20210505',  # 劳动节,周三
    '20210612',  # 端午节,周六
    '20210613',  # 端午节,周日
    '20210614',  # 端午节,周一
    '20210919',  # 中秋节,周日
    '20210920',  # 中秋节,周一
    '20210921',  # 中秋节,周二
    '20211001',  # 国庆节,周五
    '20211002',  # 国庆节,周六
    '20211003',  # 国庆节,周日
    '20211004',  # 国庆节,周一
    '20211005',  # 国庆节,周二
    '20211006',  # 国庆节,周三
    '20211007',  # 国庆节,周四
]

# 班：周末 变 工作日
workdays_exception = [
    '88888888',  # 这种情况下股市也不开，不用定义
]


def is_workday(day=None):
    """
        Args:
            day: 日期, 默认为今日

        Returns:
            True: 上班
            False: 放假
    """
    # 如果不传入参数则为今天
    today4 = datetime.today()
    # logger.info(today)
    day = day or today4

    week_day = datetime.weekday(day) + 1  # 今天星期几(星期一 = 1，周日 = 7)
    is_work_day_in_week = week_day in range(1, 6)  # 这周是不是非周末，正常工作日, 不考虑调假
    day_str = f'{day.year}{str(day.month).zfill(2)}{str(day.day).zfill(2)}'

    if day_str in workdays_exception:  # 班：周末 变 上班日
        return True
    elif day_str in holidays_exception:  # 休：工作日 变 节假日
        return False
    elif is_work_day_in_week:  # 周末
        return True
    else:
        return False


def is_holiday(day=None):
    # 如果不传入参数则为今天
    today = datetime.today()
    day = day or today
    if is_workday(day):
        return False
    else:
        return True
