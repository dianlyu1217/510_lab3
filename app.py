import streamlit as st

# 模拟数据库存储
prompts_db = []

def create_prompt(title, content):
    prompt_id = len(prompts_db) + 1
    prompts_db.append({"id": prompt_id, "title": title, "content": content, "favorite": False})

def get_prompts():
    return prompts_db

def get_prompt(prompt_id):
    for prompt in prompts_db:
        if prompt["id"] == prompt_id:
            return prompt

def update_prompt(prompt_id, title, content, favorite):
    for prompt in prompts_db:
        if prompt["id"] == prompt_id:
            prompt["title"] = title
            prompt["content"] = content
            prompt["favorite"] = favorite
            return

def delete_prompt(prompt_id):
    global prompts_db
    prompts_db = [prompt for prompt in prompts_db if prompt["id"] != prompt_id]

def toggle_favorite(prompt_id):
    for prompt in prompts_db:
        if prompt["id"] == prompt_id:
            prompt["favorite"] = not prompt["favorite"]
            return

# Streamlit UI
st.title('Prompt Manager')

# 创建提示部分
with st.form("create_prompt"):
    st.write("Create a new prompt")
    title = st.text_input("Title")
    content = st.text_area("Content")
    submitted = st.form_submit_button("Submit")
    if submitted:
        create_prompt(title, content)

# 显示所有提示
st.subheader("All Prompts")
for prompt in get_prompts():
    st.write(f"ID: {prompt['id']}, Title: {prompt['title']}, Favorite: {'Yes' if prompt['favorite'] else 'No'}")
    st.write(f"Content: {prompt['content']}")
    if st.button(f"Delete {prompt['id']}", key=f"delete_{prompt['id']}"):
        delete_prompt(prompt['id'])
    if st.button(f"Toggle Favorite {prompt['id']}", key=f"fav_{prompt['id']}"):
        toggle_favorite(prompt['id'])

# 重新加载页面以反映数据更改
if st.button("Refresh"):
    st.experimental_rerun()
