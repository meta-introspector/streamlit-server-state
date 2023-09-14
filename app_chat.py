import streamlit as st
import streamlit.components.v1 as components
from streamlit_server_state import server_state, server_state_lock

    
nickname = st.text_input("Nick name", key="nickname")

q= st.experimental_get_query_params()
if "nickname" in q:
    nickname = q["nickname"][0]
    
if not nickname:
    st.stop()

def on_clear():
    st.write("clearing")
    
    with server_state_lock["chat_messages"]:
        if "chat_messages" in server_state:
            da = server_state["chat_messages"]
            st.code(da)        
        server_state["chat_messages"]=[]
    

st.button("clear",on_click=on_clear)

def on_message_input():
    new_message_text = st.session_state["message_input"]
    if not new_message_text:
        return

    new_message_packet = {
        "nickname": nickname,
        "text": new_message_text,
    }
    
    if new_message_text.startswith("/delete-all"):
        print(server_state["chat_messages"])
        server_state["chat_messages"]=[]
    
    with server_state_lock["chat_messages"]:
        server_state["chat_messages"] = server_state["chat_messages"] + [
            new_message_packet
        ]


with server_state_lock["chat_messages"]:
    if "chat_messages" not in server_state:
        server_state["chat_messages"] = []

    urls1 = st.experimental_get_query_params()
    #st.write("urls",urls1)
    urls = []
    for x in urls1:
        #st.write("item",x)
        v = urls1[x]
        for k in v:
            #st.write(k)
            urls.append( {"nickname": nickname, "text": k})
    server_state["chat_messages"].extend(urls)           

st.text_input("Message", key="message_input", on_change=on_message_input)

#st.write(server_state["chat_messages"])

for message in server_state["chat_messages"]:
    st.write(message)

    if "text" in message:
        text = message["text"]
        if text.startswith("https://"):
            frame = components.iframe(text,
                                      #key=text
                                  #, width=500, height=400
                                      )
