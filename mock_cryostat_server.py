import socketserver
import threading
import time

class MockCryostatHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Read the incoming SCPI command
        data = self.request.recv(1024).strip().decode('utf-8')
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] [CRYOSTAT HARDWARE LOG] Packet Received from HQA HAL: {self.client_address[0]}")
        
        if data.startswith("SET:CRYO:PUMP"):
            print(f"[CRYOSTAT HARDWARE LOG] COMMAND: {data}")
            print(f"[CRYOSTAT HARDWARE LOG] ACTION: Physically engaging mechanical cooling pumps...")
            # Simulate mechanical delay
            time.sleep(0.1)
            response = "ACK_OK: PUMPS_ENGAGED\n"
            self.request.sendall(response.encode('utf-8'))
            print("[CRYOSTAT HARDWARE LOG] Status: Stable. Acknowledgment sent to HAL.")
        else:
            print(f"[CRYOSTAT HARDWARE LOG] Unknown Command: {data}")
            self.request.sendall("ERR: UNKNOWN_COMMAND\n".encode('utf-8'))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def start_server(host="127.0.0.1", port=5000):
    server = ThreadedTCPServer((host, port), MockCryostatHandler)
    print(f"Mock Physical Cryostat Server online and listening on {host}:{port}")
    print("Waiting for SCPI network commands from the HQA HAL...\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down physical cryostat simulation.")
        server.server_close()

if __name__ == "__main__":
    start_server()
