import streamlit as st
from datetime import datetime
import csv
import io

# 페이지 기본 설정
st.set_page_config(
    page_title="Lab Assistant: Cell & Drug Calculator",
    page_icon="🧪",
    layout="wide"
)

# 세션 상태 초기화
if "culture_log" not in st.session_state:
    st.session_state.culture_log = []

if "counting_log" not in st.session_state:
    st.session_state.counting_log = []

st.title("🧪 Lab Assistant: 세포 배양 & 약물 계산기")
st.caption("세포주 배양 관리 · Duplicate Counting 기록 & 필요 세포 계산 · 약물 희석 계산")

# 3개 탭 구성
tab1, tab2, tab3 = st.tabs([
    "📋 세포주 배양 관리",
    "🔢 Counting 기록 & 세포수 계산",
    "💊 약물 농도 & 희석 계산"
])

# ==============================================================================
# TAB 1: 세포주 배양 관리
# ==============================================================================
with tab1:
    st.subheader("📋 세포주 배양 이력 관리")

    with st.expander("➕ 새 배양 기록 추가하기", expanded=True):
        with st.form("culture_log_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            cell_line_options = ["Hs578T", "AGS", "SNU601", "HPAF-2", "HT-29", "JIMT-1", "B16F10", "직접 입력"]
            selected_cell = c1.selectbox("세포주 선택", cell_line_options)
            if selected_cell == "직접 입력":
                m_cell = c1.text_input("직접 입력 세포주명", placeholder="예: RAW 264.7")
            else:
                m_cell = selected_cell
                
            m_pass = c2.text_input("Passage", value="P12")
            m_date = c3.text_input("날짜", value=datetime.now().strftime("%Y-%m-%d"))
            
            c4, c5 = st.columns(2)
            m_media = c4.text_input("배지 조건", value="DMEM + 10% FBS + 1% AA")
            m_cultured_cells = c5.text_input("배양 세포수", placeholder="예: 1.0 × 10⁶ cells / 100mm dish")
            
            m_note = st.text_input("비고", placeholder="특이사항, 컨플루언시, 계대배양 비율 등")
            
            submitted = st.form_submit_button("배양 기록 추가", type="primary")
            if submitted and m_cell:
                new_entry = {
                    "날짜": m_date,
                    "세포주": m_cell,
                    "Passage": m_pass,
                    "배지 조건": m_media,
                    "배양 세포수": m_cultured_cells,
                    "비고": m_note
                }
                st.session_state.culture_log.insert(0, new_entry)
                st.success("✅ 배양 기록이 저장되었습니다!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📄 저장된 배양 기록")
    
    if st.session_state.culture_log:
        for idx, item in enumerate(st.session_state.culture_log):
            with st.container(border=True):
                h1, h2, h3 = st.columns([2, 2, 1])
                h1.markdown(f"**🧬 세포주:** {item['세포주']}")
                h2.markdown(f"**Passage:** {item['Passage']}")
                h3.markdown(f"**날짜:** {item['날짜']}")
                
                b1, b2 = st.columns(2)
                b1.text(f"배지 조건: {item['배지 조건']}")
                b2.text(f"배양 세포수: {item['배양 세포수']}")
                if item['비고']:
                    st.text(f"비고: {item['비고']}")
                
                if st.button("🗑️ 삭제", key=f"del_cult_{idx}"):
                    st.session_state.culture_log.pop(idx)
                    st.rerun()

        output1 = io.StringIO()
        writer1 = csv.DictWriter(output1, fieldnames=st.session_state.culture_log[0].keys())
        writer1.writeheader()
        writer1.writerows(st.session_state.culture_log)
        
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            st.download_button(
                label="📥 배양 기록 CSV 다운로드",
                data=output1.getvalue().encode("utf-8-sig"),
                file_name=f"cell_culture_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with col_btn2:
            if st.button("🗑️ 배양 기록 전체 초기화"):
                st.session_state.culture_log = []
                st.rerun()
    else:
        st.info("등록된 배양 기록이 없습니다.")


# ==============================================================================
# TAB 2: Counting 기록지 (세로형 Duplicate 구조) & 필요 세포 수 계산기
# ==============================================================================
with tab2:
    st.subheader("1. Counting 결과 기록지 (Duplicate 순차 입력)")
    with st.expander("➕ Counting 결과 기록하기", expanded=True):
        with st.form("counting_log_form", clear_on_submit=True):
            fc1, fc2, fc3 = st.columns(3)
            cnt_date = fc1.text_input("날짜", value=datetime.now().strftime("%Y-%m-%d"))
            cnt_cell = fc2.selectbox("세포주", ["Hs578T", "AGS", "SNU601", "HPAF-2", "HT-29", "JIMT-1", "B16F10", "기타"], key="cnt_cell_box")
            cnt_pass = fc3.text_input("Passage", value="P12", key="cnt_pass_box")
            
            st.markdown("---")
            
            # 1회차 입력 영역 (위쪽)
            st.markdown("🔹 **1회차 측정 (Count #1 & Viability #1)**")
            dc1, dc2 = st.columns(2)
            c1_val = dc1.number_input("Count #1 (×10⁶ cells/mL)", min_value=0.0, value=2.50, step=0.01, format="%.2f")
            v1_val = dc2.number_input("Viability #1 (%)", min_value=0.0, max_value=100.0, value=95.0, step=0.1, format="%.1f")
            
            st.markdown("")
            
            # 2회차 입력 영역 (아래쪽)
            st.markdown("🔹 **2회차 측정 (Count #2 & Viability #2)** *(※ 1회만 측정한 경우 0으로 두세요)*")
            dc3, dc4 = st.columns(2)
            c2_val = dc3.number_input("Count #2 (×10⁶ cells/mL)", min_value=0.0, value=2.60, step=0.01, format="%.2f")
            v2_val = dc4.number_input("Viability #2 (%)", min_value=0.0, max_value=100.0, value=96.0, step=0.1, format="%.1f")

            st.markdown("---")
            cnt_note = st.text_input("비고", placeholder="예: 1:1 Trypan blue 희석")
            
            if st.form_submit_button("Counting 기록 저장", type="primary"):
                # 평균 계산 로직 (2회차 값이 0이면 1회차 값만 사용)
                if c2_val > 0:
                    avg_c = (c1_val + c2_val) / 2.0
                    cnt_conc_str = f"{avg_c:.2f} × 10⁶ cells/mL (#1: {c1_val}, #2: {c2_val})"
                else:
                    avg_c = c1_val
                    cnt_conc_str = f"{avg_c:.2f} × 10⁶ cells/mL"

                if v2_val > 0:
                    avg_v = (v1_val + v2_val) / 2.0
                    cnt_viab_str = f"{avg_v:.1f}% (#1: {v1_val}%, #2: {v2_val}%)"
                else:
                    avg_v = v1_val
                    cnt_viab_str = f"{avg_v:.1f}%"

                cnt_entry = {
                    "날짜": cnt_date,
                    "세포주": cnt_cell,
                    "Passage": cnt_pass,
                    "평균 세포 농도": cnt_conc_str,
                    "평균 생존율": cnt_viab_str,
                    "비고": cnt_note
                }
                st.session_state.counting_log.insert(0, cnt_entry)
                st.success(f"✅ Counting 기록 저장 완료! (평균 농도: {avg_c:.2f} × 10⁶ cells/mL, 평균 생존율: {avg_v:.1f}%)")
                st.rerun()

    if st.session_state.counting_log:
        st.markdown("### 📄 저장된 Counting 목록")
        for idx, item in enumerate(st.session_state.counting_log):
            with st.container(border=True):
                ch1, ch2, ch3 = st.columns([2, 2, 1])
                ch1.markdown(f"**🧬 세포주:** {item['세포주']} ({item['Passage']})")
                ch2.markdown(f"**평균 농도:** {item['평균 세포 농도']}")
                ch3.markdown(f"**날짜:** {item['날짜']}")
                
                cb1, cb2 = st.columns(2)
                cb1.text(f"평균 생존율: {item['평균 생존율']}")
                if item['비고']:
                    cb2.text(f"비고: {item['비고']}")
                
                if st.button("🗑️ 삭제", key=f"del_cnt_{idx}"):
                    st.session_state.counting_log.pop(idx)
                    st.rerun()

        output2 = io.StringIO()
        writer2 = csv.DictWriter(output2, fieldnames=st.session_state.counting_log[0].keys())
        writer2.writeheader()
        writer2.writerows(st.session_state.counting_log)
        
        st.markdown("---")
        cbtn1, cbtn2 = st.columns([1, 4])
        with cbtn1:
            st.download_button(
                label="📥 Counting 기록 CSV 다운로드",
                data=output2.getvalue().encode("utf-8-sig"),
                file_name=f"cell_counting_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with cbtn2:
            if st.button("🗑️ Counting 기록 전체 초기화"):
                st.session_state.counting_log = []
                st.rerun()

    st.markdown("---")
    
    st.subheader("2. 필요 세포 수 & Medium 계산기")
    st.caption("측정된 평균 세포 농도와 Well당 분주 부피를 입력하면 필요한 세포 현탁액 및 배지(Medium) 부피를 계산합니다.")
    
    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        measured_conc_val = st.number_input("측정된 세포 농도 (평균, × 10⁶ cells/mL)", min_value=0.01, value=1.50, step=0.1, format="%.2f")
        vol_per_well_ml = st.number_input("Seeding에 필요한 Well당 부피 (Medium 량, mL)", min_value=0.05, value=1.0, step=0.1, format="%.2f")
    with calc_c2:
        cells_per_unit = st.number_input("Well당 필요한 세포 수 (cells/well)", min_value=100, value=100000, step=10000)
        num_units = st.number_input("필요한 Well 개수 (개)", min_value=1, value=10, step=1)

    # 계산 로직
    conc_cells_per_ml = measured_conc_val * 1e6
    needed_total_cells = cells_per_unit * num_units
    needed_susp_vol_ml = (needed_total_cells / conc_cells_per_ml) if conc_cells_per_ml > 0 else 0
    total_medium_vol_ml = vol_per_well_ml * num_units
    fresh_medium_vol_ml = total_medium_vol_ml - needed_susp_vol_ml

    st.markdown("#### 📊 계산 결과")
    rm1, rm2, rm3, rm4 = st.columns(4)
    rm1.metric("필요한 총 세포 수", f"{needed_total_cells/1e6:.2f} × 10⁶ cells", f"{needed_total_cells:,.0f} cells")
    rm2.metric("취해야 할 세포 현탁액", f"{needed_susp_vol_ml * 1000:,.1f} μL", f"{needed_susp_vol_ml:.3f} mL")
    rm3.metric("총 부피 (총 Medium 량)", f"{total_medium_vol_ml:,.2f} mL", f"{total_medium_vol_ml * 1000:,.0f} μL")
    
    if fresh_medium_vol_ml >= 0:
        rm4.metric("추가할 새 Medium 부피", f"{fresh_medium_vol_ml:,.2f} mL", f"{fresh_medium_vol_ml * 1000:,.1f} μL")
    else:
        rm4.error("⚠️ 세포 농도가 낮아 현탁액 부피가 총 부피를 초과합니다. 원심분리 후 농축하세요.")


# ==============================================================================
# TAB 3: 약물 농도 & 희석 계산
# ==============================================================================
with tab3:
    st.subheader("1. 스톡 용액 희석 계산 (C1V1 = C2V2)")
    
    unit_map = {"M": 1.0, "mM": 1e-3, "μM": 1e-6, "nM": 1e-9}
    
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        c1_val = st.number_input("Stock 농도 (C1)", min_value=0.0001, value=10.0, format="%.4f")
        c1_unit = st.selectbox("C1 단위", list(unit_map.keys()), index=1, key="c1_u")
    with d_col2:
        c2_val = st.number_input("목표 최종 농도 (C2)", min_value
