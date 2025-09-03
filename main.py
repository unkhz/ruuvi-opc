import asyncio
import logging
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from asyncua import Server, ua

# Configure logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

async def main():
    # OPC UA Server setup
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/ruuvi/server/")
    
    # Setup our own namespace
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # Create a folder for RuuviTags
    ruuvi_tags_folder = await server.nodes.objects.add_folder(idx, "RuuviTags")

    _logger.info("Starting server!")
    async with server:
        while True:
            async for data in RuuviTagSensor.get_data_async():
                mac = data[0]
                sensor_data = data[1]

                # Check if the RuuviTag object already exists
                ruuvi_tag_object = None
                for child in await ruuvi_tags_folder.get_children():
                    if await child.read_browse_name() == ua.QualifiedName(mac, idx):
                        ruuvi_tag_object = child
                        break
                
                # If the object doesn't exist, create it
                if ruuvi_tag_object is None:
                    ruuvi_tag_object = await ruuvi_tags_folder.add_object(idx, mac)
                    await ruuvi_tag_object.add_variable(idx, "Temperature", 0.0)
                    await ruuvi_tag_object.add_variable(idx, "Humidity", 0.0)
                    await ruuvi_tag_object.add_variable(idx, "Pressure", 0.0)
                    await ruuvi_tag_object.add_variable(idx, "AccelerationX", 0, ua.VariantType.Int64)
                    await ruuvi_tag_object.add_variable(idx, "AccelerationY", 0, ua.VariantType.Int64)
                    await ruuvi_tag_object.add_variable(idx, "AccelerationZ", 0, ua.VariantType.Int64)
                    await ruuvi_tag_object.add_variable(idx, "BatteryVoltage", 0, ua.VariantType.Int64)

                # Update the OPC UA variables and log the data
                temp_var = await ruuvi_tag_object.get_child(f"{idx}:Temperature")
                humidity_var = await ruuvi_tag_object.get_child(f"{idx}:Humidity")
                pressure_var = await ruuvi_tag_object.get_child(f"{idx}:Pressure")
                accel_x_var = await ruuvi_tag_object.get_child(f"{idx}:AccelerationX")
                accel_y_var = await ruuvi_tag_object.get_child(f"{idx}:AccelerationY")
                accel_z_var = await ruuvi_tag_object.get_child(f"{idx}:AccelerationZ")
                voltage_var = await ruuvi_tag_object.get_child(f"{idx}:BatteryVoltage")

                temp_val = sensor_data.get('temperature')
                humidity_val = sensor_data.get('humidity')
                pressure_val = sensor_data.get('pressure')
                accel_x_val = sensor_data.get('acceleration_x')
                accel_y_val = sensor_data.get('acceleration_y')
                accel_z_val = sensor_data.get('acceleration_z')
                voltage_val = sensor_data.get('battery')

                await temp_var.write_value(temp_val)
                await humidity_var.write_value(humidity_val)
                await pressure_var.write_value(pressure_val)
                await accel_x_var.write_value(accel_x_val)
                await accel_y_var.write_value(accel_y_val)
                await accel_z_var.write_value(accel_z_val)
                await voltage_var.write_value(voltage_val)

                _logger.info(f"Served data for {mac}: Temp={temp_val}, Humidity={humidity_val}, Pressure={pressure_val}, AccelX={accel_x_val}, AccelY={accel_y_val}, AccelZ={accel_z_val}, Voltage={voltage_val}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass