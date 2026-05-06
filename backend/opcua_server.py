import asyncio
import os
from dotenv import load_dotenv
from asyncua import Server, ua

load_dotenv()

class PCBOPCUAServer:
    def __init__(self, endpoint=None):
        if endpoint is None:
            host = os.getenv("OPCUA_HOST", "0.0.0.0")
            port = os.getenv("OPCUA_PORT", "4840")
            self.endpoint = f"opc.tcp://{host}:{port}/freeopcua/server/"
        else:
            self.endpoint = endpoint
            
        self.server = Server()
        self.server.set_endpoint(self.endpoint)
        self.server.set_server_name("PCB Defect Detection OPC-UA Server")
        
        # Configure Security
        self.server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt
        ])
        
        username = os.getenv("OPCUA_USER", "admin")
        password = os.getenv("OPCUA_PASSWORD", "adminpassword123")
        self.server.set_security_IDs(["Username"])
        self.server.user_manager.set_user(username, password)
        
        # Variables to be updated
        self.total_pcbs = None
        self.total_defective_pcbs = None
        self.last_defect_type = None
        self.system_fps = None
        
        # State
        self._total_processed = 0
        self._total_defective = 0

    async def setup(self):
        # Setup namespace
        uri = "http://pcb-detection.edge/"
        idx = await self.server.register_namespace(uri)
        
        # Get Objects node
        objects = self.server.nodes.objects
        
        # Add an object
        pcb_device = await objects.add_object(idx, "PCB_Inspection_System")
        
        # Add variables to the object
        self.total_pcbs = await pcb_device.add_variable(idx, "Total_PCBs_Processed", 0)
        self.total_defective_pcbs = await pcb_device.add_variable(idx, "Total_Defective_PCBs", 0)
        self.last_defect_type = await pcb_device.add_variable(idx, "Last_Defect_Type", "None")
        self.system_fps = await pcb_device.add_variable(idx, "System_FPS", 60.0)
        
        # Make variables writable by clients (if needed, otherwise read-only)
        await self.total_pcbs.set_writable()
        await self.total_defective_pcbs.set_writable()
        await self.last_defect_type.set_writable()
        await self.system_fps.set_writable()

    async def update_metrics(self, is_defective: bool, defects: list):
        self._total_processed += 1
        if is_defective:
            self._total_defective += 1
            
        await self.total_pcbs.write_value(self._total_processed)
        await self.total_defective_pcbs.write_value(self._total_defective)
        
        if is_defective and defects:
            # Just take the first defect class as representative
            defect_type = defects[0].get("class_name", "Unknown")
            await self.last_defect_type.write_value(defect_type)
        else:
            await self.last_defect_type.write_value("None")
