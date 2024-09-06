import streamlit as st
import mysql.connector
import math

# MySQL 데이터베이스에서 FAQ를 가져오는 함수
def get_faq_for_table(table_name):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='faq'
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

# Streamlit 애플리케이션
def main():
    st.title('자동차 회사 FAQ')

    # 테이블 목록을 가나다 순서로 정렬
    table_names = ['선택', '제네시스', '기아', '현대']
    table_names_sorted = sorted(table_names[1:])  # '선택'을 제외한 나머지 항목을 가나다 순으로 정렬
    table_names_sorted.insert(0, '선택')  # '선택'을 첫 번째 항목으로 추가

    table_map = {
        '제네시스': 'genesis',
        '기아': 'kia',
        '현대': 'hyundai'
    }

    # 사용자가 선택할 수 있는 첫 번째 콤보박스
    selected_table_display = st.selectbox('회사를 선택해 주세요.', table_names_sorted)
    
    # 선택된 테이블을 실제 테이블 이름으로 매핑
    selected_table = table_map.get(selected_table_display, None)
    
    if selected_table_display == '선택':
        # 첫 화면에서 '테이블을 선택해 주세요.' 문구를 제거
        st.write('');  # 빈 줄 추가로 구분
        return

    if selected_table is None:
        st.write('Error: Table name is not recognized.')
        return

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

if __name__ == "__main__":
    main()