# fastapi‑rag‑backend
基于FastAPI实现的RAG知识库问答后端接口服务，接收HTTP POST请求，完成文档召回与大模型问答，返回JSON结果。

## 技术栈
Python、FastAPI、Uvicorn、Qdrant、Ollama

## 安装依赖
```bash
pip install -r requirements.txt
启动服务
uvicorn rag_api:app --reload
服务默认地址：http://127.0.0.1:8000
接口文档：http://127.0.0.1:8000/docs

接口示例

POST /rag/chat

请求curl示例：
curl -X 'POST' \
  'http://127.0.0.1:8000/rag/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query":"PID控制器有哪几个环节",
  "top_k":2
}'
响应示例（status:200）
{
  "code":0,
  "query":"PID控制器有哪几个环节",
  "retrieve_docs":[],
  "answer":"PID控制器包含三个环节：比例环节（P）、积分环节（I）、微分环节（D）。每个环节都有特定的作用，比如比例环节用于快速响应偏差，积分环节消除静态误差，微分用来抑制震荡。"
}
功能说明

1. POST接口接收用户问题与top‑k参数

2. Qdrant向量库完成知识库文档Top‑K召回

3. Ollama本地大模型生成回答

4. 返回json格式问题、检索文档、最终答案
操作：
1. 编辑器里全部旧文字删掉
2. 把上面整段粘贴进去
3. 滑到底点绿色 Commit changes
4. 点Preview预览看效果，排版正常就完事。
