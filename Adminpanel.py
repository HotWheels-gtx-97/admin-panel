import streamlit as st
import json
import base64
import requests
import datetime

# 🔐 CONFIG (IMPORTANT: Fix your repo URL)
TOKEN = st.secrets["TOKEN"]
USERNAME = "HotWheels-gtx-97"
REPO = "Shop"
FILE_PATH = "products.json"

CATEGORIES = ["bestseller", "mostwanted", "limited", "newarrival", "rare", "giftset"]
AVAILABILITY = ["in-stock", "low-stock", "sold-out"]


# ---------------- LOAD DATA ----------------
def load_data():
    try:
        url = f"https://api.github.com/repos/HotWheels-gtx-97/Shop/contents/products.json"
        headers = {"Authorization": f"token {TOKEN}"}

        res = requests.get(url, headers=headers)
        data = res.json()

        content = base64.b64decode(data["content"]).decode()
        json_data = json.loads(content)

        return json_data.get("products", []), data["sha"]

    except Exception as e:
        st.error(f"Load failed: {e}")
        return [], None


# ---------------- PUSH DATA ----------------
def push_data(products, sha):
    try:
        url = f"https://api.github.com/repos/HotWheels-gtx-97/Shop/contents/products.json"
        headers = {"Authorization": f"token {TOKEN}"}

        new_json = json.dumps({"products": products}, indent=4)
        encoded = base64.b64encode(new_json.encode()).decode()

        payload = {
            "message": f"Admin Sync {datetime.datetime.now()}",
            "content": encoded,
            "sha": sha
        }

        res = requests.put(url, headers=headers, json=payload)
        return res.status_code in [200, 201]

    except Exception as e:
        st.error(f"Push failed: {e}")
        return False


# ---------------- SESSION ----------------
if "data" not in st.session_state:
    st.session_state.data, st.session_state.sha = load_data()
    st.session_state.unsaved = False
    st.session_state.selected = None


# ---------------- UI ----------------
st.title("Admin Panel")

col1, col2 = st.columns([6, 1])
with col1:
    if st.session_state.unsaved:
        st.warning("⚠️ Unsaved")
    else:
        st.success("✅ Synced")

with col2:
    if st.button("Send ▶"):
        if not st.session_state.unsaved:
            st.info("No changes to sync")
        else:
            if push_data(st.session_state.data, st.session_state.sha):
                st.session_state.unsaved = False
                st.success("Synced 🚀")
            else:
                st.error("Sync failed")


# ---------------- TABLE ----------------
st.subheader("Products")

for i, item in enumerate(st.session_state.data):
    cols = st.columns([2,1,3,3,1])
    cols[0].write(item.get("name"))
    cols[1].write(item.get("price"))
    cols[2].write(item.get("images", [""])[0])
    cols[3].write(item.get("description"))
    if cols[4].button("Select", key=f"sel{i}"):
        st.session_state.selected = i


# ---------------- FORM ----------------
st.subheader("Edit Product")

selected = st.session_state.selected

def get_val(key, default=""):
    if selected is not None:
        return st.session_state.data[selected].get(key, default)
    return default

name = st.text_input("Name", get_val("name"))
price = st.text_input("Price", str(get_val("price")))
category = st.selectbox("Category", CATEGORIES)
availability = st.selectbox("Availability", AVAILABILITY)
img = st.text_input("Image URL", get_val("images", [""])[0] if selected is not None else "")
info = st.text_input("Info", get_val("description"))


# ---------------- BUTTONS ----------------
colA, colB, colC, colD, colE, colF = st.columns(6)

# NEW
if colA.button("New"):
    st.session_state.selected = None

# ADD
if colB.button("Add"):
    item = {
        "id": max([i.get("id", 0) for i in st.session_state.data], default=0) + 1,
        "name": name,
        "price": int(price) if price.isdigit() else 0,
        "category": category,
        "availability": availability,
        "images": [img],
        "description": info
    }
    st.session_state.data.insert(0, item)
    st.session_state.unsaved = True

# UPDATE
if colC.button("Update") and selected is not None:
    st.session_state.data[selected].update({
        "name": name,
        "price": int(price) if price.isdigit() else 0,
        "category": category,
        "availability": availability,
        "images": [img],
        "description": info
    })
    st.session_state.unsaved = True

# DELETE
if colD.button("Delete") and selected is not None:
    st.session_state.data.pop(selected)
    st.session_state.selected = None
    st.session_state.unsaved = True

# MOVE UP
if colE.button("⬆") and selected is not None and selected > 0:
    d = st.session_state.data
    d[selected], d[selected-1] = d[selected-1], d[selected]
    st.session_state.selected -= 1
    st.session_state.unsaved = True

# MOVE DOWN
if colF.button("⬇") and selected is not None and selected < len(st.session_state.data)-1:
    d = st.session_state.data
    d[selected], d[selected+1] = d[selected+1], d[selected]
    st.session_state.selected += 1
    st.session_state.unsaved = True