import streamlit as st
import streamlit.components.v1 as components
from streamlit_server_state import server_state, server_state_lock
import urllib.parse        
oparams = st.experimental_get_query_params()
params = {
    x: oparams[x][0]  for x in oparams
}

if 'nickkey' not in st.session_state:
    q= st.experimental_get_query_params()
    if "nickname" in q:
        nickname = q["nickname"][0]
    else:
        nickname = st.text_input("Nick name", key="nickname")
        
    if nickname:
        st.session_state['nickkey'] = nickname

def get_nick_name():
    if 'nickkey' in st.session_state:
        return st.session_state['nickkey']
    else:
        st.stop()

    
new_messages = []
q= st.experimental_get_query_params()
if "messages" in q:
    for item in q["messages"]:
        new1 = urllib.parse.unquote(item)
        new_messages.append(new1)

seen = {}

for m in new_messages:    
    st.write("m", m )
    #chk = st.checkbox(f"include {text}",key=str("_i_"+str(i)))
    i = str(id(m))
    key=str("_a_"+str(i))

    if key not in seen:
        chk = st.checkbox(f"approve {m}",key=str("_a_"+str(i)),value=True)
        text = st.text_input("approve", key=str("_u_"+str(i)),value=m)
        seen[key]=1

    # number_input("Include" +m,
    #              min_value=0, max_value=10, value=1,
    #              step=1,
    #              #format=None,
    #              key="count"+m,
    #              help=f"How may times to include {m}",
    #              #on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible"
    #              )

        

def on_clear():
    st.write("clearing")
    
    with server_state_lock["chat_messages"]:
        if "chat_messages" in server_state:
            da = server_state["chat_messages"]
            st.write("Messages")        
            st.code(da)        
        server_state["chat_messages"]=[]
    
clear_args = st.button("clear url args")
if clear_args:
    st.experimental_set_query_params()

st.button("clear messages for all users",on_click=on_clear)

imports = st.button(f"Approve selected messages (if any)")
if imports:
    messages= []
    st.write("going to import")
    with server_state_lock["chat_messages"]:
        for x in st.session_state:
            v = st.session_state[x]
            if x.startswith("_a_"):
                value_name = "_u_"+x[3:]
                if value_name in st.session_state:
                    v2 = st.session_state[value_name]
                    if v == True:
                        new_message_packet = { "src":"import",  "nickname": get_nick_name(), "text": v2}
                        server_state["chat_messages"] = server_state["chat_messages"] + [new_message_packet]
                        st.write("added",new_message_packet)

def on_message_input():
    new_message_text = st.session_state["message_input"]
    if not new_message_text:
        return

    new_message_packet = {
        "src":"input",
        "nickname": get_nick_name(),
        "text": new_message_text,
    }
    
    #if new_message_text.startswith("/delete-all"):
    #    print(server_state["chat_messages"])
    #    server_state["chat_messages"]=[]
    
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
            if x not in ("nickname","messages"):
                urls.append( {
                    "src":"url",
                    "field":x,
                    "nickname": get_nick_name(),
                    "text": k})
    server_state["chat_messages"].extend(urls)           

st.text_input("Message", key="message_input", on_change=on_message_input)

#st.write(server_state["chat_messages"])

for i,message in enumerate(server_state["chat_messages"]):
    st.write("MESSAGE",message)

    if "text" in message:
        text = message["text"]
        if text.startswith("https://") or text.startswith("http://"):
            frame = components.iframe(text,
                                      width=st.number_input(
                                          "width",
                                          key="width"+str(id(text)),
                                          min_value=200, value=700),
                                      height=st.number_input(
                                          "height",
                                          key="height"+str(id(text)),
                                          min_value=200, value=2000)
                                      )

        i = str(id(text))
        chk = st.checkbox(f"include {text}",key=str("_i_"+str(i)))
        text = st.text_input("include", key=str("_t_"+str(i)),value=text)
    # now make a share link
base_url = st.text_input("base_url", key="base-url", value=params.get("base-url",""), help="for the target")
share = st.button(f"share selected")
if share:
    messages= []
    st.write("going to share")
    for x in st.session_state:
        v = st.session_state[x]
        
        if x.startswith("_i_"):
            value_name = "_t_"+x[3:]
            #st.write("DEBUG!A",x,value_name)
            if value_name in st.session_state:

                v2 = st.session_state[value_name]

                if v == True:
                    #st.write("DEBUGA",x,value_name, v2, v)
                    messages.append(v2)
                    #{ "DEBUG1" :{ x : v2    }}
                    
            else:
                #st.write("DEBUG2",x,value_name)
                for x in st.session_state:
                    [x,value_name]

        else:
            #st.write("DEBUG4",x,v)
            pass
    q= st.experimental_get_query_params()
    q.update(dict(messages=messages))
    q.update(dict(nickname=get_nick_name()))
    encoded_query = urllib.parse.urlencode(q, doseq=True)
    st.markdown(f"* share [input_link {encoded_query}]({base_url}/?{encoded_query})")
