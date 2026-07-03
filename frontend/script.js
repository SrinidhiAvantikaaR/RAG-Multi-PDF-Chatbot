const chatBox = document.getElementById("chatBox");

let history = [];

function addMessage(text, cls){

    const div = document.createElement("div");

    div.className = "message " + cls;

    div.innerHTML = `<span>${text}</span>`;

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById("uploadBtn").onclick = async ()=>{

    const files = document.getElementById("pdfFiles").files;

    if(files.length===0){
        alert("Select PDFs");
        return;
    }

    const formData = new FormData();

    for(let f of files)
        formData.append("files",f);

    document.getElementById("status").innerHTML="Uploading...";

    const res = await fetch("http://localhost:8000/upload",{
        method:"POST",
        body:formData
    });

    const data = await res.json();

    document.getElementById("status").innerHTML=data.message;
};

document.getElementById("sendBtn").onclick = async ()=>{

    const question = document.getElementById("question").value;

    if(question==="") return;

    addMessage(question,"user");

    document.getElementById("question").value="";

    const res = await fetch("http://localhost:8000/chat",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            question:question,

            history:history

        })

    });

    const data = await res.json();

    addMessage(data.answer.answer,"bot");

    history.push({
        user:question,
        assistant:data.answer.answer
    });

};