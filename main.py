import streamlit as st
import pandas as pd


def dynamic_input_data_editor(data, key, **_kwargs):
    """
    Like streamlit's data_editor but which allows you to initialize the data editor with input arguments that can
    change between consecutive runs. Fixes the problem described here: https://discuss.streamlit.io/t/data-editor-not-changing-cell-the-1st-time-but-only-after-the-second-time/64894/13?u=ranyahalom
    :param data: The `data` argument you normally pass to `st.data_editor()`.
    :param key: The `key` argument you normally pass to `st.data_editor()`.
    :param _kwargs: All other named arguments you normally pass to `st.data_editor()`.
    :return: Same result returned by calling `st.data_editor()`
    """
    changed_key = f'{key}_khkhkkhkkhkhkihsdhsaskskhhfgiolwmxkahs'
    initial_data_key = f'{key}_khkhkkhkkhkhkihsdhsaskskhhfgiolwmxkahs__initial_data'

    def on_data_editor_changed():
        if 'on_change' in _kwargs:
            args = _kwargs['args'] if 'args' in _kwargs else ()
            kwargs = _kwargs['kwargs'] if 'kwargs' in _kwargs else  {}
            _kwargs['on_change'](*args, **kwargs)
        st.session_state[changed_key] = True

    if changed_key in st.session_state and st.session_state[changed_key]:
        data = st.session_state[initial_data_key]
        st.session_state[changed_key] = False
    else:
        st.session_state[initial_data_key] = data
    __kwargs = _kwargs.copy()
    __kwargs.update({'data': data, 'key': key, 'on_change': on_data_editor_changed})
    return st.data_editor(**__kwargs)





st.set_page_config(page_title="Editable CSV Table", layout="wide")
st.title("CSV Viewer & Editor")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file:
    if "main_df" not in st.session_state:
        st.session_state.main_df = pd.read_csv(uploaded_file, dtype={'postal_code': 'str'})

    df = st.session_state.main_df

    # Fixed editable columns
    editable_cols = [
        "is_recruiter",
        "show_in_salary_analysis_graphic",
        "show_in_competitive_analysis_graphic"
    ]

    # Optional display columns
    display_options = [
        "company_name", "job_title", "postal_code",
        "place", "rating", "review_count"
    ]

    selected_display_cols = st.multiselect(
        "Select columns to display:",
        options=display_options,
        default=["company_name", "job_title","rating"]
    )

    # Full list of columns to show
    columns_to_show = selected_display_cols + editable_cols

    # Pagination
    page_size = 20
    total_rows = len(st.session_state.main_df)
    total_pages = (total_rows - 1) // page_size + 1
    page = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)

    start = (page - 1) * page_size
    end = min(start + page_size, total_rows)
    df_page = st.session_state.main_df.loc[start:end - 1, columns_to_show].copy()

    # Set column configs for editable checkboxes
    column_config = {
        col: st.column_config.CheckboxColumn(label=col.replace("_", " ").title())
        for col in editable_cols
    }

    st.write("### Editable Table:")
    # edited_df = st.data_editor(
    #     df_page,
    #     column_config=column_config,
    #     disabled=[col for col in selected_display_cols],
    #     use_container_width=True,
    #     hide_index=True,
    #     key=f"editor-page-{page}"
    # )
    
    edited_df = dynamic_input_data_editor(
        df_page,
        column_config=column_config,
        disabled=[col for col in selected_display_cols],
        use_container_width=True,
        hide_index=True,
        key=f"editor-page-{page}"
    )
    # Update main DataFrame with changes from edited page
    st.session_state.main_df.loc[start:end - 1, editable_cols] = edited_df[editable_cols].values
    print(edited_df)
    # Download full updated CSV
    if st.button("Download Updated CSV"):
        csv = st.session_state.main_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "updated_data.csv", "text/csv")
else:
    st.info("Please upload a CSV file.")
