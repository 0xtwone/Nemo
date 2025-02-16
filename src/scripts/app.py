import time
import subprocess
from flask import jsonify

def fetch_transfer():
    if response_cmd.status_code == 200:
        app_response = response_cmd.json()
        cast_message = app_response.get("result", "")
        cast_message = " ".join(cast_message.strip().split())
        ollama_output = cast_message  # 保存 ollama 的返回结果
        
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
        
        # 将 ollama 的结果和 takocast.js 的响应结果组合后返回
        final_output = {
            "ollama_result": ollama_output,
            "takocast_response": takocast_output
        }
    else:
        final_output = {"error": f"/command route returned status code {response_cmd.status_code}"}

    # 返回最终组合结果给客户端
    return jsonify(final_output) 