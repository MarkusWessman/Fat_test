from pyudptest import Device, CommandPacket
#from matplotlib import pyplot as plt
import asyncio

# Funktion för att homea

#homea ventilerna
async def home_valve(device_ip, valve_type):
    async with Device(ip=device_ip) as device:
        valve_data = None
        
        if valve_type == "solvent":
            valve_data = 1
        elif valve_type == "pump1":
            valve_data = 2
        elif valve_type == "pump2":
            valve_data = 3
        
        if valve_data is not None:
            pump_command = CommandPacket(module_nr=3, opcode=124, data=[valve_data])
            home = await device.send_command(pump_command)
        else:
            raise ValueError("Invalid valve type")
        
        return home.data[0]

async def home_valves(device_ip):
        async with Device(ip=device_ip) as device:
            pump_command1 = CommandPacket(module_nr=3, opcode=124, data=[1])
            pump_command2 = CommandPacket(module_nr=3, opcode=124, data=[2])
            pump_command3 = CommandPacket(module_nr=3, opcode=124, data=[3])
            left = await device.send_command(pump_command1)
            right= await device.send_command(pump_command2)
            solvent = await device.send_command(pump_command3)

            return left, right, solvent



# Funktion för att home:a drawer
async def home_drawer(device_ip):
    async with Device(ip=device_ip) as device:
        pump_command = CommandPacket(module_nr=3, opcode=124, data=[4])
        home = await device.send_command(pump_command)
        return home

# Funktion för att home:a pumpen
async def home_pump(device_ip, flow_rate, module):
    async with Device(ip=device_ip) as device:
        if module == "pump1":
            unit = 0
        elif module == "pump2":
            unit = 1

        try:
            pump_command = CommandPacket(module_nr=2, unit_nr=unit, opcode=100, data=[flow_rate])
            home = await device.send_command(pump_command)
            await device.get_event(lambda e: e.event_code == 20)
        except asyncio.exceptions.InvalidStateError:
            print("An error occurred while handling the asynchronous operations.")

        return home.data[0]


# Funktion för att home:a pumpen
async def home_pumps(device_ip, flow_rate):
    async with Device(ip=device_ip) as device:

        
        pump_command1 = CommandPacket(module_nr=2, unit_nr=0, opcode=100, data=[flow_rate])
        pump_command2 = CommandPacket(module_nr=2, unit_nr=1, opcode=100, data=[flow_rate])
        await device.send_command(pump_command1)
        await device.send_command(pump_command2)

        task_left = device.get_event(lambda e: e.event_code == 20 and e.unit_nr == 0)
        task_right = device.get_event(lambda e: e.event_code == 20 and e.unit_nr == 1)

        await asyncio.gather(task_left, task_right)

# Funktion för att fylla pumpen
async def pump_fill(device_ip, flow_rate, volume, side):
    async with Device(ip=device_ip) as device:
        if side == "left" :
            unit = 0
        elif side == "right":
            unit=1
        
        pump_command = CommandPacket(module_nr=2, unit_nr=unit, opcode=106, data=[f'{flow_rate:.5f}', f'{volume:.3f}'])
        await device.send_command(pump_command)
        await device.get_event(lambda e: e.event_code == 21)

# Funktion för att tömma pumpen
async def pump_empty(device_ip, flow_rate, side):
    async with Device(ip=device_ip) as device:
        if side == "left" :
            unit = 0
        elif side == "right":
            unit=1
        
        pump_command = CommandPacket(module_nr=2, unit_nr=unit, opcode=104, data=[f'{flow_rate:.3f}'])
        await device.send_command(pump_command)
        await device.get_event(lambda e: e.event_code == 21)

# Funktion för att ställa ventilens position
async def set_valve_pos(device_ip, valve_type, pos):
    async with Device(ip=device_ip) as device:
        valve_data = None
        
        if valve_type == "solvent":
            valve_data = 1
        elif valve_type == "pump1":
            valve_data = 2
        elif valve_type == "pump2":
            valve_data = 3
        
        if valve_data is not None:
            pump_command = CommandPacket(module_nr=3, opcode=110, data=[valve_data, pos])
            await device.send_command(pump_command)
            await device.get_event(lambda e: e.event_code == 30)

        else:
            raise ValueError("Invalid valve type")



# Funktion för att ställa drawerns position
async def set_drawer_position(device: Device, unit_nr: int, pos: int):
    async with Device(ip=device_ip) as device:
        pump_command = CommandPacket(module_nr=2, opcode=110, type=0, data=[4, pos])
        await device.send_command(pump_command)

async def set_two_valve_positions(device_ip: Device, pos: int):
    async with Device(ip=device_ip) as device:
        pump_command1 = CommandPacket(module_nr=3, opcode=110, data=[2, pos])
        pump_command2 = CommandPacket(module_nr=3, opcode=110, data=[3, pos])

        await device.send_command(pump_command1)
        await device.send_command(pump_command2)

# Funktion för att sätta LED
async def set_led(device_ip, data1, data2, data3, data4):
    async with Device(ip=device_ip) as device:
        pump_command = CommandPacket(module_nr=3,opcode=140, type=3, data=[data1, data2, data3, data4])
        light = await device.send_command(pump_command)
        return light



# Funktion för att läsa trycket

async def get_pressure(device_ip, pos, unit):
    async with Device(ip=device_ip) as device:
        
        if unit == "pump2":
            unit = 1
        else:
            unit = 0
        
        opc = None

        if pos == 1:
            opc = 800
        elif pos == 2:
            opc = 802
        elif pos == 3:
            opc = 804
        elif pos == 4:
            opc = 806

        if opc is not None:
            pump_command = CommandPacket(module_nr=2, unit_nr=unit, opcode=opc, data=[0, 0])
            reply = await device.send_command(pump_command)
            pressure_value = float(reply.data[1])  # Konvertera till flyttal
            return pressure_value
        else:
            print("Invalid valve type")
            return None
        
# Funktion för att flytta pumpen
async def move_pump(device_ip, steps, step_speed):
    async with Device(ip=device_ip) as device:
        pump_command = CommandPacket(module_nr=2,opcode=406, type=4, data=[steps, step_speed])
        await device.send_command(pump_command)     

async def set_nitro_valves(device_ip, state, pump_unit):
    async with Device(ip=device_ip) as device:
        
        if pump_unit == "pump2" :
            unit = 1
        else:
            unit = 0

        pump_command = CommandPacket(module_nr=2, unit_nr=unit, opcode=410, type=3, data=[0, state])
        ans = await device.send_command(pump_command)
        return ans.data[0]


async def set_pressure_regulator(device_ip, pressure):
    async with Device(ip=device_ip) as device:
        pump_command = CommandPacket(module_nr=3,opcode=406, type=0, data=[pressure, 1])
        press=await device.send_command(pump_command)
        return press

async def set_solvent_valves(device_ip, bank, state):
    async with Device(ip=device_ip) as device:
        if bank =="pump1":
            bank=0
        elif bank== "pump2":
            bank=1
        pump_command = CommandPacket(module_nr=3,opcode=400, type=3, data=[bank, 1, state])
        ans = await device.send_command(pump_command)
        return ans.data[0]

async def get_software_number(device_ip, module):
    
    if module == "hmi":
        module = 0
    elif module == "pump1" or module == "pump2":
        module = 2
    elif module == "valve":
        module = 3

    if module == "pump2":
        unit = 1
    else:
        unit = 0

    async with Device(ip=device_ip) as device:
        pump_command = CommandPacket(module_nr = module, unit_nr= unit,  opcode=6, type=0, data=[0])
        serial_number = await device.send_command(pump_command)
        return serial_number.data[0]


async def set_fan(device_ip, speed):
    async with Device(ip=device_ip) as device:
        pump_command = CommandPacket(module_nr=3,opcode=402, type=0, data=[speed])
        ans = await device.send_command(pump_command)
        return ans.data[0]