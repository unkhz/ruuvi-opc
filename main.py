import asyncio
import logging
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from asyncua import Server, ua

# Configure logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

async def main():
    # Discover RuuviTags
    _logger.info("Discovering RuuviTags...")
    
    sensors = {}
    
    async for data in RuuviTagSensor.get_data_async():
        mac = data[0]
        if mac not in sensors:
            sensors[mac] = data[1]
            _logger.info(f"Found RuuviTag: {mac}")

        # Stop discovery after finding the first tag
        if len(sensors) >= 1:
            break

    if not sensors:
        _logger.error("No RuuviTags found!")
        return

    selected_mac = list(sensors.keys())[0]
    _logger.info(f"Auto-selecting first found RuuviTag: {selected_mac}")

    # OPC UA Server setup
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/ruuvi/server/")
    
    # Setup our own namespace
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)
    
    # Add a new object for our RuuviTag
    ruuvi_tag_object = await server.nodes.objects.add_object(idx, "RuuviTag " + selected_mac)
    
    # Add variables to the RuuviTag object
    temp_var = await ruuvi_tag_object.add_variable(idx, "Temperature", 0.0)
    humidity_var = await ruuvi_tag_object.add_variable(idx, "Humidity", 0.0)
    pressure_var = await ruuvi_tag_object.add_variable(idx, "Pressure", 0.0)
    accel_x_var = await ruuvi_tag_object.add_variable(idx, "AccelerationX", 0, ua.VariantType.Int64)
    accel_y_var = await ruuvi_tag_object.add_variable(idx, "AccelerationY", 0, ua.VariantType.Int64)
    accel_z_var = await ruuvi_tag_object.add_variable(idx, "AccelerationZ", 0, ua.VariantType.Int64)
    voltage_var = await ruuvi_tag_object.add_variable(idx, "BatteryVoltage", 0, ua.VariantType.Int64)

    _logger.info("Starting server!")
    async with server:
        while True:
            async for data in RuuviTagSensor.get_data_async([selected_mac]):
                _logger.info(f"Received data: {data}")
                
                # Update the OPC UA variables
                await temp_var.write_value(data[1].get('temperature'))
                await humidity_var.write_value(data[1].get('humidity'))
                await pressure_var.write_value(data[1].get('pressure'))
                await accel_x_var.write_value(data[1].get('acceleration_x'))
                await accel_y_var.write_value(data[1].get('acceleration_y'))
                await accel_z_var.write_value(data[1].get('acceleration_z'))
                await voltage_var.write_value(data[1].get('battery'))
                
                await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass