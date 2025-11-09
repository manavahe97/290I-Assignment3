from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse
from typing import Dict, List
import heapq
import json

app = FastAPI()

app.state.graph = None

@app.post("/upload_graph_json")
async def create_upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".json"):
        return {"Upload Error": "Invalid file type"}
    try:
        raw = await file.read()
        data = json.loads(raw.decode("utf-8"))
        app.state.graph = data
        return {"Upload Success": file.filename}
    except Exception as e:
        return {"Upload Error": str(e)}

@app.get("/solve_shortest_path/")
def get_shortest_path(starting_node_id: str, end_node_id: str):
    if app.state.graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    graph = app.state.graph
    if starting_node_id not in graph or end_node_id not in graph:
        return {"Solver Error": "Invalid start or end node ID."}

    dist = {node: float("inf") for node in graph}
    prev = {node: None for node in graph}
    dist[starting_node_id] = 0
    pq = [(0, starting_node_id)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == end_node_id:
            break
        for neighbor, weight in graph[u].items():
            nd = d + weight
            if nd < dist[neighbor]:
                dist[neighbor] = nd
                prev[neighbor] = u
                heapq.heappush(pq, (nd, neighbor))

    if dist[end_node_id] == float("inf"):
        return {"shortest_path": None, "total_distance": None}

    path = []
    cur = end_node_id
    while cur:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return {"shortest_path": path, "total_distance": dist[end_node_id]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
