import numpy as np
from pydantic import BaseModel
from pathlib import Path
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastrtc import ReplyOnPause, Stream, AdditionalOutputs
from gradio.utils import get_space
import uvicorn
import gradio as gr

curr_dir = Path(__file__).parent
chatbot = gr.Chatbot(type="messages")


class Message(BaseModel):
    role: str
    content: str


class InputData(BaseModel):
    webrtc_id: str
    chatbot: list[Message]


def detection(audio: tuple[int, np.ndarray], chatbot):
    chatbot = chatbot or []
    messages = [{"role": d["role"], "content": d["content"]} for d in chatbot]
    ###
    prompt = "Hello"
    ###

    print("prompt", prompt)
    chatbot.append({"role": "user", "content": prompt})
    messages.append({"role": "user", "content": prompt})
    ###
    response_text = "Echo Hello"
    ###
    chatbot.append({"role": "assistant", "content": response_text})
    yield AdditionalOutputs(chatbot)
    yield audio


stream = Stream(
    handler=ReplyOnPause(detection, input_sample_rate=24000, output_sample_rate=24000),
    modality="audio",
    mode="send-receive",
    concurrency_limit=5 if get_space() else None,
    additional_outputs_handler=lambda a: a,
    time_limit=90 if get_space() else None,
    additional_inputs=[chatbot],
    additional_outputs=[chatbot],
)

app = FastAPI()

stream.mount(app)


@app.get("/")
async def index():
    html_content = (curr_dir / "index.html").read_text()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/input_hook")
async def _(body: InputData):
    stream.set_input(body.webrtc_id, body.model_dump()["chatbot"])
    return {"status": "ok"}


@app.get("/outputs")
def _(webrtc_id: str):
    print("outputs", webrtc_id)

    async def output_stream():
        async for output in stream.output_stream(webrtc_id):
            chatbot = output.args[0]
            yield f"event: output\ndata: {json.dumps(chatbot[-2])}\n\n"
            yield f"event: output\ndata: {json.dumps(chatbot[-1])}\n\n"

    return StreamingResponse(output_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
