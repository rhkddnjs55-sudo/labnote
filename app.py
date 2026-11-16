import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lab Record & Calculator", page_icon="🧬", layout="wide")

st.title("🧬 연구실 통합 기록 및 계산 어플리케이션")

# 탭 메뉴 구성
tab1, tab2 = st.tabs(["세포주 배양 및 Counting 기록 (Cell Log)", "약물 희석 계산기 (Dilution)"])

# ----------------------------------------------------
# 탭 1: 세포주 배양 기록 + Duplicate Cell Counting 통합
# ----------------------------------------------------
with tab1:
    st.header("세포주 배양, Passage 및 Counting 기록")
    
    columns = [
        "날짜", "세포주명", "Passage", "Seeding 밀도", 
        "Count #1 (x10⁶)", "Count #2 (x10⁶)", "평균 Count (x10⁶ cells/mL)", 
        "Viability #1 (%)", "Viability #2 (%)", "평균 Viability (%)", 
        "배양액 종류", "특이사항"
    ]
    
    if "culture_data" not in st.session_state:
        st.session_state.culture_data = pd.DataFrame(columns=columns)

    with st.form("culture_form", clear_on_submit=True):
        st.subheader("1️⃣ 기본 배양 정보")
        col1, col2, col3 = st.columns(3)
        with col1:
            date_input = st.date_input("배양 일자")
            cell_name = st.selectbox("세포주 선택", ["Hs578T", "AGS", "SNU-601", "HPAF-2", "HT-29", "JIMT-1", "B16F10", "HT-1080", "H6C7", "RAW264.7", "기타"])
        with col2:
            passage_num = st.number_input("Passage 번호", min_value=1, max_value=100, value=5)
            seeding_density = st.text_input("Seeding 밀도", "1.0 x 10^5 cells/mL")
        with col3:
            media_type = st.text_input("배양액 (Media)", "RPMI-1640 + 10% FBS")
            notes = st.text_input("특이사항", "Trypsin 처리 3분")

        st.markdown("---")
        st.subheader("2️⃣ Cell Counter 측정값 (Duplicate 입력)")
        st.caption("※ 1회만 측정한 경우 #2 값을 0으로 두면 #1 값으로 자동 계산됩니다.")
        
        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        with c_col1:
            count_1 = st.number_input("Cell Count #1 (× 10⁶ cells/mL)", min_value=0.0, value=2.50, step=0.01, format="%.2f")
        with c_col2:
            count_2 = st.number_input("Cell Count #2 (× 10⁶ cells/mL)", min_value=0.0, value=2.60, step=0.01, format="%.2f")
        with c_col3:
            viab_1 = st.number_input("Viability #1 (%)", min_value=0.0, max_value=100.0, value=95.0, step=0.1, format="%.1f")
        with c_col4:
            viab_2 = st.number_input("Viability #2 (%)", min_value=0.0, max_value=100.0, value=96.0, step=0.1, format="%.1f")
        
        submitted = st.form_submit_button("기록 추가")
        if submitted:
            # Duplicate 평균 계산 (2회차 값이 0이면 1회차 단독값 처리)
            if count_2 > 0:
                avg_count = (count_1 + count_2) / 2.0
                count_2_str = f"{count_2:.2f}"
            else:
                avg_count = count_1
                count_2_str = "-"

            if viab_2 > 0:
                avg_viab = (viab_1 + viab_2) / 2.0
                viab_2_str = f"{viab_2:.1f}%"
            else:
                avg_viab = viab_1
                viab_2_str = "-"

            new_row = {
                "날짜": str(date_input),
                "세포주명": cell_name,
                "Passage": passage_num,
                "Seeding 밀도": seeding_density,
                "Count #1 (x10⁶)": f"{count_1:.2f}",
                "Count #2 (x10⁶)": count_2_str,
                "평균 Count (x10⁶ cells/mL)": f"{avg_count:.2f}",
                "Viability #1 (%)": f"{viab_1:.1f}%",
                "Viability #2 (%)": viab_2_str,
                "평균 Viability (%)": f"{avg_viab:.1f}%",
                "배양액 종류": media_type,
                "특이사항": notes
            }
            st.session_state.culture_data = pd.concat([st.session_state.culture_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"기록 완료! (평균 Cell Count: {avg_count:.2f} × 10⁶ cells/mL / 평균 생존율: {avg_viab:.1f}%)")

    st.subheader("📋 배양 기록 목록")
    
    if st.session_state.culture_data.empty:
        st.info("등록된 배양 기록이 없습니다.")
    else:
        html_table = st.session_state.culture_data.to_html(index=False, classes="dataframe")
        st.markdown(f"""
        <style>
            table.dataframe {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                margin-bottom: 10px;
                font-size: 13px;
            }}
            table.dataframe th, table.dataframe td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            table.dataframe th {{
                background-color: #f0f2f6;
                color: #31333F;
            }}
        </style>
        {html_table}
        """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if not st.session_state.culture_data.empty:
            if st.button("🗑️ 전체 기록 초기화"):
                st.session_state.culture_data = pd.DataFrame(columns=columns)
                st.rerun()
    with col_btn2:
        csv = st.session_state.culture_data.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 기록 CSV로 내보내기",
            data=csv,
            file_name="cell_culture_log.csv",
            mime="text/csv",
        )

# ----------------------------------------------------
# 탭 2: 약물 농도 및 희석 계산기
# ----------------------------------------------------
with tab2:
    st.header("약물 희석 및 Stock 계산 (C1V1 = C2V2)")
    
    calc_mode = st.radio("계산 방식 선택", ["액체 스톡 희석 (C1V1 = C2V2)", "파우더 질량 계산 (Molarity)"])
    
    if calc_mode == "액체 스톡 희석 (C1V1 = C2V2)":
        c1 = st.number_input("초기 농도 (C1, mM)", min_value=0.0, value=10.0, format="%.4f")
        c2 = st.number_input("목표 농도 (C2, mM)", min_value=0.0, value=1.0, format="%.4f")
        v2 = st.number_input("목표 부피 (V2, mL)", min_value=0.0, value=5.0, format="%.2f")
        
        if c1 > 0:
            if c2 > c1:
                st.warning("⚠️ 목표 농도(C2)가 초기 농도(C1)보다 높습니다.")
            else:
                v1 = (c2 * v2) / c1
                solvent_vol = v2 - v1
                st.success(f"📌 **필요한 Stock 용액 부피 (V1):** {v1:.4f} mL ({v1 * 1000:.2f} µL)")
                st.info(f"💧 **추가할 배양액/용매 부피:** {solvent_vol:.4f} mL ({solvent_vol * 1000:.2f} µL)")
        else:
            st.error("초기 농도(C1)는 0보다 커야 합니다.")
            
    else:
        mw = st.number_input("분자량 (Molecular Weight, g/mol)", min_value=0.0, value=300.0)
        target_molarity = st.number_input("목표 농도 (mM)", min_value=0.0, value=10.0)
        target_volume_ml = st.number_input("만들 부피 (mL)", min_value=0.0, value=10.0)
        
        mass_mg = target_molarity * (target_volume_ml / 1000.0) * mw
        st.success(f"⚖️ **필요한 파우더 질량:** {mass_mg:.4f} mg ({mass_mg * 1000:.2f} µg)")
