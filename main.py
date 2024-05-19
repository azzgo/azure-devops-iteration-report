import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import os 

PROJECT_NAME = os.environ.get('PROJECT_NAME') or '当前项目'
# from pathlib import Path
# import json

from assemble import build_burn_down_diagram, build_cumulative_flow_diagram, extrace_date, extrace_key_data, get_summary
from client import get_current_iterations, get_iteration_odata



# stub_iteration_odata_file = open(Path(__file__).parent / 'data' / 'get_odata_current_iteration.json', 'r')
# stub_iteration_odata = json.load(stub_iteration_odata_file)

current_iteration = get_current_iterations()
odata = get_iteration_odata()

iteration_summary = get_summary(current_iteration)

columm_name_to_date_points_map = extrace_key_data(odata)

if len(odata) == 0:
    st.write(f'''
    # {PROJECT_NAME} 团队迭代进展报表

    ## Overview

    当前迭代: {iteration_summary.get('title') or '未知'}

    周期: {extrace_date(iteration_summary.get('start_date')) or '未知'} - {extrace_date(iteration_summary.get('end_date')) or '未知'}

    无迭代数据统计
    ''')
    st.stop()


st.write(f'''
# {PROJECT_NAME} 团队迭代进展报表

## Overview

当前迭代: {iteration_summary.get('title') or '未知'}

周期: {extrace_date(iteration_summary.get('start_date')) or '未知'} - {extrace_date(iteration_summary.get('end_date')) or '未知'}

## 迭代累积流图

''')



build_cumulative_flow_diagram(iteration_summary.get('date_range'), columm_name_to_date_points_map)

st.write('''
## 迭代燃尽图

''')

build_burn_down_diagram(iteration_summary.get('date_range'), columm_name_to_date_points_map)

