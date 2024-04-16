import os
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pytz
from datetime import datetime
import pyperclip

load_dotenv()


class Prompt:
    def __init__(self, id, title, content, create_time, update_time, favorite, template):
        self.id = id
        self.title = title
        self.content = content
        self.create_time = create_time
        self.update_time = update_time
        self.favorite = favorite
        self.template = template


def con_database():
    con = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = con.cursor()
    con.commit()
    return con, cur


def prompt_form(prompt):
    with st.form(key=f"form_{prompt.id}"):
        title = st.text_input("Title", value=prompt.title, key=f"title_{prompt.id}")
        content = st.text_area("Prompt", value=prompt.content, key=f"content_{prompt.id}")
        favorite = st.checkbox("❤️", value=prompt.favorite, key=f"favorite_{prompt.id}")
        template = st.checkbox("Is Template", value=prompt.template, key=f"template_{prompt.id}")
        submit_button = st.form_submit_button("Submit")
        if submit_button:
            return Prompt(prompt.id, title, content, prompt.create_time, prompt.update_time, favorite, template)
    return None


def extract_variables(content):
    import re
    return set(re.findall(r"\{(.*?)\}", content))


def now_timestamp() -> str:
    now = datetime.now(pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M:%S%z')
    return now


def update_prompt_in_db(prompt):
    con, cur = con_database()
    cur.execute("UPDATE prompts SET title=%s, content=%s, favorite=%s, template=%s, update_time=%s WHERE id=%s",
                (prompt.title, prompt.content, prompt.favorite, prompt.template, now_timestamp(), prompt.id))
    con.commit()
    con.close()


def insert_prompt_in_db(prompt):
    con, cur = con_database()
    cur.execute(
        "INSERT INTO prompts (title, content, favorite, template, create_time, update_time) VALUES (%s, %s, %s, %s, %s, %s)",
        (prompt.title, prompt.content, prompt.favorite, prompt.template, now_timestamp(), now_timestamp())
    )
    con.commit()
    st.success("Prompt added successfully!")
    con.close()


def delete_prompt_from_db(prompt_id):
    con, cur = con_database()
    cur.execute("DELETE FROM prompts WHERE id=%s", (prompt_id,))
    con.commit()
    con.close()


def search_model():
    con, cur = con_database()

    st.header("Search Prompts")
    searchC, orderC = st.columns([5, 2])
    with searchC:
        title = st.text_input("prompt title", value="")
    with orderC:
        order = st.selectbox("order by update_time", ["DESC", "ASC"])
    query = "SELECT * FROM prompts WHERE id > 0"
    favorite = st.checkbox("Only Show ❤️")
    template = st.checkbox("Only Show Template")
    if title != "":
        query += " AND title = '" + title + "'"
    if favorite:
        query += " AND favorite = True"
    if template:
        query += " AND template = True"
    if order == "DESC":
        query += " ORDER BY update_time DESC"
    else:
        query += " ORDER BY update_time ASC"
    cur.execute(query)
    prompts = [Prompt(*row) for row in cur.fetchall()]

    st.header("Show Prompts")
    for prompt in prompts:
        edit_key = f"edit_{prompt.id}"
        show, update, delete = st.columns([5, 0.9, 0.9])
        with update:
            if st.button("Update", key=f"button_edit_{prompt.id}"):
                st.session_state[edit_key] = not st.session_state.get(edit_key, False)
        with show:
            if prompt.favorite:
                expanderTitle = "️❤️" + prompt.update_time.astimezone(pytz.timezone('America/Los_Angeles')).strftime(
                    '%Y-%m-%d %H:%M:%S') + " | " + prompt.title
            else:
                expanderTitle = "️🤍" + prompt.update_time.astimezone(pytz.timezone('America/Los_Angeles')).strftime(
                    '%Y-%m-%d %H:%M:%S') + " | " + prompt.title
            open = False
            if st.session_state.get(edit_key):
                open = True
            with st.expander(expanderTitle, expanded=open):
                st.write("ID: ", prompt.id)
                st.checkbox("Is Template", value=prompt.template, disabled=True, key=f"show_prompt_{prompt.id}")
                st.write(prompt.content)
                # Check if we should display the edit form
                if st.session_state.get(edit_key):
                    updated_prompt = prompt_form(prompt)
                    if updated_prompt:
                        update_prompt_in_db(updated_prompt)
                        st.success("Prompt updated successfully!")
                        del st.session_state[edit_key]  # Clean up state
                        st.rerun()
        with delete:
            if st.button("Delete", key=f"delete_{prompt.id}"):
                delete_prompt_from_db(prompt.id)
                st.rerun()
    con.close()


def insert_model():
    st.sidebar.header("Add Prompt")
    with st.sidebar.form(key="insert_prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value="")
        content = st.text_area("Prompt", height=200, value="")
        favorite = st.checkbox("❤️", value=False)
        template = st.checkbox("Is Template", value=False)
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not title or not content:
                st.error('Please fill in both the title and prompt fields.')
                return
            insert_prompt = Prompt(0, title, content, 0, 0, favorite, template)
            insert_prompt_in_db(insert_prompt)
            st.rerun()


def render_template_model():
    st.sidebar.header("Render Template")
    con, cur = con_database()
    cur.execute("SELECT id, title FROM prompts WHERE template = TRUE ORDER BY update_time DESC")
    templates = {row[1]: row[0] for row in cur.fetchall()}

    template_choice = st.sidebar.selectbox("Choose a template", list(templates.keys()))
    if template_choice:
        template_id = templates[template_choice]
        cur.execute("SELECT content FROM prompts WHERE id = %s", (template_id,))
        template_content = cur.fetchone()[0]
        con.close()

        variables = extract_variables(template_content)
        values = {}
        st.sidebar.write(template_content)
        for var in variables:
            values[var] = st.sidebar.text_input(f"Value for {var}:", key=var)

        if st.sidebar.button("Generate And Copy"):
            final_prompt = template_content.format(**values)
            st.sidebar.text_area("Generated Prompt", value=final_prompt, height=200)
            pyperclip.copy(final_prompt)
            st.sidebar.success("Copied to clipboard!")


if __name__ == "__main__":
    st.title("Prompt Management System")
    search_model()
    insert_model()
    render_template_model()