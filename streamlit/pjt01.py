import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import plotly.express as px
import math


def get_data_from_db(query):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='pjt01'
        )
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    except mysql.connector.Error as err:
        st.error(f"데이터베이스 오류: {err}")
        return pd.DataFrame()  # 빈 데이터프레임 반환
    finally:
        cursor.close()
        connection.close()
        
def get_data_from_db_2(query, params):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='pjt01'
        )
        cursor = connection.cursor(dictionary=True)
        
        # 쿼리 실행
        cursor.execute(query, params)
        result = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # 데이터를 Pandas DataFrame으로 변환
        df = pd.DataFrame(result)
        return df
    except mysql.connector.Error as err:
        st.error(f"데이터베이스 쿼리 오류: {err}")
        return pd.DataFrame()  # 빈 데이터프레임 반환
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return pd.DataFrame()  # 빈 데이터프레임 반환

def get_faq_for_table(table_name):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='pjt01'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # 선택된 테이블의 모든 FAQ를 가져오는 쿼리
        query = f'SELECT company, question, answer FROM {table_name}'
        cursor.execute(query)
        faqs = cursor.fetchall()

        conn.close()
        
        return faqs
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return []

def display_vehicle_data(df):
    for index, row in df.iterrows():
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.image(row['vehicle_img'], width=100)

        with col2:
            st.markdown(f"<h3 style='font-size: 24px;'>{row['vehicle_name']}</h3>", unsafe_allow_html=True)  # 글자 크기 조정

        with col3:
            if row['vehicle_link']:
                st.markdown(
                    f"<a href='{row['vehicle_link']}' style='color: #007bff; text-decoration: none;'>모델 상세 사이트</a>",
                    unsafe_allow_html=True
                )

# 사이드바에서 페이지 선택
if 'page' not in st.session_state:
    st.session_state.page = "회사별 판매량 조회"

# 사이드바 디자인
with st.sidebar:
    st.title("메뉴")
    selected_page = option_menu(
        menu_title=None,  # 메뉴 제목
        options=["회사별 판매량 조회", "회사별 자동차 조회", "모델별 차량 판매량 조회", "자동차 회사 FAQ"],  # 옵션 리스트
        # icons=["bar-chart", "car", "calendar"],  # 아이콘 리스트 (원하는 아이콘으로 변경 가능)
        menu_icon="cast",  # 메뉴 아이콘
        default_index=["회사별 판매량 조회", "회사별 자동차 조회", "모델별 차량 판매량 조회", "자동차 회사 FAQ"].index(st.session_state.page),  # 기본 선택 인덱스
        styles={
            "container": {"padding": "5!important", "background-color": "#2e2e2e"},  # 어두운 배경 색상
            "icon": {"font-size": "20px", "color": "#ffffff"},  # 아이콘 색상
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "#ffffff"},  # 링크 스타일 및 색상
            "nav-link-selected": {"background-color": "#007bff", "color": "#ffffff"},  # 선택된 링크 배경 색상 및 텍스트 색상
        }
    )

    st.session_state.page = selected_page  # 선택된 페이지 상태 업데이트


if st.session_state.page == "회사별 판매량 조회":
    st.title("회사별 판매량 조회")
    
    # 월 선택 드롭다운
    month = st.selectbox("조회할 월을 선택하세요", 
                          pd.date_range(start="2022-01-01", end="2024-07-31", freq='M').strftime('%Y-%m').tolist(),
                          index=pd.date_range(start="2022-01-01", end="2024-07-31", freq='M').strftime('%Y-%m').tolist().index('2024-07'))
    
    # 선택된 월을 'YYYY-MM-01' 형식으로 변환
    selected_date = f"{month}-01"
    
    # 자동 조회를 위한 로직
    if selected_date:
        # 첫 번째 테이블 쿼리
        query1 = """
        SELECT  
        (select 
                 company_name
        from company c where c.company_id=d.company_id) as company_name,
        sales_rank,
        sales,
        market_share,
        last_month_sales,
        last_month_change,
        sales_month
        FROM domestic_company_sales d
        WHERE d.sales_month = %s
        """
        
        df1 = get_data_from_db_2(query1, (selected_date,))
        
        if not df1.empty:
            # 열 이름 수정
            df1.columns = [
                '회사명',
                '순위', 
                '판매량', 
                '점유율', 
                '전월 판매량', 
                '전월 대비 증가량',
                '판매 날짜'
            ]
            st.subheader("국내 회사 판매량 데이터")
            st.dataframe(df1)  # 첫 번째 데이터프레임을 Streamlit 데이터프레임으로 출력
        else:
            st.write("해당 월의 데이터가 없습니다.")
        
        # 두 번째 테이블 쿼리
        query2 = """
        SELECT  
        (select 
                 company_name
        from company c where c.company_id=d.company_id) as company_name,
        sales_rank,
        sales,
        market_share,
        last_month_sales,
        last_month_change,
        sales_month
        FROM international_company_sales d
        WHERE d.sales_month = %s
        """
        
        df2 = get_data_from_db_2(query2, (selected_date,))
        
        if not df2.empty:
            # 열 이름 수정 (실제 열 이름에 맞게 수정 필요)
            df2.columns = [
                '회사명',
                '순위', 
                '판매량', 
                '점유율', 
                '전월 판매량', 
                '전월 대비 증가량',
                '판매 날짜'
            ]
            
            st.subheader("해외 회사별 판매량 데이터")
            st.dataframe(df2)  # 두 번째 데이터프레임을 Streamlit 데이터프레임으로 출력
        else:
            st.write("두 번째 테이블에 대한 데이터가 없습니다.")

            # df1과 df2에서 판매량 합산
        if not df1.empty and not df2.empty:
            # 두 데이터프레임의 판매량 합산
            total_sales = pd.concat([df1[['회사명', '판매량']], df2[['회사명', '판매량']]])
            total_sales = total_sales.groupby('회사명', as_index=False).sum()
        
            # 원형 그래프 생성
            fig = px.pie(total_sales, names='회사명', values='판매량', title='회사별 전체 판매량 비율')
        
            # Streamlit에 그래프 표시
            st.plotly_chart(fig)
        else:
            st.write("판매량 데이터가 충분하지 않아 원형 그래프를 생성할 수 없습니다.")

 # 페이지에 따른 콘텐츠 렌더링
if st.session_state.page == "회사별 자동차 조회":
    st.title("회사별 자동차 조회")
    
    # company 테이블에서 모든 회사 목록을 가져옴
    query_companies = "SELECT company_name FROM company"
    companies_df = get_data_from_db(query_companies)
    
    # 회사 이름을 선택할 수 있는 selectbox
    company_name = st.selectbox("회사 이름을 선택하세요", companies_df["company_name"].unique())
    
    # 회사명을 선택한 후 해당 회사의 차량 데이터를 조회
    if company_name:  # 회사 이름이 선택되었을 때만 실행
        query = f"""
            SELECT * FROM vehicles 
            WHERE company_id = (SELECT company_id FROM company WHERE company_name = '{company_name}')
        """
        df = get_data_from_db(query)
        if not df.empty:
            display_vehicle_data(df)
        else:
            st.warning(f"{company_name}에 대한 데이터가 없습니다.")

# 차량 모델별 월별 판매량 조회 페이지
if st.session_state.page == "모델별 차량 판매량 조회":
    st.title("모델별 차량 판매량 조회")
    
    selected_model = st.session_state.get('selected_vehicle_name', '')

    # 모델명을 vehicles 테이블에서 조회
    query_model_names = "SELECT DISTINCT vehicle_name FROM vehicles"
    model_names_df = get_data_from_db(query_model_names)
    
    # 선택된 모델명을 사용해 selectbox에 기본값을 설정
    model_name = st.selectbox("모델명을 선택하세요", model_names_df["vehicle_name"].unique(), index=model_names_df["vehicle_name"].tolist().index(selected_model) if selected_model else 0)
    
    if model_name:
        # 모델명을 세션 상태에 저장
        st.session_state.selected_vehicle_name = model_name

        # 선택된 모델에 대한 vehicles 테이블에서 vehicle_id 가져오기
        vehicle_id_query = f"""
            SELECT vehicle_id FROM vehicles WHERE vehicle_name = '{model_name}'
        """
        vehicle_id_df = get_data_from_db(vehicle_id_query)

        if not vehicle_id_df.empty:
            vehicle_id = vehicle_id_df.iloc[0]['vehicle_id']

            # domestic_model_sales 테이블에서 국내 판매 데이터 가져오기
            domestic_sales_query = f"""
                SELECT d.sales_month, d.sales, d.last_month_sales, d.last_month_change, v.vehicle_img
                FROM domestic_model_sales d
                INNER JOIN vehicles v ON d.vehicle_id = v.vehicle_id
                WHERE v.vehicle_id = {vehicle_id}
                ORDER BY d.sales_month
            """
            domestic_sales_data = get_data_from_db(domestic_sales_query)

            # international_model_sales 테이블에서 해외 판매 데이터 가져오기
            international_sales_query = f"""
                SELECT i.sales_month, i.sales, i.last_month_change, v.vehicle_img
                FROM international_model_sales i
                INNER JOIN vehicles v ON i.vehicle_id = v.vehicle_id
                WHERE v.vehicle_id = {vehicle_id}
                ORDER BY i.sales_month
            """
            international_sales_data = get_data_from_db(international_sales_query)

            if not domestic_sales_data.empty:
                st.image(domestic_sales_data["vehicle_img"].iloc[0], width=200)
            elif not international_sales_data.empty:
                st.image(international_sales_data["vehicle_img"].iloc[0], width=200)

            # 국내 판매 데이터가 있을 경우 출력
            if not domestic_sales_data.empty:
                st.subheader(f"{model_name}의 월별 판매량 데이터")
                domestic_data_without_img = domestic_sales_data.drop(columns=["vehicle_img"])
                st.dataframe(domestic_data_without_img)

                # 국내 모델 판매량 그래프
                st.subheader(f"{model_name}의 월별 판매량 그래프")
                domestic_sales_data['sales'] = pd.to_numeric(domestic_sales_data['sales'])
                domestic_sales_data.set_index('sales_month', inplace=True)
                st.line_chart(domestic_sales_data['sales'])

            # 해외 판매 데이터가 있을 경우 출력
            if not international_sales_data.empty:
                
                st.subheader(f"{model_name}의 월별 판매량 데이터")
                international_data_without_img = international_sales_data.drop(columns=["vehicle_img"])
                st.dataframe(international_data_without_img)

                # 해외 모델 판매량 그래프
                st.subheader(f"{model_name}의 월별 판매량 그래프")
                international_sales_data['sales'] = pd.to_numeric(international_sales_data['sales'])
                international_sales_data.set_index('sales_month', inplace=True)
                st.line_chart(international_sales_data['sales'])

        else:
            st.warning(f"{model_name}에 대한 차량 정보가 없습니다.")



if st.session_state.page == "자동차 회사 FAQ":
    st.title('자동차 회사 FAQ')
    
    # 테이블 목록을 가나다 순서로 정렬
    table_names = ['제네시스', '기아', '현대']
    table_names_sorted = sorted(table_names[0:])  # '선택'을 제외한 나머지 항목을 가나다 순으로 정렬

    table_map = {
        '제네시스': 'genesis',
        '기아': 'kia',
        '현대': 'hyundai'
    }

    # 사용자가 선택할 수 있는 첫 번째 콤보박스
    selected_table_display = st.selectbox('회사를 선택해 주세요.', table_names_sorted)
    
    # 선택된 테이블을 실제 테이블 이름으로 매핑
    selected_table = table_map.get(selected_table_display, None)
    
    # if selected_table_display == '선택':
    #     # 첫 화면에서 '테이블을 선택해 주세요.' 문구를 제거
    #     st.write('');  # 빈 줄 추가로 구분
    #     return

    # if selected_table is None:
    #     st.write('Error: Table name is not recognized.')
    #     return

    # 선택된 테이블에서 FAQ를 가져옴
    faqs = get_faq_for_table(selected_table)
    
    if faqs:
        search_term = st.text_input("키워드를 검색해 주세요.")
        
        # 검색어에 따라 FAQ 필터링
        filtered_faqs = [item for item in faqs if search_term.lower() in item.get('question', '').lower()]

        if filtered_faqs:
            # 페이지네이션 설정
            items_per_page = 5
            total_pages = math.ceil(len(filtered_faqs) / items_per_page)
            page_number = st.slider("페이지", 1, total_pages, 1)

            # 현재 페이지에 해당하는 FAQ 항목을 가져옴
            start_index = (page_number - 1) * items_per_page
            end_index = start_index + items_per_page
            page_faqs = filtered_faqs[start_index:end_index]

            for item in page_faqs:
                question = item.get('question')
                answer = item.get('answer')

                # 아코디언 형태로 질문을 클릭하면 답변이 보임
                with st.expander(question):
                    st.write(answer)
        else:
            st.write('검색 결과에 맞는 FAQ가 없습니다.')
    else:
        st.write('이 테이블에 대한 FAQ가 없습니다.')