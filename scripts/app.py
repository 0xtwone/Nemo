from flask import Flask, request, jsonify
from flask_cors import CORS  # 新增导入
import subprocess
import time
import re  # 导入正则表达式模块
import requests  # <<-- 新增：用于在内部调用 /command

app = Flask(__name__)
CORS(app)  # 启用 CORS，允许所有来源的请求

# —— 保留原有 /command 路由 ——
@app.route('/command', methods=['POST'])
def receive_command():
    # 获取客户端发来的 JSON 数据
    data = request.get_json()
    command = data.get('command', '')  # 从 "command" 字段中获取指令

    # 等待10秒后再执行指令
    time.sleep(10)
    
    # 构造 combined_prompt，用于传入子进程
    combined_prompt = f"{command}\n\n你是一个区块链交易分析助手，你会获得我给你的一些市场数据（json 格式），以及我最近的交易记录。专注于解析我的近期交易记录。请分析我的代币交易，识别主要资产变动、买卖趋势、异常交易，并提供关键数据点。不要赘述，只给出清晰的结论和简要建议。最终结果用一种拟人化的方式说出来，假设你就是一个很熟悉区块链的分析师，不要过于机器，口语化一点，不要有任何的排版和格式。返回的结果需要口语化、轻松、幽默、有观点，带有起伏和俏皮的语气。表达上融合crypto黑话（比如FOMO、DYOR、HODL等），不需要解释这些术语。参考社交媒体（如Farcaster）上的发言风格，让语言既自然又有点小激动。角色定位：角色是一只Nemo里保守型、搞怪且有点害羞的小猫，既稳重又有趣，时而谨慎，时而调侃。不要用 markdown 格式输出！口语化输出。不需要解释这些术语。角色定位你自己知道就行了，不需要在表达的时候说出来"

    try:
        # 只调用一次 ollama run deepseek-r1:8b，将 combined_prompt 作为标准输入传入
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1:8b"],
            input=combined_prompt,
            text=True,
            capture_output=True,
            check=True
        )
        final_result = result.stdout.strip()

        # 使用正则表达式删除从字符串开始到第一个 </think>（包含 </think>）之前的所有内容
        final_result = re.sub(r'^.*?</think>', '', final_result, flags=re.DOTALL)
        final_result = final_result.strip()
    except subprocess.CalledProcessError as e:
        final_result = f"Error running ollama: {e}"
    
    return jsonify({
        'status': 'success',
        'result': final_result
    }), 200

# 新增/修改路由，通过调用 basescan_logs.py 和 binance_eth_trend.py 来触发整个流程，
# 将两个脚本的输出打包发给 /command，并最终调用 takocast.js，将 app.py 返回的信息传递过去
@app.route("/fetchTransfer", methods=["GET"])
def fetch_transfer():
    try:
        overall_start = time.time()
        print("[DEBUG] /fetchTransfer: Starting execution")

        # Step 1. 执行 basescan_logs.py (使用 --once 参数)
        print("[DEBUG] /fetchTransfer: Step 1 - Running basescan_logs.py with '--once'")
        t1 = time.time()
        result_basescan = subprocess.run(
            ["python3", "scripts/basescan_logs.py", "--once"],
            capture_output=True, text=True, check=True
        )
        print(f"[DEBUG] /fetchTransfer: Step 1 completed in {time.time()-t1:.2f} seconds")
        output_basescan = result_basescan.stdout
        
        # Step 2. 执行 binance_eth_trend.py
        print("[DEBUG] /fetchTransfer: Step 2 - Running binance_eth_trend.py")
        t2 = time.time()
        result_binance = subprocess.run(
            ["python3", "scripts/binance_eth_trend.py"],
            capture_output=True, text=True, check=True
        )
        print(f"[DEBUG] /fetchTransfer: Step 2 completed in {time.time()-t2:.2f} seconds")
        output_binance = result_binance.stdout
        
        # Step 3. 将两个脚本的输出信息组合在一起
        print("[DEBUG] /fetchTransfer: Step 3 - Combining outputs")
        combined_message = (
            f"Basescan Output:\n{output_basescan}\n\n"
            f"Binance Trend Output:\n{output_binance}"
        )
        
        # Step 4. 将合并的消息发送给 /command 接口进行处理
        print("[DEBUG] /fetchTransfer: Step 4 - Sending combined message to /command")
        t3 = time.time()
        response_cmd = requests.post("http://127.0.0.1:5000/command", json={"command": combined_message})
        print(f"[DEBUG] /fetchTransfer: /command responded in {time.time()-t3:.2f} seconds with status {response_cmd.status_code}")
        if response_cmd.status_code == 200:
            app_response = response_cmd.json()
            cast_message = app_response.get("result", "")
            cast_message = " ".join(cast_message.strip().split())
            
            # Step 5. 将 /command 接口返回的信息传给 takocast.js
            print("[DEBUG] /fetchTransfer: Step 5 - Running takocast.js with the command response")
            t4 = time.time()
            result_takocast = subprocess.run(
                ["node", "scripts/takocast.js", cast_message],
                capture_output=True, text=True, check=True
            )
            print(f"[DEBUG] /fetchTransfer: Step 5 (takocast.js) completed in {time.time()-t4:.2f} seconds")
            takocast_output = result_takocast.stdout.strip()
            
            # 过滤掉包含内部日志的行
            print("[DEBUG] /fetchTransfer: Filtering takocast.js output")
            filtered_lines = []
            for line in takocast_output.splitlines():
                if "向 Tako 发送 cast:" in line or "Tako cast 返回:" in line:
                    continue
                filtered_lines.append(line)
            takocast_output = "\n".join(filtered_lines)
        else:
            takocast_output = f"Error: /command route returned status code {response_cmd.status_code}"
        
        print(f"[DEBUG] /fetchTransfer: Entire operation completed in {time.time()-overall_start:.2f} seconds")
        # 返回最终组合结果给客户端（包含 ollama 的返回结果和 takocast.js 的响应结果）
        final_output = {
            "ollama_result": app_response.get("result", ""),
            "takocast_response": takocast_output
        }
        return jsonify(final_output)
    except Exception as e:
        print(f"[DEBUG] /fetchTransfer: Exception encountered: {e}")
        return jsonify({"result": f"Error running scripts: {e}"})

if __name__ == '__main__':
    # Flask 默认跑在 5000 端口，也可以通过指定 host 和 port 进行修改
    app.run(debug=True)