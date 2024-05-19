# type: ignore
from streamlit_echarts import st_echarts
from datetime import datetime, timedelta

columns = ["Ready For DEV", "IN DEV", "Block",
           "Ready For QA", "IN QA", "QA DONE"]
columnsColorMap = {
    "Ready For DEV": "#4793AF",
    "IN DEV": "#007F73",
    "Block": "#4CCD99",
    "Ready For QA": "#FF6500",
    "IN QA": "#C40C0C",
    "QA DONE": "#5BBCFF",
}

cumulative_coverage_report_options = {
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
    },
    "legend": {"data": columns},
    "toolbox": {"feature": {"saveAsImage": {}}},
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "xAxis": [
        {
            "type": "category",
            "boundaryGap": False,
            "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        }
    ],
    "yAxis": [{"type": "value"}],
    "series": [],
}


def extrace_date(date_str):
    if date_str is None:
        return None
    return date_str.split('T')[0]


def extrace_key_data(data_list):
    columm_name_to_date_points_map = {}

    # 遍历数据列表
    for item in data_list:
        # 解析日期并添加到日期范围列表，如果它还不在列表中
        date = extrace_date(item.get("DateValue"))  # 获取日期部分

        # 获取ColumnName和TotalStoryPoints
        column_name = item.get("ColumnName")
        total_story_points = item.get("TotalStoryPoints")

        # 如果ColumnName不在字典中，初始化一个新的字典来存储日期和对应的TotalStoryPoints
        if column_name not in columm_name_to_date_points_map:
            columm_name_to_date_points_map[column_name] = {}

        # 累加对应日期的TotalStoryPoints if date in columnName_to_date_group_story_points[column_name]:
            if columm_name_to_date_points_map[column_name].get(date) is None:
                columm_name_to_date_points_map[column_name][date] = 0
            columm_name_to_date_points_map[column_name][date] += total_story_points or 0
        else:
            columm_name_to_date_points_map[column_name][date] = total_story_points or 0

    return columm_name_to_date_points_map


def build_cumulative_flow_diagram(dateRange, columm_name_to_date_points_map):
    cumulative_coverage_report_options['xAxis'][0]['data'] = dateRange
    cumulative_coverage_report_options['series'] = [
        {
            "name": column_name,
            "type": "line",
            "areaStyle": {
                'zLevel': len(dateRange) - columns.index(column_name),
                'color': columnsColorMap.get(column_name),
                'opacity': 1,
            },
            "lineStyle": {
                'color': columnsColorMap.get(column_name)
            },
            "itemStyle": {
                'color': columnsColorMap.get(column_name)
            },
            "data": [get_cumulative_column_story_points(column_name, date, columm_name_to_date_points_map) for date in dateRange],
        } for column_name in columns
    ]

    # map cumulative_coverage_report_options, when column_name name is 'Ready for Dev', if the date is zero, revalue it to last date value
    for series in cumulative_coverage_report_options['series']:
        if series.get('name') == 'Ready For DEV':
            for i in range(len(series['data'])):
                if series['data'][i] == None and i > 0:
                    series['data'][i] = series['data'][i - 1]

    st_echarts(options=cumulative_coverage_report_options, height='500px')


def get_cumulative_column_story_points(column_name: str, dateKey: str, columm_name_to_date_points_map) -> int:
    today = datetime.today().strftime('%Y-%m-%d')
    if dateKey > today:
        return None
    column = columm_name_to_date_points_map.get(column_name)
    if column is None:
        column = {}
    if column_name == 'QA DONE':
        return column.get(dateKey) or 0
    if column_name == 'IN QA':
        return (column.get(dateKey) or 0) + get_cumulative_column_story_points('QA DONE', dateKey, columm_name_to_date_points_map)
    if column_name == 'Ready For QA':
        return (column.get(dateKey) or 0) + get_cumulative_column_story_points('IN QA', dateKey, columm_name_to_date_points_map)
    if column_name == 'Block':
        return (column.get(dateKey) or 0) + get_cumulative_column_story_points('Ready For QA', dateKey, columm_name_to_date_points_map)
    if column_name == 'IN DEV':
        return (column.get(dateKey) or 0) + get_cumulative_column_story_points('Block', dateKey, columm_name_to_date_points_map)
    if column_name == 'Ready For DEV':
        return (column.get(dateKey) or 0) + get_cumulative_column_story_points('IN DEV', dateKey, columm_name_to_date_points_map)
    return 0


burn_down_option = {
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
    },
    'xAxis': {
        'type': 'category',
        'data': []
    },
    "legend": {"data": ["remaining", "totalScope", "ideal"]},
    'yAxis': {
        'type': 'value'
    },
    'series': []
}


def build_burn_down_diagram(dateRange, columm_name_to_date_points_map):
    planning_story_points = sum([dateRangeData.get(
        dateRange[0]) or 0 for dateRangeData in columm_name_to_date_points_map.values()], 0)
    # QA DONE is DONE
    # burn_down key remaining story points, total scope story points, and ideal story points by date
    burn_down_by_date = {}
    for date in dateRange:
        total_scope = sum_by_data(date, columm_name_to_date_points_map)
        if total_scope == 0:
            burn_down_by_date[date] = {
                'remaining': None,
                'totalScope': None,
                'ideal': get_ideal_points(date, dateRange[0], dateRange[-1], planning_story_points)
            }
            continue
        burn_down_by_date[date] = {
            'remaining': total_scope - ((columm_name_to_date_points_map.get('QA DONE') or {}).get(date) or 0),
            'totalScope': total_scope,
            'ideal': get_ideal_points(date, dateRange[0], dateRange[-1], planning_story_points)
        }

    burn_down_option['xAxis']['data'] = dateRange
    burn_down_option['series'] = [
        {
            "name": "remaining",
            "type": "line",
            "data": [burn_down_by_date[date].get('remaining') for date in dateRange],
            "smooth": True
        },
        {
            "name": "ideal",
            "type": "line",
            "data": [burn_down_by_date[date].get('ideal') for date in dateRange],
            "smooth": True
        },
        {
            "name": "totalScope",
            "type": "line",
            "data": [burn_down_by_date[date].get('totalScope') for date in dateRange],
            "smooth": True
        }
    ]

    st_echarts(options=burn_down_option, height='500px')


def sum_by_data(date, columm_name_to_date_points_map) -> int:
    return sum([dateRangeData.get(date) or 0 for dateRangeData in columm_name_to_date_points_map.values()], 0)


def get_ideal_points(date: str, start_data: str, end_data: str, totalScope: int) -> int:
    date_start = datetime.strptime(start_data, '%Y-%m-%d')
    date_end = datetime.strptime(end_data, '%Y-%m-%d')
    date = datetime.strptime(date, '%Y-%m-%d')
    return totalScope - int(totalScope / (date_end - date_start).days * (date - date_start).days)


def get_summary(iteration_info):
    if len(iteration_info) == 0:
        return {}
    iteration = iteration_info[0].get("attributes")
    start_data = iteration.get('startDate')
    end_data = iteration.get('finishDate')

    return {
        'title': iteration_info[0].get('name'),
        'start_date': start_data,
        'end_date': end_data,
        'date_range': get_date_range(start_data, end_data),
    }


def get_date_range(start_date_str, end_date_str):
    if start_date_str is None or end_date_str is None:
        return []

    start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%SZ')
    finish_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%SZ')
    date_range = []
    current_date = start_date
    while current_date <= finish_date:
        date_range.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return date_range
