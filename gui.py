import tkinter as tk
from tkinter import ttk, messagebox
import requests
import random
import time
import aiohttp
import asyncio
from openpyxl import Workbook

API_URL = "http://127.0.0.1:8000/sqrt"

class ApiTesterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("API Tester")
        self.geometry("600x400")

        self.func_test_button = ttk.Button(self, text="功能验证", command=self.run_functional_test)
        self.func_test_button.pack(pady=10)

        self.perf_test_button = ttk.Button(self, text="性能压测", command=self.run_performance_test)
        self.perf_test_button.pack(pady=10)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.log_text = tk.Text(self, wrap='word', height=15)
        self.log_text.pack(pady=10)

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def run_functional_test(self):
        self.log("功能验证开始...")
        success_count = 0
        numbers = [random.randint(1, 10000) for _ in range(10000)]

        wb = Workbook()
        ws = wb.active
        ws.append(["Input", "Output", "Latency (ms)", "Error"])

        self.progress["maximum"] = len(numbers)

        for i, number in enumerate(numbers):
            start_time = time.time()
            try:
                response = requests.post(API_URL, json={"number": number}, timeout=5)
                latency = (time.time() - start_time) * 1000
                result = response.json().get("result")
                error = ""

                if result is None or abs(result - number ** 0.5) > 1e-6:
                    error = "Incorrect result"
                elif latency < 100 or latency > 200:
                    error = "Latency out of bounds"
                else:
                    success_count += 1

                ws.append([number, result, latency, error])
                self.log(f"Input: {number}, Output: {result}, Latency: {latency:.2f}ms, Error: {error}")
            except requests.exceptions.RequestException as e:
                self.log(f"Request failed: {e}")

            self.progress["value"] = i + 1
            self.update_idletasks()

        success_rate = success_count / len(numbers) * 100
        self.log(f"功能验证完成。成功率: {success_rate:.2f}%")
        wb.save("function_verification.xlsx")
        messagebox.showinfo("完成", f"功能验证完成。成功率: {success_rate:.2f}%")

    def run_performance_test(self):
        async def send_request(session, number):
            start_time = time.time()
            try:
                async with session.post(API_URL, json={"number": number}) as response:
                    latency = (time.time() - start_time) * 1000
                    data = await response.json()
                    result = data.get("result")
                    if result is None or abs(result - number ** 0.5) > 1e-6 or latency < 100 or latency > 200:
                        return False, latency
                    return True, latency
            except Exception as e:
                return False, 0

        async def performance_test(qps):
            numbers = [random.randint(1, 10000) for _ in range(qps)]
            success_count = 0
            total_latency = 0

            async with aiohttp.ClientSession() as session:
                tasks = [send_request(session, number) for number in numbers]
                results = await asyncio.gather(*tasks)
                for success, latency in results:
                    if success:
                        success_count += 1
                    total_latency += latency

            success_rate = success_count / qps * 100
            avg_latency = total_latency / qps if qps else 0
            return success_rate, avg_latency

        async def run_tests():
            self.log("性能压测开始...")
            qps_values = [10, 100, 200, 400, 600, 800, 1000, 10000]
            results = []

            self.progress["maximum"] = len(qps_values)

            for i, qps in enumerate(qps_values):
                self.log(f"正在测试QPS: {qps}...")
                success_rate, avg_latency = await performance_test(qps)
                results.append((qps, success_rate, avg_latency))
                self.log(f"QPS: {qps}, Success rate: {success_rate:.2f}%, Average latency: {avg_latency:.2f}ms")

                self.progress["value"] = i + 1
                self.update_idletasks()

            for qps, success_rate, avg_latency in results:
                self.log(f"QPS: {qps}, Success rate: {success_rate:.2f}%, Average latency: {avg_latency:.2f}ms")

            messagebox.showinfo("完成", "性能压测完成。")

        asyncio.run(run_tests())

if __name__ == "__main__":
    app = ApiTesterApp()
    app.mainloop()
