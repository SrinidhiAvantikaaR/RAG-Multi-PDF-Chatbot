const chatBox = document.getElementById("chatBox");

let history = [];

function addMessage(text, cls, sources = []) {

    const div = document.createElement("div");

    div.className = "message " + cls;

    let html = `<div class="bubble">${text}</div>`;

    if (sources.length > 0) {

        html += `<div class="source"><b>Sources:</b><br>`;

        sources.forEach(s => {

            html += `${s.file} | Page ${s.page} | Chunk ${s.chunk}<br>`;

        });

        html += "</div>";
    }

    div.innerHTML = html;

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;
}


// ---------------- Upload PDFs ----------------

document.getElementById("uploadBtn").onclick = async () => {

    const files = document.getElementById("pdfFiles").files;

    if (files.length === 0) {

        alert("Select at least one PDF.");

        return;
    }

    const formData = new FormData();

    for (let file of files) {

        formData.append("files", file);

    }

    document.getElementById("status").innerHTML = "Uploading PDFs...";

    try {

        const response = await fetch("http://127.0.0.1:8000/upload", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        document.getElementById("status").innerHTML = data.message;

    }

    catch (err) {

        document.getElementById("status").innerHTML = "Upload Failed.";

    }

};


// ---------------- Chat ----------------

async function sendMessage() {

    const input = document.getElementById("question");

    const question = input.value.trim();

    if (question === "") return;

    addMessage(question, "user");

    input.value = "";

    addMessage("Thinking...", "bot");

    try {

        const response = await fetch("http://127.0.0.1:8000/chat", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                question: question,

                history: history

            })

        });

        const data = await response.json();

        chatBox.removeChild(chatBox.lastChild);

        addMessage(

            data.answer,

            "bot",

            data.sources

        );

        history.push({

            user: question,

            assistant: data.answer

        });

    }

    catch (err) {

        chatBox.removeChild(chatBox.lastChild);

        addMessage("Server Error!", "bot");

    }

}

document.getElementById("sendBtn").onclick = sendMessage;

document.getElementById("question").addEventListener("keypress", function (e) {

    if (e.key === "Enter") {

        sendMessage();

    }

});